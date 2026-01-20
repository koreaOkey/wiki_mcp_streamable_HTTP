"""Wiki MCP Server 진입점."""

import logging
import os
import sys

import click


@click.command()
@click.option("-v", "--verbose", is_flag=True, help="상세 로깅")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default=lambda: os.environ.get("MCP_TRANSPORT", "sse"),
    help="통신 방식 (환경변수: MCP_TRANSPORT)",
)
@click.option(
    "--port",
    type=int,
    default=lambda: int(os.environ.get("MCP_PORT", "8002")),
    help="SSE 모드 포트 (환경변수: MCP_PORT)",
)
@click.option(
    "--host",
    default=lambda: os.environ.get("MCP_HOST", "0.0.0.0"),
    help="SSE 모드 호스트 (환경변수: MCP_HOST)",
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
    
    from .server import wiki_mcp
    
    if transport == "stdio":
        wiki_mcp.run(transport="stdio")
    else:
        wiki_mcp.run(transport="sse", host=host, port=port)


if __name__ == "__main__":
    main()
