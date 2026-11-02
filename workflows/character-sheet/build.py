"""Regenerates character-sheet-from-image.json and character-sheet-from-text.json in this folder. Edit the prompts below, then run: python build.py"""

import json
import sys
from pathlib import Path

OUT_DIR = Path(__file__).parent
sys.path.insert(0, str(OUT_DIR.parents[1] / "scripts"))
from graph import SOURCE, SOURCE_ZH, Graph, key_setup  # noqa: E402

KEEP = ("Keep exactly the same character: same face, hairstyle, ears, outfit, colors, body proportions and art style, "
        "and any item the character holds or carries. Whole body visible from head to toes at the same scale, "
        "centered, on a plain pure white background with the same soft even lighting. No text.")
FRONT_TAIL = ("Standing upright with the body, head and eyes squarely facing the viewer and looking straight ahead, "
              "shoulders level, arms relaxed at the sides, toes pointing toward the viewer, feet slightly apart, calm "
              "neutral expression. Keep any item the character holds or carries. Show the whole body from head to toes, "
              "centered, on a plain pure white background with soft even studio lighting. No text, no background "
              "objects, no extra characters.")
FRONT_FROM_IMAGE = ("Character design reference sheet panel. Redraw the character from the image as a clean full-body "
                    "front view. Keep exactly the same face, hairstyle, ears, outfit, colors and body proportions. "
                    "If the input is a rough drawing, render it as a clean, polished illustration; if it is a photo, "
                    "keep it photorealistic. " + FRONT_TAIL)
CHARACTER = ("a cheerful anime girl with huge fluffy fennec ears, a big fluffy fox tail, long wavy blonde hair and "
             "bright blue eyes, wearing a pink sundress and white sneakers")
FRONT_FROM_TEXT = ("Character: " + CHARACTER + ".\n\n"
                   "Character design reference sheet panel: a clean full-body front view of this character, as a "
                   "polished anime illustration with clean linework and soft cel shading. " + FRONT_TAIL)
VIEWS = [
    ("Three-quarter view", "Turn the whole character 45 degrees toward the left side of the image, a classic "
                           "three-quarter view halfway between the front view and a side profile. Head, chest, hips "
                           "and feet all turn together: the far side of the face is partly hidden behind the nose, the "
                           "far shoulder and arm are partly hidden behind the body, and the toes point toward the lower "
                           "left corner of the image. Standing upright with arms relaxed. "),
    ("Side view", "Show the character in a strict side profile view facing the left side of the image, standing upright "
                  "with arms relaxed, only one side of the face visible. "),
    ("Back view", "Turn the character's entire body 180 degrees so we see the character from directly behind, in a full "
                  "back view. Everything faces away from the viewer: the back of the head and hair, the back of the "
                  "outfit, the backs of the legs and knees, and the heels of the shoes; the toes point away from the "
                  "viewer. The face and everything on the front of the character, such as a beard, buttons or front "
                  "decorations, are hidden. Anything worn on the back, such as a cape, hood, backpack or tail, is "
                  "clearly visible. If the character has a tail, the whole tail is shown attached to the lower back "
                  "and clearly visible against the white background. Standing upright with arms relaxed, feet "
                  "slightly apart. "),
]
# The front view often hides what is on the back, so the back view also sees the original picture.
BACK_ORIGINAL = ("The second image is the original picture of the same character; use it only to see details that the "
                 "first image hides, such as a backpack, cape or tail. ")
EXPRESSION_HEAD = ("Head-and-shoulders close-up portrait of exactly the same character facing the viewer: same face, "
                   "hairstyle, ears, outfit and art style, on a plain pure white background with soft even lighting. "
                   "No text. Expression: ")
EXPRESSIONS = [
    ("Happy", "big joyful laugh with eyes squinted"),
    ("Sad", "sad, teary eyes, downturned mouth"),
    ("Angry", "angry, furrowed brows, gritted teeth"),
    ("Surprised", "surprised, wide open eyes and open mouth"),
    ("Shy", "shy and embarrassed, blushing cheeks, small smile looking slightly away"),
    ("Smug", "confident smug smirk with one raised eyebrow"),
]

