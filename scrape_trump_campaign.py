import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import re

def parse_date(date_text):
    """Parse date from the article listing"""
    try:
        # Format: "January 17, 2025" or "December 22, 2024"
        date_text = date_text.strip()
        dt = datetime.strptime(date_text, '%B %d, %Y')
        # Make it timezone-aware
        return dt.replace(tzinfo=timezone.utc)
    except:
        # Fallback to current time if parsing fails
        return datetime.now(timezone.utc)

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
    
    print("🔍 Fetching Trump campaign news...")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    print(f"✅ Page loaded ({len(response.text)} bytes)")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    articles = []
    seen_links = set()
    
    # Find all links that point to /news/ articles
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Match news article URLs
        if '/news/' not in href or href == '/news':
            continue
            
        # Get full URL
        if href.startswith('http'):
            full_url = href
        else:
            full_url = f"https://www.donaldjtrump.com{href}"
        
        # Skip duplicates
        if full_url in seen_links:
            continue
        seen_links.add(full_url)
        
        # Find the parent container to get date and title
        parent = link.find_parent(['div', 'article', 'section'])
        if not parent:
            continue
        
        # Extract date (usually appears before the title)
        date_text = None
        date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', parent.get_text())
        if date_match:
            date_text = date_match.group(0)
        
        # Extract title - try multiple methods
        title = link.get_text(strip=True)
        
        # If link text isn't good, try heading tags
        if not title or len(title) < 10:
            heading = parent.find(['h1', 'h2', 'h3', 'h4'])
            if heading:
                title = heading.get_text(strip=True)
        
        # Clean up title - remove date if it got concatenated
        if title and date_text:
            title = title.replace(date_text, '').strip()
        
        # Remove "Recent News" tag if present
        title = title.replace('Recent News', '').strip()
        
        # Only add if we have a good title
        if title and len(title) > 10 and len(title) < 300:
            parsed_date = parse_date(date_text) if date_text else datetime.now(timezone.utc)
            
            articles.append({
                'title': title,
                'link': full_url,
                'published': parsed_date,
                'date_text': date_text or 'Recent'
            })
            print(f"✓ {date_text or 'Recent'}: {title[:60]}...")
    
    print(f"\n📰 Found {len(articles)} unique articles")
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
