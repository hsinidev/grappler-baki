import asyncio
import aiohttp
import os
from pathlib import Path

URL = "https://ollama.com/api/generate"
MODEL = "gpt-oss:120b"
env_keys = os.environ.get("BIGMODEL_API_KEY", "")
API_KEYS = [k.strip() for k in env_keys.split(",") if k.strip()] if env_keys else []

FOOTER_PAGES = {
    "about.html": "Professional and engaging 'About Us' page for bakidou.org, a high-end Baki manga portal.",
    "contact.html": "Professional 'Contact Us' page. Email: contact@bakidou.org. Address: Virtual Headquarters in the Underground Arena.",
    "privacy-policy.html": "Standard modern Privacy Policy for a manga website. Focus on user data, cookies, and high security.",
    "dmca.html": "Strict and professional DMCA Notice and Takedown Policy for bakidou.org. Email for notices: contact@bakidou.org.",
    "terms-of-service.html": "Terms of Service for a manga reader site. User conduct, intellectual property, and limitations of liability.",
    "cookies-policy.html": "Cookies Policy explaining what cookies we use for performance and personalization.",
    "disclaimer.html": "Disclaimer stating that we do not host files on our servers and are a portal for fan-translation enthusiasts."
}

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Bakidou.org</title>
    <script src="https://unpkg.com/@tailwindcss/browser@4"></script>
    <link href="https://fonts.googleapis.com/css2?family=Bangers&family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #dc143c;
            --accent: #ffd700;
            --bg: #050505;
        }}
        body {{ 
            background: var(--bg); 
            color: #fff; 
            font-family: 'Inter', sans-serif; 
            line-height: 1.6;
            background-image: radial-gradient(circle at 50% 10%, rgba(220, 20, 60, 0.05) 0%, transparent 50%);
        }}
        .bangers {{ font-family: 'Bangers', sans-serif; }}
        .glass {{ 
            background: rgba(255, 255, 255, 0.02); 
            border: 1px solid rgba(255, 255, 255, 0.05); 
            backdrop-filter: blur(20px); 
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
        .hero-text {{
            background: linear-gradient(180deg, #fff 0%, rgba(255,255,255,0.4) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .gradient-border {{
            position: relative;
            border-radius: 1rem;
            padding: 1px;
            background: linear-gradient(to bottom right, rgba(220, 20, 60, 0.2), rgba(255, 255, 255, 0.05));
        }}
        .content-area p {{ margin-bottom: 1.5rem; color: rgba(255,255,255,0.8); }}
        .content-area h2 {{ font-family: 'Bangers', sans-serif; font-size: 2rem; margin-top: 2.5rem; margin-bottom: 1rem; color: #fff; text-transform: uppercase; letter-spacing: 0.1em; }}
        .content-area strong {{ color: var(--primary); }}
    </style>
</head>
<body class="min-h-screen">
    <nav class="p-6 md:p-12">
        <a href="index.html" class="group flex items-center gap-4 text-[10px] font-black uppercase tracking-[0.3em] text-white/40 hover:text-white transition">
            <span class="w-8 h-[1px] bg-white/20 group-hover:w-12 group-hover:bg-[var(--primary)] transition-all"></span>
            Return to Universe
        </a>
    </nav>

    <main class="max-w-4xl mx-auto px-6 pb-24">
        <header class="mb-16">
            <div class="text-[var(--primary)] font-black uppercase tracking-[0.5em] text-[10px] mb-4">Internal Protocol // {header_tag}</div>
            <h1 class="text-6xl md:text-8xl bangers uppercase hero-text leading-none">{title}</h1>
        </header>

        <div class="gradient-border">
            <div class="glass p-8 md:p-12 rounded-2xl content-area">
                {content}
            </div>
        </div>

        <footer class="mt-24 text-center">
            <p class="text-[10px] text-white/20 uppercase tracking-[0.2em] font-bold">&copy; 2024 Bakidou.org - Transcending the Arena.</p>
        </footer>
    </main>
</body>
</html>"""

async def generate_page_content(session, api_key, title, prompt_desc):
    prompt = f"""
    Title: {title}
    Task: {prompt_desc}
    
    Format:
    - Use <h2> for subheadings.
    - Use <p> for paragraphs.
    - Use <strong> for emphasis.
    - Professional tone.
    - NO JSON, NO Markdown, ONLY the HTML snippet for the content.
    - For bakidou.org website.
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
    
    try:
        async with session.post(URL, headers=headers, json=payload, timeout=60) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("response", "")
            else:
                print(f"Error {response.status} for {title}")
                return None
    except Exception as e:
        print(f"Exception for {title}: {str(e)}")
        return None

async def main():
    if not API_KEYS:
        print("No API keys found in environment variables. Please set BIGMODEL_API_KEY.")
        return
    async with aiohttp.ClientSession() as session:
        for i, (filename, desc) in enumerate(FOOTER_PAGES.items()):
            title = filename.replace(".html", "").replace("-", " ").title()
            if "Dmca" in title: title = "DMCA Notice"
            
            # Using specific header tags for aesthetic
            header_tags = ["IDENTITY", "COMMUNICATIONS", "SECURITY", "LEGAL", "TERMS", "PROTOCOL", "ADVISORY"]
            
            print(f"Building {filename}...")
            content = await generate_page_content(session, API_KEYS[i % len(API_KEYS)], title, desc)
            
            if content:
                final_html = PAGE_TEMPLATE.format(
                    title=title,
                    header_tag=header_tags[i % len(header_tags)],
                    content=content
                )
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(final_html)
                print(f"Generated {filename}")
            else:
                print(f"FAILED to generate {filename}")

if __name__ == "__main__":
    asyncio.run(main())
