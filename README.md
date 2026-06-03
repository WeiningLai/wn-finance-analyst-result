# wn-finance-analyst-result

Codex 财经工作流分析结果归档仓库。本仓库只保存本地 Obsidian 财经工作流生成的公开安全派生产物，不保存微信公众号原文、IMA 源笔记或完整剪藏正文。

## 范围

源工作流读取本地 Obsidian vault 中人工精选的财经笔记，对近期文章分类评分，提取可复用假设，并先将派生产物写回 Obsidian，再把指定结果目录镜像到本仓库。

同步目录：

```text
50-decisions/
40-distillations/
30-strategies/
_agent/state/
```

排除内容：

```text
ima/
Clippings/
原始文章正文
完整源笔记副本
私有 Obsidian 配置
```

## 输出原则

所有作者观点都按假设处理，不视为事实或交易指令。输出需要区分原作者观点、Codex 归纳、可观察信号、失效条件和后续复盘点。公开安全记录可以包含文章标题、作者名、来源文件名、观点摘要、假设台账行和策略候选，但不应包含源文章的大段原文摘录。

文章级产物必须使用源笔记 frontmatter 中的 `published` 日期，不使用 IMA `created` 日期、文件创建日期、同步日期或工作流运行日期。适用范围包括 source-card 文件名前缀、strategy-candidate 文件名前缀、hypothesis-ledger 的 `id/date`、文章分类记录中的 `published` 字段；如果源笔记缺少可解析的 `published`，应标记为 `needs-published-date`，并暂不生成文章级派生产物。

## 产物说明

这些产物不是交易答案，而是一个假设管理系统。它把人工精选文章拆成可观察、可验证、可失效、可复盘的记录，用于降低盘中临时起意和单篇文章带来的决策噪音。

### 50-decisions/daily/

日级工作台，用于记录当天文章分流、盘中观点、收盘验证和次日观察项。常用文件为 `50-decisions/daily/YYYY-MM-DD.md`。

重点字段：

```text
author_view: 原作者观点
observable_signal: 可观察信号
invalidation: 失效条件
confirmed_signals: 已确认信号
conflicts: 冲突观点
tomorrow_watch: 次日观察项
archive_decisions: 归档决策
```

使用方式：盘前查看昨日 `tomorrow_watch`，盘中只看信号和失效条件，收盘后看观点是否被市场验证。不要把 daily 产物当成买卖指令，它只回答“今天哪些假设值得观察，哪些观点已经失效或需要降权”。

### 40-distillations/weekly/

周级归纳目录，用于把一周内的文章、source-card 候选和 daily 记录整理成市场共识、分歧、盲点和下周剧本。

常用文件：

```text
YYYY-WW.md: 本周综合
YYYY-WW-playbook.md: 下周剧本
```

`YYYY-WW.md` 重点看：

```text
weekly consensus: 本周共识
disagreements: 分歧
repeated indicators: 重复出现的指标
market regime assumption: 市场状态假设
blind spots: 盲点
unsupported claims: 未被充分支持的说法
```

`YYYY-WW-playbook.md` 重点看：

```text
base case: 基准情景
bull case: 偏强情景
bear case: 偏弱情景
trigger conditions: 触发条件
invalidation conditions: 失效条件
reasons not to act: 不行动理由
```

使用方式：周五晚用综合文件判断本周主线是否稳定，周日晚用 playbook 准备下周情景预案。playbook 的价值在于提前定义观察条件，而不是盘中追着观点改计划。

### 40-distillations/source-cards/

信息源卡片目录，用于沉淀单个作者或单篇高价值文章的可复用判断框架。

重点字段：

```text
source: 来源
published: 文章 published 时间
one_line_thesis: 一句话核心判断
original_author_view: 原作者观点
evidence_chain: 证据链
hidden_assumptions: 隐含假设
observable_indicators: 可观察指标
trigger_conditions: 触发条件
invalidation_conditions: 失效条件
risks_and_counterarguments: 风险和反方观点
reusable_strategy_pattern: 可复用策略模式
related_notes: 关联笔记
```

使用方式：不要按作者结论跟随，而是评估作者在哪类行情、板块、时间窗口里更有参考价值。source-card 用于回答“这个信息源擅长什么、容易错在哪里、观点什么时候应该降权”。

### 30-strategies/candidates/

策略候选目录，用于保存还没有升级为稳定策略的交易框架雏形。

重点字段：

```text
applicable_regime: 适用市场状态
core_logic: 核心逻辑
entry_filter: 进入过滤
add_filter: 加仓过滤
reduce_or_exit_filter: 降仓或退出过滤
invalidation: 失效条件
position_limit: 仓位限制
common_failure: 常见失败方式
promotion_requirement: 升级要求
```

使用方式：strategy-candidate 只是观察对象，不是可直接执行的策略。只有当多个来源、多个交易日和复盘记录共同支持时，才考虑升级；单篇文章或单次盘中观点不能直接改变主动策略。

### _agent/state/hypothesis-ledger.md

假设台账，用于持续跟踪观点是否被确认、失效或需要继续观察。这是长期复盘中最重要的文件。

重点字段：

```text
id: 假设编号
date: 建立日期
source: 来源
hypothesis: 假设内容
asset_or_sector: 资产或板块
timeframe: 时间窗口
confirm_signal: 确认信号
invalidate_signal: 失效信号
review_date: 复盘日期
status: 状态
```

使用方式：月底或阶段性复盘时逐条检查假设状态。有效假设可以保留或升级，失效假设需要记录原因，长期无法验证的假设应降权。该文件的作用是让观点接受时间检验，而不是只保留当时看起来合理的叙述。

## 使用节奏

```text
盘前: 查看 weekly_playbook 和昨日 daily 的 tomorrow_watch
盘中: 只使用 noon_review 或 closing_review 中的观察信号和失效条件
收盘后: 查看 daily_triage，将文章分流为 ignore、daily-note、source-card、hypothesis-ledger 或 strategy-candidate
周五晚: 查看 weekly_synthesis，识别本周共识、分歧和盲点
周日晚: 查看 weekly_playbook，形成下周情景预案
月底: 查看 hypothesis-ledger，复盘哪些假设确认、失效或需要降权
季度末: 查看 source-profiles，评估哪些信息源值得继续跟踪
```

## 使用边界

本仓库记录的是研究过程和假设状态，不提供直接买入、卖出或仓位指令。任何产物都必须结合市场实时数据、个人风险约束和独立判断使用；当产物中的观察信号和失效条件冲突时，优先记录冲突并降低假设权重，而不是补充不存在的确定性。

## 提交身份

本仓库只使用局部 Git 配置：

```text
user.name=weining
user.email=weininglai@qq.com
core.sshCommand=ssh -i ~/.ssh/wn_finance_analyst_result_ed25519 -o IdentitiesOnly=yes
```

全局 Git 身份保持不变。
