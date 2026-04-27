<div align="center">

# 📜 humanities-thesis-skill

### *给人文社科研究者的 AI 写作副驾驶*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-teal)](https://github.com/)

<br>

<table>
<tr><td align="left">

📖 &nbsp;论文选题想了三天，还是"浅析《XXX》的叙事策略"？<br>
🤖 &nbsp;让AI帮你写论文，结果它编了三篇不存在的文献？<br>
😵 &nbsp;每句话单独看都对，连在一起读就是一盘散沙？<br>
🌍 &nbsp;翻译英文摘要，"延异"到底译成 différance 还是 differance？

</td></tr>
</table>

### ✨ 这个 Skill 解决以上所有问题。

<br>

从选题到投稿的 **全流程方法论指导** + **8 个学术数据库聚合搜索** + **21 条规则的文本评估引擎**

不是帮你"写"论文——是帮你**想清楚**论文该怎么写，然后检查你写的每一段是否站得住脚。

<br>

[⚡ 快速开始](#-快速开始) · [🧠 核心能力](#-核心能力) · [🔬 文本评估](#-文本评估引擎) · [📦 数据源](#-学术数据库) · [📂 项目结构](#-项目结构) · [🎯 设计原则](#-设计原则)

</div>

---

## ⚡ 快速开始

打开你的 Claude Code 或 OpenClaw，把这个仓库交给它：

> 帮我安装这个 skill：`https://github.com/yourname/humanities-thesis-skill`

Agent 会自动识别 SKILL.md 并加载。然后直接说：

> "我要写一篇关于鲁迅小说创伤叙事的硕士论文，帮我理清思路"

Skill 会从**三轮结构化提问**开始，逐步帮你锁定研究对象、核心问题、理论框架、论文结构。

<details>
<summary><b>🛠️ 手动安装</b></summary>

```bash
git clone https://github.com/yourname/humanities-thesis-skill
cd humanities-thesis-skill
pip install -r requirements.txt
```

| Agent | Skill 目录 |
|-------|-----------|
| Claude Code | 放在项目根目录，自动读取 SKILL.md |
| OpenClaw | 作为 skill 目录导入 |

</details>

<details>
<summary><b>🔧 配置搜索数据源（可选）</b></summary>

```bash
cp scripts/.env.example scripts/.env
# 编辑 .env，填入知网 Cookie / SerpAPI Key 等
# 不配置也能用——8 个数据源中 7 个零配置即可工作
```

</details>

---

## 🧠 核心能力

<table>
<thead>
<tr>
<th width="33%" align="center">📋 方法论指导</th>
<th width="33%" align="center">🔍 文献工具链</th>
<th width="33%" align="center">✅ 质量保障</th>
</tr>
</thead>
<tbody>
<tr>
<td>

**提问引导**<br>
<sub>三轮结构化提问，从模糊兴趣到可论证的问题</sub>

**选题 → 定稿全流程**<br>
<sub>选题、理论框架、结构设计、材料细读、历史语境、修改诊断</sub>

**散碎材料 → 完整论文**<br>
<sub>四步整合工作流：清点 → 提取线索 → 重组结构 → 缝合补写</sub>

</td>
<td>

**8 个学术数据库聚合搜索**<br>
<sub>知网 · 国家哲社文献中心 · 万方 · OpenAlex · CORE · Google Scholar · Semantic Scholar · CrossRef</sub>

**五层文献拆解法**<br>
<sub>元信息 → 论证结构 → 证据标记 → 关系定位 → 交叉比对</sub>

**224 条术语中英法德对照**<br>
<sub>覆盖 15 个理论学派，查不到自动联网搜索</sub>

</td>
<td>

**R1-R4 防幻觉硬规则**<br>
<sub>不编造文献、不虚构引文、不捏造数据</sub>

**21 条文本评估规则**<br>
<sub>六个维度：可信度 · 术语 · 格式 · 语体 · 论证逻辑 · 结构</sub>

**格式规范速查**<br>
<sub>GB/T 7714 · Chicago · MLA，字体字号到脚注一站式</sub>

</td>
</tr>
</tbody>
</table>

---

## 🔬 文本评估引擎

写完一段，跑一次检查。不是让模型"自己检查自己"——而是用**正则匹配 + 术语表比对**做确定性校验。

```bash
python scripts/review.py paper.md
```

```
评估完成：2 个错误 / 5 个警告 / 1 个提示

✗ [错误] R1-01 第12行
  模糊引用：使用了「有学者指出」类表述但未给出具体文献
  建议：替换为具体的作者名+出处，或删除这个引用

⚠ [警告] L-07 第45行
  总结句中堆砌了 5 个以上并列概念
  建议：检查这些并列项是否都在前文得到了论证

⚠ [警告] L-08 第38行
  强断言「显然」附近未见充分的论据支撑
  建议：删去强度词，或补充多重论据
```

### 六个维度 · 21 条规则

| 维度 | 规则 | 做什么 |
|------|------|--------|
| 🔴 **可信度** | R1-01 ~ R3-01 | 模糊引用、未来年份引用（编造嫌疑）、过度断言 |
| 🟡 **术语** | T-01 | 同一概念多个译名混用（灵晕/灵韵/灵光） |
| 🟠 **格式** | F-01 ~ F-04 | 空脚注、参考文献缺 [M][J]、中英标点混用、标题编号混用 |
| 🔵 **语体** | S-01 ~ S-02 | 口语化（"说白了""笔者觉得"）、自称不统一 |
| 🟣 **论证逻辑** | L-01 ~ L-08 | 连续断言无论证连接、并列堆砌无递进、引文后缺分析、章节间缺过渡、因果前提未论证、总结句概念堆砌、强度词缺论据 |
| ⚪ **结构** | ST-01 ~ ST-02 | 缺摘要/关键词/参考文献、引言缺论点句 |

---

## 📦 学术数据库

一条命令搜遍中英文学术圈：

```bash
python scripts/search.py "鲁迅 创伤叙事"
```

| 数据源 | 语言 | 需要配置？ | 说明 |
|--------|:----:|:---------:|------|
| 🇨🇳 国家哲社文献中心 | 中文 | ❌ | **人文社科首选**，2,400+ 种核心期刊，完全免费 |
| 🇨🇳 知网 CNKI | 中文 | Cookie | 中文文献最全 |
| 🇨🇳 万方数据 | 中文 | ❌ | 中文文献补充 |
| 🌐 OpenAlex | 英文 | ❌ | 2.5 亿+ 论文，Scopus 的免费替代品 |
| 🌐 CORE | 英文 | ❌ | 3 亿+ 开放获取论文 |
| 🌐 Google Scholar | 双语 | 推荐 | 综合搜索，推荐配 SerpAPI Key |
| 🌐 Semantic Scholar | 英文 | ❌ | Allen AI 提供，免费公开 API |
| 🌐 CrossRef | 英文 | ❌ | DOI 元数据查询 |

> 8 个数据源中 **7 个零配置可用**，只有知网需要手动配 Cookie。

---

## 📂 项目结构

```
humanities-thesis-skill/
├── SKILL.md                            # 核心指令（agent 启动时加载）
├── README.md                           # 本文件
├── requirements.txt                    # Python 依赖
│
├── references/                         # 📚 参考文档（按需加载，节省 token）
│   ├── writing-templates.md            #   写作模板（引言、摘要、过渡段）
│   ├── theory-frameworks.md            #   理论家速查（16 位，含兜底搜索策略）
│   ├── terminology-bilingual.md        #   术语对照表（224 条中英法德）
│   ├── formatting-guide.md             #   格式规范（字体字号、脚注、参考文献）
│   ├── literature-review.md            #   文献综述方法 + 搜索策略
│   ├── literature-analysis.md          #   核心文献五层拆解法
│   ├── material-integration.md         #   散碎材料 → 完整论文工作流
│   ├── english-translation.md          #   英文翻译与投稿准备
│   ├── text-review.md                  #   文本评估维度说明
│   └── platform-guide.md              #   Agent 适配说明
│
└── scripts/                            # 🔧 Python 工具链
    ├── search.py                       #   统一文献搜索入口
    ├── review.py                       #   文本评估入口
    ├── .env.example                    #   数据源配置模板
    ├── lib/                            #   公共模块
    │   ├── schema.py                   #     数据模型
    │   ├── http_client.py              #     HTTP 封装
    │   ├── utils.py                    #     工具函数
    │   ├── query.py                    #     查询预处理（中英双语展开）
    │   ├── score.py                    #     搜索结果评分排序
    │   ├── dedupe.py                   #     跨数据源去重
    │   ├── render.py                   #     输出渲染
    │   ├── citation.py                 #     引文自动生成
    │   └── review_rules.py             #     文本评估规则引擎（21 条规则）
    └── sources/                        #   数据源模块（8 个）
        ├── source_ncpssd.py            #     国家哲社文献中心
        ├── source_cnki.py              #     知网
        ├── source_wanfang.py           #     万方
        ├── source_openalex.py          #     OpenAlex
        ├── source_core.py              #     CORE
        ├── source_google_scholar.py    #     Google Scholar
        ├── source_semantic_scholar.py  #     Semantic Scholar
        └── source_crossref.py          #     CrossRef
```

---

## 🎯 设计原则

| 原则 | 具体做法 |
|------|---------|
| **SKILL.md 保持精简** | 核心指令 + Rules 控制在 240 行以内，其余内容按需从 references/ 加载，节省 token |
| **Rules 优先于方法论** | R1-R4 防幻觉规则写在所有写作指导之前——学术可信度是底线，不是建议 |
| **从材料出发** | 方法论始终强调"论点从材料内部生长"，而不是先选理论再找材料印证 |
| **确定性校验优先** | 文本评估用正则匹配 + 术语表比对，不依赖模型自我判断——模型检查自己等于没检查 |
| **查不到就搜** | 理论框架速查和术语对照表都内置了兜底机制：表里没有 → 联网搜 → 拼音+解释兜底 |

---

## ⚠️ 注意事项

- **这是写作辅助工具，不是论文代写工具。** Skill 帮你理清思路、检查问题、搜索文献，但核心论点和原创分析必须来自你自己
- **所有生成内容都需要人工核实。** 尤其是文献信息（作者、标题、年份、页码），即使有防幻觉规则，仍然建议逐条在知网或 Google Scholar 中验证
- **搜索脚本依赖网站结构。** 知网、万方等数据源通过网页解析获取结果，如果网站改版可能需要更新脚本
- **理论框架和术语表会持续扩充。** 目前覆盖 16 位理论家、224 条术语，欢迎 PR 补充你所在领域的内容

---

## 🤝 贡献

欢迎以下类型的贡献：

- 🔧 **新数据源脚本**——你常用的学术数据库不在列表里？写一个 `source_xxx.py` 提 PR
- 📖 **理论家 / 术语补充**——编辑 `references/theory-frameworks.md` 或 `terminology-bilingual.md`
- 🔍 **评估规则**——发现了 AI 写学术论文的新型错误模式？往 `review_rules.py` 里加一条
- 🌐 **多语言支持**——目前以中文论文为主，欢迎适配英文、日文等学术写作规范
- 🐛 **Bug 修复**——搜索脚本解析失败、评估规则误报等

---

<div align="center">

**MIT License**

<sub>给每一个在深夜和论文搏斗的人文社科研究者。</sub>

</div>