KEY_SETUP = key_setup("character-sheet")
COMMON_NOTES = (
    "**What you get** in `output/character_sheet/`:\n\n"
    "- `sheet_*.png`: front, three-quarter, side and back views on top, six expressions below\n"
    "- `front_*.png`: the clean front view on its own, a good first frame or reference for image-to-video\n\n"
    "**Time:** 10 images per run. The three views run in parallel, then the six expressions run in parallel, so a "
    "run usually takes a few minutes.\n\n"
    "**Redo one panel:** edit that node's prompt (even one word) and run again. Only the changed panel and the sheet "
    "are regenerated; the other panels come from the cache.\n\n"
    "**Model:** every node uses `Qwen-Image-2.1-Turbo`, which runs about twice as fast as the base model. Switch a "
    "node to `Qwen-Image-2.1` to get the `steps` slider.\n\n"
)
NOTE_FROM_IMAGE = (
    "## Character Sheet from an image\n\n"
    "Turns one picture of a character (a photo, an illustration, or even a rough doodle) into a character sheet: "
    "four turnaround views and six expressions, stitched into one image.\n\n"
    "**How to use:** load your picture in **Load Image** and run. The sample is a generated street photo; the "
    "workflow removes the background and keeps the photo look. One character per picture works best; if only the upper body is visible, the legs and shoes are "
    "invented.\n\n" + COMMON_NOTES + KEY_SETUP + "\n\n" + SOURCE + "\n\n---\n\n"
    "**中文说明：** 在 Load Image 里换成你的角色图（照片、插画、草图都行），直接运行即可。输出在 "
    "`output/character_sheet/`：`sheet` 是完整设定图（上面四视图，下面六个表情），`front` 是单独的正面全身图，"
    "可直接作为图生视频的首帧。每次运行生成 10 张图。想重做某一格，改一下那个节点的提示词再运行，"
    "其他格子走缓存，不会重新生成。\n\n" + SOURCE_ZH
)
NOTE_FROM_TEXT = (
    "## Character Sheet from a description\n\n"
    "Designs a new character from a text description and lays it out as a character sheet: four turnaround views "
    "and six expressions, stitched into one image.\n\n"
    "**How to use:** in the **Front view** node, replace the text after `Character:` with your own description "
    "(who they are, hair, eyes, outfit, colors), then run. Keep the rest of that prompt as it is: it asks for the "
    "neutral full-body pose the other panels are built from. Change `polished anime illustration` there to "
    "`photorealistic photo` or another style if you want a different look.\n\n" + COMMON_NOTES + KEY_SETUP +
    "\n\n" + SOURCE + "\n\n---\n\n"
    "**中文说明：** 在 Front view 节点里，把 `Character:` 后面的描述换成你的角色（发型、眼睛、服装、配色），直接运行即可。"
    "其余文字保持不变，它负责生成后续各格依赖的中性全身站姿；想要写实风格，把 `polished anime illustration` "
    "改成 `photorealistic photo`。输出在 `output/character_sheet/`，每次运行生成 10 张图。\n\n" + SOURCE_ZH
)


def build(from_image):
    g = Graph()
    note_text = NOTE_FROM_IMAGE if from_image else NOTE_FROM_TEXT
    g.node("MarkdownNote", (-560, 0), (500, 980), [], [], [note_text], colored=True)

    if from_image:
        g.group("1. Your character", 0, -60, 420, 520, "#3f789e")
        load = g.node("LoadImage", (20, 0), (380, 440), [], [("IMAGE", "IMAGE"), ("MASK", "MASK")], ["character_sheet_model.jpg", "image"])
        g.group("2. Clean front view", 460, -60, 440, 380, "#3f789e")
        front = g.qwen((480, 0), "Front view", FRONT_FROM_IMAGE, "9:16", 1)
        g.link(load, 0, front, "images.image_1")
    else:
        g.group("1. Describe your character", 460, -60, 440, 380, "#3f789e")
        front = g.qwen((480, 0), "Front view", FRONT_FROM_TEXT, "9:16", 0)

    g.group("3. Turnaround views", 940, -60, 440, 1140, "#8A8")
    views = []
    for i, (title, text) in enumerate(VIEWS):
        use_original = from_image and title == "Back view"
        n = g.qwen((960, i * 360), title, text + (BACK_ORIGINAL if use_original else "") + KEEP, "9:16", 2 if use_original else 1)
        g.link(front, 0, n, "images.image_1")
        if use_original:
            g.link(load, 0, n, "images.image_2")
        views.append(n)

    g.group("4. Expressions", 1420, -60, 880, 1140, "#b58b2a")
    expressions = []
    for i, (title, text) in enumerate(EXPRESSIONS):
        n = g.qwen((1440 + (i // 3) * 430, (i % 3) * 360), title, EXPRESSION_HEAD + text + ".", "1:1", 1)
        g.link(front, 0, n, "images.image_1")
        expressions.append(n)

    g.group("5. Sheet", 2340, -60, 960, 1140, "#a1309b")
    x = 2360
    row = g.stitch((x, 0), front, views[0], "right")
    row = g.stitch((x, 180), row, views[1], "right")
    row = g.stitch((x, 360), row, views[2], "right")
    top = g.stitch((x, 560), expressions[0], expressions[1], "right")
    top = g.stitch((x, 740), top, expressions[2], "right")
    bottom = g.stitch((x + 300, 560), expressions[3], expressions[4], "right")
    bottom = g.stitch((x + 300, 740), bottom, expressions[5], "right")
    grid = g.stitch((x + 300, 920), top, bottom, "down")
    sheet = g.stitch((x + 300, 0), row, grid, "down")

    g.save((x + 600, 0), (340, 560), sheet, "character_sheet/sheet", "Save character sheet")
    g.save((x + 600, 620), (340, 440), front, "character_sheet/front", "Save front view")
    return g.workflow(0.55, (700, 160))

for from_image, name in [(True, "character-sheet-from-image"), (False, "character-sheet-from-text")]:
    (OUT_DIR / f"{name}.json").write_text(json.dumps(build(from_image), indent=2, ensure_ascii=False) + "\n")
