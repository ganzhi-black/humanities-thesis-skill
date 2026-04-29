"""基于 autocli 的学术网页抓取

复用用户的 Chrome 登录会话，直接抓取需要登录的学术网站。
比传统 HTTP 抓取稳定得多——不会被反爬机制拦截，不需要 Cookie 配置。

依赖：autocli CLI 工具（https://github.com/nashsu/AutoCLI）
安装：curl -fsSL https://raw.githubusercontent.com/nashsu/AutoCLI/main/scripts/install.sh | sh

工作流：
1. 检测 autocli 是否已安装
2. 用 autocli read <url> 抓取学术网页（复用 Chrome 登录态）
3. 用 autocli google search 搜索 Google Scholar
4. 解析返回的 Markdown/JSON 提取文献信息
"""
from __future__ import annotations
import subprocess
import json
import re
import shutil
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.schema import Paper, SearchResult
from lib.utils import parse_year

logger = logging.getLogger(__name__)


def is_autocli_available() -> bool:
    """检测 autocli 是否已安装"""
    return shutil.which("autocli") is not None


def _run_autocli(args: list[str], timeout: int = 30) -> str | None:
    """执行 autocli 命令，返回 stdout 或 None"""
    try:
        result = subprocess.run(
            ["autocli"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return result.stdout
        logger.warning("autocli %s failed (exit %d): %s",
                       " ".join(args[:3]), result.returncode, result.stderr[:200])
        return None
    except FileNotFoundError:
        logger.warning("autocli not found")
        return None
    except subprocess.TimeoutExpired:
        logger.warning("autocli %s timed out", " ".join(args[:3]))
        return None
    except Exception as e:
        logger.warning("autocli error: %s", e)
        return None


def read_url(url: str, fmt: str = "text") -> str | None:
    """用 autocli read 抓取任意网页内容（复用 Chrome 登录态）

    适用于：
    - 知网论文详情页（需要登录才能看摘要）
    - Google Scholar 搜索结果页
    - 国家哲社文献中心
    - 任何需要登录的学术网站

    Args:
        url: 网页 URL
        fmt: 输出格式 (text/markdown/json)

    Returns:
        网页内容文本，或 None（如果失败）
    """
    return _run_autocli(["read", url, "-f", fmt], timeout=30)


def search_google_scholar(query: str, limit: int = 20) -> SearchResult:
    """通过 autocli + Google 搜索 Google Scholar

    原理：用 autocli google search 搜索 "site:scholar.google.com <query>"，
    复用用户的 Chrome Google 登录态，绕过反爬。
    """
    if not is_autocli_available():
        return SearchResult(
            query=query,
            source="Google Scholar (autocli)",
            error="autocli 未安装。安装方法见 references/platform-guide.md",
        )

    # 通过 Google 搜索限定 scholar.google.com
    search_query = f"site:scholar.google.com {query}"
    output = _run_autocli(
        ["google", "search", search_query, "--limit", str(limit), "--format", "json"],
        timeout=20,
    )

    if not output:
        return SearchResult(
            query=query,
            source="Google Scholar (autocli)",
            error="autocli google search 返回为空，请确认 Chrome 中已登录 Google",
        )

    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return SearchResult(
            query=query,
            source="Google Scholar (autocli)",
            error="autocli 返回内容无法解析为 JSON",
        )

    papers: list[Paper] = []
    items = data if isinstance(data, list) else data.get("results", data.get("items", []))

    for item in items[:limit]:
        title = item.get("title", "")
        url = item.get("url", item.get("link", ""))
        snippet = item.get("snippet", item.get("description", ""))

        # 从 snippet 中尝试提取作者和年份
        authors: list[str] = []
        year = parse_year(snippet)

        papers.append(Paper(
            title=title,
            authors=authors,
            year=year,
            url=url,
            source="Google Scholar (autocli)",
            abstract=snippet,
            language="en",
        ))

    return SearchResult(
        query=query,
        source="Google Scholar (autocli)",
        papers=papers,
        total_found=len(papers),
    )


def search_cnki_via_read(query: str, limit: int = 10) -> SearchResult:
    """通过 autocli read 抓取知网搜索结果页

    比 Cookie 方式更稳定——直接复用 Chrome 的知网登录态。
    """
    if not is_autocli_available():
        return SearchResult(
            query=query, source="知网 (autocli)",
            error="autocli 未安装",
        )

    import urllib.parse
    search_url = (
        f"https://kns.cnki.net/kns8s/defaultresult/index?"
        f"action=scdbsearch&txt_1_sel=SU&txt_1_value1={urllib.parse.quote(query)}"
        f"&currentid=txt_1_value1"
    )

    content = read_url(search_url, fmt="text")
    if not content:
        return SearchResult(
            query=query, source="知网 (autocli)",
            error="无法抓取知网搜索页，请确认 Chrome 中已登录知网",
        )

    # 从纯文本中提取论文信息（简单启发式）
    papers: list[Paper] = []
    # 知网的 Readability 提取可能不完美，但至少能拿到标题和部分信息
    # 更精确的解析需要根据实际返回内容调整
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        # 简单匹配看起来像论文标题的行（包含期刊年份信息的）
        if re.search(r"(19|20)\d{2}", line) and len(line) > 10 and len(line) < 200:
            year = parse_year(line)
            papers.append(Paper(
                title=line[:100],
                year=year,
                source="知网 (autocli)",
                language="zh",
            ))
            if len(papers) >= limit:
                break

    return SearchResult(
        query=query,
        source="知网 (autocli)",
        papers=papers,
        total_found=len(papers),
        error="" if papers else "从知网页面中未能解析出结构化结果，建议直接在知网中搜索",
    )


if __name__ == "__main__":
    print(f"autocli available: {is_autocli_available()}")
    if is_autocli_available():
        q = sys.argv[1] if len(sys.argv) > 1 else "鲁迅 创伤叙事"
        print(f"\nSearching Google Scholar for: {q}")
        result = search_google_scholar(q, limit=5)
        print(result.to_json())
