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

从选题到投稿的 **全流程方法论指导** + **21 条规则的文本评估引擎** + **350+ 条术语对照表**

不是帮你"写"论文——是帮你**想清楚**论文该怎么写，然后检查你写的每一段是否站得住脚。

<br>

[⚡ 快速开始](#-快速开始) · [🧠 核心能力](#-核心能力) · [🔬 文本评估](#-文本评估引擎) · [📚 文献工作流](#-文献搜索与分析) · [📂 项目结构](#-项目结构) · [🎯 设计原则](#-设计原则)

</div>

---

## ⚡ 快速开始

### 方式一：直接粘贴（最简单，适合所有平台）

1. 打开 `SKILL.md` 文件，全选复制
2. 粘贴到你用的 AI 平台里：
   - **Coze（扣子）** → 创建 Bot → 粘贴到"人设与回复逻辑"
   - **Kimi / 豆包 / 通义千问** → 直接发给它说"请按照这个指导帮我写论文"
   - **ChatGPT** → 创建 GPTs → 粘贴到 Instructions
3. `references/` 文件夹里的参考资料按需投喂——要选理论框架就发 `theory-frameworks.md`，要查术语就发 `terminology-bilingual.md`

### 方式二：作为 Skill 安装（Claude Code / OpenClaw）

打开你的 Agent，说：

> 帮我安装这个 skill：`https://github.com/ganzhi-black/humanities-thesis-skill`

Agent 会自动读取 SKILL.md 并加载全部功能。

### 方式三：命令行工具

```bash
git clone https://github.com/ganzhi-black/humanities-thesis-skill
cd humanities-thesis-skill
pip install -r requirements.txt

# 搜索英文学术文献（通过免费 API）
python scripts/search.py "trauma narrative Chinese literature"

# 检查论文文本质量
python scripts/review.py paper.md
```

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

**英文文献自动搜索**<br>
<sub>OpenAlex · Semantic Scholar · CORE · CrossRef（免费 API，稳定可靠）</sub>

**中文文献：用户搜索 + AI 分析**<br>
<sub>引导用户在知网/NCPSSD搜索导出，AI负责解析、拆解、整合</sub>

**五层文献拆解法**<br>
<sub>元信息 → 论证结构 → 证据标记 → 关系定位 → 交叉比对</sub>

</td>
<td>

**R1-R4 防幻觉硬规则**<br>
<sub>不编造文献、不虚构引文、不捏造数据</sub>

**21 条文本评估规则**<br>
<sub>六个维度：可信度 · 术语 · 格式 · 语体 · 论证逻辑 · 结构</sub>

**350+ 条术语对照表**<br>
<sub>覆盖 19 个学科：文学、历史、哲学、社会学、传播学、新闻学……</sub>

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
| 🟣 **论证逻辑** | L-01 ~ L-08 | 连续断言无论证连接、并列堆砌无递进、引文后缺分析、因果前提未论证、总结句概念堆砌、强度词缺论据 |
| ⚪ **结构** | ST-01 ~ ST-02 | 缺摘要/关键词/参考文献、引言缺论点句 |

---

## 📚 文献搜索与分析

### 英文文献：自动搜索

通过免费公开 API 搜索，稳定可靠，零配置即可使用：

```bash
python scripts/search.py "trauma narrative Chinese literature"
```

| 数据源 | 说明 |
|--------|------|
| 🌐 OpenAlex | 2.5亿+论文，Scopus 的免费替代品 |
| 🌐 Semantic Scholar | Allen AI 提供，免费公开 API |
| 🌐 CORE | 3亿+开放获取论文 |
| 🌐 CrossRef | DOI 元数据查询 |

### 中文文献：用户搜索 + AI 分析

知网、Google Scholar 等平台反爬机制较强，自动抓取不稳定。推荐的工作流是：

1. **你自己搜** — 在知网/国家哲社文献中心/万方搜索
2. **导出或复制** — 导出文献列表（txt/Endnote格式），或直接复制搜索结果
3. **交给 AI** — 上传文件或粘贴到对话中
4. **AI 来分析** — 解析、筛选、拆解、整合文献，撰写文献综述

这其实更符合真实的学术研究流程——研究者本来就是自己搜文献，AI 的价值在于帮你**分析和写作**。

### 文献拆解

筛选出核心文献后，用五层拆解法榨干每篇文献的价值：

1. **元信息提取** — 标题、作者、论点、方法、关键词
2. **论证结构拆解** — 问题→立场→论证路径→结论
3. **证据与引文标记** — 可引用的论点/数据/方法，附页码
4. **与你论文的关系定位** — 理论基础/对话对象/反面论据
5. **交叉比对** — 多篇文献之间的共识、分歧与空白

---

## 📂 项目结构

```
humanities-thesis-skill/
├── SKILL.md                            # 核心指令（agent 启动时加载）
├── README.md                           # 本文件
├── LICENSE                             # MIT License
├── requirements.txt                    # Python 依赖
├── .gitignore                          # 忽略 .env 等敏感文件
│
├── references/                         # 📚 参考文档（按需加载，节省 token）
│   ├── writing-templates.md            #   写作模板与正反面示范（269行）
│   ├── theory-frameworks.md            #   理论家速查（20 位，含兜底搜索策略）
│   ├── terminology-bilingual.md        #   术语对照表（350+ 条，19 个学科）
│   ├── formatting-guide.md             #   格式规范（字体字号、脚注、参考文献）
│   ├── literature-review.md            #   文献综述方法 + 搜索策略
│   ├── literature-analysis.md          #   核心文献五层拆解法
│   ├── material-integration.md         #   散碎材料 → 完整论文工作流
│   ├── english-translation.md          #   英文翻译与投稿准备
│   ├── text-review.md                  #   文本评估维度说明
│   └── platform-guide.md              #   Agent 适配说明
│
└── scripts/                            # 🔧 Python 工具链
    ├── search.py                       #   文献搜索入口
    ├── review.py                       #   文本评估入口
    ├── .env.example                    #   数据源配置模板
    ├── lib/                            #   公共模块
    │   ├── schema.py                   #     数据模型
    │   ├── http_client.py              #     HTTP 封装（SSL 安全验证）
    │   ├── utils.py                    #     工具函数
    │   ├── query.py                    #     查询预处理（中英双语展开）
    │   ├── score.py                    #     搜索结果评分排序
    │   ├── dedupe.py                   #     跨数据源去重
    │   ├── render.py                   #     输出渲染
    │   ├── citation.py                 #     引文自动生成
    │   └── review_rules.py             #     文本评估规则引擎（21 条）
    └── sources/                        #   数据源模块
        ├── source_openalex.py          #     OpenAlex（免费）
        ├── source_semantic_scholar.py  #     Semantic Scholar（免费）
        ├── source_core.py              #     CORE（免费）
        ├── source_crossref.py          #     CrossRef（免费）
        ├── source_cnki.py              #     知网（实验性）
        ├── source_ncpssd.py            #     国家哲社文献中心（实验性）
        ├── source_wanfang.py           #     万方（实验性）
        ├── source_google_scholar.py    #     Google Scholar（实验性）
        └── autocli_fetch.py            #     autocli 增强抓取（可选）
```

---

## 🎯 设计原则

| 原则 | 具体做法 |
|------|---------|
| **SKILL.md 保持精简** | 核心指令控制在 250 行以内，其余内容按需从 references/ 加载 |
| **Rules 优先于方法论** | R1-R4 防幻觉规则写在所有写作指导之前——学术可信度是底线 |
| **从材料出发** | 方法论始终强调"论点从材料内部生长"，不是先选理论再找材料印证 |
| **确定性校验优先** | 文本评估用正则匹配 + 术语表比对，不依赖模型自我判断 |
| **搜索与分析分离** | 英文文献自动搜索；中文文献用户搜索、AI分析——各取所长 |
| **查不到就搜** | 理论框架和术语对照表都内置兜底机制：表里没有 → 联网搜 → 拼音+解释兜底 |

---

## ⚠️ 注意事项

- **这是写作辅助工具，不是论文代写工具。** Skill 帮你理清思路、检查问题、搜索文献，但核心论点和原创分析必须来自你自己
- **所有生成内容都需要人工核实。** 尤其是文献信息（作者、标题、年份、页码），即使有防幻觉规则，仍然建议逐条验证
- **中文文献搜索建议手动。** 知网、Google Scholar 的反爬机制较强，脚本自动抓取不稳定，推荐用户自行搜索后将结果交给 AI 分析
- **术语表和理论框架会持续扩充。** 目前覆盖 20 位理论家、350+ 条术语，欢迎 PR 补充

---

## 🤝 贡献

欢迎以下类型的贡献：

- 📖 **理论家 / 术语补充** — 编辑 `references/theory-frameworks.md` 或 `terminology-bilingual.md`
- 🔍 **评估规则** — 发现了 AI 写学术论文的新型错误模式？往 `review_rules.py` 里加一条
- 🔧 **新数据源** — 写一个 `source_xxx.py` 提 PR
- 🐛 **Bug 修复** — 评估规则误报、脚本解析失败等

---

<div align="center">

**MIT License** · Created by [@ganzhi-black](https://github.com/ganzhi-black)

<sub>给每一个在深夜和论文搏斗的人文社科研究者。</sub>

</div>
