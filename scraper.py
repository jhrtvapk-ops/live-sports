import requests

# দুটি API লিঙ্কের লিস্ট
API_MOMINUL = "https://noisy-mountain-8f1a.mominulislamm3u8.workers.dev/events-streams"
API_BINGSTREAM = "https://raw.githubusercontent.com/srhady/bingstream/refs/heads/main/playlist.json"

M3U_FILENAME = "sports.m3u"
m3u_content = '#EXTM3U x-tvg-url=""\n\n'
total_streams = 0
headers = {'User-Agent': 'Mozilla/5.0'}

# -----------------------------------------
# ১. মমিনুল ভাইয়ের API থেকে ডেটা নেওয়া
# -----------------------------------------
try:
    print("Fetching from Mominul API...")
    res_mominul = requests.get(API_MOMINUL, headers=headers, timeout=15)
    data_mominul = res_mominul.json()
    
    for event in data_mominul:
        cat = event.get("cat", "Live Sports")
        title = event.get("title", "Match")
        
        for stream in event.get("streamUrls", []):
            url = stream.get("url") or stream.get("link")
            # শুধু ওপেন HLS লিংক নিচ্ছি
            if stream.get("type") == "0" and url:
                s_title = stream.get("title", "")
                logo = stream.get("logo", "")
                full_title = f"{title} [{s_title}]" if s_title else title
                
                m3u_content += f'#EXTINF:-1 group-title="{cat}" tvg-logo="{logo}", {full_title}\n'
                m3u_content += f"{url}\n\n"
                total_streams += 1
                
except Exception as e:
    print(f"Error fetching Mominul API: {e}")

# -----------------------------------------
# ২. Bingstream API থেকে ডেটা নেওয়া
# -----------------------------------------
try:
    print("Fetching from Bingstream API...")
    res_bing = requests.get(API_BINGSTREAM, headers=headers, timeout=15)
    data_bing = res_bing.json()
    
    channels = data_bing.get("channels", [])
    
    for ch in channels:
        # শুধু লাইভ খেলাগুলো নেব (Upcoming বাদ)
        if ch.get("Match Status") == "Live":
            cat = ch.get("Category", "Bingstream Sports")
            title = ch.get("Match Title", "Live Match")
            logo = ch.get("Team 1 Logo", "")
            referer = ch.get("Referer", "")
            user_agent = ch.get("User-Agent", "")
            
            for stream in ch.get("Stream URL", []):
                server = stream.get("server_name", "Server")
                play_url = stream.get("play_url")
                
                if play_url:
                    full_title = f"{title} [{server}]"
                    
                    m3u_content += f'#EXTINF:-1 group-title="{cat}" tvg-logo="{logo}", {full_title}\n'
                    # Referer এবং User-Agent যোগ করা হচ্ছে যেন প্লেয়ারে এরর না আসে
                    m3u_content += f'#EXTVLCOPT:http-referrer={referer}\n'
                    m3u_content += f'#EXTVLCOPT:http-user-agent={user_agent}\n'
                    m3u_content += f"{play_url}\n\n"
                    total_streams += 1

except Exception as e:
    print(f"Error fetching Bingstream API: {e}")

# -----------------------------------------
# ফাইল সেভ করা
# -----------------------------------------
try:
    with open(M3U_FILENAME, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print(f"Success! Total {total_streams} streams written to {M3U_FILENAME}.")
except Exception as e:
    print(f"Error writing file: {e}")
