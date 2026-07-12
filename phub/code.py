import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "origin": "https://cn.pornhub.com",
    "priority": "u=1, i",
    "referer": "https://cn.pornhub.com/",
    "sec-ch-ua": "\"Google Chrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
}
m3u8_url = "https://ev-h.phncdn.com/hls/c6251/videos/202511/07/28931025/720P_4000K_28931025.mp4/index-v1-a1.m3u8"
params = {
    "validfrom": "1781750283",
    "validto": "1781757483",
    "ipa": "1",
    "hdl": "-1",
    "hash": "RcNs9no93Pbu3bKcR8c9Q+TDhak="
}

OUTPUT_FILE = "output.mp4"
TEMP_DIR = "ts_segments"
MAX_WORKERS = 8


def fetch_m3u8(url, params):
    """Fetch and parse the M3U8 playlist, returning a list of TS segment URLs."""
    print(f"[1/4] Fetching M3U8 playlist...")
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()

    lines = resp.text.strip().splitlines()
    segments = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            # Resolve relative URLs against the base M3U8 URL
            full_url = urljoin(url, line)
            segments.append(full_url)

    print(f"  Found {len(segments)} TS segments")
    return segments


def download_segment(args):
    """Download a single TS segment. Returns (index, filepath) on success."""
    idx, url = args
    filepath = os.path.join(TEMP_DIR, f"segment_{idx:05d}.ts")
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(resp.content)
            return idx, filepath
        except Exception as e:
            print(f"  Retry {attempt + 1} for segment {idx}: {e}")
    raise Exception(f"Failed to download segment {idx} after 3 attempts")


def download_all_segments(segments):
    """Download all TS segments in parallel."""
    print(f"[2/4] Downloading {len(segments)} TS segments ({MAX_WORKERS} workers)...")
    os.makedirs(TEMP_DIR, exist_ok=True)

    tasks = [(i, url) for i, url in enumerate(segments)]
    results = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_segment, task): task[0] for task in tasks}
        for future in as_completed(futures):
            idx, filepath = future.result()
            results[idx] = filepath
            if len(results) % 50 == 0 or len(results) == len(tasks):
                print(f"  Progress: {len(results)}/{len(tasks)}")

    # Return sorted by index
    return [results[i] for i in sorted(results)]


def merge_to_mp4(segment_files, output_path):
    """Merge TS segments into a single MP4 file using binary concatenation."""
    print(f"[3/4] Merging {len(segment_files)} segments into {output_path}...")
    with open(output_path, "wb") as outfile:
        for filepath in segment_files:
            with open(filepath, "rb") as infile:
                outfile.write(infile.read())
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  Output: {output_path} ({size_mb:.1f} MB)")


def cleanup():
    """Remove temporary TS segment files and directory."""
    print(f"[4/4] Cleaning up temp files...")
    for f in os.listdir(TEMP_DIR):
        os.remove(os.path.join(TEMP_DIR, f))
    os.rmdir(TEMP_DIR)
    print("  Done.")


if __name__ == "__main__":
    try:
        segments = fetch_m3u8(m3u8_url, params)
        segment_files = download_all_segments(segments)
        merge_to_mp4(segment_files, OUTPUT_FILE)
        cleanup()
        print(f"\nSaved as: {OUTPUT_FILE}")
    except Exception as e:
        print(f"\nError: {e}")
        raise