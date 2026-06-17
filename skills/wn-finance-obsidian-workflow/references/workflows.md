# Workflows

## shared_output_closure

All daily, weekly, monthly, playbook, and source-intake outputs must follow the same investment reference structure from `references/output-contract.md`: `速览`, `资料闭环`, workflow-specific body sections, and `下次复盘`. The wording can vary by workflow, but each file must state what was read, what conclusion was made, what entered the knowledge base, what remains unsupported, what should be reviewed next, and what evidence would invalidate the current view.

Every article or observation must close into exactly one result:

```text
ignore
daily-note
article card
hypothesis tracking row
strategy candidate
source-profile evidence
confirmed
partly_confirmed
extended
downgraded
false_belief
needs-full-content
needs-published-date
duplicate
```

Do not leave output as a loose watchlist. If an item is important enough to keep, it needs a destination, a review date or next check, and an invalidation condition.

Article cards are stored under `finance-analysis/source-cards/YYYY-MM/`. When a local source note exists, refresh also maintains `finance-analysis/source-evidence/YYYY-MM/` with the full source text and original source link. Use source evidence as the bottom layer for later audit; do not put long raw text inside daily, weekly, concept, or source-profile pages.

## missed_workflow_catchup

When `scripts/decide_workflow.sh` prints `catchup=1`, run the selected workflow for the printed target period instead of the current wall-clock period. Use `expected_output` as the destination file. For weekly workflows, use `target_week`; for monthly workflows, use `target_month`; for daily workflows, use `target_date`.

Catch-up is meant to close missing artifacts, not to duplicate existing reviews. If `expected_output` already exists, update the relevant workflow section only when the user explicitly asks to rerun it or when the file is incomplete.

## xiaohongshu_source_ingest

Use when the user supplies a Xiaohongshu note URL, `xhslink.com` short link, profile URL, asks to import a Xiaohongshu blogger, or asks to update an existing Xiaohongshu blogger by author name.

Read `references/xiaohongshu.md`. Use OpenCLI to fetch source data:

```text
note: opencli xiaohongshu note '<full signed note URL>'
profile: opencli xiaohongshu user '<full profile URL>' --limit N --format json
```

For profile intake, resolve an existing author from `finance-analysis/state/xiaohongshu-sources.md` before asking for a URL. Use the registered `profile_url` and `默认抓取篇数` when available. Process only the requested limit or the smallest useful batch, normally 5-10 notes. Deduplicate by platform, note id, title, and author before classification. Classify only new readable notes with the same A-E labels as inbox triage, but add source fields:

```text
platform
profile_url
note_id
note_url_status
published_basis
likes
collects
comments
tags
```

If OpenCLI returns no stable publish time, set `published` to current Asia/Shanghai fetch time and `published_basis` to `fetched_at`; this is allowed for Xiaohongshu only. If content cannot be read, mark `needs-full-content` and do not create article cards or hypothesis rows.

Write the daily intake section to `finance-analysis/daily/YYYY-MM-DD.md`. Create public-safe source cards for score >= 19 and hypothesis rows for score >= 25. Update `finance-analysis/state/xiaohongshu-sources.md` with profile-level read status and source-quality notes. After at least 5 readable notes from the same blogger, create or update `finance-analysis/source-profiles/xiaohongshu__author.md`.

If all profile notes returned by OpenCLI are already known, write `本次新增=0`, update the source status row, and do not create duplicate source cards, hypothesis rows, or strategy candidates.

Closure rule: every high-score Xiaohongshu hypothesis must have a concrete review date and observable confirm/invalidation signals. Every imported blogger profile must have a next source-quality review date; if later notes repeatedly conflict with prior hypotheses or rely on unverifiable claims, downgrade the source profile instead of deleting old notes.

## inbox_triage

Use when outside a specific time window or when recent IMA notes exist.

Read recent Markdown notes under `ima/个人知识库/` modified in the last 3 days. Classify each note:

```text
A: strategy article
B: market judgement
C: case article
D: concept article
E: source-profile material
```

Use each note's frontmatter `published` value as the article date. Do not use `created`, filesystem dates, sync time, or workflow run date for article-level dates. If `published` is missing or invalid, mark the item as `needs-published-date`.

