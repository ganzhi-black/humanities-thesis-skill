"""引文自动生成

根据 Paper 对象的元数据自动生成符合学术规范的引用格式。
支持 GB/T 7714（中文学位论文和期刊最常用）、Chicago Notes、MLA 三种格式。

注意：自动生成的引文可能因元数据不完整而需要人工校对。
建议在论文定稿时逐条核对。
"""
from __future__ import annotations

from schema import Paper


def _join_authors_gbt(authors: list[str], max_show: int = 3) -> str:
    """GB/T 7714 作者格式：最多3人，超出用'等'"""
    if not authors:
        return ""
    shown = authors[:max_show]
    result = ", ".join(shown)
    if len(authors) > max_show:
        result += ", 等"
    return result


def _join_authors_chicago(authors: list[str], max_show: int = 3) -> str:
    """Chicago 作者格式：姓, 名. 多人用 and"""
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    shown = authors[:max_show]
    if len(authors) > max_show:
        return ", ".join(shown) + ", et al."
    return ", ".join(shown[:-1]) + f", and {shown[-1]}"


def _join_authors_mla(authors: list[str]) -> str:
    """MLA 作者格式：第一作者姓名倒置，其余正常"""
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]}, and {authors[1]}"
    if len(authors) >= 3:
        return f"{authors[0]}, et al."
    return authors[0]


def gbt7714(paper: Paper, doc_type: str = "J") -> str:
    """生成 GB/T 7714 格式引文

    Args:
        paper: 论文对象
        doc_type: 文献类型标识
            J=期刊, M=专著, D=学位论文, C=论文集, EB/OL=网络

    Returns:
        格式化的引文字符串

    示例输出:
        陈思和. 中国当代文学中的创伤叙事[J]. 文学评论, 2018(3): 5-15.
        Benjamin, Walter. Illuminations[M]. New York: Schocken Books, 1969.
    """
    parts: list[str] = []

    # 作者
    author_str = _join_authors_gbt(paper.authors)
    if author_str:
        parts.append(author_str)

    # 标题 + 文献类型标识
    if paper.title:
        parts.append(f"{paper.title}[{doc_type}]")

    # 期刊/出版信息
    if paper.venue:
        parts.append(paper.venue)

    # 年份
    if paper.year:
        parts.append(str(paper.year))

    # DOI（如果有）
    if paper.doi:
        parts.append(f"DOI: {paper.doi}")

    return ". ".join(parts) + "."


def chicago_note(paper: Paper) -> str:
    """生成 Chicago Notes-Bibliography 格式脚注

    示例输出:
        Walter Benjamin, Illuminations (New York: Schocken Books, 1969), 257.
        Rey Chow, "Rereading Mandarin Ducks," Cultural Critique 45 (2000): 69.
    """
    parts: list[str] = []

    # 作者
    author_str = _join_authors_chicago(paper.authors)
    if author_str:
        parts.append(author_str)

    # 标题（期刊文章用引号，书用斜体标记）
    if paper.title:
        if paper.venue:
            parts.append(f'"{paper.title}"')
        else:
            parts.append(paper.title)  # 书名，实际排版时需斜体

    # 期刊名和年份
    if paper.venue and paper.year:
        parts.append(f"{paper.venue} ({paper.year})")
    elif paper.venue:
        parts.append(paper.venue)
    elif paper.year:
        parts.append(f"({paper.year})")

    return ", ".join(parts) + "."


def mla(paper: Paper) -> str:
    """生成 MLA 格式引文

    示例输出:
        Benjamin, Walter. Illuminations. Schocken Books, 1969.
        Chow, Rey. "Rereading Mandarin Ducks." Cultural Critique, no. 45, 2000, pp. 69-93.
    """
    parts: list[str] = []

    # 作者
    author_str = _join_authors_mla(paper.authors)
    if author_str:
        parts.append(author_str)

    # 标题
    if paper.title:
        if paper.venue:
            parts.append(f'"{paper.title}."')
        else:
            parts.append(f"{paper.title}.")  # 书名

    # 期刊/出版信息
    if paper.venue:
        venue_part = paper.venue
        if paper.year:
            venue_part += f", {paper.year}"
        parts.append(venue_part)
    elif paper.year:
        parts.append(str(paper.year))

    return " ".join(parts) + "."


def auto_cite(paper: Paper, style: str = "gbt7714") -> str:
    """根据指定样式自动生成引文

    Args:
        paper: 论文对象
        style: 引用样式，可选 'gbt7714' / 'chicago' / 'mla'

    Returns:
        格式化的引文字符串
    """
    # 自动推断文献类型（GB/T 7714 需要）
    doc_type = "J"  # 默认为期刊
    if not paper.venue:
        doc_type = "M"  # 无期刊名假设为专著

    formatters = {
        "gbt7714": lambda p: gbt7714(p, doc_type),
        "chicago": chicago_note,
        "mla": mla,
    }

    formatter = formatters.get(style.lower(), formatters["gbt7714"])
    return formatter(paper)


def batch_cite(papers: list[Paper], style: str = "gbt7714") -> list[str]:
    """批量生成引文列表

    Returns:
        编号引文列表，如 ["[1] 陈思和. ...", "[2] Benjamin. ..."]
    """
    return [
        f"[{i + 1}] {auto_cite(p, style)}"
        for i, p in enumerate(papers)
    ]
