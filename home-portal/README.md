# home-portal image

Offspot image to trigger a *captive-portal-like* web UI on WiFi connection to inform users about our main content URL

## Configuration

Configuration is done solely via environment variables

| Variable            | Default               | Usage                                                             |
| ------------------- | --------------------- | ----------------------------------------------------------------- |
| `HOTSPOT_NAME`      | `default`             | Name of the hotspot, displayed on portal and as title             |
| `HOTSPOT_FQDN`      | `default.hotspot`     | URL (hostname actualy) to point users to.                         |
| `HOSTPOT_IP`        | `192.168.2.1`         | IP to redirect unregistered HTTP traffic to                       |
| `CAPTURED_NETWORKS` | `192.168.2.128/25     | `|` separated networks to limit *capture* to. Otherwise any       |
| `TIMEOUT`           | `60`                  | Minutes after which to consider an *inactive* client unregistered |
| `FOOTER_NOTE`       |                       | Small text displayed on footer of portal                          |
| `DEBUG`             |                       | Set any value to trigger debug logging                            |
| `DB_PATH`           | `portal-users.db`     | Path to store the SQLite DB to                                    |
| `FILTER_MODULE`     | `dummy_portal_filter` | Name of python module to use as *filter*. `portal_filter` is ours |
| `DONT_SETUP_FILTER` |                       | Set any value to skip *filter module* setup on start              |


## deployment notes

- firewall resides in Kernel and is thus unreachable by containers.
- for a container to talk to the firewall, it requires the `NET_ADMIN` capability.
- `NET_ADMIN` allows accessing the firewall but container's network stack (and firewall) is still isolated.
- container must be ran in `host` `network_mode` for access the host's firewall kernel space.
- `host` mode is not compatible with other networks. In `hsot` mode, container is solely in this network (the one of the host).
- container in `host` mode cannot be reached by other containers using in-docker communication such as aliases.
- it is thus not possible for a reverse-proxy on port `:80` to reverse proxy the portal as it cannot communicate with it.
- `host` mode is not compatible with `ports` definition as those are implemented as NAT forwards between host and containers.
- All exposed ports of an `host` mode container are directly exposed on the host. An `host` container binding to a port already mapped by another container will conflict. Which ever bound to it first will use it.
- Only in `host` mode will the client requests hold their actual IP addresses. Otherwise, it will be the docker interface IP beacause of the NAT/masquerade (unless you use an host-level reverse proxy setting `X-Forwarded-For`).
- `host` mode is only available on Linux host. Not on macOS nor Windows.

### Sample compose config

```yaml
services:
  home-portal:
    network_mode: host
    cap_add:
      - NET_ADMIN
    container_name: home-portal
    image: ghcr.io/offspot/home-portal:latest
    environment:
      HOTSPOT_NAME: My hotspot
      HOTSPOT_IP: "192.168.2.1"
      HOTSPOT_FQDN: demo.offspot
      CAPTURED_NETWORKS: "192.168.2.128/25"
    expose:
      - "2080"
      - "2443"
```


- clean-up job
- test without internet
