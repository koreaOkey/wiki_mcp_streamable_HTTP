# wiki-mcp-fastmcp

기존 `wiki_mcp` 구현을 FastMCP 기반으로 분리한 Confluence MCP 서버입니다.

## 기능

- `wiki_get_page`
- `wiki_create_page`
- `wiki_update_page`
- `wiki_delete_page`
- `wiki_search`
- `wiki_get_spaces`
- HTTP 엔드포인트: `/mcp`, `/health`, `/info`

## 환경변수

- `CONFLUENCE_URL` 또는 `CONFLUENCE_HOST` + `CONFLUENCE_PORT` (+ 선택: `CONFLUENCE_PROTOCOL`)
- Server/DC 인증: `CONFLUENCE_PERSONAL_TOKEN`
- `CONFLUENCE_SSL_VERIFY` (`true`/`false`, 기본값: `true`)
- `MCP_HOST` (기본값: `0.0.0.0`)
- `MCP_PORT` (기본값: `8002`)
- `MCP_PATH` (기본값: `/mcp`)

## 실행

```bash
cd @wiki_mcp_fastmcp
uv run wiki-mcp-fastmcp --host 0.0.0.0 --port 8002
```

## 프로젝트 구조

```text
@wiki_mcp_fastmcp/
+-- pyproject.toml
+-- README.md
`-- src/
    `-- wiki_mcp_fastmcp/
        +-- __init__.py
        +-- __main__.py
        +-- server.py
        +-- api_client.py
        `-- models.py
```

## 파일 역할

- `pyproject.toml`: 프로젝트 메타데이터, 의존성, CLI 스크립트(`wiki-mcp-fastmcp`) 엔트리 정의
- `README.md`: 사용 방법과 구조 문서
- `src/wiki_mcp_fastmcp/__init__.py`: CLI 엔트리포인트. 실행 옵션(`host`, `port`, `path`, `verbose`)을 파싱하고 Streamable HTTP 모드로 서버 실행
- `src/wiki_mcp_fastmcp/__main__.py`: `python -m wiki_mcp_fastmcp` 실행용 모듈 진입점 (`main()` 위임)
- `src/wiki_mcp_fastmcp/server.py`: FastMCP 서버 생성, 툴 등록(`wiki_get_page`, `wiki_create_page`, `wiki_update_page`, `wiki_delete_page`, `wiki_search`, `wiki_get_spaces`), 커스텀 라우트(`/health`, `/info`) 제공
- `src/wiki_mcp_fastmcp/api_client.py`: Confluence REST API 인증/요청 처리 및 페이지/검색/스페이스 기능 래핑
- `src/wiki_mcp_fastmcp/models.py`: `WikiPage`, `WikiSpace` 데이터 모델과 API 응답 변환 헬퍼

참고:
- `__pycache__/`는 실행 시 생성되는 캐시 파일로, 소스 구조 설계 대상에서 제외됩니다.

## Multi-user Request Auth (Simple PAT per request)

This server supports multi-user auth by reading a personal token from each MCP request.

### Environment variables

- `AUTH_MODE` (default: `request_pat`)
- `ALLOW_LEGACY_ENV_TOKEN` (default: `false`)
- `MCP_USER_ID_HEADER` (default: `x-user-id`)
- `MCP_PAT_HEADER` (default: `x-personal-token`)

### Request headers used by tools

- `x-user-id`: Optional. Used as client key for connection reuse.
- `x-personal-token`: Required when `AUTH_MODE=request_pat` and legacy fallback is disabled.

If `ALLOW_LEGACY_ENV_TOKEN=true`, missing request token falls back to `CONFLUENCE_PERSONAL_TOKEN`.
