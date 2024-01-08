# file-browser

A [tinyfilemanager](https://github.com/prasathmani/tinyfilemanager)-based image for managing on-device files

## Usage

```sh
docker run -p 80:80 -v /some/folder:/data:ro ghcr.io/offspot/file-manager
```

## Configuration

Just mount your files tree to `/data`. If you don't plan on editing them, mount it read-only.

Configuration is done most via environment variables

| Variable            | Default               | Usage                                                                                                                                |
| ------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `ACCESS_MODE`       | `listing`             | One of `listing` (no auth, read-only), `manager` (auth-required, editable) and `mixed` (`listing` on `/` and `manager` on `/admin/`) |
| `APP_URL`           |                       | URL to the app. Not used in `mixed` mode. Allows better-looking URLs (`index.php` not visible)                                       |
| `UI_LANG`           | `en`                  | UI Language (ISO-636-1), must be a supported one                                                                                     |
| `UI_TIMEZONE`       | `Etc/UTC`             | Timezone to use to display file details.                                                                      |
| `ADMIN_USERNAME`    | `admin`               | Username for authentication (for `manager` and `mixed`) modes                                                                        |
| `ADMIN_PASSWORD`    | `admin@123`           | Password for authentication (for `manager` and `mixed`) modes                                                                        |

