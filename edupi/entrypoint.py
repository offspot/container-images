#!/usr/local/bin/python3

import grp
import os
import pathlib
import pwd
import shutil
import subprocess
import sys
from typing import Union

SKIP_CHOWN = bool(os.getenv("NO_CHOWN_DATA"))
username = "www-data"
groupname = "www-data"


def ensure_folders():
    root = pathlib.Path("/data")
    stat = root.stat()
    folders = ("database", "media", "stats", "log")

    def _chown(path, user: Union[str, int], group: Union[str, int]):
        try:
            shutil.chown(path, user, group)
        except Exception as exc:
            print(f"Unable to change ownership of {path}: {exc}")

    for folder in folders:
        path = root.joinpath(folder)
        try:
            path.mkdir(parents=True)
        except FileExistsError:
            pass
        else:
            _chown(path, stat.st_uid, stat.st_gid)

    if not SKIP_CHOWN:
        for folder_name in folders:
            folder = root.joinpath(folder_name)
            _chown(folder, username, groupname)
            for path in folder.rglob("*"):
                _chown(folder, username, groupname)


def start_nginx():
    if os.getenv("NO_NGINX"):
        return True
    return subprocess.run(["/usr/sbin/nginx"]).returncode == 0


def setup_django():
    sys.path.append("/src")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edupi.settings")

    import django

    django.setup()


def install_db():
    from django.core.management import execute_from_command_line

    try:
        execute_from_command_line(["manage.py", "migrate"])
    except Exception:
        return False
    return True


def create_admin(username: str, password):
    if not username or not password:
        return False

    from django.contrib.auth.models import User

    if User.objects.filter(username=username).count():
        return False

    return User.objects.create_superuser(username, None, password)


def import_src_dir(src_dir: pathlib.Path):
    if not src_dir.exists():
        return False

    from django.core.management import execute_from_command_line

    try:
        execute_from_command_line(["manage.py", "import-from-folder", str(src_dir)])
    except Exception:
        return False
    else:
        shutil.rmtree(src_dir, ignore_errors=True)
        return True


def main():
    setup_django()

    if not install_db():
        sys.exit(1)

    user = create_admin(
        username=os.getenv("ADMIN_USERNAME", ""),
        password=os.getenv("ADMIN_PASSWORD", ""),
    )
    if user:
        print(f"Created admin account: {user}")

    try:
        src_dir = pathlib.Path(os.getenv("SRC_DIR", "#"))
    except Exception:
        print("Invalid SRC_DIR environ")
        return

    if import_src_dir(src_dir=src_dir):
        print(f"Imported files from {src_dir}")


if __name__ == "__main__":
    ensure_folders()

    # drop to www-data privileges as to run script with web-alike perms
    os.setegid(grp.getgrnam(groupname)[2])
    os.seteuid(pwd.getpwnam(username)[2])
    main()
    # restore root privileges
    os.seteuid(0)
    os.setegid(0)

    if not start_nginx():
        sys.exit(1)

    if len(sys.argv) < 2:
        sys.exit(0)
    os.execvp(sys.argv[1], sys.argv[1:])  # nosec
