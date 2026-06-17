# Xiaohongshu Intake

Use this file only for `xiaohongshu_source_ingest`.

## Commands

Prefer the installed CLI:

```bash
/Users/weining.lai/.local/bin/opencli xiaohongshu note '<full signed note URL>'
/Users/weining.lai/.local/bin/opencli xiaohongshu user '<full profile URL>' --limit 5 --format json
```

If `opencli` is not on that path, use `which opencli`. Do not install or update OpenCLI unless the user asks.

For short links, first expand the URL and keep the full signed target:

```bash
curl -s -L -w '\nEFFECTIVE_URL=%{url_effective}\n' -o /tmp/xhs.html '<xhslink-url>'
```

`opencli xiaohongshu note` requires the full signed note URL with `xsec_token`; note id alone is not enough.

## Note Intake

For each readable note, extract:

```text
platform: xiaohongshu
note_id
title
author
content
likes
collects
comments
tags
fetched_at
published
published_basis
```

OpenCLI `xiaohongshu note` may omit publish time from its normal rows. Before falling back to fetch time, try the browser page state after opening the signed note URL:

```bash
/Users/weining.lai/.local/bin/opencli browser open '<full signed note URL>'
/Users/weining.lai/.local/bin/opencli browser eval "(() => { const id='<note_id>'; const note=window.__INITIAL_STATE__?.note?.noteDetailMap?.[id]?.note || {}; const fmt=(ms)=>ms?new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}).format(new Date(Number(ms))).replace(' ','T'):''; return JSON.stringify({published:fmt(note.time), updated:fmt(note.lastUpdateTime), basis: note.time ? 'xhs_initial_state_note_time' : ''}); })()"
```

Use `note.time` as `published` when present. `lastUpdateTime` is edit time and must not replace publish time. Some notes have `lastUpdateTime` earlier than `note.time`, so treat it as optional metadata only.

If neither OpenCLI output nor page state returns a stable publish time, set:

```text
published: current Asia/Shanghai time
published_basis: fetched_at
```

This exception exists only for Xiaohongshu because the platform reader may omit publish time. Keep the limitation visible in daily output and source cards.

## Profile Intake

For a profile, read the smallest useful batch. First intake normally uses 10 notes. Existing-source updates normally use the source row's `默认抓取篇数`, usually 5. If the source has not been read for more than 14 days, use 10 unless the user gives another limit; if it has not been read for more than 30 days, use 20 and state the larger catch-up cost before processing.

When the user gives only an author name, resolve it from `finance-analysis/state/xiaohongshu-sources.md`:

```text
match fields: 作者, 别名
required field: profile_url
fallback: ask the user for the profile link
```

For first intake, write both a human-readable `主页` value and a full `profile_url` value. `profile_url` must be directly usable by:

```bash
/Users/weining.lai/.local/bin/opencli xiaohongshu user '<profile_url>' --limit N --format json
```

Before processing profile results, build a known note id set from existing derived outputs:

```text
finance-analysis/source-cards/YYYY-MM/
finance-analysis/source-evidence/YYYY-MM/
finance-analysis/daily/
finance-analysis/state/xiaohongshu-sources.md
```

Prefer saving raw OpenCLI profile JSON to a temporary local file outside Obsidian and GitHub, then inspect only note ids, titles, authors, and note URLs first. Do not paste or summarize full raw profile JSON into the conversation or public outputs. Filter by note id before classification and article-card writing. If all returned notes are already known, write a short daily row with `本次新增=0`, update `最近读取`, keep `上次新增` at 0, and stop without scoring old notes again.

Process each new readable note independently and write a profile-level summary to `finance-analysis/state/xiaohongshu-sources.md`. Update `已处理笔记` with a compact comma-separated note id list or short hash list if the full ids make the row too wide. Use this field as a cache hint, not as the only source of truth; source cards and daily files remain the audit source.

After at least 5 readable notes from one author, create or update:

```text
finance-analysis/source-profiles/xiaohongshu__author.md
```

The profile note should answer:

```text
repeated themes
useful signals
blind spots
conflicts with existing knowledge
next source-quality review date
```

## Scoring Adjustments

Use the normal 1-5 evidence standard. Likes, collects, and comments are popularity signals only; they can raise processing priority but cannot raise truth quality by themselves.

Prefer article cards for:

```text
clear thesis
named sector or asset chain
observable verification path
explicit failure condition
repeated theme across notes
```

Skip or daily-note only for:

```text
pure sentiment
unverifiable single-stock hype
missing content
no observable signal
only screenshots without readable text
```

## Public Safety

When a Xiaohongshu note is intentionally saved as local source evidence, keep the full saved text and original link in `finance-analysis/source-evidence/YYYY-MM/`. Public outputs may include platform, note id, author display name, title, interaction counts, tags, full saved text, hypotheses, and source-quality conclusions.

## Closure

Every high-score note must close into one of:

```text
article card
hypothesis row
strategy candidate
source-profile evidence
daily-note only
needs-full-content
```

Every hypothesis must include review date, confirm signal, and invalidation signal. Every imported profile must have a next source-quality review date. If later notes contradict earlier claims, record the conflict in `knowledge-attention.md`, `false-beliefs.md`, or the source profile.
