"""Semantic Scholar 数据源 - 开放 API，无需 Key

Semantic Scholar 由 Allen AI 提供，拥有免费公开 API，
覆盖 2 亿+ 篇学术论文，适合英文文献搜索。
免费层限制：100 次/5 分钟。

文档：https://api.semanticscholar.org/
"""
from __future__ import annotations
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.schema import Paper, SearchResult
from lib.http_client import get_json
from lib.utils import env_get

SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def is_available() -> bool:
    """Semantic Scholar 公开 API，始终可用"""
    return True


def search(query: str, limit: int = 20) -> SearchResult:
    """搜索 Semantic Scholar"""
    params = {
        "query": query,
        "limit": str(min(limit, 100)),
        "fields": "title,authors,year,url,venue,abstract,citationCount,externalIds",
    }
    headers = {}
    # 可选：配置 API Key 提高速率限制
    api_key = env_get("S2_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    try:
        data = get_json(SEARCH_URL, params=params, headers=headers, timeout=15)
        papers: list[Paper] = []

        for item in data.get("data", [])[:limit]:
            authors = [
                a.get("name", "") for a in item.get("authors", []) if a.get("name")
            ]

            doi = ""
            ext_ids = item.get("externalIds") or {}
            if isinstance(ext_ids, dict):
                doi = ext_ids.get("DOI", "")

            url = item.get("url", "")
            if not url and doi:
                url = f"https://doi.org/{doi}"

            papers.append(
                Paper(
                    title=item.get("title", ""),
                    authors=authors,
                    year=item.get("year") or 0,
                    url=url,
                    source="Semantic Scholar",
                    venue=item.get("venue", ""),
                    abstract=item.get("abstract") or "",
                    doi=doi,
                    citation_count=item.get("citationCount") or 0,
                    language="en",
                )
            )

        return SearchResult(
            query=query,
            source="Semantic Scholar",
            papers=papers,
            total_found=data.get("total", len(papers)),
        )
    except Exception as e:
        return SearchResult(query=query, source="Semantic Scholar", error=str(e))


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "trauma narrative modern Chinese literature"
    result = search(q)
    print(result.to_json())
