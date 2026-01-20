"""Test page search."""
import os
import sys

# 환경변수 설정
os.environ['CONFLUENCE_URL'] = 'http://localhost:8090'
os.environ['CONFLUENCE_PERSONAL_TOKEN'] = 'YOUR_PERSONAL_TOKEN_HERE'

# stdout UTF-8 설정
sys.stdout.reconfigure(encoding='utf-8')

from src.wiki_mcp.client import WikiClient

client = WikiClient()

# 페이지 검색
print("=== Searching for 'Test_page_name' ===")
try:
    results = client.search('title = "Test_page_name"')
    print(f"Found: {len(results)} pages")
    
    for page in results:
        print(f"\n--- Page ---")
        print(f"ID: {page.id}")
        print(f"Title: {page.title}")
        print(f"Space: {page.space_key}")
        print(f"URL: {page.url}")
        if page.content:
            print(f"Content preview: {page.content[:300]}...")
except Exception as e:
    print(f"Error: {e}")
