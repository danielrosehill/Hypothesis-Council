import json
import os
import httpx
from .config import OPENROUTER_URL


def call(model: str, system: str, user: str, timeout: float = 120.0) -> str:
    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/danielrosehill/Hypothesis-Council",
        "X-Title": "Hypothesis-Council",
    }
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.4,
    }
    r = httpx.post(OPENROUTER_URL, headers=headers, json=body, timeout=timeout)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_json(model: str, system: str, user: str) -> dict:
    raw = call(model, system, user)
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object in response from {model}: {raw[:200]}")
    return json.loads(raw[start : end + 1])
