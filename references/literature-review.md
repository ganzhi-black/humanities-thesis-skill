# 文献综述与搜索策略

文献综述不是罗列"谁说了什么"，而是建立你的论文在学术对话中的位置。

---

## 搜索策略

按以下顺序逐步缩小范围：

1. **核心关键词搜索**：用研究对象+核心概念搜索（如"鲁迅 创伤叙事 研究"），先获得领域全貌
2. **理论方向搜索**：用理论家名字+研究对象搜索（如"本雅明 寓言 中国现代文学"），找到理论运用的先例
3. **近五年动态搜索**：加上年份限定，了解最新研究走向
4. **英文文献补充**：用英文关键词搜索同一主题的海外研究，拓宽视野

**搜索工具选择**（按优先级）：
1. 如果当前环境支持执行 Python 脚本，运行 `scripts/search.py` 自动聚合多个学术数据库
2. 如果当前环境有联网搜索能力（如 Claude、GPT 联网模式），直接搜索
3. 都没有的话，引导用户前往以下数据库按此策略自行检索

**推荐学术数据库**：
- 中文文献：中国知网（CNKI）、万方数据、维普、读秀
- 英文文献：Google Scholar、JSTOR、Project MUSE、Web of Science
- 开放获取：Semantic Scholar、Academia.edu

每次搜索后，帮用户筛选：这篇文献和我的论文是什么关系？是要对话的对手、可以借力的盟友、还是需要补充的空白？

---

## 文献综述的组织方式

不要按时间顺序罗列文献，而是按**论证功能**分组：

| 功能 | 作用 | 写法 |
|------|------|------|
| 奠基型 | 确立研究领域的基本共识 | "关于X，学界已形成共识：……" |
| 对话型 | 展示你要介入的争论 | "A认为……，B则提出……，但双方都忽略了……" |
| 空白型 | 指出你的论文填补什么 | "已有研究较少追问……，而这恰恰是理解X的关键" |

文献综述的最后一段必须落到**你的论文要做什么**——读者读完综述后应该自然理解：为什么需要你这篇论文。

---

## 脚本工具：学术文献搜索

`scripts/` 目录包含一套 Python 脚本，可以自动聚合多个学术数据库进行文献搜索。

### 支持的数据源

| 数据源 | 脚本文件 | 是否需要配置 | 说明 |
|--------|---------|-------------|------|
| 国家哲社文献中心 | `sources/source_ncpssd.py` | 无需配置 | **人文社科首选**，2,400+种核心期刊，完全免费 |
| 知网 CNKI | `sources/source_cnki.py` | 需要 Cookie | 中文文献最全，需从浏览器复制 Cookie |
| 万方数据 | `sources/source_wanfang.py` | 无需配置 | 中文文献补充 |
| OpenAlex | `sources/source_openalex.py` | 无需配置 | 2.5亿+论文，Scopus 的免费替代品 |
| CORE | `sources/source_core.py` | 无需配置 | 3亿+开放获取论文，可获取全文 |
| Google Scholar | `sources/source_google_scholar.py` | 推荐配置 SerpAPI Key | 综合学术搜索 |
| Semantic Scholar | `sources/source_semantic_scholar.py` | 无需配置 | 英文文献，免费公开 API |
| CrossRef | `sources/source_crossref.py` | 无需配置 | 通过 DOI 获取英文文献元数据 |

### 使用方式

```bash
# 搜索所有可用数据源
python scripts/search.py "鲁迅 创伤叙事"

# 指定数据源
python scripts/search.py "鲁迅 创伤叙事" --sources cnki,wanfang

# 查看数据源配置状态
python scripts/search.py --list-sources
```

### 配置方式

将 `scripts/.env.example` 复制为 `scripts/.env`，填入对应的 Key 或 Cookie。没有配置的数据源会被自动跳过。

### 在 Agent 工作流中调用

```python
from scripts.search import search_to_json
result = search_to_json("鲁迅 创伤叙事", sources=["cnki", "semantic_scholar"], limit=10)
```

返回标准化 JSON，包含标题、作者、年份、摘要、引用次数等字段。
