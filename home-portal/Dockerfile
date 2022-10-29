# alpine 3.16 has python 3.10
FROM alpine:3.16
WORKDIR /src

RUN  \
    apk add --no-cache \
    nftables conntrack-tools \
    curl dumb-init \
    openssl \
    py3-pip uwsgi uwsgi-http uwsgi-python3 && \
    # install caddy (single binary)
    ARCH=$(cat /etc/apk/arch) && \
    if [ "$ARCH" = "x86_64" ]; then ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ]; then ARCH="arm64"; \
    elif [ "$ARCH" = "armhf" ]; then ARCH="armv6"; fi &&\
    curl -LO https://github.com/caddyserver/caddy/releases/download/v2.6.2/caddy_2.6.2_linux_$ARCH.tar.gz && \
    tar -xf caddy_2.6.2_linux_$ARCH.tar.gz -C /usr/local/bin/ && \
    chmod +x /usr/local/bin/caddy && \
    pip3 install --no-cache-dir -U pip wheel

COPY entrypoint.sh /usr/local/bin/
COPY clear-passlist reset-passlist remove-client /usr/local/bin/
COPY Caddyfile /etc/caddy/

RUN \
    url="https://github.com/offspot/home-portal-app/archive/refs/heads/main.tar.gz" && \
    curl -L $url | tar -C /src/ --strip-components 1 -xz  && \
    pip3 install --no-cache-dir -r /src/portal/requirements.txt && \
    pip3 install --no-cache-dir -r /src/portal_filter/requirements.txt && \
    apk del curl

ENV HOTSPOT_NAME "My Hotspot"
ENV HOTSPOT_FQDN "generic.offspot"
ENV HOTSPOT_IP "192.168.2.1"
ENV FOOTER_NOTE ""
# minutes after which to unregister gone clients
ENV TIMEOUT "60"
ENV FILTER_MODULE "portal_filter"
ENV DB_PATH /data/portal-users.db
# restrict netfilter rules to specified networks
ENV CAPTURED_NETWORKS "192.168.2.128/25"
# should you install it yourself
ENV DONT_SETUP_FILTER ""
ENV PYTHONPATH "/src"

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["uwsgi", "--ini", "/src/uwsgi.ini"]
