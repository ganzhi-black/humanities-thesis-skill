"""OpenAlex 数据源 - 完全免费开放 API

OpenAlex 是目前最大的开放学术数据库，索引了 2.5 亿+ 篇论文，
由非营利组织 OurResearch 运营，可视为 Scopus / Web of Science 的免费替代品。

API 文档：https://docs.openalex.org/
无需 API Key（可选配置 email 进入 polite pool 提高速率）。
"""
from __future__ import annotations
import sys, os, re, json
import urllib.request
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.schema import Paper, SearchResult
from lib.utils import env_get

SEARCH_URL = "https://api.openalex.org/works"


def is_available() -> bool:
    """OpenAlex 完全免费，始终可用"""
    return True


def search(query: str, limit: int = 20) -> SearchResult:
    """搜索 OpenAlex"""
    params = {
        "search": query,
        "per_page": str(min(limit, 50)),
        "sort": "relevance_score:desc",
    }
    # 配置 email 进入 polite pool（速率更快更稳定）
    email = env_get("OPENALEX_EMAIL")
    if email:
        params["mailto"] = email

    url = SEARCH_URL + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "humanities-thesis-skill/1.0"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        papers: list[Paper] = []
        for item in data.get("results", [])[:limit]:
            # 标题
            title = item.get("title") or ""

            # 作者
            authors = []
            for authorship in item.get("authorships", []):
                author = authorship.get("author", {})
                name = author.get("display_name", "")
                if name:
                    authors.append(name)

            # 年份
            year = item.get("publication_year") or 0

            # DOI 和 URL
            doi = item.get("doi") or ""
            if doi and doi.startswith("https://doi.org/"):
                doi = doi.replace("https://doi.org/", "")
            url_paper = item.get("doi") or item.get("id", "")

            # 期刊
            venue = ""
            primary_loc = item.get("primary_location") or {}
            source = primary_loc.get("source") or {}
            venue = source.get("display_name") or ""

            # 摘要（OpenAlex 返回 abstract_inverted_index，需要还原）
            abstract = ""
            abs_idx = item.get("abstract_inverted_index")
            if abs_idx and isinstance(abs_idx, dict):
                try:
                    word_positions = []
                    for word, positions in abs_idx.items():
                        for pos in positions:
                            word_positions.append((pos, word))
                    word_positions.sort()
                    abstract = " ".join(w for _, w in word_positions)
                    if len(abstract) > 500:
                        abstract = abstract[:500] + "..."
                except Exception:
                    abstract = ""

            # 引用次数
            citation_count = item.get("cited_by_count") or 0

            # 语言
            language = item.get("language") or ""

            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    year=year,
                    url=url_paper,
                    source="OpenAlex",
                    venue=venue,
                    abstract=abstract,
                    doi=doi,
                    citation_count=citation_count,
                    language=language if language else "en",
                )
            )

        total = data.get("meta", {}).get("count", len(papers))
        return SearchResult(
            query=query, source="OpenAlex", papers=papers, total_found=total
        )
    except Exception as e:
        return SearchResult(query=query, source="OpenAlex", error=str(e))


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "trauma narrative Chinese literature"
    result = search(q)
    print(result.to_json())
