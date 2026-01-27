# MCP Wiki - Streamable HTTP 전환 작업 정리

## 📊 현재 상태 분석

### 현재 아키텍처
- **MCP 라이브러리**: `fastmcp >= 2.0.0`
- **통신 방식**: SSE (Server-Sent Events) 또는 stdio
- **웹 서버**: uvicorn
- **HTTP 클라이언트**: requests
- **Python 버전**: 3.10+

### 현재 통신 흐름
```
Cursor IDE (Client)
    ↓ HTTP/SSE
MCP Server (fastmcp)
    ↓ REST API (requests)
Confluence Server
```

### 파일 구조
```
src/wiki_mcp/
├── __init__.py          # CLI 진입점 (transport 선택)
├── server.py            # FastMCP 서버 정의 (tools 등록)
├── client.py            # Confluence REST API 클라이언트
└── models.py            # 데이터 모델 (WikiPage, WikiSpace)
```

---

## 🔄 Streamable HTTP 전환 개요

### Streamable HTTP란?
- MCP 프로토콜의 표준 HTTP transport 방식
- 양방향 HTTP 통신 (요청/응답 모두 스트리밍 가능)
- SSE보다 더 표준적이고 유연한 통신 방식
- JSON-RPC over HTTP streams

### 전환 목표
1. SSE 기반 통신 → HTTP Streamable transport로 변경
2. fastmcp의 기본 제공 기능 활용 또는 수동 구현
3. 기존 Confluence API 연동 로직은 유지
4. 도커 배포 및 폐쇄망 환경 지원 유지

---

## 🛠️ 변경이 필요한 부분

### 1. 의존성 변경 (`pyproject.toml`)

#### 현재 의존성
```toml
dependencies = [
    "fastmcp>=2.0.0",
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "click>=8.1.0",
    "uvicorn>=0.27.0",
]
```

#### 변경 방안 (2가지 옵션)

**옵션 A: fastmcp 활용 (권장)**
- fastmcp가 이미 HTTP transport를 지원하는지 확인 필요
- 지원한다면 최소한의 코드 변경으로 가능

**옵션 B: mcp SDK 직접 사용**
```toml
dependencies = [
    "mcp>=0.9.0",              # MCP 공식 SDK
    "httpx>=0.25.0",           # 비동기 HTTP 클라이언트 (streamable 지원)
    "starlette>=0.27.0",       # ASGI 프레임워크
    "uvicorn>=0.27.0",         # ASGI 서버
    "requests>=2.31.0",        # Confluence API 호출용 (유지)
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "click>=8.1.0",
]
```

---

### 2. 서버 초기화 변경 (`__init__.py`)

#### 현재 코드 (42-45줄)
```python
if transport == "stdio":
    wiki_mcp.run(transport="stdio")
else:
    wiki_mcp.run(transport="sse", host=host, port=port)
```

#### 변경 방안

**옵션 A: fastmcp 활용**
```python
if transport == "stdio":
    wiki_mcp.run(transport="stdio")
elif transport == "streamable":
    wiki_mcp.run(transport="http_streamable", host=host, port=port)
else:
    wiki_mcp.run(transport="sse", host=host, port=port)
```

**옵션 B: mcp SDK 직접 사용**
```python
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
import asyncio

async def run_streamable_server():
    from .server import create_mcp_server
    server = create_mcp_server()
    
    # HTTP Streamable transport 설정
    async with httpx_sse.aconnect_sse(...) as transport:
        await server.run(transport)

if transport == "stdio":
    asyncio.run(stdio_server(create_mcp_server()))
elif transport == "streamable":
    asyncio.run(run_streamable_server())
else:
    # SSE 모드
    ...
```

---

### 3. 서버 정의 수정 (`server.py`)

#### 현재 구조
- `FastMCP` 객체 생성 (13-16줄)
- `@wiki_mcp.tool()` 데코레이터로 도구 등록
- 동기 함수 사용

#### 변경 필요 사항

**옵션 A: fastmcp 활용**
- 코드 변경 최소화 (transport 설정만 변경)

**옵션 B: mcp SDK 직접 사용**
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

# 서버 생성 함수
def create_mcp_server() -> Server:
    server = Server("wiki-mcp")
    
    # 도구 등록
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="wiki_get_page",
                description="Confluence 페이지를 조회합니다.",
                inputSchema={...}
            ),
            # ... 다른 도구들
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "wiki_get_page":
            # 기존 로직 활용
            result = wiki_get_page(**arguments)
            return [TextContent(type="text", text=result)]
        # ...
    
    return server
```

**비동기 처리 고려사항:**
- WikiClient는 현재 requests (동기) 사용
- 비동기 전환 옵션:
  1. `asyncio.to_thread()` 로 동기 함수 래핑
  2. requests → httpx로 교체하여 완전 비동기화

---

### 4. 클라이언트 코드 (`client.py`)

#### 현재 상태
- `requests.Session` 사용 (동기 HTTP)
- REST API 호출은 모두 동기 방식

#### 변경 옵션

**옵션 1: 동기 방식 유지 (간단)**
```python
# 변경 없음
# MCP 서버에서 asyncio.to_thread()로 래핑
```

**옵션 2: 비동기 전환 (권장)**
```python
import httpx

