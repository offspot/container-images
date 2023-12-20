#!/usr/bin/env python3

""" Entrypoint-friendly static homepage generation script

    Dependencies:
    - Jinja2
    - humanfriendly
"""

import os
import pathlib
import re
import sys
import traceback
import urllib.parse
from typing import List, Union

import humanfriendly
from jinja2 import Environment, FileSystemLoader, select_autoescape
from yaml import load as yaml_load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

src_dir = pathlib.Path(os.getenv("SRC_DIR", "/src"))
dest_dir = pathlib.Path(os.getenv("DEST_DIR", "/var/www"))
templates_dir = src_dir.joinpath("templates")
env = Environment(
    loader=FileSystemLoader(templates_dir), autoescape=select_autoescape()
)


def format_fsize(size: Union[str, int]) -> str:
    if not str(size).isdigit():
        size = humanfriendly.parse_size(size)
    try:
        return humanfriendly.format_size(int(size), keep_width=False, binary=True)
    except Exception:
        return size


env.filters["fsize"] = format_fsize


class Conf:
    debug: bool = bool(os.getenv("DEBUG", False))
    fqdn: str = ""
    name: str = ""
    footer_note: str = ""

    @classmethod
    def from_doc(cls, document):
        for key in ("name", "fqdn", "footer_note"):
            setattr(cls, key, document.get(key, "--"))

    @classmethod
    def to_dict(cls):
        return {
            key: getattr(cls, key) for key in ("debug", "fqdn", "name", "footer_note")
        }


class Package(dict):
    MANDATORY_FIELDS = ["title", "url"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["url"] = self.normalize(self.get("url", ""))
        try:
            self["download"]["url"] = self.normalize(self["download"]["url"])
        except KeyError:
            ...

    @property
    def tags(self) -> list[str]:
        return [tag for tag in self.get("tags", []) if tag and not tag.startswith("_")]

    @property
    def private_tags(self) -> list[str]:
        return [tag for tag in self.get("tags", []) if tag.startswith("_")]

    @staticmethod
    def normalize(url: str) -> str:
        if not url.strip():
            return ""
        uri = urllib.parse.urlparse(url)
        if not uri.scheme and not url.startswith("//"):
            url = f"//{url}"

        url = re.sub(r"{([a-z]+)-fqdn}", r"\1.{fqdn}", url)
        url = url.replace("{fqdn}", Conf.fqdn)
        return url

    @property
    def visible(self):
        try:
            return all([self[key] for key in self.MANDATORY_FIELDS])
        except KeyError:
            return False

    @property
    def langs(self) -> List[str]:
        return [lang[:2] for lang in self.get("languages", [])]


def gen_home(fpath: pathlib.Path):
    try:
        document = yaml_load(fpath.read_text(), Loader=Loader)
    except Exception as exc:
        print("[CRITICAL] unable to read home YAML document, using fallback homepage")
        traceback.print_exception(exc)
        return

    Conf.from_doc(document.get("metadata", {}))
    context = Conf.to_dict()
    context["packages"] = filter(
        lambda p: p.visible, [Package(**item) for item in document["packages"]]
    )

    try:
        with open(dest_dir / "index.html", "w") as fh:
            fh.write(env.get_template("home.html").render(**context))
    except Exception as exc:
        print("[CRITICAL] unable to gen homepage, using fallback")
        traceback.print_exception(exc)
        return

    print("Generated homepage")


if __name__ == "__main__":
    gen_home(src_dir / "home.yaml")

    if Conf.debug:
        with open(dest_dir / "index.html", "r") as fh:
            print(fh.read())

    if len(sys.argv) < 2:
        sys.exit(0)
    os.execvp(sys.argv[1], sys.argv[1:])  # nosec
