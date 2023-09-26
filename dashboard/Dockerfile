FROM caddy:2.6.1-alpine
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

RUN \
    apk add --no-cache curl dumb-init yaml python3 py3-pip && \
    # Fira font
    mkdir -p /var/www/assets/fira && \
    curl -L -O https://github.com/mozilla/Fira/archive/refs/tags/4.202.zip && \
        unzip -j -o 4.202.zip \
            Fira-4.202/eot/FiraSans-Bold.eot \
            Fira-4.202/eot/FiraSans-Regular.eot \
            Fira-4.202/ttf/FiraSans-Bold.ttf \
            Fira-4.202/ttf/FiraSans-Regular.ttf \
            Fira-4.202/woff/FiraSans-Bold.woff \
            Fira-4.202/woff/FiraSans-Regular.woff \
            -d /var/www/assets/fira && \
            rm -f 4.202.zip && \
    # FontAwesome font
    curl -L -O https://use.fontawesome.com/releases/v6.2.0/fontawesome-free-6.2.0-web.zip && \
        unzip -o fontawesome-free-6.2.0-web.zip \
            fontawesome-free-6.2.0-web/css/* \
            fontawesome-free-6.2.0-web/webfonts/* \
            -d /var/www/assets/ && \
        mv /var/www/assets/fontawesome-free-6.2.0-web /var/www/assets/fontawesome && \
        rm -f fontawesome-free-6.2.0-web.zip && \
    # Pure CSS
    curl \
        -L -o /var/www/assets/pure-min.css \
        https://cdn.jsdelivr.net/npm/purecss@3.0.0/build/pure-min.css && \
    curl \
        -L -o /var/www/assets/grids-responsive-min.css \
        https://cdn.jsdelivr.net/npm/purecss@3.0.0/build/grids-responsive-min.css && \
    # python dependencies
    pip3 install --no-cache-dir -U pip && \
    pip3 install \
        --no-cache-dir \
        Jinja2==3.1.2 PyYAML==6.0.1 humanfriendly==10.0 && \
    apk del curl

ENV FQDN "generic.hotspot"
ENV NAME "My Hotspot"

COPY Caddyfile /etc/caddy/
COPY gen-home.py /src/
COPY templates /src/templates
COPY assets /var/www/assets
COPY fallback.html /var/www/fallback.html

# store python bytecode in image
RUN python3 -m compileall /src/gen-home.py && mv /src/__pycache__/*.pyc /usr/local/lib/

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/bin/python3", "/usr/local/lib/gen-home.cpython-310.pyc"]
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]

