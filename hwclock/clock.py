#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" hardware clock management Web UI

    - set HW clock using system time
    - set System time manually
    - set system time using HW clock """

# https://linux.die.net/man/8/hwclock
# https://afterthoughtsoftware.com/products/rasclock
# https://www.cyberciti.biz/faq/howto-set-date-time-from-linux-command-prompt/

import re
import subprocess
import urllib.parse
from typing import Dict

template = """<html>
<head>
  <meta charset="utf-8"><style type="text/css">th { text-align: left; }</style></head>
<body>
  <h1><a href="/">Hardware & System Time Management</a></h1>
  {output}
  <table>
    <tr><th>System date</th><td>{system_time}</td></tr>
    <tr><th>Hardware date</th><td>{hardware_time}</td></tr>
  </table>

  <h1>Set Hardware Clock</h1>

  <p>Copies System date into the Hardware clock.</p>
  <p>Use this option if the hardware clock is incorrect while the system one is not.</p>
  <p>This is what you would do to
  <strong>configure a newly plugged hardware clock</strong>
  using an <strong>🌐 online Pi</strong>.</p>

  <form action="/sys2hw" method="GET">
    <input type="submit" value="Copy System Time into Hardware Clock" />
  </form>

  <hr />

  <h1>Set System Date manually</h1>
  <p>Specify a datetime to change the system clock to.</p>
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

  <hr />

  <h1>Set System Date using Hardware Clock</h1>
  <p>Use this option if the System Date is incorrect while the Hardware one is not.</p>
  <p>This step is not required as this is done
  upon system startup but can help you check the process.</p>
  <form action="/hw2sys" method="GET">
    <input type="submit" value="Update System Time with Hardware Clock one" />
  </form>

</body>
</html>
"""

date_bin = "/bin/date"
hwclock_bin = "/sbin/hwclock"
dt_re = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")


def get_output(command: str) -> str:
    ps = subprocess.run(command, capture_output=True, text=True)
    stdout = ps.stdout.strip()
    if ps.returncode == 0:
        return stdout
    if ps.returncode == 1 and "hwclock" in command[0]:
        return "ERROR: no hardware clock installed?"
    return "ERROR: {}".format(stdout)


def format(template: str, context: Dict[str, str]) -> str:
    for key, value in context.items():
        template = template.replace("{" + key + "}", value)
    return template


def application(env, start_response):
    output = ""

    if env["REQUEST_URI"] == "/sys2hw":
        # write system datetime into hardware clock
        output = get_output([hwclock_bin, "-w"])

    if env["REQUEST_URI"] == "/hw2sys":
        # set system datetime using hardware clock
        output = get_output([hwclock_bin, "-s"])

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

    context = {
        "output": '<p style="color: blue; font-weight: bold;">{}</p>'.format(output),
        "system_time": get_output([date_bin, '+"%Y-%m-%d %H:%M:%S.000000%z"'])[1:-1],
        "hardware_time": get_output([hwclock_bin, "-r"]),
    }

    start_response("200 OK", [("Content-Type", "text/html")])
    return [format(template, context).encode("utf-8")]
