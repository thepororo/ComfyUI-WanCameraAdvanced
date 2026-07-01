# Wan Camera Embedding Advanced

[English](README.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

ComfyUI Wan 영상 워크플로를 위한 고급 카메라 제어 노드입니다. 독립적인 6DoF
축 이동·회전, 경로 연결, 카메라 임베딩 시각화와 선택적인 다중 프레임 참조 이미지
조건을 제공합니다.

## 설치

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/thepororo/ComfyUI-WanCameraAdvanced.git
```

설치 후 ComfyUI를 재시작하세요. `Wan Camera Multi-Frame Reference` 노드는
`wan22fmlf` 커스텀 노드가 필요하지만 나머지 노드는 독립적으로 사용할 수 있습니다.

## 포함된 노드

- **Wan Camera Embedding Advanced** — 모든 축의 이동과 회전을 제어합니다.
- **Wan Camera Embedding Visualizer** — 네이티브 또는 Advanced
  `WAN_CAMERA_EMBEDDING`을 이미지 시퀀스로 변환합니다.
- **Wan Camera Multi-Frame Reference** — 카메라 조건과 시작·중간·끝 참조
  이미지를 결합합니다.

`camera_embedding`을 `WanCameraImageToVideo`의 `camera_conditions` 입력에
연결합니다.

## 경로 연결

앞 노드의 `camera_path`를 다음 노드의 `previous_camera_path`에 연결합니다.
다음 구간은 이전 구간의 마지막 카메라 변환에서 시작하며 경계 프레임은 한 번만
포함됩니다. 따라서 길이 41인 구간 3개를 연결하면 최종 길이는 121입니다.

`length`는 41, 81처럼 4의 배수에 1을 더한 값이어야 합니다.

## 시작 권장값

- 오른쪽 Yaw: `rotate_y_deg = 15`
- 오른쪽 Truck: `translate_x = 0.3`
- Tracking 조합: `translate_x = 0.2`, `rotate_y_deg = -8`

큰 회전은 원본 이미지에 없는 장면을 생성하도록 요구합니다. 약 45도 이상의 회전에는
원근이 일치하는 중간·끝 참조 이미지를 사용하는 것이 좋습니다.

## 라이선스

GPL-3.0

## 개발 참고

[thepororo](https://github.com/thepororo)가 설계하고 관리하며, 구현 과정에서
OpenAI Codex를 활용했습니다. AI 지원 변경 사항은 공개 전에 직접 검토하고 로컬에서
검증했습니다.
