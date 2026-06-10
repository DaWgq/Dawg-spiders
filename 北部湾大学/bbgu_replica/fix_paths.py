import os
import re

base = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(base, "index.html")

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace backslashes with forward slashes in src/href and url() paths
content = content.replace("\\", "/")

# Fix any doubled slashes from the replacement
content = content.replace("//", "/")

# But restore protocol slashes
content = content.replace("https:/", "https://")
content = content.replace("http:/", "http://")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed backslashes to forward slashes in index.html")

# Also fix CSS files
for dirpath, dirnames, filenames in os.walk(base):
    for fn in filenames:
        if fn.endswith(".css"):
            css_path = os.path.join(dirpath, fn)
            with open(css_path, "r", encoding="utf-8", errors="ignore") as f:
                css_content = f.read()
            if "\\" in css_content:
                css_content = css_content.replace("\\", "/")
                with open(css_path, "w", encoding="utf-8") as f:
                    f.write(css_content)
                print(f"Fixed backslashes in: {os.path.relpath(css_path, base)}")

print("Done fixing paths!")
