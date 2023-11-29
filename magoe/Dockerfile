FROM alpine:3.18
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

COPY httpd-foreground entrypoint /usr/local/bin/

RUN apk add --no-cache \
    dumb-init \
    php81-apache2 \
    php81-curl php81-gd php81-pdo_sqlite php81-session php81-sqlite3 php81-mbstring \
    && mkdir -p /var/www/magoe \
    && printf "\n\
ServerName magoe;\n\
ErrorLog /dev/stderr\n\
CustomLog /dev/stdout combined\n\
\n" >> /etc/apache2/conf.d/default.conf

VOLUME /var/www/magoe
EXPOSE 80
STOPSIGNAL SIGWINCH
ENV MAGOE_URL http://localhost

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/local/bin/entrypoint"]
CMD ["httpd-foreground"]
