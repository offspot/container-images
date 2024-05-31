FROM caddy:2.8.4-alpine
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

RUN \
    # openssl required to generate cert when CAPTIVE_PORTAL is on
    apk add --no-cache dumb-init python3 \
    && python3 -m venv /usr/local/proxy-env \
    && /usr/local/proxy-env/bin/pip3 install --no-cache-dir -U pip \
    && /usr/local/proxy-env/bin/pip3 install --no-cache-dir Jinja2==3.1.2

COPY Caddyfile /etc/caddy/
COPY gen-caddyfile.py /src/

ENV FQDN "generic.hotspot"
ENV WELCOME_FQDN "goto.generic.hotspot"
ENV METRICS_LOGS_DIR "/var/log/metrics"
# set this when using reverse proxy in online demo to trigger real SSL certs usage
ENV IS_ONLINE_DEMO ""
# read SSL certs require an email address to send expiration notice to
ENV DEMO_TLS_EMAIL "dev@kiwix.org"

# store python bytecode in image
RUN /usr/local/proxy-env/bin/python3 -m compileall /src/gen-caddyfile.py && mv /src/__pycache__/*.pyc /usr/local/lib/

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/local/proxy-env/bin/python3", "/usr/local/lib/gen-caddyfile.cpython-312.pyc"]
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]

