# mcp-wiki-ver2 폴더 구조 요약

아래는 `mcp-wiki-ver2` 폴더의 상위 구조와 주요 하위 디렉터리입니다.

```
mcp-wiki-ver2/
├─ Dockerfile
├─ Dockerfile copy
├─ errorlog.md
├─ load-and-run.ps1
├─ newREAD.md
├─ pyproject.toml
├─ README.md
├─ save-all-images.ps1
├─ torenew.md
├─ uv.lock
├─ wikiREAD.md
└─ src/
   └─ wiki_mcp/
      ├─ __init__.py
      ├─ app.py
      ├─ api_client.py
      ├─ models.py
      ├─ server.py
      └─ __pycache__/
```

메모:
- `__pycache__/`는 파이썬 바이트코드 캐시 디렉터리입니다.

---

# mcp-wiki-ver2 MCP 서버 동작 흐름 요약

## 실행/진입 흐름 (분기 구조)
```
┌───────────────────────────────┐
│ main()  (wiki_mcp.__init__)    │
└───────────────┬───────────────┘
                │ --transport
        ┌───────┴────────┐
        │                │
        ▼                ▼
   stdio 모드        streamable 모드
   ──────────        ─────────────
   stdio_server      uvicorn.run(
   (create_mcp_server)  "wiki_mcp.app:create_app"
   )
```

## HTTP 모드 요청 처리 흐름
```
클라이언트 HTTP 요청
        │
        ▼
   /mcp 라우트
        │
        ▼
StreamableHTTPSessionManager.handle_request(...)
        │
        ▼
MCP 서버 (create_mcp_server)
```

## MCP 도구 호출 내부 흐름
```
call_tool(name, arguments)
        │
        ▼
_wiki_* 비동기 래퍼
        │
        ▼
get_wiki_client() → WikiClient
        │
        ▼
Confluence REST API 호출 (requests)
        │
        ▼
모델 변환(WikiPage/WikiSpace) → JSON 텍스트 응답
```

## Streamable HTTP 요청 → MCP 도구 호출 (파일 포함 다이어그램)
```
클라이언트 HTTP 요청
        │
        ▼
/mcp 라우트
  (src/wiki_mcp/app.py)
        │
        ▼
StreamableHTTPSessionManager.handle_request(...)
  (src/wiki_mcp/app.py)
        │
        ▼
call_tool(name, arguments)
  (src/wiki_mcp/server.py)
        │
        ▼
_wiki_* 비동기 래퍼
  (src/wiki_mcp/server.py)
        │
        ▼
get_wiki_client() → WikiClient
  (src/wiki_mcp/api_client.py)
        │
        ▼
Confluence REST API 요청
  (src/wiki_mcp/api_client.py)
        │
        ▼
WikiPage/WikiSpace 변환
  (src/wiki_mcp/models.py)
        │
        ▼
JSON 텍스트 응답 반환
  (src/wiki_mcp/server.py)
```

## 핵심 포인트 요약
- 엔트리: `wiki_mcp.__init__.main()`
- HTTP 엔드포인트: `/mcp` (`app.py`)
- 도구 정의/분기: `server.py`
- 외부 API 호출: `api_client.py` → Confluence REST API

## src/ 하위 파일별 역할
- `src/wiki_mcp/__init__.py`: CLI 엔트리포인트, transport/host/port 설정 및 서버 실행 분기
- `src/wiki_mcp/app.py`: Streamable HTTP용 ASGI 앱 구성, `/mcp` 요청 처리 라우팅
- `src/wiki_mcp/server.py`: MCP 서버 생성, 도구 등록/호출 분기, 비동기 래퍼 제공
- `src/wiki_mcp/api_client.py`: Confluence REST API 클라이언트, 인증/요청 처리
- `src/wiki_mcp/models.py`: Confluence 응답 데이터 모델(WikiPage/WikiSpace) 정의 및 변환
