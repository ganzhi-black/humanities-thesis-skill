"""Google Scholar 数据源 - 通过 SerpAPI 或直接抓取

优先使用 SerpAPI（需要 API Key，推荐），回退到直接抓取（容易被反爬）。

配置方式：
  - 推荐：设置环境变量 SERPAPI_KEY（从 https://serpapi.com 获取免费 Key）
  - 回退：不配置任何 Key，直接抓取（不稳定，仅供测试）
"""
from __future__ import annotations
import sys, os, re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.schema import Paper, SearchResult
from lib.http_client import get_text, get_json
from lib.utils import env_get, parse_year

SERPAPI_URL = "https://serpapi.com/search"
SCHOLAR_URL = "https://scholar.google.com/scholar"


def is_available() -> bool:
    """SerpAPI 或直接抓取均可用"""
    return True


def search(query: str, limit: int = 20) -> SearchResult:
    """搜索 Google Scholar"""
    serpapi_key = env_get("SERPAPI_KEY")
    if serpapi_key:
        return _search_via_serpapi(query, limit, serpapi_key)
    return _search_direct(query, limit)


def _search_via_serpapi(query: str, limit: int, api_key: str) -> SearchResult:
    """通过 SerpAPI 搜索（稳定、推荐）"""
    params = {
        "engine": "google_scholar",
        "q": query,
        "num": str(min(limit, 20)),
        "api_key": api_key,
        "hl": "zh-CN",
    }
    try:
        data = get_json(SERPAPI_URL, params=params, timeout=20)
        papers: list[Paper] = []
        for item in data.get("organic_results", [])[:limit]:
            authors = []
            pub_info = item.get("publication_info", {})
            author_str = pub_info.get("summary", "")
            if " - " in author_str:
                author_part = author_str.split(" - ")[0]
                authors = [a.strip() for a in author_part.split(",") if a.strip()]

            year = 0
            year_match = re.search(r"(19|20)\d{2}", pub_info.get("summary", ""))
            if year_match:
                year = int(year_match.group())

            venue = ""
            if " - " in author_str:
                parts = author_str.split(" - ")
                if len(parts) >= 2:
                    venue = parts[1].strip().rstrip(",").strip()

            cited_by = item.get("inline_links", {}).get("cited_by", {})
            citation_count = cited_by.get("total", 0) if isinstance(cited_by, dict) else 0

            papers.append(
                Paper(
                    title=item.get("title", ""),
                    authors=authors,
                    year=year,
                    url=item.get("link", ""),
                    source="Google Scholar",
                    venue=venue,
                    abstract=item.get("snippet", ""),
                    citation_count=citation_count,
                    language="en",
                )
            )
        return SearchResult(
            query=query,
            source="Google Scholar (SerpAPI)",
            papers=papers,
            total_found=data.get("search_information", {}).get("total_results", len(papers)),
        )
    except Exception as e:
        return SearchResult(query=query, source="Google Scholar (SerpAPI)", error=str(e))


def _search_direct(query: str, limit: int) -> SearchResult:
    """直接抓取 Google Scholar（不稳定，可能被反爬）"""
    params = {
        "q": query,
        "num": str(min(limit, 10)),
        "hl": "zh-CN",
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    try:
        html = get_text(SCHOLAR_URL, params=params, headers=headers, timeout=15)
        if not html:
            return SearchResult(query=query, source="Google Scholar", error="返回内容为空")
        if "unusual traffic" in html.lower() or "captcha" in html.lower():
            return SearchResult(
                query=query,
                source="Google Scholar",
                error="被 Google 反爬机制拦截，建议配置 SERPAPI_KEY 使用 SerpAPI",
            )
        papers = _parse_scholar_html(html)
        return SearchResult(
            query=query, source="Google Scholar", papers=papers, total_found=len(papers)
        )
    except Exception as e:
        return SearchResult(query=query, source="Google Scholar", error=str(e))


def _parse_scholar_html(html: str) -> list[Paper]:
    """解析 Google Scholar 搜索结果"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    soup = BeautifulSoup(html, "html.parser")
    papers: list[Paper] = []

    for item in soup.select("div.gs_r.gs_or.gs_scl"):
        title_el = item.select_one("h3.gs_rt a")
        if not title_el:
            title_el = item.select_one("h3.gs_rt")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        url = title_el.get("href", "") if title_el.name == "a" else ""

        authors: list[str] = []
        year = 0
        venue = ""
        info_el = item.select_one("div.gs_a")
        if info_el:
            info_text = info_el.get_text(strip=True)
            parts = info_text.split(" - ")
            if parts:
                authors = [a.strip() for a in parts[0].split(",") if a.strip() and "…" not in a]
            if len(parts) >= 2:
                venue = parts[1].strip().rstrip(",").strip()
            year = parse_year(info_text)

        abstract = ""
        abs_el = item.select_one("div.gs_rs")
        if abs_el:
            abstract = abs_el.get_text(strip=True)

        citation_count = 0
        cited_el = item.select_one("a[href*='cites']")
        if cited_el:
            cited_text = cited_el.get_text(strip=True)
            num_match = re.search(r"\d+", cited_text)
            if num_match:
                citation_count = int(num_match.group())

        papers.append(
            Paper(
                title=title,
                authors=authors,
                year=year,
                url=url,
                source="Google Scholar",
                venue=venue,
                abstract=abstract,
                citation_count=citation_count,
                language="en",
            )
        )

    return papers


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "trauma narrative Chinese literature"
    result = search(q)
    print(result.to_json())
