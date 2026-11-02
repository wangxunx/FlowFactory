"""Copies the featured workflows that need one node pack into that pack, so they show up in ComfyUI's template browser.

    python scripts/sync_to_node_pack.py ../custom_nodes/ComfyUI-AMD-Qwen-Image-2.1 amd-qwen-image-21

Each workflow JSON and its thumbnail go to <pack>/example_workflows/ named after the title in the manifest. The
template browser only reads that one flat folder and shows the file name as the title. Sample inputs listed in the
manifest go to <pack>/example_inputs/, which the pack copies into ComfyUI's input folder because Load Image only reads
from there."""

import argparse
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pack_dir", type=Path)
    parser.add_argument("registry_id")
    args = parser.parse_args()

    workflows_dir = args.pack_dir / "example_workflows"
    inputs_dir = args.pack_dir / "example_inputs"
    for manifest_path in sorted(ROOT.glob("workflows/*/manifest.yaml")):
        manifest = yaml.safe_load(manifest_path.read_text())
        if manifest["node_pack"] != args.registry_id or not manifest["featured"]:
            continue
        folder = manifest_path.parent
        for entry in manifest["files"]:
            workflow = folder / entry["workflow"]
            workflows_dir.mkdir(exist_ok=True)
            shutil.copy(workflow, workflows_dir / f"{entry['title']}.json")
            shutil.copy(workflow.with_suffix(".jpg"), workflows_dir / f"{entry['title']}.jpg")
            print(f"{workflow.relative_to(ROOT)} -> {entry['title']}.json")
        for sample in manifest.get("sample_inputs", []):
            inputs_dir.mkdir(exist_ok=True)
            shutil.copy(folder / sample, inputs_dir)
            print(f"{(folder / sample).relative_to(ROOT)} -> example_inputs/")


main()
