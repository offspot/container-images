# reverse-proxy

Caddy-based reverse-proxy to serve all our services

## Configuration

Configuration is done solely via environment variables

| Variable        | Default            | Usage                                                                                                                                                           |
| --------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `FQDN`          | `generic.hotspot`  | Hostname to serve at                                                                                                                                            |
| `SERVICES`      |                    | `,`-separated list of services to configure. Ex `kiwix,edupi`                                                                                                   |
| `FILES_MAPPING` |                    | `,`-separated list of `{subdomain}:{subfolder}` mapping for files-related services (using a single files service). Ex `nomad:nomadeducation,download-zims:zims` |
| `DEBUG`         |                    | Set any value to enable Caddy debug output                                                                                                                      |

Although served as a docker-service, `home` is not to be listed as it has no user-facing endpoint.

All services are expected to be reachable from reverse-proxy container at `{service}:80`.
