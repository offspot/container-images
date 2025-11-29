FROM alpine:3.22
LABEL org.opencontainers.image.source=https://github.com/offspot/container-images

ENV WEBDIR="/var/www/html"
WORKDIR $WEBDIR

COPY tinyfilemanager.php.patch $WEBDIR

RUN apk add --no-cache \
        dumb-init \
        sed \
        lighttpd \
        php83-fpm php83-fileinfo php83-iconv php83-zip php83-mbstring \
        php83-session php83-phar php83-ctype php83-posix \
        # curl and patch are used only in docker-build \
        curl \
        patch \
    && set -e \
    && TFMREF="8e87afae5b744c3e23490000bf0d398d6d4a749c" \
    && TFMPREFIX="https://raw.githubusercontent.com/prasathmani/tinyfilemanager/$TFMREF/" \
    && mkdir -p $WEBDIR/assets/css $WEBDIR/assets/js $WEBDIR/assets/fonts \
    && cd $WEBDIR/assets/css \
    && curl -L -O https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css \
    && curl -L -O https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.css.map \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/dropzone/5.9.3/min/dropzone.min.css \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.6.0/styles/vs.min.css \
    && echo "CSS OK" \
    && cd $WEBDIR/assets/fonts \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/FontAwesome.otf \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.eot \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.svg \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.ttf \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.woff \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.woff2 \
    && echo "FONTS OK" \
    && cd $WEBDIR/assets/js \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/ace/1.13.1/ace.js \
    && curl -L -O https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js \
    && curl -L -O https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.js.map \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/dropzone/5.9.3/min/dropzone.min.js \
    && curl -L -O https://code.jquery.com/jquery-3.6.1.min.js \
    && curl -L -O https://cdn.datatables.net/1.13.1/js/jquery.dataTables.min.js \
    && curl -L -O https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.6.0/highlight.min.js \
    # replace passing-through animation with slide-in (which stays) for success
    && sed -i 's/.dz-success-mark {/.dz-success-mark {opacity:1;/g' $WEBDIR/assets/css/dropzone.min.css \
    && sed -i 's/animation:passing-through/animation:slide-in/g' $WEBDIR/assets/css/dropzone.min.css \
    # replace success icon with solid green color fill="#FFFFFF" (JS)
    && sed -i '0,/fill="#FFFFFF"/s//fill="green"/' $WEBDIR/assets/js/dropzone.min.js \
    # replace error icon with solid red color fill="#FFFFFF"
    && sed -i '0,/fill="#FFFFFF"/s//fill="red"/' $WEBDIR/assets/js/dropzone.min.js \
    && echo "JS OK" \
    && cd $WEBDIR \
    && curl -L -O "$TFMPREFIX/translation.json" \
    && curl -L -O "$TFMPREFIX/tinyfilemanager.php" \
    && mkdir -p /data \
    && patch tinyfilemanager.php tinyfilemanager.php.patch \
    && rm tinyfilemanager.php.patch \
    && apk del \
         curl \
         patch \
    # replace head of file to change the external assets (which is AFTER config incl in original file)
    && lnum=$(grep -n -F "EDIT BELOW CAREFULLY OR DO NOT EDIT AT ALL" tinyfilemanager.php | cut -d ':' -f 1) \
    && printf "<?php\n\
\$config_file = __DIR__.'/config.php';\n\
if (is_readable(\$config_file)) {\n\
    @include(\$config_file);\n\
}\n" > index.php \
    && tail -n +$lnum tinyfilemanager.php >> index.php

COPY config.php listing_auth.php manager_auth.php conf-rewrite.php $WEBDIR/
COPY lighttpd.conf /etc/lighttpd/lighttpd.conf
COPY entrypoint /usr/local/bin/

# there are three modes:
# - listing: lists the content of /data read-only
# - manager: auth-required, /data is in read-write
# - mixed: listing mode on / endpoint but manager on /admin/ endpoint
ENV ACCESS_MODE="listing"

# authentication for manager and mixed modes (plaintext)
ENV ADMIN_USERNAME="admin"
ENV ADMIN_PASSWORD="admin@123"

# timezone to use for date/time (assuming host has date)
# /!\ must be escaped! (slash)
ENV UI_TIMEZONE="Etc/UTC"

ENV UI_LANG="en"

ENV APP_URL=""

EXPOSE 80
ENTRYPOINT ["/usr/bin/dumb-init", "--", "entrypoint"]
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
