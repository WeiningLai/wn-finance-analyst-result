#!/usr/bin/env bash
set -euo pipefail

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
  printf 'artifact_date_audit=blocked\n'
  printf 'reason=vault_not_found\n'
  exit 0
fi

issues=0
checked=0

card_dir="$vault/finance-analysis/source-cards"
if [ -d "$card_dir" ]; then
  while IFS= read -r card; do
    checked=$((checked + 1))
    file_date="$(basename "$card" | sed -n 's/^\([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\)__.*/\1/p')"
    card_published="$(sed -n 's/^published:[[:space:]]*//p' "$card" | head -1)"
    card_published_date="$(printf '%s' "$card_published" | sed -n 's/^\([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\).*/\1/p')"
    related_note="$(sed -n 's/^related_notes:[[:space:]]*//p' "$card" | head -1)"
    source_published_date=""
    if [ -n "$related_note" ] && [ -f "$vault/$related_note" ]; then
      source_published="$(sed -n 's/^published:[[:space:]]*//p' "$vault/$related_note" | head -1)"
      source_published_date="$(printf '%s' "$source_published" | sed -n 's/^\([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\).*/\1/p')"
    fi

    if [ -z "$file_date" ] || [ -z "$card_published_date" ] || [ "$file_date" != "$card_published_date" ]; then
      issues=$((issues + 1))
      printf 'issue=source_card_date_mismatch file=%s file_date=%s published=%s\n' "$card" "$file_date" "$card_published"
    fi
    if [ -n "$source_published_date" ] && [ "$card_published_date" != "$source_published_date" ]; then
      issues=$((issues + 1))
      printf 'issue=source_card_source_mismatch file=%s card_published=%s source_published=%s\n' "$card" "$card_published_date" "$source_published_date"
    fi
  done < <(find "$card_dir" -type f -name '*.md' -print | sort)
fi

ledger="$vault/finance-analysis/state/hypothesis-ledger.md"
if [ -f "$ledger" ]; then
  while IFS= read -r row; do
    case "$row" in
      '| H-'*)
        checked=$((checked + 1))
        id="$(printf '%s' "$row" | awk -F'|' '{gsub(/^ +| +$/, "", $2); print $2}')"
        row_date="$(printf '%s' "$row" | awk -F'|' '{gsub(/^ +| +$/, "", $3); print $3}')"
        id_date="$(printf '%s' "$id" | sed -n 's/^H-\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)-.*/\1-\2-\3/p')"
        if [ -z "$id_date" ] || [ "$id_date" != "$row_date" ]; then
          issues=$((issues + 1))
          printf 'issue=hypothesis_ledger_date_mismatch id=%s date=%s\n' "$id" "$row_date"
        fi
        ;;
    esac
  done < "$ledger"
fi

if [ "$issues" -eq 0 ]; then
  printf 'artifact_date_audit=ok\n'
else
  printf 'artifact_date_audit=failed\n'
fi
printf 'checked=%s\n' "$checked"
printf 'issues=%s\n' "$issues"
