import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import re

def scrape_trump_news():
    url = "https://www.donaldjtrump.com/news"
    
    # Fake browser headers to bypass basic bot detection
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    print("🔍 Fetching page...")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    print(f"✅ Page loaded ({len(response.text)} bytes)")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links that point to /news/ pages
    articles = []
    seen_links = set()
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Match news article URLs
        if '/news/' in href and href != '/news':
            # Get full URL
            if href.startswith('http'):
                full_url = href
            else:
                full_url = f"https://www.donaldjtrump.com{href}"
            
            # Skip duplicates
            if full_url in seen_links:
                continue
            seen_links.add(full_url)
            
            # Extract title from link text or nearby elements
            title = link.get_text(strip=True)
            
            # Try to get title from nearby h2/h3 if link text is empty
            if not title or len(title) < 10:
                parent = link.find_parent(['div', 'article', 'section'])
                if parent:
                    heading = parent.find(['h1', 'h2', 'h3', 'h4'])
                    if heading:
                        title = heading.get_text(strip=True)
            
            if title and len(title) > 10:
                articles.append({
                    'title': title,
                    'link': full_url,
                    'published': datetime.now(timezone.utc)  # We'll improve date parsing later
                })
    
    print(f"📰 Found {len(articles)} unique articles")
    return articles[:30]  # Return top 30

def generate_rss(articles, filename='trump_feed.xml'):
    fg = FeedGenerator()
    fg.title('Donald J. Trump News (Unofficial)')
    fg.link(href='https://www.donaldjtrump.com/news', rel='alternate')
    fg.description('Unofficial RSS feed for donaldjtrump.com/news')
    fg.language('en')
    
    for article in articles:
        fe = fg.add_entry()
        fe.title(article['title'])
        fe.link(href=article['link'])
        fe.published(article['published'])
        fe.guid(article['link'], permalink=True)
    
    # Save to file
    fg.rss_file(filename, pretty=True)
    print(f"💾 Saved {len(articles)} articles to {filename}")

if __name__ == '__main__':
    try:
        articles = scrape_trump_news()
        if articles:
            generate_rss(articles)
            print("\n✅ SUCCESS! Check trump_feed.xml")
        else:
            print("❌ No articles found. The site structure may have changed.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

