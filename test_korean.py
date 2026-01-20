# -*- coding: utf-8 -*-
from wiki_mcp.client import WikiClient
client = WikiClient()

print("=== Korean Search Test ===")

# Test Korean search
queries = [
    'text ~ "?좊Ц湲곗궗"',
    'text ~ "?좊Ц"', 
    'text ~ "寃쎌같"',
    'text ~ "源蹂묎린"',
]

for q in queries:
    print(f"\nQuery: {q}")
    try:
        results = client.search(q, limit=5)
        if results:
            for p in results:
                print(f"   Found: {p.title}")
        else:
            print("   No results")
    except Exception as e:
        print(f"   Error: {e}")
