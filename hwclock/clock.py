#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""hardware clock management Web UI

- set HW clock using system time
- set System time manually
- set system time using HW clock"""

# https://linux.die.net/man/8/hwclock
# https://afterthoughtsoftware.com/products/rasclock
# https://www.cyberciti.biz/faq/howto-set-date-time-from-linux-command-prompt/

import datetime
import os
import re
import subprocess
import urllib.parse
import zoneinfo
from pathlib import Path
from typing import Any
from dataclasses import dataclass

import dateutil.parser
from babel.dates import format_datetime
from jinja2 import Environment, select_autoescape

env = Environment(autoescape=select_autoescape(["html", "xml", "txt"]))


def yesno(value) -> str:
    """yes or no string from bool value"""
    return "yes" if bool(value) else "no"


def format_dt(dt: datetime.datetime, fmt="long", locale=None) -> str:
    return format_datetime(dt, fmt, locale=locale or getattr(env, "_locale", "en_GB"))


env.filters["yesno"] = yesno
env.filters["datetime"] = format_dt

template = env.from_string(
    """<html>
<head>
  <meta charset="utf-8">
  <title>Timekeeping manager</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style type="text/css">th { text-align: left; }</style>
  <style type="text/css">
  </style>
  <style type="text/css">
/* http://meyerweb.com/eric/tools/css/reset/
   v2.0 | 20110126
   License: none (public domain)
*/

html, body, div, span, applet, object, iframe,
h1, h2, h3, h4, h5, h6, p, blockquote, pre,
a, abbr, acronym, address, big, cite, code,
del, dfn, em, img, ins, kbd, q, s, samp,
small, strike, strong, sub, sup, tt, var,
b, u, i, center,
dl, dt, dd, ol, ul, li,
fieldset, form, label, legend,
table, caption, tbody, tfoot, thead, tr, th, td,
article, aside, canvas, details, embed,
figure, figcaption, footer, header, hgroup,
menu, nav, output, ruby, section, summary,
time, mark, audio, video {
    margin: 0;
    padding: 0;
    border: 0;
    font-size: 100%;
    font: inherit;
    vertical-align: baseline;
}
/* HTML5 display-role reset for older browsers */
article, aside, details, figcaption, figure,
footer, header, hgroup, menu, nav, section {
    display: block;
}
body {
    line-height: 1;
}
ol, ul {
    list-style: none;
}
blockquote, q {
    quotes: none;
}
blockquote:before, blockquote:after,
q:before, q:after {
    content: '';
    content: none;
}
table {
    border-collapse: collapse;
    border-spacing: 0;
}

  :root {
    --primary-color: #ff9500;
    --secondary-color: #f69000;
    --secondary-color: #9c5900;
    --text-color: #333333;
    --alt-text-color: #646b79;
  }
  html {
    width: 100%;
  }
  body {
    max-width: 50em;
    margin: auto;
    padding: 1em;
    color: var(--text-color);
    font-family: system-ui, sans-serif;
  }
  section {
    margin-top: 3em;
  }
  h1, h2 {
    color: var(--primary-color);
    margin-bottom: .5em;
  }
  h1 {
    font-size: 1.4em;
    font-weight: 600;
  }
  a {
    text-decoration: none;
    color: var(--text-color);
  }
  a:hover {
    color: var(--secondary-color);
  }
  section.status {
    border-radius: .25rem;
    padding: 1rem;
    margin-top: 1.5em;
  }

  section.status.success {
    background-color: #cfe2ff;
    border-left: 5px solid #9dc5fe;
    color:#062c65;
  }
  section.status.warning {
    background-color: #fff3cd;
    border-left: 5px solid #ffe69c;
    color:#664d03;
  }

  table {
    width: 100%;
    color: var(--alt-text-color);
    margin-top: 1.5em;
  }
  th {
    font-weight: 500;
  }
  th, td {
    padding: 0.2em 1em;
    border: .05rem solid var(--alt-text-color);
    vertical-align: middle;
  }

  p {
    line-height: 1.1em;
    margin-top: .2em;
    margin-bottom: .2em;
  }
  p.summary {
    font-weight: 500;
    margin-bottom: .8em;
  }
  form {
    margin-top: .8em;
  }
  input {
    padding: .4em;
    border: .1em solid var(--secondary-color);
    border-radius: .4em;
  }
  input[type=submit] {
    background-color: var(--primary-color);
    color: white;
    cursor: pointer;
  }
  input[type=submit]:hover {
    border-color: var(--primary-color);
    background-color: var(--secondary-color);
  }
  pre, code {
    white-space: pre;
  }
  code, td {
    font-family: monospace;
    font-size: .875em;
    color: var(--alt-text-color);
    word-wrap: break-word;
    line-height: 1.75em;
  }
  tr th {
    width: 25%;
  }
  tr td:last-child {
    width: 30%;
  }
  </style>
