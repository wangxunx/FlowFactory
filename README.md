# FlowFactory

Ready-to-run ComfyUI workflows for everyday creative tasks, powered by cloud model APIs. Every workflow runs on
ComfyUI core nodes plus the AMD Video Factory nodes, so no GPU and no model downloads are needed.

[中文说明](README.zh.md)

## Workflows

### Characters and stories

| Workflow | What it does | Video Factory node |
|---|---|---|
| [Character Sheet](workflows/character-sheet/) | One picture or description of a character becomes a sheet with four turnaround views and six expressions | Qwen-Image 2.1 |

![Character Sheet](workflows/character-sheet/assets/from_image_example.jpg)

### E-commerce

| Workflow | What it does | Video Factory node |
|---|---|---|
| [Product Scenes](workflows/product-scenes/) | One phone photo of a product becomes eight product images: a white-background main image, studio, tabletop, in-hand, close-up, outdoor and festive scenes | Qwen-Image 2.1 |

![Product Scenes](workflows/product-scenes/assets/example.jpg)

### Portraits

| Workflow | What it does | Video Factory node |
|---|---|---|
| [Anime to Real](workflows/anime-to-real/) | An anime, cartoon or game character image becomes a real photo with the same pose, framing and scene | Qwen-Image 2.1 |

![Anime to Real](workflows/anime-to-real/assets/example.jpg)

## Video Factory nodes

The workflows call cloud models through the AMD Video Factory nodes. Install the pack a workflow needs from the
ComfyUI Manager, or let ComfyUI offer it when you open the workflow and a node is missing.

| Node | Pack | Version |
|---|---|---|
| Qwen-Image 2.1 | [ComfyUI-AMD-Qwen-Image-2.1](https://github.com/wangxunx/ComfyUI-AMD-Qwen-Image-2.1) | 2.0.0 or later |
| MiniMax H3 | [ComfyUI-AMD-MiniMaxH3](https://github.com/wangxunx/ComfyUI-AMD-MiniMaxH3) | 1.0.0 or later |

All packs share one API key. Register at [h3.oneclickamd.ai](https://h3.oneclickamd.ai/?src=flowfactory) and configure
the key as the Qwen-Image 2.1 pack's README describes.

## Getting a workflow

Download the workflow's zip from [Releases](https://github.com/wangxunx/FlowFactory/releases), or take its JSON from
this repository, and drag it onto the ComfyUI canvas.

Each workflow's README explains how to use it.

## Layout

Each workflow lives in its own folder under `workflows/`:

| File | Purpose |
|---|---|
| `manifest.yaml` | ID, version, category, tags, the node pack it needs and the workflow files |
| `*.json` | The ComfyUI workflows |
| `*.jpg` | Thumbnail for the workflow JSON with the same name |
| `README.md` | Usage and known limits |
| `build.py` | Optional. Regenerates the JSON when the workflow is written as a script, using `scripts/graph.py` |

Workflows are grouped by what the user wants to make, not by model or by image and video. `category` in the manifest
lists one or more of these IDs; the first one decides the section the workflow is listed under above. Put the output
type, such as `image` or `video`, in `tags`.

| Category | Covers |
|---|---|
| `character-story` | Character sheets, comics, short dramas, storyboards |
| `ecommerce` | Product photos, product videos, try-on, posters |
| `portrait` | Style transfer, headshots, relighting, hairstyles |
| `restoration` | Upscaling, old photo repair, outpainting, local edits |
| `video` | Image to video, transitions, lip sync, motion transfer |
| `design` | Interior design, tattoos, game assets |
| `audio` | Voice, music, sound effects |
| `3d` | Image to 3D |

`python scripts/validate.py` checks every manifest and workflow; run it before opening a pull request. Workflows may
only use ComfyUI core nodes and the one node pack named in the manifest, and every node must carry its
`properties.cnr_id` so ComfyUI can offer to install a missing pack.

## Maintainer scripts

| Script | Purpose |
|---|---|
| `scripts/sync_to_node_pack.py <pack dir> <registry id>` | Copies the featured workflows that need that pack into its `example_workflows/`, named after their titles |
| `scripts/stats.py` | Prints release downloads per workflow and Registry downloads per node pack |

Pushing a tag such as `character-sheet-v1.0.0` publishes that workflow's zip as a release asset; the version must
match its manifest.

## License

MIT. See [LICENSE](LICENSE).
