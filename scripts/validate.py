"""Checks every workflow folder: manifest fields, the files it lists, and that each node names the pack it comes from.

    python scripts/validate.py

Nodes must come from ComfyUI core or the workflow's own node pack, so a user only has to install that one pack. Each
node needs properties.cnr_id, which ComfyUI uses to offer installing the pack when the node is missing."""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["id", "name", "version", "category", "tags", "node_pack", "min_node_pack_version", "featured", "files"]
# Nodes the frontend implements itself; they never reach the server and belong to no pack.
FRONTEND_ONLY = {"MarkdownNote", "Note", "Reroute", "PrimitiveNode"}
VERSION = re.compile(r"^\d+\.\d+\.\d+$")
# Scenario categories, listed in the README. The first category in a manifest decides where the workflow is listed.
CATEGORIES = {"character-story", "ecommerce", "portrait", "restoration", "video", "design", "audio", "3d"}


def check_workflow(path, node_pack):
    workflow = json.loads(path.read_text())
    subgraphs = workflow.get("definitions", {}).get("subgraphs", [])
    subgraph_ids = {s["id"] for s in subgraphs}
    errors = []
    for node in workflow["nodes"] + [n for s in subgraphs for n in s["nodes"]]:
        if node["type"] in FRONTEND_ONLY or node["type"] in subgraph_ids:
            continue
        cnr_id = node.get("properties", {}).get("cnr_id")
        if cnr_id is None:
            errors.append(f"node {node['id']} ({node['type']}) has no properties.cnr_id")
        elif cnr_id not in ("comfy-core", node_pack):
            errors.append(f"node {node['id']} ({node['type']}) is from {cnr_id}, not comfy-core or {node_pack}")
    return errors


def check(folder):
    manifest_path = folder / "manifest.yaml"
    if not manifest_path.exists():
        return ["no manifest.yaml"]
    manifest = yaml.safe_load(manifest_path.read_text())
    errors = [f"manifest is missing {f}" for f in FIELDS if f not in manifest]
    if errors:
        return errors
    if manifest["id"] != folder.name:
        errors.append(f"id {manifest['id']} does not match the folder name")
    if not isinstance(manifest["category"], list) or not manifest["category"]:
        errors.append("category must be a non-empty list")
    else:
        errors += [f"unknown category {c}" for c in manifest["category"] if c not in CATEGORIES]
    for field in ("version", "min_node_pack_version"):
        if not VERSION.match(str(manifest[field])):
            errors.append(f"{field} {manifest[field]} is not MAJOR.MINOR.PATCH")
    if not (folder / "README.md").exists():
        errors.append("no README.md")
    titles = [entry["title"] for entry in manifest["files"]]
    if len(set(titles)) != len(titles):
        errors.append("two files share a title")
    for entry in manifest["files"]:
        workflow = folder / entry["workflow"]
        if not workflow.exists():
            errors.append(f"{entry['workflow']} does not exist")
            continue
        if not workflow.with_suffix(".jpg").exists():
            errors.append(f"{entry['workflow']} has no thumbnail {workflow.with_suffix('.jpg').name}")
        try:
            errors += [f"{entry['workflow']}: {e}" for e in check_workflow(workflow, manifest["node_pack"])]
        except (json.JSONDecodeError, KeyError) as e:
            errors.append(f"{entry['workflow']} is not a valid workflow: {e!r}")
    for sample in manifest.get("sample_inputs", []):
        if not (folder / sample).exists():
            errors.append(f"sample input {sample} does not exist")
    return errors


def main():
    failed = False
    for folder in sorted(p for p in (ROOT / "workflows").iterdir() if p.is_dir()):
        errors = check(folder)
        print(f"{folder.name}: {'ok' if not errors else 'FAILED'}")
        for e in errors:
            print(f"  {e}")
        failed |= bool(errors)
    sys.exit(1 if failed else 0)


main()
