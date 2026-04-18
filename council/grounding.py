import os
import re

import httpx

from .config import OPENROUTER_URL


def _strip_md(s: str) -> str:
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    s = re.sub(r"^\s*[-*]\s+", "• ", s, flags=re.MULTILINE)
    s = re.sub(r"^#+\s*", "", s, flags=re.MULTILINE)
    return s


def _tavily(hypothesis: str, max_results: int) -> list[dict]:
    from tavily import TavilyClient

    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    res = client.search(query=hypothesis, search_depth="basic", max_results=max_results)
    return [
        {"n": i + 1, "title": r["title"], "url": r["url"], "snippet": r["content"]}
        for i, r in enumerate(res.get("results", []))
    ]


def _sonar(hypothesis: str, max_results: int) -> list[dict]:
    """Perplexity `sonar` via OpenRouter. Returns the briefing as item 1
    and citation URLs as subsequent items."""
    body = {
        "model": "perplexity/sonar",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a neutral news briefer. Given a hypothesis or claim, "
                    "produce a factual context pack covering recent relevant "
                    "developments, key actors, current state, and any relevant "
                    "counter-narratives in reporting. Write in plain prose — no "
                    "markdown formatting, no bullet lists, no bold or headers. "
                    "No opinion, no probability estimates. Aim for 400-600 words."
                ),
            },
            {"role": "user", "content": hypothesis},
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
    }
    r = httpx.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/danielrosehill/Hypothesis-Council",
            "X-Title": "Hypothesis-Council",
        },
        json=body,
        timeout=90.0,
    )
    r.raise_for_status()
    data = r.json()
    summary = _strip_md(data["choices"][0]["message"]["content"])
    citations = data.get("citations") or []

    pack: list[dict] = [
        {"n": 1, "title": "Perplexity Sonar briefing", "url": "", "snippet": summary}
    ]
    for i, c in enumerate(citations[: max_results - 1], start=2):
        if isinstance(c, str):
            url, title = c, c
        else:
            url = c.get("url", "")
            title = c.get("title") or url
        pack.append({"n": i, "title": title, "url": url, "snippet": ""})
    return pack


def ground(hypothesis: str, max_results: int = 8, source: str | None = None) -> list[dict]:
    source = source or os.environ.get("GROUNDING_SOURCE", "sonar")
    if source == "tavily":
        return _tavily(hypothesis, max_results)
    if source == "sonar":
        return _sonar(hypothesis, max_results)
    raise ValueError(f"unknown grounding source: {source}")


def format_pack(pack: list[dict]) -> str:
    lines = []
    for item in pack:
        header = f"[{item['n']}] {item['title']}"
        if item.get("url"):
            header += f"\n    {item['url']}"
        if item.get("snippet"):
            header += f"\n    {item['snippet']}"
        lines.append(header)
    return "\n\n".join(lines)
