FROM docker.io/library/alpine:3.22
LABEL org.opencontainers.image.source=https://github.com/offspot/container-images

RUN apk add --no-cache lighttpd \
    && mkdir -p /data

COPY lighttpd.conf /etc/lighttpd/lighttpd.conf

EXPOSE 80
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
