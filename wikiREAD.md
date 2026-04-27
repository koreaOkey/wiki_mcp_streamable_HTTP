# wiki-mcp (Streamable HTTP)

Confluence 위키와 상호작용하기 위한 MCP 서버입니다.
현재 구현은 `mcp` SDK 기반이며, 기본 통신 방식은 Streamable HTTP입니다.

## 현재 기준 (2026-02-23)

### 프로젝트 의존성 선언 (`pyproject.toml`)
- `mcp>=1.0.0`
- `requests>=2.31.0`
- `pydantic>=2.0.0`
- `python-dotenv>=1.0.0`
- `click>=8.1.0`
- `uvicorn>=0.27.0`
- `starlette>=0.27.0`

### 실제 설치 버전 (`.venv`)
- `mcp==1.25.0`
- `requests==2.32.5`
- `pydantic==2.11.10`
- `python-dotenv==1.2.1`
- `click==8.3.1`
- `uvicorn==0.40.0`
- `starlette==0.50.0`

참고: `.venv`에 `fastmcp==2.14.3`가 설치되어 있을 수 있으나, 현재 코드의 핵심 런타임은 `mcp` 기준입니다.

## 프로젝트 구조

```text
src/wiki_mcp/
├── __init__.py   # CLI 진입점
├── app.py        # Streamable HTTP ASGI 앱 (/mcp)
├── server.py     # MCP tool 정의/호출 처리
├── api_client.py # Confluence REST API 클라이언트
└── models.py     # WikiPage/WikiSpace 모델
```

## 설치

```bash
uv sync
```

## 실행

### 1) Streamable HTTP 모드 (기본)

```bash
uv run wiki-mcp
```

기본값:
- `MCP_TRANSPORT=streamable`
- `MCP_HOST=0.0.0.0`
- `MCP_PORT=8002`
- 엔드포인트: `http://localhost:8002/mcp`

### 2) STDIO 모드

```bash
uv run wiki-mcp --transport stdio
```

### CLI 옵션
- `-v, --verbose`: 상세 로깅
- `--transport`: `streamable` 또는 `stdio`
- `--host`: 서버 호스트 (streamable 모드)
- `--port`: 서버 포트 (streamable 모드)

## 환경 변수

### MCP 서버
- `MCP_TRANSPORT` (`streamable` | `stdio`, 기본 `streamable`)
- `MCP_HOST` (기본 `0.0.0.0`)
- `MCP_PORT` (기본 `8002`)

### Confluence 연결
- `CONFLUENCE_URL` 또는
- `CONFLUENCE_HOST` + `CONFLUENCE_PORT` (+ 선택 `CONFLUENCE_PROTOCOL`)
- 인증:
  - Cloud: `CONFLUENCE_USERNAME` + `CONFLUENCE_API_TOKEN`
  - Server/DC: `CONFLUENCE_PERSONAL_TOKEN`
- 선택: `CONFLUENCE_SSL_VERIFY` (`true`/`false`)

## MCP Tools
- `wiki_get_page`
- `wiki_create_page`
- `wiki_update_page`
- `wiki_delete_page`
- `wiki_search`
- `wiki_get_spaces`

## Cursor 연동

### Streamable HTTP 방식

```json
{
  "mcpServers": {
    "wiki-mcp": {
      "url": "http://localhost:8002/mcp"
    }
  }
}
```

### STDIO 방식

```json
{
  "mcpServers": {
    "wiki-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\leeyo\\programming\\wiki_mcp\\mcp-wiki-ver2",
        "run",
        "wiki-mcp"
      ],
      "env": {
        "CONFLUENCE_URL": "http://localhost:8090",
        "CONFLUENCE_PERSONAL_TOKEN": "your-token-here"
      }
    }
  }
}
```

## 참고
- MCP Specification (HTTP Transport): https://spec.modelcontextprotocol.io/specification/2024-11-05/transport/#http
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
