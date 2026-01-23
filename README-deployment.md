# mcp-wiki 다중 인스턴스 배포 가이드

이 가이드는 3개의 mcp-wiki 인스턴스를 서로 다른 IP 주소에 배포하는 방법을 설명합니다.

## 📋 배포 구성

| 인스턴스 | MCP 서버 IP | 포트 | Confluence 서버 |
|---------|------------|------|----------------|
| wiki-mcp-140 | 172.23.192.140 | 80 | 172.23.192.78:8090 |
| wiki-mcp-141 | 172.23.192.141 | 80 | 172.23.192.78:8090 |
| wiki-mcp-142 | 172.23.192.142 | 80 | 172.23.192.78:8090 |

## 🚀 빠른 시작

### 방법 1: PowerShell 스크립트 (권장)

```powershell
cd C:\Users\leeyo\programming\wiki_mcp\mcp-wiki
.\build-and-run.ps1
```

이 스크립트는 자동으로:
1. 3개의 Docker 이미지 빌드
2. 기존 컨테이너 정리
3. 3개의 컨테이너 실행
4. 상태 확인

### 방법 2: Docker Compose

```bash
cd C:\Users\leeyo\programming\wiki_mcp\mcp-wiki
docker-compose up -d
```

### 방법 3: 수동 실행

```bash
# 이미지 빌드
docker build -f "Dockerfile copy" -t wiki-mcp:140 .
docker build -f Dockerfile.141 -t wiki-mcp:141 .
docker build -f Dockerfile.142 -t wiki-mcp:142 .

# 컨테이너 실행
docker run -d --name wiki-mcp-140 --network host wiki-mcp:140
docker run -d --name wiki-mcp-141 --network host wiki-mcp:141
docker run -d --name wiki-mcp-142 --network host wiki-mcp:142
```

## 🔍 상태 확인

```powershell
# 컨테이너 상태
docker ps --filter "name=wiki-mcp"

# 로그 확인
docker logs wiki-mcp-140
docker logs wiki-mcp-141
docker logs wiki-mcp-142

# 로그 실시간 확인
docker logs -f wiki-mcp-140
```

## 🧪 연결 테스트

### PowerShell에서 테스트

```powershell
# 인스턴스 1 테스트
Invoke-WebRequest -Uri "http://172.23.192.140:80/sse" -UseBasicParsing

# 인스턴스 2 테스트
Invoke-WebRequest -Uri "http://172.23.192.141:80/sse" -UseBasicParsing

# 인스턴스 3 테스트
Invoke-WebRequest -Uri "http://172.23.192.142:80/sse" -UseBasicParsing
```

## 🛑 중지 및 제거

```powershell
# 모든 인스턴스 중지
docker stop wiki-mcp-140 wiki-mcp-141 wiki-mcp-142

# 모든 인스턴스 제거
docker rm wiki-mcp-140 wiki-mcp-141 wiki-mcp-142

# 이미지 제거 (선택)
docker rmi wiki-mcp:140 wiki-mcp:141 wiki-mcp:142
```

## 📝 Cursor MCP 설정

Cursor에서 사용하려면 `~/.cursor/mcp.json`에 다음 설정 추가:

```json
{
  "mcpServers": {
    "wiki-mcp-140": {
      "url": "http://172.23.192.140:80/sse"
    },
    "wiki-mcp-141": {
      "url": "http://172.23.192.141:80/sse"
    },
    "wiki-mcp-142": {
      "url": "http://172.23.192.142:80/sse"
    }
  }
}
```

## 🔧 환경 변수 수정

각 Dockerfile에서 다음 환경 변수를 수정할 수 있습니다:

- `MCP_HOST`: mcp-wiki가 바인딩할 IP 주소
- `MCP_PORT`: mcp-wiki 포트 (기본: 80)
- `CONFLUENCE_HOST`: Confluence 서버 IP
- `CONFLUENCE_PORT`: Confluence 포트
- `CONFLUENCE_PERSONAL_TOKEN`: Personal Access Token

## 🎯 트러블슈팅

### 포트가 이미 사용 중인 경우

```powershell
# 포트 80을 사용 중인 프로세스 확인
netstat -ano | findstr ":80"

# 해당 프로세스 종료 (PID 확인 후)
Stop-Process -Id <PID> -Force
```

### 컨테이너가 시작되지 않는 경우

```powershell
# 로그 확인
docker logs wiki-mcp-140

# 컨테이너 내부 진입
docker exec -it wiki-mcp-140 sh

# 환경 변수 확인
docker exec wiki-mcp-140 env | findstr MCP
docker exec wiki-mcp-140 env | findstr CONFLUENCE
```

### 네트워크 연결 문제

```powershell
# IP 주소가 시스템에 할당되어 있는지 확인
ipconfig

# Confluence 서버 연결 테스트
Test-NetConnection -ComputerName 172.23.192.78 -Port 8090
```

## 📊 모니터링

```powershell
# 리소스 사용량 확인
docker stats wiki-mcp-140 wiki-mcp-141 wiki-mcp-142

# 컨테이너 정보
docker inspect wiki-mcp-140
```

## 🔄 업데이트

코드를 수정한 후:

```powershell
# 1. 이미지 재빌드
docker build -f "Dockerfile copy" -t wiki-mcp:140 .
docker build -f Dockerfile.141 -t wiki-mcp:141 .
docker build -f Dockerfile.142 -t wiki-mcp:142 .

# 2. 컨테이너 재시작
docker stop wiki-mcp-140 wiki-mcp-141 wiki-mcp-142
docker rm wiki-mcp-140 wiki-mcp-141 wiki-mcp-142

# 3. 다시 실행
.\build-and-run.ps1
```
