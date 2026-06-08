#!/usr/bin/env bash
set -euo pipefail

tz="${WN_FINANCE_TZ:-Asia/Shanghai}"
now_hm="$(TZ="$tz" date +%H%M)"
weekday="$(TZ="$tz" date +%u)"
today="$(TZ="$tz" date +%Y-%m-%d)"
day="$(TZ="$tz" date +%d)"
month="$(TZ="$tz" date +%m)"

vault="${OBSIDIAN_VAULT:-}"
if [ -z "$vault" ] || [ ! -d "$vault" ]; then
  obsidian_json="$HOME/Library/Application Support/obsidian/obsidian.json"
  if [ -f "$obsidian_json" ]; then
    vault="$(sed -n 's/.*"path":"\([^"]*\)".*/\1/p' "$obsidian_json" | head -1)"
  fi
fi
if [ -z "$vault" ] || [ ! -d "$vault" ]; then
  fallback="$HOME/Documents/Obsidian Vault"
  if [ -d "$fallback" ]; then
    vault="$fallback"
  fi
fi

if [ -z "$vault" ] || [ ! -d "$vault" ]; then
  printf 'workflow=blocked\n'
  printf 'reason=vault_not_found\n'
  printf 'today=%s\n' "$today"
  exit 0
fi

recent_count=0
if [ -d "$vault/ima" ]; then
  recent_count="$(find "$vault/ima" -type f -name '*.md' -mtime -3 2>/dev/null | wc -l | tr -d ' ')"
fi

is_weekday=0
if [ "$weekday" -ge 1 ] && [ "$weekday" -le 5 ]; then
  is_weekday=1
fi

is_last_weekday_of_month=0
next_business_month="$month"
offset=1
while [ "$offset" -le 4 ]; do
  next_weekday="$(TZ="$tz" date -v+"$offset"d +%u)"
  next_month="$(TZ="$tz" date -v+"$offset"d +%m)"
  if [ "$next_weekday" -ge 1 ] && [ "$next_weekday" -le 5 ]; then
    next_business_month="$next_month"
    break
  fi
  offset=$((offset + 1))
done
if [ "$is_weekday" -eq 1 ] && [ "$next_business_month" != "$month" ]; then
  is_last_weekday_of_month=1
fi

workflow="inbox_triage"
reason="default_recent_finance_notes"

if [ "$weekday" -eq 7 ] && [ "$now_hm" -ge 2000 ] && [ "$now_hm" -le 2130 ]; then
  if [ "$day" -ge 24 ] && { [ "$month" = "03" ] || [ "$month" = "06" ] || [ "$month" = "09" ] || [ "$month" = "12" ]; }; then
    workflow="quarterly_source_review"
    reason="quarter_end_sunday_evening"
  elif [ "$now_hm" -ge 2030 ] && [ "$now_hm" -le 2100 ]; then
    workflow="weekly_playbook"
    reason="sunday_evening_next_week_setup"
  fi
elif [ "$is_last_weekday_of_month" -eq 1 ] && [ "$now_hm" -ge 2200 ] && [ "$now_hm" -le 2300 ]; then
  workflow="monthly_review"
  reason="last_weekday_of_month_evening"
elif [ "$weekday" -eq 5 ] && [ "$now_hm" -ge 2200 ] && [ "$now_hm" -le 2240 ]; then
  workflow="weekly_synthesis"
  reason="friday_after_market_weekly_close"
elif [ "$is_weekday" -eq 1 ] && [ "$now_hm" -ge 1445 ] && [ "$now_hm" -le 1505 ]; then
  workflow="closing_review"
  reason="weekday_closing_review_window"
elif [ "$is_weekday" -eq 1 ] && [ "$now_hm" -ge 1145 ] && [ "$now_hm" -le 1205 ]; then
  workflow="noon_review"
  reason="weekday_noon_review_window"
elif [ "$is_weekday" -eq 1 ] && [ "$now_hm" -ge 2130 ] && [ "$now_hm" -le 2145 ]; then
  workflow="daily_triage"
  reason="weekday_evening_inbox_triage"
elif [ "$recent_count" -gt 0 ]; then
  workflow="inbox_triage"
  reason="recent_ima_notes_found"
fi

printf 'workflow=%s\n' "$workflow"
printf 'reason=%s\n' "$reason"
printf 'vault=%s\n' "$vault"
printf 'today=%s\n' "$today"
printf 'timezone=%s\n' "$tz"
printf 'weekday=%s\n' "$weekday"
printf 'time=%s\n' "$now_hm"
printf 'recent_ima_notes=%s\n' "$recent_count"
