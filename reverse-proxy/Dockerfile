FROM caddy:2.7.6-alpine
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

RUN \
    # openssl required to generate cert when CAPTIVE_PORTAL is on
    apk add --no-cache dumb-init python3 py3-pip && \
    pip3 install --no-cache-dir -U pip && \
    pip3 install --no-cache-dir Jinja2==3.1.2

COPY Caddyfile /etc/caddy/
COPY gen-caddyfile.py /src/

ENV FQDN "generic.hotspot"
ENV METRICS_LOGS_DIR "/var/log/metrics"

# store python bytecode in image
RUN python3 -m compileall /src/gen-caddyfile.py && mv /src/__pycache__/*.pyc /usr/local/lib/

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/bin/python3", "/usr/local/lib/gen-caddyfile.cpython-311.pyc"]
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]

