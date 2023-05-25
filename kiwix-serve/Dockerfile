FROM alpine:3
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

# TARGETPLATFORM is injected by docker build
ARG TARGETPLATFORM
ARG VERSION

RUN set -e && \
    # default (no VERSION set) means latest release
    # `dev` version means today's nightly
    if [ "$VERSION" = "dev" ] ; then export VERSION="$(date +"%Y-%m-%d")" ; fi && \
    apk --no-cache add dumb-init curl && \
    echo "TARGETPLATFORM: $TARGETPLATFORM" && \
    if [ "$TARGETPLATFORM" = "linux/386" ]; then ARCH="i586"; \
    # linux/arm64/v8 points to linux/arm64
    elif [ "$TARGETPLATFORM" = "linux/arm64/v8" \
        -o "$TARGETPLATFORM" = "linux/arm64" ]; then ARCH="aarch64"; \
    # linux/arm translates to linux/arm/v7
    elif [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then ARCH="armv8"; \
    elif [ "$TARGETPLATFORM" = "linux/arm/v6" ]; then ARCH="armv6"; \
    elif [ "$TARGETPLATFORM" = "linux/amd64/v3" \
        -o "$TARGETPLATFORM" = "linux/amd64/v2" \
        -o "$TARGETPLATFORM" = "linux/amd64" ]; then ARCH="x86_64"; \
    # we dont suppot any other arch so let it fail
    else ARCH="unknown"; fi && \
    # default download source is releases
    export DLFROM="https://download.kiwix.org/release/kiwix-tools" && \
    # change download source for nightlies (VERSION is a date)
    if [[ "$VERSION" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] ; then \
    export DLFROM="https://download.kiwix.org/nightly/${VERSION}" ; fi && \
    # only non-specified (latest) release doesnt include VERSION in filename (sep by dash)
    if [ ! -z "$VERSION" ] ; then export VERSION="-$VERSION" ; fi && \
    export filename="kiwix-tools_linux-$ARCH$VERSION.tar.gz" && \
    # download requested kiwix-tools version
    url="$DLFROM/$filename" && \
    echo "URL: $url" && \
    if [ -z "$VERSION" ] ; then \
    # fetch actual filename (latest release is a redirect)
    export foldername="$(curl --head --insecure --location --silent --no-buffer $url |grep -m 1 'location:' | cut -d '/' -f 6 | sed 's/.tar.gz//' | sed 's/\r//')"; \
    else export foldername=$(echo -n $filename|sed 's/.tar.gz//'); fi && \
    echo "foldername: $foldername" && \
    # download and extract just kiwix-serve
    curl --insecure --location $url | tar -xzo -f - -C /usr/local/bin/ --strip-components 1 -- "$foldername/kiwix-serve" && \
    # only needed in dockerfile
    apk del curl

# expose kiwix-serve default port
EXPOSE 80

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["kiwix-serve", "--help"]
