# MCP 서버 핸즈온 교육 - wiki_get_page 전체 흐름

## 전체 아키텍처 흐름도

```
LLM (Claude, GPT 등)
  │
  │  JSON-RPC over HTTP POST
  ▼
┌─────────────────────────────────────────────────┐
│  Step 1. 서버 시작 (__init__.py)                 │
│  - FastMCP 인스턴스 생성 & HTTP 서버 실행         │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 2. Tool 등록 (server.py)                   │
│  - @mcp.tool() 데코레이터로 wiki_get_page 등록    │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 3. 에러 래퍼 (server.py - _run_tool)       │
│  - 모든 Tool 호출을 try/except로 감싸기           │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 4. 비즈니스 로직 (server.py - _wiki_get_page)│
│  - 인증 처리 + 동기→비동기 변환                    │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 5. API 클라이언트 (api_client.py)           │
│  - Confluence REST API 호출                      │
│  - GET /rest/api/content/{page_id}               │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Step 6. 데이터 모델 (models.py)                  │
│  - API 응답 → WikiPage 객체 → JSON               │
└─────────────────────────────────────────────────┘
```

---

## 파일 구조

```
@wiki_mcp_fastmcp/
├── run.py                        ← Step 0. 개발용 직접 실행 스크립트
├── src/wiki_mcp_fastmcp/
│   ├── __init__.py               ← Step 1. 서버 시작 (진입점)
│   ├── __main__.py               ← python -m 실행 지원
│   ├── server.py                 ← Step 2~4. Tool 등록 + 비즈니스 로직
│   ├── api_client.py             ← Step 5. Confluence REST API 클라이언트
│   └── models.py                 ← Step 6. 데이터 모델 (WikiPage, WikiSpace)
└── .env                          ← 환경변수 파일 (CONFLUENCE_URL, TOKEN 등)
```

---

## Step 0. 개발용 실행 스크립트 (run.py)

> 파일: `run.py`
> 역할: `pip install` 없이 바로 서버를 실행할 수 있는 개발용 스크립트.

### __init__.py로 직접 실행하면 안 되는 이유

`__init__.py`의 `main()` 함수를 호출하려면 원래 아래 과정이 필요하다:

```bash
# 정식 실행 방법 (패키지 설치 필요)
pip install -e .            # pyproject.toml 기반으로 패키지 설치
wiki-mcp-fastmcp --dev      # 설치된 CLI 명령어로 실행
```

하지만 **개발/교육 환경에서는 매번 `pip install`하기 번거롭다.**
`run.py`는 이 문제를 해결한다.

### run.py가 하는 3가지 일

```python
"""직접 실행 스크립트. pip install 없이 사용 가능."""
import sys
import os

# ★★★ [교육에 필요] 핵심 1: Python 경로에 src 디렉토리 추가 ★★★
# 역할: pip install 없이도 src/wiki_mcp_fastmcp를 import할 수 있게 한다.
#       이 한 줄이 없으면 "ModuleNotFoundError: No module named 'wiki_mcp_fastmcp'" 에러 발생
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "src"))

# ★★★ [교육에 필요] 핵심 2: --dev 환경변수를 import 전에 설정 ★★★
# 역할: server.py가 import될 때 AUTH_MODE를 읽으므로, import보다 먼저 설정해야 한다.
#       __init__.py에서는 click이 옵션을 파싱한 후에 설정하지만,
#       server.py 모듈 최상단의 _AUTH_MODE = os.environ.get("AUTH_MODE") 가
#       import 시점에 이미 실행되므로 타이밍이 중요하다.
if "--dev" in sys.argv:
    os.environ.setdefault("AUTH_MODE", "env")
    os.environ.setdefault("ALLOW_LEGACY_ENV_TOKEN", "true")

# ★★★ [교육에 필요] 핵심 3: 환경변수 로드 및 설정 확인 출력 ★★★
# 역할: .env 파일을 로드하고, Confluence 연결 정보가 올바른지 시작 전에 확인한다.
#       토큰이 없으면 서버가 시작되어도 API 호출 시 에러가 나므로 미리 알려준다.
from dotenv import load_dotenv
load_dotenv()
token = os.environ.get("CONFLUENCE_PERSONAL_TOKEN", "")
url = os.environ.get("CONFLUENCE_URL") or (
    os.environ.get("CONFLUENCE_PROTOCOL", "http") + "://" +
    os.environ.get("CONFLUENCE_HOST", "") + ":" +
    os.environ.get("CONFLUENCE_PORT", "8090")
)
print(f"[startup] CONFLUENCE URL : {url}")
print(f"[startup] TOKEN 설정 여부 : {'✅ 있음' if token else '❌ 없음 (.env 확인 필요)'}")

from wiki_mcp_fastmcp import main

if __name__ == "__main__":
    main()
```

