"""搜索结果格式化输出

将去重、评分后的论文列表渲染为人类可读或 Agent 可解析的格式。
支持三种输出模式：终端文本、Markdown、JSON。
"""
from __future__ import annotations
import json

from schema import Paper
from citation import auto_cite


def render_text(
    ranked_papers: list[tuple[Paper, float]],
    query: str,
    style: str = "gbt7714",
    max_show: int = 20,
) -> str:
    """渲染为终端可读的文本格式"""
    lines: list[str] = []
    lines.append(f"\n搜索：「{query}」")
    lines.append(f"共找到 {len(ranked_papers)} 篇文献（已去重）\n")
    lines.append("=" * 60)

    for i, (paper, score) in enumerate(ranked_papers[:max_show], 1):
        lines.append(f"\n  [{i}] {paper.title}")
        if paper.authors:
            author_str = ", ".join(paper.authors[:3])
            if len(paper.authors) > 3:
                author_str += " 等"
            lines.append(f"      作者：{author_str}")
        if paper.venue:
            lines.append(f"      期刊：{paper.venue}")
        info_parts = []
        if paper.year:
            info_parts.append(str(paper.year))
        if paper.citation_count > 0:
            info_parts.append(f"被引 {paper.citation_count}")
        if paper.language:
            info_parts.append(paper.language.upper())
        info_parts.append(f"评分 {score:.0f}")
        lines.append(f"      {' | '.join(info_parts)}")
        if paper.source:
            lines.append(f"      来源：{paper.source}")
        if paper.url:
            lines.append(f"      链接：{paper.url}")
        if paper.abstract:
            abs_text = paper.abstract[:150]
            if len(paper.abstract) > 150:
                abs_text += "..."
            lines.append(f"      摘要：{abs_text}")

    lines.append("\n" + "=" * 60)

    # 生成参考文献列表
    lines.append(f"\n参考文献（{style.upper()} 格式）：\n")
    for i, (paper, _) in enumerate(ranked_papers[:max_show], 1):
        lines.append(f"  [{i}] {auto_cite(paper, style)}")

    return "\n".join(lines)


def render_markdown(
    ranked_papers: list[tuple[Paper, float]],
    query: str,
    style: str = "gbt7714",
    max_show: int = 20,
) -> str:
    """渲染为 Markdown 格式（适合 Agent 回复或文件输出）"""
    lines: list[str] = []
    lines.append(f"# 文献搜索结果：{query}\n")
    lines.append(f"共找到 **{len(ranked_papers)}** 篇文献（已去重、评分排序）\n")

    for i, (paper, score) in enumerate(ranked_papers[:max_show], 1):
        lines.append(f"## {i}. {paper.title}\n")
        meta_parts = []
        if paper.authors:
            author_str = ", ".join(paper.authors[:3])
            if len(paper.authors) > 3:
                author_str += " 等"
            meta_parts.append(f"**作者**：{author_str}")
        if paper.venue:
            meta_parts.append(f"**期刊**：{paper.venue}")
        if paper.year:
            meta_parts.append(f"**年份**：{paper.year}")
        if paper.citation_count > 0:
            meta_parts.append(f"**被引**：{paper.citation_count}")
        meta_parts.append(f"**评分**：{score:.0f}/100")
        meta_parts.append(f"**来源**：{paper.source}")
        lines.append(" | ".join(meta_parts) + "\n")
        if paper.url:
            lines.append(f"[查看全文]({paper.url})\n")
        if paper.abstract:
            abs_text = paper.abstract[:200]
            if len(paper.abstract) > 200:
                abs_text += "..."
            lines.append(f"> {abs_text}\n")

    # 参考文献列表
    lines.append(f"\n---\n\n# 参考文献（{style.upper()}）\n")
    for i, (paper, _) in enumerate(ranked_papers[:max_show], 1):
        lines.append(f"{i}. {auto_cite(paper, style)}")

    return "\n".join(lines)


def render_json(
    ranked_papers: list[tuple[Paper, float]],
    query: str,
    style: str = "gbt7714",
) -> str:
    """渲染为 JSON 格式（适合程序化处理）"""
    output = {
        "query": query,
        "total": len(ranked_papers),
        "citation_style": style,
        "papers": [
            {
                **paper.to_dict(),
                "score": round(score, 1),
                "citation": auto_cite(paper, style),
                "rank": i + 1,
            }
            for i, (paper, score) in enumerate(ranked_papers)
        ],
    }
    return json.dumps(output, ensure_ascii=False, indent=2)
