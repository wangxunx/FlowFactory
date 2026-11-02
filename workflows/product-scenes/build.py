"""Regenerates product-scenes.json in this folder. Edit the prompts below, then run: python build.py"""

import json
import sys
from pathlib import Path

OUT_DIR = Path(__file__).parent
sys.path.insert(0, str(OUT_DIR.parents[1] / "scripts"))
from graph import SOURCE, SOURCE_ZH, Graph, key_setup  # noqa: E402

KEEP = ("Keep the product exactly as it is in the image: the same shape and proportions, colors, materials and "
        "finish, and the same logo and printed text, sharp and legible. Do not redesign, recolor or add anything to "
        "the product, and show only one of it. ")
PHOTO = ("Professional commercial product photograph, photorealistic, high detail, the product in sharp focus. The "
         "lighting on the product matches the scene, with natural highlights and reflections on its surfaces and a "
         "soft contact shadow where it rests. No added text, logos or watermarks.")
# (node title, file name, scene sentence). Every prompt is the scene sentence + KEEP + PHOTO.
SHOTS = [
    ("White background", "white_background",
     "E-commerce main image: the product from the image alone on a pure white background, centered and filling "
     "about 85% of the frame, facing the camera so its front and label are clearly visible. Soft, even studio "
     "lighting and a faint natural shadow under the product. No props. "),
    ("Studio podium", "studio",
     "Hero shot: place the product from the image on a simple round podium in a minimal studio, with a smooth "
     "seamless backdrop in a soft color that complements the product's colors. Soft key light from one side and a "
     "gentle rim light that outlines the product. "),
    ("Tabletop", "tabletop",
     "Lifestyle shot: replace the background with a cozy, modern home, and place the product from the image on a "
     "light wooden table there, with a small green plant, a folded linen cloth and a ceramic cup arranged behind "
     "it, never covering it. Warm morning sunlight from a window, softly blurred background. "),
    ("Leaf shadows", "leaf_shadows",
     "Minimal sunlit shot: replace the background with a smooth warm beige stone surface and a matching plain "
     "wall, and place the product from the image on the stone. Bright direct sunlight casts soft, natural shadows "
     "of palm leaves across the wall, the surface and the product. "),
    ("In hand", "in_hand",
     "Replace the background with a bright, softly blurred indoor setting, and show a person's hand naturally "
     "holding the product from the image at its real size, by its handle if it has one. Only the hand and part of "
     "the forearm are visible, with natural skin and neat nails. "),
    ("Close-up detail", "detail",
     "Macro detail shot in a photo studio: the camera moves in very close to the product from the image, so its "
     "logo or label and the surrounding material fill most of the frame and the texture and finish are seen up "
     "close; parts of the product may extend past the edges. The background is a smooth, softly blurred warm grey "
     "studio backdrop with nothing else in it. Very shallow depth of field and soft directional light that brings "
     "out the texture. "),
    ("Outdoor", "outdoor",
     "Outdoor shot: place the product from the image outdoors in a natural setting that suits it, for example on "
     "a sunlit stone, a wooden bench in a park, or on sand, in warm golden-hour sunlight with a softly blurred "
     "background. "),
    ("Festive gift", "festive",
     "Festive shot: the product from the image as the centerpiece of a holiday gift arrangement, with wrapped gift "
     "boxes, ribbons and a few seasonal decorations around it, and warm bokeh lights in the background. Cozy warm "
     "light. "),
]

NOTE = (
    "## Product Scenes\n\n"
    "Turns one photo of a product, even a quick phone snapshot, into eight product images: a white-background main "
    "image, a studio hero shot, a tabletop scene, a sunlit leaf-shadow shot, an in-hand shot, a close-up, and "
    "outdoor and festive scenes. The product's shape, colors, logo and label text stay the same in every image, "
    "and each scene relights it to match.\n\n"
    "**How to use:** load your product photo in **Load Image** and run. One product per photo, with its label in "
    "view, works best. The sample is a generated phone photo.\n\n"
    "**What you get** in `output/product_scenes/`: one square image per scene, named after it "
    "(`white_background_*.png`, `studio_*.png`, ...). Square suits marketplace main images; set a node's "
    "`aspect_ratio` to `3:4` or `9:16` for social posts.\n\n"
    "**Change a scene:** the first sentence of each prompt describes the scene, so rewrite it to fit your brand, "
    "for example a Lunar New Year table instead of a holiday gift. Keep the rest of the prompt: it keeps the "
    "product, its label and its lighting right. Run again and only the changed scenes are regenerated.\n\n"
    "**Model:** every node uses `Qwen-Image-2.1-Turbo`, and all eight run in parallel. Switch a node to "
    "`Qwen-Image-2.1` to get the `steps` slider.\n\n" + key_setup("product-scenes") + "\n\n" + SOURCE + "\n\n---\n\n"
    "**中文说明：** 在 Load Image 里换成你的商品照片（手机随手拍即可），直接运行。一张图放一件商品、标签朝向镜头效果最好。"
    "输出在 `output/product_scenes/`，每个场景一张方图：白底主图、展台棚拍、桌面生活场景、阳光树影、手持、细节特写、户外、节日。"
    "商品的外形、颜色、logo 和标签文字在每张图里保持不变，光影随场景重新匹配。"
    "方图适合电商主图；发小红书或抖音可把节点的 `aspect_ratio` 改成 `3:4` 或 `9:16`。"
    "想换场景，只改提示词的第一句（例如把节日礼物改成春节年货），其余文字负责保持商品、标签和光影，不要删。"
    "再次运行时只重新生成改过的场景。\n\n" + SOURCE_ZH
)


def build():
    g = Graph()
    g.node("MarkdownNote", (-560, 0), (500, 1000), [], [], [NOTE], colored=True)

    g.group("1. Your product", 0, -60, 420, 580, "#3f789e")
    load = g.node("LoadImage", (20, 0), (380, 500), [], [("IMAGE", "IMAGE"), ("MASK", "MASK")], ["product_sample.jpg", "image"])

    g.group("2. Product images", 460, -60, 1520, 1560, "#8A8")
    for i, (title, name, scene) in enumerate(SHOTS):
        x, y = 480 + (i // 4) * 760, (i % 4) * 380
        shot = g.qwen((x, y), title, scene + KEEP + PHOTO, "1:1", 1)
        g.link(load, 0, shot, "images.image_1")
        g.save((x + 420, y), (300, 340), shot, f"product_scenes/{name}", f"Save {title.lower()}")
    return g.workflow(0.5, (700, 160))


(OUT_DIR / "product-scenes.json").write_text(json.dumps(build(), indent=2, ensure_ascii=False) + "\n")
