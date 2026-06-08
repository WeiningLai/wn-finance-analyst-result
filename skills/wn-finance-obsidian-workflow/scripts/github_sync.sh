#!/usr/bin/env bash
set -euo pipefail

if [ "${WN_FINANCE_GITHUB_SYNC:-1}" = "0" ]; then
  printf 'github_sync_status=skipped\n'
  printf 'reason=WN_FINANCE_GITHUB_SYNC\n'
  exit 0
fi

if [ "${WN_FINANCE_REPORT_ONLY:-0}" = "1" ]; then
  printf 'github_sync_status=skipped\n'
  printf 'reason=WN_FINANCE_REPORT_ONLY\n'
  exit 0
fi

if [ "${WN_FINANCE_SYNC_RAW_ARTICLES:-0}" = "1" ]; then
  printf 'github_sync_status=blocked\n'
  printf 'reason=raw_article_sync_not_allowed_by_default\n'
  exit 0
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

if [ -z "$vault" ] || [ ! -d "$vault" ]; then
  printf 'github_sync_status=blocked\n'
  printf 'reason=vault_not_found\n'
  exit 0
fi

repo_path="${WN_FINANCE_GITHUB_REPO_PATH:-/Users/weining.lai/Documents/stock/wn-finance-analyst-result}"
repo_url="${WN_FINANCE_GITHUB_REPO_URL:-https://github.com/WeiningLai/wn-finance-analyst-result.git}"
branch="${WN_FINANCE_GITHUB_BRANCH:-}"
auto_commit="${WN_FINANCE_GITHUB_AUTO_COMMIT:-1}"
auto_push="${WN_FINANCE_GITHUB_AUTO_PUSH:-1}"
public_safe="${WN_FINANCE_PUBLIC_SAFE:-1}"
git_user_name="${WN_FINANCE_GITHUB_USER_NAME:-weining}"
git_user_email="${WN_FINANCE_GITHUB_USER_EMAIL:-weininglai@qq.com}"
git_ssh_key="${WN_FINANCE_GITHUB_SSH_KEY:-$HOME/.ssh/wn_finance_analyst_result_ed25519}"

if [ "$public_safe" != "1" ]; then
  printf 'github_sync_status=blocked\n'
  printf 'reason=public_safe_required\n'
  exit 0
fi

if [ ! -d "$repo_path/.git" ]; then
  if [ -e "$repo_path" ] && [ ! -d "$repo_path/.git" ]; then
    printf 'github_sync_status=blocked\n'
    printf 'reason=repo_path_exists_but_not_git_repo\n'
    printf 'repo_path=%s\n' "$repo_path"
    exit 0
  fi
  mkdir -p "$(dirname "$repo_path")"
  git clone "$repo_url" "$repo_path" >/tmp/wn-finance-github-clone.out 2>/tmp/wn-finance-github-clone.err || {
    printf 'github_sync_status=failed\n'
    printf 'reason=git_clone_failed\n'
    printf 'repo_url=%s\n' "$repo_url"
    printf 'repo_path=%s\n' "$repo_path"
    printf 'stderr=%s\n' "$(tr '\n' ' ' </tmp/wn-finance-github-clone.err | sed 's/[[:space:]]*$//')"
    exit 0
  }
fi

cd "$repo_path"

git config --local user.name "$git_user_name"
git config --local user.email "$git_user_email"
if [ -f "$git_ssh_key" ]; then
  git config --local core.sshCommand "ssh -i $git_ssh_key -o IdentitiesOnly=yes"
fi

if [ -z "$branch" ]; then
  branch="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true)"
fi
if [ -z "$branch" ]; then
  branch="$(git branch --show-current 2>/dev/null || true)"
fi
if [ -z "$branch" ]; then
  branch="main"
fi

git fetch origin "$branch" >/tmp/wn-finance-github-fetch.out 2>/tmp/wn-finance-github-fetch.err || {
  printf 'github_sync_status=failed\n'
  printf 'reason=git_fetch_failed\n'
  printf 'branch=%s\n' "$branch"
  printf 'stderr=%s\n' "$(tr '\n' ' ' </tmp/wn-finance-github-fetch.err | sed 's/[[:space:]]*$//')"
  exit 0
}

