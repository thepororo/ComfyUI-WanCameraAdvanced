# Wan Camera Embedding Advanced

[English](README.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-2b2b2b)](https://www.comfy.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?logo=githubsponsors)](https://github.com/sponsors/thepororo)

ComfyUI Wan 영상 워크플로를 위한 고급 카메라 제어 노드입니다. 독립적인 6DoF
축 이동·회전, 경로 연결, 임베딩 시각화와 다중 프레임 참조 조건을 제공합니다.

## 설치

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/thepororo/ComfyUI-WanCameraAdvanced.git
```

설치 후 ComfyUI를 재시작하세요. `Wan Camera Multi-Frame Reference`만
`wan22fmlf` 커스텀 노드가 필요합니다.

## 포함된 노드

- **Wan Camera Embedding Advanced** — 모든 축의 이동과 회전 제어
- **Wan Camera Embedding Visualizer** — `WAN_CAMERA_EMBEDDING` 시각화
- **Wan Camera Multi-Frame Reference** — 시작·중간·끝 참조 이미지 결합

`camera_embedding`을 `WanCameraImageToVideo`의 `camera_conditions`에 연결합니다.

## 경로 연결과 권장값

앞 노드의 `camera_path`를 다음 노드의 `previous_camera_path`에 연결합니다.
경계 프레임은 한 번만 포함되므로 길이 41인 구간 3개는 최종 길이 121이 됩니다.
`length`는 41, 81처럼 4의 배수에 1을 더한 값이어야 합니다.

- 오른쪽 Yaw: `rotate_y_deg = 15`
- 오른쪽 Truck: `translate_x = 0.3`
- Tracking: `translate_x = 0.2`, `rotate_y_deg = -8`

약 45도 이상의 회전에는 원근이 일치하는 중간·끝 참조 이미지를 권장합니다.

## 개발 후원

[GitHub Sponsors](https://github.com/sponsors/thepororo)를 통해 호환성 테스트,
문서화와 유지보수를 후원할 수 있습니다. 후원은 선택 사항이며 필수 기능을
잠금 해제하지 않습니다. 자세한 내용은 [SUPPORT.ko.md](SUPPORT.ko.md)를 확인하세요.

## 라이선스

GPL-3.0

## 개발 참고

[thepororo](https://github.com/thepororo)가 설계하고 관리하며 구현 과정에서
OpenAI Codex를 활용했습니다. AI 지원 변경 사항은 공개 전에 직접 검토하고
로컬에서 검증했습니다.
