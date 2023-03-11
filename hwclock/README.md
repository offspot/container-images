hwclock
=======

An Alpine-based image running a small web server allowing configuration of an hardware clock.

## Usage

```yaml
docker run -p 80:80 --cap-add CAP_SYS_TIME --device /dev/rtc ghcr.io/offspot/hwclock
```

- ⚠️ Capability `CAP_SYS_TIME` is required.
- You can use without a `--device` but you'll only be able to manually set System date.
- If you don't know device path, you can run with `--privileged`. Also removes need for `CAP_SYS_TIME`.


---

The Web UI allows three actions:

- Set Hardware Clock (using System date)
- Set System Date manually
- Set System Date using Hardware Clock

Manually setting System date can be used even if the host does not have an hardware clock and shall remain accurate for a reasonnable amount of time. 
