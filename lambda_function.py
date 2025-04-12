import os
import requests
import re
from pymongo import MongoClient
from datetime import datetime

def lambda_handler(event, context):
    API_KEY = os.environ["SEARCHAPI_KEY"]
    MONGO_URI = os.environ["MONGODB_URI"]

    trends_url = f"https://www.searchapi.io/api/v1/search?api_key={API_KEY}&engine=youtube_trends&gl=PL"
    trends_response = requests.get(trends_url)

    if trends_response.status_code != 200:
        print("Błąd podczas pobierania trendów:", trends_response.text)
        return

    trending_data = trends_response.json()
    videos = trending_data.get("trending", [])

    print(f"\nZnalaziono {len(videos)} trendujących filmów:\n")

    for i, video in enumerate(videos[:1], 1):
        video_id = video.get("id")
        title = video.get("title")

        detail_url = f"https://www.searchapi.io/api/v1/search?api_key={API_KEY}&engine=youtube_video&video_id={video_id}"
        detail_response = requests.get(detail_url)

        if detail_response.status_code != 200:
            print(f"{i}. Błąd przy pobieraniu szczegółów filmu: {title}")
            continue

        details = detail_response.json()
        keywords = details.get("video", {}).get("keywords", [])
        description = details.get("video", {}).get("description", "")
        hashtags = re.findall(r"#\w+", description)

        print(f"{i}.  {title}")
        print(f"    🔗 https://www.youtube.com/watch?v={video_id}")
        print(f"    🏷️ Hashtagi: {', '.join(hashtags) if hashtags else 'brak'}")
        print(f"    🧠 Słowa kluczowe: {', '.join(keywords) if keywords else 'brak'}\n")

        client = MongoClient(MONGO_URI)
        db = client["Hacknarok"]
        collection = db["Youtube"]

        collection.insert_one({
            "title": title,
            "video_id": video_id,
            "hashtags": hashtags,
            "keywords": keywords,
            "date": datetime.now()
        })