### 실행 방법 비교

| 방법 | 명령어 | 사전 준비 |
|------|--------|-----------|
| **run.py (개발용)** | `python run.py --dev` | 없음 (바로 실행) |
| 패키지 설치 후 | `wiki-mcp-fastmcp --dev` | `pip install -e .` 필요 |
| 모듈 실행 | `python -m wiki_mcp_fastmcp --dev` | `pip install -e .` 필요 |

### --dev 플래그의 의미

```
python run.py --dev
```

`--dev` 없이 실행하면 **AUTH_MODE=request_pat** (기본값)이 적용되어,
모든 MCP 요청에 `x-personal-token` 헤더가 필수가 된다. (운영 환경용)

`--dev`를 붙이면 **AUTH_MODE=env**로 전환되어,
`.env` 파일의 `CONFLUENCE_PERSONAL_TOKEN`을 공용으로 사용한다. (개발/교육용)

```
운영 모드 (기본):  LLM 요청마다 개인 토큰을 헤더에 포함해야 함
개발 모드 (--dev): .env의 토큰 하나로 모든 요청을 처리 (테스트에 편리)
```

---

## Step 1. 서버 시작

> 파일: `src/wiki_mcp_fastmcp/__init__.py`
> 역할: CLI 진입점. FastMCP 서버를 생성하고 HTTP로 실행한다.

```python
"""CLI entrypoint for the FastMCP-based Wiki MCP server."""

from __future__ import annotations

import os

import click                          # [교육에 필요] CLI 옵션 파싱 라이브러리
from dotenv import load_dotenv        # [교육에 필요] .env 파일에서 환경변수 로드

from .server import create_mcp_server # [교육에 필요] MCP 서버 팩토리 함수 import

load_dotenv()                         # [교육에 필요] .env 파일의 환경변수를 os.environ에 로드


@click.command()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
@click.option(
    "--port",
    type=int,
    default=lambda: int(os.environ.get("MCP_PORT", "8002")),
    show_default="MCP_PORT or 8002",
    help="Port to bind for streamable HTTP transport.",
)
@click.option(
    "--host",
    default=lambda: os.environ.get("MCP_HOST", "0.0.0.0"),
    show_default="MCP_HOST or 0.0.0.0",
    help="Host to bind for streamable HTTP transport.",
)
@click.option(
    "--path",
    default=lambda: os.environ.get("MCP_PATH", "/mcp"),
    show_default="MCP_PATH or /mcp",
    help="MCP endpoint path for streamable HTTP transport.",
)
@click.option(
    "--dev",
    is_flag=True,
    help="Dev mode: use env-var auth (no request PAT header required).",
)
def main(verbose: bool, port: int, host: str, path: str, dev: bool) -> None:
    """Start the FastMCP-based Wiki server."""

    # [교육에 필요] dev 모드일 때 환경변수 인증으로 전환 (PAT 헤더 불필요)
    if dev:
        os.environ.setdefault("AUTH_MODE", "env")
        os.environ.setdefault("ALLOW_LEGACY_ENV_TOKEN", "true")
        click.echo(f"[dev mode] AUTH_MODE=env, ALLOW_LEGACY_ENV_TOKEN=true")
        click.echo(f"[dev mode] Listening on http://{host}:{port}{path}")

    # ★★★ [교육에 필요] 핵심 2줄: 서버 생성 → 실행 ★★★
    # 역할: FastMCP 인스턴스를 만들고, streamable-http 방식으로 서버를 기동한다.
    mcp = create_mcp_server()
    mcp.run(
        transport="streamable-http",   # MCP 전송 방식 (streamable HTTP)
        host=host,                     # 바인딩 호스트 (기본: 0.0.0.0)
        port=port,                     # 바인딩 포트 (기본: 8002)
        path=path,                     # MCP 엔드포인트 경로 (기본: /mcp)
        log_level="debug" if verbose else "info",
    )
```

