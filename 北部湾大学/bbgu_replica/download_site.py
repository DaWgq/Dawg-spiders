import requests
import os
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import shutil

BASE_URL = "https://www.bbgu.edu.cn/"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

session = requests.Session()
session.headers.update(
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
)

downloaded = set()


def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def download_file(url, save_path):
    if url in downloaded or os.path.exists(save_path):
        return True
    downloaded.add(url)
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 200:
            ensure_dir(save_path)
            with open(save_path, "wb") as f:
                f.write(resp.content)
            print(f"  OK: {url}")
            return True
        else:
            print(f"  FAIL({resp.status_code}): {url}")
            return False
    except Exception as e:
        print(f"  ERROR: {url} - {e}")
        return False


def url_to_local_path(url, base_dir=OUTPUT_DIR):
    parsed = urlparse(url)
    path = parsed.path
    if path.startswith("/"):
        path = path[1:]
    if not path:
        path = "index.html"
    if parsed.query:
        path = path.replace("?", "_").replace("&", "_").replace("=", "_")
    full_path = os.path.join(base_dir, path)
    if not os.path.splitext(full_path)[1]:
        full_path = os.path.join(full_path, "index.html")
    return full_path


print("=" * 60)
print("Step 1: Download homepage HTML")
print("=" * 60)
resp = session.get(BASE_URL, timeout=30)
resp.encoding = "utf-8"
html = resp.text

soup = BeautifulSoup(html, "html.parser")

# Save original HTML
with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("Saved index.html")

print("\n" + "=" * 60)
print("Step 2: Download all linked resources")
print("=" * 60)

# Collect all resource URLs
resources = set()

# CSS links
for link in soup.find_all("link", rel="stylesheet"):
    href = link.get("href")
    if href:
        full_url = urljoin(BASE_URL, href)
        resources.add(("css", full_url, href))

# JS scripts
for script in soup.find_all("script", src=True):
    src = script.get("src")
    if src:
        full_url = urljoin(BASE_URL, src)
        resources.add(("js", full_url, src))

# Images
for img in soup.find_all("img", src=True):
    src = img.get("src")
    if src:
        full_url = urljoin(BASE_URL, src)
        resources.add(("img", full_url, src))

# Background images in inline styles
for tag in soup.find_all(style=True):
    style = tag.get("style", "")
    urls = re.findall(r'url\(["\']?([^"\'\)]+)["\']?\)', style)
    for url in urls:
        full_url = urljoin(BASE_URL, url)
        resources.add(("img", full_url, url))

# Links (for favicon etc)
for link in soup.find_all("link"):
    href = link.get("href")
    if (
        href
        and not link.get("rel")
        or (link.get("rel") and "stylesheet" not in link.get("rel"))
    ):
        full_url = urljoin(BASE_URL, href)
        ext = os.path.splitext(full_url)[1].lower()
        if ext in [
            ".ico",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".webp",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
        ]:
            resources.add(("other", full_url, href))

print(f"\nFound {len(resources)} resources to download")

# Download CSS files first, then parse them for additional resources
css_downloaded = []
for rtype, full_url, original_url in sorted(
    resources, key=lambda x: (0 if x[0] == "css" else 1, x[1])
):
    if (
        "bbgu.edu.cn" in full_url
        or urlparse(full_url).netloc == ""
        or urlparse(full_url).netloc == "www.bbgu.edu.cn"
    ):
        local_path = url_to_local_path(full_url)
        success = download_file(full_url, local_path)
        if success and rtype == "css":
            css_downloaded.append((full_url, local_path))

# Parse downloaded CSS for additional resources (fonts, images)
print("\n" + "=" * 60)
print("Step 3: Parse CSS for embedded resources")
print("=" * 60)
css_resources = set()
for css_url, css_path in css_downloaded:
    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
        except:
            try:
                with open(css_path, "r", encoding="gbk") as f:
                    css_content = f.read()
            except:
                continue

        urls = re.findall(r'url\(["\']?([^"\'\)]+)["\']?\)', css_content)
        for url in urls:
            if url.startswith("data:"):
                continue
            full_url = urljoin(css_url, url)
            if (
                "bbgu.edu.cn" in full_url
                or urlparse(full_url).netloc == ""
                or urlparse(full_url).netloc == "www.bbgu.edu.cn"
            ):
                css_resources.add(full_url)

print(f"Found {len(css_resources)} additional resources in CSS")
for url in css_resources:
    local_path = url_to_local_path(url)
    download_file(url, local_path)

# Also download __local/ images from the HTML
print("\n" + "=" * 60)
print("Step 4: Download __local/ resources (news images etc)")
print("=" * 60)
local_resources = set()
for tag in soup.find_all(["img", "a", "link"]):
    for attr in ["src", "href"]:
        val = tag.get(attr)
        if val and "/__local/" in val:
            full_url = urljoin(BASE_URL, val)
            local_resources.add(full_url)

for url in local_resources:
    local_path = url_to_local_path(url)
    download_file(url, local_path)

print("\n" + "=" * 60)
print("Step 5: Fix HTML paths to local")
print("=" * 60)

# Re-read the saved HTML and fix paths
with open(os.path.join(OUTPUT_DIR, "index.html"), "r", encoding="utf-8") as f:
    html_content = f.read()


def fix_url_in_html(match):
    prefix = match.group(1)
    url = match.group(2)
    suffix = match.group(3)

    if (
        url.startswith("data:")
        or url.startswith("http://")
        or url.startswith("https://")
    ):
        if "bbgu.edu.cn" not in url and "www.bbgu.edu.cn" not in url:
            return match.group(0)

    full_url = urljoin(BASE_URL, url)
    local_path = url_to_local_path(full_url)
    relative = os.path.relpath(local_path, OUTPUT_DIR)
    return f"{prefix}{relative}{suffix}"


# Fix src and href attributes
html_content = re.sub(
    r'((?:src|href)=["\'])([^"\']+)(["\'])', fix_url_in_html, html_content
)

# Fix CSS url() references in inline styles
html_content = re.sub(
    r'(url\(["\']?)([^"\'\)]+)(["\']?\))', fix_url_in_html, html_content
)

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

print("Fixed HTML paths")

print("\n" + "=" * 60)
print("Step 6: Fix CSS file paths")
print("=" * 60)
for css_url, css_path in css_downloaded:
    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            try:
                with open(css_path, "r", encoding="gbk") as f:
                    content = f.read()
            except:
                continue

        original_content = content

        def fix_css_url(match):
            url = match.group(1)
            if url.startswith("data:"):
                return match.group(0)
            full_url = urljoin(css_url, url)
            local_path = url_to_local_path(full_url)
            css_dir = os.path.dirname(css_path)
            try:
                relative = os.path.relpath(local_path, css_dir)
            except:
                relative = local_path
            return f'url("{relative}")'

        content = re.sub(r'url\(["\']?([^"\'\)]+)["\']?\)', fix_css_url, content)

        if content != original_content:
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Fixed: {css_path}")

print("\n" + "=" * 60)
print("Download complete!")
print(f"Output directory: {OUTPUT_DIR}")
print("=" * 60)
