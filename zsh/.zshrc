# ── PATH exports ──────────────────────────────────────────────
export PATH=/opt/homebrew/bin:$PATH
export PATH="$HOME/go/bin:$PATH"
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
export PATH="/Users/vbongale/.antigravity/antigravity/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"
export VOLTA_HOME="$HOME/.volta"
export PATH="$VOLTA_HOME/bin:$PATH"

## Environment
export EDITOR="/opt/homebrew/bin/hx"

# ── Zinit ─────────────────────────────────────────────────────
declare -A ZINIT
ZINIT[NO_ALIASES]=1
source /opt/homebrew/opt/zinit/zinit.zsh

# OMZ snippets (loaded synchronously for Warp autocompletion)
zinit lucid for \
  OMZP::git \
  OMZP::kubectl

# GitHub plugins — syntax-highlighting last, with completion init
zinit wait lucid for \
  light-mode zsh-users/zsh-autosuggestions \
  light-mode atload"zicompinit; zicdreplay" zsh-users/zsh-syntax-highlighting


# ── History settings (Atuin handles search, sync & dedup) ────
setopt SHARE_HISTORY             # Share native history between sessions (fallback)
setopt HIST_IGNORE_SPACE         # Space-prefixed commands skip both Zsh & Atuin history

# ── Aliases ───────────────────────────────────────────────────
alias kubectl='kubecolor'
alias k='kubecolor'
alias hh='atuin search -i'
alias ccusage='npx ccusage@latest'
q() { claude --model sonnet -p "$*" | glow; }

# ── Tool init ─────────────────────────────────────────────────
eval "$(oh-my-posh init zsh --config $HOME/.config/oh-my-posh/catppuccin_mocha.omp.json)"

# Precommand
precmd() { print "" }

# ── FZF ───────────────────────────────────────────────────────
# Use fd instead of find (respects .gitignore, faster)
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'

# Catppuccin Mocha theme + layout
export FZF_DEFAULT_OPTS=" \
  --color=bg+:#313244,bg:#1e1e2e,spinner:#f5e0dc,hl:#f38ba8 \
  --color=fg:#cdd6f4,header:#f38ba8,info:#cba6f7,pointer:#f5e0dc \
  --color=marker:#b4befe,fg+:#cdd6f4,prompt:#cba6f7,hl+:#f38ba8 \
  --color=selected-bg:#45475a \
  --color=border:#6c7086,label:#cdd6f4 \
  --height=60% --layout=reverse --border=rounded \
  --prompt='  ' --pointer='▎' --marker='✓ ' \
  --preview-window='right:50%:border-left' \
  --bind='ctrl-d:half-page-down,ctrl-u:half-page-up' \
  --bind='ctrl-y:execute-silent(echo -n {+} | pbcopy)+abort' \
"

# Ctrl-T: file search with bat preview
export FZF_CTRL_T_OPTS="--preview 'bat --style=numbers --color=always --line-range :300 {} 2>/dev/null || cat {}'"

# Alt-C: directory search with tree preview
export FZF_ALT_C_OPTS="--preview 'ls -la --color=always {} | head -50'"

eval "$(fzf --zsh)"
eval "$(atuin init zsh --disable-up-arrow)"
eval "$(zoxide init zsh)"

# Fx - CLI for JSON configurations
export FX_SHOW_SIZE=true
export FX_LINE_NUMBERS=true 
