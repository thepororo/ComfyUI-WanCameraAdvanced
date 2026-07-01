# Wan Camera Embedding Advanced

[English](README.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-2b2b2b)](https://www.comfy.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?logo=githubsponsors)](https://github.com/sponsors/thepororo)

面向 ComfyUI Wan 视频工作流的高级相机控制节点。支持独立的六自由度平移与旋转、
路径串联、相机嵌入可视化和多帧参考图条件。

## 安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/thepororo/ComfyUI-WanCameraAdvanced.git
```

安装后重启 ComfyUI。只有 `Wan Camera Multi-Frame Reference` 需要
`wan22fmlf` 自定义节点。

## 包含的节点

- **Wan Camera Embedding Advanced**：控制所有轴向的平移和旋转
- **Wan Camera Embedding Visualizer**：可视化 `WAN_CAMERA_EMBEDDING`
- **Wan Camera Multi-Frame Reference**：组合开始、中间和结束参考图

将 `camera_embedding` 连接到 `WanCameraImageToVideo` 的
`camera_conditions` 输入。

## 路径串联与建议值

把前一个节点的 `camera_path` 连接到下一个节点的 `previous_camera_path`。
共用边界帧只保留一次，因此三个 41 帧片段会生成 121 帧路径。
`length` 必须是 4 的倍数加 1，例如 41 或 81。

- 向右摇摄：`rotate_y_deg = 15`
- 向右横移：`translate_x = 0.3`
- 跟踪组合：`translate_x = 0.2`、`rotate_y_deg = -8`

超过约 45 度时，建议加入透视一致的中间和结束参考图。

## 支持开发

可以通过 [GitHub Sponsors](https://github.com/sponsors/thepororo) 支持兼容性测试、
文档和维护。赞助完全自愿，不会解锁必要功能。详情请参阅
[SUPPORT.zh-CN.md](SUPPORT.zh-CN.md)。

## 许可证

GPL-3.0

## 开发说明

本项目由 [thepororo](https://github.com/thepororo) 设计和维护，并使用
OpenAI Codex 协助实现。所有 AI 辅助修改均在发布前经过人工审查和本地验证。
