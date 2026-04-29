"""万方数据 (Wanfang) 数据源

万方提供了部分公开的搜索接口，不需要登录即可获取基本搜索结果。
高级功能（全文下载等）需要机构账号。
"""
from __future__ import annotations
import sys, os, re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.schema import Paper, SearchResult
from lib.http_client import get_text
from lib.utils import parse_year

SEARCH_URL = "https://s.wanfangdata.com.cn/paper"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.wanfangdata.com.cn/",
}


def is_available() -> bool:
    """万方公开搜索不需要额外配置"""
    return True


def search(query: str, limit: int = 20) -> SearchResult:
    """搜索万方数据"""
    params = {
        "q": query,
        "style": "detail",
        "page": "1",
        "size": str(min(limit, 20)),
    }
    try:
        html = get_text(SEARCH_URL, params=params, headers=_HEADERS, timeout=15)
        if not html:
            return SearchResult(query=query, source="万方", error="返回内容为空")
        papers = _parse_results(html)
        return SearchResult(
            query=query, source="万方", papers=papers, total_found=len(papers)
        )
    except Exception as e:
        return SearchResult(query=query, source="万方", error=str(e))


def _parse_results(html: str) -> list[Paper]:
    """解析万方搜索结果"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    soup = BeautifulSoup(html, "html.parser")
    papers: list[Paper] = []

    items = soup.select("div.normal-list") or soup.select("div.result-item")
    for item in items:
        # 标题
        title_el = item.select_one("a.title") or item.select_one("h3 a")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title:
            continue

        url = title_el.get("href", "")
        if url and not url.startswith("http"):
            url = "https://s.wanfangdata.com.cn" + url

        # 作者
        authors: list[str] = []
        author_el = item.select_one("span.author") or item.select_one(".author")
        if author_el:
            for a_tag in author_el.select("a"):
                name = a_tag.get_text(strip=True)
                if name:
                    authors.append(name)

        # 年份
        year = 0
        date_el = item.select_one("span.year") or item.select_one(".date")
        if date_el:
            year = parse_year(date_el.get_text(strip=True))
        if not year:
            # 从完整文本中尝试提取
            year = parse_year(item.get_text())

        # 期刊
        venue = ""
        source_el = item.select_one("span.source a") or item.select_one(".periodical a")
        if source_el:
            venue = source_el.get_text(strip=True)

        # 摘要
        abstract = ""
        abs_el = item.select_one("div.abstract") or item.select_one(".summary")
        if abs_el:
            abstract = abs_el.get_text(strip=True)

        papers.append(
            Paper(
                title=title,
                authors=authors,
                year=year,
                url=url,
                source="万方",
                venue=venue,
                abstract=abstract,
                language="zh",
            )
        )

    return papers


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "鲁迅 创伤叙事"
    result = search(q)
    print(result.to_json())