git checkout "$branch" >/tmp/wn-finance-github-checkout.out 2>/tmp/wn-finance-github-checkout.err || {
  printf 'github_sync_status=failed\n'
  printf 'reason=git_checkout_failed\n'
  printf 'branch=%s\n' "$branch"
  printf 'stderr=%s\n' "$(tr '\n' ' ' </tmp/wn-finance-github-checkout.err | sed 's/[[:space:]]*$//')"
  exit 0
}

git pull --rebase origin "$branch" >/tmp/wn-finance-github-pull.out 2>/tmp/wn-finance-github-pull.err || {
  printf 'github_sync_status=failed\n'
  printf 'reason=git_pull_failed\n'
  printf 'branch=%s\n' "$branch"
  printf 'stderr=%s\n' "$(tr '\n' ' ' </tmp/wn-finance-github-pull.err | sed 's/[[:space:]]*$//')"
  exit 0
}

allowed_dirs="finance-analysis"
legacy_dirs="50-decisions 40-distillations 30-strategies _agent/state"
for rel in $allowed_dirs; do
  if [ -e "$vault/$rel" ]; then
    mkdir -p "$repo_path/$rel"
    rsync -a --delete "$vault/$rel/" "$repo_path/$rel/"
  fi
done

for rel in $legacy_dirs; do
  if [ -e "$repo_path/$rel" ]; then
    rm -rf "$repo_path/$rel"
  fi
done

for rel in $allowed_dirs $legacy_dirs; do
  if [ -e "$repo_path/$rel" ] || git ls-files --error-unmatch "$rel" >/dev/null 2>&1; then
    git add -A -- "$rel" 2>/tmp/wn-finance-github-add.err || {
      printf 'github_sync_status=failed\n'
      printf 'reason=git_add_failed\n'
      printf 'path=%s\n' "$rel"
      printf 'stderr=%s\n' "$(tr '\n' ' ' </tmp/wn-finance-github-add.err | sed 's/[[:space:]]*$//')"
      exit 0
    }
  fi
done

if git diff --cached --quiet; then
  printf 'github_sync_status=unchanged\n'
  printf 'repo_path=%s\n' "$repo_path"
  printf 'branch=%s\n' "$branch"
  exit 0
fi

if [ "$auto_commit" != "1" ]; then
  printf 'github_sync_status=staged\n'
  printf 'repo_path=%s\n' "$repo_path"
  printf 'branch=%s\n' "$branch"
  exit 0
fi

commit_message="${WN_FINANCE_GITHUB_COMMIT_MESSAGE:-Update finance analysis outputs}"
git commit -m "$commit_message" >/tmp/wn-finance-github-commit.out 2>/tmp/wn-finance-github-commit.err || {
  printf 'github_sync_status=failed\n'
  printf 'reason=git_commit_failed\n'
  printf 'stderr=%s\n' "$(tr '\n' ' ' </tmp/wn-finance-github-commit.err | sed 's/[[:space:]]*$//')"
  exit 0
}

if [ "$auto_push" != "1" ]; then
  printf 'github_sync_status=committed\n'
  printf 'repo_path=%s\n' "$repo_path"
  printf 'branch=%s\n' "$branch"
  exit 0
fi

git push origin "$branch" >/tmp/wn-finance-github-push.out 2>/tmp/wn-finance-github-push.err || {
  printf 'github_sync_status=failed\n'
  printf 'reason=git_push_failed\n'
  printf 'branch=%s\n' "$branch"
  printf 'stderr=%s\n' "$(tr '\n' ' ' </tmp/wn-finance-github-push.err | sed 's/[[:space:]]*$//')"
  exit 0
}

printf 'github_sync_status=pushed\n'
printf 'repo_path=%s\n' "$repo_path"
printf 'branch=%s\n' "$branch"
