---
name: WN-FINANCE-OBSIDIAN-WORKFLOW
description: Use when the user wants Codex to run the finance Obsidian workflow with no extra prompt. The skill reads the user's Obsidian vault, detects the current time window, and automatically chooses inbox triage, noon review, closing review, daily archive, weekly synthesis, weekly playbook, monthly review, quarterly source review, Xiaohongshu/OpenCLI source intake, article-card creation, draft-strategy extraction, or hypothesis-tracking updates for WeChat/IMA and public finance notes, then writes readable Chinese Markdown outputs to Obsidian and syncs public-safe results to the user's GitHub archive.
---

# WN Finance Obsidian Workflow

## Entry

When this skill is invoked, run `scripts/sync_ima.sh` first, then run `scripts/decide_workflow.sh`. Do not ask the user which workflow to run unless the vault cannot be found.

If `scripts/sync_ima.sh` reports `sync_status=completed`, read recent notes immediately. If it reports `sync_status=timeout`, continue with already-synced notes and mention that sync completion was not confirmed. If it reports `sync_status=skipped` or `sync_status=failed`, continue with already-synced notes and mention the sync status in the final output.

If the user supplies a Xiaohongshu URL, `xhslink.com` short link, Xiaohongshu profile URL, or asks to import or update a Xiaohongshu blogger, run `xiaohongshu_source_ingest` instead of the time-window workflow after any required source fetch. Read `references/xiaohongshu.md` and use OpenCLI. If the user gives only an author name, first look up `finance-analysis/state/xiaohongshu-sources.md` by `作者` or `别名` and use its `profile_url`; if no match exists, ask for the profile link. Do not save full raw Xiaohongshu article bodies to GitHub-facing outputs.

Use the script output to select the workflow. If multiple workflows are due, run the highest priority one first:

```text
quarterly_source_review
monthly_review
weekly_synthesis
weekly_playbook
closing_review
noon_review
daily_triage
xiaohongshu_source_ingest
inbox_triage
```

If `scripts/decide_workflow.sh` prints `catchup=1`, treat the run as a missed-workflow catch-up. Use the printed `target_date`, `target_week`, `target_month`, and `expected_output` values when naming daily, weekly, monthly, or quarterly output files. Do not infer the target period only from the current run time.

Every run must also treat the knowledge base as a debt register, not only as a date-window workflow. After the selected workflow writes outputs, run the knowledge refresh and inspect its `overdue_hypotheses` and `rule_review_items` counters. If either counter is greater than zero, summarize the required closure work in the final output and update `finance-analysis/state/knowledge-attention.md`; do not wait for a fixed Friday, Sunday, or month-end window.

For `closing_review`, `daily_triage`, `weekly_synthesis`, and `weekly_playbook`, run `scripts/market_snapshot.py` before writing analysis when TickFlow is configured. After writing Obsidian outputs, run `scripts/refresh_knowledge_base.py`, then run `scripts/audit_artifact_dates.sh`, then run `scripts/github_sync.sh` unless `WN_FINANCE_GITHUB_SYNC=0` or `WN_FINANCE_REPORT_ONLY=1`. If the file date audit fails, fix article-level dates before GitHub sync. If GitHub sync fails, keep the Obsidian write and report the sync status.

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
finance-analysis/source-evidence/
finance-analysis/weekly/
finance-analysis/monthly/
finance-analysis/source-profiles/
finance-analysis/strategy-candidates/
finance-analysis/market-snapshots/
finance-analysis/state/
finance-analysis/concepts/
finance-analysis/entities/
finance-analysis/explorations/
finance-analysis/decisions/
finance-analysis/comparisons/
finance-analysis/overview.md
finance-analysis/rules.md
finance-analysis/false-beliefs.md
```

## Write Behavior

Default to writing workflow results into Obsidian. Do not stop at chat-only output unless the user explicitly asks for report-only mode or `WN_FINANCE_REPORT_ONLY=1` is set.

## Output Style

Write human-facing files in polished Markdown with Chinese headings and table headers. Prefer this order: title, short daily note, summary table, then compact sections. Use a natural daily Chinese tone: clear, direct, and easy to read, but do not use jokes, slang, or casual filler. Keep financial boundaries explicit: all author views are hypotheses, not trading instructions.

Weekly review and playbook files must be readable by a person before they are useful to an AI. Put a plain-language `本周主线` section near the top, use short paragraphs for the main view, keep tables for comparison and audit details, and avoid table-heavy pages where the reader must reconstruct the conclusion from many cells.

Daily, weekly, monthly, playbook, and Xiaohongshu intake files must share the same investment-reference skeleton: `速览`, `资料闭环`, workflow-specific body sections, and `下次复盘`. Each file must state what was read, what conclusion was made, what entered the knowledge base, what remains unsupported, what should be reviewed next, and what evidence would invalidate the current view. Do not leave important items as a loose watchlist.

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
weekly_synthesis: finance-analysis/weekly/YYYY-WW__周复盘.md
weekly_playbook: finance-analysis/weekly/YYYY-WW__周计划.md
monthly_review: finance-analysis/monthly/YYYY-MM.md
quarterly_source_review: finance-analysis/source-profiles/YYYY-QN.md
source-card: finance-analysis/source-cards/YYYY-MM/YYYY-MM-DD__author__title.md
source-evidence: finance-analysis/source-evidence/YYYY-MM/YYYY-MM-DD__author__title.md
strategy-candidate: finance-analysis/strategy-candidates/YYYY-MM-DD__strategy-name.md
market-snapshot: finance-analysis/market-snapshots/YYYY-MM-DD.md
hypothesis-ledger: finance-analysis/state/hypothesis-ledger.md
xhs-source-status: finance-analysis/state/xiaohongshu-sources.md
concept: finance-analysis/concepts/name.md
entity-profile: finance-analysis/entities/name/profile.md
knowledge-overview: finance-analysis/overview.md
knowledge-attention: finance-analysis/state/knowledge-attention.md
knowledge-index: finance-analysis/state/knowledge-index.json
source-quality: finance-analysis/source-profiles/source-quality.md
structure-review: finance-analysis/state/structure-review.md
rules: finance-analysis/rules.md
false-beliefs: finance-analysis/false-beliefs.md
```

