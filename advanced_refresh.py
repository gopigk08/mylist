import requests
import json
import time

# The file we want to create/update
OUTPUT_FILE = "jiohd.json" 

SOURCES = [
    {"name": "GPTR", "url": "https://raw.githubusercontent.com/gptrworldtech/iptv-stream-control/main/channels.json"},
    {"name": "RAUF", "url": "https://raw.githubusercontent.com/Abdur-Rauf/JioTV-Live/main/jio.json"}
]

def refresh():
    all_channels = []
    print(f"Starting refresh at {time.ctime()}")
    
    for source in SOURCES:
        try:
            print(f"Fetching from {source['name']}...")
            res = requests.get(source['url'], timeout=15)
            if res.status_code == 200:
                data = res.json()
                print(f"Found {len(data)} items in {source['name']}")
                for item in data:
                    all_channels.append({
                        "name": item.get("name", item.get("title", "Unknown")),
                        "url": item.get("link", item.get("url", "")),
                        "logo": item.get("logo", ""),
                        "category": item.get("group", item.get("category", "General")),
                        "keyId": item.get("keyId"),
                        "key": item.get("key")
                    })
            else:
                print(f"Failed to fetch {source['name']}: Status {res.status_code}")
        except Exception as e:
            print(f"Error fetching {source['name']}: {str(e)}")

    # Create the final structure with a timestamp to FORCE an update
    result = {
        "last_updated": time.ctime(),
        "channel_count": len(all_channels),
        "channels": all_channels
    }

    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=4)
        
    print(f"Successfully wrote {len(all_channels)} channels to {OUTPUT_FILE}")

if __name__ == "__main__":
    refresh()
