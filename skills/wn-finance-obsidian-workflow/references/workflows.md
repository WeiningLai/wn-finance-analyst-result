# Workflows

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

For each created or updated strategy candidate, fill the research validation fields from `references/output-contract.md` when the idea can be expressed as observable rules. Use `validation_status: text_only` when the article is still narrative-only, and `validation_status: blocked_data` when market data is unavailable.

Read same-day single-target observations when present and attach them to related hypothesis tracking rows or draft strategies when ids match. Do not change hypothesis or strategy status solely from one observation.

## weekly_synthesis

Use Friday `22:00-22:40`.

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

Write to `finance-analysis/weekly/YYYY-WW.md`.

If a strategy candidate appears repeatedly across the week, mark whether it should become an observable draft, be sample-checked, be rejected, or stay text-only under the research validation fields.

Aggregate single-target observations by hypothesis_id, strategy_id, sector, and regime. Mark repeated confirmations, repeated failures, conflicts, and missing verification.

## weekly_playbook

Use Sunday `20:30-21:00`.

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

Write to `finance-analysis/weekly/YYYY-WW-playbook.md`.

## monthly_review

Use the last weekday of the month `22:00-23:00`.

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

Write to `finance-analysis/monthly/YYYY-MM.md`.

Only promote a strategy candidate when its validation status, validation metrics, review lenses, robustness check, and source evidence meet the promotion requirement recorded in the candidate file.

Use accumulated single-target observations as one evidence source when reviewing confirmed hypotheses, invalidated hypotheses, strategy promotions, and strategy demotions.

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
