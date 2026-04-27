# MCP Wiki - Streamable HTTP 전환 작업 정리

## 1) 현재 기준(정확 버전)
기준일: 2026-02-23

### 프로젝트 선언 의존성 (`pyproject.toml`)
```toml
dependencies = [
    "mcp>=1.0.0",
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "click>=8.1.0",
    "uvicorn>=0.27.0",
    "starlette>=0.27.0",
]
```

### 실제 설치 버전 (`.venv`, `uv pip list` 기준)
- `mcp==1.25.0`
- `requests==2.32.5`
- `pydantic==2.11.10`
- `python-dotenv==1.2.1`
- `click==8.3.1`
- `uvicorn==0.40.0`
- `starlette==0.50.0`

### fastmcp 상태
- `.venv`에는 `fastmcp==2.14.3`가 설치되어 있음
- 하지만 현재 프로젝트 코드/의존성 선언은 `fastmcp`가 아니라 `mcp` 기준으로 동작

## 2) 핵심 정리
- 현재 코드베이스는 `mcp + starlette + uvicorn` 조합으로 Streamable HTTP를 구성함
- 따라서 문서/계획에서 `fastmcp>=2.0.0` 전제는 현재 상태와 불일치
- 이후 문서에서는 아래 기준으로 표기 권장
  - 런타임 기준: `mcp`
  - 참고 설치 항목: `fastmcp`(선택/잔여 설치)

## 3) 버전 표기 권장안
문서에 버전을 "범위"와 "실제"로 분리해 적는 형식:

- 선언(범위): `mcp>=1.0.0`
- 실제(환경): `mcp==1.25.0`

예시:
- `mcp>=1.0.0 (installed: 1.25.0)`
- `uvicorn>=0.27.0 (installed: 0.40.0)`

## 4) pyproject를 정확 버전으로 고정하려면 (선택)
아래는 "문서 참고용" 예시이며, 실제 적용은 별도 결정:

```toml
dependencies = [
    "mcp==1.25.0",
    "requests==2.32.5",
    "pydantic==2.11.10",
    "python-dotenv==1.2.1",
    "click==8.3.1",
    "uvicorn==0.40.0",
    "starlette==0.50.0",
]
```

## 5) 다음 액션
1. `torenew.md` 기준으로 README/내부 공유문서 버전 문구 동기화
2. 의존성 정책 결정
   - 범위 유지(`>=`) + `uv.lock`으로 고정
   - 또는 `==` 직접 고정
