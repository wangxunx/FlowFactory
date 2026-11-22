# FlowFactory

开箱即用的 ComfyUI 创作工作流，由云端模型 API 驱动。每个工作流只用 ComfyUI 核心节点和 AMD Video Factory 节点，不需要显卡，也不用下载模型。

[English](README.md)

## 工作流

### 角色与故事

| 工作流 | 作用 | Video Factory 节点 |
|---|---|---|
| [角色设定图](workflows/character-sheet/) | 从一张角色图或一段描述生成设定图：四视图加六种表情 | Qwen-Image 2.1 |

![角色设定图](workflows/character-sheet/assets/from_image_example.jpg)

### 电商与营销

| 工作流 | 作用 | Video Factory 节点 |
|---|---|---|
| [商品场景图](workflows/product-scenes/) | 一张手机拍的商品照生成八张商品图：白底主图、棚拍、桌面、手持、细节特写、户外、节日等场景 | Qwen-Image 2.1 |

![商品场景图](workflows/product-scenes/assets/example.jpg)

### 人像与写真

| 工作流 | 作用 | Video Factory 节点 |
|---|---|---|
| [动漫转真人](workflows/anime-to-real/) | 动漫、卡通或游戏角色图变成真人照片，姿势、取景和场景不变 | Qwen-Image 2.1 |

![动漫转真人](workflows/anime-to-real/assets/example.jpg)

## Video Factory 节点

工作流通过 AMD Video Factory 节点调用云端模型。用 ComfyUI Manager 安装工作流需要的节点包；也可以直接打开工作流，缺节点时 ComfyUI 会提示安装。

| 节点 | 节点包 | 版本 |
|---|---|---|
| Qwen-Image 2.1 | [ComfyUI-AMD-Qwen-Image-2.1](https://github.com/wangxunx/ComfyUI-AMD-Qwen-Image-2.1) | 2.0.0 或更新 |
| MiniMax H3 | [ComfyUI-AMD-MiniMaxH3](https://github.com/wangxunx/ComfyUI-AMD-MiniMaxH3) | 1.0.0 或更新 |

所有节点包共用一个 API key。在 [h3.oneclickamd.ai](https://h3.oneclickamd.ai/?utm_source=comfyui) 注册，按 Qwen-Image 2.1 节点包的 README 配好 key。

## 获取工作流

在 [Releases](https://github.com/wangxunx/FlowFactory/releases) 下载工作流的 zip，或者直接用本仓库里的 JSON，拖进 ComfyUI 画布。

每个工作流的 README 里写了使用方法。

## 目录结构

每个工作流在 `workflows/` 下有自己的目录：

| 文件 | 作用 |
|---|---|
| `manifest.yaml` | ID、版本、分类、标签、依赖的节点包和工作流文件 |
| `*.json` | ComfyUI 工作流 |
| `*.jpg` | 同名工作流 JSON 的缩略图 |
| `README.md` | 使用方法和已知限制 |
| `build.py` | 可选。工作流用脚本生成时，用它（借助 `scripts/graph.py`）重新生成 JSON |

工作流按用户要完成的事情分类，不按模型，也不按图像或视频分。manifest 里的 `category` 从下面的 ID 中选一个或多个，第一个决定工作流列在上面哪一节。输出类型（如 `image`、`video`）写进 `tags`。

| 分类 | 包括 |
|---|---|
| `character-story` | 角色与故事：角色设定图、漫剧、短剧、分镜 |
| `ecommerce` | 电商与营销：商品图、带货视频、换装、海报 |
| `portrait` | 人像与写真：风格互转、证件照、重打光、发型 |
| `restoration` | 修复与增强：放大、老照片修复、扩图、局部修改 |
| `video` | 视频创作：图生视频、转场、对口型、动作迁移 |
| `design` | 设计与空间：室内设计、纹身、游戏素材 |
| `audio` | 音频：配音、音乐、音效 |
| `3d` | 3D：图生 3D |

提交 PR 前运行 `python scripts/validate.py`，它会检查所有 manifest 和工作流。工作流只能用 ComfyUI 核心节点和 manifest 里写明的那一个节点包，每个节点都要带 `properties.cnr_id`，这样缺节点时 ComfyUI 才能提示安装对应的节点包。

## 维护脚本

| 脚本 | 作用 |
|---|---|
| `scripts/sync_to_node_pack.py <节点包目录> <registry id>` | 把需要该节点包的精选工作流拷进它的 `example_workflows/`，以标题命名 |
| `scripts/stats.py` | 输出每个工作流的 Release 下载数，以及每个节点包在 Registry 上的下载数 |

推送 `character-sheet-v1.0.0` 这类 tag，会把该工作流打成 zip 发布为 Release asset；tag 里的版本号必须和 manifest 一致。

## 许可

MIT，见 [LICENSE](LICENSE)。
