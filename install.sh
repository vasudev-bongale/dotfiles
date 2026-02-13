#!/usr/bin/env bash
set -euo pipefail

# ── Colors ──────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Preflight ───────────────────────────────────
if [[ "$(uname)" != "Darwin" ]]; then
  error "This dotfiles setup is macOS-only."
  exit 1
fi

echo ""
echo "  ╭──────────────────────────────────╮"
echo "  │   dotfiles installer — vbongale  │"
echo "  ╰──────────────────────────────────╯"
echo ""

# ── Homebrew ────────────────────────────────────
if ! command -v brew &>/dev/null; then
  warn "Homebrew not found. Installing..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv)"
else
  info "Homebrew already installed"
fi

# ── Brew packages ───────────────────────────────
FORMULAS=(
  oh-my-posh zinit atuin tmux helix yazi glow gitmux stow
  fzf fd bat ripgrep zoxide kubecolor kube-ps1
  tmux-mem-cpu-load
)
CASKS=(ghostty)

warn "Checking brew packages..."
MISSING_F=()
for pkg in "${FORMULAS[@]}"; do
  if ! brew list --formula "$pkg" &>/dev/null; then
    MISSING_F+=("$pkg")
  fi
done
MISSING_C=()
for pkg in "${CASKS[@]}"; do
  if ! brew list --cask "$pkg" &>/dev/null && [[ ! -d "/Applications/${pkg}.app" && ! -d "/Applications/${pkg^}.app" ]]; then
    MISSING_C+=("$pkg")
  fi
done

if [[ ${#MISSING_F[@]} -gt 0 ]]; then
  warn "Installing formulas: ${MISSING_F[*]}"
  brew install "${MISSING_F[@]}"
fi
if [[ ${#MISSING_C[@]} -gt 0 ]]; then
  warn "Installing casks: ${MISSING_C[*]}"
  brew install --cask "${MISSING_C[@]}"
fi
if [[ ${#MISSING_F[@]} -eq 0 && ${#MISSING_C[@]} -eq 0 ]]; then
  info "All brew packages already installed"
fi

# ── Backup conflicting files ────────────────────
backup_conflicts() {
  local backup_dir="$HOME/dotfiles_backup/$(date +%Y%m%d_%H%M%S)"
  local count=0

  for pkg in ghostty oh-my-posh atuin tmux zsh helix yazi gitmux claude; do
    [[ -d "$DOTFILES_DIR/$pkg" ]] || continue
    while IFS= read -r file; do
      # Derive the target path under $HOME
      local rel="${file#"$DOTFILES_DIR/$pkg/"}"
      local target="$HOME/$rel"
      # Back up real files (not symlinks) that would conflict
      if [[ -f "$target" && ! -L "$target" ]]; then
        local dest="$backup_dir/$rel"
        mkdir -p "$(dirname "$dest")"
        mv "$target" "$dest"
        count=$((count + 1))
      fi
    done < <(find "$DOTFILES_DIR/$pkg" -type f -not -path '*/.git/*')
  done

  if [[ $count -gt 0 ]]; then
    warn "Backed up $count conflicting file(s) to $backup_dir"
  else
    info "No conflicting files found"
  fi
}

backup_conflicts

# ── Stow packages ───────────────────────────────
STOW_PACKAGES=(ghostty oh-my-posh atuin tmux zsh helix yazi gitmux claude)

for pkg in "${STOW_PACKAGES[@]}"; do
  if [[ -d "$DOTFILES_DIR/$pkg" ]]; then
    stow -d "$DOTFILES_DIR" -t "$HOME" --restow "$pkg" 2>/dev/null
    info "Stowed $pkg"
  else
    warn "Package $pkg not found in dotfiles, skipping"
  fi
done

# ── Zinit (loaded via Homebrew, no extra install needed) ──
info "Zinit sourced via /opt/homebrew/opt/zinit/zinit.zsh"

# ── TPM (tmux plugin manager) ──────────────────
if [[ ! -d "$HOME/.tmux/plugins/tpm" ]]; then
  warn "Installing TPM..."
  git clone https://github.com/tmux-plugins/tpm "$HOME/.tmux/plugins/tpm"
else
  info "TPM already installed"
fi

# ── kube-tmux ───────────────────────────────────
if [[ ! -d "$HOME/.tmux/kube-tmux" ]]; then
  warn "Installing kube-tmux..."
  git clone https://github.com/jonmosco/kube-tmux.git "$HOME/.tmux/kube-tmux"
else
  info "kube-tmux already installed"
fi

# ── tmux plugins (via TPM) ─────────────────────
if [[ -x "$HOME/.tmux/plugins/tpm/bin/install_plugins" ]]; then
  warn "Installing tmux plugins..."
  "$HOME/.tmux/plugins/tpm/bin/install_plugins" >/dev/null 2>&1 || true
  info "tmux plugins installed"
else
  warn "TPM install script not found, skipping tmux plugin install"
fi

# ── Yazi plugins ────────────────────────────────
if command -v ya &>/dev/null; then
  warn "Installing yazi plugins..."
  ya pkg install 2>/dev/null || true
  info "Yazi plugins installed"
else
  warn "ya CLI not found, skipping yazi plugin install"
fi

# ── Summary ─────────────────────────────────────
echo ""
echo "  ╭──────────────────────────────────╮"
echo "  │          Setup complete!         │"
echo "  ╰──────────────────────────────────╯"
echo ""
info "Configs stowed: ${STOW_PACKAGES[*]}"
echo ""
warn "Manual steps:"
echo "  1. Install JetBrainsMono Nerd Font: brew install --cask font-jetbrains-mono-nerd-font"
echo "  2. Reload shell: source ~/.zshrc"
echo "  3. Inside tmux: press C-a I to install plugins"
echo "  4. Import zsh history into atuin: atuin import zsh"
echo ""
