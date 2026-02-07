import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import re

def scrape_wire():
    """Scrape White House Wire aggregation page"""
    print("🔍 Fetching Wire page...")
    
    url = "https://www.whitehouse.gov/wire/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    print(f"✅ Page loaded ({len(response.content)} bytes)")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    
    # Find all article links on the Wire page
    # The Wire page has links with headlines
    links = soup.find_all('a', href=True)
    
    seen_urls = set()
    
    for link in links:
        href = link.get('href', '')
        title = link.get_text(strip=True)
        
        # Skip empty titles, navigation links, and social media
        if not title or len(title) < 10:
            continue
        if any(skip in href.lower() for skip in ['facebook', 'twitter', 'instagram', 'youtube', '#', 'mailto:']):
            continue
            
        # Make sure it's a full URL
        if href.startswith('/'):
            href = 'https://www.whitehouse.gov' + href
        elif not href.startswith('http'):
            continue
            
        # Avoid duplicates
        if href in seen_urls:
            continue
        seen_urls.add(href)
        
        articles.append({
            'title': title,
            'link': href,
            'pubDate': datetime.now()
        })
        
        print(f"Found: {title[:60]}...")
    
    print(f"\n📰 Found {len(articles)} unique articles")
    
    # Create RSS feed
    fg = FeedGenerator()
    fg.title('White House Wire (Aggregated)')
    fg.link(href=url, rel='alternate')
    fg.description('Aggregated news from White House Wire - Pro-Trump news coverage')
    fg.language('en')
    
    # Add articles to feed (limit to 30 most recent)
    for article in articles[:30]:
        fe = fg.add_entry()
        fe.title(article['title'])
        fe.link(href=article['link'])
        fe.description(article['title'])
        fe.pubDate(article['pubDate'].replace(tzinfo=None).isoformat() + 'Z')
    
    # Save feed
    fg.rss_file('wire_feed.xml')
    print(f"💾 Saved {min(len(articles), 30)} articles to wire_feed.xml\n")
    print("✅ SUCCESS! Check wire_feed.xml")

if __name__ == '__main__':
    scrape_wire()
