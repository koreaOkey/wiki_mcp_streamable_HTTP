"""FastMCP server definition for Wiki tools."""

from __future__ import annotations

import asyncio
import json
import logging
import os

from fastmcp import Context, FastMCP  # [교육에 필요] FastMCP 프레임워크 import
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .api_client import WikiClientError, get_wiki_client

logger = logging.getLogger("wiki-mcp-fastmcp.server")

# [교육에 필요] 모듈 최상단에서 환경변수를 읽는다.
# 주의: import 시점에 실행되므로, run.py에서 --dev 환경변수를 import 전에 설정해야 한다.
_AUTH_MODE = os.environ.get("AUTH_MODE", "request_pat").strip().lower()
_ALLOW_LEGACY_ENV_TOKEN = (
    os.environ.get("ALLOW_LEGACY_ENV_TOKEN", "false").strip().lower() == "true"
)
_USER_ID_HEADER = os.environ.get("MCP_USER_ID_HEADER", "x-user-id").strip().lower()
_PAT_HEADER = os.environ.get("MCP_PAT_HEADER", "x-personal-token").strip().lower()


def create_mcp_server() -> FastMCP:
    # [교육에 필요] FastMCP 인스턴스 생성. 이름은 LLM에게 노출되는 서버 이름이다.
    # 역할: MCP 서버 객체를 만든다. 이 객체에 Tool들을 등록하게 된다.
    mcp = FastMCP("wiki-mcp-fastmcp")

    '''★★★ [교육에 필요] Tool 등록 - 가장 핵심적인 부분 ★★★'''
    # 역할: LLM이 "wiki_get_page"라는 이름으로 이 함수를 호출할 수 있게 등록한다.
    # - name: LLM이 사용하는 Tool 이름
    # - description: LLM이 이 Tool을 언제 써야 하는지 판단하는 설명
    # - page_id: LLM이 넘겨주는 파라미터 (함수 시그니처에서 자동 추출)
    # - ctx: MCP 컨텍스트 (세션 정보, 요청 헤더 등 포함)

    # @mcp.tool(
    #     name="wiki_get_page",
    #     description="Get a Confluence page by page ID.",
    # )
    # async def wiki_get_page(page_id: str, ctx: Context) -> str:
    #     return await _run_tool("wiki_get_page", _wiki_get_page, page_id, ctx)

    @mcp.tool(
        name="wiki_create_page",
        description="Create a new Confluence page.",
    )
    async def wiki_create_page(
        space_key: str,
        title: str,
        content: str,
        parent_id: str | None = None,
        ctx: Context = None,
    ) -> str:
        return await _run_tool(
            "wiki_create_page",
            _wiki_create_page,
            space_key,
            title,
            content,
            parent_id,
            ctx,
        )

    @mcp.tool(
        name="wiki_update_page",
        description="Update an existing Confluence page.",
    )
    async def wiki_update_page(
        page_id: str,
        title: str,
        content: str,
        version_comment: str | None = None,
        ctx: Context = None,
    ) -> str:
        return await _run_tool(
            "wiki_update_page",
            _wiki_update_page,
            page_id,
            title,
            content,
            version_comment,
            ctx,
        )

    @mcp.tool(
        name="wiki_delete_page",
        description="Delete a Confluence page.",
    )
    async def wiki_delete_page(page_id: str, ctx: Context) -> str:
        return await _run_tool("wiki_delete_page", _wiki_delete_page, page_id, ctx)

    @mcp.tool(
        name="wiki_search",
        description="Search Confluence pages by query/CQL.",
    )
    async def wiki_search(query: str, limit: int = 10, ctx: Context = None) -> str:
        return await _run_tool("wiki_search", _wiki_search, query, limit, ctx)

    @mcp.tool(
        name="wiki_get_spaces",
        description="List Confluence spaces.",
    )
    async def wiki_get_spaces(limit: int = 25, ctx: Context = None) -> str:
        return await _run_tool("wiki_get_spaces", _wiki_get_spaces, limit, ctx)

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(_request: Request) -> Response:
        return JSONResponse({"status": "ok"})

    @mcp.custom_route("/info", methods=["GET"])
    async def info(_request: Request) -> Response:
        return JSONResponse(
            {
                "name": "Wiki MCP Server (FastMCP)",
                "version": "0.1.0",
                "transport": "streamable-http",
                "auth": {
                    "mode": _AUTH_MODE,
                    "allow_legacy_env_token": _ALLOW_LEGACY_ENV_TOKEN,
                    "user_id_header": _USER_ID_HEADER,
                    "pat_header": _PAT_HEADER,
                },
                "endpoints": {
                    "mcp": "/mcp",
                    "health": "/health",
                    "info": "/info",
                },
            }
        )

    return mcp


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


def _resolve_client_key(ctx: Context | None) -> str:
    if ctx is None:
        return "default"
    if ctx.client_id:
        return str(ctx.client_id)
    try:
        return str(ctx.session_id)
    except RuntimeError:
        return "default"


