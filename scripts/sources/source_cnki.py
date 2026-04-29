"""知网 CNKI 数据源 - 需要 Cookie 配置

使用方式：
  1. 在浏览器中登录知网 (https://kns.cnki.net)
  2. 从浏览器开发者工具中复制 Cookie
  3. 设置环境变量 CNKI_COOKIE 或写入 scripts/.env 文件
"""
from __future__ import annotations
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.schema import Paper, SearchResult
from lib.http_client import get_text
from lib.utils import env_get, parse_year

SEARCH_URL = "https://kns.cnki.net/kns8s/brief/grid"
_HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://kns.cnki.net/",
}


def is_available() -> bool:
    """检查是否配置了 CNKI Cookie"""
    return bool(env_get("CNKI_COOKIE"))


def search(query: str, limit: int = 20) -> SearchResult:
    """搜索知网文献

    注意：知网没有公开 API，此模块通过 Cookie 模拟登录用户搜索。
    需要在环境变量或 .env 中设置 CNKI_COOKIE。
    """
    cookie = env_get("CNKI_COOKIE")
    if not cookie:
        return SearchResult(
            query=query,
            source="知网",
            error="未配置 CNKI_COOKIE，请在 .env 文件中设置知网 Cookie",
        )

    headers = {**_HEADERS_BASE, "Cookie": cookie}
    params = {
        "QueryJson": (
            f'{{"Platform":"","DBCode":"CFLS",'
            f'"KuaKuCode":"CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN",'
            f'"QNode":{{"QGroup":[{{"Key":"Subject","Title":"","Logic":1,"Items":'
            f'[{{"Title":"主题","Name":"SU","Value":"{query}",'
            f'"Operate":"%3D","BlurType":""}}],"ChildItems":[]}}]}}}}'
        ),
        "SearchSql": query,
        "PageName": "DefaultResult",
        "DBCode": "CFLS",
        "KuaKuCodes": "CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN",
        "CurPage": "1",
        "RecordsCntPerPage": str(limit),
    }

    try:
        html = get_text(SEARCH_URL, params=params, headers=headers, timeout=15)
        if not html:
            return SearchResult(query=query, source="知网", error="返回内容为空")
        papers = _parse_results(html)
        return SearchResult(
            query=query, source="知网", papers=papers, total_found=len(papers)
        )
    except Exception as e:
        return SearchResult(query=query, source="知网", error=str(e))


def _parse_results(html: str) -> list[Paper]:
    """解析知网搜索结果 HTML"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    soup = BeautifulSoup(html, "html.parser")
    papers: list[Paper] = []
    rows = soup.select("table.result-table-list tbody tr")
    if not rows:
        rows = soup.select("div.result-list div.result-item")

    for row in rows:
        title_el = row.select_one("td.name a") or row.select_one("a.fz14")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title:
            continue

        url = title_el.get("href", "")
        if url and not url.startswith("http"):
            url = "https://kns.cnki.net" + url

        authors: list[str] = []
        author_el = row.select_one("td.author") or row.select_one(".author")
        if author_el:
            for a_tag in author_el.select("a"):
                name = a_tag.get_text(strip=True)
                if name:
                    authors.append(name)

        year = 0
        date_el = row.select_one("td.date") or row.select_one(".date")
        if date_el:
            year = parse_year(date_el.get_text(strip=True))

        venue = ""
        source_el = row.select_one("td.source a") or row.select_one(".source a")
        if source_el:
            venue = source_el.get_text(strip=True)

        papers.append(
            Paper(
                title=title,
                authors=authors,
                year=year,
                url=url,
                source="知网",
                venue=venue,
                language="zh",
            )
        )

    return papers


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "鲁迅 创伤叙事"
    result = search(q)
    print(result.to_json())
