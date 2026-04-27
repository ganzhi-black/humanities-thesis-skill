"""统一文献搜索入口 - 聚合多个数据源

用法：
  python search.py "鲁迅 创伤叙事"                         # 搜索并输出排序结果
  python search.py "鲁迅 创伤叙事" --sources cnki,wanfang   # 指定数据源
  python search.py "鲁迅 创伤叙事" --limit 10               # 限制每个数据源返回数量
  python search.py "鲁迅 创伤叙事" --style chicago           # 指定引文格式
  python search.py "鲁迅 创伤叙事" --format json             # JSON 输出（供 Agent 调用）
  python search.py "鲁迅 创伤叙事" --expand                  # 显示查询展开建议
  python search.py --list-sources                            # 列出所有数据源及其配置状态

数据源配置（在 scripts/.env 文件或环境变量中设置）：
  CNKI_COOKIE=...       知网 Cookie（从浏览器复制）
  SERPAPI_KEY=...        SerpAPI Key（用于 Google Scholar，免费注册）
  S2_API_KEY=...         Semantic Scholar API Key（可选，提高速率限制）
  CROSSREF_EMAIL=...     邮箱（可选，CrossRef polite pool）

完整流程：搜索 → 去重 → 评分排序 → 格式化输出（含自动引文生成）
"""
from __future__ import annotations
import sys, os, json, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(__file__))

from lib.schema import Paper, SearchResult
from lib.dedupe import dedupe
from lib.score import rank
from lib.render import render_text, render_markdown, render_json
from lib.query import expand_query, suggest_queries

# 注册所有数据源
_SOURCES: dict[str, object] = {}


def _load_sources():
    """延迟加载所有数据源模块"""
    global _SOURCES
    if _SOURCES:
        return
    from sources import source_cnki
    from sources import source_google_scholar
    from sources import source_wanfang
    from sources import source_semantic_scholar
    from sources import source_crossref
    from sources import source_openalex
    from sources import source_core
    from sources import source_ncpssd

    _SOURCES = {
        "cnki": source_cnki,
        "ncpssd": source_ncpssd,
        "google_scholar": source_google_scholar,
        "wanfang": source_wanfang,
        "openalex": source_openalex,
        "semantic_scholar": source_semantic_scholar,
        "core": source_core,
        "crossref": source_crossref,
    }


def list_sources() -> dict[str, dict]:
    """列出所有数据源及其可用状态"""
    _load_sources()
    info = {}
    for name, mod in _SOURCES.items():
        info[name] = {
            "available": mod.is_available(),
            "description": (mod.__doc__ or "").strip().split("\n")[0],
        }
    return info


def search(
    query: str,
    sources: list[str] | None = None,
    limit: int = 20,
    parallel: bool = True,
) -> list[SearchResult]:
    """在多个数据源中搜索文献

    Args:
        query: 搜索关键词
        sources: 要使用的数据源列表（None 表示所有可用的）
        limit: 每个数据源的最大返回数量
        parallel: 是否并行搜索

    Returns:
        各数据源的搜索结果列表
    """
    _load_sources()

    if sources:
        active = {k: v for k, v in _SOURCES.items() if k in sources}
    else:
        active = {k: v for k, v in _SOURCES.items() if v.is_available()}

    if not active:
        return [
            SearchResult(
                query=query,
                source="all",
                error="没有可用的数据源。请检查配置（运行 python search.py --list-sources）",
            )
        ]

    results: list[SearchResult] = []

    if parallel and len(active) > 1:
        with ThreadPoolExecutor(max_workers=len(active)) as pool:
            futures = {
                pool.submit(mod.search, query, limit): name
                for name, mod in active.items()
            }
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    name = futures[future]
                    results.append(
                        SearchResult(query=query, source=name, error=str(e))
                    )
    else:
        for name, mod in active.items():
            try:
                results.append(mod.search(query, limit))
            except Exception as e:
                results.append(SearchResult(query=query, source=name, error=str(e)))

    return results


def search_and_rank(
    query: str,
    sources: list[str] | None = None,
    limit: int = 20,
    style: str = "gbt7714",
) -> tuple[list[tuple[Paper, float]], list[str]]:
    """搜索 → 去重 → 评分排序 完整流程

    Returns:
        (ranked_papers, errors): 排序后的论文列表和搜索过程中的错误信息
    """
    results = search(query, sources=sources, limit=limit)

    # 收集所有论文和错误
    all_papers: list[Paper] = []
    errors: list[str] = []
    for r in results:
        all_papers.extend(r.papers)
        if r.error:
            errors.append(f"[{r.source}] {r.error}")

    # 去重
    unique_papers = dedupe(all_papers)

    # 评分排序
    ranked = rank(unique_papers, query)

    return ranked, errors


def search_to_json(
    query: str,
    sources: list[str] | None = None,
    limit: int = 20,
    style: str = "gbt7714",
) -> str:
    """搜索并返回 JSON 字符串，方便被 LLM agent 调用

    返回的 JSON 包含去重后的排序结果和自动生成的引文。
    """
    ranked, errors = search_and_rank(query, sources=sources, limit=limit, style=style)
    return render_json(ranked, query, style=style)


def main():
    parser = argparse.ArgumentParser(description="学术文献统一搜索")
    parser.add_argument("query", nargs="?", default="", help="搜索关键词")
    parser.add_argument("--sources", type=str, default="",
                        help="指定数据源，逗号分隔（如 cnki,wanfang）")
    parser.add_argument("--limit", type=int, default=20,
                        help="每个数据源的最大返回数量")
    parser.add_argument("--style", type=str, default="gbt7714",
                        choices=["gbt7714", "chicago", "mla"],
                        help="引文格式（默认 gbt7714）")
    parser.add_argument("--format", type=str, default="text",
                        choices=["text", "markdown", "json"],
                        help="输出格式（默认 text）")
    parser.add_argument("--expand", action="store_true",
                        help="显示查询展开建议（中英文变体）")
    parser.add_argument("--list-sources", action="store_true",
                        help="列出所有数据源及其配置状态")
    args = parser.parse_args()

    if args.list_sources:
        info = list_sources()
        print("\n可用数据源：")
        for name, detail in info.items():
            status = "✓ 已配置" if detail["available"] else "✗ 未配置"
            print(f"  [{status}] {name}: {detail['description']}")
        print("\n配置方法：在 scripts/.env 文件中设置对应的环境变量")
        return

    if not args.query:
        parser.print_help()
        return

    # 查询展开建议
    if args.expand:
        suggestions = suggest_queries(args.query)
        expanded = expand_query(args.query)
        print(f"\n原始查询：{args.query}")
        print(f"中文优化：{expanded['zh']}")
        print(f"英文版本：{expanded['en']}")
        print(f"\n推荐搜索变体：")
        for i, s in enumerate(suggestions, 1):
            print(f"  {i}. {s}")
        return

    # 执行搜索
    sources_list = [s.strip() for s in args.sources.split(",") if s.strip()] or None
    ranked, errors = search_and_rank(
        args.query, sources=sources_list, limit=args.limit, style=args.style
    )

    # 输出错误信息
    if errors:
        import sys as _sys
        for e in errors:
            print(e, file=_sys.stderr)

    # 格式化输出
    if args.format == "json":
        print(render_json(ranked, args.query, style=args.style))
    elif args.format == "markdown":
        print(render_markdown(ranked, args.query, style=args.style))
    else:
        print(render_text(ranked, args.query, style=args.style))


if __name__ == "__main__":
    main()