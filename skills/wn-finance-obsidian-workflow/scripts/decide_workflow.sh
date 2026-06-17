#!/usr/bin/env bash
set -euo pipefail

tz="${WN_FINANCE_TZ:-Asia/Shanghai}"
now_hm="$(TZ="$tz" date +%H%M)"
weekday="$(TZ="$tz" date +%u)"
today="$(TZ="$tz" date +%Y-%m-%d)"
day="$(TZ="$tz" date +%d)"
month="$(TZ="$tz" date +%m)"
month_id="$(TZ="$tz" date +%Y-%m)"
week_id="$(TZ="$tz" date +%G-W%V)"

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

finance_root="$vault/finance-analysis"
weekly_dir="$finance_root/weekly"
monthly_dir="$finance_root/monthly"
daily_dir="$finance_root/daily"
weekly_synthesis_file="$weekly_dir/${week_id}__周复盘.md"
weekly_playbook_file="$weekly_dir/${week_id}__周计划.md"
monthly_file="$monthly_dir/$month_id.md"
daily_file="$daily_dir/$today.md"

previous_week_offset=$((weekday + 2))
previous_week_id="$(TZ="$tz" date "-v-${previous_week_offset}d" +%G-W%V)"
previous_weekly_synthesis_file="$weekly_dir/${previous_week_id}__周复盘.md"

previous_month_id="$(TZ="$tz" date -v-1m +%Y-%m)"
previous_monthly_file="$monthly_dir/$previous_month_id.md"

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

weekly_synthesis_due=0
if { [ "$weekday" -eq 5 ] && [ "$now_hm" -gt 2240 ]; } || [ "$weekday" -eq 6 ] || { [ "$weekday" -eq 7 ] && [ "$now_hm" -lt 2030 ]; }; then
  weekly_synthesis_due=1
fi

previous_weekly_synthesis_due=0
if [ "$weekday" -ge 1 ] && [ "$weekday" -le 4 ]; then
  previous_weekly_synthesis_due=1
fi

weekly_playbook_due=0
if { [ "$weekday" -eq 7 ] && [ "$now_hm" -gt 2100 ]; } || { [ "$weekday" -ge 1 ] && [ "$weekday" -le 3 ]; }; then
  weekly_playbook_due=1
fi

monthly_review_due=0
monthly_review_target="$month_id"
monthly_review_file="$monthly_file"
if [ "$is_last_weekday_of_month" -eq 1 ] && [ "$now_hm" -gt 2300 ]; then
  monthly_review_due=1
elif [ "$day" -le 7 ]; then
  monthly_review_due=1
  monthly_review_target="$previous_month_id"
  monthly_review_file="$previous_monthly_file"
fi

workflow="inbox_triage"
reason="default_recent_finance_notes"
catchup=0
target_date="$today"
target_week="$week_id"
target_month="$month_id"
expected_output="$daily_file"

if [ "$weekday" -eq 7 ] && [ "$now_hm" -ge 2000 ] && [ "$now_hm" -le 2130 ]; then
  if [ "$day" -ge 24 ] && { [ "$month" = "03" ] || [ "$month" = "06" ] || [ "$month" = "09" ] || [ "$month" = "12" ]; }; then
    workflow="quarterly_source_review"
    reason="quarter_end_sunday_evening"
    expected_output="$finance_root/source-profiles/$(TZ="$tz" date +%Y)-Q$(( (10#$month + 2) / 3 )).md"
  elif [ "$now_hm" -ge 2030 ] && [ "$now_hm" -le 2100 ]; then
    workflow="weekly_playbook"
    reason="sunday_evening_next_week_setup"
    expected_output="$weekly_playbook_file"
  fi
elif [ "$is_last_weekday_of_month" -eq 1 ] && [ "$now_hm" -ge 2200 ] && [ "$now_hm" -le 2300 ]; then
  workflow="monthly_review"
  reason="last_weekday_of_month_evening"
  expected_output="$monthly_file"
elif [ "$weekday" -eq 5 ] && [ "$now_hm" -ge 2200 ] && [ "$now_hm" -le 2240 ]; then
  workflow="weekly_synthesis"
  reason="friday_after_market_weekly_close"
  expected_output="$weekly_synthesis_file"
elif [ "$is_weekday" -eq 1 ] && [ "$now_hm" -ge 1445 ] && [ "$now_hm" -le 1505 ]; then
  workflow="closing_review"
  reason="weekday_closing_review_window"
elif [ "$is_weekday" -eq 1 ] && [ "$now_hm" -ge 1145 ] && [ "$now_hm" -le 1205 ]; then
  workflow="noon_review"
  reason="weekday_noon_review_window"
elif [ "$is_weekday" -eq 1 ] && [ "$now_hm" -ge 2130 ] && [ "$now_hm" -le 2145 ]; then
  workflow="daily_triage"
  reason="weekday_evening_inbox_triage"
elif [ "$monthly_review_due" -eq 1 ] && [ ! -f "$monthly_review_file" ]; then
  workflow="monthly_review"
  reason="missing_monthly_review_output"
  catchup=1
  target_month="$monthly_review_target"
  expected_output="$monthly_review_file"
elif [ "$weekly_synthesis_due" -eq 1 ] && [ ! -f "$weekly_synthesis_file" ]; then
  workflow="weekly_synthesis"
  reason="missing_weekly_synthesis_output"
  catchup=1
  expected_output="$weekly_synthesis_file"
elif [ "$previous_weekly_synthesis_due" -eq 1 ] && [ ! -f "$previous_weekly_synthesis_file" ]; then
  workflow="weekly_synthesis"
  reason="missing_previous_weekly_synthesis_output"
  catchup=1
  target_week="$previous_week_id"
  expected_output="$previous_weekly_synthesis_file"
elif [ "$weekly_playbook_due" -eq 1 ] && [ ! -f "$weekly_playbook_file" ]; then
  workflow="weekly_playbook"
  reason="missing_weekly_playbook_output"
  catchup=1
  expected_output="$weekly_playbook_file"
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
printf 'target_date=%s\n' "$target_date"
printf 'target_week=%s\n' "$target_week"
printf 'target_month=%s\n' "$target_month"
printf 'expected_output=%s\n' "$expected_output"
printf 'catchup=%s\n' "$catchup"
