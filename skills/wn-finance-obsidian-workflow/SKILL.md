---
name: WN-FINANCE-OBSIDIAN-WORKFLOW
description: Use when the user wants Codex to run the finance Obsidian workflow with no extra prompt. The skill reads the user's Obsidian vault, detects the current time window, and automatically chooses inbox triage, noon review, closing review, daily archive, weekly synthesis, weekly playbook, monthly review, quarterly source review, article-card creation, draft-strategy extraction, or hypothesis-tracking updates for WeChat/IMA finance notes, then writes readable Chinese Markdown outputs to Obsidian and syncs public-safe results to the user's GitHub archive.
---

# WN Finance Obsidian Workflow

## Entry

When this skill is invoked, run `scripts/sync_ima.sh` first, then run `scripts/decide_workflow.sh`. Do not ask the user which workflow to run unless the vault cannot be found.

If `scripts/sync_ima.sh` reports `sync_status=completed`, read recent notes immediately. If it reports `sync_status=timeout`, continue with already-synced notes and mention that sync completion was not confirmed. If it reports `sync_status=skipped` or `sync_status=failed`, continue with already-synced notes and mention the sync status in the final output.

Use the script output to select the workflow. If multiple workflows are due, run the highest priority one first:

```text
quarterly_source_review
monthly_review
weekly_synthesis
weekly_playbook
closing_review
noon_review
daily_triage
inbox_triage
```

For `closing_review`, `daily_triage`, `weekly_synthesis`, and `weekly_playbook`, run `scripts/market_snapshot.py` before writing analysis when TickFlow is configured. After writing Obsidian outputs, run `scripts/audit_artifact_dates.sh`, then run `scripts/github_sync.sh` unless `WN_FINANCE_GITHUB_SYNC=0` or `WN_FINANCE_REPORT_ONLY=1`. If the file date audit fails, fix article-level dates before GitHub sync. If GitHub sync fails, keep the Obsidian write and report the sync status.

For draft-strategy extraction or promotion, use the strategy research validation layer when the idea can be expressed as observable OHLCV, market-regime, sector, or event-proxy conditions. Validation can be manual, script-assisted, or data-source-assisted. Do not block the workflow if market data is unavailable or the idea lacks enough observable conditions.

## Vault

Find the vault in this order:

```text
1. OBSIDIAN_VAULT
2. ~/Library/Application Support/obsidian/obsidian.json
3. /Users/weining.lai/Documents/Obsidian Vault
```

Read notes from the vault. Do not modify raw IMA or source notes unless the user explicitly asks. Write derived outputs only under:

```text
finance-analysis/daily/
finance-analysis/source-cards/
finance-analysis/weekly/
finance-analysis/monthly/
finance-analysis/source-profiles/
finance-analysis/strategy-candidates/
finance-analysis/market-snapshots/
finance-analysis/state/
```

## Write Behavior

Default to writing workflow results into Obsidian. Do not stop at chat-only output unless the user explicitly asks for report-only mode or `WN_FINANCE_REPORT_ONLY=1` is set.

## Output Style

Write human-facing files in polished Markdown with Chinese headings and table headers. Prefer this order: title, short daily note, summary table, then compact sections. Use a natural daily Chinese tone: clear, direct, and easy to read, but do not use jokes, slang, or casual filler. Keep financial boundaries explicit: all author views are hypotheses, not trading instructions.

Use Markdown tables for metadata and triage summaries. Use short paragraphs for "作者怎么看", "我们怎么理解", "接下来怎么观察", and "什么情况说明错了". Avoid long raw key-value blocks in public-facing files. Article cards must still keep these machine-readable audit anchors as plain lines near the top:

```text
published: YYYY-MM-DDTHH:MM:SS
related_notes: ima/...
```

Hypothesis tracking tables must use Chinese column headers, but rows must still start with `| H-... |` and keep the date as the second data column so `scripts/audit_artifact_dates.sh` can audit IDs against dates.

Use these output files:

