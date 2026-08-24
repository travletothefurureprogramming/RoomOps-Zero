import feedparser
from urllib.parse import quote
import time

_news_cache = {"timestamp": 0, "data": []}
CACHE_DURATION = 900

def get_current_news(city:str | None = None):
    now = time.time()
    if _news_cache["data"] and (now - _news_cache["timestamp"] < CACHE_DURATION):
       return _news_cache["data"]

    query = "Ελλάδα" if city == None else city
    url = (
        "https://news.google.com/rss/search?"
        f"q={quote(query)}&hl=el&gl=GR&ceid=GR:el"
    )

    try:
            feed = feedparser.parse(url)
            articles = [entry.title for entry in feed.entries[:10]]
            
            _news_cache["timestamp"] = now
            _news_cache["data"] = articles
            return articles
    except Exception:
        return _news_cache["data"] if _news_cache["data"] else ["Αδυναμία λήψης ειδήσεων"]

if __name__ == '__main__':
  print(get_current_news())