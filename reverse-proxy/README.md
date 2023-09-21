# reverse-proxy

Caddy-based reverse-proxy to serve all our services

## Configuration

Configuration is done solely via environment variables

| Variable             | Default            | Usage                                                                                                                                                           |
| -------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `FQDN`               | `generic.hotspot`  | Hostname to serve at                                                                                                                                            |
| `SERVICES`           |                    | `,`-separated list of services to configure. Either `name` (service-name) or `name:target:port` for special ones. Ex `kiwix,edupi,api.edupi:edupi:8080`         |
| `PROTECTED_SERVICES` |                    | `,`-separated list of services to password-protect<sup>1</sup>. `name:username:password` format (clear text password). Ex `kiwix,admin,passW0rd`   | 
| `FILES_MAPPING`      |                    | `,`-separated list of `{subdomain}:{subfolder}` mapping for files-related services (using a single files service). Ex `nomad:nomadeducation,download-zims:zims` |
| `DEBUG`              |                    | Set any value to enable Caddy debug output                                                                                                                      |

Although served as a docker-service, `home` is not to be listed as it has no user-facing endpoint.

All simple services are expected to be reachable from reverse-proxy container at `{service}:80`.

**<sup>1</sup>**: At the moment, password-protection uses HTTP Basic which is not secure over HTTP (credentials sent clearly).