```text
inbox_triage: finance-analysis/daily/YYYY-MM-DD.md
noon_review: finance-analysis/daily/YYYY-MM-DD.md
closing_review: finance-analysis/daily/YYYY-MM-DD.md
daily_triage: finance-analysis/daily/YYYY-MM-DD.md
weekly_synthesis: finance-analysis/weekly/YYYY-WW.md
weekly_playbook: finance-analysis/weekly/YYYY-WW-playbook.md
monthly_review: finance-analysis/monthly/YYYY-MM.md
quarterly_source_review: finance-analysis/source-profiles/YYYY-QN.md
source-card: finance-analysis/source-cards/YYYY-MM-DD__author__title.md
strategy-candidate: finance-analysis/strategy-candidates/YYYY-MM-DD__strategy-name.md
market-snapshot: finance-analysis/market-snapshots/YYYY-MM-DD.md
hypothesis-ledger: finance-analysis/state/hypothesis-ledger.md
```

For article-level files, `YYYY-MM-DD` must be the article `published` date from source frontmatter, not the IMA `created` date, filesystem creation date, sync date, or workflow run date. If a source note has no parseable `published` value, mark the item as `needs-published-date` and do not create an article card, draft strategy, or hypothesis tracking row for that article.

Create missing directories before writing. For daily, weekly, monthly, and quarterly workflow files, overwrite the section for the same workflow/date when rerun and preserve unrelated sections. For source cards and strategy candidates, create a new file if absent and update the same file if the same source note is processed again. For hypothesis ledger, append new rows and avoid duplicate source/title/hypothesis rows.

After article-level files are written or updated, run:

```text
scripts/audit_artifact_dates.sh
```

The audit must return `artifact_date_audit=ok` before syncing to GitHub. It checks article-card file dates, card `published` fields, related IMA note `published` values, and hypothesis-tracking `id/date` consistency.

## GitHub Archive

Default repository:

```text
repo_path: /Users/weining.lai/Documents/stock/wn-finance-analyst-result
repo_url: https://github.com/WeiningLai/wn-finance-analyst-result.git
branch: default branch from repository
auto_commit: yes
auto_push: yes
sync_raw_articles: no
public_safe: yes
git_user_name: weining
git_user_email: weininglai@qq.com
ssh_key: ~/.ssh/wn_finance_analyst_result_ed25519
```

Only sync derived output directories:

```text
finance-analysis/
```

Never copy IMA source notes, raw clippings, or full article text into the GitHub archive unless the user explicitly sets `WN_FINANCE_SYNC_RAW_ARTICLES=1`. With `public_safe=yes`, keep outputs limited to analysis, source file names, article titles, author names, hypothesis rows, signals, invalidation conditions, and strategy candidates; avoid long verbatim excerpts from source articles.

Use `scripts/github_sync.sh` after all derived Obsidian outputs for the run have been written. The script clones the archive repo if missing, pulls the selected branch with rebase, mirrors allowed derived directories from the vault, commits changed files, and pushes when enabled. Environment overrides:

```text
WN_FINANCE_GITHUB_REPO_PATH
WN_FINANCE_GITHUB_REPO_URL
WN_FINANCE_GITHUB_BRANCH
WN_FINANCE_GITHUB_AUTO_COMMIT
WN_FINANCE_GITHUB_AUTO_PUSH
WN_FINANCE_GITHUB_SYNC
WN_FINANCE_GITHUB_USER_NAME
WN_FINANCE_GITHUB_USER_EMAIL
WN_FINANCE_GITHUB_SSH_KEY
WN_FINANCE_PUBLIC_SAFE
WN_FINANCE_SYNC_RAW_ARTICLES
```

## Market Data

Optional TickFlow market snapshots provide A-share market verification for review workflows. Configure the key outside the skill by using one of:

```text
WN_TICKFLOW_API_KEY
TICKFLOW_API_KEY
macOS Keychain service: wn-finance-tickflow
```

Do not write API keys to Obsidian, GitHub, SKILL.md, README, or committed files. Run:

```text
scripts/market_snapshot.py
```

The script writes `finance-analysis/market-snapshots/YYYY-MM-DD.md` with main A-share indices, market breadth, limit-up/limit-down counts, and turnover when available. If TickFlow is not configured, not installed, or the current plan lacks `CN_Equity_A` universe permission, continue the workflow and record the snapshot status. Use snapshots only to verify market regime, breadth, turnover, and index structure; do not convert them into direct buy or sell instructions.

## Strategy Research Validation

Use this layer to convert high-quality article hypotheses into observable research ideas and attach validation evidence to Obsidian files. The borrowed pattern is: thesis -> observable rule -> validation sample -> research verdict -> promotion or rejection. Use it only after preserving the separation between original author view, Codex synthesis, observable signal, invalidation condition, and user-actionable hypothesis.

