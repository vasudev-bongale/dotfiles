#!/usr/bin/env python3
"""Claude Code custom status line renderer."""

import json
import os
import re
import subprocess
import sys


# ── Catppuccin Mocha palette ──────────────────────────────────────────────────
def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def bg(r, g, b):
    return f"\033[48;2;{r};{g};{b}m"

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

RED     = rgb(243, 139, 168)   # flamingo/red
GREEN   = rgb(166, 227, 161)   # green
YELLOW  = rgb(249, 226, 175)   # yellow
BLUE    = rgb(137, 180, 250)   # blue
PEACH   = rgb(250, 179, 135)   # peach
MAUVE   = rgb(203, 166, 247)   # mauve
TEAL    = rgb(148, 226, 213)   # teal
SKY     = rgb(137, 220, 235)   # sky
TEXT    = rgb(205, 214, 244)   # text (bright white-ish)
SUBTEXT = rgb(166, 173, 200)   # subtext0 (muted)
OVERLAY = rgb(108, 112, 134)   # overlay0 (dimmer)

BG_BASE    = bg(30, 30, 46)    # base
BG_SURFACE = bg(49, 50, 68)    # surface0


# ── Helpers ───────────────────────────────────────────────────────────────────
def c(color, text):
    return f"{color}{text}{RESET}"

def link(url, text):
    """Wrap text in an OSC 8 clickable hyperlink."""
    return f"\033]8;;{url}\007{text}\033]8;;\007"

def fmt_tokens(n):
    if n >= 1_000_000:
        v = n / 1_000_000
        return f"{int(v)}M" if v == int(v) else f"{v:.1f}M"
    if n >= 1000:
        return f"{n // 1000}K"
    return str(n)

def fmt_duration(ms):
    s = ms // 1000
    h = s // 3600
    m = (s % 3600) // 60
    s2 = s % 60
    if h > 0:
        return f"{h}h {m}m"
    if m > 0:
        return f"{m}m {s2}s"
    return f"{s2}s"

def fmt_cost(usd):
    if usd >= 1.0:
        return f"${usd:.2f}"
    return f"{usd * 100:.1f}¢"

def context_bar(pct, width=10):
    """Render a colored block bar for context usage."""
    filled = round(pct / 100 * width)
    if pct < 50:
        bar_color = GREEN
    elif pct < 80:
        bar_color = YELLOW
    else:
        bar_color = RED
    bar = bar_color + "█" * filled + OVERLAY + "░" * (width - filled) + RESET
    return bar

def get_computer_name():
    try:
        return subprocess.check_output(
            ["scutil", "--get", "ComputerName"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        try:
            return os.uname().nodename.split(".")[0]
        except Exception:
            return "unknown"

def get_git_info(cwd):
    """Return (branch, additions, deletions, ahead, behind) from git in cwd."""
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=cwd, stderr=subprocess.DEVNULL
        ).decode().strip()
        if not branch:
            # detached HEAD - show short commit hash
            branch = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=cwd, stderr=subprocess.DEVNULL
            ).decode().strip() or None

        shortstat = subprocess.check_output(
            ["git", "diff", "--shortstat", "HEAD"],
            cwd=cwd, stderr=subprocess.DEVNULL
        ).decode().strip()

        additions = deletions = 0
        m = re.search(r"(\d+) insertion", shortstat)
        if m:
            additions = int(m.group(1))
        m = re.search(r"(\d+) deletion", shortstat)
        if m:
            deletions = int(m.group(1))

        ahead = behind = 0
        try:
            ab = subprocess.check_output(
                ["git", "rev-list", "--left-right", "--count", "@{upstream}...HEAD"],
                cwd=cwd, stderr=subprocess.DEVNULL
            ).decode().strip()
            parts = ab.split()
            if len(parts) == 2:
                behind, ahead = int(parts[0]), int(parts[1])
        except Exception:
            pass

        return branch, additions, deletions, ahead, behind
    except Exception:
        return None, 0, 0, 0, 0

