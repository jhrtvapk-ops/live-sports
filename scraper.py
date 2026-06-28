import requests
import os
import json

# -----------------------------------------
# এক বক্স থেকে সব লিংক বের করে আনা
# -----------------------------------------
links_json_str = os.environ.get("ALL_API_LINKS", "{}")

try:
    LINKS = json.loads(links_json_str)
except json.JSONDecodeError:
    LINKS = {}

API_EAMIN = LINKS.get("EAMIN")
API_MOMINUL = LINKS.get("MOMINUL")
API_TAPMAD = LINKS.get("TAPMAD")
API_198 = LINKS.get("IP_198")
API_BINGSTREAM = LINKS.get("BINGSTREAM")
URL_M3U_BD26 = LINKS.get("BD26")

m3u_content = '#EXTM3U x-tvg-url=""\n\n'
headers = {'User-Agent': 'Mozilla/5.0'}

# 1. Eamin API
try:
    if API_EAMIN:
        res = requests.get(API_EAMIN, headers=headers, timeout=10)
        for ch in res.json():
            if url := ch.get("url"):
                if ".m3u8" in url or "play.php" in url:
                    m3u_content += f'#EXTINF:-1 group-title="Bangla TV" tvg-logo="{ch.get("logo", "")}", {ch.get("name", "BD Channel")}\n{url}\n\n'
except: pass

# 2. Mominul API
try:
    if API_MOMINUL:
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
except: pass

# 3. Tapmad API
try:
    if API_TAPMAD:
        res = requests.get(API_TAPMAD, headers=headers, timeout=10)
        for match in res.json().get("Matches", []):
            if match.get("Status") == "Live" and (url := match.get("stream_url")):
                title = f"{match.get('VideoName', 'Tapmad Match')} [{match.get('StageName', 'Live')}]"
                m3u_content += f'#EXTINF:-1 group-title="{match.get("CategoryName", "Tapmad Sports")}" tvg-logo="{match.get("ThumbnailStandard", "")}", {title}\n{url}\n\n'
except: pass

# 4. 198 IP API
try:
    if API_198:
        res = requests.get(API_198, headers=headers, timeout=10)
        for ch in res.json().get("channels", []):
            if ch.get("status") != "hidden" and (url := ch.get("url")):
                m3u_content += f'#EXTINF:-1 group-title="{ch.get("category", "Live TV")}" tvg-logo="http://198.195.239.50/{ch.get("logo", "")}", {ch.get("name", "Channel")}\n{url}\n\n'
except: pass

# 5. Bingstream API
try:
    if API_BINGSTREAM:
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
except: pass

# 6. BD26 M3U8
try:
    if URL_M3U_BD26:
        res = requests.get(URL_M3U_BD26, headers=headers, timeout=10)
        if res.status_code == 200:
            lines = res.text.splitlines()
            for line in lines:
                if line.strip() and not line.startswith("#EXTM3U"):
                    m3u_content += f"{line}\n"
            m3u_content += "\n"
except: pass

# -----------------------------------------
# Upload to Secret Gist
# -----------------------------------------
gist_id = os.environ.get("GIST_ID")
gist_token = os.environ.get("GIST_TOKEN")

if gist_id and gist_token:
    headers_gist = {
        "Authorization": f"token {gist_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "files": {
            "sports.m3u": {
                "content": m3u_content
            }
        }
    }
    try:
        response = requests.patch(f"https://api.github.com/gists/{gist_id}", headers=headers_gist, data=json.dumps(data))
        if response.status_code == 200:
            print("Successfully updated Secret Gist!")
        else:
            print(f"Failed to update Gist: {response.status_code}")
    except Exception as e:
        print(f"Error updating Gist: {e}")
else:
    print("GIST_ID or GIST_TOKEN is missing!")
