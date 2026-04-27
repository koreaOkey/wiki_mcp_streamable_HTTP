"""MCP 서버 수동 테스트 스크립트.

사용법:
    python test_mcp.py <page_id>

예:
    python test_mcp.py 12345678
"""

import json
import sys

import requests

BASE_URL = "http://localhost:8002/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def rpc(method: str, params: dict, req_id: int, session_id: str | None = None) -> requests.Response | None:
    headers = {**HEADERS}
    if session_id:
        headers["mcp-session-id"] = session_id
    try:
        return requests.post(
            BASE_URL,
            headers=headers,
            json={"jsonrpc": "2.0", "id": req_id, "method": method, "params": params},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        print(f"❌ 서버 연결 실패: {BASE_URL}")
        print("   MCP 서버가 실행 중인지 확인하세요.")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ 요청 타임아웃: {BASE_URL}")
        return None


def parse_result(response: requests.Response) -> dict:
    """SSE 또는 JSON 응답을 파싱합니다."""
    content_type = response.headers.get("content-type", "")
    print(f"   [debug] content-type: {content_type}")
    print(f"   [debug] raw response:\n{response.text[:500]}")
    if "text/event-stream" in content_type:
        for line in response.text.splitlines():
            if not line.startswith("data:"):
                continue
            text = line[5:].strip()
            if not text:
                continue
            try:
                parsed = json.loads(text)
                if "result" in parsed or "error" in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue
        return {}
    return response.json()


def main():
    page_id = sys.argv[1] if len(sys.argv) > 1 else input("테스트할 page_id 입력: ").strip()

    # 1. Initialize
    print("▶ [1] MCP 세션 초기화...")
    r = rpc(
        method="initialize",
        params={
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"},
        },
        req_id=1,
    )
    session_id = r.headers.get("mcp-session-id")
    result = parse_result(r)
    print(f"   세션 ID: {session_id}")
    print(f"   서버 정보: {result.get('result', {}).get('serverInfo', {})}")

    # 2. initialized 알림
    requests.post(
        BASE_URL,
        headers={**HEADERS, "mcp-session-id": session_id},
        json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        timeout=5,
    )

    # 3. wiki_get_page 호출
    print(f"\n▶ [2] wiki_get_page 호출 (page_id={page_id})...")
    r = rpc(
        method="tools/call",
        params={"name": "wiki_get_page", "arguments": {"page_id": page_id}},
        req_id=2,
        session_id=session_id,
    )
    result = parse_result(r)

    tool_result = result.get("result", {})
    content = tool_result.get("content", [])
    if content:
        text = content[0].get("text", "")
        try:
            parsed = json.loads(text)
            print("\n✅ 결과:")
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print("\n✅ 결과:")
            print(text)
    else:
        print("\n❌ 응답 없음:")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