class WikiClient:
    def __init__(self, ...):
        self.client = httpx.AsyncClient(verify=self.ssl_verify)
        # ...
    
    async def _request(self, method, endpoint, ...):
        response = await self.client.request(...)
        # ...
    
    async def get_page(self, page_id: str) -> WikiPage:
        # 비동기 구현
        ...
```

---

### 5. 환경 변수 및 설정 변경

#### 현재 (README.md 참조)
```bash
MCP_TRANSPORT=sse  # 또는 stdio
MCP_HOST=0.0.0.0
MCP_PORT=8002
```

#### 변경 후
```bash
MCP_TRANSPORT=streamable  # 또는 stdio, sse (하위 호환)
MCP_HOST=0.0.0.0
MCP_PORT=8002
```

#### CLI 옵션 변경 (`__init__.py` 14줄)
```python
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable"]),  # streamable 추가
    default=lambda: os.environ.get("MCP_TRANSPORT", "streamable"),
    help="통신 방식 (환경변수: MCP_TRANSPORT)",
)
```

---

### 6. Docker 설정 (`Dockerfile`)

#### 검토 필요 사항
- 현재 Dockerfile 확인 필요
- 포트 노출 설정 유지 (8002)
- 환경 변수 기본값 변경

```dockerfile
# 기본 transport를 streamable로 변경
ENV MCP_TRANSPORT=streamable
```

---

### 7. 문서 업데이트 (`README.md`)

#### 변경 필요 섹션
1. **통신 방식 설명**: SSE → Streamable HTTP
2. **환경 변수 테이블**: MCP_TRANSPORT 기본값 변경
3. **Cursor IDE 연동**: URL 엔드포인트 변경
   ```json
   {
     "mcpServers": {
       "wiki-mcp": {
         "url": "http://localhost:8002/mcp"  // 엔드포인트 확인 필요
       }
     }
   }
   ```
4. **실행 예시**: streamable 모드 추가

---

## 📋 작업 단계 (권장 순서)

### Phase 1: 조사 및 설계
1. ✅ 현재 코드 분석 완료
2. ⬜ fastmcp의 HTTP streamable 지원 여부 확인
3. ⬜ MCP 프로토콜 스펙 확인 (HTTP transport)
4. ⬜ 구현 방식 결정 (옵션 A vs B)

### Phase 2: 핵심 변경
1. ⬜ `pyproject.toml` 의존성 업데이트
2. ⬜ `server.py` 서버 로직 변경
3. ⬜ `__init__.py` transport 초기화 변경
4. ⬜ 로컬 테스트 (localhost:8002)

### Phase 3: 비동기 전환 (선택)
1. ⬜ `client.py`를 httpx로 마이그레이션
2. ⬜ 모든 API 호출을 async/await로 변경
3. ⬜ 통합 테스트

### Phase 4: 배포 및 문서화
1. ⬜ Dockerfile 업데이트
2. ⬜ README.md 업데이트
3. ⬜ Docker 이미지 빌드 및 테스트
4. ⬜ Cursor IDE 연동 테스트

---

## ⚠️ 주의사항

### 1. 하위 호환성
- 기존 SSE 모드도 유지할 것 (옵션으로)
- 환경 변수 기본값만 streamable로 변경

### 2. 에러 처리
- Streamable HTTP는 연결 관리 방식이 다름
- 타임아웃 및 재연결 로직 검토 필요

### 3. 성능
- 비동기 전환 시 동시성 이점
- 하지만 코드 복잡도 증가

### 4. 테스트
- 단위 테스트 작성 필요
- Confluence 연결 mock 처리

---

## 🔍 추가 조사 필요 항목

1. **fastmcp HTTP streamable 지원 여부**
   - fastmcp 문서 확인
   - 지원한다면 가장 간단한 방법

2. **MCP SDK HTTP transport 구현 방법**
   - mcp 패키지의 server.http 모듈 확인
   - 예제 코드 참조

3. **Cursor IDE의 streamable HTTP 엔드포인트 형식**
   - `/sse` → `/mcp` 또는 다른 경로?
   - 프로토콜 핸드셰이크 방식

4. **비동기 전환 필요성**
   - 성능 요구사항에 따라 결정
   - 간단한 래핑으로 시작 가능

---

## 💡 권장 접근 방식

### 단계별 마이그레이션 (최소 리스크)

**Step 1: fastmcp 활용 (우선 시도)**
```bash
# fastmcp가 streamable을 지원한다면
wiki_mcp.run(transport="http", host=host, port=port)
```
→ 코드 변경 최소, 빠른 전환

**Step 2: mcp SDK 직접 사용 (필요시)**
- fastmcp가 지원하지 않으면 mcp SDK로 직접 구현
- 코드 구조 변경 필요하지만 완전한 제어 가능

**Step 3: 비동기 전환 (성능 개선 필요시)**
- requests → httpx
- 모든 함수를 async/await로 변경
- 성능 향상 기대

---

## 📚 참고 자료

- [MCP Specification - HTTP Transport](https://spec.modelcontextprotocol.io/specification/2024-11-05/transport/#http)
- [fastmcp Documentation](https://github.com/jlowin/fastmcp)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [httpx Documentation](https://www.python-httpx.org/)

---

## 📅 작성일
2026-01-27

## 📝 다음 액션
1. fastmcp의 streamable HTTP 지원 여부 확인
2. 구현 방식 결정 (옵션 A vs B)
3. 변경 작업 시작