Write the classification, score, topic, evidence, next step, published date, and file path to `finance-analysis/daily/YYYY-MM-DD.md`. Create article cards, draft strategies, and hypothesis tracking rows for items that meet the evidence standard and have a valid published date.

When creating a source card, place it in the month directory for its `published` date and keep `related_notes` accurate so the refresh step can generate or update the matching source evidence file.

The daily file must include a `资料闭环` section listing created cards, created hypotheses, blocked items, duplicate items, and the next review action. Each article row must include a final destination such as daily-note, article card, hypothesis tracking row, strategy candidate, needs-full-content, or needs-published-date.

After the knowledge refresh, check overdue hypotheses and rule review items. If any exist, mention them in the run summary and keep the detail in `finance-analysis/state/knowledge-attention.md`. This makes irregular runs catch missed reviews.

## noon_review

Use for `11:45-12:05` on weekdays.

Read intraday or noon notes from today. Output only tactical observation:

```text
author view
asset/sector
morning trigger
afternoon verification signal
conflict with weekly playbook
noise check
daily panel update candidate
```

Do not create source cards or strategies.

Write the noon review section to `finance-analysis/daily/YYYY-MM-DD.md`.

The noon section must close each observation as confirmed later, waiting for close, noise, or daily panel update candidate.

## closing_review

Use for `14:45-15:05` on weekdays.

Run `scripts/market_snapshot.py` when TickFlow is configured. Check whether noon hypotheses were confirmed or invalidated by the close. Output:

```text
morning thesis
closing evidence
confirmed signals
failed signals
tomorrow watch item
archive decision
```

Write the closing review section to `finance-analysis/daily/YYYY-MM-DD.md`.

The closing section must update the same day's `资料闭环` with confirmed signals, failed signals, tomorrow watch items, and whether any hypothesis, rule, or false belief needs an update.

## daily_triage

Use for `21:30-21:45` on weekdays.

Run `scripts/market_snapshot.py` when TickFlow is configured. Read IMA notes and same-day finance clippings by article `published` date, not by IMA `created` date. Classify, score, and recommend one of:

```text
ignore
daily-note
article card
hypothesis tracking row
draft strategy
needs-full-content
needs-published-date
```

High-value articles may be summarized, but keep it short.

Write the daily triage section to `finance-analysis/daily/YYYY-MM-DD.md`. Create source cards, strategy candidates, and hypothesis ledger rows for high-value items.

The daily triage section must update the daily `资料闭环` rather than leaving recommendations only inside item paragraphs.

For each created or updated strategy candidate, fill the research validation fields from `references/output-contract.md` when the idea can be expressed as observable rules. Use `validation_status: text_only` when the article is still narrative-only, and `validation_status: blocked_data` when market data is unavailable.

Read same-day single-target observations when present and attach them to related hypothesis tracking rows or draft strategies when ids match. Do not change hypothesis or strategy status solely from one observation.

If `finance-analysis/state/knowledge-attention.md` lists overdue hypotheses, process the most important items before adding new low-priority rows. The valid outcomes are confirmed, partly confirmed, extended, downgraded, or false_belief. Do not leave an overdue item in plain observation without a new review date or downgrade reason.

## weekly_synthesis

Use Friday `22:00-22:40`, or later as catch-up when `workflow=weekly_synthesis` and `catchup=1`.

Run `scripts/market_snapshot.py` when TickFlow is configured. Read this week's article-card candidates, daily notes, finance IMA notes, and available market snapshots. Output:

```text
weekly consensus
disagreements
repeated indicators
market regime assumption
strategy candidates
blind spots
next-week watchlist
unsupported claims
```

Write to `finance-analysis/weekly/YYYY-WW__周复盘.md`. On catch-up runs, use `target_week` from `scripts/decide_workflow.sh` for `YYYY-WW`.

The weekly file must use the fixed weekly heading order from `references/output-contract.md`: `速览`, `本周主线`, `资料闭环`, `博主共识和分歧`, `核心判断`, `验证指标`, `假设和规则`, `策略和执行`, `盲点和暂不支持`, and `下次复盘`. It must include hypothesis handling, rule handling, strategy-candidate handling, unsupported claims, and next review actions. It should be usable as a durable reference file even if the original daily notes are not reopened.

