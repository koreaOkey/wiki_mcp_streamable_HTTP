# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from wiki_mcp.client import WikiClient
import html
import re

client = WikiClient()

# Search for news-related pages
print("=== Searching for news content ===")
results = client.search('type=page', limit=20)

news_page = None
for page in results:
    # lee_page contains the news article
    if 'lee_page' in page.title.lower():
        news_page = page
        break

if news_page:
    # Get full content
    full_page = client.get_page(news_page.id, expand='body.storage,version,space')
    
    print(f"Title: {full_page.title}")
    print(f"ID: {full_page.id}")
    print(f"URL: {full_page.url}")
    print(f"Version: {full_page.version}")
    print()
    print("=== Original Content (HTML) ===")
    print(full_page.content)
    print()
    print("=== Plain Text ===")
    content = html.unescape(full_page.content or '')
    content = re.sub(r'<[^>]+>', '\n', content)
    content = re.sub(r'\n+', '\n', content).strip()
    print(content)
else:
    print("News page not found")
