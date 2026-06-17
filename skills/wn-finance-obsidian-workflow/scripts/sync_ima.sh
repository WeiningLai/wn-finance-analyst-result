#!/usr/bin/env bash
set -euo pipefail

if [ "${WN_FINANCE_SKIP_SYNC:-0}" = "1" ]; then
  printf 'sync_status=skipped\n'
  printf 'reason=WN_FINANCE_SKIP_SYNC\n'
  exit 0
fi

dry_run=0
if [ "${1:-}" = "--dry-run" ]; then
  dry_run=1
fi

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

plugin_dir="$vault/.obsidian/plugins/ima-copilot-sync"
if [ -z "$vault" ] || [ ! -d "$plugin_dir" ]; then
  printf 'sync_status=skipped\n'
  printf 'reason=ima_plugin_not_found\n'
  printf 'vault=%s\n' "${vault:-}"
  exit 0
fi

command_name="立即同步 ima.copilot 笔记"
search_query="${WN_FINANCE_IMA_SYNC_QUERY:-ima.copilot}"
data_json="$plugin_dir/data.json"
before_sync_time=""
if [ -f "$data_json" ]; then
  before_sync_time="$(sed -n 's/.*"lastSyncTime": *\([0-9][0-9]*\).*/\1/p' "$data_json" | head -1)"
fi

if [ "$dry_run" -eq 1 ]; then
  printf 'sync_status=dry_run\n'
  printf 'reason=would_trigger_obsidian_command_palette\n'
  printf 'vault=%s\n' "$vault"
  printf 'command=%s\n' "$command_name"
  printf 'search_query=%s\n' "$search_query"
  printf 'lastSyncTime=%s\n' "$before_sync_time"
  exit 0
fi

set +e
osascript - "$search_query" <<'APPLESCRIPT' >/tmp/wn-finance-ima-sync.out 2>/tmp/wn-finance-ima-sync.err
on run argv
set syncQuery to item 1 of argv

tell application "Obsidian"
  activate
end tell

delay 0.6

tell application "System Events"
  if not (exists process "Obsidian") then error "Obsidian process not found"
  tell process "Obsidian"
    set frontmost to true
  end tell
  keystroke "p" using {command down}
  delay 0.4
  keystroke syncQuery
  delay 0.4
  key code 36
end tell
end run
APPLESCRIPT
status=$?
set -e

if [ "$status" -eq 0 ]; then
  timeout="${WN_FINANCE_SYNC_TIMEOUT:-90}"
  interval=2
  elapsed=0
  after_sync_time="$before_sync_time"
  while [ "$elapsed" -lt "$timeout" ]; do
    sleep "$interval"
    elapsed=$((elapsed + interval))
    if [ -f "$data_json" ]; then
      after_sync_time="$(sed -n 's/.*"lastSyncTime": *\([0-9][0-9]*\).*/\1/p' "$data_json" | head -1)"
      if [ -n "$after_sync_time" ] && [ "$after_sync_time" != "$before_sync_time" ]; then
        printf 'sync_status=completed\n'
        printf 'reason=lastSyncTime_changed\n'
        printf 'vault=%s\n' "$vault"
        printf 'command=%s\n' "$command_name"
        printf 'search_query=%s\n' "$search_query"
        printf 'before_lastSyncTime=%s\n' "$before_sync_time"
        printf 'after_lastSyncTime=%s\n' "$after_sync_time"
        printf 'elapsed_seconds=%s\n' "$elapsed"
        exit 0
      fi
    fi
  done
  printf 'sync_status=timeout\n'
  printf 'reason=lastSyncTime_not_changed\n'
  printf 'vault=%s\n' "$vault"
  printf 'command=%s\n' "$command_name"
  printf 'search_query=%s\n' "$search_query"
  printf 'before_lastSyncTime=%s\n' "$before_sync_time"
  printf 'after_lastSyncTime=%s\n' "$after_sync_time"
  printf 'elapsed_seconds=%s\n' "$elapsed"
else
  printf 'sync_status=failed\n'
  printf 'reason=osascript_failed\n'
  printf 'vault=%s\n' "$vault"
  printf 'command=%s\n' "$command_name"
  printf 'search_query=%s\n' "$search_query"
  printf 'stderr=%s\n' "$(tr '\n' ' ' </tmp/wn-finance-ima-sync.err | sed 's/[[:space:]]*$//')"
fi
