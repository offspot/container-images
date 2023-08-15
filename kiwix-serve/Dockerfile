ARG VERSION=latest

# kiwix-tools is multi-arch
FROM ghcr.io/kiwix/kiwix-tools:$VERSION
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

# remove other kiwix-tools
RUN find /usr/local/bin -name 'kiwix-*' -not -name 'kiwix-serve' -delete

CMD ["kiwix-serve", "--help"]
