# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from wiki_mcp.client import WikiClient
import html
import re

client = WikiClient()

print("=== Searching for 'news' related pages ===\n")

# Search for news
results = client.search('text ~ "news"', limit=10)

if results:
    print(f"Found {len(results)} page(s):\n")
    
    for i, page in enumerate(results, 1):
        print(f"--- Page {i} ---")
        print(f"Title: {page.title}")
        print(f"ID: {page.id}")
        print(f"URL: {page.url}")
        
        # Get full content
        full_page = client.get_page(page.id, expand='body.storage,version')
        content = full_page.content or ''
        
        # Clean HTML
        content = html.unescape(content)
        content = re.sub(r'<[^>]+>', ' ', content)
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Show preview (first 500 chars)
        preview = content[:500] + "..." if len(content) > 500 else content
        print(f"Preview: {preview}")
        print()
else:
    print("No news-related pages found.")
