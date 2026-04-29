"""跨数据源搜索结果去重

同一篇论文可能同时出现在知网、万方、Google Scholar等多个数据源中。
本模块通过 DOI 精确匹配 + 标题模糊匹配 两级策略识别重复，
合并元数据（取最完整的字段）后输出去重结果。
"""
from __future__ import annotations
import re
import unicodedata

from schema import Paper


def _normalize(text: str) -> str:
    """标准化文本用于比较：去除空白、标点、统一大小写"""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[^\w]", "", text)  # 去掉所有非字母数字字符
    return text.lower().strip()


def _title_key(paper: Paper) -> str:
    """从标题生成比较用的 key"""
    return _normalize(paper.title)


def _doi_key(paper: Paper) -> str | None:
    """从 DOI 生成比较用的 key"""
    if not paper.doi:
        return None
    return paper.doi.lower().strip()


def _merge_papers(existing: Paper, new: Paper) -> Paper:
    """合并两条重复记录，取最完整的字段"""
    return Paper(
        title=existing.title if len(existing.title) >= len(new.title) else new.title,
        authors=existing.authors if len(existing.authors) >= len(new.authors) else new.authors,
        year=existing.year or new.year,
        url=existing.url or new.url,
        source=f"{existing.source}, {new.source}",  # 记录来自哪些数据源
        venue=existing.venue or new.venue,
        abstract=existing.abstract if len(existing.abstract) >= len(new.abstract) else new.abstract,
        doi=existing.doi or new.doi,
        keywords=existing.keywords if len(existing.keywords) >= len(new.keywords) else new.keywords,
        citation_count=max(existing.citation_count, new.citation_count),
        language=existing.language or new.language,
    )


def dedupe(papers: list[Paper]) -> list[Paper]:
    """对论文列表去重

    策略：
    1. DOI 精确匹配（最可靠）
    2. 标题归一化后匹配（覆盖无 DOI 的情况）
    重复项会合并元数据，保留最完整的信息。

    Returns:
        去重后的论文列表，保持原始顺序
    """
    seen_doi: dict[str, int] = {}      # doi_key -> index in result
    seen_title: dict[str, int] = {}    # title_key -> index in result
    result: list[Paper] = []

    for paper in papers:
        if not paper.title:
            continue

        doi_k = _doi_key(paper)
        title_k = _title_key(paper)

        # 跳过空标题
        if not title_k:
            continue

        # 先查 DOI 匹配
        if doi_k and doi_k in seen_doi:
            idx = seen_doi[doi_k]
            result[idx] = _merge_papers(result[idx], paper)
            # 也注册标题 key，防止后续标题匹配时遗漏
            if title_k not in seen_title:
                seen_title[title_k] = idx
            continue

        # 再查标题匹配
        if title_k in seen_title:
            idx = seen_title[title_k]
            result[idx] = _merge_papers(result[idx], paper)
            # 如果新记录有 DOI，也注册上
            if doi_k and doi_k not in seen_doi:
                seen_doi[doi_k] = idx
            continue

        # 新论文
        idx = len(result)
        result.append(paper)
        seen_title[title_k] = idx
        if doi_k:
            seen_doi[doi_k] = idx

    return result
