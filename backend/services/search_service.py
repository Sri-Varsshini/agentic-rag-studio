from config import settings


def web_search(query: str) -> str:
    if not settings.search_api_key:
        return "Web search is not configured. Set SEARCH_API_KEY in .env."

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.search_api_key)
        response = client.search(query=query, max_results=5)

        results = response.get("results", [])
        if not results:
            return "No web search results found."

        lines = []
        for r in results:
            lines.append(f"**{r.get('title', 'No title')}**")
            lines.append(r.get("content", ""))
            lines.append(f"Source: {r.get('url', '')}")
            lines.append("")

        return "\n".join(lines)
    except Exception as e:
        print(f"[search_service] error: {e}")
        return f"Web search failed: {str(e)}"
