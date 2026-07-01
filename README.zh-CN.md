# Wan Camera Embedding Advanced

[English](README.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

面向 ComfyUI Wan 视频工作流的高级相机控制节点。支持独立的六自由度平移与旋转、
路径串联、相机嵌入可视化，以及可选的多帧参考图条件。

## 安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/thepororo/ComfyUI-WanCameraAdvanced.git
```

安装后重启 ComfyUI。`Wan Camera Multi-Frame Reference` 需要额外安装
`wan22fmlf`；其他节点不依赖它。

## 节点

- **Wan Camera Embedding Advanced**：控制所有轴向的平移和旋转。
- **Wan Camera Embedding Visualizer**：将原生或高级
  `WAN_CAMERA_EMBEDDING` 转换为图像序列。
- **Wan Camera Multi-Frame Reference**：结合相机条件与开始、中间、结束参考图。

将 `camera_embedding` 连接到 `WanCameraImageToVideo` 的
`camera_conditions` 输入。

## 路径串联

把前一个节点的 `camera_path` 连接到下一个节点的
`previous_camera_path`。后续片段会从前一片段的最终变换开始，共用边界帧只保留一次。
因此，三个 41 帧片段会生成 121 帧路径。

`length` 必须是 4 的倍数加 1，例如 41 或 81。

## 建议起始值

- 向右摇摄：`rotate_y_deg = 15`
- 向右横移：`translate_x = 0.3`
- 跟踪组合：`translate_x = 0.2`、`rotate_y_deg = -8`

大角度旋转会要求模型生成源图中不存在的场景内容。超过约 45 度时，建议加入透视一致的
中间和结束参考图。

## 许可证

GPL-3.0

## 开发说明

本项目由 [thepororo](https://github.com/thepororo) 设计和维护，并使用
OpenAI Codex 协助实现。所有 AI 辅助修改均在发布前经过人工审查和本地验证。
