import math
import importlib.util
import sys
from pathlib import Path

import comfy.model_management
import node_helpers
import nodes
import numpy as np
import torch

from comfy_extras.nodes_camera_trajectory import process_pose_params


def compute_rotation_matrix(rx, ry, rz):
    rx_matrix = np.array(
        [
            [1, 0, 0],
            [0, np.cos(rx), -np.sin(rx)],
            [0, np.sin(rx), np.cos(rx)],
        ],
        dtype=np.float32,
    )
    ry_matrix = np.array(
        [
            [np.cos(ry), 0, np.sin(ry)],
            [0, 1, 0],
            [-np.sin(ry), 0, np.cos(ry)],
        ],
        dtype=np.float32,
    )
    rz_matrix = np.array(
        [
            [np.cos(rz), -np.sin(rz), 0],
            [np.sin(rz), np.cos(rz), 0],
            [0, 0, 1],
        ],
        dtype=np.float32,
    )
    return rz_matrix @ ry_matrix @ rx_matrix


def make_rt_sequence(
    length,
    tx,
    ty,
    tz,
    rx_deg,
    ry_deg,
    rz_deg,
    translation_scale,
    rotation_scale,
    speed,
    easing,
):
    final_translation = (
        np.array([tx, ty, tz], dtype=np.float32).reshape(3, 1)
        * translation_scale
        * speed
    )
    final_rotation = (
        np.radians(np.array([rx_deg, ry_deg, rz_deg], dtype=np.float32))
        * rotation_scale
        * speed
    )

    matrices = []
    denominator = max(length - 1, 1)
    for frame in range(length):
        progress = frame / denominator
        if easing == "ease_in":
            progress = progress * progress
        elif easing == "ease_out":
            progress = 1.0 - (1.0 - progress) ** 2
        elif easing == "ease_in_out":
            progress = progress * progress * (3.0 - 2.0 * progress)

        rotation = compute_rotation_matrix(*(final_rotation * progress))
        translation = final_translation * progress
        matrices.append(np.concatenate([rotation, translation], axis=1))

    return np.stack(matrices).astype(np.float32)


def append_rt_sequence(previous_rt, local_rt):
    previous_h = np.tile(np.eye(4, dtype=np.float32), (len(previous_rt), 1, 1))
    previous_h[:, :3, :4] = previous_rt
    local_h = np.tile(np.eye(4, dtype=np.float32), (len(local_rt), 1, 1))
    local_h[:, :3, :4] = local_rt

    continued_h = previous_h[-1] @ local_h
    combined_h = np.concatenate([previous_h, continued_h[1:]], axis=0)
    return combined_h[:, :3, :4].astype(np.float32)


