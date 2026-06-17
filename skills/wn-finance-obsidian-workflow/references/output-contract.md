# 输出契约

## 总体排版

输出文件面向人阅读，默认用中文标题、中文表头和清晰 Markdown。语气可以日常一点，像给自己做投资复盘笔记：直接、好懂、有边界。不要写成交易指令，不要复述大段原文。避免使用偏内部的词；面向人时用“假设追踪清单、文章卡片、输出文件”这类一看就懂的说法。

daily、weekly、monthly、playbook 等周期性输出必须使用同一套资料骨架。不同工作流可以扩展正文分区，但不能省略“速览”“资料闭环”“正文分区”“下次复盘”四块。每份输出都要能回答：本次读了什么、得出什么结论、哪些进入知识库、哪些需要复盘、什么情况说明错了。

通用资料骨架：

```markdown
# 标题

> 一句话说明这份笔记在做什么。所有观点都当作待验证假设，不直接构成买卖建议。

## 速览

| 项目 | 内容 |
| --- | --- |
| 工作流 | workflow_name |
| 覆盖范围 | date_or_period |
| 输入材料 | notes/cards/snapshots |
| 本次结论 | one_line_result |
| 同步或数据状态 | sync/data status |

## 资料闭环

| 项目 | 内容 |
| --- | --- |
| 已进入知识库 | article cards / hypotheses / strategies / source profiles |
| 新增或更新假设 | H-id or 暂无 |
| 需要复盘 | review items with date |
| 暂不采纳 | unsupported claims |
| 下次检查 | concrete next review action |

## 正文分区

### 小标题

短段落说明。

## 下次复盘

| 日期 | 要检查什么 | 触发动作 |
| --- | --- | --- |
```

## 文章分拣

Daily inbox triage 使用这种结构：

```markdown
# YYYY-MM-DD 文章分拣

> 今天先把同步进来的文章分好类。这里记录的是观点和验证线索，不是买卖建议。

## 速览

| 项目 | 内容 |
| --- | --- |
| 工作流 | inbox_triage |
| 条目数 | N |
| 本次结论 | one_line_result |

## 资料闭环

| 项目 | 内容 |
| --- | --- |
| 已进入知识库 | article cards N, hypotheses N, strategy candidates N |
| 新增或更新假设 | H-id list or 暂无 |
| 需要复盘 | review dates and ids |
| 暂不采纳 | needs-full-content / needs-published-date / low score |
| 下次检查 | next_action |

## 分拣结果

### 1. 《文章标题》

| 项目 | 内容 |
| --- | --- |
| 作者 | author |
| 发布时间 | published |
| 文件 | file |
| 分类 | A/B/C/D/E |
| 评分 | score |
| 主题 | topic |
| 下一步 | next_artifact |
| 资料状态 | closed_to_card / closed_to_hypothesis / daily_only / blocked |
| 复盘日期 | YYYY-MM-DD or 暂无 |

**作者怎么看**  
author_view

**证据和观察**  
evidence

**可以怎么验证**  
observable_signal

**什么情况说明错了**  
invalidation

**处理理由**  
reason
```

每个分拣条目必须闭环到一个明确结果：忽略、日报记录、文章卡片、假设追踪、待验证策略、需要完整正文、需要发布时间。不能只写“值得关注”而不写后续去向。

## 小红书来源接入

Daily Xiaohongshu intake 使用这种结构。不要写入完整原文，不要写入带 `xsec_token` 的签名 URL：

```markdown
## 小红书来源接入

| 项目 | 内容 |
| --- | --- |
| 工作流 | xiaohongshu_source_ingest |
| 来源 | note/profile |
| 读取数量 | N |
| 已知重复 | N |
| 本次新增 | N |
| 成功 | N |
| 失败 | N |
| 时间依据 | source_published/fetched_at |

## 资料闭环

| 项目 | 内容 |
| --- | --- |
| 已进入知识库 | source cards N, hypotheses N, source profile status |
| 已跳过重复 | note ids or count |
| 需要复盘 | source quality review date |
| 暂不采纳 | unreadable or duplicate notes |
| 下次检查 | next profile refresh rule |

### 1. 《笔记标题》

| 项目 | 内容 |
| --- | --- |
| 平台 | 小红书 |
| 作者 | author |
| 发布时间 | published |
| 时间依据 | published_basis |
| 笔记编号 | note_id |
| 互动 | likes / collects / comments |
| 标签 | tags |
| 分类 | A/B/C/D/E |
| 评分 | score |
| 主题 | topic |
| 下一步 | next_artifact |
| 资料状态 | closed_to_card / closed_to_hypothesis / daily_only / duplicate / blocked |
| 复盘日期 | YYYY-MM-DD or 暂无 |

**作者怎么看**  
author_view

**我们怎么理解**  
synthesis

**可以怎么验证**  
observable_signal

**什么情况说明错了**  
invalidation

**处理理由**  
reason
```

