import requests

API_URL = "https://noisy-mountain-8f1a.mominulislamm3u8.workers.dev/events-streams"
M3U_FILENAME = "sports.m3u"

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(API_URL, headers=headers, timeout=15)
    data = response.json()
    
    m3u_content = '#EXTM3U x-tvg-url=""\n\n'
    count = 0
    
    for event in data:
        cat = event.get("cat", "Live Sports")
        title = event.get("title", "Match")
        
        for stream in event.get("streamUrls", []):
            url = stream.get("url") or stream.get("link")
            if stream.get("type") == "0" and url:
                s_title = stream.get("title", "")
                logo = stream.get("logo", "")
                full_title = f"{title} [{s_title}]" if s_title else title
                
                m3u_content += f'#EXTINF:-1 group-title="{cat}" tvg-logo="{logo}", {full_title}\n'
                m3u_content += f"{url}\n\n"
                count += 1
                
    with open(M3U_FILENAME, "w", encoding="utf-8") as f:
        f.write(m3u_content)
        print(f"Success: {count} streams updated!")

except Exception as e:
    print(f"Error happened: {e}")
