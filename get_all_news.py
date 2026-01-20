# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from wiki_mcp.client import WikiClient
import html
import re

client = WikiClient()

print("=== All Pages (checking for news content) ===\n")

# Get all pages
results = client.search('type=page', limit=20)

news_pages = []
for page in results:
    full_page = client.get_page(page.id, expand='body.storage')
    content = (full_page.content or '').lower()
    title = page.title.lower()
    
    if 'news' in content or 'news' in title or 'summary' in title:
        news_pages.append(full_page)

print(f"Found {len(news_pages)} news-related page(s):\n")

for i, page in enumerate(news_pages, 1):
    print(f"=== Page {i}: {page.title} ===")
    print(f"ID: {page.id}")
    print(f"URL: {page.url}")
    print(f"Version: {page.version}")
    print()
    
    # Clean and show content
    content = html.unescape(page.content or '')
    content = re.sub(r'<[^>]+>', '\n', content)
    content = re.sub(r'\n+', '\n', content).strip()
    
    print("Content:")
    print("-" * 50)
    print(content[:1500] + "..." if len(content) > 1500 else content)
    print()
    print("=" * 60)
    print()
