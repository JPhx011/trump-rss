from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import time

def create_rss_feed(articles):
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    
    title = ET.SubElement(channel, 'title')
    title.text = 'White House News (Official)'
    
    link = ET.SubElement(channel, 'link')
    link.text = 'https://www.whitehouse.gov/news/'
    
    description = ET.SubElement(channel, 'description')
    description.text = 'Official White House news and presidential actions'
    
    for article in articles:
        item = ET.SubElement(channel, 'item')
        
        item_title = ET.SubElement(item, 'title')
        item_title.text = article['title']
        
        item_link = ET.SubElement(item, 'link')
        item_link.text = article['url']
        
        item_desc = ET.SubElement(item, 'description')
        item_desc.text = article['title']
        
        item_date = ET.SubElement(item, 'pubDate')
        item_date.text = article['date']
    
    xml_string = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
    return xml_string

def scrape_whitehouse():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get('https://www.whitehouse.gov/news/')
        time.sleep(5)
        
        articles = []
        
        # NEW STRUCTURE: Find all post containers
        post_containers = driver.find_elements(By.CLASS_NAME, 'wp-block-whitehouse-post-template__content')
        
        print(f"Found {len(post_containers)} articles")
        
        for container in post_containers[:20]:
            try:
                # Find the title link inside each container
                title_div = container.find_element(By.CLASS_NAME, 'wp-block-post-title')
                link_elem = title_div.find_element(By.TAG_NAME, 'a')
                
                title = link_elem.text.strip()
                url = link_elem.get_attribute('href')
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
                    })
                    print(f"Found: {title[:60]}...")
                    
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue
        
        driver.quit()
        
        if articles:
            rss_content = create_rss_feed(articles)
            with open('whitehouse_feed.xml', 'w', encoding='utf-8') as f:
                f.write(rss_content)
            print(f"\n✅ Successfully created feed with {len(articles)} articles")
            return True
        else:
            print("❌ No articles found")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        driver.quit()
        return False

if __name__ == "__main__":
    scrape_whitehouse()
