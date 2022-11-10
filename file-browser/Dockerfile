FROM caddy:2.6.1-alpine

RUN mkdir -p /data
COPY config.json /config/caddy/autosave.json

CMD ["caddy", "run", "--resume"]
