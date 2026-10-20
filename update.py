import json
import requests
import os

CHANNEL_ID = "UCriPI_vMh2Aven_czYRWxhw"
CHANNEL_HANDLE = "@TsukaharaDaichi_Y4T4"

# Holodex 免費 public API 查 VTuber 影片
HOLODEX_URL = f"https://holodex.net/api/v2/channels/{CHANNEL_ID}/videos?lang=en&type=stream%2Cplaceholder%2Cclip&limit=50&offset=0&paginated=true"

# 保底 API (Invidious API)
INVIDIOUS_API = f"https://yewtu.be/api/v1/channels/{CHANNEL_ID}/videos"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def load_existing_data():
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"streams": []}

def fetch_videos():
    videos = []
    
    # 方法 1: 優先嘗試 Holodex (專為 VTuber 設計，對 GitHub Actions 最穩定)
    try:
        print("正在從 Holodex API 擷取塚原大地的影片...")
        res = requests.get(HOLODEX_URL, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            items = data.get("items", []) if isinstance(data, dict) else data
            for item in items:
                video_id = item.get("id")
                title = item.get("title")
                # 取得開台時間或發布時間
                pub_time = item.get("available_at") or item.get("published_at")
                date_str = pub_time.split("T")[0] if pub_time else "2026-10-01"
                
                if video_id and title:
                    videos.append({
                        "type": "upload",
                        "title": title,
                        "video_id": video_id,
                        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                        "published_at": date_str,
                        "date": date_str
                    })
            if len(videos) > 0:
                print(f"✅ Holodex 抓取成功！獲取 {len(videos)} 條影片。")
                return videos
    except Exception as e:
        print(f"❌ Holodex 失敗: {e}")

    # 方法 2: 保底 Invidious API
    try:
        print("嘗試保底 Invidious API...")
        res = requests.get(INVIDIOUS_API, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            items = res.json()
            for item in items:
                video_id = item.get("videoId")
                title = item.get("title")
                pub_time = item.get("publishedText")
                date_str = "2026-10-18" # 預設預備日期
                if video_id and title:
                    videos.append({
                        "type": "upload",
                        "title": title,
                        "video_id": video_id,
                        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                        "published_at": date_str,
                        "date": date_str
                    })
            if len(videos) > 0:
                print(f"✅ Invidious API 抓取成功！獲取 {len(videos)} 條影片。")
                return videos
    except Exception as e:
        print(f"❌ Invidious 失敗: {e}")

    return videos

if __name__ == "__main__":
    existing = load_existing_data()
    existing_streams = {s["video_id"]: s for s in existing.get("streams", []) if "video_id" in s}

    new_videos = fetch_videos()
    
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
        
    print(f"🎉 成功！目前 data.json 共有 {len(combined_list)} 筆資料。")