def encode_rt_sequence(rt_sequence, width, height, fx, fy, cx, cy):
    trajectories = []
    for camera_pose in rt_sequence.tolist():
        trajectory = [fx, fy, cx, cy, 0, 0]
        trajectory.extend(camera_pose[0])
        trajectory.extend(camera_pose[1])
        trajectory.extend(camera_pose[2])
        trajectory.extend([0, 0, 0, 1])
        trajectories.append(trajectory)

    camera_params = np.asarray(trajectories, dtype=np.float32)
    camera_params = np.concatenate(
        [np.zeros_like(camera_params[:, :1]), camera_params],
        axis=1,
    )
    camera_video = process_pose_params(
        camera_params,
        width=width,
        height=height,
        device="cpu",
    )
    camera_video = (
        camera_video.permute(3, 0, 1, 2)
        .unsqueeze(0)
        .to(device=comfy.model_management.intermediate_device())
    )
    camera_video = torch.concat(
        [
            torch.repeat_interleave(camera_video[:, :, 0:1], repeats=4, dim=2),
            camera_video[:, :, 1:],
        ],
        dim=2,
    ).transpose(1, 2)

    batch, frames, channels, out_height, out_width = camera_video.shape
    camera_video = (
        camera_video.contiguous()
        .view(batch, frames // 4, 4, channels, out_height, out_width)
        .transpose(2, 3)
    )
    return (
        camera_video.contiguous()
        .view(
            batch,
            frames // 4,
            channels * 4,
            out_height,
            out_width,
        )
        .transpose(1, 2)
    )


class WanCameraEmbeddingAdvanced:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": (
                    "INT",
                    {
                        "default": 832,
                        "min": 16,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 16,
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 480,
                        "min": 16,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 16,
                    },
                ),
                "length": (
                    "INT",
                    {
                        "default": 81,
                        "min": 1,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 4,
                    },
                ),
                "translate_x": (
                    "FLOAT",
                    {"default": 0.0, "min": -4.0, "max": 4.0, "step": 0.01},
                ),
                "translate_y": (
                    "FLOAT",
                    {"default": 0.0, "min": -4.0, "max": 4.0, "step": 0.01},
                ),
                "translate_z": (
                    "FLOAT",
                    {"default": 0.0, "min": -4.0, "max": 4.0, "step": 0.01},
                ),
                "rotate_x_deg": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -180.0,
                        "max": 180.0,
                        "step": 0.1,
                    },
                ),
                "rotate_y_deg": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -180.0,
                        "max": 180.0,
                        "step": 0.1,
                    },
                ),
                "rotate_z_deg": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -180.0,
                        "max": 180.0,
                        "step": 0.1,
                    },
                ),
                "speed": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
                "translation_scale": (
                    "FLOAT",
                    {"default": 1.5, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
                "rotation_scale": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
                "easing": (
                    ["linear", "ease_in", "ease_out", "ease_in_out"],
                    {"default": "ease_in_out"},
                ),
            },
            "optional": {
                "previous_camera_path": ("WAN_CAMERA_PATH",),
                "fx": (
                    "FLOAT",
                    {
                        "default": 0.5,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.000000001,
                    },
                ),
                "fy": (
                    "FLOAT",
                    {
                        "default": 0.5,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.000000001,
                    },
                ),
                "cx": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "cy": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
            },
        }

    RETURN_TYPES = (
        "WAN_CAMERA_EMBEDDING",
        "INT",
        "INT",
        "INT",
        "WAN_CAMERA_PATH",
    )
    RETURN_NAMES = (
        "camera_embedding",
        "width",
        "height",
        "length",
        "camera_path",
    )
    FUNCTION = "execute"
    CATEGORY = "model/conditioning/wan/camera"

    def execute(
        self,
        width,
        height,
        length,
        translate_x,
        translate_y,
        translate_z,
        rotate_x_deg,
        rotate_y_deg,
        rotate_z_deg,
        speed,
        translation_scale,
        rotation_scale,
        easing,
        previous_camera_path=None,
        fx=0.5,
        fy=0.5,
        cx=0.5,
        cy=0.5,
    ):
        if (length - 1) % 4 != 0:
            raise ValueError("length must be 1 + a multiple of 4 (for example 81)")

        local_rt_sequence = make_rt_sequence(
            length,
            translate_x,
            translate_y,
            translate_z,
            rotate_x_deg,
            rotate_y_deg,
            rotate_z_deg,
            translation_scale,
            rotation_scale,
            speed,
            easing,
        )

        if previous_camera_path is None:
            rt_sequence = local_rt_sequence
        else:
            if (
                previous_camera_path["width"] != width
                or previous_camera_path["height"] != height
            ):
                raise ValueError(
                    "All chained camera segments must use the same width and height"
                )
            if (
                previous_camera_path["fx"] != fx
                or previous_camera_path["fy"] != fy
                or previous_camera_path["cx"] != cx
                or previous_camera_path["cy"] != cy
            ):
                raise ValueError(
                    "All chained camera segments must use the same fx, fy, cx, and cy"
                )
            rt_sequence = append_rt_sequence(
                previous_camera_path["rt_sequence"],
                local_rt_sequence,
            )

        camera_video = encode_rt_sequence(
            rt_sequence,
            width,
            height,
            fx,
            fy,
            cx,
            cy,
        )
        camera_path = {
            "rt_sequence": rt_sequence,
            "width": width,
            "height": height,
            "fx": fx,
            "fy": fy,
            "cx": cx,
            "cy": cy,
        }
        total_length = len(rt_sequence)
        return (
            camera_video,
            width,
            height,
            total_length,
            camera_path,
        )


def unpack_camera_embedding(camera_embedding):
    if camera_embedding.ndim != 5:
        raise ValueError(
            "WAN_CAMERA_EMBEDDING must have shape [batch, 24, time, height, width]"
        )

    batch, packed_channels, time, height, width = camera_embedding.shape
    if packed_channels != 24:
        raise ValueError(
            f"Expected 24 packed channels, received {packed_channels}"
        )

    unpacked = (
        camera_embedding.transpose(1, 2)
        .contiguous()
        .view(batch, time, 6, 4, height, width)
        .transpose(2, 3)
        .contiguous()
        .view(batch, time * 4, 6, height, width)
    )

    # Native WanCameraEmbedding repeats the first frame four times before packing.
    return unpacked[:, 3:]


class WanCameraEmbeddingVisualizer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "camera_embedding": ("WAN_CAMERA_EMBEDDING",),
                "visualization": (
                    ["ray_direction", "ray_moment"],
                    {"default": "ray_direction"},
                ),
                "frame_stride": (
                    "INT",
                    {"default": 4, "min": 1, "max": 100, "step": 1},
                ),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("visualization",)
    FUNCTION = "visualize"
    CATEGORY = "model/conditioning/wan/camera"

    def visualize(self, camera_embedding, visualization, frame_stride):
        unpacked = unpack_camera_embedding(camera_embedding)
        channel_start = 3 if visualization == "ray_direction" else 0
        channels = unpacked[:, ::frame_stride, channel_start:channel_start + 3]

        if visualization == "ray_direction":
            image = channels.mul(0.5).add(0.5).clamp(0.0, 1.0)
        else:
            scale = channels.abs().amax()
            if scale.item() == 0:
                image = torch.full_like(channels, 0.5)
            else:
                image = channels.div(scale).mul(0.5).add(0.5).clamp(0.0, 1.0)

        batch, frames, _, height, width = image.shape
        image = (
            image.permute(0, 1, 3, 4, 2)
            .reshape(batch * frames, height, width, 3)
            .detach()
            .float()
            .cpu()
        )
        return (image,)


