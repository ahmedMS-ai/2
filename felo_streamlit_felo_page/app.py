\
import streamlit as st
from bs4 import BeautifulSoup
from pathlib import Path
import base64, os

st.set_page_config(page_title="ا.محمد نبيل", page_icon="🟣", layout="wide")

SITE_DIR = Path(__file__).parent / "site"
# Detect candidate HTML if not set explicitly
CANDIDATES = []
for p in SITE_DIR.rglob("*.html"):
    CANDIDATES.append(p)
HTML_PATH = None
# Prefer file names containing Arabic or 'index'
for p in CANDIDATES:
    name = p.name
    if any(k in name for k in ["index", "Index", "home"]):
        HTML_PATH = p
        break
if HTML_PATH is None and CANDIDATES:
    HTML_PATH = sorted(CANDIDATES, key=lambda p: p.stat().st_size, reverse=True)[0]

if HTML_PATH is None:
    st.error("لم يتم العثور على صفحة HTML داخل مجلد site/.")
    st.stop()

def is_relative_url(url: str) -> bool:
    if not url: return False
    url = url.strip()
    return not (url.startswith("http://") or url.startswith("https://") or url.startswith("data:") or url.startswith("#"))

def file_to_data_uri(fp: Path) -> str:
    mime = "application/octet-stream"
    ext = fp.suffix.lower()
    if ext in [".png"]: mime = "image/png"
    elif ext in [".jpg", ".jpeg"]: mime = "image/jpeg"
    elif ext in [".gif"]: mime = "image/gif"
    elif ext in [".svg"]: mime = "image/svg+xml"
    data = fp.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"

html = HTML_PATH.read_text(encoding="utf-8", errors="ignore")
soup = BeautifulSoup(html, "html.parser")

# Force RTL if needed
html_tag = soup.find("html")
if html_tag and not html_tag.has_attr("dir"):
    html_tag["dir"] = "rtl"
body_tag = soup.find("body")
if body_tag and body_tag.get("dir", "").lower() != "rtl":
    body_tag["dir"] = "rtl"

# Inline <link rel="stylesheet" href="..."> that are local
for link in soup.find_all("link"):
    rel = (link.get("rel") or [""])[0]
    href = link.get("href", "")
    if rel and "stylesheet" in rel and is_relative_url(href):
        css_path = (SITE_DIR / href).resolve()
        if css_path.exists():
            css_text = css_path.read_text(encoding="utf-8", errors="ignore")
            style_tag = soup.new_tag("style")
            style_tag.string = css_text
            link.replace_with(style_tag)

# Inline <script src="..."> that are local
for script in soup.find_all("script"):
    src = script.get("src", "")
    if is_relative_url(src):
        js_path = (SITE_DIR / src).resolve()
        if js_path.exists():
            js_text = js_path.read_text(encoding="utf-8", errors="ignore")
            new_sc = soup.new_tag("script")
            new_sc.string = js_text
            script.replace_with(new_sc)

# Inline <img src="..."> that are local
for img in soup.find_all("img"):
    src = img.get("src", "")
    if is_relative_url(src):
        img_path = (SITE_DIR / src).resolve()
        if img_path.exists():
            img["src"] = file_to_data_uri(img_path)

# Render
st.components.v1.html(str(soup), height=1200, scrolling=True)