### 이 단계에서 이해해야 할 것
- `FastMCP`는 MCP 프로토콜 서버를 쉽게 만들어주는 프레임워크
- `mcp.run(transport="streamable-http")`로 HTTP 서버가 시작됨
- LLM 클라이언트는 `http://{host}:{port}{path}`로 요청을 보냄

---

## Step 2. Tool 등록

> 파일: `src/wiki_mcp_fastmcp/server.py` (29~34행)
> 역할: `@mcp.tool()` 데코레이터로 LLM이 호출할 수 있는 Tool을 등록한다.

```python
from fastmcp import Context, FastMCP  # [교육에 필요] FastMCP 프레임워크 import

def create_mcp_server() -> FastMCP:
    # [교육에 필요] FastMCP 인스턴스 생성. 이름은 LLM에게 노출되는 서버 이름이다.
    # 역할: MCP 서버 객체를 만든다. 이 객체에 Tool들을 등록하게 된다.
    mcp = FastMCP("wiki-mcp-fastmcp")

    # ★★★ [교육에 필요] Tool 등록 - 가장 핵심적인 부분 ★★★
    # 역할: LLM이 "wiki_get_page"라는 이름으로 이 함수를 호출할 수 있게 등록한다.
    # - name: LLM이 사용하는 Tool 이름
    # - description: LLM이 이 Tool을 언제 써야 하는지 판단하는 설명
    # - page_id: LLM이 넘겨주는 파라미터 (함수 시그니처에서 자동 추출)
    # - ctx: MCP 컨텍스트 (세션 정보, 요청 헤더 등 포함)
    @mcp.tool(
        name="wiki_get_page",
        description="Get a Confluence page by page ID.",
    )
    async def wiki_get_page(page_id: str, ctx: Context) -> str:
        return await _run_tool("wiki_get_page", _wiki_get_page, page_id, ctx)

    # ... (다른 Tool 등록들은 생략) ...

    return mcp  # [교육에 필요] 등록 완료된 MCP 서버를 반환
```

### 이 단계에서 이해해야 할 것
- `@mcp.tool()` 데코레이터 하나로 LLM이 호출 가능한 Tool이 된다
- 함수 파라미터(`page_id: str`)가 자동으로 Tool의 입력 스키마가 된다
- `description`은 LLM이 Tool 선택 시 참고하는 설명이므로 중요하다

---

## Step 3. 에러 래퍼

> 파일: `src/wiki_mcp_fastmcp/server.py` (127~138행)
> 역할: 모든 Tool 호출을 감싸서 예외 발생 시 에러 JSON을 반환한다.

