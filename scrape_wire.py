#!/usr/bin/env python3
"""
White House Wire RSS Feed Generator (AGGREGATOR VERSION)
Scrapes https://www.whitehouse.gov/wire/ and creates an RSS feed
The Wire page aggregates external news articles about the White House
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import time

def setup_driver():
    """Configure Chrome WebDriver with headless options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def is_news_article(url, title):
    """
    Check if this is a real news article.
    Wire page links to EXTERNAL news sites (Fox, Breitbart, etc.)
    We want those, but NOT whitehouse.gov navigation links.
    """
    url_lower = url.lower()
    
    # Title must be substantial (real articles are descriptive)
    if len(title) < 30:
        return False
    
    # EXCLUDE whitehouse.gov navigation/section pages
    # (We want external news, not WH site navigation)
    if 'whitehouse.gov' in url_lower:
        # These are navigation links, not news articles
        navigation_patterns = [
            '/about/', '/administration/', '/issues/', '/priorities/',
            '/presidential-actions/', '/briefings-statements/', '/fact-sheets/',
            '/contact', '/visit', '/apply', '/privacy', '/terms',
            '/ceq/', '/omb/', '/ostp/', '/cea/', '/ondcp/', '/oncd/',
            '/show/', '/gallery/', '/video/', '/livestream/', '/videos/',
            '/wire/', 'javascript:', '/news/#', '/articles/#',
            '/mediabias/', '/jfk-files/', '/rfk-files/', '/j6/',
            '/criminals/', '/saveamerica/', '/investments/',
            '/lab-leak-true-origins-of-covid-19/', '/easter-egg-roll/'
        ]
        
        for pattern in navigation_patterns:
            if pattern in url_lower:
                return False
        
        # If it's a whitehouse.gov URL and not in the exclusion list,
        # it might be a real WH article, so keep it
    
    # Accept all external URLs (news aggregator links)
    # Examples: foxnews.com, breitbart.com, dailywire.com, etc.
    return True

def scrape_wire():
    """Scrape White House Wire and return articles"""
    driver = None
    try:
        print("🌐 Starting Wire scraper (External News Aggregator)...")
        driver = setup_driver()
        
        url = "https://www.whitehouse.gov/wire/"
        print(f"📰 Fetching: {url}")
        driver.get(url)
        
        # Wait for content to load
        print("⏳ Waiting for page to load...")
        time.sleep(5)
        
        # Get page source after JavaScript has loaded
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        articles = []
        seen_urls = set()
        seen_titles = set()
        
        print("🔍 Searching for news article links...")
        
        for link in soup.find_all('a', href=True):
            url = link['href']
            
            # Make absolute URL if relative
            if url.startswith('/'):
                url = f"https://www.whitehouse.gov{url}"
            
            # Skip if we've seen this URL
            if url in seen_urls:
                continue
            
            # Get title from link text
            title = link.get_text(strip=True)
            
            # Skip if no title
            if not title:
                continue
            
            # Skip if we've seen this exact title
            if title in seen_titles:
                continue
            
            # Check if this is a news article
            if not is_news_article(url, title):
                continue
            
            seen_urls.add(url)
            seen_titles.add(title)
            
            print(f"✅ Found: {title[:70]}...")
            
            articles.append({
                'title': title,
                'link': url,
                'date': datetime.now(timezone.utc)
            })
        
        print(f"\n📰 Found {len(articles)} news articles!")
        return articles
        
    except Exception as e:
        print(f"❌ Error scraping Wire: {e}")
        return []
    finally:
        if driver:
            driver.quit()

def generate_rss(articles, output_file='wire_feed.xml'):
    """Generate RSS feed from articles"""
    print(f"📝 Generating RSS feed...")
    
    fg = FeedGenerator()
    fg.title('White House Wire (Aggregated) - Unofficial')
    fg.link(href='https://www.whitehouse.gov/wire/', rel='alternate')
    fg.description('Unofficial RSS feed for White House Wire aggregated news')
    fg.language('en')
    
    # Add articles to feed (limit to 30 most recent)
    for article in articles[:30]:
        fe = fg.add_entry()
        fe.title(article['title'])
        fe.link(href=article['link'])
        fe.guid(article['link'], permalink=True)
        fe.pubDate(article['date'])
    
    # Write to file
    fg.rss_file(output_file, pretty=True)
    print(f"💾 Saved {len(articles[:30])} articles to {output_file}")

def main():
    print("=" * 60)
    print("White House Wire RSS Scraper (External News)")
    print("=" * 60)
    
    articles = scrape_wire()
    
    if articles:
        generate_rss(articles)
        print("\n✅ SUCCESS! Check wire_feed.xml")
    else:
        print("\n⚠️  No articles found")

if __name__ == "__main__":
    main()
