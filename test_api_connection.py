import asyncio
import aiohttp
import json
import os
from pathlib import Path

# Use values from the main script
URL = "https://ollama.com/api/generate"
MODEL = "gpt-oss:120b"
import os
# API keys are loaded from environment variables for security
env_keys = os.environ.get("BIGMODEL_API_KEY", "")
API_KEYS = [k.strip() for k in env_keys.split(",") if k.strip()] if env_keys else []

async def test_one():
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {API_KEYS[0]}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL,
            "prompt": "Hello test prompt. Respond with the word 'SUCCESS' if you get this.",
            "stream": False
        }
        try:
            print(f"Connecting to {URL}...")
            async with session.post(URL, headers=headers, json=payload, timeout=10) as response:
                print(f"Status: {response.status}")
                text = await response.text()
                print(f"Response: {text[:500]}")
        except Exception as e:
            print(f"FAIL: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_one())
