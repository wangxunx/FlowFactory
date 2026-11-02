"""Runs product-scenes.json on every picture in tests/inputs through a local ComfyUI server and writes an overview
image to tests/results/<tag>.jpg: one row per product, the input first, then one image per scene. Outputs go to
output/product_scenes_test/<tag>/.

    python tests/run_tests.py --tag baseline
    python tests/run_tests.py --tag flat_lay_v2 --shots "Flat lay,In hand"

--shots runs only the listed scenes. ComfyUI caches unchanged nodes, so rerunning on the same server reuses earlier
results of scenes whose prompt did not change."""

import argparse
import io
import json
import sys
import time
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).parent
WORKFLOW = ROOT.parent / "product-scenes.json"
sys.path.insert(0, str(ROOT.parents[2] / "scripts"))
from graph import QWEN, to_api  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--tag", required=True)
    parser.add_argument("--shots", help="comma separated node titles, e.g. \"Flat lay,In hand\"")
    args = parser.parse_args()

    base = to_api(json.loads(WORKFLOW.read_text()))
    if args.shots:
        keep = {s.strip() for s in args.shots.split(",")}
        base = {k: v for k, v in base.items() if v["class_type"] != QWEN or v["_meta"]["title"] in keep}
        base = {k: v for k, v in base.items() if v["class_type"] != "SaveImage" or v["inputs"]["images"][0] in base}
    saves = [k for k, v in base.items() if v["class_type"] == "SaveImage"]

    jobs = []
    for path in sorted((ROOT / "inputs").iterdir()):
        r = requests.post(f"{args.server}/upload/image", files={"image": (path.name, path.read_bytes())},
                          data={"subfolder": "product_scenes_tests", "overwrite": "true"})
        r.raise_for_status()
        prompt = json.loads(json.dumps(base))
        for node in prompt.values():
            if node["class_type"] == "LoadImage":
                node["inputs"]["image"] = f"product_scenes_tests/{path.name}"
            if node["class_type"] == "SaveImage":
                name = node["inputs"]["filename_prefix"].rsplit("/", 1)[-1]
                node["inputs"]["filename_prefix"] = f"product_scenes_test/{args.tag}/{path.stem}_{name}"
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
