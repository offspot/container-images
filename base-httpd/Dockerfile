FROM alpine:3 as builder
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

RUN apk --no-cache add build-base gcc make
# building thttpd with JSON Content-Type support
# and a hack allowing it to serve files with execution permissions
# which is needed to server any file from /boot (fat32)
RUN wget --progress=dot:giga https://www.acme.com/software/thttpd/thttpd-2.29.tar.gz && \
    tar xf thttpd-2.29.tar.gz && \
    rm -f ./thttpd-2.29.tar.gz && \
    cd thttpd-2.29 && \
    echo "json application/json" >> mime_types.txt && \
    sed -i 's/^    if ( hc->sb.st_mode \& S_IXOTH )$/    if ( hc->sb.st_mode \& S_IXOTH \& 0 )/' libhttpd.c && \
    ./configure --host="$(uname -m)-linux" && \
    make && \
    cd .. && \
    mv thttpd-2.29/thttpd / && \
    rm -rf ./thttpd-2.29

FROM alpine:3
COPY --from=builder /thttpd /usr/sbin/thttpd
WORKDIR /var/www/
EXPOSE 80
ENTRYPOINT ["/usr/sbin/thttpd"]
CMD ["-D", "-l", "/dev/stdout", "-nos", "-r"]
