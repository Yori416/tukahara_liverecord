import json
import re
import requests
from bs4 import BeautifulSoup

CHANNEL_ID = "UCriPI_vMh2Aven_czYRWxhw"
CHANNEL_HANDLE = "@TsukaharaDaichi_Y4T4"
BASE_URL = f"https://www.youtube.com/channel/{CHANNEL_ID}"
LIVE_URL = f"{BASE_URL}/live"
VIDEOS_URL = f"{BASE_URL}/videos"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
}

def get_channel_info():
    try:
        res = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        og_image = soup.find("meta", property="og:image")
        og_title = soup.find("meta", property="og:title")
        
        return {
            "name": og_title["content"] if og_title else "塚原大地 / Tsukahara Daichi【にじさんじ】",
            "handle": CHANNEL_HANDLE,
            "icon": og_image["content"] if og_image else "https://yt3.googleusercontent.com/ytc/AIdro_n...=s900-c-k-c0x00ffffff-no-rj"
        }
    except Exception as e:
        print(f"頻道資訊抓取警報: {e}")
        return {
            "name": "塚原大地 / Tsukahara Daichi【にじさんじ】",
            "handle": CHANNEL_HANDLE,
            "icon": "https://yt3.googleusercontent.com/ytc/AIdro_n...=s900-c-k-c0x00ffffff-no-rj"
        }

def get_latest_videos():
    videos = []
    try:
        res = requests.get(VIDEOS_URL, headers=HEADERS, timeout=10)
        match = re.search(r'var ytInitialData = ({.*?});</script>', res.text)
        if not match:
            match = re.search(r'ytInitialData\s*=\s*({.+?});</script>', res.text)
            
        if match:
            data = json.loads(match.group(1))
            contents = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents']
            for content in contents:
                if 'richItemRenderer' in content:
                    v_data = content['richItemRenderer']['content'].get('videoRenderer')
                    if v_data:
                        vid = v_data['videoId']
                        videos.append({
                            "type": "upload",
                            "title": v_data['title']['runs'][0]['text'],
                            "video_id": vid,
                            "thumbnail": f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg",
                            "published_at": v_data.get('publishedTimeText', {}).get('simpleText', '近期')
                        })
    except Exception as e:
        print(f"影片列表抓取警報: {e}")
    
    # 防呆保底：如果爬蟲失敗，自動呈現熱門影片
    if not videos:
        videos = [
            {
                "type": "upload",
                "title": "パンダヒーロー / Covered by Y4T4男 (塚原大地×男虎×レヨン×九里詠太)【にじさんじ】",
                "video_id": "I67xVNUMj9k",
                "thumbnail": "https://i.ytimg.com/vi/I67xVNUMj9k/maxresdefault.jpg",
                "published_at": "1週前"
            },
            {
                "type": "upload",
                "title": "【浮気判定シート】塚原大地の恋愛観を話してみる。【塚原大地 / にじさんじ】",
                "video_id": "GriXje18gMA",
                "thumbnail": "https://i.ytimg.com/vi/GriXje18gMA/maxresdefault.jpg",
                "published_at": "4日前"
            }
        ]
    return videos[:6]

def check_live_status():
    try:
        res = requests.get(LIVE_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        og_type = soup.find("meta", property="og:type")
        if og_type and og_type["content"] == "video":
            og_image = soup.find("meta", property="og:image")
            og_title = soup.find("meta", property="og:title")
            if og_image:
                img_url = og_image["content"]
                vid_match = re.search(r'/vi/([a-zA-Z0-9_-]+)/', img_url)
                if vid_match:
                    vid = vid_match.group(1)
                    return {
                        "type": "live",
                        "title": og_title["content"] if og_title else "【直播中】塚原大地の配信",
                        "video_id": vid,
                        "thumbnail": img_url,
                        "published_at": "🔴 配信中"
                    }
    except Exception:
        pass
    return None

if __name__ == "__main__":
    print("正在執行抓取程序...")
    channel_info = get_channel_info()
    videos = get_latest_videos()
    live = check_live_status()
    
    if live:
        videos.insert(0, live)
        
    output = {
        "channel": channel_info,
        "streams": videos
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("成功：data.json 已順利生成！")
