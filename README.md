# wiki-mcp

Confluence 위키 페이지를 관리하는 MCP (Model Context Protocol) 서버입니다.

## 🚀 기능

- ✅ 페이지 조회 (`wiki_get_page`)
- ✅ 페이지 생성 (`wiki_create_page`)
- ✅ 페이지 수정 (`wiki_update_page`)
- ✅ 페이지 삭제 (`wiki_delete_page`)
- ✅ 페이지 검색 (`wiki_search`)
- ✅ 스페이스 목록 조회 (`wiki_get_spaces`)

## 📋 요구사항

- Python 3.10+
- Docker (컨테이너 사용 시)
- Confluence Server/Data Center 또는 Confluence Cloud

## 🔧 환경 변수 설정

### **Confluence 연결 설정**

#### **방법 1: IP와 포트 분리 (권장)** 🌟

| 환경 변수 | 필수 | 기본값 | 설명 | 예시 |
|-----------|------|--------|------|------|
| `CONFLUENCE_HOST` | ✅ | `localhost` | Confluence 서버 IP/도메인 | `192.168.1.100` |
| `CONFLUENCE_PORT` | ❌ | `8090` | Confluence 서버 포트 | `8090` |
| `CONFLUENCE_PROTOCOL` | ❌ | `http` | 프로토콜 | `http` / `https` |

#### **방법 2: 전체 URL 입력**

| 환경 변수 | 필수 | 기본값 | 설명 | 예시 |
|-----------|------|--------|------|------|
| `CONFLUENCE_URL` | ⚠️ | - | Confluence 전체 URL | `http://192.168.1.100:8090` |

💡 **우선순위**: `CONFLUENCE_URL` > `CONFLUENCE_HOST` + `CONFLUENCE_PORT`

### **인증 설정**

| 환경 변수 | 필수 | 기본값 | 설명 | 예시 |
|-----------|------|--------|------|------|
| `CONFLUENCE_PERSONAL_TOKEN` | ✅ | - | Personal Access Token (Server/DC용) | `OTEzNjg...` |
| `CONFLUENCE_USERNAME` | ⚠️ | - | 사용자 이름 (Cloud용) | `user@company.com` |
| `CONFLUENCE_API_TOKEN` | ⚠️ | - | API 토큰 (Cloud용) | `ATATT3x...` |
| `CONFLUENCE_SSL_VERIFY` | ❌ | `true` | SSL 인증서 검증 | `true` / `false` |

**인증 방식:**
- Server/DC: `CONFLUENCE_PERSONAL_TOKEN` 필수
- Cloud: `CONFLUENCE_USERNAME` + `CONFLUENCE_API_TOKEN` 필수

### **MCP 서버 설정**

| 환경 변수 | 필수 | 기본값 | 설명 | 예시 |
|-----------|------|--------|------|------|
| `MCP_TRANSPORT` | ❌ | `sse` | 통신 방식 | `sse` / `stdio` |
| `MCP_HOST` | ❌ | `0.0.0.0` | 리스닝 IP (외부 접속 허용) | `0.0.0.0` / `192.168.1.200` |
| `MCP_PORT` | ❌ | `8002` | 서비스 포트 | `8002` / `8080` |

💡 **MCP_HOST 설정:**
- `0.0.0.0`: 모든 네트워크 인터페이스에서 접속 허용 (권장)
- `127.0.0.1`: localhost에서만 접속 허용
- `192.168.1.200`: 특정 IP에서만 리스닝 (보안 강화)

## 🐳 Docker 사용

### 1️⃣ 이미지 빌드

```bash
cd mcp-wiki
docker build -t wiki-mcp:latest .
```

### 2️⃣ 컨테이너 실행

#### **로컬 테스트 (localhost:8090)**

```bash
docker run -d \
  --name wiki-mcp-server \
  -p 8002:8002 \
  -e CONFLUENCE_PERSONAL_TOKEN="your-token-here" \
  wiki-mcp:latest
```

💡 **간단!** HOST와 PORT는 기본값(`localhost:8090`)이 사용됩니다.

#### **IP와 포트 분리 입력 (권장)** 🌟

```bash
docker run -d \
  --name wiki-mcp-server \
  -p 8002:8002 \
  -e CONFLUENCE_HOST="192.168.1.100" \
  -e CONFLUENCE_PORT="8090" \
  -e CONFLUENCE_PERSONAL_TOKEN="your-token-here" \
  wiki-mcp:latest
```

#### **전체 URL 입력**

```bash
docker run -d \
  --name wiki-mcp-server \
  -p 8002:8002 \
  -e CONFLUENCE_URL="http://192.168.1.100:8090" \
  -e CONFLUENCE_PERSONAL_TOKEN="your-token-here" \
  wiki-mcp:latest
```

