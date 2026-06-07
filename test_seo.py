import asyncio
import aiohttp
from pathlib import Path
import os

# TEST CONFIG
URL = "https://ollama.com/api/generate"
MODEL = "gpt-oss:120b"
import os
# API keys are loaded from environment variables for security
env_keys = os.environ.get("BIGMODEL_API_KEY", "")
API_KEYS = [k.strip() for k in env_keys.split(",") if k.strip()] if env_keys else []

async def test():
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": MODEL,
            "prompt": "Write a 50-word test summary for Baki Chapter 100 in HTML format. NO Markdown. Only <h2> and <p> tags.",
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {API_KEYS[0]}",
            "Content-Type": "application/json"
        }
        try:
            async with session.post(URL, headers=headers, json=payload, timeout=30) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("Generated Content:")
                    print(data.get("response", ""))
                else:
                    text = await response.text()
                    print(f"Error: {text}")
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test())
