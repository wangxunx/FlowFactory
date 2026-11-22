"""Regenerates anime-to-real.json in this folder. Edit the prompt below, then run: python build.py"""

import json
import sys
from pathlib import Path

OUT_DIR = Path(__file__).parent
sys.path.insert(0, str(OUT_DIR.parents[1] / "scripts"))
from graph import SOURCE, SOURCE_ZH, Graph, key_setup  # noqa: E402

# Followed by the user's extra instructions.
PROMPT = ("Transform the image to a realistic photograph. Keep exactly the same composition, framing, camera angle, "
          "pose and background layout as the image; only the style changes from a drawing to a real photo. The "
          "character becomes a real person with the same hairstyle and hair color, eye color, facial expression and "
          "mouth shape, outfit, colors, accessories and anything they hold. Normal human body proportions, a real "
          "human face with visible skin pores and natural imperfections, real hair with flyaway strands instead of a "
          "wig, little or no makeup, and real fabric with creases and seams. The background becomes a real "
          "photographed place with real depth, light and detail. Not cosplay, not a doll, not a 3D render, not a "
          "painting, not anime. No text or watermark.")

NOTE = (
    "## Anime to Real\n\n"
    "Turns an anime, cartoon or game character image into a real photo with the same composition: the same pose, "
    "framing and scene, with the character as a real person and the background as a real place. A side-by-side of "
    "the original and the photo is saved for sharing.\n\n"
    "**How to use:** load your image in **Load Image**, set **aspect_ratio** on the Qwen node to the shape of your "
    "image (the photo is reframed to it), and run. The sample is a generated character.\n\n"
    "**Extra instructions** are added to the end of the prompt. Leave them empty, or steer the result in a few "
    "words, for example `a man`, `Western features`, or `East Asian features`.\n\n"
    "**What you get** in `output/anime_to_real/`: `real_*.png` and `before_after_*.png`.\n\n"
    "**Rerun:** the seed is fixed, so running again with the same image and instructions reuses the last result. "
    "Change the `seed` for a new take, also when the result still looks drawn or 3D-rendered.\n\n"
    "**Model:** Qwen-Image 2.1 Turbo, 1 credit per run. Chibi characters keep their big-head proportions.\n\n"
    + key_setup() + "\n\n" + SOURCE +
    "\n\n---\n\n"
    "**中文说明：** 在 Load Image 里换成你的动漫、卡通或游戏角色图，把 Qwen 节点的 aspect_ratio 设成和原图一样的比例"
    "（输出会按这个比例重新取景），然后运行。结果保持原图的构图、姿势和场景，角色变成真人，背景变成真实场景。"
    "输出在 `output/anime_to_real/`：真人照片 `real_*.png`，外加一张原图和真人照片的左右对比图 `before_after_*.png`。"
    "**补充要求**会追加到提示词末尾，可以留空，也可以用几个词调整，例如 `a man`（男性）、`Western features`（欧美面孔）、"
    "`East Asian features`（东亚面孔）。seed 固定，图和补充要求不变时再次运行会复用上次的结果；想换一版，或者结果看起来还像画的、像 3D 渲染，就改 seed。"
    "模型是 Qwen-Image 2.1 Turbo，一次运行 1 credit。Q 版角色会保留大头小身的比例，不推荐。\n\n" + SOURCE_ZH
)


def build():
    g = Graph()
    g.node("MarkdownNote", (-560, 0), (500, 900), [], [], [NOTE], colored=True)

    g.group("1. Your character", 0, -60, 420, 860, "#3f789e")
    load = g.node("LoadImage", (20, 0), (380, 500), [], [("IMAGE", "IMAGE"), ("MASK", "MASK")], ["anime_sample.jpg", "image"])
    extra = g.text((20, 540), (380, 220), "", "Extra instructions (optional)")

    g.group("2. Real photo", 460, -60, 1260, 620, "#8A8")
    prompt = g.concat((480, 0), PROMPT, extra, " ", "Prompt")
    real = g.qwen((900, 0), "Anime to real", "", "3:4", 1, seed=5)
    g.widget_input(real, "prompt", "STRING")
    g.link(prompt, 0, real, "prompt")
    g.link(load, 0, real, "images.image_1")
    g.save((1320, 0), (380, 500), real, "anime_to_real/real", "Save real photo")

    g.group("3. Before and after", 1760, -60, 460, 620, "#a1309b")
    stitch = g.stitch((1780, 0), load, real, "right")
    g.save((1780, 180), (420, 360), stitch, "anime_to_real/before_after", "Save before and after")
    return g.workflow(0.55, (700, 160))


(OUT_DIR / "anime-to-real.json").write_text(json.dumps(build(), indent=2, ensure_ascii=False) + "\n")
