"""Builds ComfyUI workflow JSON for the build.py scripts in workflows/*/."""

QWEN = "AMDQwenImage21TextToImage"
TURBO = "Qwen-Image-2.1-Turbo"
# cnr_id and ver let ComfyUI find the node pack to install when a node is missing.
QWEN_PACK = {"cnr_id": "amd-qwen-image-21", "ver": "2.0.1"}
COMFY_CORE = {"cnr_id": "comfy-core", "ver": "0.39.0"}
COLOR, BGCOLOR = "#432", "#653"
SOURCE = "**From FlowFactory:** more ready-to-run workflows at https://github.com/wangxunx/FlowFactory"
SOURCE_ZH = "更多开箱即用的工作流见 FlowFactory：https://github.com/wangxunx/FlowFactory"


def key_setup(workflow_id):
    return (
        "**One-time setup.** This workflow uses the Video Factory Qwen-Image 2.1 node; if ComfyUI reports it missing, "
        f"install it from the Manager. Register at https://h3.oneclickamd.ai/?src={workflow_id}, then save your key to `h3_gateway_api_key.txt` in the ComfyUI user directory (or set `H3_GATEWAY_API_KEY`). "
        "On the Windows Desktop app use the file, for example "
        "`C:\\Users\\<you>\\AppData\\Local\\Comfy-Desktop\\ComfyUI-Installs\\ComfyUI\\ComfyUI\\user\\h3_gateway_api_key.txt`. "
        "If the key is missing, the first node fails right away and names the exact file it looked for.\n\n"
        "**Your key is not in this workflow**, so the workflow and the images it saves are safe to share."
    )


class Graph:
    def __init__(self):
        self.nodes = []
        self.links = []
        self.groups = []

    def node(self, type_, pos, size, inputs, outputs, widgets, title=None, colored=False):
        node_id = len(self.nodes) + 1
        node = {
            "id": node_id, "type": type_, "pos": list(pos), "size": list(size), "flags": {}, "order": node_id - 1,
            "mode": 0, "inputs": [{"name": n, "type": t, "link": None, **({"shape": 7} if opt else {})} for n, t, opt in inputs],
            "outputs": [{"name": n, "type": t, "links": []} for n, t in outputs],
            "properties": {} if type_ == "MarkdownNote" else {**(QWEN_PACK if type_ == QWEN else COMFY_CORE), "Node name for S&R": type_},
            "widgets_values": widgets,
        }
        if title:
            node["title"] = title
        if colored:
            node["color"], node["bgcolor"] = COLOR, BGCOLOR
        self.nodes.append(node)
        return node_id

    def link(self, src, src_slot, dst, dst_input):
        link_id = len(self.links) + 1
        dst_node = self.nodes[dst - 1]
        slot = next(i for i, inp in enumerate(dst_node["inputs"]) if inp["name"] == dst_input)
        out = self.nodes[src - 1]["outputs"][src_slot]
        dst_node["inputs"][slot]["link"] = link_id
        out["links"].append(link_id)
        self.links.append([link_id, src, src_slot, dst, slot, out["type"]])

    def group(self, title, x, y, w, h, color):
        self.groups.append({"id": len(self.groups) + 1, "title": title, "bounding": [x, y, w, h], "color": color, "font_size": 24, "flags": {}})

    def qwen(self, pos, title, prompt, aspect_ratio, refs):
        # Autogrow shows one empty socket after the connected ones, up to three.
        inputs = [(f"images.image_{i}", "IMAGE", True) for i in range(1, min(refs + 1, 3) + 1)]
        return self.node(QWEN, pos, (400, 300), inputs, [("IMAGE", "IMAGE")], [prompt, aspect_ratio, TURBO],
                         title=title, colored=True)

    def stitch(self, pos, a, b, direction):
        node_id = self.node("ImageStitch", pos, (270, 150), [("image1", "IMAGE", False), ("image2", "IMAGE", True)],
                            [("IMAGE", "IMAGE")], [direction, True, 0, "white"])
        self.link(a, 0, node_id, "image1")
        self.link(b, 0, node_id, "image2")
        return node_id

    def save(self, pos, size, image, prefix, title):
        node_id = self.node("SaveImage", pos, size, [("images", "IMAGE", False)], [], [prefix], title=title)
        self.link(image, 0, node_id, "images")
        return node_id

    def workflow(self, scale, offset):
        return {
            "last_node_id": len(self.nodes), "last_link_id": len(self.links), "nodes": self.nodes, "links": self.links,
            "groups": self.groups, "config": {}, "extra": {"ds": {"scale": scale, "offset": list(offset)}}, "version": 0.4,
        }


WIDGETS = {
    QWEN: ["prompt", "aspect_ratio", "model", "model.steps"],
    "ImageStitch": ["direction", "match_image_size", "spacing_width", "spacing_color"],
    "LoadImage": ["image"],
    "SaveImage": ["filename_prefix"],
}


def to_api(workflow):
    """Converts a workflow built here to the /prompt API format, for the test runners."""
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
