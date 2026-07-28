# ChongPlus Image Skill

ChongPlus Image API로 이미지를 생성하고 참조 이미지를 편집하는 Agent Skill입니다.

[English](../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Русский](README.ru.md)

## 기능

- `gpt-image-2`를 이용한 텍스트 이미지 생성
- 참조 이미지를 이용한 이미지 편집
- 현재 사용자의 로컬 설정 디렉터리에 API Key 저장
- Base64 및 URL 이미지 응답 지원
- Python 표준 라이브러리만 사용

## 요구 사항

- Codex처럼 Agent Skills와 로컬 스크립트 실행을 지원하는 클라이언트
- Python 3.9 이상
- `gpt-image-2` 접근 권한이 있는 ChongPlus API Key

일반 채팅 클라이언트는 Skill 자동 설치, 로컬 코드 실행 또는 안전한 자격 증명 저장을 할 수 없습니다. 이 경우 API를 직접 사용하세요.

## Codex에 설치

Codex에게 이 저장소를 설치하도록 요청하거나 Skill 설치기를 실행하세요.

```bash
python3 /path/to/install-skill-from-github.py \
  --repo Rodert/chongplus-image-skill --path .
```

설치 후 새 Codex 대화에서 "ChongPlus로 해 뜰 때의 영화 같은 산 풍경을 생성해 줘"라고 요청하세요. 처음 사용할 때 API Key를 요청하여 로컬에 저장하며 환경 변수는 필요하지 않습니다.

API Key가 없나요? [ChongPlus Keys](https://api.chongplus.plus/keys)에 로그인하여 키를 만들고 이미지 생성 그룹을 선택하세요.

## 로컬 사용

저장소 루트에서 실행하세요.

```bash
python3 scripts/chongplus_image.py config --set-key
python3 scripts/chongplus_image.py generate \
  --prompt "A cinematic mountain landscape at sunrise" \
  --size 1536x1024 --output-dir ./outputs
```

키는 macOS/Linux에서는 `~/.config/chongplus-image/config.json`(또는 `$XDG_CONFIG_HOME`)에, Windows에서는 `%APPDATA%\\chongplus-image\\config.json`에 저장됩니다. Unix에서는 디렉터리 권한 `0700`, 파일 권한 `0600`이 적용됩니다.

`config --check`는 로컬 설정만 확인합니다. 실제 생성은 할당량을 사용할 수 있습니다. `403 / error code: 1010`이 발생하면 기본 클라이언트 헤더를 유지하고 ChongPlus 운영자에게 Cloudflare Firewall 이벤트를 확인해 달라고 요청하세요.

## Skill 사용자 지정

사용자 지정 이미지 워크플로가 필요하다면 이 저장소와 [ChongPlus Image API 문서](https://api.chongplus.plus/tools/image-studio/docs/)를 AI Agent에 제공하세요. 엔드포인트, 매개변수, 지원 크기 및 응답 형식은 이 문서를 기준으로 합니다.
