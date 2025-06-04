# captive-portal image

Offspot image to trigger a *captive-portal-like* web UI on WiFi connection to inform users about our main content URL

## Dependencies

- Static WLAN connection
- WiFI Access Point (`hostapd`)
- DNS server (`dnsmasq`)
- DHCP server (`dnsmasq`)
- IP forwarding and routing

## Configuration

Configuration is done mostly via environment variables

| Variable            | Default                 | Usage                                                             |
| ------------------- | ----------------------- | ----------------------------------------------------------------- |
| `HOTSPOT_NAME`      | `Kiwix Hotspot`         | Name of the hotspot/SSSID, displayed on portal and as title             |
| `HOTSPOT_FQDN`      | `default.hotspot`       | URL (hostname actualy) to point users to.                         |
| `HOSTPOT_IP`        | `192.168.144.1`         | IP to redirect unregistered HTTP traffic to                       |
| `CAPTURED_NETWORKS` | `192.168.144.128/25     | `|` separated networks to limit *capture* to. Otherwise any       |
| `TIMEOUT`           | `60`                    | Minutes after which to consider an *inactive* client unregistered |
| `FOOTER_NOTE`       |                         | Small text displayed on footer of portal                          |
| `DEBUG`             |                         | Set any value to trigger debug logging                            |
| `DB_PATH`           | `portal-users.db`       | Path to store the SQLite DB to                                    |
| `FILTER_MODULE`     | `dummy_portal_filter`   | Name of python module to use as *filter*. `portal_filter` is ours |
| `DONT_SETUP_FILTER` |                         | Set any value to skip *filter module* setup on start              |
| `ALWAYS_ONLINE`     |                         | Assumes system should be connected to Internet and route traffic  |

A volume **is required** at `/var/run/internet`.
This should be a text file with either `online` or `offline` content, informing about connectivity status. This files is checked for updates periodically.

It is used to decide whether to forward foreign traffic to the portal or not.

## deployment notes

- firewall resides in Kernel and is thus unreachable by containers.
- for a container to talk to the firewall, it requires the `NET_ADMIN` capability.
- `NET_ADMIN` allows accessing the firewall but container's network stack (and firewall) is still isolated.
- container must be ran in `host` `network_mode` for access the host's firewall kernel space.
- `host` mode is not compatible with other networks. In `host` mode, container is solely in this network (the one of the host).
- container in `host` mode cannot be reached by other containers using in-docker communication such as aliases.
- it is thus not possible for a reverse-proxy on port `:80` to reverse proxy the portal as it cannot communicate with it.
- `host` mode is not compatible with `ports` definition as those are implemented as NAT forwards between host and containers.
- All exposed ports of an `host` mode container are directly exposed on the host. An `host` container binding to a port already mapped by another container will conflict. Which ever bound to it first will use it.
- Only in `host` mode will the client requests hold their actual IP addresses. Otherwise, it will be the docker interface IP beacause of the NAT/masquerade (unless you use an host-level reverse proxy setting `X-Forwarded-For`).
- `host` mode is only available on Linux host. Not on macOS nor Windows.
- a custom self-signed certificate is created in entrypoint because it is accessed without a valid host (`:2443`)
- HTTPs request to the portal using an IP (ie. without a `Host` header: `https://192.168.144.1`) fails for some reason. It's not a warning issue.
- DNS server must be working and configured on clients (via DHCP) for clients to query the server, otherwise request fail without ever hitting the server.

Offline and Online work differently. A connection-status file is used to toggle between modes.

## when online

`online` server is a server expected to be online and thus routing actual, non-hotspot, traffic over the internet. 

- regular DNS upstream server is OK as HTTP requests will be intercepted

## when offline

- DNS server cannot simply reference upstream servers as those are unreachable and would thus result in network error at client level.
- DNS must spoof response to return any non-local IP.
- It's important spoofed-IP is different than hotspot IP (pass it in `CAPTURED_ADDRESS`) so client's HTTP requests go through the router stack and get intercepted

### Sample compose config

```yaml
services:
  home-portal:
    network_mode: host
    cap_add:
      - NET_ADMIN
    container_name: home-portal
    image: ghcr.io/offspot/captive-portal:latest
    environment:
      HOTSPOT_NAME: My hotspot
      HOTSPOT_IP: "192.168.144.1"
      HOTSPOT_FQDN: demo.offspot
      CAPTURED_NETWORKS: "192.168.144.128/25"
      CAPTURED_ADDRESS: "198.51.100.1"
    volumes:
    - "/var/run/internet:/var/run/internet:ro"
    expose:
      - "2080"
      - "2443"
```
