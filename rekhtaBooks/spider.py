"""爬取 rekhta 电子书图片 001-677.

用法:
    python spider.py            # 默认并发 10, 输出到 ./images
    python spider.py --concurrency 20
    python spider.py --start 1 --end 677
"""

import argparse
import asyncio
from pathlib import Path

import httpx

BASE_URL = "https://ebooksapi.rekhta.org/images/24501190-8779-4c8c-8d52-434cc7efbcb5/{:03d}.jpg"
HEADERS = {
    "accept": "image/jxl,image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://www.rekhta.org/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36",
}


async def download_one(client, sem, idx, out_dir, retries):
    url = BASE_URL.format(idx)
    dest = out_dir / f"{idx:03d}.jpg"
    if dest.exists() and dest.stat().st_size > 0:
        return idx, "skip", 0

    async with sem:
        for attempt in range(1, retries + 1):
            try:
                r = await client.get(url, headers=HEADERS)
                if r.status_code != 200:
                    if attempt == retries:
                        return idx, f"http {r.status_code}", 0
                    await asyncio.sleep(1 * attempt)
                    continue
                data = r.content
                if not data:
                    if attempt == retries:
                        return idx, "empty", 0
                    await asyncio.sleep(1 * attempt)
                    continue
                dest.write_bytes(data)
                return idx, "ok", len(data)
            except Exception as e:  # noqa: BLE001
                if attempt == retries:
                    return idx, f"err {e}", 0
                await asyncio.sleep(1 * attempt)
    return idx, "fail", 0


async def main(start, end, concurrency, out_dir, retries):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sem = asyncio.Semaphore(concurrency)
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    async with httpx.AsyncClient(limits=limits, timeout=60, http2=False) as client:
        tasks = [download_one(client, sem, i, out_dir, retries) for i in range(start, end + 1)]
        done = 0
        failed = []
        total = len(tasks)
        for coro in asyncio.as_completed(tasks):
            idx, status, size = await coro
            done += 1
            if status not in ("ok", "skip"):
                failed.append((idx, status))
                print(f"[{done}/{total}] {idx:03d} -> {status}")
            elif done % 25 == 0 or done == total:
                print(f"[{done}/{total}] progress... (last {idx:03d}: {status} {size})")

        if failed:
            fail_file = Path(out_dir).parent / "failed.txt"
            with open(fail_file, "w", encoding="utf-8") as f:
                for idx, status in failed:
                    f.write(f"{idx:03d} {status}\n")
            print(f"\n完成，失败 {len(failed)} 个，详见 {fail_file}")
        else:
            print(f"\n全部完成，共 {total} 张图片 -> {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=677)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--out", default="images")
    args = parser.parse_args()
    asyncio.run(main(args.start, args.end, args.concurrency, args.out, args.retries))
