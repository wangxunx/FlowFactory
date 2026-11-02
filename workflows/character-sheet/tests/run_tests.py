"""Runs the from-image workflow on every picture in tests/inputs through a local ComfyUI server and writes an
overview image per run to tests/results/<tag>.jpg. Outputs go to output/character_sheet_test/<tag>/.

    python tests/run_tests.py --tag baseline
    python tests/run_tests.py --tag back_v2 --panels "Back view"

--panels runs only the front view plus the listed panels and saves each panel on its own, which takes a fraction of a
full run when only some prompts changed. ComfyUI caches unchanged nodes, so rerunning on the same server reuses earlier
front views instead of generating them again."""

import argparse
import io
import json
import time
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).parent
WORKFLOW = ROOT.parent / "character-sheet-from-image.json"
WIDGETS = {
    "AMDQwenImage21TextToImage": ["prompt", "aspect_ratio", "model", "model.steps"],
    "ImageStitch": ["direction", "match_image_size", "spacing_width", "spacing_color"],
    "LoadImage": ["image"],
    "SaveImage": ["filename_prefix"],
}


def to_api(workflow):
    links = {link[0]: link for link in workflow["links"]}
    prompt = {}
    for node in workflow["nodes"]:
        if node["type"] not in WIDGETS:
            continue
        inputs = dict(zip(WIDGETS[node["type"]], node["widgets_values"]))
        for i in node["inputs"]:
            if i["link"] is not None:
                link = links[i["link"]]
                inputs[i["name"]] = [str(link[1]), link[2]]
        prompt[str(node["id"])] = {"class_type": node["type"], "inputs": inputs, "_meta": {"title": node.get("title", node["type"])}}
    return prompt


def panels_only(prompt, panels):
    keep = {"Front view", *panels}
    out = {k: v for k, v in prompt.items() if v["class_type"] == "LoadImage" or v["_meta"]["title"] in keep}
    for k, v in list(out.items()):
        if v["class_type"] == "AMDQwenImage21TextToImage":
            out[f"save_{k}"] = {"class_type": "SaveImage", "inputs": {"images": [k, 0], "filename_prefix": v["_meta"]["title"]}}
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--tag", required=True)
    parser.add_argument("--panels", help="comma separated panel titles, e.g. \"Three-quarter view,Side view\"")
    args = parser.parse_args()
    panels = [p.strip() for p in args.panels.split(",")] if args.panels else None

    base = to_api(json.loads(WORKFLOW.read_text()))
    if panels:
        base = panels_only(base, panels)

    jobs = []
    for path in sorted((ROOT / "inputs").iterdir()):
        r = requests.post(f"{args.server}/upload/image", files={"image": (path.name, path.read_bytes())},
                          data={"subfolder": "character_sheet_tests", "overwrite": "true"})
        r.raise_for_status()
        prompt = json.loads(json.dumps(base))
        for node in prompt.values():
            if node["class_type"] == "LoadImage":
                node["inputs"]["image"] = f"character_sheet_tests/{path.name}"
            if node["class_type"] == "SaveImage":
                name = node["inputs"]["filename_prefix"].rsplit("/", 1)[-1].replace(" ", "_")
                node["inputs"]["filename_prefix"] = f"character_sheet_test/{args.tag}/{path.stem}_{name}"
        r = requests.post(f"{args.server}/prompt", json={"prompt": prompt})
        r.raise_for_status()
        jobs.append((path, r.json()["prompt_id"]))
    print(f"queued {len(jobs)} runs", flush=True)

    rows = []
    for path, prompt_id in jobs:
        while not (history := requests.get(f"{args.server}/history/{prompt_id}").json()):
            time.sleep(5)
        entry = history[prompt_id]
        errors = [m[1].get("exception_message", "") for m in entry["status"]["messages"] if m[0] == "execution_error"]
        images = [i for k in base if k in entry["outputs"] for i in entry["outputs"][k]["images"]]
        if panels is None:
            images = [i for i in images if "_sheet_" in i["filename"]]
        print(path.name, entry["status"]["status_str"], *errors, flush=True)
        row = [Image.open(path)]
        for i in images:
            r = requests.get(f"{args.server}/view", params={"filename": i["filename"], "subfolder": i["subfolder"], "type": "output"})
            row.append(Image.open(io.BytesIO(r.content)))
        rows.append(row)

    height = 400 if panels else 700
    rows = [[im.convert("RGB").resize((round(im.width * height / im.height), height)) for im in row] for row in rows]
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
