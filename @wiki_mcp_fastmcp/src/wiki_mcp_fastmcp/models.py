"""Data models for Confluence API responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ★★★ [교육에 필요] Confluence 페이지 데이터 모델 ★★★
# 역할: Confluence API의 복잡한 중첩 JSON 응답을 깔끔한 Python 객체로 변환한다.
@dataclass
class WikiPage:
    id: str            # 페이지 고유 ID
    title: str         # 페이지 제목
    space_key: str     # 스페이스 키 (예: "DEV", "TEST")
    space_name: str    # 스페이스 이름
    version: int       # 페이지 버전 번호
    content: str       # 페이지 HTML 본문
    url: str           # 페이지 웹 URL

    # [교육에 필요] Confluence API 응답 JSON → WikiPage 객체 변환
    # 역할: 깊게 중첩된 JSON(body.storage.value 등)을 flat한 구조로 변환한다.
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
            content=body.get("value", ""),
            url=page_url,
        )

    # [교육에 필요] WikiPage 객체 → dict 변환 (JSON 직렬화용)
    # 역할: LLM에게 반환할 메타정보만 포함한다. content(본문)는 별도 추가해야 한다.
    def to_dict(self) -> dict[str, Any]:
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
    key: str
    name: str
    description: str
    url: str

    @classmethod
    def from_api_response(cls, data: dict[str, Any], base_url: str) -> "WikiSpace":
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
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "url": self.url,
        }
