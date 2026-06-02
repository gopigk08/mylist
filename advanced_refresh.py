import requests
import json
import concurrent.futures
import time

# --- ADVANCED CONFIGURATION ---
SOURCES = [
    {"name": "GPTR", "url": "https://raw.githubusercontent.com/gptrworldtech/iptv-stream-control/main/channels.json", "type": "json"},
    {"name": "Jio-Alternative", "url": "https://raw.githubusercontent.com/Abdur-Rauf/JioTV-Live/main/jio.json", "type": "json"},
    # Add more sources here
]

OUTPUT_FILE = "playlist.json"
CHECK_THREADS = 10  # Speed up link checking
TIMEOUT = 5         # Timeout for health check

def check_link(channel):
    """Advanced Health Check: Verifies if the link is active and returns the channel if alive."""
    url = channel.get('url')
    if not url: return None
    
    try:
        # Use HEAD request for speed, fallback to GET for workers
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://joplay.lrl45.workers.dev/"}
        response = requests.get(url, headers=headers, stream=True, timeout=TIMEOUT)
        
        if response.status_code == 200:
            # Smart DRM Detection: If it's an .mpd but has no key, it might be clear Widevine
            if ".mpd" in url.lower() and not channel.get('keyId'):
                channel['drmScheme'] = "widevine"
            return channel
    except:
        pass
    return None

def process_sources():
    all_channels = []
    
    for source in SOURCES:
        print(f"[*] Processing Source: {source['name']}")
        try:
            res = requests.get(source['url'], timeout=10)
            if res.status_code != 200: continue
            
            data = res.json()
            for entry in data:
                # Normalize data structure to OMNI TV format
                channel = {
                    "id": f"{source['name'].lower()}_{entry.get('name', '').replace(' ', '_')}",
                    "name": entry.get('name', entry.get('title')),
                    "url": entry.get('link', entry.get('url')),
                    "logo": entry.get('logo', entry.get('image', '')),
                    "category": entry.get('group', entry.get('category', 'General')),
                    "keyId": entry.get('keyId'),
                    "key": entry.get('key'),
                    "userAgent": "OminiTV/1.0",
                    "headers": {"Referer": "https://joplay.lrl45.workers.dev/"}
                }
                if channel['url']:
                    all_channels.append(channel)
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")

    # --- ADVANCED FEATURE: Parallel Health Checking ---
    print(f"[*] Checking {len(all_channels)} links for health...")
    working_channels = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CHECK_THREADS) as executor:
        results = list(executor.map(check_link, all_channels))
        working_channels = [ch for ch in results if ch is not None]

    # Deduplicate by name
    unique_channels = {ch['name']: ch for ch in working_channels}.values()

    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(list(unique_channels), f, indent=4)
    
    print(f"[!] SUCCESS: {len(unique_channels)} working channels saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    start_time = time.time()
    process_sources()
    print(f"Finished in {time.time() - start_time:.2f} seconds")
