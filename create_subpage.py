"""Create a subpage with Korean translation."""
import os
import sys

# 환경변수 설정
os.environ['CONFLUENCE_URL'] = 'http://localhost:8090'
os.environ['CONFLUENCE_PERSONAL_TOKEN'] = 'YOUR_PERSONAL_TOKEN_HERE'

# stdout UTF-8 설정
sys.stdout.reconfigure(encoding='utf-8')

from src.wiki_mcp.client import WikiClient

client = WikiClient()

# 한글 번역 내용
korean_content = """
<h1>코스피, 사상 첫 4,900포인트 돌파</h1>

<p><strong>서울, 1월 19일 (연합뉴스)</strong> -- 한국 주식시장이 월요일 또 다른 이정표를 세우며 
역사상 처음으로 4,900포인트를 넘어 마감했습니다.</p>

<h2>주요 내용</h2>
<ul>
    <li><strong>종가:</strong> 코스피 지수가 63.92포인트(1.32%) 상승한 4,904.66으로 마감</li>
    <li><strong>신기록:</strong> 전 거래일 기록한 4,840.74포인트의 종가 최고치를 경신</li>
    <li><strong>장중 최고:</strong> 장중 사상 최고치인 4,917.37포인트 기록</li>
</ul>

<h2>시장 동향</h2>
<p>트럼프 미국 대통령이 그린란드 인수 계획에 반대하는 8개 유럽 국가에 
10%의 추가 관세를 부과하겠다고 위협하면서 무역 긴장이 재점화되어 
지수는 처음에 하락 출발했습니다.</p>

<p>그러나 코스피는 곧 반전하여 장중 사상 최고치를 기록했습니다.</p>

<h2>상승세 지속</h2>
<table>
    <tr>
        <th>기간</th>
        <th>상승률</th>
    </tr>
    <tr>
        <td>12거래일 연속 상승</td>
        <td>지속적인 상승세</td>
    </tr>
    <tr>
        <td>작년 초 대비</td>
        <td>2배 이상 (2,398.94 → 4,904.66)</td>
    </tr>
    <tr>
        <td>올해 12거래일</td>
        <td>16% 이상 상승</td>
    </tr>
    <tr>
        <td>작년 한 해</td>
        <td>75% 이상 상승</td>
    </tr>
</table>

<p><em>* 이 페이지는 원본 영문 기사를 한글로 번역한 내용입니다.</em></p>
"""

# 하위 페이지 생성
parent_id = "98371"  # Test_page_name 페이지 ID
space_key = "TES"
title = "코스피 4900 돌파 (한글 번역)"

print(f"=== Creating subpage under page {parent_id} ===")
try:
    page = client.create_page(
        space_key=space_key,
        title=title,
        content=korean_content,
        parent_id=parent_id
    )
    print(f"✅ Page created successfully!")
    print(f"ID: {page.id}")
    print(f"Title: {page.title}")
    print(f"URL: {page.url}")
except Exception as e:
    print(f"❌ Error: {e}")
