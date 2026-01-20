# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from wiki_mcp.client import WikiClient

client = WikiClient()

# Create summary page
title = "Iran Protests News Summary"
space_key = "~admin"  # lee's personal space

content = '''
<h1>Iran Protests News Summary</h1>
<p><strong>Original Article:</strong> Iranians in Korea call for Seoul's attention as turmoil continues</p>
<p><strong>Source:</strong> The Korea Times</p>
<hr />

<h2>Key Points</h2>
<ul>
    <li><strong>Situation:</strong> Nationwide anti-government protests in Iran since December 2025</li>
    <li><strong>Casualties:</strong> Government claims ~2,000, but reports suggest closer to 12,000</li>
    <li><strong>Internet:</strong> Iranian government has cut off digital networks to obscure crackdowns</li>
</ul>

<h2>Iranian Residents in Korea Appeal</h2>
<p>Three Iranian residents (Niusha, Sarah, Layla) living in Korea for 6-10 years are pleading for Korean support:</p>
<ul>
    <li>Urging Korean government to take diplomatic action like Canada, France, Germany</li>
    <li>Requesting Korea to cut economic and political ties with Iran's regime</li>
    <li>Comparing situation to Korea's own 1980 Gwangju pro-democracy uprising</li>
</ul>

<h2>Key Quotes</h2>
<blockquote>
    <p>"Korea is a country that won democracy through sacrifice. I sincerely hope it will neither remain silent nor stand by as a spectator." - Sarah</p>
</blockquote>
<blockquote>
    <p>"The youth of Iran are standing before guns, shouting for the same freedom that Koreans fought for decades ago." - Layla</p>
</blockquote>
<blockquote>
    <p>"We are educated, peaceful and brave - and right now, we are asking you to stand on the right side of history with us." - Sarah</p>
</blockquote>

<h2>Main Request</h2>
<p><strong>"Be our voice"</strong> - The most common plea from Iranians inside Iran to those abroad.</p>

<hr />
<p><em>Summary created: 2026-01-14</em></p>
<p><em>Original page ID: 98383 (lee_page)</em></p>
'''

print("Creating summary page...")
try:
    page = client.create_page(
        space_key=space_key,
        title=title,
        content=content
    )
    print(f"Success!")
    print(f"Title: {page.title}")
    print(f"ID: {page.id}")
    print(f"URL: {page.url}")
except Exception as e:
    print(f"Error: {e}")
