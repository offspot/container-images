FROM caddy:2.6.1-alpine
LABEL org.opencontainers.image.source https://github.com/offspot/container-images

RUN mkdir -p /data
COPY config.json /config/caddy/autosave.json

CMD ["caddy", "run", "--resume"]