def get_git_worktree(cwd):
    """Return worktree name if cwd is in a non-main worktree, else None."""
    try:
        output = subprocess.check_output(
            ["git", "worktree", "list", "--porcelain"],
            cwd=cwd, stderr=subprocess.DEVNULL
        ).decode()
        worktrees = []
        current_wt = None
        for block in output.strip().split("\n\n"):
            lines = block.strip().splitlines()
            wt_path = None
            is_bare = False
            for line in lines:
                if line.startswith("worktree "):
                    wt_path = line.split(" ", 1)[1]
                if line == "bare":
                    is_bare = True
            if wt_path and not is_bare:
                worktrees.append(wt_path)
                if cwd.startswith(wt_path):
                    current_wt = wt_path
        if len(worktrees) <= 1 or current_wt is None:
            return None
        return os.path.basename(current_wt)
    except Exception:
        return None

def get_git_dirty_count(cwd):
    """Return count of dirty (uncommitted) files."""
    try:
        output = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=cwd, stderr=subprocess.DEVNULL
        ).decode().strip()
        if not output:
            return 0
        return len(output.splitlines())
    except Exception:
        return 0

def get_active_agents(session_id, cwd):
    """Count active background agents by finding recently-written subagent files."""
    try:
        import time
        claude_dir = os.environ.get("CLAUDE_CONFIG_DIR", os.path.expanduser("~/.claude"))
        projects_dir = os.path.join(claude_dir, "projects")
        if not os.path.isdir(projects_dir):
            return 0
        # Find the session's subagents directory
        now = time.time()
        count = 0
        for project in os.listdir(projects_dir):
            sa_dir = os.path.join(projects_dir, project, session_id, "subagents")
            if os.path.isdir(sa_dir):
                for f in os.listdir(sa_dir):
                    fpath = os.path.join(sa_dir, f)
                    if f.endswith(".jsonl") and (now - os.path.getmtime(fpath)) < 120:
                        count += 1
                break
        return count
    except Exception:
        return 0

def get_pr_info(cwd):
    """Return cached PR info for the current branch. Refreshes async every 60s."""
    import time, hashlib
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=cwd, stderr=subprocess.DEVNULL
        ).decode().strip()
        if not branch:
            return None
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=cwd, stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return None

    cache_key = hashlib.md5(f"{remote_url}:{branch}".encode()).hexdigest()[:12]
    cache_dir = os.path.join(os.environ.get("TMPDIR", "/tmp"), "claude-pr-cache")
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    lock_file = os.path.join(cache_dir, f"{cache_key}.lock")

    os.makedirs(cache_dir, exist_ok=True)

    now = time.time()
    cached = None

    # Read cache if fresh (< 60s)
    if os.path.exists(cache_file):
        try:
            age = now - os.path.getmtime(cache_file)
            with open(cache_file) as f:
                cached = json.load(f)
            if age < 60:
                return cached if cached.get("number") else None
        except Exception:
            pass

    # Spawn background refresh if no lock or lock is stale (> 30s)
    should_refresh = True
    if os.path.exists(lock_file):
        try:
            if (now - os.path.getmtime(lock_file)) < 30:
                should_refresh = False
        except Exception:
            pass

    if should_refresh:
        # Fork a background process to refresh the cache
        try:
            subprocess.Popen(
                ["sh", "-c", f"""
                    touch "{lock_file}"
                    cd "{cwd}" || exit 1
                    result=$(gh pr view --json number,state,reviewDecision,url 2>/dev/null)
                    if [ $? -eq 0 ] && [ -n "$result" ]; then
                        printf '%s' "$result" > "{cache_file}"
                    else
                        printf '{{}}' > "{cache_file}"
                    fi
                    rm -f "{lock_file}"
                """],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True, env=os.environ.copy()
            )
        except Exception:
            pass

    # Return stale cache while refresh is in progress
    if cached and cached.get("number"):
        return cached
    return None

