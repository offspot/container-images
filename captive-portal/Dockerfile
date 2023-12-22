# alpine 3.19 has python 3.11
FROM alpine:3.19
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

WORKDIR /src

RUN  \
    apk add --no-cache \
    nftables conntrack-tools \
    curl dumb-init \
    openssl \
    py3-pip py3-nftables uwsgi uwsgi-http uwsgi-python3 \
    && python3 -m venv --system-site-packages /usr/local/captive-env \
    # install caddy (single binary)
    && ARCH=$(cat /etc/apk/arch) \
    && if [ "$ARCH" = "x86_64" ]; then ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ]; then ARCH="arm64"; \
    elif [ "$ARCH" = "armhf" ]; then ARCH="armv6"; fi \
    && curl -LO https://github.com/caddyserver/caddy/releases/download/v2.7.6/caddy_2.7.6_linux_$ARCH.tar.gz \
    && tar -xf caddy_2.7.6_linux_$ARCH.tar.gz -C /usr/local/bin/ \
    && rm -rf caddy_2.7.6_linux_$ARCH.tar.gz \
    && chmod +x /usr/local/bin/caddy \
    && /usr/local/captive-env/bin/pip install --no-cache-dir -U pip wheel

COPY entrypoint.sh /usr/local/bin/
COPY clear-passlist reset-passlist remove-client watcher /usr/local/bin/
COPY Caddyfile /etc/caddy/

RUN \
    url="https://github.com/offspot/captive-portal/archive/refs/tags/1.1.0.tar.gz" \
    && curl -L $url | tar -C /src/ --strip-components 1 -xz \
    # set python virtualenv in app's uwsgi config
    && echo "home = /usr/local/captive-env" >> /src/uwsgi.ini \
    && /usr/local/captive-env/bin/pip install --no-cache-dir -r /src/portal/requirements.txt \
    && /usr/local/captive-env/bin/pip install --no-cache-dir -r /src/portal_filter/requirements.txt \
    # inotify is used in our watcher
    && /usr/local/captive-env/bin/pip install --no-cache-dir inotify==0.2.10 \
    && apk del curl ca-certificates

ENV HOTSPOT_NAME "My Hotspot"
ENV HOTSPOT_FQDN "generic.offspot"
ENV HOTSPOT_IP "192.168.2.1"
ENV FOOTER_NOTE ""
# minutes after which to unregister gone clients
ENV TIMEOUT "60"
# minutes after which to clear filter passlist when online
ENV CLEAR_PASSLIST_INTERVAL "60"
ENV FILTER_MODULE "portal_filter"
ENV DB_PATH /data/portal-users.db
# restrict netfilter rules to specified networks
ENV CAPTURED_NETWORKS "192.168.2.128/25"
ENV PYTHONPATH "/src"

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["uwsgi", "--ini", "/src/uwsgi.ini"]