When creating or updating a draft strategy file, add validation fields when applicable:

```text
validation_status: text_only | observable_draft | blocked_data | sample_checked | rejected | watchlist_candidate | promoted
rule_id:
observable_conditions:
sample_period:
data_quality:
validation_metrics:
robustness_check:
review_lenses:
validation_artifacts:
next_validation_step:
```

Mapping rules:

```text
core_logic -> strategy description and thesis
entry_filter/add_filter -> entry triggers and guards
reduce_or_exit_filter/invalidation -> exit triggers, stop loss, take profit, max holding days
applicable_regime -> preferred_regime
common_failure -> failure pattern to test in backtest and review
promotion_requirement -> minimum validation gate
```

Validation gates for promotion:

```text
minimum status: sample_checked
data_quality: acceptable for the stated claim
regime_fit: stated and not contradicted by available market snapshots
signal_count: enough for the stated timeframe, normally >= 30 unless explicitly marked small-sample
robustness_check: no obvious small-sample, hindsight, single-source, market-regime, or overfitting failure
review_lenses: data_quality, regime_fit, risk_reward, robustness, and actionability are pass or watch, not fail
source evidence: at least article-card level, not a single intraday note
```

If the rule cannot be represented as observable conditions, keep `validation_status: text_only` and state the missing observable signal. If market data is blocked, keep `validation_status: blocked_data` and do not infer validation. Do not write raw article text, API keys, private notes, or full LLM prompts into reports synced to GitHub.

## Single-Target Feedback Loop

Stock Analysis may write or propose single-target observations derived from real trades, support/resistance tests, volume behavior, invalidation events, or user-confirmed actions. Treat these observations as evidence inputs, not final research verdicts.

Accepted feedback destinations:

```text
- finance-analysis/daily/YYYY-MM-DD.md under single-target observations
- finance-analysis/state/hypothesis-ledger.md as evidence rows or review notes
- related draft-strategy files under observation_log or validation_artifacts when the observation maps to existing observable_conditions
```

Do not let one intraday observation promote, reject, or materially rewrite a strategy candidate. Promotion, rejection, or hypothesis status changes must happen in daily_triage, weekly_synthesis, weekly_playbook, or monthly_review after checking evidence quality, regime fit, robustness, and source context.

## Core Rules

- Output code/data blocks first; explanation only if needed.
- Always try IMA sync before selecting the workflow unless `WN_FINANCE_SKIP_SYNC=1`.
- Treat all blogger views as hypotheses, not facts.
- Separate original author view, Codex synthesis, observable signal, invalidation condition, and user-actionable hypothesis.
- Human-facing file headings and table headers should be in Chinese.
- Prefer readable Markdown sections over raw English field names. Keep `published:` and `related_notes:` anchors in article cards for audit compatibility.
- Skip IMA warning blocks that start with `> [!warning] 由于目标网站限制`.
- Prefer recent IMA notes under `ima/个人知识库/` and finance clippings under `Clippings/`.
- Do not provide direct buy or sell instructions.
- Do not let a single intraday note create or change an active strategy.
- Do not let a single Stock Analysis observation promote, reject, or rewrite a strategy candidate.
- Use market snapshots to confirm or challenge article hypotheses, not to create trade instructions.
- For time-sensitive claims, use concrete dates.
- For each article, use the `published` frontmatter date as the article date. Do not use `created`, file ctime, sync time, or workflow run date for article-level dates.
- If content is insufficient, mark the note as `needs-full-content`; do not infer missing article text.
- If `published` is missing or invalid, mark the note as `needs-published-date` and skip article-level derived files until the date is available.
- Keep GitHub archive output public-safe by default and do not include raw IMA article bodies.

## Workflow Selection

After running `scripts/decide_workflow.sh`, read `references/workflows.md` for the selected workflow and `references/output-contract.md` for the required output format.

If the selected workflow is `inbox_triage`, read only recent notes first. If high-value articles are found, write the triage file and create recommended article cards, draft strategies, or hypothesis tracking rows when the evidence standard requires them.

## Evidence Standard

Use this scoring for each article:

```text
thesis clarity: 1-5
evidence quality: 1-5
verifiability: 1-5
strategy transferability: 1-5
counterargument awareness: 1-5
current relevance: 1-5
```

Processing rule:

```text
score <= 12: archive only
13-18: daily-note
19-24: can become an article card
25-30: can become an article card and enter the hypothesis tracking list
```
