#!/usr/bin/env python3

""" Entrypoint-friendly Caddyfile generation script

    Generates reverse-proxy endpoints from SERVICES environ.
    Handles default redirection in case of single service
    Creates /{service} redirects as well

    Dependencies:
    - Jinja2
"""

import dataclasses
import os
import pathlib
import subprocess
import sys
import traceback

from jinja2 import Template


def bcrypt_password(plaintext: str) -> str:
    """bcrypt-encoded version of the plaintext password"""
    ps = subprocess.run(
        args=[
            "/usr/bin/env",
            "caddy",
            "hash-password",
            "--algorithm",
            "bcrypt",
            "--plaintext",
            plaintext,
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return ps.stdout.strip()


@dataclasses.dataclass
class Service:
    name: str
    target: str
    port: int
    username: str | None = None
    password: str | None = None
    password_e: str | None = None
    disable_home: bool | None = False

    @classmethod
    def from_line(cls, text: str):
        """Service from svc-name[:target:port] format"""
        parts = text.strip().split(":", 2)
        base = (parts[0], parts[0], "80")
        name, target, port = tuple(
            parts[idx] if len(parts) >= idx + 1 else base[idx] for idx in range(3)
        )
        return cls(name=name, target=target, port=int(port))

    def protect_from(self, text: str):
        """Adds password-protect definition from svcname:username:password format"""
        name, username, password = text.split(":", 2)
        if name != self.name:
            raise ValueError(f"Mismatch service {name} != {self.name}")
        if username and password:
            self.username = username.strip()
            self.password = password.strip()
            self.password_e = bcrypt_password(self.password)

    @property
    def should_protect(self) -> bool:
        return bool(self.username) and bool(self.password_e)


services: dict[str, Service] = {
    Service.from_line(svc).name: Service.from_line(svc)
    for svc in os.getenv("SERVICES", "").split(",")
} if os.getenv("SERVICES", "") else {}
for svc in os.getenv("PROTECTED_SERVICES", "").split(","):
    svc_name = svc.split(":", 1)[0]
    if svc_name in services:
        services[svc_name].protect_from(svc)
for svc_name in os.getenv("NO_HOME_SERVICES", "").split(","):
    if svc_name in services:
        services[svc_name].disable_home = True

files_map: dict[str, str] = {
    entry.split(":", 1)[0]: entry.split(":", 1)[1]
    for entry in os.getenv("FILES_MAPPING", "").split(",")
    if ":" in entry
}

debug: bool = bool(os.getenv("DEBUG", False))
template: Template = Template(
    """
{
    admin :2020
    auto_https disable_redirects
    local_certs
    skip_install_trust
    {% if debug %}debug{% endif %}

    log metrics {
        include http.log.access
        output file {$METRICS_LOGS_DIR}/metrics.json {
            roll_size 1MiB
            roll_keep 2
            roll_uncompressed
            roll_keep_for 48h
        }
        format json
    }
}

{% if with_contentfilter %}
(block_path) {
    respond "Web page in admin's black-list." 451
}
{% endif %}

# home page on domain, with prefix redirects
{$FQDN}:80, {$FQDN}:443 {
    tls internal
    log

    {% if services %}
    # redirect to services (convenience only){% for service in services.values() %}
    redir /{{service.name}}* {scheme}://{{service.name}}.{$FQDN} permanent
    {% endfor %}{% endif %}

    reverse_proxy home:80

    handle_errors {
        respond "HTTP {http.error.status_code} Error ({http.error.message})"
    }
}

{% if services %}# endpoint-based services
{% for service in services.values() %}
{{service.name}}.{$FQDN}:80, {{service.name}}.{$FQDN}:443 {
    tls internal
    log

    {% if service.should_protect %}
    basicauth * {
        {{service.username}} {{service.password_e}}
    }
    {% endif %}
    {% if service.disable_home %}
    redir / {scheme}://{$FQDN} permanent
    {% endif %}
    reverse_proxy {{service.target}}:{{service.port}}
    handle_errors {
        respond "HTTP {http.error.status_code} Error ({http.error.message})"
    }
}

{% endfor %}
{% endif %}

{% if files_map %}# endpoint-based files_map
{% for subdomain, folder in files_map.items() %}
{{subdomain}}.{$FQDN}:80, {{subdomain}}.{$FQDN}:443 {
    tls internal
    log
    reverse_proxy files:80
    rewrite * /{{folder}}/{path}?{query}
    handle_errors {
        respond "HTTP {http.error.status_code} Error ({http.error.message})"
    }
}

{% endfor %}
{% endif %}

# fallback for unhandled names/IP arriving here
:80, :443 {
    tls internal
    log
    respond "Not Found! Oops" 404
}


"""
)


def gen_caddyfile():
    try:
        with open("/etc/caddy/Caddyfile", "w") as fh:
            fh.write(
                template.render(
                    debug=debug,
                    services=services,
                    nb_services=len(services),
                    files_map=files_map,
                )
            )
    except Exception as exc:
        print("[CRITICAL] unable to gen Caddyfile, using default", flush=True)
        traceback.print_exception(exc)
        return

    print(f"Generated Caddyfile for: {services=} and {files_map}", flush=True)


if __name__ == "__main__":
    # create metrics logs dir on start in case it doesnt exist. (corner case as this
    # would generally be mounted and thus created by Docker and caddy will ultimately
    # create it upon first request)
    pathlib.Path(os.getenv("METRICS_LOGS_DIR", "")).mkdir(parents=True, exist_ok=True)
    gen_caddyfile()

    if debug:
        with open("/etc/caddy/Caddyfile", "r") as fh:
            print(fh.read(), flush=True)

    if len(sys.argv) < 2:
        sys.exit(0)
    os.execvp(sys.argv[1], sys.argv[1:])  # nosec
