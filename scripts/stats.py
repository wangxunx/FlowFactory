"""Prints download counts from public pages: each workflow's release zips on GitHub, and the Comfy Registry node packs
the workflows need.

    python scripts/stats.py

Set GITHUB_TOKEN to avoid GitHub's limit of 60 unauthenticated requests per hour. A download is a file download, not a
user, and not a run."""

import json
import os
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REPO = "wangxunx/FlowFactory"
ASSET = re.compile(r"^(.+)-v(\d+\.\d+\.\d+)\.zip$")


def get(url):
    headers = {"Accept": "application/json"}
    if url.startswith("https://api.github.com") and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return json.load(r)


def main():
    manifests = [yaml.safe_load(p.read_text()) for p in sorted(ROOT.glob("workflows/*/manifest.yaml"))]

    downloads = defaultdict(dict)
    page = 1
    while releases := get(f"https://api.github.com/repos/{REPO}/releases?per_page=100&page={page}"):
        for release in releases:
            for asset in release["assets"]:
                if m := ASSET.match(asset["name"]):
                    downloads[m[1]][m[2]] = asset["download_count"]
        page += 1

    print("Workflow release downloads")
    for manifest in manifests:
        versions = downloads.get(manifest["id"], {})
        detail = ", ".join(f"{v}: {n}" for v, n in sorted(versions.items()))
        print(f"  {manifest['id']}: {sum(versions.values())}" + (f" ({detail})" if detail else ""))

    print("Node packs on the Comfy Registry")
    for pack in sorted({m["node_pack"] for m in manifests}):
        node = get(f"https://api.comfy.org/nodes/{pack}")
        active = [v["version"] for v in get(f"https://api.comfy.org/nodes/{pack}/versions") if v["status"] == "NodeVersionStatusActive"]
        latest = node["latest_version"]
        print(f"  {pack}: {node.get('downloads')} downloads, latest {latest['version']} {latest['status']}, "
              f"active: {', '.join(active) or 'none'}")


main()