</head>
<body>
    <h1><a href="/">Timekeeping and Hardware Clock Management</a></h1>

    {% if tdctl.all_good %}
    <section class="status success">
      <p>System and Hardware date appears to be in sync.</p>
      <p>You don't need to do anything.</p>
    </section>
    {% elif tdctl.failed or not tdctl.parsed %}
    <section class="status danger">
      <p><code>timedatectl</code> did not run successfuly or its output could not be parsed.</p>
      <p>This might indicate an issue, please troubleshoot the running system via command line.</p>
    </section>
    {% else %}
    <section class="status warning">
      <ul>
      {% for warning in tdctl.warnings %}
        <li>{{ warning }}</li>
      {% endfor %}
      </ul>
    </section>
    {% endif %}

    {% if tdctl.parsed %}
      <table>
      <tr><th>System Time (UTC)</th><td>{{ tdctl.utc_time | datetime }}</td><td></td></tr>
      {% if self.has_rtc %}
      <tr><th>RTC Time (UTC)</th><td>{{ tdctl.rtc_utc_time | datetime }}</td><td>should be identical to previous</td></tr>
      {% endif %}
      <tr><th>NTP Synced</th><td>{{ tdctl.ntp_synced | yesno }}</td><td>should be if connected to Internet</td></tr>
      <tr><th>NTP Enabled</th><td>{{ tdctl.ntp_enabled | yesno }}</td><td>should be</td></tr>
      <tr><th>Can NTP</th><td>{{ tdctl.can_ntp | yesno }}</td><td>should be</td></tr>
      <tr><th>Timezone</th><td>{{ tdctl.timezone }}</td><td>should match configured timezone</td></tr>
      <tr><th>System Time (local)</th><td>{{ tdctl.local_time | datetime }}</td><td>Above-Timezone-aware version of UTC time on top. Timezone may use abbrevation.</td></tr>
      <tr><th>RTC in local time</th><td>{{ tdctl.rtc_in_local_tz | yesno }}</td><td>shouln't be</td></tr>
      <tr><th>RTC Battery Charger Enabled</th><td>{% if rtc_charger.is_present %}{{ rtc_charger.enabled | yesno }}{% else %}not-found{% endif %}</td><td>shouldn't be on fresh Pi5</td></tr>
      <tr><th>RTC Battery Charger Voltage</th><td>{% if rtc_charger.is_present %}{{ rtc_charger.charging_voltage }}{% else %}n/a{% endif %}</td><td></td></tr>
      </table>
    {% endif %}


    <section>
      <h1>Set Hardware Clock</h1>
      <p class="summary">❯ Copies System date into the Hardware clock.</p>
      <p>Use this option if the hardware clock is incorrect while the system one is not.</p>
      <p>This is what you would do to
      <strong>configure a newly plugged hardware clock</strong>
      using an <strong>🌐 online Pi</strong>.</p>

      <form action="/sys2hw" method="GET">
      <input type="submit" value="Copy System Time into Hardware Clock" />
      </form>
    </section>


    <section>
      <h1>Set System Date manually</h1>
      <p class="summary">❯ Specify a datetime to change the system clock to.</p>
      <p>This will only work with an <strong>offline Pi</strong>.</p>
      <p>Use the <em>Set Hardware Clock</em> afterwards so this specific date is
      recorded on the Hardware clock.</p>

      <p>Use this option if neither the Hardware Clock nor the System one is right.</p>

      <p>This is what you would do to
      <strong>configure a newly plugged hardware clock</strong>
      using an <strong>offline Pi</strong>.</p>

      <form action="/manual2hw" method="GET">
      <input name="datetime" type="text"
        pattern="[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]"
        required="required" placeholder="2017-12-01 20:30" />
      <input type="submit" value="Save this time as System one" />
      </form>
    </section>


    <section>
      <h1>Set System Date using Hardware Clock</h1>
      <p class="summary">❯ Use this option if the System Date is incorrect while the Hardware one is not.</p>
      <p>This step is not required as this is done
      upon system startup but can help you check the process.</p>
      <form action="/hw2sys" method="GET">
      <input type="submit" value="Update System Time with Hardware Clock one" />
      </form>
    </section>

    <section>
      <h1>Trigger NTP sync</h1>
      <p class="summary">❯ Try to force fetching time from the Internet</p>
      <p>Use this if NTP is not synchronized and you're convinced your Internet
      Connection is now working. Sync happens automatically but every failure
      to contact NTP servers increases the delay in-between attempts.</p>
      <p>This is done by restarting <code>systemd-timesyncd.service</code>. Restarting Pi is equally effective.</p>
      <form action="/ntpsync" method="GET">
      <input type="submit" value="Trigger NTP sync" />
      </form>
    </section>

    <section>
      <h1>Toggle RTC Battery Charger</h1>
      <p class="summary">❯ Enable or disable the Pi5 internal RTC battery charger</p>
      <p>Enable it for the Pi5 to charge the RTC battery (for it to last longer).</p>
      <p>You need to know the <strong>constant charging voltage</strong> it can sustain
      given it charges with a <strong>constant 3mA current</strong>.</p>
      <p>If using Raspberry's official Pi5 battery, charge at <code>3V</code>.</p>
      {% if not rtc_charger.is_present %}
      <p>RTC Charger not visible in sys tree. Not a Pi5?</p>
      {% else %}
      <form action="/charger-enable" method="GET">
            <input name="charging_voltage"
                   type="number"
                   min="{{ rtc_charger.charging_voltage_min }}"
                   max="{{ rtc_charger.charging_voltage_max }}"
                   step="0.1"
                   list="sampleChargingValues"
                   required="required" placeholder="3.0"
                   {% if rtc_charger.charging_voltage %}value="{{ rtc_charger.charging_voltage }}"{% endif %} />
            <datalist id="sampleChargingValues">
              <option value="3.0" label="3V official Pi5 battery"></option>
              </option>
            </datalist>

            <input type="submit" value="{% if rtc_charger.enabled %}Update{% else %}Enable{% endif %} RTC Charger" />
      </form>
      {% if rtc_charger.enabled %}
        <form action="/charger-disable" method="GET"><input type="submit" value="Disable RTC Charger" /></form>
      {% endif %}
      {% endif %}
    </section>