The weekly synthesis must be human-readable before it is machine-readable. Write `本周主线` as 2-3 short paragraphs, write `核心判断` as short judgment paragraphs instead of a dense table, keep tables to 4 columns or fewer, and explain each hypothesis or rule id on first use.

The weekly file must treat blogger consensus and blogger disagreement as an evidence layer, not as a casual summary. Use the section `博主共识和分歧`. Each row should state whether it is a consensus or disagreement, the source evidence, how it enters the knowledge base, the next verification action, and what would invalidate or downgrade it.

If a strategy candidate appears repeatedly across the week, mark whether it should become an observable draft, be sample-checked, be rejected, or stay text-only under the research validation fields.

Aggregate single-target observations by hypothesis_id, strategy_id, sector, and regime. Mark repeated confirmations, repeated failures, conflicts, and missing verification.

Use this workflow as the default place to close overdue hypotheses when several are waiting. For each item, compare the original confirm signal, invalidation signal, related article cards, market snapshots when available, and any single-target observations. Update the hypothesis status, `rules.md`, or `false-beliefs.md` only when the evidence quality is clear.

## weekly_playbook

Use Sunday `20:30-21:00`, or later as catch-up when `workflow=weekly_playbook` and `catchup=1`.

Use available market snapshots as regime evidence. Convert weekly synthesis into next-week scenarios:

```text
base case
bull case
bear case
key indicators
trigger conditions
invalidation conditions
position implication
reasons not to act
```

Write to `finance-analysis/weekly/YYYY-WW__周计划.md`. On catch-up runs, use `target_week` from `scripts/decide_workflow.sh` for `YYYY-WW`.

The playbook file must use the fixed weekly heading order from `references/output-contract.md`: `速览`, `本周主线`, `资料闭环`, `博主共识和分歧`, `核心判断`, `验证指标`, `假设和规则`, `策略和执行`, `盲点和暂不支持`, and `下次复盘`. It must include `资料闭环` that links back to the weekly synthesis, lists the hypotheses or rules being tested this week, states what signals trigger recording, and states what signals trigger downgrade.

The playbook must be readable as a next-week plan. Write `本周主线` as the plain-language setup for the week, write `核心判断` as base, bull, and bear scenarios, keep tables to 4 columns or fewer, and make every `下次复盘` trigger action concrete, using "if X then do Y" wording rather than status labels only.

The playbook file must include `博主共识和分歧`, using the previous weekly synthesis as its evidence source. Do not only list scenarios; state which consensus or disagreement is being tested in the new week and what signal would prove it weak.

## monthly_review

Use the last weekday of the month `22:00-23:00`, or later as catch-up when `workflow=monthly_review` and `catchup=1`.

Review hypothesis ledger and strategy candidates:

```text
confirmed hypotheses
invalidated hypotheses
still-open hypotheses
strategy promotions
strategy demotions
source-profile updates
process mistakes
```

Write to `finance-analysis/monthly/YYYY-MM.md`. On catch-up runs, use `target_month` from `scripts/decide_workflow.sh` for `YYYY-MM`.

The monthly file must include `资料闭环` with confirmed hypotheses, downgraded hypotheses, extended hypotheses with new dates, promoted or rejected strategy candidates, source-profile changes, and process mistakes.

Only promote a strategy candidate when its validation status, validation metrics, review lenses, robustness check, and source evidence meet the promotion requirement recorded in the candidate file.

Use accumulated single-target observations as one evidence source when reviewing confirmed hypotheses, invalidated hypotheses, strategy promotions, and strategy demotions.

Monthly review must clear stale review debt. Any hypothesis older than its review date should be confirmed, partly confirmed, extended with a new date, downgraded, or moved into false beliefs. Candidate rules can become confirmed only when they have multiple sources, at least three evidence points, observable confirmation, actionable invalidation, explicit applicable regime, recorded counterexample, and a clear portfolio action.

## quarterly_source_review

Use the last Sunday evening of March, June, September, and December.

Review source quality:

```text
best sources
noisy sources
source strengths
source blind spots
accuracy examples
failure examples
sources to keep
sources to downgrade
new source needs
```

Write to `finance-analysis/source-profiles/YYYY-QN.md`.
