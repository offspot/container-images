hwclock
=======

An Alpine-based image running a small web server allowing configuration of an hardware clock.

## Usage

⚠️ Capability `CAP_SYS_TIME` is required.

```yaml
docker run -p 80:80 --cap-add CAP_SYS_TIME ghcr.io/offspot/hwclock
```

Web service is exposed on port `80`.

---

The Web UI allows three actions:

- Set Hardware Clock (using System date)
- Set System Date manually
- Set System Date using Hardware Clock

Manually setting System date can be used even if the host does not have an hardware clock and shall remain accurate for a reasonnable amount of time. 
