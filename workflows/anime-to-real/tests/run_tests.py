"""Runs anime-to-real.json on every picture in tests/inputs through a local ComfyUI server and writes an overview
image to tests/results/<tag>.jpg: one row per character, the input next to the real photo. Outputs go to
output/anime_to_real_test/<tag>/.

    python tests/run_tests.py --tag baseline
    python tests/run_tests.py --tag men --extra "a man" --inputs old_knight,shonen_hero

--inputs runs only the listed pictures; --extra fills in the extra instructions. ComfyUI caches unchanged nodes, so
rerunning on the same server with the same prompt and seed reuses earlier results."""

import argparse
import io
import json
import sys
import time
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).parent
WORKFLOW = ROOT.parent / "anime-to-real.json"
sys.path.insert(0, str(ROOT.parents[2] / "scripts"))
from graph import to_api  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--tag", required=True)
    parser.add_argument("--extra", default="", help="text for the extra instructions node")
    parser.add_argument("--inputs", help="comma separated file names in tests/inputs without extension; default all")
    args = parser.parse_args()

    base = to_api(json.loads(WORKFLOW.read_text()))
    for node in base.values():
        if node["class_type"] == "PrimitiveStringMultiline":
            node["inputs"]["value"] = args.extra
    saves = [k for k, v in base.items() if v["class_type"] == "SaveImage"]

    jobs = []
    paths = sorted((ROOT / "inputs").iterdir())
    if args.inputs:
        paths = [p for p in paths if p.stem in args.inputs.split(",")]
    for path in paths:
        r = requests.post(f"{args.server}/upload/image", files={"image": (path.name, path.read_bytes())},
                          data={"subfolder": "anime_to_real_tests", "overwrite": "true"})
        r.raise_for_status()
        prompt = json.loads(json.dumps(base))
        for node in prompt.values():
            if node["class_type"] == "LoadImage":
                node["inputs"]["image"] = f"anime_to_real_tests/{path.name}"
            if node["class_type"] == "SaveImage":
                name = node["inputs"]["filename_prefix"].rsplit("/", 1)[-1]
                node["inputs"]["filename_prefix"] = f"anime_to_real_test/{args.tag}/{path.stem}_{name}"
        r = requests.post(f"{args.server}/prompt", json={"prompt": prompt})
        r.raise_for_status()
        jobs.append((path, r.json()["prompt_id"]))
    print(f"queued {len(jobs)} runs", flush=True)

    height = 400
    rows = []
    for path, prompt_id in jobs:
        while not (history := requests.get(f"{args.server}/history/{prompt_id}").json()):
            time.sleep(5)
        entry = history[prompt_id]
        errors = [m[1].get("exception_message", "") for m in entry["status"]["messages"] if m[0] == "execution_error"]
        print(path.name, entry["status"]["status_str"], *errors, flush=True)
        row = [Image.open(path)]
        for k in saves:
            if base[k]["_meta"]["title"] == "Save before and after":
                continue
            for i in entry["outputs"].get(k, {}).get("images", []):
                r = requests.get(f"{args.server}/view", params={"filename": i["filename"], "subfolder": i["subfolder"], "type": "output"})
                row.append(Image.open(io.BytesIO(r.content)))
        rows.append([im.convert("RGB").resize((round(im.width * height / im.height), height)) for im in row])

    width = max(sum(im.width + 10 for im in row) for row in rows)
    overview = Image.new("RGB", (width, len(rows) * (height + 10)), "white")
    for y, row in enumerate(rows):
        x = 0
        for im in row:
            overview.paste(im, (x, y * (height + 10)))
            x += im.width + 10
    out = ROOT / "results" / f"{args.tag}.jpg"
    out.parent.mkdir(exist_ok=True)
    overview.save(out, quality=85)
    print("overview:", out)


main()
