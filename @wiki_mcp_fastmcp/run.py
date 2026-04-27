"""직접 실행 스크립트. pip install 없이 사용 가능."""
import sys
import os

# ★★★ [교육에 필요] 핵심 1: Python 경로에 src 디렉토리 추가 ★★★
# 역할: pip install 없이도 src/wiki_mcp_fastmcp를 import할 수 있게 한다.
#       이 한 줄이 없으면 "ModuleNotFoundError: No module named 'wiki_mcp_fastmcp'" 에러 발생
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "src"))

# ★★★ [교육에 필요] 핵심 2: --dev 환경변수를 import 전에 설정 ★★★
# 역할: server.py가 import될 때 AUTH_MODE를 읽으므로, import보다 먼저 설정해야 한다.
#       __init__.py에서는 click이 옵션을 파싱한 후에 설정하지만,
#       server.py 모듈 최상단의 _AUTH_MODE = os.environ.get("AUTH_MODE") 가
#       import 시점에 이미 실행되므로 타이밍이 중요하다.
if "--dev" in sys.argv:
    os.environ.setdefault("AUTH_MODE", "env")
    os.environ.setdefault("ALLOW_LEGACY_ENV_TOKEN", "true")

# ★★★ [교육에 필요] 핵심 3: 환경변수 로드 및 설정 확인 출력 ★★★
# 역할: .env 파일을 로드하고, Confluence 연결 정보가 올바른지 시작 전에 확인한다.
#       토큰이 없으면 서버가 시작되어도 API 호출 시 에러가 나므로 미리 알려준다.
from dotenv import load_dotenv
load_dotenv()
token = os.environ.get("CONFLUENCE_PERSONAL_TOKEN", "")
url = os.environ.get("CONFLUENCE_URL") or (
    os.environ.get("CONFLUENCE_PROTOCOL", "http") + "://" +
    os.environ.get("CONFLUENCE_HOST", "") + ":" +
    os.environ.get("CONFLUENCE_PORT", "8090")
)
print(f"[startup] CONFLUENCE URL : {url}")
print(f"[startup] TOKEN 설정 여부 : {'✅ 있음' if token else '❌ 없음 (.env 확인 필요)'}")

from wiki_mcp_fastmcp import main

if __name__ == "__main__":
    main()
