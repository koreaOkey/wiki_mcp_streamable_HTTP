"""CLI entrypoint for the FastMCP-based Wiki MCP server."""

from __future__ import annotations

import os

import click                          # [교육에 필요] CLI 옵션 파싱 라이브러리
from dotenv import load_dotenv        # [교육에 필요] .env 파일에서 환경변수 로드

from .server import create_mcp_server # [교육에 필요] MCP 서버 팩토리 함수 import

load_dotenv()                         # [교육에 필요] .env 파일의 환경변수를 os.environ에 로드


# [교육에 필요] @click.command()와 @click.option()은 CLI 옵션을 정의하는 데코레이터이다.
# 터미널에서 python run.py --dev --port 9000 처럼 입력하면,
# click이 옵션을 파싱해서 main() 함수의 파라미터로 넘겨준다.
# 각 옵션의 default는 환경변수 → 하드코딩 기본값 순으로 폴백한다.
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

    '''★★★ [교육에 필요] 핵심 2줄: 서버 생성 → 실행 ★★★'''
    # 역할: FastMCP 인스턴스를 만들고, streamable-http 방식으로 서버를 기동한다.
    # mcp = create_mcp_server()
    # mcp.run(
    #     transport="streamable-http",   # MCP 전송 방식 (streamable HTTP)
    #     host=host,                     # 바인딩 호스트 (기본: 0.0.0.0)
    #     port=port,                     # 바인딩 포트 (기본: 8002)
    #     path=path,                     # MCP 엔드포인트 경로 (기본: /mcp)
    #     log_level="debug" if verbose else "info",
    # )
    


if __name__ == "__main__":
    main()
