
import os
import json
import http.client
import urllib.parse
import random

# Configuration
CONFIG_PATH = "ollama_api.json"
PORTAL_FILES = {
    "index.html": "Grappler Baki",
    "baki.html": "Baki",
    "son-of-ogre.html": "Baki - Son Of Ogre",
    "baki-dou-2018.html": "Baki-Dou (2018)",
    "golden-kamui.html": "Golden Kamui"
}

def get_api_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file {CONFIG_PATH} not found.")
        
    with open(CONFIG_PATH, "r") as f:
        content = f.read()
        
    # Extract values using regex or split for the custom format
    try:
        url = content.split('URL = "')[1].split('"')[0]
        model = content.split('MODEL = "')[1].split('"')[0]
        keys_block = content.split('API_KEYS = [')[1].split(']')[0]
        api_keys = [k.strip().strip('"').strip("'") for k in keys_block.split(",") if k.strip()]
        return url, model, api_keys
    except Exception as e:
        print(f"Error parsing config: {e}")
        # Fallback to hardcoded if necessary or fail
        raise

def generate_seo_content(series_name, url, model, api_key):
    print(f"Generating POWERFUL SEO content for {series_name}...")
    
    prompt = f"""
    Write a definitive, high-authority, and emotionally charged SEO article about the legendary manga '{series_name}'. 
    This is for a premium fan portal. The tone should be epic, insightful, and professional.
    
    Structure:
    1. A magnetic H2 title (e.g., "The Absolute Legend of {series_name}: Why It Redefined the Genre").
    2. An opening hook that captures the visceral intensity of the series.
    3. Deep dive into the "Art of Combat": Discuss the unique, distorted, yet hyper-realistic art style of Keisuke Itagaki (or Satoru Noda for Golden Kamui).
    4. "The Philosophy of Strength": Explore the character motivations, specifically focusing on the Hanma legacy or the survival stakes in Golden Kamui.
    5. "Immersive Experience": Mention why reading this series in High Definition on a dedicated portal is the only way to experience the raw power of the panels.
    6. A concluding punch that leaves the reader ready to start chapter 1.
    
    SEO Requirements:
    - Seamlessly integrate keywords like "Read {series_name} Online", "High Definition Manga", "Combat Realism", and "Manga Masterpiece".
    - Use HTML format ONLY.
    - Wrap everything in a <section class="seo-section">.
    - Use <h2> for the main title.
    - Use multiple <p> paragraphs for readability.
    - Use <strong> for emphasis on characters and key terms.
    - Do NOT mention links or site URLs, just the experience.
    - Format must be valid HTML. No intro/outro text.
    """

    parsed_url = urllib.parse.urlparse(url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        conn.request("POST", parsed_url.path, payload, headers)
        res = conn.getresponse()
        if res.status != 200:
            print(f"API Error {res.status}: {res.read().decode()}")
            return ""
            
        data = res.read()
        response_json = json.loads(data.decode("utf-8"))
        return response_json.get("response", "").strip()
    except Exception as e:
        print(f"Error generating for {series_name}: {e}")
        return ""

def inject_seo_content(filename, new_content):
    if not new_content:
        return
        
    with open(filename, "r", encoding="utf-8") as f:
        html = f.read()
        
    injection_marker = "<!-- SEO_CONTENT_INJECTION_POINT -->"
    injected_marker = "<!-- SEO_CONTENT_INJECTED -->"
    
    # If already injected, we replace it. If not, we look for the injection point.
    if injected_marker in html:
        print(f"Found existing SEO content in {filename}, overwriting...")
        start_idx = html.find(injected_marker)
        # Search for the end of the section
        end_idx = html.find("</section>", start_idx) + len("</section>")
        
        if start_idx != -1 and end_idx != -1:
            header = "<!-- SEO_CONTENT_INJECTED -->"
            new_block = f"{header}\n{new_content}"
            new_html = html[:start_idx] + new_block + html[end_idx:]
        else:
            print(f"Could not find end of section in {filename}, skipping overwrite.")
            return
    elif injection_marker in html:
        header = "<!-- SEO_CONTENT_INJECTED -->"
        new_block = f"{header}\n{new_content}"
        new_html = html.replace(injection_marker, new_block)
    else:
        print(f"No injection marker found in {filename}")
        return
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"Successfully updated/injected SEO content in {filename}")

def main():
    try:
        url, model, keys = get_api_config()
    except Exception as e:
        print(f"Failed to read config: {e}")
        return

    # Use keys in rotation if one fails
    for filename, series_name in PORTAL_FILES.items():
        if not os.path.exists(filename):
            print(f"File {filename} not found, skipping.")
            continue
            
        success = False
        random.shuffle(keys) # Shuffle to distribute load
        
        for api_key in keys:
            seo_html = generate_seo_content(series_name, url, model, api_key)
            if seo_html:
                # Basic validation: check if it contains the required tag
                if "<section" in seo_html:
                    inject_seo_content(filename, seo_html)
                    success = True
                    break
                else:
                    print(f"Invalid content received for {series_name}, retrying with next key...")
            else:
                print(f"Failed to generate with key {api_key[:8]}..., trying next...")
        
        if not success:
            print(f"CRITICAL: Failed to generate POWERFUL portal SEO for {series_name} after trying all available keys.")

if __name__ == "__main__":
    main()