## 盘中和收盘面板

```markdown
# YYYY-MM-DD 盘面复盘

## 速览

| 项目 | 内容 |
| --- | --- |
| 工作流 | noon_review / closing_review |
| 覆盖范围 | YYYY-MM-DD |
| 市场状态 | market_regime |
| 盘中观点 | intraday_views |
| 已确认信号 | confirmed_signals |
| 主要冲突 | conflicts |
| 明日观察 | tomorrow_watch |
| 归档决定 | archive_decisions |

## 资料闭环

| 项目 | 内容 |
| --- | --- |
| 已确认 | confirmed ids or signals |
| 已证伪 | invalidated ids or signals |
| 延后观察 | items with next date |
| 需要写入 | hypothesis / rules / false-beliefs / none |
```

## Weekly 固定格式

weekly 目录只允许两类文件名：

```text
finance-analysis/weekly/YYYY-WW__周复盘.md
finance-analysis/weekly/YYYY-WW__周计划.md
```

这两类文件必须使用同一组一级标题。允许在内容里体现复盘和计划的差异，但标题顺序必须一致。weekly 文件要先让人读懂，再让 AI 解析：`本周主线` 必须用短段落写清发生了什么、我们怎么看、什么情况说明错了；表格只用于对比、闭环和审计。

weekly 表格最多 4 列。超过 4 列时，删掉系统路由类信息，或改成短段落。假设编号和规则编号第一次出现时必须带一句话解释，例如 `H-20260611-001（半导体和 PCB 材料第二波需要量价结构支持）`；后续可以只写编号。`下次复盘` 的触发动作必须写成具体条件和操作，不写只有确认、延后、降权的状态枚举。

```markdown
# YYYY-WW 周复盘 / YYYY-WW 周计划

> 一句话说明这篇 weekly 的用途。所有结论都需要后续验证，不构成买卖建议。

## 速览

| 项目 | 内容 |
| --- | --- |
| 一句话结论 | one_line_result |
| 目标周 | YYYY-WW |
| 覆盖范围 | YYYY-MM-DD 至 YYYY-MM-DD |
| 输入材料 | source cards N, daily N, snapshots N |
| 数据状态 | sync/snapshot status |

## 本周主线

2-3 个短段落，不用表格。周复盘写清本周发生了什么、博主共识和分歧是什么、我们的结论和失效条件是什么。周计划写清本周要验证什么、基础/乐观/悲观情景是什么、最容易误判的地方是什么。

## 资料闭环

| 项目 | 内容 |
| --- | --- |
| 重要依据 | blogger consensus / blogger conflicts |
| 已进入知识库 | concepts / entities / hypotheses / rules / evidence |
| 假设处理 | confirmed / extended / downgraded / still watching |
| 分歧处理 | what to keep, downgrade, or verify |
| 规则处理 | promoted / not promoted with reason |
| 策略候选处理 | promoted / sample needed / rejected / text-only |
| 下次检查 | concrete date and signal |

## 博主共识和分歧

| 类型 | 内容 | 主要证据或本周用法 | 失效或降权条件 |
| --- | --- | --- | --- |

## 核心判断

周复盘用 `### 判断 N：...` 的短段落写，不用大表。每个判断说明依据、使用边界和下一步。周计划用 `### 基础情景`、`### 乐观情景`、`### 悲观情景` 写清观察条件和失效条件。

## 验证指标

| 指标 | 看什么 | 说明错了的情况 |
| --- | --- | --- |

## 假设和规则

| 编号或规则 | 当前含义 | 当前处理或本周验证 | 复盘日期 |
| --- | --- | --- | --- |

## 策略和执行

