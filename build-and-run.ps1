# ============================================
# 여러 mcp-wiki 인스턴스 빌드 및 실행 스크립트
# ============================================

Write-Host "=== mcp-wiki 다중 인스턴스 배포 ===" -ForegroundColor Cyan

$mcpDir = "C:\Users\leeyo\programming\wiki_mcp\mcp-wiki"

# 1. 이미지 빌드
Write-Host "`n[1/4] Docker 이미지 빌드 중..." -ForegroundColor Yellow

Push-Location $mcpDir

Write-Host "  - wiki-mcp:140 빌드 중..." -ForegroundColor Gray
docker build -f "Dockerfile copy" -t wiki-mcp:140 .

Write-Host "  - wiki-mcp:141 빌드 중..." -ForegroundColor Gray
docker build -f Dockerfile.141 -t wiki-mcp:141 .

Write-Host "  - wiki-mcp:142 빌드 중..." -ForegroundColor Gray
docker build -f Dockerfile.142 -t wiki-mcp:142 .

Pop-Location

Write-Host "이미지 빌드 완료!" -ForegroundColor Green

# 2. 기존 컨테이너 정리
Write-Host "`n[2/4] 기존 컨테이너 정리 중..." -ForegroundColor Yellow

@("wiki-mcp-140", "wiki-mcp-141", "wiki-mcp-142") | ForEach-Object {
    $exists = docker ps -a --filter "name=$_" --format "{{.Names}}"
    if ($exists) {
        Write-Host "  - $_ 중지 및 삭제..." -ForegroundColor Gray
        docker stop $_ 2>$null
        docker rm $_ 2>$null
    }
}

Write-Host "정리 완료!" -ForegroundColor Green

# 3. 컨테이너 실행
Write-Host "`n[3/4] 컨테이너 실행 중..." -ForegroundColor Yellow

# 인스턴스 1 (172.23.192.140)
Write-Host "  - wiki-mcp-140 (172.23.192.140) 시작..." -ForegroundColor Gray
docker run -d --name wiki-mcp-140 `
    --network host `
    -e MCP_HOST=172.23.192.140 `
    -e MCP_PORT=80 `
    -e CONFLUENCE_HOST=172.23.192.78 `
    -e CONFLUENCE_PORT=8090 `
    -e CONFLUENCE_PERSONAL_TOKEN="YOUR_TOKEN_HERE" `
    wiki-mcp:140

# 인스턴스 2 (172.23.192.141)
Write-Host "  - wiki-mcp-141 (172.23.192.141) 시작..." -ForegroundColor Gray
docker run -d --name wiki-mcp-141 `
    --network host `
    -e MCP_HOST=172.23.192.141 `
    -e MCP_PORT=80 `
    -e CONFLUENCE_HOST=172.23.192.78 `
    -e CONFLUENCE_PORT=8090 `
    -e CONFLUENCE_PERSONAL_TOKEN="YOUR_TOKEN_HERE" `
    wiki-mcp:141

# 인스턴스 3 (172.23.192.142)
Write-Host "  - wiki-mcp-142 (172.23.192.142) 시작..." -ForegroundColor Gray
docker run -d --name wiki-mcp-142 `
    --network host `
    -e MCP_HOST=172.23.192.142 `
    -e MCP_PORT=80 `
    -e CONFLUENCE_HOST=172.23.192.78 `
    -e CONFLUENCE_PORT=8090 `
    -e CONFLUENCE_PERSONAL_TOKEN="YOUR_TOKEN_HERE" `
    wiki-mcp:142

Write-Host "컨테이너 실행 완료!" -ForegroundColor Green

# 4. 상태 확인
Write-Host "`n[4/4] 컨테이너 상태 확인..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

docker ps --filter "name=wiki-mcp" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n=== 배포 완료 ===" -ForegroundColor Cyan
Write-Host "접속 URL:" -ForegroundColor White
Write-Host "  - http://172.23.192.140:80/sse" -ForegroundColor White
Write-Host "  - http://172.23.192.141:80/sse" -ForegroundColor White
Write-Host "  - http://172.23.192.142:80/sse" -ForegroundColor White

Write-Host "`n로그 확인:" -ForegroundColor Gray
Write-Host "  docker logs wiki-mcp-140" -ForegroundColor Gray
Write-Host "  docker logs wiki-mcp-141" -ForegroundColor Gray
Write-Host "  docker logs wiki-mcp-142" -ForegroundColor Gray
