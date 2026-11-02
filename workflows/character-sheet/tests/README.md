# Regression tests

`inputs/` holds 5 generated pictures that produce a correct sheet with the current prompts: a 3D cartoon boy, an
anime girl, a side-on runner, a street photo and a techwear outfit. Every panel of every input should still pass the checklist below after a prompt change.

Start ComfyUI with the Qwen-Image 2.1 node installed and a key configured (see the repository README), then:

```bash
python tests/run_tests.py --server http://127.0.0.1:8188 --tag baseline
python tests/run_tests.py --server http://127.0.0.1:8188 --tag back_v2 --panels "Back view"
```

A full run generates 50 images. After changing one panel's prompt, run only that panel with `--panels`; on the same
server the front views come from cache, so it generates only 5. Overviews are written to `tests/results/`.

The gateway returns the identical image for identical inputs, with either model, so rerunning a test tells nothing
new. Judge a change by how many of the inputs pass, not by repeats.

## Checklist per input

- Front: body, head and eyes face the viewer, whole body, plain white background, held items kept
- Three-quarter: clearly between front and side, feet turned with the body
- Side: strict profile facing left
- Back: face hidden, heels and backs of the legs visible, capes, backpacks and tails visible
- All panels: same face, hair, outfit and colors as the front view
- Expressions: readable and still the same person

## Findings so far

These were measured while the prompts were developed, on a wider set of 16 inputs that also included a pencil
sketch, a child, an elderly man with a cane, a seated pose, a half-body portrait, a busy low-resolution background,
long robes and items worn on the back.

| Problem | Before | Fix |
|---|---|---|
| Back view legs still facing the viewer | 4/4 candidates | Name the backs of the legs, heels and toes in the back prompt |
| Three-quarter view barely turned | 5/16 | Describe what a 45 degree turn hides instead of only the angle |
| Front view head turned aside | 1/16 | Ask for body, head and eyes to face the viewer |
| Held items dropped (cane, helmet) | 3/16 | Ask the front and the views to keep held or carried items |
| Cape, backpack or tail missing from the back | 3/16 | Ask for items worn on the back; give the back view the original picture as a second image; name the tail |
| Back view still facing the viewer (wizard) | 1/16 | Open. Fails with the front view alone, with the original picture or with the side view as second image, and with `Qwen-Image-2.1` instead of Turbo |

The back view with the original picture as second image was kept because it scored best over all 16 inputs: 15/16
turned correctly, against 15/16 with the front view alone, and only the cane was missing instead of the cane, a
backpack and a tail. `Qwen-Image-2.1` gave nearly the same back views as Turbo, so Turbo stays the default.

Known and accepted: a character whose face is hidden under a hat or hood and whose outfit looks the same front and
back may keep facing the viewer in the back view; items hidden on the far side of the body may be missing in the side view; a pose such as hands in
pockets is kept from the original rather than forced to arms down; a pencil sketch is redrawn as a rendered
illustration.
