"""国家哲学社会科学文献中心 (NCPSSD) 数据源

国家哲学社会科学文献中心是由中国社会科学院图书馆承建的国家级公益性
开放获取平台，收录 2,400+ 种中文社科核心期刊、2,300 万+ 篇论文，
全部免费在线阅读和下载。对人文社科研究极为重要。

网址：https://www.ncpssd.cn/
无公开 API，通过网页搜索接口获取结果。
"""
from __future__ import annotations
import sys, os, re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.schema import Paper, SearchResult
from lib.http_client import get_text
from lib.utils import parse_year

SEARCH_URL = "https://www.ncpssd.cn/Literature/search"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.ncpssd.cn/",
}


def is_available() -> bool:
    """NCPSSD 公开访问，无需配置"""
    return True


def search(query: str, limit: int = 20) -> SearchResult:
    """搜索国家哲学社会科学文献中心

    注意：NCPSSD 没有公开 REST API，此脚本通过模拟网页搜索获取结果。
    如果网站结构变动，解析可能失败。失败时会返回带 error 的结果，
    并建议用户直接访问 https://www.ncpssd.cn/ 手动搜索。
    """
    params = {
        "keyword": query,
        "pageNum": "1",
        "pageSize": str(min(limit, 20)),
    }

    try:
        html = get_text(SEARCH_URL, params=params, headers=_HEADERS, timeout=15)
        if not html:
            return SearchResult(
                query=query,
                source="国家哲社文献中心",
                error="返回为空，请直接访问 https://www.ncpssd.cn/ 搜索",
            )

        papers = _parse_results(html)

        if not papers:
            return SearchResult(
                query=query,
                source="国家哲社文献中心",
                papers=[],
                total_found=0,
                error=(
                    "未解析到结果（可能是页面结构变动或无匹配文献）。"
                    "建议直接访问 https://www.ncpssd.cn/ 手动搜索。"
                ),
            )

        return SearchResult(
            query=query,
            source="国家哲社文献中心",
            papers=papers,
            total_found=len(papers),
        )
    except Exception as e:
        return SearchResult(
            query=query,
            source="国家哲社文献中心",
            error=f"{e}。建议直接访问 https://www.ncpssd.cn/ 搜索。",
        )


def _parse_results(html: str) -> list[Paper]:
    """解析 NCPSSD 搜索结果"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    soup = BeautifulSoup(html, "html.parser")
    papers: list[Paper] = []

    # NCPSSD 的搜索结果通常在列表项中
    items = (
        soup.select("div.article-list div.article-item")
        or soup.select("ul.article-list li")
        or soup.select("div.search-result-list div.result-item")
        or soup.select("div.list-item")
    )

    for item in items:
        # 标题
        title_el = (
            item.select_one("h3 a")
            or item.select_one("a.title")
            or item.select_one("div.title a")
            or item.select_one("a[href*='Literature']")
        )
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title:
            continue

        url = title_el.get("href", "")
        if url and not url.startswith("http"):
            url = "https://www.ncpssd.cn" + url

        # 作者
        authors: list[str] = []
        author_el = item.select_one("span.author") or item.select_one("div.author")
        if author_el:
            # 多个作者可能用 a 标签或逗号/分号分隔
            a_tags = author_el.select("a")
            if a_tags:
                authors = [a.get_text(strip=True) for a in a_tags if a.get_text(strip=True)]
            else:
                text = author_el.get_text(strip=True)
                authors = [a.strip() for a in re.split(r"[,;，；、]", text) if a.strip()]

        # 年份
        year = 0
        date_el = item.select_one("span.date") or item.select_one("span.year")
        if date_el:
            year = parse_year(date_el.get_text(strip=True))
        if not year:
            year = parse_year(item.get_text())

        # 期刊
        venue = ""
        source_el = (
            item.select_one("span.source a")
            or item.select_one("span.journal")
            or item.select_one("a.source")
        )
        if source_el:
            venue = source_el.get_text(strip=True)

        # 摘要
        abstract = ""
        abs_el = item.select_one("div.abstract") or item.select_one("p.summary")
        if abs_el:
            abstract = abs_el.get_text(strip=True)

        # 关键词
        keywords: list[str] = []
        kw_el = item.select_one("span.keywords") or item.select_one("div.keywords")
        if kw_el:
            keywords = [k.strip() for k in re.split(r"[,;，；]", kw_el.get_text()) if k.strip()]

        papers.append(
            Paper(
                title=title,
                authors=authors,
                year=year,
                url=url,
                source="国家哲社文献中心",
                venue=venue,
                abstract=abstract,
                keywords=keywords,
                language="zh",
            )
        )

    return papers


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "鲁迅 创伤叙事"
    result = search(q)
    print(result.to_json())
