import json
import xml.etree.ElementTree as ET
import requests
import os

CHANNEL_ID = "UCriPI_vMh2Aven_czYRWxhw"
CHANNEL_HANDLE = "@TsukaharaDaichi_Y4T4"

# 輪詢多個 RSS 及 Invidious 節點，防止單一 IP 被檔
RSS_SOURCES = [
    f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}",
    f"https://invidious.nerdvpn.de/feed/channel/{CHANNEL_ID}",
    f"https://yewtu.be/feed/channel/{CHANNEL_ID}",
    f"https://invidious.flokinet.to/feed/channel/{CHANNEL_ID}"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def load_existing_data():
    """讀取歷史紀錄，確保舊資料不會遺失"""
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"streams": []}

def fetch_rss_videos():
    videos = []
    for url in RSS_SOURCES:
        try:
            print(f"嘗試抓取來源: {url}")
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200 and "<entry>" in res.text:
                root = ET.fromstring(res.text)
                ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
                
                for entry in root.findall('atom:entry', ns):
                    video_id_elem = entry.find('yt:videoId', ns)
                    title_elem = entry.find('atom:title', ns)
                    published_elem = entry.find('atom:published', ns)
                    
                    if video_id_elem is not None and title_elem is not None and published_elem is not None:
                        video_id = video_id_elem.text
                        title = title_elem.text
                        published_full = published_elem.text
                        date_str = published_full.split('T')[0]
                        
                        videos.append({
                            "type": "upload",
                            "title": title,
                            "video_id": video_id,
                            "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                            "published_at": date_str,
                            "date": date_str
                        })
                
                if len(videos) > 0:
                    print(f"✅ 成功獲取 {len(videos)} 條影片紀錄！")
                    break
        except Exception as e:
            print(f"❌ 來源 {url} 失敗: {e}")
            
    return videos

if __name__ == "__main__":
    existing = load_existing_data()
    existing_streams = {s["video_id"]: s for s in existing.get("streams", []) if "video_id" in s}

    new_videos = fetch_rss_videos()
    
    # 追加並合併新舊數據
    for v in new_videos:
        existing_streams[v["video_id"]] = v
        
    combined_list = list(existing_streams.values())
    combined_list.sort(key=lambda x: x.get("date", ""), reverse=True)

    output = {
        "channel": {
            "name": "塚原大地 / Tsukahara Daichi【にじさんじ】",
            "handle": CHANNEL_HANDLE,
            "icon": "https://ui-avatars.com/api/?name=Daichi&background=1e293b&color=38bdf8&size=200&bold=true"
        },
        "streams": combined_list
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"🎉 成功更新！累積資料總筆數: {len(combined_list)}")