```python
# ★★★ [교육에 필요] 공통 에러 처리 래퍼 ★★★
# 역할: Tool 실행 중 에러가 나도 서버가 죽지 않고, 에러 내용을 JSON으로 LLM에게 전달한다.
#       이렇게 해야 LLM이 에러 메시지를 읽고 사용자에게 안내할 수 있다.
async def _run_tool(tool_name: str, func, *args) -> str:
    try:
        return await func(*args)       # 실제 Tool 함수 호출
    except Exception as exc:
        logger.error("Error calling tool %s: %s", tool_name, exc, exc_info=True)
        return json.dumps(             # 에러를 JSON 문자열로 변환하여 반환
            {
                "error": str(exc),
                "tool": tool_name,
            },
            ensure_ascii=False,
        )
```

### 이 단계에서 이해해야 할 것
- Tool 함수에서 예외가 발생해도 MCP 서버는 계속 동작한다
- 에러 메시지가 LLM에게 전달되어, LLM이 사용자에게 설명할 수 있다

---

## Step 4. 비즈니스 로직

> 파일: `src/wiki_mcp_fastmcp/server.py` (161~194행)
> 역할: 인증 정보를 추출하고, Confluence API를 호출하여 페이지 데이터를 JSON으로 반환한다.

```python
# ── 인증 관련 헬퍼 함수들 ──

# [교육에 필요] 요청 헤더에서 인증 정보를 추출하는 함수
# 역할: MCP 요청의 HTTP 헤더에서 사용자 ID, PAT 토큰 등을 꺼낸다.
def _get_request_header(ctx: Context | None, header_name: str) -> str:
    if ctx is None:
        return ""
    request_context = ctx.request_context
    if request_context is None or request_context.request is None:
        return ""
    return request_context.request.headers.get(header_name, "").strip()


# [교육에 필요] 클라이언트 인증 정보를 결정하는 함수
# 역할: AUTH_MODE에 따라 요청 헤더의 PAT 또는 환경변수의 토큰을 사용할지 결정한다.
def _resolve_client_credentials(
    ctx: Context | None,
) -> tuple[str, str | None, bool]:
    # AUTH_MODE가 "request_pat"이 아니면 환경변수 토큰 사용
    if _AUTH_MODE != "request_pat":
        return _resolve_client_key(ctx), None, True

    # 요청 헤더에서 사용자 ID와 PAT 추출 시도
    client_key = _get_request_header(ctx, _USER_ID_HEADER) or _resolve_client_key(ctx)
    personal_token = _get_request_header(ctx, _PAT_HEADER)
    if personal_token:
        return client_key, personal_token, False

    # 환경변수 폴백 허용 시
    if _ALLOW_LEGACY_ENV_TOKEN:
        return client_key, None, True

    raise WikiClientError(f"Missing request PAT header '{_PAT_HEADER}'.")


# ── wiki_get_page 핵심 구현 ──

# ★★★ [교육에 필요] wiki_get_page의 실제 구현부 ★★★
# 역할: 인증 처리 → WikiClient 획득 → Confluence API 호출 → JSON 직렬화
async def _wiki_get_page(page_id: str, ctx: Context | None = None) -> str:
    # [교육에 필요] 인증 정보 추출
    # 역할: 요청 컨텍스트에서 누구의 토큰으로 Confluence에 접근할지 결정
    client_key, personal_token, allow_legacy_env_token = _resolve_client_credentials(ctx)

    # [교육에 필요] 동기 함수를 정의 (requests 라이브러리가 동기이므로)
    def _sync_get_page() -> str:
        # 역할: 인증 정보로 WikiClient를 가져온다 (캐싱됨)
        client = get_wiki_client(
            client_key=client_key,
            personal_token=personal_token,
            allow_legacy_env_token=allow_legacy_env_token,
        )
        # 역할: Confluence REST API를 호출하여 페이지를 가져온다
        page = client.get_page(page_id)

        # 역할: WikiPage 객체를 dict로 변환하고, content(본문)를 추가
        data = page.to_dict()         # id, title, space_key 등 메타정보
        data["content"] = page.content # HTML 본문 추가
        return json.dumps(data, ensure_ascii=False, indent=2)

    # [교육에 필요] asyncio.to_thread로 동기 호출을 비동기로 변환
    # 역할: 동기 HTTP 호출이 이벤트 루프를 블로킹하지 않도록 별도 스레드에서 실행
    return await asyncio.to_thread(_sync_get_page)
```

