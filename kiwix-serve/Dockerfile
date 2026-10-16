ARG VERSION=latest

# kiwix-tools is multi-arch upstream
FROM ghcr.io/kiwix/kiwix-tools:$VERSION
LABEL org.opencontainers.image.source=https://github.com/offspot/container-images

# remove other kiwix-tools
RUN find /usr/local/bin -name 'kiwix-*' -not -name 'kiwix-serve' -delete

ENV DATA_PATH=/data

RUN printf "#!/bin/sh\n\
# a sorted list of ZIM files in passed folder or DATA_PATH env\n\
TARGET=\$1\n\
[ ! -n \"\${1}\" ] && TARGET=\$DATA_PATH\n\
LC_ALL=C find \$TARGET -name '*.zim' | sort \n" > /usr/local/bin/list-zims && chmod +x /usr/local/bin/list-zims
RUN printf "#!/bin/sh\n\
# kiwix-serve shortcut without passing ZIM paths (assumes DATA_PATH env)\n\
exec /usr/local/bin/kiwix-serve \"\$@\" \$(list-zims)\n" > /usr/local/bin/kiwix-serve-zims && chmod +x /usr/local/bin/kiwix-serve-zims

VOLUME /data

CMD ["kiwix-serve", "--help"]
