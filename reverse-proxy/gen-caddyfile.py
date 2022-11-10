#!/usr/bin/env python3

""" Entrypoint-friendly Caddyfile generation script

    Generates reverse-proxy endpoints from SERVICES environ.
    Handles default redirection in case of single service
    Creates /{service} redirects as well

    Dependencies:
    - Jinja2
"""

import os
import sys
import traceback
from typing import List

from jinja2 import Template

services: List[str] = [
    srv.strip() for srv in os.getenv("SERVICES", "").split(",") if srv
]
debug: bool = bool(os.getenv("DEBUG", False))
template: Template = Template(
    """
{
    admin :2020
    auto_https disable_redirects
    local_certs
    skip_install_trust
    {% if debug %}debug{% endif %}
}

{% if with_contentfilter %}
(block_path) {
    respond "Web page in admin's black-list." 451
}
{% endif %}

# home page on domain, with prefix redirects
{$FQDN}:80, {$FQDN}:443 {
    tls internal
    {% if services %}
    # redirect to services (convenience only){% for service in services %}
    redir /{{service}}* {scheme}://{{service}}.{$FQDN} permanent
    {% endfor %}{% endif %}

    {% if nb_services == 0 %}# no service at all (testing?)
    respond "Hello world, you requested no service." 200
    {% elif nb_services == 1 %}# single service, redirecting from home
    redir / /{{services.0}} permanent
    {% else  %}# home service has no endpoint
    reverse_proxy home:80
    {% endif %}

    handle_errors {
        respond "HTTP {http.error.status_code} Error ({http.error.message})"
    }
}

{% if services %}# endpoint-based services
{% for service in services %}{{service}}.{$FQDN}:80, {{service}}.{$FQDN}:443 {
    tls internal
    reverse_proxy {{service}}:80
    handle_errors {
        respond "HTTP {http.error.status_code} Error ({http.error.message})"
    }
}

{% endfor %}
{% endif %}

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
                )
            )
    except Exception as exc:
        print("[CRITICAL] unable to gen Caddyfile, using default")
        traceback.print_exception(exc)
        return

    print(f"Generated Caddyfile for: {services}")


if __name__ == "__main__":
    gen_caddyfile()

    if debug:
        with open("/etc/caddy/Caddyfile", "r") as fh:
            print(fh.read())

    if len(sys.argv) < 2:
        sys.exit(0)
    os.execvp(sys.argv[1], sys.argv[1:])  # nosec
