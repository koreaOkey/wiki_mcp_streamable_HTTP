# wiki-mcp

Confluence 위키 페이지를 관리하는 MCP(Model Context Protocol) 서버입니다.

## 개요

wiki-mcp는 AI 언어 모델이 Confluence 위키와 상호작용할 수 있도록 해주는 MCP 서버입니다. 
페이지 조회, 생성, 수정, 삭제 및 검색 기능을 제공합니다.

## 프로젝트 구조

```
mcp-wiki/
├── pyproject.toml          # 프로젝트 설정 및 의존성
├── uv.lock                  # 의존성 잠금 파일
├── wikiREAD.md              # 프로젝트 설명서 (현재 파일)
├── wikiapiREAD.md           # Confluence API 분석 문서
├── diffREAD.md              # Cloud vs Server API 차이점
└── src/
    └── wiki_mcp/
        ├── __init__.py      # CLI 진입점
        ├── server.py        # MCP 서버 및 도구 정의
        ├── client.py        # Confluence REST API 클라이언트
        └── models.py        # 데이터 모델 (WikiPage, WikiSpace)
```

## 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| fastmcp | >=2.0.0 | MCP 서버 프레임워크 |
| requests | >=2.31.0 | HTTP 클라이언트 |
| pydantic | >=2.0.0 | 데이터 검증 |
| python-dotenv | >=1.0.0 | 환경변수 로드 |
| click | >=8.1.0 | CLI 인터페이스 |
| uvicorn | >=0.27.0 | ASGI 서버 |

## 설치

```bash
cd mcp-wiki
uv sync
```

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `CONFLUENCE_URL` | Confluence 서버 URL | http://localhost:8090 |
| `CONFLUENCE_USERNAME` | 사용자 이름 (Cloud용) | - |
| `CONFLUENCE_API_TOKEN` | API 토큰 (Cloud용) | - |
| `CONFLUENCE_PERSONAL_TOKEN` | Personal Access Token (Server/DC용) | - |

## 서버 실행

### STDIO 모드 (기본)
```bash
uv run wiki-mcp
```

### SSE 모드 (HTTP 서버)
```bash
uv run wiki-mcp --transport sse --port 8002 -v
```

### CLI 옵션
| 옵션 | 설명 |
|------|------|
| `-v, --verbose` | 상세 로깅 활성화 |
| `--transport` | 전송 방식 (stdio, sse) |
| `--port` | SSE 모드 포트 (기본: 8002) |
| `--host` | SSE 모드 호스트 (기본: 0.0.0.0) |

## MCP 도구 (Tools)

### 1. wiki_get_page
페이지 조회

```json
{
  "page_id": "98371"
}
```

**반환**: 페이지 정보 (ID, 제목, 내용, 버전, URL)

### 2. wiki_create_page
새 페이지 생성

```json
{
  "space_key": "TES",
  "title": "새 페이지 제목",
  "content": "<p>HTML 형식의 내용</p>",
  "parent_id": "98371"  // 선택: 부모 페이지 ID
}
```

**반환**: 생성된 페이지 정보

### 3. wiki_update_page
페이지 수정

```json
{
  "page_id": "98379",
  "title": "수정된 제목",
  "content": "<p>수정된 내용</p>",
  "version_comment": "오타 수정"  // 선택
}
```

**반환**: 수정된 페이지 정보

### 4. wiki_delete_page
페이지 삭제

```json
{
  "page_id": "98379"
}
```

**반환**: 삭제 확인 메시지

### 5. wiki_search
페이지 검색

```json
{
  "query": "title = \"Test_page_name\"",  // CQL 쿼리
  "limit": 10
}
```

또는 단순 텍스트 검색:
```json
{
  "query": "검색어",
  "limit": 10
}
```

**반환**: 검색 결과 목록

### 6. wiki_get_spaces
스페이스 목록 조회

```json
{
  "limit": 25
}
```

**반환**: 스페이스 목록 (키, 이름, 설명, URL)

## 데이터 모델

### WikiPage
```python
@dataclass
class WikiPage:
    id: str           # 페이지 ID
    title: str        # 페이지 제목
    space_key: str    # 스페이스 키
    space_name: str   # 스페이스 이름
    version: int      # 버전 번호
    content: str      # 페이지 내용 (HTML)
    url: str          # 페이지 URL
```

### WikiSpace
```python
@dataclass
class WikiSpace:
    key: str          # 스페이스 키 (예: TES, DEV)
    name: str         # 스페이스 이름
    description: str  # 스페이스 설명
    url: str          # 스페이스 URL
```

## 인증 방식

### Confluence Server/Data Center
Personal Access Token (PAT) 사용:
```
Authorization: Bearer <PAT>
```

PAT 발급 방법:
1. Confluence → 우측 상단 프로필 → Settings
2. Personal Access Tokens → Create token
3. 토큰 이름 입력 후 생성
4. 생성된 토큰 복사 (한 번만 표시됨)

### Confluence Cloud
API Token + Basic Auth 사용:
```
Authorization: Basic base64(email:api_token)
```

## Cursor MCP 연동

### 방법 1: STDIO 모드 (권장)
```json
{
  "mcpServers": {
    "wiki-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\leeyo\\programming\\wiki_mcp\\mcp-wiki",
        "run",
        "wiki-mcp"
      ],
      "env": {
        "CONFLUENCE_URL": "http://localhost:8090",
        "CONFLUENCE_PERSONAL_TOKEN": "your-token-here"
      }
    }
  }
}
```

### 방법 2: SSE 모드
서버를 먼저 실행한 후:
```json
{
  "mcpServers": {
    "wiki-mcp": {
      "url": "http://localhost:8002/sse"
    }
  }
}
```

## 사용 예시

### Python 스크립트로 테스트
```python
import os
os.environ['CONFLUENCE_URL'] = 'http://localhost:8090'
os.environ['CONFLUENCE_PERSONAL_TOKEN'] = 'your-token'

from src.wiki_mcp.client import WikiClient

client = WikiClient()

# 검색
results = client.search('title = "Test_page_name"')
for page in results:
    print(f"Found: {page.title} (ID: {page.id})")

# 페이지 조회
page = client.get_page("98371")
print(f"Content: {page.content}")

# 페이지 생성
new_page = client.create_page(
    space_key="TES",
    title="새 페이지",
    content="<p>내용</p>",
    parent_id="98371"
)
print(f"Created: {new_page.url}")
```

## 아키텍처

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI 모델       │────▶│   wiki-mcp      │────▶│   Confluence    │
│   (Cursor)      │     │   (FastMCP)     │     │   REST API      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │   MCP Protocol        │   HTTP/REST           │
        │   (STDIO/SSE)         │   + Bearer Token      │
        ▼                       ▼                       ▼
   도구 호출 요청         WikiClient 처리          API 응답
```

## 관련 파일

- [wikiapiREAD.md](./wikiapiREAD.md) - Confluence REST API 분석
- [diffREAD.md](./diffREAD.md) - Cloud vs Server API 차이점
- [../README.md](../README.md) - 프로젝트 전체 개요

## 라이선스

MIT License