def get_monthly_cost():
    """Return monthly cost from ccusage with background caching (refreshes every 5 min)."""
    import time
    cache_dir = os.path.join(os.environ.get("TMPDIR", "/tmp"), "claude-pr-cache")
    cache_file = os.path.join(cache_dir, "monthly-cost.json")
    lock_file = os.path.join(cache_dir, "monthly-cost.lock")
    os.makedirs(cache_dir, exist_ok=True)

    now = time.time()
    cached = None

    if os.path.exists(cache_file):
        try:
            age = now - os.path.getmtime(cache_file)
            with open(cache_file) as f:
                cached = json.load(f)
            if age < 300:
                return cached.get("cost")
        except Exception:
            pass

    should_refresh = True
    if os.path.exists(lock_file):
        try:
            if (now - os.path.getmtime(lock_file)) < 60:
                should_refresh = False
        except Exception:
            pass

    if should_refresh:
        try:
            import datetime
            since = datetime.date.today().strftime("%Y%m01")
            subprocess.Popen(
                ["sh", "-c", f"""
                    touch "{lock_file}"
                    result=$(ccusage monthly --since {since} --json 2>/dev/null)
                    if [ $? -eq 0 ] && [ -n "$result" ]; then
                        cost=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps({{'cost':d['monthly'][0]['totalCost']}}))" 2>/dev/null)
                        [ -n "$cost" ] && printf '%s' "$cost" > "{cache_file}"
                    fi
                    rm -f "{lock_file}"
                """],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True, env=os.environ.copy()
            )
        except Exception:
            pass

    if cached:
        return cached.get("cost")
    return None

def get_kube_info():
    """Return (context, namespace) from current kubeconfig."""
    try:
        context = subprocess.check_output(
            ["kubectl", "config", "current-context"],
            stderr=subprocess.DEVNULL, timeout=2
        ).decode().strip()
        namespace = subprocess.check_output(
            ["kubectl", "config", "view", "--minify", "-o", "jsonpath={..namespace}"],
            stderr=subprocess.DEVNULL, timeout=2
        ).decode().strip() or "default"
        return context, namespace
    except Exception:
        return None, None

