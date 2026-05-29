# wn-finance-analyst-result

Codex finance workflow output archive. This repository stores public-safe derived analysis generated from the local Obsidian finance workflow, not raw WeChat articles, IMA source notes, or full clipping text.

## Scope

The source workflow reads curated finance notes from the local Obsidian vault, classifies recent articles, extracts reusable hypotheses, and writes derived outputs back to Obsidian before mirroring selected result directories here.

Synced directories:

```text
50-decisions/
40-distillations/
30-strategies/
_agent/state/
```

Excluded content:

```text
ima/
Clippings/
raw article bodies
full source-note copies
private Obsidian configuration
```

## Output Principles

All author views are treated as hypotheses, not facts or trading instructions. Outputs separate original author views, Codex synthesis, observable signals, invalidation conditions, and follow-up review points. Public-safe records may include article titles, author names, source file names, summarized claims, hypothesis rows, and strategy candidates, but should not include long verbatim excerpts from source articles.

## Commit Identity

This repository uses local Git configuration only:

```text
user.name=weining
user.email=weininglai@qq.com
core.sshCommand=ssh -i ~/.ssh/wn_finance_analyst_result_ed25519 -o IdentitiesOnly=yes
```

Global Git identity remains unchanged.