### 이 단계에서 이해해야 할 것
- MCP 서버는 `async`로 동작하지만, `requests` 라이브러리는 동기이다
- `asyncio.to_thread()`로 동기 코드를 비동기 환경에서 안전하게 실행한다
- 인증은 요청 헤더의 PAT 또는 환경변수 토큰 두 가지 방식을 지원한다

---

## Step 5. Confluence API 클라이언트

> 파일: `src/wiki_mcp_fastmcp/api_client.py`
> 역할: Confluence REST API와 실제로 HTTP 통신하는 클라이언트.

```python
import requests                      # [교육에 필요] HTTP 요청 라이브러리
from .models import WikiPage         # [교육에 필요] 응답 파싱용 데이터 모델


# ★★★ [교육에 필요] Confluence REST API 클라이언트 클래스 ★★★
# 역할: Confluence 서버와 통신하는 HTTP 클라이언트. 인증, 요청, 에러 처리를 담당한다.
class WikiClient:

    def __init__(
        self,
        url: str | None = None,
        personal_token: str | None = None,
        ssl_verify: bool | None = None,
    ):
        # [교육에 필요] Confluence URL 결정
        # 역할: 환경변수에서 Confluence 서버 주소를 읽어온다.
        #       CONFLUENCE_URL 또는 CONFLUENCE_HOST + PORT 조합
        if url:
            self.url = url
        elif os.environ.get("CONFLUENCE_URL"):
            self.url = os.environ.get("CONFLUENCE_URL")
        else:
            host = os.environ.get("CONFLUENCE_HOST", "")
            port = os.environ.get("CONFLUENCE_PORT", "8090")
            protocol = os.environ.get("CONFLUENCE_PROTOCOL", "http")
            self.url = f"{protocol}://{host}:{port}" if host else ""

        # [교육에 필요] 인증 토큰 설정
        # 역할: Personal Access Token을 파라미터 또는 환경변수에서 가져온다.
        self.personal_token = personal_token or os.environ.get(
            "CONFLUENCE_PERSONAL_TOKEN", ""
        )

        # [교육에 필요] requests.Session 설정
        # 역할: HTTP 세션을 만들고 공통 헤더와 인증 토큰을 세팅한다.
        #       Session을 사용하면 연결을 재사용하여 성능이 좋아진다.
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        if self.personal_token:
            self.session.headers["Authorization"] = f"Bearer {self.personal_token}"

    @property
    def api_url(self) -> str:
        # 역할: Confluence REST API 기본 URL (예: http://host:8090/rest/api)
        return f"{self.url}/rest/api"

    # [교육에 필요] HTTP 요청 공통 메서드
    # 역할: 모든 API 호출의 공통 로직 (요청 전송, 에러 처리, JSON 파싱)
    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json_data: dict | None = None,
    ) -> dict | list | None:
        request_url = f"{self.api_url}{endpoint}"
        try:
            response = self.session.request(
                method=method,
                url=request_url,
                params=params,
                json=json_data,
            )
            if response.status_code in (401, 403):
                raise WikiAuthenticationError(
                    f"Authentication failed ({response.status_code})."
                )
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()
        except requests.exceptions.RequestException as exc:
            if isinstance(exc, requests.exceptions.HTTPError):
                try:
                    error_detail = exc.response.json()
                    message = error_detail.get("message", str(exc))
                except Exception:
                    message = str(exc)
                raise WikiClientError(f"API error: {message}") from exc
            raise WikiClientError(f"Request failed: {exc}") from exc

    # ★★★ [교육에 필요] 페이지 조회 메서드 ★★★
    # 역할: Confluence REST API GET /rest/api/content/{page_id} 호출
    #       expand 파라미터로 본문(body.storage), 버전, 스페이스 정보를 함께 가져온다.
    def get_page(
        self,
        page_id: str,
        expand: str = "body.storage,version,space",
    ) -> WikiPage:
        response = self._request(
            "GET",
            f"/content/{page_id}",          # Confluence REST API 엔드포인트
            params={"expand": expand},       # 어떤 필드를 확장해서 가져올지
        )
        # 역할: API 응답 JSON을 WikiPage 객체로 변환
        return WikiPage.from_api_response(response, self.url)


# ── 클라이언트 캐싱 (팩토리 패턴) ──

_clients: dict[str, WikiClient] = {}      # 클라이언트 캐시
_clients_lock = threading.Lock()          # 스레드 안전 보장

# [교육에 필요] 클라이언트 팩토리 함수
# 역할: 동일한 인증 정보에 대해 WikiClient를 재사용한다. (매번 새로 만들지 않음)
def get_wiki_client(
    client_key: str | None = None,
    personal_token: str | None = None,
    allow_legacy_env_token: bool = True,
) -> WikiClient:
    resolved_key = (client_key or "default").strip() or "default"
    resolved_token = (personal_token or "").strip()

    with _clients_lock:                    # 스레드 안전하게 캐시 접근
        existing = _clients.get(resolved_key)
        if existing is not None and _client_tokens.get(resolved_key, "") == resolved_token:
            return existing                # 캐시된 클라이언트 반환

        # 새 클라이언트 생성
        client = WikiClient(personal_token=resolved_token) if resolved_token else WikiClient()
        _clients[resolved_key] = client
        return client
```

