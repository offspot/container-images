# EduPi

A file-sharing service image for [edupi](https://github.com/offspot/edupi). Allows exposing a tree of files to view (images, PDF, videos) and/or download. An *admin* account allows updating the file tree.

## Usage

```sh
docker run -p 80:80 ghcr.io/offspot/edupi
```

```sh
docker run -p 80:80 \
  -e ADMIN_USERNAME=admin -e ADMIN_PASSWORD=my-secret \
  -e SRC_DIR=/data/source \
  -v /content/edupi:/data \
  -v /branding/favicon.ico:/var/lib/edupi/favicon.ico \
  ghcr.io/offspot/edupi
```

### Configuration

No configuration is required but you'll likely want to set some of the following environment variables:

| Variable         | Usage                                                        |
| -----------------| ------------------------------------------------------------ |
| `ADMIN_USERNAME` | Username of the *admin* user. Requires setting the password. |
| `ADMIN_PASSWORD` | Password of the *admin* user.                                |
| `SRC_DIR`        | In-container path of the folder to import files from.        |

Note that registered users access the special UI at [`/custom`](http://localhost/custom). A link is only present on homepage is there is no imported data.

### Storage persistence

If you want to persist EduPi's data, you'll need to bind some paths to a persistent storage.

**TL;DR**: bind `/data`

| Path         | Usage                                                        |
| --- | --- |
| `/data`                      | All user-modifiable data |
| `/data/database`              | Only EduPi's database (SQLite) |
| `/data/media`                | EduPi's files are stored here. Their thumbnails inside a `thumbnails` sub-folder |
| `/data/log`                  | nginx's access logs |
| `/data/stats`                | EduPi's statistics based off (on-demand) reading of nginx log |
| `/var/lib/edupi/favicon.ico` | Default EduPi favicon |

**Important**: when importing existing content (via `SRC_DIR` environ), make sure to mount that source directory in the same bound volume as `/data/media` so that files are moved effisciently.
