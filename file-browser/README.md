# file-browser

An Caddy-based image for serving static files

## Usage

```sh
docker run -p 80:80 -v /some/folder:/data:ro offspot/file-browser
```

## Configuration

Just mount your files try to `/data`.

- Include your homepage as `index.html` if you have one.
- Include and properly reference any support files (CSS, JS, font, etc).
- Include your own favicon(s).
