"""Wiki MCP Server 정의."""

import json
import logging

from fastmcp import FastMCP

from .client import WikiClient, get_wiki_client

logger = logging.getLogger("wiki-mcp.server")

# MCP 서버 생성
wiki_mcp = FastMCP(
    name="wiki-mcp",
    instructions="Confluence 위키 페이지를 관리하는 MCP 서버입니다.",
)


@wiki_mcp.tool()
def wiki_get_page(page_id: str) -> str:
    """
    Confluence 페이지를 조회합니다.
    
    Args:
        page_id: 페이지 ID
        
    Returns:
        페이지 정보 (JSON)
    """
    client = get_wiki_client()
    page = client.get_page(page_id)
    return json.dumps(page.to_dict(), ensure_ascii=False, indent=2)


@wiki_mcp.tool()
def wiki_create_page(
    space_key: str,
    title: str,
    content: str,
    parent_id: str | None = None,
) -> str:
    """
    새 Confluence 페이지를 생성합니다.
    
    Args:
        space_key: 스페이스 키 (예: DEV, TEST)
        title: 페이지 제목
        content: 페이지 내용 (HTML 형식)
        parent_id: 부모 페이지 ID (선택)
        
    Returns:
        생성된 페이지 정보 (JSON)
    """
    client = get_wiki_client()
    page = client.create_page(
        space_key=space_key,
        title=title,
        content=content,
        parent_id=parent_id,
    )
    return json.dumps(
        {"message": "페이지가 생성되었습니다", "page": page.to_dict()},
        ensure_ascii=False,
        indent=2,
    )


@wiki_mcp.tool()
def wiki_update_page(
    page_id: str,
    title: str,
    content: str,
    version_comment: str | None = None,
) -> str:
    """
    Confluence 페이지를 업데이트합니다.
    
    Args:
        page_id: 페이지 ID
        title: 새 제목
        content: 새 내용 (HTML 형식)
        version_comment: 버전 코멘트 (선택)
        
    Returns:
        업데이트된 페이지 정보 (JSON)
    """
    client = get_wiki_client()
    page = client.update_page(
        page_id=page_id,
        title=title,
        content=content,
        version_comment=version_comment,
    )
    return json.dumps(
        {"message": "페이지가 업데이트되었습니다", "page": page.to_dict()},
        ensure_ascii=False,
        indent=2,
    )


@wiki_mcp.tool()
def wiki_delete_page(page_id: str) -> str:
    """
    Confluence 페이지를 삭제합니다.
    
    Args:
        page_id: 삭제할 페이지 ID
        
    Returns:
        삭제 결과 메시지
    """
    client = get_wiki_client()
    client.delete_page(page_id)
    return json.dumps(
        {"message": f"페이지 {page_id}가 삭제되었습니다"},
        ensure_ascii=False,
    )


@wiki_mcp.tool()
def wiki_search(query: str, limit: int = 10) -> str:
    """
    Confluence에서 페이지를 검색합니다.
    
    Args:
        query: 검색어 또는 CQL 쿼리
        limit: 최대 결과 수 (기본: 10)
        
    Returns:
        검색 결과 목록 (JSON)
    """
    client = get_wiki_client()
    pages = client.search(query, limit=limit)
    return json.dumps(
        {"count": len(pages), "results": [p.to_dict() for p in pages]},
        ensure_ascii=False,
        indent=2,
    )


@wiki_mcp.tool()
def wiki_get_spaces(limit: int = 25) -> str:
    """
    Confluence 스페이스 목록을 조회합니다.
    
    Args:
        limit: 최대 결과 수 (기본: 25)
        
    Returns:
        스페이스 목록 (JSON)
    """
    client = get_wiki_client()
    spaces = client.get_spaces(limit=limit)
    return json.dumps(
        {"count": len(spaces), "spaces": [s.to_dict() for s in spaces]},
        ensure_ascii=False,
        indent=2,
    )
