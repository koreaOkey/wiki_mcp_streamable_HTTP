# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from wiki_mcp.client import WikiClient

client = WikiClient()

title = "Iran News Summary 2026"
space_key = "~admin"

content = '''<h1>Iran Protests - News Summary</h1>
<p><em>Source: The Korea Times | Summarized: 2026-01-14</em></p>
<hr/>

<h2>Overview</h2>
<p>Nationwide anti-government protests have been ongoing in Iran since December 2025, with heavy crackdowns by the government.</p>

<h2>Key Facts</h2>
<table>
<tr><th>Item</th><th>Details</th></tr>
<tr><td>Start Date</td><td>December 2025</td></tr>
<tr><td>Casualties (Gov't claim)</td><td>~2,000</td></tr>
<tr><td>Casualties (Reports)</td><td>~12,000</td></tr>
<tr><td>Internet Status</td><td>Blocked by government</td></tr>
</table>

<h2>Iranian Residents in Korea Appeal</h2>
<p>Three Iranian residents living in Korea (6-10 years) urge Korean support:</p>
<ul>
<li><strong>Niusha:</strong> Calls out Korea's silence despite being a G7-level democracy</li>
<li><strong>Sarah:</strong> Reminds Korea won democracy through sacrifice</li>
<li><strong>Layla:</strong> Links to 1980 Gwangju uprising, asks Korea to be their voice</li>
</ul>

<h2>Their Requests</h2>
<ol>
<li>Korean government should take diplomatic action</li>
<li>Cut economic/political ties with Iran's regime</li>
<li>Remove Iranian Embassy from Korea</li>
</ol>

<h2>Key Message</h2>
<blockquote><p><strong>"Be our voice"</strong> - The most common plea from Iranians</p></blockquote>

<blockquote><p>"Iranians are not dangerous people. We are educated, peaceful and brave - and right now, we are asking you to stand on the right side of history with us." - Sarah</p></blockquote>

<hr/>
<p><em>Original article in: lee_page (ID: 98383)</em></p>
'''

print("Creating new summary page...")
try:
    page = client.create_page(
        space_key=space_key,
        title=title,
        content=content
    )
    print("Success!")
    print(f"Title: {page.title}")
    print(f"ID: {page.id}")
    print(f"URL: {page.url}")
    print(f"Space: {page.space_key}")
except Exception as e:
    print(f"Error: {e}")
