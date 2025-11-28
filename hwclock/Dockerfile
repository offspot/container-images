FROM alpine:3.22
LABEL org.opencontainers.image.source=https://github.com/offspot/container-images

RUN apk add --no-cache dumb-init uwsgi uwsgi-http uwsgi-python3

COPY clock.py /src/clock.py

EXPOSE 80
STOPSIGNAL SIGQUIT

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["uwsgi", "--plugins=http,python", "--master", "--http=:80", "--process=1", "--wsgi-file=/src/clock.py"]
