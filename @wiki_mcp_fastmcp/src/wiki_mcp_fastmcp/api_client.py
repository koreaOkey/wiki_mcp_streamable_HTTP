"""Confluence REST API client."""

from __future__ import annotations

import logging
import os
import threading
from typing import Any

import requests

from .models import WikiPage, WikiSpace

logger = logging.getLogger("wiki-mcp-fastmcp.api_client")
_CLIENT_KEY_DEFAULT = "default"


class WikiClientError(Exception):
    """Wiki client error."""


class WikiAuthenticationError(WikiClientError):
    """Wiki authentication error."""


# ★★★ [교육에 필요] Confluence REST API 클라이언트 클래스 ★★★
# 역할: Confluence 서버와 통신하는 HTTP 클라이언트. 인증, 요청, 에러 처리를 담당한다.
class WikiClient:
    """Confluence REST API client."""

    def __init__(
        self,
        url: str | None = None,
        personal_token: str | None = None,
        ssl_verify: bool | None = None,
    ):
        # [교육에 필요] Confluence URL 결정
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
        self.personal_token = personal_token or os.environ.get(
            "CONFLUENCE_PERSONAL_TOKEN", ""
        )

        if ssl_verify is None:
            ssl_verify_env = os.environ.get("CONFLUENCE_SSL_VERIFY", "true").lower()
            self.ssl_verify = ssl_verify_env in ("true", "1", "yes")
        else:
            self.ssl_verify = ssl_verify

        if not self.url:
            raise WikiClientError(
                "Confluence URL is not configured. "
                "Set CONFLUENCE_URL or CONFLUENCE_HOST/CONFLUENCE_PORT."
            )

        if not self.personal_token:
            raise WikiClientError(
                "Confluence auth is not configured. "
                "Set CONFLUENCE_PERSONAL_TOKEN."
            )

        # [교육에 필요] requests.Session 설정
        # 역할: 연결을 재사용하고 인증 헤더를 공통 설정한다.
        self.url = self.url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = self.ssl_verify
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        if self.personal_token:
            self.session.headers["Authorization"] = f"Bearer {self.personal_token}"
            logger.debug("Using personal token authentication")

    @property
    def api_url(self) -> str:
        return f"{self.url}/rest/api"

    # [교육에 필요] HTTP 요청 공통 메서드
    # 역할: 모든 Confluence API 호출이 이 메서드를 거친다. 인증 실패/에러를 공통 처리한다.
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

    '''★★★ [교육에 필요] 페이지 조회 메서드 ★★★'''
    # 역할: Confluence REST API GET /rest/api/content/{page_id} 호출
    # expand 파라미터로 본문(body.storage), 버전(version), 스페이스(space) 정보를 한 번에 가져온다.
    def get_page(
        self,
        page_id: str,
        expand: str = "body.storage,version,space",
    ) -> WikiPage:
        response = self._request(
            "GET",
            f"/content/{page_id}",
            params={"expand": expand},
        )
        return WikiPage.from_api_response(response, self.url)

    def create_page(
        self,
        space_key: str,
        title: str,
        content: str,
        parent_id: str | None = None,
        representation: str = "storage",
    ) -> WikiPage:
        data: dict[str, Any] = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": content,
                    "representation": representation,
                }
            },
        }
        if parent_id:
            data["ancestors"] = [{"id": parent_id}]

        logger.info("Creating page '%s' in space '%s'", title, space_key)
        response = self._request("POST", "/content", json_data=data)
        return WikiPage.from_api_response(response, self.url)

    def update_page(
        self,
        page_id: str,
        title: str,
        content: str,
        version: int | None = None,
        version_comment: str | None = None,
        representation: str = "storage",
    ) -> WikiPage:
        if version is None:
            current_page = self.get_page(page_id, expand="version")
            version = current_page.version

        data: dict[str, Any] = {
            "type": "page",
            "title": title,
            "version": {"number": version + 1},
            "body": {
                "storage": {
                    "value": content,
                    "representation": representation,
                }
            },
        }
        if version_comment:
            data["version"]["message"] = version_comment

        logger.info("Updating page %s to version %s", page_id, version + 1)
        response = self._request("PUT", f"/content/{page_id}", json_data=data)
        return WikiPage.from_api_response(response, self.url)

    def delete_page(self, page_id: str) -> bool:
        logger.info("Deleting page %s", page_id)
        self._request("DELETE", f"/content/{page_id}")
        return True

    def search(
        self,
        query: str,
        limit: int = 10,
        start: int = 0,
    ) -> list[WikiPage]:
        if not any(op in query for op in ["=", "~", ">", "<", " AND ", " OR "]):
            query = f'text ~ "{query}"'

        response = self._request(
            "GET",
            "/search",
            params={
                "cql": query,
                "limit": limit,
                "start": start,
            },
        )

        results: list[WikiPage] = []
        for item in response.get("results", []):
            content = item.get("content", item)
            if content.get("type") in ("page", "blogpost"):
                results.append(WikiPage.from_api_response(content, self.url))
        return results

    def get_spaces(self, limit: int = 25, start: int = 0) -> list[WikiSpace]:
        response = self._request(
            "GET",
            "/space",
            params={"limit": limit, "start": start},
        )
        return [
            WikiSpace.from_api_response(space, self.url)
            for space in response.get("results", [])
        ]


# ── 클라이언트 캐싱 (팩토리 패턴) ──

_clients: dict[str, WikiClient] = {}      # 클라이언트 캐시
_client_tokens: dict[str, str] = {}       # 토큰 캐시
_clients_lock = threading.Lock()          # 스레드 안전 보장


# [교육에 필요] 클라이언트 팩토리 함수
# 역할: 동일한 인증 정보에 대해 WikiClient를 재사용한다. (매번 새로 만들지 않음)
#       threading.Lock으로 스레드 안전성을 보장한다.
def get_wiki_client(
    client_key: str | None = None,
    personal_token: str | None = None,
    allow_legacy_env_token: bool = True,
) -> WikiClient:
    resolved_key = (client_key or _CLIENT_KEY_DEFAULT).strip() or _CLIENT_KEY_DEFAULT
    resolved_token = (personal_token or "").strip()
    if not resolved_token and not allow_legacy_env_token:
        raise WikiClientError(
            "Request token is missing and legacy environment-token fallback is disabled."
        )

    with _clients_lock:
        existing_client = _clients.get(resolved_key)
        existing_token = _client_tokens.get(resolved_key, "")
        if existing_client is not None and existing_token == resolved_token:
            return existing_client

        if resolved_token:
            client = WikiClient(personal_token=resolved_token)
        else:
            client = WikiClient()

        _clients[resolved_key] = client
        _client_tokens[resolved_key] = resolved_token
        logger.info("Initialized WikiClient for client_key=%s", resolved_key)
        return client