def get_transcript_stats(transcript_path):
    """Parse transcript for turns and last tool/skill used."""
    try:
        turns = 0
        last_tool = None
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "assistant":
                        turns += 1
                        for block in entry.get("message", {}).get("content", []):
                            if block.get("type") == "tool_use":
                                name = block.get("name", "")
                                if name == "Skill":
                                    skill = block.get("input", {}).get("skillName", "")
                                    last_tool = f"/{skill}" if skill else name
                                else:
                                    last_tool = name
                except Exception:
                    pass
        return turns, last_tool
    except Exception:
        return 0, None


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    cwd            = data.get("cwd", "")
    session_id     = data.get("session_id", "")
    model          = data.get("model", {})
    cost           = data.get("cost", {})
    ctx            = data.get("context_window", {})
    transcript     = data.get("transcript_path", "")

    model_name     = re.sub(r"\s*\([^)]*context\)", "", model.get("display_name", "Claude"))
    ctx_size       = ctx.get("context_window_size", 200_000)
    used_pct       = ctx.get("used_percentage", 0)
    current_usage  = ctx.get("current_usage", {})

    # Token accounting: cache_read dominates real usage
    input_tokens  = (
        current_usage.get("cache_read_input_tokens", 0) +
        current_usage.get("cache_creation_input_tokens", 0) +
        current_usage.get("input_tokens", 0)
    )
    output_tokens  = ctx.get("total_output_tokens", 0)

    duration_ms    = cost.get("total_duration_ms", 0)
    total_cost     = cost.get("total_cost_usd", 0)
    lines_added    = cost.get("total_lines_added", 0)
    lines_removed  = cost.get("total_lines_removed", 0)

    project_dir    = os.path.basename(cwd) if cwd else ""
    git_branch, git_add, git_del, git_ahead, git_behind = get_git_info(cwd)
    git_wt         = get_git_worktree(cwd)
    dirty_count    = get_git_dirty_count(cwd)
    pr_info        = get_pr_info(cwd)
    active_agents  = get_active_agents(session_id, cwd)
    kube_ctx, kube_ns  = get_kube_info()
    monthly_cost       = get_monthly_cost()
    turns, last_tool = get_transcript_stats(transcript)
    ctx_label      = fmt_tokens(ctx_size)

    dot = c(OVERLAY, " · ")

    # ── Line 1: identity + k8s ───────────────────────────────────────────────
    model_str = c(MAUVE, f"{model_name} ({ctx_label} context)")
    line1 = model_str
    if kube_ctx:
        kube_str = c(MAUVE, f"󰠳 {kube_ctx}")
        if kube_ns and kube_ns != "default":
            kube_str += c(OVERLAY, "/") + c(SKY, kube_ns)
        line1 += dot + kube_str

    # ── Line 2: session stats ─────────────────────────────────────────────────
    tok_in  = c(TEAL,   f"{fmt_tokens(input_tokens)}↓")
    tok_out = c(PEACH,  f"{fmt_tokens(output_tokens)}↑")
    tokens_str = f"󰆼 {tok_in} {tok_out}"

    if turns:
        turns_str = dot + c(SKY, f"󰭹 {turns}")
    else:
        turns_str = ""

    if last_tool:
        tools_str = dot + c(PEACH, f"󰁯 {last_tool}")
    else:
        tools_str = ""

    dur_str   = dot + c(YELLOW, f"󰥔 {fmt_duration(duration_ms)}")
    monthly_str = ""
    if monthly_cost is not None:
        monthly_str = c(OVERLAY, f" (mtd ${monthly_cost:.0f})")
    cost_str  = dot + c(GREEN,  f"󰄴 {fmt_cost(total_cost)}") + monthly_str

    bar       = context_bar(used_pct)
    used_tokens = int(ctx_size * used_pct / 100)
    ctx_str   = dot + f"󰓅 {bar}  {c(YELLOW, str(used_pct) + '%')} {c(SUBTEXT, fmt_tokens(used_tokens) + '/' + ctx_label)}"

    line2 = tokens_str + turns_str + tools_str + dur_str + cost_str + ctx_str

    # ── Line 3: workspace ─────────────────────────────────────────────────────
    dir_str = c(BLUE, f"󰝰 {project_dir}")

    parts = [dir_str]

    if dirty_count:
        parts.append(c(PEACH, f"󰷈 {dirty_count}"))

    if git_add or git_del:
        diff_str = c(GREEN, f"+{git_add}") + " " + c(RED, f"-{git_del}")
        parts.append(c(SUBTEXT, "󰏫 ") + diff_str)

    if git_branch:
        branch_str = c(TEAL, f"󰘬 {git_branch}")
        ab_parts = []
        if git_ahead:
            ab_parts.append(c(GREEN, f"↑{git_ahead}"))
        if git_behind:
            ab_parts.append(c(RED, f"↓{git_behind}"))
        if ab_parts:
            branch_str += " " + "".join(ab_parts)
        parts.append(branch_str)

    if pr_info:
        pr_num = f"#{pr_info['number']}"
        pr_url = pr_info.get("url", "")
        state = pr_info.get("state", "").upper()
        review = pr_info.get("review", "") or pr_info.get("reviewDecision", "")
        if state == "MERGED":
            pr_str = c(MAUVE, f"\ueafe {pr_num} merged")
        elif state == "CLOSED":
            pr_str = c(RED, f"\uebda {pr_num} closed")
        elif review == "APPROVED":
            pr_str = c(GREEN, f"\uea64 {pr_num} approved")
        elif review == "CHANGES_REQUESTED":
            pr_str = c(RED, f"\uea64 {pr_num} changes")
        else:
            pr_str = c(YELLOW, f"\uea64 {pr_num} open")
        if pr_url:
            pr_str = link(pr_url, pr_str)
        parts.append(pr_str)

    if git_wt:
        parts.append(c(YELLOW, f"󰙅 {git_wt}"))

    if active_agents:
        parts.append(c(SKY, f"󰜎 {active_agents}"))

    line3 = dot.join(parts)

    # ── Output ────────────────────────────────────────────────────────────────
    print(line1)
    print(line2)
    print(line3)


if __name__ == "__main__":
    main()