# 역할: MCP 요청의 HTTP 헤더에서 사용자 ID, PAT 토큰 등을 꺼낸다.
def _get_request_header(ctx: Context | None, header_name: str) -> str:
    if ctx is None:
        return ""
    request_context = ctx.request_context
    if request_context is None or request_context.request is None:
        return ""
    return request_context.request.headers.get(header_name, "").strip()


# 클라이언트 인증 정보를 결정하는 함수
# 역할: AUTH_MODE에 따라 요청 헤더의 PAT 또는 환경변수의 토큰을 사용할지 결정한다.
#       - request_pat 모드: 요청 헤더에서 PAT 추출 (운영 환경)
#       - env 모드: 환경변수의 CONFLUENCE_PERSONAL_TOKEN 사용 (개발 환경)
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

    raise WikiClientError(
        f"Missing request PAT header '{_PAT_HEADER}'."
    )


'''★★★ [교육에 필요] wiki_get_page의 실제 구현부 ★★★'''
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
        data = page.to_dict()          # id, title, space_key 등 메타정보
        data["content"] = page.content  # HTML 본문 추가
        return json.dumps(data, ensure_ascii=False, indent=2)

    # [교육에 필요] asyncio.to_thread로 동기 호출을 비동기로 변환
    # 역할: 동기 HTTP 호출이 이벤트 루프를 블로킹하지 않도록 별도 스레드에서 실행
    return await asyncio.to_thread(_sync_get_page)


async def _wiki_create_page(
    space_key: str,
    title: str,
    content: str,
    parent_id: str | None = None,
    ctx: Context | None = None,
) -> str:
    client_key, personal_token, allow_legacy_env_token = _resolve_client_credentials(ctx)

    def _sync_create_page() -> str:
        client = get_wiki_client(
            client_key=client_key,
            personal_token=personal_token,
            allow_legacy_env_token=allow_legacy_env_token,
        )
        page = client.create_page(
            space_key=space_key,
            title=title,
            content=content,
            parent_id=parent_id,
        )
        return json.dumps(
            {"message": "Page created", "page": page.to_dict()},
            ensure_ascii=False,
            indent=2,
        )

    return await asyncio.to_thread(_sync_create_page)


async def _wiki_update_page(
    page_id: str,
    title: str,
    content: str,
    version_comment: str | None = None,
    ctx: Context | None = None,
) -> str:
    client_key, personal_token, allow_legacy_env_token = _resolve_client_credentials(ctx)

    def _sync_update_page() -> str:
        client = get_wiki_client(
            client_key=client_key,
            personal_token=personal_token,
            allow_legacy_env_token=allow_legacy_env_token,
        )
        page = client.update_page(
            page_id=page_id,
            title=title,
            content=content,
            version_comment=version_comment,
        )
        return json.dumps(
            {"message": "Page updated", "page": page.to_dict()},
            ensure_ascii=False,
            indent=2,
        )

    return await asyncio.to_thread(_sync_update_page)


async def _wiki_delete_page(page_id: str, ctx: Context | None = None) -> str:
    client_key, personal_token, allow_legacy_env_token = _resolve_client_credentials(ctx)

    def _sync_delete_page() -> str:
        client = get_wiki_client(
            client_key=client_key,
            personal_token=personal_token,
            allow_legacy_env_token=allow_legacy_env_token,
        )
        client.delete_page(page_id)
        return json.dumps(
            {"message": f"Page {page_id} deleted"},
            ensure_ascii=False,
        )

    return await asyncio.to_thread(_sync_delete_page)


async def _wiki_search(
    query: str,
    limit: int = 10,
    ctx: Context | None = None,
) -> str:
    client_key, personal_token, allow_legacy_env_token = _resolve_client_credentials(ctx)

    def _sync_search() -> str:
        client = get_wiki_client(
            client_key=client_key,
            personal_token=personal_token,
            allow_legacy_env_token=allow_legacy_env_token,
        )
        pages = client.search(query, limit=limit)
        return json.dumps(
            {"count": len(pages), "results": [page.to_dict() for page in pages]},
            ensure_ascii=False,
            indent=2,
        )

    return await asyncio.to_thread(_sync_search)


async def _wiki_get_spaces(limit: int = 25, ctx: Context | None = None) -> str:
    client_key, personal_token, allow_legacy_env_token = _resolve_client_credentials(ctx)

    def _sync_get_spaces() -> str:
        client = get_wiki_client(
            client_key=client_key,
            personal_token=personal_token,
            allow_legacy_env_token=allow_legacy_env_token,
        )
        spaces = client.get_spaces(limit=limit)
        return json.dumps(
            {"count": len(spaces), "spaces": [space.to_dict() for space in spaces]},
            ensure_ascii=False,
            indent=2,
        )

    return await asyncio.to_thread(_sync_get_spaces)
