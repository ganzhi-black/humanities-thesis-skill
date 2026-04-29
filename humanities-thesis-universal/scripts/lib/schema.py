"""学术文献搜索 - 数据模型定义"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class Paper:
    """单篇文献的标准化表示"""
    title: str
    authors: list[str] = field(default_factory=list)
    year: int = 0
    url: str = ""
    source: str = ""          # 数据源名称：知网 / 万方 / Google Scholar / JSTOR 等
    venue: str = ""           # 期刊名 / 会议名 / 出版社
    abstract: str = ""        # 摘要
    doi: str = ""
    keywords: list[str] = field(default_factory=list)
    citation_count: int = 0
    language: str = ""        # zh / en

    def to_dict(self) -> dict:
        return asdict(self)

    def to_citation_str(self) -> str:
        """生成简易引用字符串"""
        author_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            author_str += " 等"
        parts = [author_str] if author_str else []
        if self.title:
            parts.append(f"《{self.title}》" if self.language == "zh" else f'"{self.title}"')
        if self.venue:
            parts.append(self.venue)
        if self.year:
            parts.append(str(self.year))
        return ", ".join(parts)


@dataclass
class SearchResult:
    """一次搜索的完整结果"""
    query: str
    source: str
    papers: list[Paper] = field(default_factory=list)
    error: Optional[str] = None
    total_found: int = 0

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(
            {
                "query": self.query,
                "source": self.source,
                "total_found": self.total_found,
                "error": self.error,
                "papers": [p.to_dict() for p in self.papers],
            },
            ensure_ascii=False,
            indent=indent,
        )
