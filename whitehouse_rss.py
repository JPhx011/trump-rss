from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import time

def scrape_whitehouse_news():
    url = "https://www.whitehouse.gov/news/"
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    print("🔍 Starting browser...")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"🔍 Loading {url}...")
        driver.get(url)
        time.sleep(5)
        
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        print(f"✅ Page loaded ({len(html)} bytes)")
        
        articles = []
        seen_links = set()
        
        # Look for WordPress post template containers
        for container in soup.find_all('div', class_=lambda x: x and 'post-template' in x):
            link = container.find('a', href=True)
            if not link:
                continue
            
            href = link['href']
            
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                full_url = f"https://www.whitehouse.gov{href}"
            else:
                continue
            
            if full_url in seen_links or full_url == url:
                continue
            seen_links.add(full_url)
            
            title = link.get_text(strip=True)
            if not title or len(title) < 10:
                heading = container.find(['h1', 'h2', 'h3', 'h4'])
                if heading:
                    title = heading.get_text(strip=True)
            
            if title and len(title) > 10 and len(title) < 300:
                articles.append({
                    'title': title,
                    'link': full_url,
                    'published': datetime.now(timezone.utc)
                })
        
        print(f"📰 Found {len(articles)} unique articles")
        return articles[:30]
        
    finally:
        driver.quit()
        print("🛑 Browser closed")

def generate_rss(articles, filename='whitehouse_feed.xml'):
    fg = FeedGenerator()
    fg.title('White House News (Official)')
    fg.link(href='https://www.whitehouse.gov/news/', rel='alternate')
    fg.description('Official White House news and presidential actions')
    fg.language('en')
    
    for article in articles:
        fe = fg.add_entry()
        fe.title(article['title'])
        fe.link(href=article['link'])
        fe.published(article['published'])
        fe.guid(article['link'], permalink=True)
    
    fg.rss_file(filename, pretty=True)
    print(f"💾 Saved {len(articles)} articles to {filename}")

if __name__ == '__main__':
    try:
        articles = scrape_whitehouse_news()
        if articles:
            generate_rss(articles)
            print("\n✅ SUCCESS! Check whitehouse_feed.xml")
        else:
            print("❌ No articles found.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

