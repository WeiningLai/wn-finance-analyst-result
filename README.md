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

## 提交身份

本仓库只使用局部 Git 配置：

```text
user.name=weining
user.email=weininglai@qq.com
core.sshCommand=ssh -i ~/.ssh/wn_finance_analyst_result_ed25519 -o IdentitiesOnly=yes
```

全局 Git 身份保持不变。
