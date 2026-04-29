"""查询预处理

将用户的自然语言搜索词优化为更适合学术数据库检索的形式。
处理中英文混合、理论家名字中英对照、常见缩写展开等。
"""
from __future__ import annotations
import re


# 常见理论家中英文对照（人文社科高频）
_SCHOLAR_MAP: dict[str, str] = {
    "福柯": "Foucault",
    "德里达": "Derrida",
    "本雅明": "Benjamin",
    "阿甘本": "Agamben",
    "巴特勒": "Butler",
    "阿伦特": "Arendt",
    "南希": "Nancy",
    "布朗肖": "Blanchot",
    "阿多诺": "Adorno",
    "萨义德": "Said",
    "巴巴": "Bhabha",
    "斯皮瓦克": "Spivak",
    "鲁迅": "Lu Xun",
    "布尔迪厄": "Bourdieu",
    "拉康": "Lacan",
    "列维纳斯": "Levinas",
    "德勒兹": "Deleuze",
    "齐泽克": "Žižek",
    "海德格尔": "Heidegger",
    "哈贝马斯": "Habermas",
    "韦伯": "Weber",
    "涂尔干": "Durkheim",
    "葛兰西": "Gramsci",
    "霍克海默": "Horkheimer",
    "克里斯蒂娃": "Kristeva",
    "索绪尔": "Saussure",
    "巴赫金": "Bakhtin",
    "本尼迪克特·安德森": "Benedict Anderson",
    "莫雷蒂": "Moretti",
}

# 常见学术缩写展开
_ABBREV_MAP: dict[str, str] = {
    "文革": "文化大革命",
    "五四": "五四运动",
    "后殖民": "后殖民主义",
    "解构": "解构主义",
    "现象学": "现象学 phenomenology",
}


def _extract_chinese(text: str) -> list[str]:
    """提取中文词汇（连续中文字符）"""
    return re.findall(r"[\u4e00-\u9fff]+", text)


def _extract_english(text: str) -> list[str]:
    """提取英文词汇"""
    return re.findall(r"[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*", text)


def expand_query(query: str) -> dict[str, str]:
    """将用户查询展开为中英文两个版本

    输入：用户的自然语言查询
    输出：{
        "zh": "中文优化查询",
        "en": "英文优化查询",
        "original": "原始查询"
    }

    示例：
        "福柯 规训 中国现代文学"
        → zh: "福柯 规训 中国现代文学"
        → en: "Foucault discipline modern Chinese literature"
    """
    query = query.strip()
    zh_parts: list[str] = []
    en_parts: list[str] = []

    # 提取中文部分
    chinese_words = _extract_chinese(query)
    for word in chinese_words:
        zh_parts.append(word)
        # 如果是理论家名字，添加英文对照
        if word in _SCHOLAR_MAP:
            en_parts.append(_SCHOLAR_MAP[word])
        # 如果是常见缩写，展开
        if word in _ABBREV_MAP:
            expanded = _ABBREV_MAP[word]
            if expanded != word:
                # 提取展开词中的英文部分
                en_words = _extract_english(expanded)
                if en_words:
                    en_parts.extend(en_words)

    # 提取英文部分
    english_words = _extract_english(query)
    en_parts.extend(english_words)

    # 如果中文查询中没有识别出理论家，尝试翻译关键概念
    concept_map = {
        "创伤": "trauma",
        "叙事": "narrative",
        "现代性": "modernity",
        "暴力": "violence",
        "记忆": "memory",
        "身体": "body",
        "空间": "space",
        "权力": "power",
        "主体": "subjectivity",
        "他者": "other alterity",
        "共同体": "community",
        "寓言": "allegory",
        "废墟": "ruin",
    }
    for word in chinese_words:
        if word in concept_map and concept_map[word] not in " ".join(en_parts).lower():
            en_parts.append(concept_map[word])

    # 如果英文部分为空，使用原始查询
    if not en_parts:
        en_parts = [query]

    return {
        "zh": " ".join(zh_parts) if zh_parts else query,
        "en": " ".join(en_parts) if en_parts else query,
        "original": query,
    }


def suggest_queries(query: str) -> list[str]:
    """基于用户查询推荐多个搜索变体

    返回3-5个搜索建议，用于不同数据库。
    """
    expanded = expand_query(query)
    suggestions = [expanded["original"]]

    if expanded["zh"] != expanded["original"]:
        suggestions.append(expanded["zh"])
    if expanded["en"] != expanded["original"]:
        suggestions.append(expanded["en"])

    # 如果查询包含理论家名字，生成"理论家+研究对象"的组合
    chinese_words = _extract_chinese(query)
    scholars_found = [w for w in chinese_words if w in _SCHOLAR_MAP]
    non_scholars = [w for w in chinese_words if w not in _SCHOLAR_MAP]

    if scholars_found and non_scholars:
        # 英文版：理论家英文名+研究对象
        for scholar in scholars_found:
            en_name = _SCHOLAR_MAP[scholar]
            en_suggestion = f"{en_name} {' '.join(non_scholars)}"
            if en_suggestion not in suggestions:
                suggestions.append(en_suggestion)

    return suggestions[:5]