For catch-up runs, replace `YYYY-MM-DD`, `YYYY-WW`, or `YYYY-MM` with the target fields from `scripts/decide_workflow.sh`. For example, `workflow=weekly_synthesis`, `catchup=1`, and `target_week=2026-W24` must write `finance-analysis/weekly/2026-W24__周复盘.md` even if the skill is run during week 2026-W25.

For WeChat/IMA article-level files, `YYYY-MM-DD` must be the article `published` date from source frontmatter, not the IMA `created` date, filesystem creation date, sync date, or workflow run date. If a WeChat/IMA source note has no parseable `published` value, mark the item as `needs-published-date` and do not create an article card, draft strategy, or hypothesis tracking row for that article. For Xiaohongshu notes, OpenCLI may not return a stable publish time; in that case use current Asia/Shanghai fetch time as `published`, add `published_basis: fetched_at`, and record the limitation in the daily intake table.

Create missing directories before writing. For daily, weekly, monthly, and quarterly workflow files, overwrite the section for the same workflow/date when rerun and preserve unrelated sections. For source cards and strategy candidates, create a new file if absent and update the same file if the same source note is processed again. For hypothesis ledger, append new rows and avoid duplicate source/title/hypothesis rows.

For daily, weekly, monthly, and playbook outputs, every retained article, observation, signal, hypothesis, and strategy candidate must close into exactly one result: ignore, daily-note, article card, hypothesis tracking row, strategy candidate, source-profile evidence, confirmed, partly_confirmed, extended, downgraded, false_belief, needs-full-content, needs-published-date, or duplicate. If the result is not final, add a review date or next check and an invalidation condition.

After article-level files are written or updated, run:

```text
scripts/refresh_knowledge_base.py
scripts/audit_artifact_dates.sh
```

The knowledge refresh links source cards to concept and entity pages, updates `overview.md`, `rules.md`, `false-beliefs.md`, `concepts/`, `entities/`, and `state/knowledge-attention.md`. The audit must return `artifact_date_audit=ok` before syncing to GitHub. It checks article-card file dates, card `published` fields, related IMA note `published` values, and hypothesis-tracking `id/date` consistency.

`overview.md` must behave like an investment reference dashboard, not only a directory. It should surface the review queue, high-attention themes, rule gaps, source quality, and recent additions. Concept pages must include an "投资使用摘要" section with current view, applicable boundary, confirm signals, invalidation signals, and next review action. `source-profiles/source-quality.md` must aggregate author-level source quality so repeated blogger views are not treated as truth by default.

## GitHub Archive

Default repository:

```text
repo_path: /Users/weining.lai/Documents/stock/wn-finance-analyst-result
repo_url: https://github.com/WeiningLai/wn-finance-analyst-result.git
branch: default branch from repository
auto_commit: yes
auto_push: yes
sync_raw_articles: yes
public_safe: yes
git_user_name: weining
git_user_email: weininglai@qq.com
ssh_key: ~/.ssh/wn_finance_analyst_result_ed25519
```

Only sync derived output directories:

```text
finance-analysis/
```

GitHub archive includes `finance-analysis/source-evidence/` as the bottom evidence layer. Store local source-note full text and the original source link there when a local IMA note exists. Keep the original raw IMA note in place and do not modify it. Derived article cards still summarize and analyze; source evidence files preserve the underlying text for audit and future re-reading.

For Xiaohongshu, sync full note bodies only when they have been saved into local source evidence intentionally. Preserve original links when available, but do not invent publish time or source fields. Public outputs may include platform name, note id, profile id, author display name, title, full saved text, interaction counts, tags, hypothesis rows, and source-quality notes.

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

## Knowledge Base Layer

The finance knowledge base follows a markdown wiki pattern adapted for investment research:

```text
source-cards/        slow-changing single-source summaries, grouped by YYYY-MM
source-evidence/     full local source text and original links, grouped by YYYY-MM
concepts/            cross-source themes such as 国产替代 or 涨价方向
entities/            tracked sectors, assets, or objects such as 半导体材料
state/knowledge-*    generated index and attention reports
source-profiles/     author and source-quality records
rules.md             patterns that may become rules after repeated confirmation
false-beliefs.md     old beliefs that have been disproved or need narrower boundaries
```

Run `scripts/refresh_knowledge_base.py` after creating or updating source cards, hypothesis rows, strategy candidates, daily reviews, weekly reviews, monthly reviews, or single-target observations. The script is allowed to add a generated `## 知识库链接` section to source cards while preserving `published:` and `related_notes:` anchors, and it also generates `source-evidence/` from local source notes as the bottom evidence layer.

When using the knowledge base for investment reference, always distinguish:

```text
single-source observation -> repeated pattern -> candidate rule -> confirmed rule -> retired or updated rule
```

Do not promote a pattern into `rules.md` as an active rule until it has multiple sources and review evidence. If a new source conflicts with an old rule or common belief, write the conflict to `state/knowledge-attention.md` or `false-beliefs.md` instead of silently deleting the old belief.

## Xiaohongshu Source Intake

Use this when the user provides a Xiaohongshu note/profile link, asks to add a Xiaohongshu blogger to the knowledge base, or asks to update an existing Xiaohongshu blogger by name. Read `references/xiaohongshu.md`. The short path is: resolve author name to `profile_url` when possible, expand short links when needed, fetch notes with OpenCLI, filter known note ids before classification, classify and score only new readable notes, write a daily `小红书来源接入` section, create public-safe article cards for score >= 19, add hypothesis rows for score >= 25, update `state/xiaohongshu-sources.md`, then run knowledge refresh, date audit, and GitHub sync.

For existing Xiaohongshu bloggers, never require the user to resend the profile URL if `state/xiaohongshu-sources.md` already has a matching author or alias with a usable `profile_url`. Use the source row's `默认抓取篇数` unless the user specifies a limit. If all fetched notes are already known, record `本次新增=0`, update `最近读取`, and stop without creating duplicate article cards, hypothesis rows, or strategy candidates.

Xiaohongshu source quality must be tracked separately from article quality. After at least 5 readable notes from one blogger, write or update a source-profile note under `finance-analysis/source-profiles/` with repeated themes, useful signals, blind spots, conflicts with existing rules, and next review date. Do not treat likes, collects, or comments as truth; use them only as attention and popularity signals.

## Irregular Execution Closure

The user may run this skill at irregular times. Closure must therefore be due-date driven instead of schedule driven.

The workflow selector must also be artifact driven. If a scheduled workflow window was missed and the expected output file is still absent, run the missing workflow before ordinary inbox triage. Current rules cover weekly synthesis, weekly playbook, and monthly review; the selected catch-up target is exposed by `scripts/decide_workflow.sh` as `target_week`, `target_month`, and `expected_output`.

On every run, after `scripts/refresh_knowledge_base.py`, check `finance-analysis/state/knowledge-attention.md` and handle the two generated sections:

```text
需要处理的复盘
规则晋级检查
```

For each overdue hypothesis, choose exactly one closure action:

```text
confirmed: evidence matched the confirm signal; keep or promote the pattern.
partly_confirmed: part of the signal worked; narrow the applicable regime.
extended: evidence is incomplete but still relevant; set a new review date and state what evidence is missing.
downgraded: evidence was weak or contradicted; lower priority and explain why.
false_belief: the hypothesis exposed a recurring wrong belief; add or update `false-beliefs.md`.
```

For candidate rules, use this promotion gate:

```text
source_count >= 2
evidence_count >= 3
observable_confirm_signal = yes
actionable_invalidation_signal = yes
applicable_regime = explicit
known_counterexample = recorded
portfolio_action = clear
```

If the gate passes, move the item from candidate review toward `已确认规则` with a short boundary. If the gate does not pass, keep it in `候选规则池` and write the missing evidence. Never keep an overdue item in plain `观察中` without either a new review date or a downgrade reason.

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
- For Xiaohongshu, prefer OpenCLI with full signed note URLs; do not rely on note id alone.
- Do not provide direct buy or sell instructions.
- Do not let a single intraday note create or change an active strategy.
- Do not let a single Stock Analysis observation promote, reject, or rewrite a strategy candidate.
- Use market snapshots to confirm or challenge article hypotheses, not to create trade instructions.
- For time-sensitive claims, use concrete dates.
- For each article, use the `published` frontmatter date as the article date. Do not use `created`, file ctime, sync time, or workflow run date for article-level dates.
- If content is insufficient, mark the note as `needs-full-content`; do not infer missing article text.
- If `published` is missing or invalid, mark the note as `needs-published-date` and skip article-level derived files until the date is available.
- Keep GitHub archive output traceable by syncing article cards, source evidence, hypotheses, concept pages, and review outputs together.

## Workflow Selection

After running `scripts/decide_workflow.sh`, read `references/workflows.md` for the selected workflow and `references/output-contract.md` for the required output format. For `xiaohongshu_source_ingest`, also read `references/xiaohongshu.md`.

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
