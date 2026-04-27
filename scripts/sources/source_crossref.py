"""CrossRef 数据源 - 开放 API，无需 Key

CrossRef 是全球最大的 DOI 注册机构，覆盖绝大多数正式出版的学术论文。
API 完全免费开放，支持按关键词、作者、DOI 搜索。
提供 polite pool（配置 email 后速率限制更宽松）。

文档：https://api.crossref.org/swagger-ui/index.html
"""
from __future__ import annotations
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.schema import Paper, SearchResult
from lib.http_client import get_json
from lib.utils import env_get

SEARCH_URL = "https://api.crossref.org/works"


def is_available() -> bool:
    """CrossRef 公开 API，始终可用"""
    return True


def search(query: str, limit: int = 20) -> SearchResult:
    """搜索 CrossRef"""
    params = {
        "query": query,
        "rows": str(min(limit, 50)),
        "sort": "relevance",
        "order": "desc",
    }
    # 配置 email 进入 polite pool，速率限制更宽松
    email = env_get("CROSSREF_EMAIL")
    if email:
        params["mailto"] = email

    try:
        data = get_json(SEARCH_URL, params=params, timeout=20)
        message = data.get("message", {})
        items = message.get("items", [])

        papers: list[Paper] = []
        for item in items[:limit]:
            # 标题
            titles = item.get("title", [])
            title = titles[0] if titles else ""

            # 作者
            authors: list[str] = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                name = f"{given} {family}".strip()
                if name:
                    authors.append(name)

            # 年份
            year = 0
            date_parts = (
                item.get("published-print", {}).get("date-parts")
                or item.get("published-online", {}).get("date-parts")
                or item.get("created", {}).get("date-parts")
            )
            if date_parts and date_parts[0]:
                year = date_parts[0][0]

            # 期刊
            venue_list = item.get("container-title", [])
            venue = venue_list[0] if venue_list else ""

            # DOI
            doi = item.get("DOI", "")
            url = f"https://doi.org/{doi}" if doi else item.get("URL", "")

            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    year=year,
                    url=url,
                    source="CrossRef",
                    venue=venue,
                    doi=doi,
                    citation_count=item.get("is-referenced-by-count", 0),
                    language="en",
                )
            )

        return SearchResult(
            query=query,
            source="CrossRef",
            papers=papers,
            total_found=message.get("total-results", len(papers)),
        )
    except Exception as e:
        return SearchResult(query=query, source="CrossRef", error=str(e))


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "deconstruction Chinese literature Benjamin"
    result = search(q)
    print(result.to_json())
