FROM python:3.7.14-slim-bullseye
LABEL org.opencontainers.image.source https://github.com/offspot/container-images
EXPOSE 80
VOLUME /data

ENV ADMIN_USERNAME ""
ENV ADMIN_PASSWORD ""
ENV SRC_DIR "#"


RUN apt-get update -y && \
    apt-get install -y --no-install-recommends libmagic1 ghostscript libmagickwand-dev nginx npm nodejs curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /src

RUN npm -g install bower && \
    # static files folder
    mkdir -p /var/lib/edupi/static && \
    # /data structure
    mkdir -p /data/database /data/media /data/stats /data/log && chown -R www-data:www-data /data && \
    # to write thumbnails for PDF files
    sed -i 's/domain="coder" rights="none" pattern="PDF"/domain="coder" rights="read | write" pattern="PDF"/g' /etc/ImageMagick-6/policy.xml && \
    # download and extract edupi source
    curl -L -o v1.4.11.tar.gz https://github.com/offspot/edupi/archive/refs/tags/v1.4.11.tar.gz && tar -C . --strip-components 1 -x -f v1.4.11.tar.gz && rm -f v1.4.11.tar.gz && \
    # allow accessing service from any URL (nginx upstream)
    sed -i 's/^ALLOWED_HOSTS\s=.\+/ALLOWED_HOSTS = ["*"]/g' /src/edupi/settings.py && \
    # change data root folder
    sed -i 's/^DATA_ROOT\s=.\+/DATA_ROOT = "\/data"/g' /src/edupi/settings.py && \
    # fetch nginx access log from root folder
    sed -i 's/^NGINX_LOG_DIR\s=.\+/NGINX_LOG_DIR = "\/data\/log"/g' /src/edupi/settings.py && \
    # static files stored in-image
    sed -i 's/^STATIC_ROOT\s=.\+/STATIC_ROOT = "\/var\/lib\/edupi\/static"/g' /src/edupi/settings.py && \
    # edupi dependencies
    pip install pip install --no-cache-dir -U pip && \
    pip install pip install --no-cache-dir -r ./requirements.txt && \
    # edupi static files
    python3 ./manage.py bower install && \
    python3 ./manage.py collectstatic --noinput && \
    python3 ./manage.py migrate

COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.py /usr/local/bin/entrypoint
COPY favicon.ico /var/lib/edupi/favicon.ico


ENTRYPOINT ["entrypoint"]
CMD ["gunicorn", "--user", "www-data", "--group", "www-data", "--bind", "localhost:8010", "edupi.wsgi:application", "--log-level", "info"]