FROM alpine:3.19
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

RUN \
    apk add --no-cache curl dumb-init yaml python3 lighttpd \
    # Fira font
    && mkdir -p /var/www/assets/fira \
    && curl -L -O https://github.com/mozilla/Fira/archive/refs/tags/4.202.zip \
        && unzip -j -o 4.202.zip \
            Fira-4.202/eot/FiraSans-Bold.eot \
            Fira-4.202/eot/FiraSans-Regular.eot \
            Fira-4.202/ttf/FiraSans-Bold.ttf \
            Fira-4.202/ttf/FiraSans-Regular.ttf \
            Fira-4.202/woff/FiraSans-Bold.woff \
            Fira-4.202/woff/FiraSans-Regular.woff \
            -d /var/www/assets/fira \
            && rm -f 4.202.zip \
    # FontAwesome font
    && curl -L -O https://use.fontawesome.com/releases/v6.2.0/fontawesome-free-6.2.0-web.zip \
        && unzip -o fontawesome-free-6.2.0-web.zip \
            fontawesome-free-6.2.0-web/css/* \
            fontawesome-free-6.2.0-web/webfonts/* \
            -d /var/www/assets/ \
        && mv /var/www/assets/fontawesome-free-6.2.0-web /var/www/assets/fontawesome \
        && rm -f fontawesome-free-6.2.0-web.zip \
    # Pure CSS
    && curl \
        -L -o /var/www/assets/pure-min.css \
        https://cdn.jsdelivr.net/npm/purecss@3.0.0/build/pure-min.css \
    && curl \
        -L -o /var/www/assets/grids-responsive-min.css \
        https://cdn.jsdelivr.net/npm/purecss@3.0.0/build/grids-responsive-min.css \
    # python dependencies
    && python3 -m venv /usr/local/bin/gen-home_env \
    && /usr/local/bin/gen-home_env/bin/pip3 install --no-cache-dir -U pip \
    && /usr/local/bin/gen-home_env/bin/pip3 install \
        --no-cache-dir \
        Jinja2==3.1.2 PyYAML==6.0.1 humanfriendly==10.0 libzim==3.4.0 \
    && apk del curl

ENV FQDN "generic.hotspot"
ENV NAME "My Hotspot"
# path in which to find code (templates)
ENV SRC_DIR "/src"
# path to packages YAML file
ENV PACKAGES_PATH "/src/home.yaml"
# path to write home HTML and assets file
ENV DEST_DIR "/var/www"
# folder storing ZIM files. unless DONT_UPDATE_PACKAGES, ZimPackages not in the folder
# will be removed (disabled) from packages.yaml
# discovered ZIM (not in YAML) will be added
ENV ZIM_DIR "/data/zims"
# set to skip packages.yaml update on start (reading ZIM_PATH folder)
ENV DONT_UPDATE_PACKAGES ""

# templates to write ZIM Package links to reader and ZIM downloads.
# Available patterns (to be replaced): `{fqdn}`, `{zim_name}`, `{zim_filename}`
ENV KIWIX_READER_LINK_TPL "//kiwix.{fqdn}/viewer#{zim_name}"
ENV KIWIX_DOWNLOAD_LINK_TPL "//zim-download.{fqdn}/{zim_filename}"

# WARN: this break apk but saves a lot of space
# it's OK on prod but comment it during dev if you need packages
RUN apk del apk-tools ca-certificates-bundle

COPY gen-home.py refresh-zims.py /src/
COPY templates /src/templates
COPY assets /var/www/assets
COPY fallback.html /var/www/fallback.html
COPY home.yaml /src/
COPY lighttpd.conf /etc/lighttpd/
COPY entrypoint.sh /usr/local/bin/

# store python bytecode in image
RUN /usr/local/bin/gen-home_env/bin/python3 -m compileall /src/gen-home.py /src/refresh-zims.py && mv /src/__pycache__/*.pyc /usr/local/bin/gen-home_env/lib/

HEALTHCHECK --interval=10s --timeout=2s CMD ["/bin/ls", "/tmp/.ready"]
ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]