| 项目 | 当前处理 | 不行动或降权条件 |
| --- | --- | --- |

## 盲点和暂不支持

| 项目 | 为什么重要 | 下次补什么 |
| --- | --- | --- |

## 下次复盘

| 日期 | 要检查什么 | 触发动作 |
| --- | --- | --- |
```

## 文章卡片

文章卡片按月份分目录保存，路径为 `finance-analysis/source-cards/YYYY-MM/YYYY-MM-DD__author__title.md`。原文依据按同样月份分目录保存，路径为 `finance-analysis/source-evidence/YYYY-MM/YYYY-MM-DD__author__title.md`。文章卡片只写分析和闭环，原文依据保存本地原文全文和原始链接，作为后续复盘、质疑和再蒸馏的底层依据。

Article card 必须保留 `published:` 和 `related_notes:` 两个顶格字段，供审计脚本读取。其余内容用中文标题和中文表头：

```markdown
published: article frontmatter published date, never created date
related_notes: ima/...
source_platform: wechat|xiaohongshu
published_basis: source_published|fetched_at

# 《文章标题》

> 一句话主题。

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 来源 | source |
| 发布时间 | published |
| 关联笔记 | related_notes |

## 核心观点

one_line_thesis

## 作者怎么看

original_author_view

## 证据链

evidence_chain

## 隐含前提

hidden_assumptions

## 可以怎么观察

observable_indicators

## 触发条件

trigger_conditions

## 什么情况说明错了

invalidation_conditions

## 风险和反面观点

risks_and_counterarguments

## 可复用模式

reusable_strategy_pattern
```

## 假设追踪清单

表头用中文；数据行仍以 `H-` 开头，日期放在第二列：

```markdown
| 编号 | 日期 | 来源 | 假设 | 资产或板块 | 时间范围 | 确认信号 | 失效信号 | 复盘日期 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

## 小红书来源状态

用于记录一个博主是否值得持续接入：

```markdown
# 小红书来源状态

| 作者 | 别名 | 主页 | profile_url | 默认抓取篇数 | 最近读取 | 上次新增 | 成功 | 失败 | 已处理笔记 | 主要主题 | 当前评价 | 下次复核 |
| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | --- | --- | --- | --- |
```

## 来源画像

`finance-analysis/source-profiles/author.md` 和 `finance-analysis/source-profiles/xiaohongshu__author.md` 用这种结构：

```markdown
# 来源画像：author

> 这里评估来源质量，不记录原文，不构成买卖建议。

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 平台 | platform |
| 作者 | author |
| 已读笔记 | N |
| 最近更新 | YYYY-MM-DD |
| 下次复核 | YYYY-MM-DD |

## 反复出现的主题

短段落。

## 有用的信号

短段落。

## 盲点和噪音

短段落。

## 和现有知识库的关系

短段落。

## 继续跟踪条件

短段落。
```

## 待验证策略

```markdown
# 待验证策略：name

> 研究用，不是买卖建议。只有样本检查通过后，才可能进入观察清单或晋级。

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 发布时间 | published |
| 来源笔记 | source_notes |
| 适用环境 | applicable_regime |
| 验证状态 | validation_status |
| 规则编号 | rule_id |

## 核心逻辑

core_logic

## 入场过滤

entry_filter

## 加仓过滤

add_filter

## 降仓或退出

reduce_or_exit_filter

## 失效条件

invalidation

## 仓位边界

position_limit

## 常见失败方式

common_failure

## 晋级要求

promotion_requirement

## 可观察条件

observable_conditions

## 验证记录

| 项目 | 内容 |
| --- | --- |
| 样本区间 | sample_period |
| 数据质量 | data_quality |
| 验证指标 | validation_metrics |
| 稳健性检查 | robustness_check |
| 评审视角 | review_lenses |
| 验证文件 | validation_artifacts |
| 下一步 | next_validation_step |
```

## 知识库概念页

用于把多张文章卡片和多条假设合并成一个可长期查看的主题页：

