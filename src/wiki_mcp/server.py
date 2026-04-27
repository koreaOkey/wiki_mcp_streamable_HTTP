"""Wiki MCP Server 정의 (Streamable HTTP)."""

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool
# [fastmcp 전환] 위 두 import는 FastMCP 중심 import로 교체.
# 예: from fastmcp import FastMCP

from .api_client import get_wiki_client

logger = logging.getLogger("wiki-mcp.server")


def create_mcp_server() -> Server:
    """MCP 서버 인스턴스를 생성한다."""
    # [fastmcp 전환] 반환 타입을 Server -> FastMCP로 변경.
    server = Server("wiki-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """사용 가능한 도구 목록을 반환한다."""
        # [fastmcp 전환] list_tools/call_tool 수동 디스패치 대신
        # @wiki_mcp.tool() 데코레이터로 각 함수를 직접 등록 가능.
        return [
            Tool(
                name="wiki_get_page",
                description="Confluence 페이지를 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "페이지 ID",
                        }
                    },
                    "required": ["page_id"],
                },
            ),
            Tool(
                name="wiki_create_page",
                description="새 Confluence 페이지를 생성합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "스페이스 키 (예: DEV, TEST)",
                        },
                        "title": {
                            "type": "string",
                            "description": "페이지 제목",
                        },
                        "content": {
                            "type": "string",
                            "description": "페이지 내용 (HTML 형식)",
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "부모 페이지 ID (선택)",
                        },
                    },
                    "required": ["space_key", "title", "content"],
                },
            ),
            Tool(
                name="wiki_update_page",
                description="Confluence 페이지를 업데이트합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "페이지 ID",
                        },
                        "title": {
                            "type": "string",
                            "description": "새 제목",
                        },
                        "content": {
                            "type": "string",
                            "description": "새 내용 (HTML 형식)",
                        },
                        "version_comment": {
                            "type": "string",
                            "description": "버전 코멘트 (선택)",
                        },
                    },
                    "required": ["page_id", "title", "content"],
                },
            ),
            Tool(
                name="wiki_delete_page",
                description="Confluence 페이지를 삭제합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_id": {
                            "type": "string",
                            "description": "삭제할 페이지 ID",
                        }
                    },
                    "required": ["page_id"],
                },
            ),
            Tool(
                name="wiki_search",
                description="Confluence에서 페이지를 검색합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "검색어 또는 CQL 쿼리",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "최대 결과 수 (기본: 10)",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="wiki_get_spaces",
                description="Confluence 스페이스 목록을 조회합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "최대 결과 수 (기본: 25)",
                            "default": 25,
                        }
                    },
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """도구 호출을 처리한다."""
        # [fastmcp 전환] name 분기 + arguments dict 수동 파싱 대신
        # 함수 시그니처 기반 인자 매핑/검증으로 단순화 가능.
        try:
            # [Pydantic] 도구 입력(arguments)을 여기서 먼저 검증하면 안전하다.
            # [Pydantic] 예: payload = CreatePageInput.model_validate(arguments)
            if name == "wiki_get_page":
                result = await _wiki_get_page(arguments["page_id"])
            elif name == "wiki_create_page":
                result = await _wiki_create_page(
                    arguments["space_key"],
                    arguments["title"],
                    arguments["content"],
                    arguments.get("parent_id"),
                )
            elif name == "wiki_update_page":
                result = await _wiki_update_page(
                    arguments["page_id"],
                    arguments["title"],
                    arguments["content"],
                    arguments.get("version_comment"),
                )
            elif name == "wiki_delete_page":
                result = await _wiki_delete_page(arguments["page_id"])
            elif name == "wiki_search":
                result = await _wiki_search(
                    arguments["query"],
                    arguments.get("limit", 10),
                )
            elif name == "wiki_get_spaces":
                result = await _wiki_get_spaces(arguments.get("limit", 25))
            else:
                raise ValueError(f"Unknown tool: {name}")

            return [TextContent(type="text", text=result)]
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}", exc_info=True)
            error_message = json.dumps(
                {
                    "error": str(e),
                    "tool": name,
                },
                ensure_ascii=False,
            )
            return [TextContent(type="text", text=error_message)]

    return server


# 비동기 래퍼 함수들 (기존 동기 api_client.py 사용)


async def _wiki_get_page(page_id: str) -> str:
    """페이지 조회 (비동기 래퍼)."""

    def _sync_get_page():
        client = get_wiki_client()
        page = client.get_page(page_id)
        data = page.to_dict()
        data["content"] = page.content
        return json.dumps(data, ensure_ascii=False, indent=2)

    return await asyncio.to_thread(_sync_get_page)


async def _wiki_create_page(
    space_key: str,
    title: str,
    content: str,
    parent_id: str | None = None,
) -> str:
    """페이지 생성 (비동기 래퍼)."""

    def _sync_create_page():
        client = get_wiki_client()
        page = client.create_page(
            space_key=space_key,
            title=title,
            content=content,
            parent_id=parent_id,
        )
        return json.dumps(
            {"message": "페이지가 생성되었습니다.", "page": page.to_dict()},
            ensure_ascii=False,
            indent=2,
        )

    return await asyncio.to_thread(_sync_create_page)


async def _wiki_update_page(
    page_id: str,
    title: str,
    content: str,
    version_comment: str | None = None,
) -> str:
    """페이지 업데이트 (비동기 래퍼)."""

    def _sync_update_page():
        client = get_wiki_client()
        page = client.update_page(
            page_id=page_id,
            title=title,
            content=content,
            version_comment=version_comment,
        )
        return json.dumps(
            {"message": "페이지가 업데이트되었습니다.", "page": page.to_dict()},
            ensure_ascii=False,
            indent=2,
        )

    return await asyncio.to_thread(_sync_update_page)


async def _wiki_delete_page(page_id: str) -> str:
    """페이지 삭제 (비동기 래퍼)."""

    def _sync_delete_page():
        client = get_wiki_client()
        client.delete_page(page_id)
        return json.dumps(
            {"message": f"페이지 {page_id}가 삭제되었습니다."},
            ensure_ascii=False,
        )

    return await asyncio.to_thread(_sync_delete_page)


async def _wiki_search(query: str, limit: int = 10) -> str:
    """페이지 검색 (비동기 래퍼)."""

    def _sync_search():
        client = get_wiki_client()
        pages = client.search(query, limit=limit)
        return json.dumps(
            {"count": len(pages), "results": [p.to_dict() for p in pages]},
            ensure_ascii=False,
            indent=2,
        )

    return await asyncio.to_thread(_sync_search)


async def _wiki_get_spaces(limit: int = 25) -> str:
    """스페이스 목록 조회 (비동기 래퍼)."""

    def _sync_get_spaces():
        client = get_wiki_client()
        spaces = client.get_spaces(limit=limit)
        return json.dumps(
            {"count": len(spaces), "spaces": [s.to_dict() for s in spaces]},
            ensure_ascii=False,
            indent=2,
        )

    return await asyncio.to_thread(_sync_get_spaces)
