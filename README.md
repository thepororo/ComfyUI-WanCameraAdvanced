# Wan Camera Embedding Advanced

[English](README.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-2b2b2b)](https://www.comfy.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?logo=githubsponsors)](https://github.com/sponsors/thepororo)

Advanced camera-control nodes for ComfyUI Wan video workflows. They provide
independent 6DoF translation and rotation, path chaining, camera-embedding
visualization, and optional multi-frame reference conditioning.

## Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/thepororo/ComfyUI-WanCameraAdvanced.git
```

Restart ComfyUI. The optional `Wan Camera Multi-Frame Reference` node requires
the `wan22fmlf` custom node; the other nodes do not.

## Included nodes

- **Wan Camera Embedding Advanced** — translation and rotation on all axes.
- **Wan Camera Embedding Visualizer** — converts native or advanced
  `WAN_CAMERA_EMBEDDING` data into an image sequence.
- **Wan Camera Multi-Frame Reference** — combines camera conditioning with
  start, middle, and end reference images.

Connect `camera_embedding` to the `camera_conditions` input of
`WanCameraImageToVideo`.

## Path chaining

Connect one node's `camera_path` to the next node's
`previous_camera_path`. The next segment starts at the previous segment's final
transform. A shared boundary frame is included once, so three 41-frame segments
produce 121 frames.

`length` must be 1 plus a multiple of 4, such as 41 or 81.

## Starting values

- Yaw right: `rotate_y_deg = 15`
- Truck right: `translate_x = 0.3`
- Tracking combination: `translate_x = 0.2`, `rotate_y_deg = -8`

Large rotations request scene content that may not exist in the source image.
Use perspective-consistent middle and end references for rotations above about
45 degrees.

## Support development

Development support is available through
[GitHub Sponsors](https://github.com/sponsors/thepororo). Sponsorship is
optional and does not unlock required functionality. See [SUPPORT.md](SUPPORT.md).

## License

GPL-3.0

## Development note

Designed and maintained by [thepororo](https://github.com/thepororo) with
implementation assistance from OpenAI Codex. AI-assisted changes are reviewed
and validated locally before publication.