</body>
</html>
"""
)

DEVEL = bool(os.getenv("DEVEL"))
date_bin = "/bin/date"
hwclock_bin = "/sbin/hwclock"
hwclock_bin = "/bin/echo"
timedatectl_bin = "timedatectl" if DEVEL else "/sbin/timedatectl"
rtc0dir = (
    Path.cwd().joinpath("rtc0").resolve()
    if DEVEL
    else Path("/sys/devices/platform/soc/soc:rpi_rtc/rtc/rtc0/")
)

dt_re = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

# build list of timezone abbrevations
std = datetime.datetime(2024, 1, 1)
dst = datetime.datetime(2024, 6, 1)
tz_map = {}
for zone in zoneinfo.available_timezones():
    tz = zoneinfo.ZoneInfo(zone)
    tz_map[tz.tzname(std)] = tz
    tz_map[tz.tzname(dst)] = tz


@dataclass
class RTCBatteryCharger:
    charging_voltage: float
    charging_voltage_max: float
    charging_voltage_min: float

    @property
    def is_present(self) -> bool:
        return self.charging_voltage >= 0

    @property
    def enabled(self) -> bool:
        return self.charging_voltage > 0

    @classmethod
    def read_microvolt_sysfile(cls, fname: str) -> float:
        fpath = rtc0dir.joinpath(fname)
        if not fpath.exists():
            return -1.0
        return int(fpath.read_text()) / 1000000

    @classmethod
    def load(cls) -> "RTCBatteryCharger":
        return cls(
            charging_voltage=cls.read_microvolt_sysfile("charging_voltage"),
            charging_voltage_max=cls.read_microvolt_sysfile("charging_voltage_max"),
            charging_voltage_min=cls.read_microvolt_sysfile("charging_voltage_min"),
        )

    def save(self):
        rtc0dir.joinpath("charging_voltage").write_text(
            str(int(self.charging_voltage * 1000000)) if self.charging_voltage else "0"
        )


@dataclass
class TimedatectlData:
    retcode: int
    raw_output: str
    raw_data: dict[str, str]
    parsed: bool

    timezone: zoneinfo.ZoneInfo
    rtc_in_local_tz: bool
    can_ntp: bool
    ntp_enabled: bool
    ntp_synced: bool
    local_time: datetime.datetime
    has_rtc: bool
    rtc_time: datetime.datetime

    def __init__(self, *, retcode: int, output: str):
        self.retcode = retcode
        self.raw_output = output

        self.raw_data = {}
        for line in self.raw_output.splitlines():
            if not line.strip():
                continue
            parts = line.split("=", 1)
            self.raw_data[parts[0].strip()] = (
                parts[-1].strip() if len(parts) > 1 else ""
            )

        try:
            self.parse()
        except Exception:
            raise
            self.parsed = False
        else:
            self.parsed = True

    def parse(self):
        def parse_date(text) -> datetime.datetime:
            return dateutil.parser.parse(text, tzinfos=tz_map, fuzzy=True)

        def parse_tz(text: str) -> zoneinfo.ZoneInfo:
            return zoneinfo.ZoneInfo(text.strip())

        self.timezone = parse_tz(self.raw_data["Timezone"])
        self.rtc_in_local_tz = self.raw_data["LocalRTC"] == "yes"
        self.can_ntp = self.raw_data["CanNTP"] == "yes"
        self.ntp_enabled = self.raw_data["NTP"] == "active"
        self.ntp_synced = self.raw_data["NTPSynchronized"] == "yes"
        self.local_time = parse_date(self.raw_data["TimeUSec"])
        self.has_rtc = "RTCTimeUSec" in self.raw_data
        if self.has_rtc:
            self.rtc_time = parse_date(self.raw_data["RTCTimeUSec"])

    @property
    def failed(self) -> bool:
        return self.retcode != 0

    @property
    def rtc_utc_time(self) -> datetime.datetime:
        if not self.has_rtc:
            raise OSError("No RTC detected")
        return self.rtc_time.astimezone(datetime.UTC)

    @property
    def utc_time(self) -> datetime.datetime:
        return self.local_time.astimezone(datetime.UTC)

    @property
    def sys_and_rtc_synced(self) -> bool:
        if not self.has_rtc:
            return True
        return abs((self.rtc_utc_time - self.utc_time).total_seconds()) <= 120

    @property
    def all_good(self) -> bool:
        return all([self.ntp_enabled, self.ntp_synced, self.sys_and_rtc_synced])

    @property
    def warnings(self) -> list[str]:
        warnings = []
        out_of_sync = datetime.datetime(2025, 1, 1, tzinfo=datetime.UTC)

        if not self.ntp_enabled:
            warnings.append(
                "NTP Syncing is disabled. That's unexpected. "
                "System clock will not auto sync when online."
            )
        if not self.ntp_synced:
            warnings.append(
                "System time is not synced via NTP. It's normal when offline."
            )
        if self.utc_time <= out_of_sync:
            warnings.append("System time is in the past.")
        if self.has_rtc and self.rtc_time <= out_of_sync:
            warnings.append("RTC time is in the past.")

        return warnings


def query_status():
    os.environ["LANG"] = "C"
    os.environ["LC_ALL"] = "C"
    ps = subprocess.run(
        ["/usr/bin/env", timedatectl_bin, "show"],
        capture_output=True,
        text=True,
        env=os.environ,
    )
    status_code = ps.returncode
    status_output = ps.stdout.strip()
    ps = subprocess.run(
        ["/usr/bin/env", timedatectl_bin, "show-timesync"],
        capture_output=True,
        text=True,
        env=os.environ,
    )
    time_code = ps.returncode
    time_output = ps.stdout.strip()
    return TimedatectlData(
        retcode=status_code + time_code, output=status_output + "\n" + time_output
    )


def get_output(command: list[str] | str) -> str:
    ps = subprocess.run(command, capture_output=True, text=True)
    stdout = ps.stdout.strip()
    if ps.returncode == 0:
        return stdout
    if ps.returncode == 1 and "hwclock" in command[0]:
        return "ERROR: no hardware clock installed?"
    return "ERROR: {}".format(stdout)


def format(template: str, context: dict[str, str]) -> str:
    for key, value in context.items():
        template = template.replace("{" + key + "}", value)
    return template


def application(env, start_response):
    output = ""
    context: dict[str, Any] = {
        "tdctl": query_status(),
        "rtc_charger": RTCBatteryCharger.load(),
        "system_time": get_output([date_bin, '+"%Y-%m-%d %H:%M:%S.000000%z"'])[1:-1],
        "hardware_time": get_output([hwclock_bin, "-r"]),
    }

    if env["REQUEST_URI"] == "/sys2hw":
        # write system datetime into hardware clock
        output = get_output([hwclock_bin, "-w"])

    if env["REQUEST_URI"] == "/hw2sys":
        # set system datetime using hardware clock
        output = get_output([hwclock_bin, "-s"])

    if env["REQUEST_URI"] == "/ntpsync":
        output = get_output(["systemctl", "restart", "systemd-timesyncd.service"])

    if env["REQUEST_URI"].startswith("/charger-disable"):
        context["rtc_charger"].charging_voltage = 0
        context["rtc_charger"].save()

    if env["REQUEST_URI"].startswith("/charger-enable"):
        cv = urllib.parse.unquote_plus(env["QUERY_STRING"]).split("charging_voltage=")[
            1
        ]
        try:
            charging_voltage = float(cv)
        except Exception:
            context["error"] = "Unreadable voltage"
        else:
            if (
                charging_voltage >= context["rtc_charger"].charging_voltage_min
                and charging_voltage <= context["rtc_charger"].charging_voltage_max
            ):
                context["rtc_charger"].charging_voltage = charging_voltage
                context["rtc_charger"].save()
            else:
                context["error"] = "Invalid charging voltage value"

    if env["REQUEST_URI"].startswith("/manual2sys"):
        # write a manual datetime into hardware clock
        try:
            dt = urllib.parse.unquote_plus(env["QUERY_STRING"]).split("datetime=")[1]
            if dt_re.match(dt):
                output = get_output([date_bin, "-s", dt])
            else:
                output = "ERROR: invalid format"
        except Exception as exp:
            output = "ERROR: {}".format(exp)

    context["output"] = output

    if context["tdctl"].retcode != 0:
        context["error"] = "timedatectl failed. Try refreshing?"

    # build raw table from timedatectl
    output_html = "<table>\n"
    for key, value in context["tdctl"].raw_data.items():
        output_html += f"<tr><th>{key}</th><td>{value}</td></tr>\n"
    output_html += "</table>\n"
    context["raw_table"] = output_html

    if context["tdctl"].parsed:
        ...

    print(context["rtc_charger"])

    start_response("200 OK", [("Content-Type", "text/html")])
    # return [format(template, context).encode("utf-8")]
    return [template.render(context).encode("utf-8")]
