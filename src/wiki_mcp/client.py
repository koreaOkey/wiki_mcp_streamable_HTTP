"""Confluence REST API 클라이언트."""

import logging
import os
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from .models import WikiPage, WikiSpace

logger = logging.getLogger("wiki-mcp.client")


class WikiClientError(Exception):
    """Wiki 클라이언트 오류."""
    pass


class WikiAuthenticationError(WikiClientError):
    """인증 오류."""
    pass


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
        """
        WikiClient 초기화.
        
        Args:
            url: Confluence URL (환경변수: CONFLUENCE_URL 또는 CONFLUENCE_HOST+PORT)
            username: 사용자 이름 (환경변수: CONFLUENCE_USERNAME)
            api_token: API 토큰 (환경변수: CONFLUENCE_API_TOKEN)
            personal_token: Personal Access Token (환경변수: CONFLUENCE_PERSONAL_TOKEN)
            ssl_verify: SSL 인증서 검증 여부 (환경변수: CONFLUENCE_SSL_VERIFY)
            
        Raises:
            WikiClientError: 필수 설정이 누락된 경우
        """
        # URL 구성: 우선순위 1) 직접 제공 2) CONFLUENCE_URL 3) HOST+PORT 조합
        if url:
            self.url = url
        elif os.environ.get("CONFLUENCE_URL"):
            self.url = os.environ.get("CONFLUENCE_URL")
        else:
            # HOST, PORT, PROTOCOL로 URL 조합
            host = os.environ.get("CONFLUENCE_HOST", "")
            port = os.environ.get("CONFLUENCE_PORT", "8090")
            protocol = os.environ.get("CONFLUENCE_PROTOCOL", "http")
            
            if host:
                self.url = f"{protocol}://{host}:{port}"
            else:
                self.url = ""
        
        # 인증 정보
        self.username = username or os.environ.get("CONFLUENCE_USERNAME", "")
        self.api_token = api_token or os.environ.get("CONFLUENCE_API_TOKEN", "")
        self.personal_token = personal_token or os.environ.get("CONFLUENCE_PERSONAL_TOKEN", "")
        
        # SSL 검증 옵션 처리 (환경 변수 지원)
        if ssl_verify is None:
            ssl_verify_env = os.environ.get("CONFLUENCE_SSL_VERIFY", "true").lower()
            self.ssl_verify = ssl_verify_env in ("true", "1", "yes")
        else:
            self.ssl_verify = ssl_verify
        
        # 필수 값 검증
        if not self.url:
            raise WikiClientError(
                "Confluence URL이 설정되지 않았습니다. 다음 중 하나를 설정하세요:\n"
                "1. 환경 변수 CONFLUENCE_URL (예: http://localhost:8090)\n"
                "2. 환경 변수 CONFLUENCE_HOST + CONFLUENCE_PORT (선택: CONFLUENCE_PROTOCOL)"
            )
        
        # 인증 정보 검증
        has_cloud_auth = self.username and self.api_token
        has_server_auth = self.personal_token
        
        if not (has_cloud_auth or has_server_auth):
            raise WikiClientError(
                "인증 정보가 설정되지 않았습니다. 다음 중 하나를 설정하세요:\n"
                "1. Cloud: CONFLUENCE_USERNAME + CONFLUENCE_API_TOKEN\n"
                "2. Server/DC: CONFLUENCE_PERSONAL_TOKEN"
            )
        
        # URL 정규화
        self.url = self.url.rstrip("/")
        
        # 세션 설정
        self.session = requests.Session()
        self.session.verify = self.ssl_verify
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        # 인증 설정
        if self.personal_token:
            # Server/Data Center - Bearer Token
            self.session.headers["Authorization"] = f"Bearer {self.personal_token}"
            logger.debug("Using Personal Access Token authentication")
        elif self.username and self.api_token:
            # Cloud - Basic Auth with API Token
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
        """
        API 요청 실행.
        
        Args:
            method: HTTP 메서드
            endpoint: API 엔드포인트 (예: /content)
            params: 쿼리 파라미터
            json_data: 요청 본문
            
        Returns:
            API 응답 (JSON)
            
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
            
            # 인증 오류 확인
            if response.status_code in (401, 403):
                raise WikiAuthenticationError(
                    f"Authentication failed ({response.status_code}). "
                    "Please check your credentials."
                )
            
            # 기타 오류 확인
            response.raise_for_status()
            
            # 204 No Content
            if response.status_code == 204:
                return None
            
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
        """
        페이지 조회.
        
        Args:
            page_id: 페이지 ID
            expand: 확장할 필드
            
        Returns:
            WikiPage 객체
        """
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
        """
        새 페이지 생성.
        
        Args:
            space_key: 스페이스 키
            title: 페이지 제목
            content: 페이지 내용 (HTML 또는 Storage format)
            parent_id: 부모 페이지 ID (선택)
            representation: 콘텐츠 형식 (storage, wiki)
            
        Returns:
            생성된 WikiPage 객체
        """
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
        """
        페이지 업데이트.
        
        Args:
            page_id: 페이지 ID
            title: 새 제목
            content: 새 내용
            version: 현재 버전 (None이면 자동으로 조회)
            version_comment: 버전 코멘트
            representation: 콘텐츠 형식
            
        Returns:
            업데이트된 WikiPage 객체
        """
        # 현재 버전 조회
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
        """
        페이지 삭제.
        
        Args:
            page_id: 페이지 ID
            
        Returns:
            성공 여부
        """
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
        """
        CQL로 콘텐츠 검색.
        
        Args:
            query: CQL 쿼리 또는 검색어
            limit: 결과 제한
            start: 시작 위치
            
        Returns:
            WikiPage 목록
        """
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
        """
        스페이스 목록 조회.
        
        Args:
            limit: 결과 제한
            start: 시작 위치
            
        Returns:
            WikiSpace 목록
        """
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
        """
        특정 스페이스 조회.
        
        Args:
            space_key: 스페이스 키
            
        Returns:
            WikiSpace 객체
        """
        response = self._request("GET", f"/space/{space_key}")
        return WikiSpace.from_api_response(response, self.url)


# 싱글톤 인스턴스를 위한 전역 변수
_client: WikiClient | None = None


def get_wiki_client() -> WikiClient:
    """WikiClient 싱글톤 인스턴스 반환."""
    global _client
    if _client is None:
        _client = WikiClient()
    return _client
