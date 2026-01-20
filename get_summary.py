# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from wiki_mcp.client import WikiClient
import html
import re

client = WikiClient()

# Get the summary page we just created (ID: 98388)
print("=== Iran Protests News Summary (ID: 98388) ===\n")

try:
    page = client.get_page('98388', expand='body.storage,version')
    print(f"Title: {page.title}")
    print(f"ID: {page.id}")
    print(f"URL: {page.url}")
    print(f"Version: {page.version}")
    print()
    
    content = html.unescape(page.content or '')
    content = re.sub(r'<[^>]+>', '\n', content)
    content = re.sub(r'\n+', '\n', content).strip()
    
    print("Content:")
    print("-" * 50)
    print(content)
except Exception as e:
    print(f"Error: {e}")
