# dumb-init to use as entrypoint so it can forward signals to our CMD
FROM debian:bullseye-slim as builder
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
    build-essential ca-certificates musl-tools wget unzip make \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # compile dumb-init ; \
    && wget -nv https://github.com/Yelp/dumb-init/archive/refs/tags/v1.2.5.zip \
    && unzip v1.2.5.zip && cd dumb-init-1.2.5 && CC=musl-gcc make

# declare build option ARCH if not using buildx
ARG ARCH=
# declare version to build image for
ARG VERSION=

# alpine is a multi-arch image
FROM alpine:3
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

# TARGETARCH is injected by buildx
ARG TARGETARCH
ARG VERSION
ARG ARCH

# copy built dumb-init
COPY --from=builder /dumb-init-1.2.5/dumb-init /usr/bin/dumb-init

# find and store arch in image, using (in this order):
# $TARGETARCH || --build-arg ARCH (not using buildx) || amd64
RUN echo "amd64" > /etc/docker_arch && \
    if [ ! -z "$ARCH" ] ; then echo "$ARCH" > /etc/docker_arch ; fi && \
    if [ ! -z "$TARGETARCH" ] ; then echo "$TARGETARCH" > /etc/docker_arch ; fi \
    # decide which kiwix arch to download later (`armhf` for all arm* and x86_64 otherwise); \
    && if [ $(cat /etc/docker_arch) = "arm64" ] ; then echo "aarch64" > /etc/kiwix_arch ; elif [ $(cut -c 1-3 /etc/docker_arch) = "arm" ] ; then echo "armhf" > /etc/kiwix_arch ; else echo "x86_64" > /etc/kiwix_arch ; fi \
    # dev version means latest
    && if [ "$VERSION" = "dev" ] ; then export VERSION="" ; fi \
    # change download source for nightlies (VERSION is a date)
    && export DLFROM="https://download.kiwix.org/release/kiwix-tools/" \
    && if [[ "$VERSION" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] ; then export DLFROM="https://download.kiwix.org/nightly/${VERSION}" ; fi \
    # fallback version if not suppplied; \
    && if [ ! -z "$VERSION" ] ; then export VERSION="-$VERSION" ; fi \
    # Install kiwix-tools
    && url="$DLFROM/kiwix-tools_linux-$(cat /etc/kiwix_arch)$VERSION.tar.gz" \
    && echo "URL: $url" \
    && wget -q -O - $url | tar -xz \
    && mv kiwix-tools*/kiwix-serve /usr/local/bin/ \
    && rm -r kiwix-tools*

# expose kiwix-serve default port
EXPOSE 80

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["kiwix-serve", "--help"]
