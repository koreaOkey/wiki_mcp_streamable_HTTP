# ============================================
# 스냅샷에서 복원 및 실행
# ============================================

param(
    [Parameter(Mandatory=$false)]
    [string]$SnapshotZip
)

Write-Host "=== Docker Compose 스냅샷 복원 ===" -ForegroundColor Cyan

# zip 파일 찾기
if (-not $SnapshotZip) {
    $zipFiles = Get-ChildItem "C:\Users\leeyo\programming\wiki_mcp\wiki-mcp-compose-*.zip" | Sort-Object LastWriteTime -Descending
    if ($zipFiles.Count -eq 0) {
        Write-Host "스냅샷 파일을 찾을 수 없습니다!" -ForegroundColor Red
        exit 1
    }
    $SnapshotZip = $zipFiles[0].FullName
    Write-Host "최신 스냅샷 사용: $($zipFiles[0].Name)" -ForegroundColor Yellow
}

# 1. 압축 해제
Write-Host "`n[1/4] 압축 해제 중..." -ForegroundColor Yellow
$extractDir = [System.IO.Path]::GetFileNameWithoutExtension($SnapshotZip)
$extractPath = "C:\Users\leeyo\programming\wiki_mcp\$extractDir"

if (Test-Path $extractPath) {
    Remove-Item $extractPath -Recurse -Force
}

Expand-Archive -Path $SnapshotZip -DestinationPath $extractPath -Force
Write-Host "  ✓ 압축 해제 완료" -ForegroundColor Green

# 2. Docker 이미지 로드
Write-Host "`n[2/4] Docker 이미지 로드 중..." -ForegroundColor Yellow

Push-Location $extractPath

$tarFiles = Get-ChildItem "*.tar"
foreach ($tar in $tarFiles) {
    Write-Host "  - $($tar.Name) 로드 중..." -ForegroundColor Gray
    docker load -i $tar.FullName
}

Write-Host "  ✓ 이미지 로드 완료" -ForegroundColor Green

# 3. Compose 디렉토리로 이동
Write-Host "`n[3/4] Docker Compose 설정 확인 중..." -ForegroundColor Yellow

$composeDir = Get-ChildItem -Directory "*-compose" | Select-Object -First 1
if ($composeDir) {
    Push-Location $composeDir.FullName
    Write-Host "  ✓ Compose 디렉토리: $($composeDir.Name)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Compose 디렉토리를 찾을 수 없습니다!" -ForegroundColor Red
    Pop-Location
    exit 1
}

# 4. Docker Compose 실행
Write-Host "`n[4/4] 컨테이너 시작 중..." -ForegroundColor Yellow

docker-compose down 2>$null
docker-compose up -d

Write-Host "  ✓ 컨테이너 시작 완료" -ForegroundColor Green

# 5. 상태 확인
Write-Host "`n=== 배포 완료 ===" -ForegroundColor Cyan

Start-Sleep -Seconds 3
docker-compose ps

Write-Host "`n접속 URL:" -ForegroundColor White
Write-Host "  - http://172.23.192.140:80/sse" -ForegroundColor White
Write-Host "  - http://172.23.192.141:80/sse" -ForegroundColor White
Write-Host "  - http://172.23.192.142:80/sse" -ForegroundColor White

Pop-Location
Pop-Location
