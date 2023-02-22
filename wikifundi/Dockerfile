# we need a base system with PHP7.4.3 ; https://www.mediawiki.org/wiki/Manual:Installation_requirements#PHP
FROM debian:bullseye-slim

ENV DEBIAN_FRONTEND noninteractive
ENV WIKIFUNDI_ROOT /var/www/wikifundi
ENV MEDIAWIKI_ROOT $WIKIFUNDI_ROOT/w
ENV WIKIFUNDI_DATA /var/www/data
ENV DATABASE_NAME mw_wikifundi
ENV MEDIAWIKI_ADMIN_PASSWORD admin-password
ENV CACHE_DIR /dev/shm/mw

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends ca-certificates && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
        php7.4-fpm php7.4-sqlite3 php7.4-intl php7.4-mbstring php7.4-xml php7.4-curl php7.4-gd php7.4-gmp \
        # texlive texlive-fonts-recommended texlive-lang-greek texlive-latex-recommended texlive-latex-extra build-essential dvipng ocaml cjk-latex \
        imagemagick libicu-dev ffmpeg librsvg2-bin poppler-utils memcached lua5.1 python3 locales sqlite3 fonts-freefont-ttf ttf-unifont exiv2 libtiff-tools libvips-tools \
        curl unzip python3 make build-essential librsvg2-dev ghostscript \
        git unzip curl \
        cron nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    LC_ALL=C locale-gen en_US.UTF-8 && \
    # name: hack to avoid thumbs generation error for PDF with errors
    mv /usr/bin/gs /usr/bin/gs9-20 && echo '/usr/bin/gs9-20 -sstdout=%stderr $@' > /usr/bin/gs && chmod a+x /usr/bin/gs && \
    # sqlite3 node module calls python bin in its build process
    ln -s /usr/bin/python3 /usr/bin/python && \
    # memcached folder in memory
    mkdir -m 755 -p /dev/shm/mw && \
    # wikifundi and mediawiki root
    mkdir -p $MEDIAWIKI_ROOT && \
    # download and extract mediawiki (with extensions)
    curl --insecure -L --output /tmp/mediawiki.tar.bz2 -L https://drive.offspot.it/wikifundi/dependencies/mediawiki-1.36.1__with-extensions.tar.bz2 && \
    tar -C $MEDIAWIKI_ROOT -x --strip-components=1 -f /tmp/mediawiki.tar.bz2 && \
    # remove archive
    rm -f /tmp/mediawiki.tar.bz2 && \
    # increase mediawiki UI timeout
    sed -i 's/30/150/g' $MEDIAWIKI_ROOT/resources/src/mediawiki.api/index.js && \
    # fix ownership of mediawiki folders
    chown -R www-data:www-data $MEDIAWIKI_ROOT/skins $MEDIAWIKI_ROOT/cache && \
    # download composer
    curl --insecure -L --output $MEDIAWIKI_ROOT/composer.phar https://drive.offspot.it/wikifundi/dependencies/composer-2.1.5.phar && \
    # update composer config to prevent network header mismatch
    cd $MEDIAWIKI_ROOT && \
    php composer.phar config -g repo.packagist composer https://packagist.org && \
    php composer.phar config -g github-protocols https ssh && \
    # install composer
    php composer.phar install --no-dev && \
    cd - && \
    # link FreeSans font without extension
    cd /usr/share/fonts/truetype/freefont && \
    ln -s FreeSans.ttf FreeSans && \
    # download mathoid and restbase
    curl --insecure -L -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash && \
    # install nvm to specify node version
    export NVM_DIR="$HOME/.nvm" && \
    . "$NVM_DIR/nvm.sh" && \
    nvm install 12.22.12 && \
    curl --insecure -L --output /tmp/mathoid.zip https://github.com/wikimedia/mediawiki-services-mathoid/archive/95788093badfbed75a70780ca35658f64804d3b1.zip && \
    unzip -d /tmp/ /tmp/mathoid.zip && \
    rm /tmp/mathoid.zip && \
    mv /tmp/mediawiki-services-mathoid-* /usr/local/lib/mathoid && \
    cd /usr/local/lib/mathoid && \
    $NVM_DIR/versions/node/v12.22.12/bin/npm install && \
    # node server.js
    cd .. && \
    curl --insecure -L --output /tmp/restbase.zip https://github.com/wikimedia/restbase/archive/c1d391c74d39d38f7b1a8175e510fa714b4d91f1.zip && \
    unzip -d /tmp/ /tmp/restbase && \
    rm /tmp/restbase.zip && \
    mv /tmp/restbase-* /usr/local/lib/restbase && \
    cd /usr/local/lib/restbase && \
    curl --insecure -L --output config.yaml https://raw.githubusercontent.com/wikimedia/mediawiki-services-mathoid/95788093badfbed75a70780ca35658f64804d3b1/test/restbase/config.yaml && \
    $NVM_DIR/versions/node/v12.22.12/bin/npm install && \
    # fix permissions on extensions folder
    chown -R www-data:www-data $MEDIAWIKI_ROOT/extensions && \
    # create wikifundi data placeholder (will be mounted)
    mkdir -p /var/www/data/images

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

VOLUME /var/www/data

COPY conf/90-wikifundi.ini /etc/php/7.4/fpm/conf.d/90-wikifundi.ini
COPY conf/www.conf /etc/php/7.4/fpm/pool.d/www.conf
COPY conf/php.conf /etc/nginx/conf.d/php.conf
COPY conf/nginx.conf /etc/nginx/sites-enabled/default
COPY conf/mathoid.init /etc/init.d/mathoid
COPY conf/restbase.init /etc/init.d/restbase
COPY conf/sqlite-vacuum.sh /etc/cron.weekly/sqlite-vacuum.sh
COPY branding/cc-by-sa.png branding/A_WikiAfrica_project.png branding/favicon.ico branding/logo.png branding/logo-sq.png $WIKIFUNDI_ROOT/
COPY LocalSettings.php $MEDIAWIKI_ROOT/
COPY entrypoint.sh /usr/bin/entrypoint
RUN chmod +x /usr/bin/entrypoint /etc/init.d/mathoid /etc/init.d/restbase /etc/cron.weekly/sqlite-vacuum.sh

WORKDIR $MEDIAWIKI_ROOT
EXPOSE 80
EXPOSE 7231
EXPOSE 10044

ENV URL "http://localhost"
ENV RESTBASE_URL ""
ENV MATHOID_URL ""

ENTRYPOINT ["/usr/bin/entrypoint"]
CMD ["nginx", "-g", "daemon off;"]
