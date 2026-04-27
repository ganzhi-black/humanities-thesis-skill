"""搜索结果评分与排序

对去重后的论文列表进行综合评分，帮用户快速定位最相关、最有价值的文献。
评分维度：相关性（标题/摘要与查询的匹配度）、时效性、影响力（引用次数）、
信息完整度（有无摘要、DOI等）。
"""
from __future__ import annotations
import re
import math
import datetime

from schema import Paper


def _tokenize(text: str) -> set[str]:
    """简单分词：按非字母数字字符分割 + 逐字拆分中文"""
    tokens: set[str] = set()
    # 英文按空格和标点分割
    for word in re.findall(r"[a-zA-Z]+", text.lower()):
        if len(word) > 1:
            tokens.add(word)
    # 中文逐字 + 双字窗口
    chars = re.findall(r"[\u4e00-\u9fff]", text)
    tokens.update(chars)
    for i in range(len(chars) - 1):
        tokens.add(chars[i] + chars[i + 1])
    return tokens


def _relevance_score(paper: Paper, query_tokens: set[str]) -> float:
    """计算与查询的相关性（0-40分）"""
    title_tokens = _tokenize(paper.title)
    abstract_tokens = _tokenize(paper.abstract) if paper.abstract else set()

    if not query_tokens:
        return 0.0

    # 标题匹配（权重更高）
    title_overlap = len(query_tokens & title_tokens)
    title_ratio = title_overlap / len(query_tokens) if query_tokens else 0

    # 摘要匹配
    abstract_overlap = len(query_tokens & abstract_tokens)
    abstract_ratio = abstract_overlap / len(query_tokens) if query_tokens else 0

    return title_ratio * 28 + abstract_ratio * 12


def _recency_score(paper: Paper, current_year: int = datetime.date.today().year) -> float:
    """计算时效性（0-20分）：近5年满分，逐年递减"""
    if not paper.year or paper.year < 1900:
        return 5.0  # 无年份信息给基础分
    age = current_year - paper.year
    if age <= 0:
        return 20.0
    if age <= 2:
        return 18.0
    if age <= 5:
        return 15.0
    if age <= 10:
        return 10.0
    if age <= 20:
        return 6.0
    return 3.0


def _impact_score(paper: Paper) -> float:
    """计算影响力（0-20分）：基于引用次数的对数评分"""
    if paper.citation_count <= 0:
        return 2.0  # 基础分
    # log2 缩放，避免高引用论文过度主导
    return min(2.0 + math.log2(1 + paper.citation_count) * 2.5, 20.0)


def _completeness_score(paper: Paper) -> float:
    """计算信息完整度（0-20分）：字段越完整分越高"""
    score = 0.0
    if paper.title:
        score += 3.0
    if paper.authors:
        score += 3.0
    if paper.year:
        score += 2.0
    if paper.abstract:
        score += 4.0
    if paper.doi:
        score += 3.0
    if paper.venue:
        score += 2.0
    if paper.url:
        score += 1.5
    if paper.keywords:
        score += 1.5
    return score


def score_paper(paper: Paper, query: str, current_year: int = datetime.date.today().year) -> float:
    """综合评分（0-100分）

    评分构成：
    - 相关性 40%：标题和摘要与查询词的匹配程度
    - 时效性 20%：发表年份越近分越高
    - 影响力 20%：引用次数（对数缩放）
    - 完整度 20%：元数据字段的完整程度
    """
    query_tokens = _tokenize(query)
    return (
        _relevance_score(paper, query_tokens)
        + _recency_score(paper, current_year)
        + _impact_score(paper)
        + _completeness_score(paper)
    )


def rank(papers: list[Paper], query: str, current_year: int = datetime.date.today().year) -> list[tuple[Paper, float]]:
    """对论文列表评分并按分数降序排列

    Returns:
        [(paper, score), ...] 按分数从高到低排列
    """
    scored = [(p, score_paper(p, query, current_year)) for p in papers]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
