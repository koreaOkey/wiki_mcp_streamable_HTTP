"""Streamable HTTP ASGI 애플리케이션."""

import logging
from contextlib import asynccontextmanager

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
# [fastmcp 전환] 이 파일(app.py) 자체가 불필요해질 수 있음.
# FastMCP가 HTTP/streamable 실행을 직접 제공하면 별도 ASGI 래핑 제거 가능.

from .server import create_mcp_server

logger = logging.getLogger("wiki-mcp.app")


def create_app():
    """ASGI 앱을 생성한다."""
    # [fastmcp 전환] create_app() + uvicorn.run(...factory=True) 경로 대신
    # FastMCP 인스턴스의 run(...) 한 단계로 실행 가능.
    mcp_server = create_mcp_server()
    session_manager = StreamableHTTPSessionManager(mcp_server)

    @asynccontextmanager
    async def lifespan(app: Starlette):
        async with session_manager.run():
            yield

    async def mcp_asgi(scope, receive, send):
        """MCP Streamable HTTP 요청을 처리한다."""
        if scope.get("type") == "http":
            headers = list(scope.get("headers", []))
            headers = [(k, v) for (k, v) in headers if k.lower() != b"accept"]
            headers.append((b"accept", b"application/json, text/event-stream"))
            scope = {**scope, "headers": headers}
        await session_manager.handle_request(scope, receive, send)

    async def health_check(request):
        return JSONResponse({"status": "ok"})

    async def info(request):
        return JSONResponse(
            {
                "name": "Wiki MCP Server",
                "version": "0.2.0",
                "transport": "streamable-http",
                "endpoints": {
                    "mcp": "/mcp",
                    "health": "/health",
                    "info": "/info",
                },
            }
        )

    app = Starlette(
        debug=False,
        routes=[
            Route("/health", endpoint=health_check, methods=["GET"]),
            Route("/info", endpoint=info, methods=["GET"]),
            Mount("/mcp", app=mcp_asgi),
        ],
        lifespan=lifespan,
    )

    logger.info("Wiki MCP Server (Streamable HTTP) initialized")
    logger.info("MCP endpoint available at /mcp")

    return app
