# dotfiles

Personal dotfiles managed with [GNU Stow](https://www.gnu.org/software/stow/). Catppuccin Mocha everywhere.

## Quick Install

```bash
git clone <your-repo-url> ~/dotfiles
cd ~/dotfiles
./install.sh
```

The script is idempotent — safe to re-run anytime. It backs up any existing config files to `~/dotfiles_backup/` before stowing.

## What's Inside

| Package | Config Path | What it does |
|---------|-------------|--------------|
| **ghostty** | `~/.config/ghostty/config` | Terminal emulator — Catppuccin Mocha, JetBrainsMono Nerd Font, copy-on-select |
| **starship** | `~/.config/starship.toml` | Prompt — two-line, k8s context (color-coded), git, Claude Code indicator |
| **atuin** | `~/.config/atuin/config.toml` | Shell history — fuzzy search, local-only, filters noise (clear, ls) |
| **tmux** | `~/.tmux.conf` | Multiplexer — Catppuccin rounded tabs, status: git/kube/cpu/battery/host |
| **zsh** | `~/.zshrc` | Shell — Oh My Zsh, autosuggestions, syntax highlighting, atuin, starship |
| **helix** | `~/.config/helix/` | Editor — Catppuccin Mocha, relative lines, auto-save, YAML/k8s LSP |
| **yazi** | `~/.config/yazi/` | File manager — glow (markdown preview), toggle-pane, Catppuccin flavor |
| **gitmux** | `~/.gitmux.conf` | Git status in tmux — branch, divergence, modified/staged/untracked flags |

## Dependencies

Installed automatically by `install.sh`:

```
ghostty  starship  atuin  tmux  helix  yazi  glow  gitmux  stow
fzf  fd  ripgrep  zoxide  kubecolor  kube-ps1
zsh-autosuggestions  zsh-syntax-highlighting  tmux-mem-cpu-load
```

**Manual install** (cask): `brew install --cask font-jetbrains-mono-nerd-font`

## Key Bindings

### tmux (prefix: `Ctrl+a`)

| Key | Action |
|-----|--------|
| `C-a v` | Split vertical |
| `C-a b` | Split horizontal |
| `C-a c` | New window |
| `C-a h/j/k/l` | Navigate panes |
| `C-a u/y` | Sync panes on/off |
| `C-a r` | Reload config |
| `C-a I` | Install plugins (TPM) |

### yazi

| Key | Action |
|-----|--------|
| `h/l` | Navigate parent/child |
| `j/k` | Move up/down |
| `T` | Toggle preview pane |
| `Space` | Toggle selection |
| `/` | Find files |
| `s/S` | Search by name (fd) / content (rg) |
| `z/Z` | Jump via zoxide / fzf |

### Kubernetes context colors (starship)

| Pattern | Color |
|---------|-------|
| `prod-*` | **Red** (bold) |
| `ei*` | Green |
| `corp-*` | Yellow |

## Adding a New Config

```bash
# 1. Create the stow package mirroring the home directory structure
mkdir -p ~/dotfiles/newtool/.config/newtool
cp ~/.config/newtool/config.toml ~/dotfiles/newtool/.config/newtool/

# 2. Remove the original and stow
rm ~/.config/newtool/config.toml
cd ~/dotfiles && stow newtool

# 3. Commit
git add newtool && git commit -m "Add newtool config"
```

## Structure

```
~/dotfiles/
├── install.sh          # Bootstrap script
├── README.md
├── atuin/.config/atuin/config.toml
├── ghostty/.config/ghostty/config
├── gitmux/.gitmux.conf
├── helix/.config/helix/{config,languages}.toml
├── starship/.config/starship.toml
├── tmux/.tmux.conf
├── yazi/.config/yazi/{yazi,keymap,theme,package}.toml
└── zsh/.zshrc
```

Plugins/flavors installed by their own package managers (yazi `ya pkg`, tmux TPM) are **not** tracked here — only the config files that reference them.