#### **HTTPS 사용**

```bash
docker run -d \
  --name wiki-mcp-server \
  -p 8002:8002 \
  -e CONFLUENCE_PROTOCOL="https" \
  -e CONFLUENCE_HOST="wiki.company.com" \
  -e CONFLUENCE_PORT="443" \
  -e CONFLUENCE_PERSONAL_TOKEN="your-token-here" \
  wiki-mcp:latest
```

#### **환경 파일 사용 (.env)**

```bash
# .env 파일 생성
cat > .env << EOF
CONFLUENCE_HOST=192.168.1.100
CONFLUENCE_PORT=8090
CONFLUENCE_PROTOCOL=http
CONFLUENCE_PERSONAL_TOKEN=your-token-here
MCP_PORT=8002
EOF

# 실행
docker run -d \
  --name wiki-mcp-server \
  -p 8002:8002 \
  --env-file .env \
  wiki-mcp:latest
```

### 3️⃣ 로그 확인

```bash
docker logs -f wiki-mcp-server
```

### 4️⃣ 컨테이너 중지/제거

```bash
docker stop wiki-mcp-server
docker rm wiki-mcp-server
```

## 📦 폐쇄망 배포

### 1️⃣ 이미지 저장

```bash
docker save wiki-mcp:latest -o wiki-mcp-image.tar
```

### 2️⃣ 폐쇄망으로 파일 전송

- `wiki-mcp-image.tar` 파일을 폐쇄망 서버로 복사

### 3️⃣ 이미지 로드 & 실행

```bash
# 이미지 로드
docker load -i wiki-mcp-image.tar

# 폐쇄망 A 실행
docker run -d \
  --name wiki-mcp-server \
  -p 8002:8002 \
  -e CONFLUENCE_HOST="192.168.1.100" \
  -e CONFLUENCE_PORT="8090" \
  -e CONFLUENCE_PERSONAL_TOKEN="폐쇄망A-토큰" \
  wiki-mcp:latest

# 폐쇄망 B 실행 (IP만 다름)
docker run -d \
  --name wiki-mcp-server \
  -p 8002:8002 \
  -e CONFLUENCE_HOST="10.0.0.50" \
  -e CONFLUENCE_PORT="8090" \
  -e CONFLUENCE_PERSONAL_TOKEN="폐쇄망B-토큰" \
  wiki-mcp:latest
```

### 💡 **폐쇄망 배포 팁**

#### **일반적인 시나리오 (표준 포트)**

```bash
# 환경마다 IP만 변경
# 폐쇄망 A
-e CONFLUENCE_HOST="192.168.1.100"

# 폐쇄망 B
-e CONFLUENCE_HOST="10.20.30.40"

# 폐쇄망 C
-e CONFLUENCE_HOST="172.16.0.10"
```

💡 포트는 기본값(8090) 사용

#### **특수한 경우 (비표준 포트)**

```bash
# 포트가 다른 경우
-e CONFLUENCE_HOST="192.168.1.100"
-e CONFLUENCE_PORT="9090"
```

#### **변경이 필요한 항목**

| 항목 | 환경마다 다름 | 예시 |
|------|--------------|------|
| ✅ **CONFLUENCE_HOST** | IP 주소 | `192.168.1.100` |
| ✅ **CONFLUENCE_PERSONAL_TOKEN** | 토큰 (보안) | `OTEzNjg...` |
| ⚠️ **CONFLUENCE_PORT** | 비표준 포트인 경우만 | `9090` |

#### **변경하지 않아도 되는 항목**

| 항목 | 기본값 | 이유 |
|------|--------|------|
| ❌ **MCP_PORT** | `8002` | 표준 포트 |
| ❌ **MCP_HOST** | `0.0.0.0` | 표준 설정 |
| ❌ **CONFLUENCE_PORT** | `8090` | Confluence 기본 포트 |
| ❌ **CONFLUENCE_PROTOCOL** | `http` | 폐쇄망은 일반적으로 HTTP |

## 💻 로컬 개발

### 1️⃣ 의존성 설치

```bash
# uv 설치 (Windows PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 프로젝트 의존성 설치
cd mcp-wiki
uv sync
```

### 2️⃣ 환경 변수 설정

```bash
# .env 파일 생성
cat > .env << EOF
CONFLUENCE_HOST=localhost
CONFLUENCE_PORT=8090
CONFLUENCE_PERSONAL_TOKEN=your-token-here
EOF
```

### 3️⃣ 실행

```bash
# SSE 모드 (권장)
uv run wiki-mcp --transport sse --port 8002

# 또는 환경 변수 사용
export MCP_PORT=8002
uv run wiki-mcp
```

