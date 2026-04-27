# wiki_gitsop

GitLab CI/CD-ready Wiki MCP package in gitsop style.

## Included
- `.gitlab-ci.yml`: build -> push -> deploy pipeline
- `.gitsop/Dockerfile`: image build for `wiki-mcp`
- `.gitsop/deployment.yaml`: OpenShift deployment/service/route template
- `pyproject.toml`, `src/wiki_mcp/*`: Wiki MCP source code

## Required GitLab CI/CD variables
- `CONFLUENCE_PERSONAL_TOKEN` (Server/DC auth)
- One of:
  - `CONFLUENCE_URL`
  - `CONFLUENCE_HOST` (+ optional `CONFLUENCE_PORT`, `CONFLUENCE_PROTOCOL`)

## Optional variables
- `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` (Cloud auth)
- `CONFLUENCE_SSL_VERIFY` (default: `true`)
- `MCP_TRANSPORT` (default: `streamable`)
- `MCP_HOST` (default: `0.0.0.0`)
- `MCP_PORT` (default: `8002`)

## Runtime endpoints
- `/health`
- `/info`
- `/mcp`


구성 포인트

Docker 이미지 실행 엔트리: wiki-mcp (ENTRYPOINT ["wiki-mcp"])
OpenShift 배포 템플릿 포함(Deployment/Service/Route)
배포 시 ConfigMap/Secret를 CI에서 생성 후 Pod에 envFrom 주입
기본 서비스 포트 8002, 헬스체크 /health, MCP 경로 /mcp
GitLab 변수로 꼭 넣어야 하는 것

CONFLUENCE_PERSONAL_TOKEN
CONFLUENCE_URL 또는 CONFLUENCE_HOST (+선택 CONFLUENCE_PORT, CONFLUENCE_PROTOCOL)
검증 관련

이 환경에서 python/py 실행기가 없어 코드 컴파일 테스트는 수행하지 못했습니다. (CI 러너에서 검증 권장)