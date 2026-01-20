"""Confluence 데이터 모델."""

from dataclasses import dataclass
from typing import Any


@dataclass
class WikiPage:
    """Confluence 페이지 모델."""
    
    id: str
    title: str
    space_key: str
    space_name: str
    version: int
    content: str
    url: str
    
    @classmethod
    def from_api_response(cls, data: dict[str, Any], base_url: str) -> "WikiPage":
        """API 응답에서 WikiPage 생성."""
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
            content=body.get("value", ""),
            url=page_url,
        )
    
    def to_dict(self) -> dict[str, Any]:
        """딕셔너리로 변환."""
        return {
            "id": self.id,
            "title": self.title,
            "space_key": self.space_key,
            "space_name": self.space_name,
            "version": self.version,
            "url": self.url,
        }


@dataclass
class WikiSpace:
    """Confluence 스페이스 모델."""
    
    key: str
    name: str
    description: str
    url: str
    
    @classmethod
    def from_api_response(cls, data: dict[str, Any], base_url: str) -> "WikiSpace":
        """API 응답에서 WikiSpace 생성."""
        desc = data.get("description", {}).get("plain", {}).get("value", "")
        links = data.get("_links", {})
        webui = links.get("webui", "")
        
        return cls(
            key=data.get("key", ""),
            name=data.get("name", ""),
            description=desc,
            url=f"{base_url}{webui}" if webui else "",
        )
    
    def to_dict(self) -> dict[str, Any]:
        """딕셔너리로 변환."""
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "url": self.url,
        }
