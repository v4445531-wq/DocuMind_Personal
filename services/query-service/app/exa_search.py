"""Exa web search fallback — used when no relevant context is found in user documents.

When DocuMind cannot answer from uploaded documents, instead of a plain refusal
it falls back to Exa to search the web and returns labelled web results alongside
the refusal so the user gets useful context either way.

Disabled automatically when EXA_API_KEY is not set (no crash, just no fallback).
"""
from __future__ import annotations

import httpx

from app.config import settings
from documind_common.logging import get_logger

log = get_logger(__name__)

EXA_SEARCH_URL = "https://api.exa.ai/search"
_NUM_RESULTS = 3


async def exa_web_search(query: str) -> list[dict]:
    """Return up to _NUM_RESULTS web results from Exa for the given query.

    Returns an empty list if EXA_API_KEY is not configured or the request fails.
    Each result is a dict with keys: title, url, snippet.
    """
    if not settings.exa_api_key:
        return []

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                EXA_SEARCH_URL,
                headers={"x-api-key": settings.exa_api_key, "Content-Type": "application/json"},
                json={
                    "query": query,
                    "numResults": _NUM_RESULTS,
                    "useAutoprompt": True,
                    "contents": {"text": {"maxCharacters": 400}},
                },
            )
            response.raise_for_status()
            data = response.json()
            results = []
            for r in data.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": (r.get("text") or r.get("summary") or "")[:400],
                })
            log.info("exa_search_ok", query=query, hits=len(results))
            return results
    except Exception as exc:
        log.warning("exa_search_failed", error=str(exc))
        return []


def format_exa_results(results: list[dict]) -> str:
    """Format Exa results into a readable string appended to the refusal message."""
    if not results:
        return ""
    lines = ["\n\n---\n**Web results (via Exa):**\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. **{r['title']}**")
        if r["snippet"]:
            lines.append(f"   {r['snippet']}")
        lines.append(f"   {r['url']}\n")
    return "\n".join(lines)
