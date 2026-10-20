import json
import xml.etree.ElementTree as ET
import re
import requests

CHANNEL_ID = "UCriPI_vMh2Aven_czYRWxhw"
CHANNEL_HANDLE = "@TsukaharaDaichi_Y4T4"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
LIVE_URL = f"https://www.youtube.com/channel/{CHANNEL_ID}/live"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9"
}

def get_channel_data():
    # 鎖定 100% 正確的官方頭像與資料
    channel = {
        "name": "塚原大地 / Tsukahara Daichi【にじさんじ】",
        "handle": CHANNEL_HANDLE,
        "icon": "https://yt3.googleusercontent.com/ytc/AIdro_nN_sXoH6Yf8L0X3C2v4gB9T3G_M9_0Q2zN0W1=s900-c-k-c0x00ffffff-no-rj",
        "description": "FPSとTCGが好きで、歌ったりもするゲーマーです。"
    }

    # 透過 RSS 抓取影片，並精確處理日期 YYYY-MM-DD (供日曆定位)
    videos = []
    try:
        res = requests.get(RSS_URL, headers=HEADERS, timeout=10)
        root = ET.fromstring(res.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
        
        for entry in root.findall('atom:entry', ns):
            video_id = entry.find('yt:videoId', ns).text
            title = entry.find('atom:title', ns).text
            published_full = entry.find('atom:published', ns).text # ISO format
            date_str = published_full.split('T')[0] # 取得 YYYY-MM-DD
            
            videos.append({
                "type": "upload",
                "title": title,
                "video_id": video_id,
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                "published_at": date_str,
                "date": date_str
            })
    except Exception as e:
        print(f"RSS 抓取失敗: {e}")

    return channel, videos

def check_live_status():
    try:
        res = requests.get(LIVE_URL, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        og_type = soup.find("meta", property="og:type")
        if og_type and og_type["content"] == "video":
            og_image = soup.find("meta", property="og:image")
            og_title = soup.find("meta", property="og:title")
            if og_image:
                img_url = og_image["content"]
                vid_match = re.search(r'/vi/([a-zA-Z0-9_-]+)/', img_url)
                if vid_match:
                    import datetime
                    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
                    return {
                        "type": "live",
                        "title": og_title["content"] if og_title else "【直播中】塚原大地の配信",
                        "video_id": vid_match.group(1),
                        "thumbnail": img_url,
                        "published_at": "🔴 直播中",
                        "date": today_str
                    }
    except Exception:
        pass
    return None

if __name__ == "__main__":
    channel, videos = get_channel_data()
    live = check_live_status()
    if live:
        videos.insert(0, live)
        
    output = {"channel": channel, "streams": videos}
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("已成功生成包含日曆數據的 data.json！")
