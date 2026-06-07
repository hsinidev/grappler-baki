import asyncio
import aiohttp
import json
import os
from pathlib import Path
import re

# Configuration from ollama_api.json (manually extracted here for robustness)
URL = "https://ollama.com/api/generate"
MODEL = "gpt-oss:120b"
import os
# API keys are loaded from environment variables for security
env_keys = os.environ.get("BIGMODEL_API_KEY", "")
API_KEYS = [k.strip() for k in env_keys.split(",") if k.strip()] if env_keys else []

MANGA_DIR = Path("manga")
CONCURRENCY = 16
SEMAPHORE = asyncio.Semaphore(CONCURRENCY)

def clean_name(name):
    # Capitalize and replace hyphens with spaces
    return name.replace("-", " ").title()

async def generate_seo_article(session, api_key, series, chapter):
    series_clean = clean_name(series)
    chapter_clean = clean_name(chapter)
    
    prompt = f"""
    Write a high-authority, SEO-optimized blog article (~500 words) about {series_clean} {chapter_clean}.
    The article MUST be professional and engaging.
    
    Requirements:
    1. A catchy H2 title including "Read {series_clean} {chapter_clean} Online".
    2. An intensive summary of the chapter's plot.
    3. Character break-down (The Hanma family, the Sumos, or the Convicts depending on context).
    4. Why bakidou.org is the best place to read this manga.
    5. A compelling "Next Chapter" teaser.
    
    Format in HTML:
    - Use <h2> for the title.
    - Use <p> for body text.
    - Use <strong> for important character names.
    - NO Markdown formatting (no **, no #). Use HTML tags.
    - Absolutely no <html> or <body> boilerplate.
    - Return ONLY the HTML content.
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    for attempt in range(5): # Increased retry attempts
        try:
            async with session.post(URL, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "")
                elif response.status == 429:
                    wait_time = (attempt + 1) * 10
                    print(f"RATE LIMIT: Key {api_key[:8]}... waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    error_text = await response.text()
                    print(f"ERROR {response.status}: {api_key[:8]}... - {error_text[:200]}")
                    await asyncio.sleep(2)
        except Exception as e:
            wait_time = (attempt + 1) * 2
            print(f"RETRY {attempt+1}: {series}/{chapter} - {type(e).__name__}: {str(e)}")
            await asyncio.sleep(wait_time)
            
    return None

async def process_chapter(session, api_key, html_file):
    series = html_file.parts[-3]
    chapter = html_file.parts[-2]
    
    async with SEMAPHORE:
        # Check if already injected
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "<!-- SEO_CONTENT_INJECTED -->" in content:
            print(f"ALREADY INJECTED: {series}/{chapter}")
            return

        print(f"GENERATING: {series}/{chapter} using {api_key[:8]}...")
        article = await generate_seo_article(session, api_key, series, chapter)
        
        if article:
            # Wrap in the required CSS class and add a marker
            injected_html = f'\n    <!-- SEO_CONTENT_INJECTED -->\n    <section class="seo-section">\n        {article}\n    </section>\n'
            
            if "<!-- SEO_CONTENT_INJECTION_POINT -->" in content:
                new_content = content.replace("<!-- SEO_CONTENT_INJECTION_POINT -->", injected_html)
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"SUCCESS: Injected {series}/{chapter}")
            else:
                print(f"ERROR: Injection point missing in {html_file}")
        else:
            print(f"FAILED: Could not generate for {series}/{chapter}")

async def main():
    if not MANGA_DIR.exists():
        print(f"Error: {MANGA_DIR} directory not found.")
        return

    # Sort files to ensure stable order
    html_files = sorted(list(MANGA_DIR.glob("**/index.html")))
    total = len(html_files)
    print(f"Total Chapters Found: {total}")
    
    MAX_TASKS = 200 # Process in batches to avoid overwhelming memory/connection pool
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
        for i in range(0, total, MAX_TASKS):
            batch = html_files[i:i + MAX_TASKS]
            tasks = []
            for j, html_file in enumerate(batch):
                api_key = API_KEYS[(i + j) % len(API_KEYS)]
                tasks.append(process_chapter(session, api_key, html_file))
            
            print(f"--- Processing Batch {i//MAX_TASKS + 1} ({len(batch)} chapters) ---")
            await asyncio.gather(*tasks)
            print(f"--- Batch {i//MAX_TASKS + 1} Complete. Sleeping for stabilization... ---")
            await asyncio.sleep(5)

if __name__ == "__main__":
    import sys
    # Increase recursion depth for deeply nested paths if any
    sys.setrecursionlimit(2000)
    asyncio.run(main())
