#!/usr/local/bin/python3

import os
import pathlib
import shutil
import subprocess
import sys


def ensure_folders():
    root = pathlib.Path("/data")
    stat = root.stat()

    for folder in ("database", "media", "stats", "log"):
        path = root.joinpath(folder)
        try:
            path.mkdir(parents=True)
        except FileExistsError:
            continue
        else:
            try:
                os.chown(path, stat.st_uid, stat.st_gid)
            except Exception as exc:
                print(f"Unable to change owner of created {path}: {exc}")


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
    ensure_folders()

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
    main()

    if not start_nginx():
        sys.exit(1)

    if len(sys.argv) < 2:
        sys.exit(0)
    os.execvp(sys.argv[1], sys.argv[1:])  # nosec
