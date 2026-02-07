# trump-rss

Automated RSS feed generator for Trump-related news sources, including official White House news, campaign news, and aggregated media coverage.

## 📰 Available Feeds

This project generates three RSS feeds that update automatically 4 times daily:

1. **Trump Campaign News** (`trump_feed.xml`)
   - Source: https://www.donaldjtrump.com/news
   - Campaign announcements, press releases, and statements

2. **White House News** (`whitehouse_feed.xml`)
   - Source: https://www.whitehouse.gov/news/
   - Official presidential actions, briefings, and statements

3. **White House Wire** (`wire_feed.xml`)
   - Source: https://www.whitehouse.gov/wire/
   - Aggregated news coverage and media mentions

## 🚀 How It Works

The project uses Python web scrapers that run automatically via GitHub Actions:
- **Runs 4x daily** at 2am, 8am, 2pm, and 8pm UTC
- **Auto-commits** updated feeds back to the repository
- **Error-resilient** - if one scraper fails, others continue

## 🛠️ Setup (Local Development)

### Prerequisites
- Python 3.11+
- Google Chrome (for Selenium-based scrapers)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/JPhx011/trump-rss.git
cd trump-rss
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run individual scrapers:
```bash
# Trump campaign news
python scrape_trump_campaign.py

# White House news
python scrape_whitehouse.py

# Wire aggregator
python scrape_wire.py
```

The scrapers will generate `.xml` files in the project directory.

## 📡 Using the Feeds

### Option 1: Subscribe via GitHub (Current)
You can subscribe to the feeds directly from this repository:
- Trump Campaign: `https://raw.githubusercontent.com/JPhx011/trump-rss/main/trump_feed.xml`
- White House: `https://raw.githubusercontent.com/JPhx011/trump-rss/main/whitehouse_feed.xml`
- Wire: `https://raw.githubusercontent.com/JPhx011/trump-rss/main/wire_feed.xml`

Just paste these URLs into your RSS reader!

### Option 2: GitHub Pages (Future)
Coming soon - cleaner URLs via GitHub Pages hosting.

## 🤖 Automation

The project uses GitHub Actions for automation. See `.github/workflows/update-feeds.yml` for details.

Manual trigger:
1. Go to the "Actions" tab on GitHub
2. Click "Update RSS Feed"
3. Click "Run workflow"

## 📝 Technical Details

- **Trump scraper**: Uses `requests` + BeautifulSoup for fast HTML parsing
- **White House scraper**: Uses Selenium for JavaScript-rendered content
- **Wire scraper**: Uses `requests` + BeautifulSoup
- **RSS generation**: Uses `feedgen` library

## 🤝 Contributing

This is a personal learning project, but suggestions and improvements are welcome!

## ⚠️ Disclaimer

This is an **unofficial** RSS feed project created for personal use and learning purposes. It is not affiliated with, endorsed by, or connected to Donald J. Trump, the Trump campaign, or the White House.

## 📄 License

MIT License - feel free to use and modify!

---

**Project started**: February 2025  
**Status**: ✅ Active and updating automatically