### 이 단계에서 이해해야 할 것
- Confluence REST API: `GET /rest/api/content/{page_id}?expand=body.storage,version,space`
- `expand` 파라미터로 본문, 버전, 스페이스 정보를 한 번에 가져온다
- `requests.Session`으로 연결을 재사용하고 인증 헤더를 공통 설정한다
- 클라이언트 캐싱으로 동일 사용자의 반복 요청 시 성능을 최적화한다

---

## Step 6. 데이터 모델

> 파일: `src/wiki_mcp_fastmcp/models.py`
> 역할: Confluence API 응답 JSON을 Python 객체로 변환하는 데이터 모델.

```python
from dataclasses import dataclass     # [교육에 필요] Python 데이터 클래스
from typing import Any


# ★★★ [교육에 필요] Confluence 페이지 데이터 모델 ★★★
# 역할: Confluence API의 복잡한 JSON 응답을 깔끔한 Python 객체로 변환한다.
@dataclass
class WikiPage:
    id: str            # 페이지 고유 ID
    title: str         # 페이지 제목
    space_key: str     # 스페이스 키 (예: "DEV", "TEST")
    space_name: str    # 스페이스 이름
    version: int       # 페이지 버전 번호
    content: str       # 페이지 HTML 본문
    url: str           # 페이지 웹 URL

    # [교육에 필요] Confluence API 응답 → WikiPage 객체
    # 역할: 중첩된 JSON 구조에서 필요한 필드만 추출하여 flat한 객체로 만든다.
    #
    # Confluence API 응답 예시:
    # {
    #   "id": "12345",
    #   "title": "My Page",
    #   "space": {"key": "DEV", "name": "Development"},
    #   "version": {"number": 3},
    #   "body": {"storage": {"value": "<p>Hello</p>"}},
    #   "_links": {"webui": "/pages/viewpage.action?pageId=12345"}
    # }
    @classmethod
    def from_api_response(cls, data: dict[str, Any], base_url: str) -> "WikiPage":
        space = data.get("space", {})
        body = data.get("body", {}).get("storage", {})
        links = data.get("_links", {})
        webui = links.get("webui", "")
        page_url = f"{base_url}{webui}" if webui else ""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            space_key=space.get("key", ""),
            space_name=space.get("name", ""),
            version=data.get("version", {}).get("number", 1),
            content=body.get("value", ""),   # HTML 본문
            url=page_url,
        )

    # [교육에 필요] WikiPage 객체 → dict (JSON 직렬화용)
    # 역할: LLM에게 반환할 데이터를 dict로 변환한다.
    #       주의: content(본문)는 여기에 포함되지 않고, server.py에서 별도로 추가한다.
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "space_key": self.space_key,
            "space_name": self.space_name,
            "version": self.version,
            "url": self.url,
        }
```

