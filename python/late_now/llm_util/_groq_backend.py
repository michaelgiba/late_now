import time

import requests
import os

_GROQ_APIKEY = os.environ.get("GROQ_API_KEY")


def completion(prompt: str, system_prompt: str, temperature: float) -> str:
    time.sleep(5.0)
    result = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_GROQ_APIKEY}",
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 4096,
            "temperature": temperature,
        },
    )
    return result.json()
