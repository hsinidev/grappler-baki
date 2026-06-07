import os
import re
import json
from pathlib import Path

CHAPTER_REGISTRY = []
MANGA_DIR = Path("manga")
BASE_URL = "https://bakidou.org"

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-').lower()

def scan_chapters():
    registry = []
    series_dirs = [d for d in MANGA_DIR.iterdir() if d.is_dir()]
    for s_dir in series_dirs:
        series_name = s_dir.name
        chap_dirs = [d for d in s_dir.iterdir() if d.is_dir() and (d.name.startswith("chapter-") or d.name.startswith("ch-") or re.search(r'\d+', d.name))]
        for c_dir in chap_dirs:
            # Check for index.html
            if (c_dir / "index.html").exists():
                registry.append(f"{s_dir.name}/{c_dir.name}/index.html")
    return registry

def generate_sitemap():
    print("Regenerating sitemap.xml...")
    chapters = scan_chapters()
    
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    
    # Root pages
    root_pages = ["index.html", "baki.html", "son-of-ogre.html", "baki-dou-2018.html", "golden-kamui.html", 
                  "about.html", "contact.html", "privacy-policy.html", "dmca.html", "terms-of-service.html", 
                  "cookies-policy.html", "disclaimer.html"]
    
    for page in root_pages:
        if os.path.exists(page):
            sitemap.append(f"  <url><loc>{BASE_URL}/{page}</loc><priority>0.8</priority></url>")
    
    # Chapter Pages
    for path in chapters:
        url = path.replace('\\', '/')
        sitemap.append(f"  <url><loc>{BASE_URL}/manga/{url}</loc><priority>0.6</priority></url>")
    
    sitemap.append("</urlset>")
    
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap))
    
    print(f"Sitemap finalized with {len(root_pages) + len(chapters)} URLs.")

if __name__ == "__main__":
    generate_sitemap()
