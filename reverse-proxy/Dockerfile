FROM caddy:2.6.1-alpine

RUN \
    # openssl required to generate cert when CAPTIVE_PORTAL is on
    apk add --no-cache dumb-init python3 py3-pip && \
    pip3 install --no-cache-dir -U pip && \
    pip3 install --no-cache-dir Jinja2==3.1.2

COPY Caddyfile /etc/caddy/Caddyfile
COPY gen-caddyfile /usr/local/bin/

ENV FQDN "generic.hotspot"

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/local/bin/gen-caddyfile"]
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]

