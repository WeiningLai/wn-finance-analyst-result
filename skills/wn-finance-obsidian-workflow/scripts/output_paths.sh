#!/usr/bin/env bash
set -euo pipefail

workflow="${1:?Usage: output_paths.sh <workflow> [name] [published_date]}"
name="${2:-}"
published="${3:-}"
tz="${WN_FINANCE_TZ:-Asia/Shanghai}"

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
  printf 'status=blocked\n'
  printf 'reason=vault_not_found\n'
  exit 0
fi

today="$(TZ="$tz" date +%Y-%m-%d)"
year="$(TZ="$tz" date +%Y)"
month="$(TZ="$tz" date +%m)"
week="$(TZ="$tz" date +%V)"
quarter=$(( (10#$month - 1) / 3 + 1 ))

published_date=""
if [ -n "$published" ]; then
  published_date="$(printf '%s' "$published" | sed -n 's/^\([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\).*/\1/p')"
fi

case "$workflow" in
  inbox_triage|noon_review|closing_review|daily_triage)
    rel="finance-analysis/daily/$today.md"
    ;;
  weekly_synthesis)
    rel="finance-analysis/weekly/$year-W$week.md"
    ;;
  weekly_playbook)
    rel="finance-analysis/weekly/$year-W$week-playbook.md"
    ;;
  monthly_review)
    rel="finance-analysis/monthly/$year-$month.md"
    ;;
  quarterly_source_review)
    rel="finance-analysis/source-profiles/$year-Q$quarter.md"
    ;;
  hypothesis-ledger)
    rel="finance-analysis/state/hypothesis-ledger.md"
    ;;
  source-card)
    if [ -z "$name" ]; then
      printf 'status=blocked\n'
      printf 'reason=missing_source_card_name\n'
      printf 'usage=output_paths.sh source-card author__title published_date\n'
      exit 0
    fi
    if [ -z "$published_date" ]; then
      printf 'status=blocked\n'
      printf 'reason=missing_published_date\n'
      printf 'usage=output_paths.sh source-card author__title published_date\n'
      exit 0
    fi
    safe_name="$(printf '%s' "$name" | sed 's#[/:]#_#g; s#[[:cntrl:]]##g')"
    rel="finance-analysis/source-cards/${published_date}__$safe_name.md"
    ;;
  strategy-candidate)
    if [ -z "$name" ]; then
      printf 'status=blocked\n'
      printf 'reason=missing_strategy_name\n'
      printf 'usage=output_paths.sh strategy-candidate strategy-name published_date\n'
      exit 0
    fi
    if [ -z "$published_date" ]; then
      printf 'status=blocked\n'
      printf 'reason=missing_published_date\n'
      printf 'usage=output_paths.sh strategy-candidate strategy-name published_date\n'
      exit 0
    fi
    safe_name="$(printf '%s' "$name" | sed 's#[/:]#_#g; s#[[:cntrl:]]##g')"
    rel="finance-analysis/strategy-candidates/${published_date}__$safe_name.md"
    ;;
  *)
    printf 'status=blocked\n'
    printf 'reason=unknown_workflow\n'
    printf 'workflow=%s\n' "$workflow"
    exit 0
    ;;
esac

mkdir -p "$(dirname "$vault/$rel")"
printf 'status=ok\n'
printf 'vault=%s\n' "$vault"
printf 'workflow=%s\n' "$workflow"
printf 'relative_path=%s\n' "$rel"
printf 'absolute_path=%s\n' "$vault/$rel"