def load_multi_frame_reference_class():
    module_name = "_wan_camera_multi_frame_dependency"
    if module_name in sys.modules:
        return sys.modules[module_name].WanMultiFrameRefToVideo

    module_path = (
        Path(__file__).resolve().parents[1]
        / "wan22fmlf"
        / "wan_multi_frame.py"
    )
    if not module_path.is_file():
        raise RuntimeError(
            "Wan Multi-Frame Reference is required. Install the wan22fmlf "
            f"custom node first. Expected file: {module_path}"
        )

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.WanMultiFrameRefToVideo


class WanCameraMultiFrameReference:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "vae": ("VAE",),
                "camera_embedding": ("WAN_CAMERA_EMBEDDING",),
                "start_image": ("IMAGE",),
                "middle_image": ("IMAGE",),
                "end_image": ("IMAGE",),
                "width": (
                    "INT",
                    {
                        "default": 832,
                        "min": 16,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 16,
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 480,
                        "min": 16,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 16,
                    },
                ),
                "length": (
                    "INT",
                    {
                        "default": 81,
                        "min": 5,
                        "max": nodes.MAX_RESOLUTION,
                        "step": 4,
                    },
                ),
                "middle_frame": (
                    "INT",
                    {"default": 40, "min": 4, "max": 9996, "step": 4},
                ),
                "ref_strength_high": (
                    "FLOAT",
                    {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "ref_strength_low": (
                    "FLOAT",
                    {"default": 0.30, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "end_strength_high": (
                    "FLOAT",
                    {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "end_strength_low": (
                    "FLOAT",
                    {"default": 0.70, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "CONDITIONING", "LATENT")
    RETURN_NAMES = ("positive_high", "positive_low", "negative", "latent")
    FUNCTION = "execute"
    CATEGORY = "model/conditioning/wan/camera"

    def execute(
        self,
        positive,
        negative,
        vae,
        camera_embedding,
        start_image,
        middle_image,
        end_image,
        width,
        height,
        length,
        middle_frame,
        ref_strength_high,
        ref_strength_low,
        end_strength_high,
        end_strength_low,
    ):
        if (length - 1) % 4 != 0:
            raise ValueError("length must be 1 + a multiple of 4")
        if not 4 <= middle_frame <= length - 5:
            raise ValueError(
                f"middle_frame must be between 4 and {length - 5}"
            )
        if middle_frame % 4 != 0:
            raise ValueError("middle_frame must be a multiple of 4")

        multi_frame_class = load_multi_frame_reference_class()
        reference_images = torch.cat(
            [start_image[:1], middle_image[:1], end_image[:1]],
            dim=0,
        )
        result = multi_frame_class.execute(
            positive=positive,
            negative=negative,
            vae=vae,
            width=width,
            height=height,
            length=length,
            batch_size=1,
            ref_images=reference_images,
            mode="NORMAL",
            ref_positions=f"0,{middle_frame},{length - 1}",
            ref_strength_high=ref_strength_high,
            ref_strength_low=ref_strength_low,
            end_frame_strength_high=end_strength_high,
            end_frame_strength_low=end_strength_low,
            structural_repulsion_boost=1.0,
            clip_vision_output=None,
        )
        positive_high, positive_low, negative_out, latent = tuple(result)

        camera_values = {"camera_conditions": camera_embedding}
        positive_high = node_helpers.conditioning_set_values(
            positive_high,
            camera_values,
        )
        positive_low = node_helpers.conditioning_set_values(
            positive_low,
            camera_values,
        )
        negative_out = node_helpers.conditioning_set_values(
            negative_out,
            camera_values,
        )

        return (positive_high, positive_low, negative_out, latent)


NODE_CLASS_MAPPINGS = {
    "WanCameraEmbeddingAdvanced": WanCameraEmbeddingAdvanced,
    "WanCameraEmbeddingVisualizer": WanCameraEmbeddingVisualizer,
    "WanCameraMultiFrameReference": WanCameraMultiFrameReference,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WanCameraEmbeddingAdvanced": "Wan Camera Embedding Advanced",
    "WanCameraEmbeddingVisualizer": "Wan Camera Embedding Visualizer",
    "WanCameraMultiFrameReference": "Wan Camera Multi-Frame Reference",
}