## 🔌 Cursor IDE 연동

### 1️⃣ `mcp.json` 설정

#### **로컬 환경 (wiki-mcp가 같은 PC에서 실행)**

Cursor 설정 파일 (`C:\Users\<username>\.cursor\mcp.json`)에 추가:

```json
{
  "mcpServers": {
    "wiki-mcp": {
      "url": "http://localhost:8002/sse"
    }
  }
}
```

#### **원격 서버 환경 (wiki-mcp가 다른 서버에서 실행)**

```json
{
  "mcpServers": {
    "wiki-mcp": {
      "url": "http://192.168.1.200:8002/sse"
    }
  }
}
```

💡 `192.168.1.200`은 wiki-mcp 서버의 실제 IP 주소로 변경하세요.

### 2️⃣ Cursor 재시작

Cursor를 완전히 종료하고 다시 시작하면 자동으로 연결됩니다.

### 3️⃣ 사용 예시

```
wiki-mcp로 TES 스페이스의 페이지 목록 알려줘
```

```
wiki-mcp로 페이지 ID 98371 내용 가져와줘
```

## 🖥️ 원격 서버 배포

### **시나리오: wiki-mcp를 별도 서버에서 실행**

#### **1️⃣ 서버에서 실행**

```bash
# 서버 192.168.1.200에서 실행
docker run -d \
  --name wiki-mcp-server \
  -p 8002:8002 \
  -e MCP_HOST="0.0.0.0" \
  -e MCP_PORT="8002" \
  -e CONFLUENCE_HOST="192.168.1.100" \
  -e CONFLUENCE_PORT="8090" \
  -e CONFLUENCE_PERSONAL_TOKEN="토큰" \
  wiki-mcp:latest
```

**환경 변수 설명:**
- `MCP_HOST="0.0.0.0"`: 외부에서 접속 가능하게 설정
- `MCP_PORT="8002"`: 서비스 포트
- `CONFLUENCE_HOST`: Confluence 서버 IP
- `CONFLUENCE_PORT`: Confluence 서버 포트

#### **2️⃣ 방화벽 설정**

```bash
# Linux (firewalld)
sudo firewall-cmd --add-port=8002/tcp --permanent
sudo firewall-cmd --reload

# Windows
New-NetFirewallRule -DisplayName "wiki-mcp" -Direction Inbound -LocalPort 8002 -Protocol TCP -Action Allow
```

#### **3️⃣ 클라이언트 PC에서 연결**

`mcp.json`:
```json
{
  "mcpServers": {
    "wiki-mcp": {
      "url": "http://192.168.1.200:8002/sse"
    }
  }
}
```

### **네트워크 구성**

```
PC A (Cursor)
    │
    │ HTTP
    ▼
서버 B (192.168.1.200)
    wiki-mcp:8002
    │
    │ REST API
    ▼
서버 C (192.168.1.100)
    Confluence:8090
```

## 🔑 Personal Access Token 생성

### Confluence Server/Data Center

1. Confluence 로그인
2. 프로필 아이콘 → **Settings**
3. 좌측 메뉴 → **Personal Access Tokens**
4. **Create token** 클릭
5. 이름 입력 후 **Create**
6. 생성된 토큰 복사 (다시 볼 수 없음!)

## 🛠️ 문제 해결

### 1️⃣ "Confluence URL이 설정되지 않았습니다"

```bash
# 방법 1: HOST와 PORT 설정
export CONFLUENCE_HOST="192.168.1.100"
export CONFLUENCE_PORT="8090"

# 방법 2: 전체 URL 설정
export CONFLUENCE_URL="http://192.168.1.100:8090"
```

### 2️⃣ "인증 정보가 설정되지 않았습니다"

```bash
# Server/DC
export CONFLUENCE_PERSONAL_TOKEN="your-token"

# Cloud
export CONFLUENCE_USERNAME="user@email.com"
export CONFLUENCE_API_TOKEN="your-api-token"
```

### 3️⃣ SSL 인증서 오류

```bash
export CONFLUENCE_SSL_VERIFY=false
```

### 4️⃣ 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker logs wiki-mcp-server

# 환경 변수 확인
docker exec wiki-mcp-server env | grep CONFLUENCE
```

## 📚 환경 변수 우선순위

URL 결정 순서:
1. **직접 매개변수로 전달된 `url`** (최우선)
2. **환경 변수 `CONFLUENCE_URL`** (전체 URL)
3. **환경 변수 `CONFLUENCE_HOST` + `CONFLUENCE_PORT` + `CONFLUENCE_PROTOCOL`** (조합)

## 📄 라이선스

이 프로젝트는 개인 및 상업적 용도로 자유롭게 사용 가능합니다.
