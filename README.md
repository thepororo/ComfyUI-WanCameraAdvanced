# Wan Camera Embedding Advanced

[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-2b2b2b)](https://www.comfy.org/)
[![Wan Video](https://img.shields.io/badge/Wan-Video%20Camera%20Control-5c6ac4)](https://docs.comfy.org/tutorials/video/wan/fun-camera)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

An extended Wan camera embedding node with independent translation and
rotation controls.

## Installation

Clone this repository into `ComfyUI/custom_nodes`:

```bash
git clone https://github.com/thepororo/ComfyUI-WanCameraAdvanced.git
```

Restart ComfyUI after installation.

The optional `Wan Camera Multi-Frame Reference` node requires the
`wan22fmlf` custom node. The camera embedding, path chaining, and visualizer
nodes do not require it.

## Nodes

The node appears at:

`model/conditioning/wan/camera > Wan Camera Embedding Advanced`

Connect `camera_embedding` to the `camera_conditions` input of
`WanCameraImageToVideo`.

`Wan Camera Embedding Visualizer` converts native or advanced
`WAN_CAMERA_EMBEDDING` data into an `IMAGE` sequence:

- `ray_direction`: maps the XYZ ray direction to RGB.
- `ray_moment`: maps the XYZ Plucker moment to RGB with sequence-wide scaling.
- `frame_stride`: outputs every Nth source frame to reduce preview memory.

Multiple `Wan Camera Embedding Advanced` nodes can be chained by connecting
`camera_path` to the next node's optional `previous_camera_path` input. The
next segment starts from the previous segment's final camera transform. The
shared boundary frame is included only once, so chaining two 81-frame segments
produces 161 frames.

`Wan Camera Multi-Frame Reference` combines a camera embedding with explicit
start, middle, and end reference images. It reuses the installed
`wan22fmlf/Wan Multi-Frame Reference` implementation and adds
`camera_conditions` without replacing its latent image or mask conditioning.
For an 81-frame video, use `middle_frame = 40`.

`length` must be 1 plus a multiple of 4, such as 81.

## Suggested starting values

- Yaw right: `rotate_y_deg = 15`, all other motion values `0`
- Truck right: `translate_x = 0.3`, all other motion values `0`
- Tracking combination: `translate_x = 0.2`, `rotate_y_deg = -8`

Large rotations reveal parts of a scene that are not present in the source
image. Use perspective-consistent middle and end reference images when
attempting rotations above roughly 45 degrees.

## License

GPL-3.0

## Development

Designed and maintained by
[`thepororo`](https://github.com/thepororo), with implementation assistance
from OpenAI Codex. AI-assisted changes are reviewed and validated locally
before publication.
