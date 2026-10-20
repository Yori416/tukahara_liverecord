import json
import xml.etree.ElementTree as ET
import re
import requests
import os

CHANNEL_ID = "UCriPI_vMh2Aven_czYRWxhw" # 塚原大地 官方頻道 ID
CHANNEL_HANDLE = "@TsukaharaDaichi_Y4T4"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
LIVE_URL = f"https://www.youtube.com/channel/{CHANNEL_ID}/live"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9"
}

def load_existing_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"streams": []}

def fetch_rss_videos():
    videos = []
    try:
        res = requests.get(RSS_URL, headers=HEADERS, timeout=10)
        root = ET.fromstring(res.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
        
        for entry in root.findall('atom:entry', ns):
            video_id = entry.find('yt:videoId', ns).text
            title = entry.find('atom:title', ns).text
            published_full = entry.find('atom:published', ns).text
            date_str = published_full.split('T')[0] # YYYY-MM-DD
            
            videos.append({
                "type": "upload",
                "title": title,
                "video_id": video_id,
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                "published_at": date_str,
                "date": date_str
            })
    except Exception as e:
        print(f"RSS 抓取失敗: {e}")
    return videos

if __name__ == "__main__":
    existing = load_existing_data()
    existing_streams = {s["video_id"]: s for s in existing.get("streams", [])}

    new_videos = fetch_rss_videos()
    for v in new_videos:
        existing_streams[v["video_id"]] = v
        
    combined_list = list(existing_streams.values())
    combined_list.sort(key=lambda x: x.get("date", ""), reverse=True)

    output = {
        "channel": {
            "name": "塚原大地 / Tsukahara Daichi【にじさんじ】",
            "handle": CHANNEL_HANDLE,
            "icon": "https://yt3.googleusercontent.com/ytc/AIdro_nN_sXoH6Yf8L0X3C2v4gB9T3G_M9_0Q2zN0W1=s900-c-k-c0x00ffffff-no-rj"
        },
        "streams": combined_list
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"成功更新！共有 {len(combined_list)} 筆紀錄。")