### 이 단계에서 이해해야 할 것
- Confluence API 응답은 깊게 중첩된 JSON이다 (`body.storage.value` 등)
- `from_api_response()`가 이를 flat한 구조로 변환한다
- `to_dict()`는 LLM에게 반환할 메타정보만 포함한다 (content는 별도 추가)

---

## 최종 호출 체인 요약

```
LLM이 tools/call 요청 전송
  │
  ▼
[Step 2] @mcp.tool - wiki_get_page(page_id, ctx)
  │
  ▼
[Step 3] _run_tool("wiki_get_page", _wiki_get_page, page_id, ctx)
  │      → try/except로 에러 처리
  ▼
[Step 4] _wiki_get_page(page_id, ctx)
  │      → _resolve_client_credentials(ctx) : 인증 정보 추출
  │      → asyncio.to_thread(_sync_get_page) : 동기→비동기 변환
  ▼
[Step 5] get_wiki_client() → client.get_page(page_id)
  │      → _request("GET", "/content/{page_id}")
  │      → Confluence 서버에 HTTP GET 요청
  ▼
[Step 6] WikiPage.from_api_response(response)
  │      → API JSON → WikiPage 객체
  │      → to_dict() + content 추가 → json.dumps()
  ▼
LLM에게 JSON 결과 반환
```

---

## 필수 환경변수

| 환경변수 | 설명 | 예시 |
|---------|------|------|
| `CONFLUENCE_URL` | Confluence 서버 URL | `http://confluence.company.com` |
| `CONFLUENCE_PERSONAL_TOKEN` | API 인증 토큰 | `NjE2MDI4...` |
| `MCP_PORT` | MCP 서버 포트 (기본: 8002) | `8002` |
| `MCP_HOST` | MCP 서버 호스트 (기본: 0.0.0.0) | `0.0.0.0` |
| `AUTH_MODE` | 인증 모드 (기본: request_pat) | `env` 또는 `request_pat` |

---

## 핸즈온 권장 순서

교육 시 **바닥부터 쌓아올리는 순서**로 진행하면 이해하기 쉽습니다:

1. **Step 6 (models.py)** - 데이터 구조 먼저 정의
2. **Step 5 (api_client.py)** - Confluence API 호출 구현
3. **Step 4 (server.py - _wiki_get_page)** - 비즈니스 로직 작성
4. **Step 3 (server.py - _run_tool)** - 에러 처리 래퍼 추가
5. **Step 2 (server.py - @mcp.tool)** - Tool로 등록
6. **Step 1 (__init__.py)** - 서버 시작 진입점 작성
7. **Step 0 (run.py)** - 개발용 실행 스크립트로 `python run.py --dev` 실행

이렇게 하면 각 단계의 입력/출력을 확인하며 점진적으로 완성할 수 있습니다.

### run.py가 필요한 이유 정리

| 문제 | run.py의 해결 |
|------|--------------|
| `pip install -e .` 없이 실행 불가 | `sys.path.insert()`로 src 경로 직접 추가 |
| server.py import 시 AUTH_MODE가 이미 결정됨 | import 전에 `--dev` 환경변수를 먼저 설정 |
| 토큰/URL 설정 누락 시 에러 원인 파악 어려움 | 시작 시 설정 상태를 출력하여 바로 확인 가능 |
