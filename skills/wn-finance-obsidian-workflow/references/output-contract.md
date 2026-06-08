# 输出契约

## 总体排版

输出文件面向人阅读，默认用中文标题、中文表头和清晰 Markdown。语气可以日常一点，像给自己做投资复盘笔记：直接、好懂、有边界。不要写成交易指令，不要复述大段原文。避免使用偏内部的词；面向人时用“假设追踪清单、文章卡片、输出文件”这类一看就懂的说法。

常用结构：

```markdown
# 标题

> 一句话说明这份笔记在做什么。所有观点都当作待验证假设，不直接构成买卖建议。

## 速览

| 项目 | 内容 |
| --- | --- |

## 正文分区

### 小标题

短段落说明。
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

## 盘中和收盘面板

```markdown
# YYYY-MM-DD 盘面复盘

## 速览

| 项目 | 内容 |
| --- | --- |
| 市场状态 | market_regime |
| 盘中观点 | intraday_views |
| 已确认信号 | confirmed_signals |
| 主要冲突 | conflicts |
| 明日观察 | tomorrow_watch |
| 归档决定 | archive_decisions |
```

## 文章卡片

Article card 必须保留 `published:` 和 `related_notes:` 两个顶格字段，供审计脚本读取。其余内容用中文标题和中文表头：

```markdown
published: article frontmatter published date, never created date
related_notes: ima/...

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
