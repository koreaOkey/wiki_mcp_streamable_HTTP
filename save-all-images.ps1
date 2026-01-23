# ============================================
# Docker Compose 기반 전체 이미지 스냅샷 생성
# ============================================

Write-Host "=== Docker Compose 이미지 스냅샷 생성 ===" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputDir = "C:\Users\leeyo\programming\wiki_mcp"
$snapshotName = "wiki-mcp-compose-$timestamp"

# 1. 개별 이미지를 tar로 저장
Write-Host "`n[1/3] 개별 이미지 저장 중..." -ForegroundColor Yellow

Push-Location $outputDir

docker save wiki-mcp:140 -o "$snapshotName-140.tar"
Write-Host "  [OK] wiki-mcp:140 저장 완료" -ForegroundColor Green

docker save wiki-mcp:141 -o "$snapshotName-141.tar"
Write-Host "  [OK] wiki-mcp:141 저장 완료" -ForegroundColor Green

docker save wiki-mcp:142 -o "$snapshotName-142.tar"
Write-Host "  [OK] wiki-mcp:142 저장 완료" -ForegroundColor Green

# 2. Docker Compose 파일 복사
Write-Host "`n[2/3] Docker Compose 설정 저장 중..." -ForegroundColor Yellow

$composeDir = "$outputDir\$snapshotName-compose"
New-Item -ItemType Directory -Path $composeDir -Force | Out-Null

Copy-Item ".\mcp-wiki\docker-compose.yml" "$composeDir\"
Copy-Item ".\mcp-wiki\Dockerfile copy" "$composeDir\"
Copy-Item ".\mcp-wiki\Dockerfile.141" "$composeDir\"
Copy-Item ".\mcp-wiki\Dockerfile.142" "$composeDir\"

Write-Host "  [OK] Compose 설정 저장 완료" -ForegroundColor Green

# 3. 모든 것을 하나의 zip으로 압축
Write-Host "`n[3/3] 전체 패키지 압축 중..." -ForegroundColor Yellow

Compress-Archive -Path "$snapshotName-*.tar", $composeDir -DestinationPath "$snapshotName.zip" -Force

Write-Host "  [OK] 압축 완료" -ForegroundColor Green

# 4. 결과 출력
Write-Host "`n=== 스냅샷 생성 완료 ===" -ForegroundColor Cyan

$zipFile = Get-Item "$snapshotName.zip"
$zipSizeMB = [math]::Round($zipFile.Length / 1MB, 2)

Write-Host "`n생성된 파일:" -ForegroundColor White
Write-Host "  - $snapshotName-140.tar" -ForegroundColor Gray
Write-Host "  - $snapshotName-141.tar" -ForegroundColor Gray
Write-Host "  - $snapshotName-142.tar" -ForegroundColor Gray
Write-Host "  - $composeDir\" -ForegroundColor Gray
Write-Host "  - $snapshotName.zip (${zipSizeMB} MB)" -ForegroundColor Yellow

Write-Host "`n다음 단계:" -ForegroundColor Cyan
Write-Host "  1. zip 파일을 다른 서버로 복사" -ForegroundColor Gray
Write-Host "  2. 압축 해제" -ForegroundColor Gray
Write-Host "  3. tar 파일로 이미지 로드" -ForegroundColor Gray
Write-Host "  4. docker-compose up -d 실행" -ForegroundColor Gray

Pop-Location
