import requests
import os

_OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def completion(prompt: str, system_prompt: str, temperature: float) -> str:
    result = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_OPENAI_API_KEY}",
        },
        json={
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": 1024,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        },
    )
    print(result.json())
    return result.json()
