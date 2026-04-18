import os
from tavily import TavilyClient


def ground(hypothesis: str, max_results: int = 8) -> list[dict]:
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    res = client.search(query=hypothesis, search_depth="basic", max_results=max_results)
    return [
        {"n": i + 1, "title": r["title"], "url": r["url"], "snippet": r["content"]}
        for i, r in enumerate(res.get("results", []))
    ]


def format_pack(pack: list[dict]) -> str:
    lines = []
    for item in pack:
        lines.append(f"[{item['n']}] {item['title']}\n    {item['url']}\n    {item['snippet']}")
    return "\n\n".join(lines)
