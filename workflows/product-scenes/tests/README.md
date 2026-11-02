# Regression tests

`inputs/` holds 10 generated phone photos of fictional products, picked to cover different materials and label
types: a fabric speaker, a ceramic mug, glossy earbuds, a leather tote, a glass perfume bottle, a running shoe that is
small in the frame, a candle, an amber serum bottle, a snack pouch with Chinese text and a misspelled English line,
and a watch. Every scene of every input should still pass the checklist below after a prompt change.

Start ComfyUI with the Qwen-Image 2.1 node installed and a key configured (see the repository README), then:

```bash
python tests/run_tests.py --server http://127.0.0.1:8188 --tag baseline
python tests/run_tests.py --server http://127.0.0.1:8188 --tag detail_v2 --shots "Close-up detail"
```

A full run generates 80 images. After changing one scene's prompt, run only that scene with `--shots`. Overviews are
written to `tests/results/`, one row per product.

## Checklist per input

- Product: same shape, colors, logo and label text as the input; only one of it
- Background: the original background is gone, except where the scene asks for it
- Lighting: highlights, reflections and a contact shadow that fit the scene
- White background: pure white, no props
- In hand: a believable hand at a believable size
- Close-up: the label or material fills most of the frame

## Findings so far

| Problem | Before | Fix |
|---|---|---|
| Lifestyle scene ignored the product and put everything in a bathroom | 10/10 | The model latches on to the first example in a list. Replaced with one fixed tabletop scene |
| Lifestyle scene without examples was an empty beige room | 10/10 | Same fix: name the place and the props |
| Flat lay kept the product's front-on angle and looked pasted on | 10/10 | Replaced with the leaf-shadow scene |
| In hand and close-up kept the original messy background | 10/10 | Start the prompt with "Replace the background" and name the backdrop color |

Known and accepted: the earbuds case, which has no text, gets a few invented characters on the white background and
the close-up; very small print can drift in the close-up ("Eau de Parfe").
