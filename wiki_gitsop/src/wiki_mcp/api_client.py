"""Confluence REST API 클라이언트."""

import logging
import os
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from .models import WikiPage, WikiSpace

logger = logging.getLogger("wiki-mcp.api_client")


class WikiClientError(Exception):
    """Wiki 클라이언트 오류."""


class WikiAuthenticationError(WikiClientError):
    """인증 오류."""


class WikiClient:
    """Confluence REST API 클라이언트."""

    def __init__(
        self,
        url: str | None = None,
        username: str | None = None,
        api_token: str | None = None,
        personal_token: str | None = None,
        ssl_verify: bool | None = None,
    ):
        """WikiClient를 초기화한다.

        Args:
            url: Confluence URL (환경변수: CONFLUENCE_URL 또는 CONFLUENCE_HOST+PORT)
            username: 사용자 이름 (환경변수: CONFLUENCE_USERNAME)
            api_token: API 토큰 (환경변수: CONFLUENCE_API_TOKEN)
            personal_token: Personal Access Token (환경변수: CONFLUENCE_PERSONAL_TOKEN)
            ssl_verify: SSL 인증서 검증 여부 (환경변수: CONFLUENCE_SSL_VERIFY)

        Raises:
            WikiClientError: 필수 설정이 누락된 경우
        """
        # URL 구성 우선순위: 1) 인자로 직접 전달 2) CONFLUENCE_URL 3) HOST+PORT 조합
        if url:
            self.url = url
        elif os.environ.get("CONFLUENCE_URL"):
            self.url = os.environ.get("CONFLUENCE_URL")
        else:
            host = os.environ.get("CONFLUENCE_HOST", "")
            port = os.environ.get("CONFLUENCE_PORT", "8090")
            protocol = os.environ.get("CONFLUENCE_PROTOCOL", "http")
            self.url = f"{protocol}://{host}:{port}" if host else ""

        self.username = username or os.environ.get("CONFLUENCE_USERNAME", "")
        self.api_token = api_token or os.environ.get("CONFLUENCE_API_TOKEN", "")
        self.personal_token = personal_token or os.environ.get("CONFLUENCE_PERSONAL_TOKEN", "")
        # [Pydantic] BaseSettings로 CONFLUENCE_* 값을 한 번에 로드/검증하면 안전하다.

        if ssl_verify is None:
            ssl_verify_env = os.environ.get("CONFLUENCE_SSL_VERIFY", "true").lower()
            self.ssl_verify = ssl_verify_env in ("true", "1", "yes")
        else:
            self.ssl_verify = ssl_verify

        if not self.url:
            raise WikiClientError(
                "Confluence URL이 설정되지 않았습니다. 다음 중 하나를 설정하세요:\n"
                "1. 환경 변수 CONFLUENCE_URL (예: http://localhost:8090)\n"
                "2. 환경 변수 CONFLUENCE_HOST + CONFLUENCE_PORT (선택: CONFLUENCE_PROTOCOL)"
            )

        has_cloud_auth = self.username and self.api_token
        has_server_auth = self.personal_token
        if not (has_cloud_auth or has_server_auth):
            raise WikiClientError(
                "인증 정보가 설정되지 않았습니다. 다음 중 하나를 설정하세요:\n"
                "1. Cloud: CONFLUENCE_USERNAME + CONFLUENCE_API_TOKEN\n"
                "2. Server/DC: CONFLUENCE_PERSONAL_TOKEN"
            )

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
            # Server/Data Center: Bearer Token
            self.session.headers["Authorization"] = f"Bearer {self.personal_token}"
            logger.debug("Using Personal Access Token authentication")
        elif self.username and self.api_token:
            # Cloud: Basic Auth + API Token
            self.session.auth = HTTPBasicAuth(self.username, self.api_token)
            logger.debug("Using Basic Auth with API Token")

    @property
    def api_url(self) -> str:
        """REST API 기본 URL."""
        return f"{self.url}/rest/api"

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json_data: dict | None = None,
    ) -> dict | list | None:
        """API 요청을 실행한다.

        Args:
            method: HTTP 메서드
            endpoint: API 엔드포인트 (예: /content)
            params: 쿼리 파라미터
            json_data: 요청 본문

        Returns:
            API 응답(JSON)

        Raises:
            WikiAuthenticationError: 인증 실패
            WikiClientError: 기타 API 오류
        """
        url = f"{self.api_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
            )

            if response.status_code in (401, 403):
                raise WikiAuthenticationError(
                    f"Authentication failed ({response.status_code}). "
                    "Please check your credentials."
                )

            response.raise_for_status()

            if response.status_code == 204:
                return None

            # [Pydantic] 외부 API 응답을 모델로 검증한 뒤 사용하면 안전하다.
            return response.json()

        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError):
                try:
                    error_detail = e.response.json()
                    message = error_detail.get("message", str(e))
                except Exception:
                    message = str(e)
                raise WikiClientError(f"API error: {message}") from e
            raise WikiClientError(f"Request failed: {e}") from e

    # ============ Content API ============

    def get_page(
        self,
        page_id: str,
        expand: str = "body.storage,version,space",
    ) -> WikiPage:
        """페이지를 조회한다."""
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
        """새 페이지를 생성한다."""
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

        logger.info(f"Creating page '{title}' in space '{space_key}'")
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
        """페이지를 업데이트한다."""
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

        logger.info(f"Updating page {page_id} to version {version + 1}")
        response = self._request("PUT", f"/content/{page_id}", json_data=data)
        return WikiPage.from_api_response(response, self.url)

    def delete_page(self, page_id: str) -> bool:
        """페이지를 삭제한다."""
        logger.info(f"Deleting page {page_id}")
        self._request("DELETE", f"/content/{page_id}")
        return True

    # ============ Search API ============

    def search(
        self,
        query: str,
        limit: int = 10,
        start: int = 0,
    ) -> list[WikiPage]:
        """CQL로 콘텐츠를 검색한다."""
        # 단순 검색어인 경우 CQL로 변환
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

        results = []
        for item in response.get("results", []):
            content = item.get("content", item)
            if content.get("type") in ("page", "blogpost"):
                results.append(WikiPage.from_api_response(content, self.url))

        return results

    # ============ Space API ============

    def get_spaces(self, limit: int = 25, start: int = 0) -> list[WikiSpace]:
        """스페이스 목록을 조회한다."""
        response = self._request(
            "GET",
            "/space",
            params={"limit": limit, "start": start},
        )

        return [
            WikiSpace.from_api_response(space, self.url)
            for space in response.get("results", [])
        ]

    def get_space(self, space_key: str) -> WikiSpace:
        """특정 스페이스를 조회한다."""
        response = self._request("GET", f"/space/{space_key}")
        return WikiSpace.from_api_response(response, self.url)


# 싱글톤 인스턴스를 위한 전역 변수
_client: WikiClient | None = None


def get_wiki_client() -> WikiClient:
    """WikiClient 싱글톤 인스턴스를 반환한다."""
    global _client
    if _client is None:
        _client = WikiClient()
    return _client
