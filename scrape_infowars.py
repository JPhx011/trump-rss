#!/usr/bin/env python3
"""
InfoWars Breaking News RSS Feed Generator
Scrapes https://www.infowars.com/breaking-news and creates an RSS feed
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import time
import re

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

def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        # Try various date formats
        date_formats = [
            '%B %d, %Y',  # January 15, 2025
            '%b %d, %Y',  # Jan 15, 2025
            '%Y-%m-%d',   # 2025-01-15
            '%m/%d/%Y',   # 01/15/2025
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        
        # If no format matches, return current time
        return datetime.now(timezone.utc)
    except:
        return datetime.now(timezone.utc)

def scrape_infowars():
    """Scrape InfoWars breaking news and return articles"""
    driver = None
    try:
        print("🌐 Starting InfoWars scraper...")
        driver = setup_driver()
        
        url = "https://www.infowars.com/breaking-news"
        print(f"📰 Fetching: {url}")
        driver.get(url)
        
        # Wait for content to load
        print("⏳ Waiting for page to load...")
        time.sleep(5)  # Give it time to load
        
        # Get page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        articles = []
        
        # Find article containers - InfoWars uses various selectors
        # We'll try multiple patterns to catch articles
        article_selectors = [
            'article',
            '.post',
            '.article',
            '.news-item',
            '[class*="article"]',
            '[class*="post"]'
        ]
        
        found_articles = []
        for selector in article_selectors:
            found = soup.select(selector)
            if found:
                found_articles.extend(found)
        
        # Remove duplicates
        seen_urls = set()
        
        print(f"📊 Found {len(found_articles)} potential article containers")
        
        for article in found_articles[:50]:  # Limit to first 50 to avoid overwhelming
            try:
                # Try to find title
                title = None
                title_selectors = ['h2', 'h3', 'h1', '.title', '[class*="title"]', 'a']
                for sel in title_selectors:
                    title_elem = article.find(sel)
                    if title_elem and title_elem.get_text(strip=True):
                        title = title_elem.get_text(strip=True)
                        break
                
                if not title:
                    continue
                
                # Try to find link
                link = None
                link_elem = article.find('a', href=True)
                if link_elem:
                    link = link_elem['href']
                    # Make absolute URL if relative
                    if link.startswith('/'):
                        link = f"https://www.infowars.com{link}"
                    elif not link.startswith('http'):
                        continue
                
                if not link or link in seen_urls:
                    continue
                
                seen_urls.add(link)
                
                # Try to find date
                date = None
                date_selectors = ['.date', '.published', 'time', '[class*="date"]', '[class*="time"]']
                for sel in date_selectors:
                    date_elem = article.find(sel)
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        if date_text:
                            date = parse_date(date_text)
                            break
                
                if not date:
                    # Try to extract date from datetime attribute
                    time_elem = article.find('time', datetime=True)
                    if time_elem:
                        try:
                            date = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                        except:
                            date = datetime.now(timezone.utc)
                    else:
                        date = datetime.now(timezone.utc)
                
                # Try to find description/excerpt
                description = None
                desc_selectors = ['.excerpt', '.description', 'p', '[class*="excerpt"]']
                for sel in desc_selectors:
                    desc_elem = article.find(sel)
                    if desc_elem:
                        desc_text = desc_elem.get_text(strip=True)
                        if len(desc_text) > 20:  # Make sure it's substantial
                            description = desc_text[:300]  # Limit length
                            break
                
                articles.append({
                    'title': title,
                    'link': link,
                    'date': date,
                    'description': description
                })
                
            except Exception as e:
                print(f"⚠️ Error parsing article: {e}")
                continue
        
        print(f"✅ Successfully parsed {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"❌ Error scraping InfoWars: {e}")
        return []
    finally:
        if driver:
            driver.quit()

def generate_rss(articles, output_file='infowars_feed.xml'):
    """Generate RSS feed from articles"""
    print(f"📝 Generating RSS feed...")
    
    fg = FeedGenerator()
    fg.title('InfoWars Breaking News (Unofficial)')
    fg.link(href='https://www.infowars.com/breaking-news', rel='alternate')
    fg.description('Unofficial RSS feed for InfoWars breaking news')
    fg.language('en')
    
    # Sort by date (newest first)
    articles.sort(key=lambda x: x['date'], reverse=True)
    
    # Add articles to feed (limit to 30 most recent)
    for article in articles[:30]:
        fe = fg.add_entry()
        fe.title(article['title'])
        fe.link(href=article['link'])
        fe.guid(article['link'], permalink=True)
        fe.pubDate(article['date'])
        
        if article.get('description'):
            fe.description(article['description'])
    
    # Write to file
    fg.rss_file(output_file, pretty=True)
    print(f"💾 Saved {len(articles[:30])} articles to {output_file}")

def main():
    print("=" * 60)
    print("InfoWars Breaking News RSS Scraper")
    print("=" * 60)
    
    articles = scrape_infowars()
    
    if articles:
        generate_rss(articles)
        print("\n✅ SUCCESS! Check infowars_feed.xml")
    else:
        print("\n❌ No articles found")

if __name__ == "__main__":
    main()
