"""Wiki MCP Server 진입점 (Streamable HTTP)."""

import asyncio
import logging
import os
import sys

import click
import uvicorn
from mcp.server.stdio import stdio_server


@click.command()
@click.option("-v", "--verbose", is_flag=True, help="상세 로깅")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "streamable"]),
    default=lambda: os.environ.get("MCP_TRANSPORT", "streamable"),
    help="통신 방식 (환경변수: MCP_TRANSPORT)",
)
@click.option(
    "--port",
    type=int,
    default=lambda: int(os.environ.get("MCP_PORT", "8002")),
    help="서버 포트 (환경변수: MCP_PORT)",
)
@click.option(
    "--host",
    default=lambda: os.environ.get("MCP_HOST", "0.0.0.0"),
    help="서버 호스트 (환경변수: MCP_HOST)",
)
def main(verbose: bool, transport: str, port: int, host: str):
    """Wiki MCP Server를 시작합니다."""
    
    # 로깅 설정
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    
    logger = logging.getLogger("wiki-mcp")
    
    from .server import create_mcp_server
    
    if transport == "stdio":
        # STDIO 모드
        logger.info("Starting Wiki MCP Server in STDIO mode")
        asyncio.run(stdio_server(create_mcp_server()))
    else:
        # Streamable HTTP 모드
        logger.info(f"Starting Wiki MCP Server in Streamable HTTP mode on {host}:{port}")
        logger.info(f"MCP endpoint: http://{host}:{port}/mcp")

        uvicorn.run(
            "wiki_mcp.app:create_app",
            host=host,
            port=port,
            log_level="info" if not verbose else "debug",
            factory=True,
        )


if __name__ == "__main__":
    main()
