import json
import xml.etree.ElementTree as ET
import requests
import os

CHANNEL_ID = "UCriPI_vMh2Aven_czYRWxhw"
CHANNEL_HANDLE = "@TsukaharaDaichi_Y4T4"

# 使用多個備用 Invidious / RSS 鏡站，防止單一節點失效
RSS_SOURCES = [
    f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}",
    f"https://invidious.nerdvpn.de/feed/channel/{CHANNEL_ID}",
    f"https://yewtu.be/feed/channel/{CHANNEL_ID}"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def load_existing_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"streams": []}

def fetch_all_rss_videos():
    videos = []
    for url in RSS_SOURCES:
        try:
            print(f"嘗試從 {url} 擷取影片清單...")
            res = requests.get(url, headers=HEADERS, timeout=8)
            if res.status_code == 200 and "<entry>" in res.text:
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
                
                if len(videos) > 0:
                    print(f"成功抓取到 {len(videos)} 條影片紀錄！")
                    break
        except Exception as e:
            print(f"該來源失敗，切換下一來源: {e}")
            
    return videos

if __name__ == "__main__":
    existing = load_existing_data()
    # 建立歷史紀錄 Map，避免舊的資料被刪除
    existing_streams = {s["video_id"]: s for s in existing.get("streams", []) if "video_id" in s}

    # 1. 抓取最新影片
    new_videos = fetch_all_rss_videos()
    
    # 2. 追加與合併（新舊資料融合）
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
        
    print(f"更新完畢！目前歷史資料庫共累積了 {len(combined_list)} 條紀錄。")