```markdown
---
title: concept
type: concept
domain: [investing]
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: medium
---

# concept

> 一句话说明这个主题为什么重要。

## 当前结论

这不是买卖建议，只是当前最佳理解和适用边界。

## 投资使用摘要

| 项目 | 内容 |
| --- | --- |
| 当前看法 | 当前最佳理解 |
| 适用场景 | 什么情况下才参考这个主题 |
| 优先确认 | 后续最该验证的信号 |
| 立即降权 | 什么情况说明需要降低权重 |
| 下一步 | 最近一次复盘要做什么 |

## 相关对象

[[entities/name/profile|name]]

## 关联假设

| 编号 | 日期 | 假设 | 状态 | 复盘日期 |
| --- | --- | --- | --- | --- |

## 来源卡片

| 日期 | 来源 | 文章 | 相关线索 |
| --- | --- | --- | --- |

## 观察指标

- 可被数据或后续文章验证的信号。

## 失效信号

- 什么情况说明这个主题需要降权。
```

## 知识库首页驾驶舱

`overview.md` 不是目录页，而是每次打开知识库时的第一屏：

```markdown
# 投资知识库总览

## 速览

| 项目 | 数量 | 入口 |
| --- | --- | --- |

## 投资参考驾驶舱

### 复盘队列

| 复盘日期 | 编号 | 假设 | 状态 |
| --- | --- | --- | --- |

### 高关注主题

| 主题 | 文章卡片数 | 当前用法 |
| --- | --- | --- |

### 规则状态

| 编号 | 状态 | 缺什么 | 下一步 |
| --- | --- | --- | --- |

### 来源质量

| 来源 | 卡片数 | 主要主题 | 适合怎么用 | 风险 |
| --- | ---: | --- | --- | --- |

### 最近新增

| 日期 | 来源 | 文章 | 核心线索 |
| --- | --- | --- | --- |
```

## 来源质量总表

`source-profiles/source-quality.md` 汇总作者层面的使用边界。它不判断作者“对不对”，只说明该来源适合贡献什么信号，以及需要怎样验证：

```markdown
# 来源质量总表

## 来源速览

| 来源 | 卡片数 | 主要主题 | 适合怎么用 | 风险 |
| --- | ---: | --- | --- | --- |

## 使用规则

- 高频来源只代表样本多，不代表结论更真。
- 同一作者反复出现的观点，可以作为假设来源，但必须回到确认信号和失效信号。
```

## 知识库对象页

用于持续跟踪板块、资产、策略工具或其他投资对象：

```markdown
---
title: entity
type: entity
domain: [investing]
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: medium
aliases: []
judgment: watching
---

# entity

> 这个对象的跟踪重点。

## 当前判断

当前只记录研究判断和验证条件，不直接写成交易指令。

## 相关概念

[[concepts/name|name]]

## 关联假设

| 编号 | 日期 | 假设 | 状态 | 复盘日期 |
| --- | --- | --- | --- | --- |

## 证据来源

| 日期 | 来源 | 文章 | 观察线索 |
| --- | --- | --- | --- |

## 跟踪清单

- 后续必须补证据的问题。
```

## 投资规则和被证伪认知

`rules.md` 只放被多次验证的候选规则或正式规则，不把单篇文章直接提升为规则。`false-beliefs.md` 记录被复盘推翻或需要缩小适用范围的旧认知，格式是“旧认知、现实、来源、适用范围”。

## 单标的观察

```markdown
## 单标的观察：name

| 项目 | 内容 |
| --- | --- |
| 标的 | symbol |
| 日期 | date |
| 时间 | time |
| 关联假设 | related_hypothesis_id |
| 关联策略 | related_strategy_id |
| 市场状态 | market_regime |
| 市场门槛 | market_gate |
| 价格行为 | price_action |
| 成交量信号 | volume_signal |
| 支撑阻力事件 | support_resistance_event |
| 命中条件 | matched_observable_conditions |
| 失效事件 | invalidation_event |
| 已执行动作 | action_taken |
| 观察结果 | observed_result |
| 证据类型 | evidence_type |
| 数据质量 | data_quality |
| 下次检查 | next_check |
| 备注 | notes |
```

## 市场快照

```markdown
# YYYY-MM-DD 市场快照

| 项目 | 内容 |
| --- | --- |
| 获取时间 | fetched_at |
| 来源 | source |
| 范围 | scope |
| 指数 | indices |
| 市场宽度 | market_breadth |
| 成交额 | turnover |
| 涨跌停结构 | limit_structure |
| 数据质量 | data_quality |
| 使用边界 | usage_boundary |
```
