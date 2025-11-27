FROM alpine:3.22
LABEL org.opencontainers.image.source=https://github.com/offspot/container-images

COPY entrypoint /usr/local/bin/

RUN apk add --no-cache \
    dumb-init \
    lighttpd \
    php82-cgi \
    php82-curl php82-gd php82-pdo_sqlite php82-session php82-sqlite3 php82-mbstring \
    && mkdir -p /var/www/magoe

COPY lighttpd.conf /etc/lighttpd/lighttpd.conf

VOLUME /var/www/magoe
EXPOSE 80
ENV MAGOE_URL=http://localhost

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/local/bin/entrypoint"]
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
