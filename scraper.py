import requests

# -----------------------------------------
# API Links (আপনার দেওয়া সিরিয়াল অনুযায়ী)
# -----------------------------------------
API_EAMIN = "https://eamintalukdar.pages.dev/channels.json"
API_MOMINUL = "https://noisy-mountain-8f1a.mominulislamm3u8.workers.dev/events-streams"
API_TAPMAD = "https://raw.githubusercontent.com/srhady/tapmad-bd/refs/heads/main/tapmad_bd.json"
API_198 = "http://198.195.239.50/tv_channels.json"
API_BINGSTREAM = "https://raw.githubusercontent.com/srhady/bingstream/refs/heads/main/playlist.json"
URL_M3U_BD26 = "https://raw.githubusercontent.com/cctvccplc/Tv-Test/refs/heads/main/BD26.m3u8"

M3U_FILENAME = "sports.m3u"
m3u_content = '#EXTM3U x-tvg-url=""\n\n'
total_streams = 0
headers = {'User-Agent': 'Mozilla/5.0'}

# -----------------------------------------
# 1. Eamin Talukdar JSON (Bangla Channels)
# -----------------------------------------
try:
    print("Fetching from Eamin API...")
    res = requests.get(API_EAMIN, headers=headers, timeout=10)
    for ch in res.json():
        if url := ch.get("url"):
            # শুধু .m3u8 বা .php যুক্ত ডিরেক্ট লিংক নিচ্ছি
            if ".m3u8" in url or "play.php" in url:
                m3u_content += f'#EXTINF:-1 group-title="Bangla TV" tvg-logo="{ch.get("logo", "")}", {ch.get("name", "BD Channel")}\n{url}\n\n'
                total_streams += 1
except Exception as e: print(f"Error (Eamin): {e}")

# -----------------------------------------
# 2. মমিনুল ভাইয়ের API
# -----------------------------------------
try:
    print("Fetching from Mominul API...")
    res = requests.get(API_MOMINUL, headers=headers, timeout=10)
    for event in res.json():
        cat = event.get("cat", "Live Sports")
        title = event.get("title", "Match")
        for stream in event.get("streamUrls", []):
            url = stream.get("url") or stream.get("link")
            if stream.get("type") == "0" and url:
                s_title = stream.get("title", "")
                full_title = f"{title} [{s_title}]" if s_title else title
                m3u_content += f'#EXTINF:-1 group-title="{cat}" tvg-logo="{stream.get("logo", "")}", {full_title}\n{url}\n\n'
                total_streams += 1
except Exception as e: print(f"Error (Mominul): {e}")

# -----------------------------------------
# 3. Tapmad BD JSON (Live Matches)
# -----------------------------------------
try:
    print("Fetching from Tapmad API...")
    res = requests.get(API_TAPMAD, headers=headers, timeout=10)
    for match in res.json().get("Matches", []):
        if match.get("Status") == "Live" and (url := match.get("stream_url")):
            title = f"{match.get('VideoName', 'Tapmad Match')} [{match.get('StageName', 'Live')}]"
            m3u_content += f'#EXTINF:-1 group-title="{match.get("CategoryName", "Tapmad Sports")}" tvg-logo="{match.get("ThumbnailStandard", "")}", {title}\n{url}\n\n'
            total_streams += 1
except Exception as e: print(f"Error (Tapmad): {e}")

# -----------------------------------------
# 4. 198.195.239.50 JSON (Sports & BD)
# -----------------------------------------
try:
    print("Fetching from 198 IP API...")
    res = requests.get(API_198, headers=headers, timeout=10)
    for ch in res.json().get("channels", []):
        # শুধু যেসব চ্যানেল 'visible' বা অ্যাকটিভ আছে সেগুলো নিচ্ছি
        if ch.get("status") != "hidden" and (url := ch.get("url")):
            m3u_content += f'#EXTINF:-1 group-title="{ch.get("category", "Live TV")}" tvg-logo="http://198.195.239.50/{ch.get("logo", "")}", {ch.get("name", "Channel")}\n{url}\n\n'
            total_streams += 1
except Exception as e: print(f"Error (198 IP): {e}")

# -----------------------------------------
# 5. Bingstream API
# -----------------------------------------
try:
    print("Fetching from Bingstream API...")
    res = requests.get(API_BINGSTREAM, headers=headers, timeout=10)
    for ch in res.json().get("channels", []):
        if ch.get("Match Status") == "Live":
            cat = ch.get("Category", "Bingstream Sports")
            title = ch.get("Match Title", "Live Match")
            for stream in ch.get("Stream URL", []):
                if play_url := stream.get("play_url"):
                    m3u_content += f'#EXTINF:-1 group-title="{cat}" tvg-logo="{ch.get("Team 1 Logo", "")}", {title} [{stream.get("server_name", "")}]\n'
                    m3u_content += f'#EXTVLCOPT:http-referrer={ch.get("Referer", "")}\n'
                    m3u_content += f'#EXTVLCOPT:http-user-agent={ch.get("User-Agent", "")}\n{play_url}\n\n'
                    total_streams += 1
except Exception as e: print(f"Error (Bingstream): {e}")

# -----------------------------------------
# 6. BD26 M3U8 (Direct text file append)
# -----------------------------------------
try:
    print("Fetching from BD26 M3U8...")
    res = requests.get(URL_M3U_BD26, headers=headers, timeout=10)
    if res.status_code == 200:
        lines = res.text.splitlines()
        for line in lines:
            if line.strip() and not line.startswith("#EXTM3U"):
                m3u_content += f"{line}\n"
        m3u_content += "\n"
        print("BD26 Playlist appended successfully.")
except Exception as e: print(f"Error (BD26): {e}")

# -----------------------------------------
# Save to File
# -----------------------------------------
try:
    with open(M3U_FILENAME, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print(f"Success! Final playlist has {total_streams} dynamic streams + BD26 channels.")
except Exception as e:
    print(f"Error writing file: {e}")
