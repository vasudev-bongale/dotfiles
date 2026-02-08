export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git kubectl kube-ps1)
source "/opt/homebrew/opt/kube-ps1/share/kube-ps1.sh"
PROMPT='$(kube_ps1)'$PROMPT

source $ZSH/oh-my-zsh.sh

# export PATHs
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
export PATH=/opt/homebrew/bin:$PATH

# K8s auto-complete
autoload -U +X compinit && compinit
source <(kubectl completion zsh)

# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# source ~/powerlevel10k/powerlevel10k.zsh-theme

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
## [[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

### Don't correct on these commands
alias kubectl='nocorrect kubecolor'
alias k='nocorrect kubecolor'

setopt BANG_HIST                 # Treat the '!' character specially during expansion.
setopt EXTENDED_HISTORY          # Write the history file in the ":start:elapsed;command" format.
setopt INC_APPEND_HISTORY        # Write to the history file immediately, not when the shell exits.
setopt SHARE_HISTORY             # Share history between all sessions.
setopt HIST_EXPIRE_DUPS_FIRST    # Expire duplicate entries first when trimming history.
setopt HIST_IGNORE_DUPS          # Don't record an entry that was just recorded again.
setopt HIST_IGNORE_ALL_DUPS      # Delete old recorded entry if new entry is a duplicate.
setopt HIST_FIND_NO_DUPS         # Do not display a line previously found.
setopt HIST_IGNORE_SPACE         # Don't record an entry starting with a space.
setopt HIST_SAVE_NO_DUPS         # Don't write duplicate entries in the history file.
setopt HIST_REDUCE_BLANKS        # Remove superfluous blanks before recording entry.
setopt HIST_VERIFY               # Don't execute immediately upon history expansion.
setopt HIST_BEEP                 # Beep when accessing nonexistent history.


source /opt/homebrew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
export VOLTA_HOME="$HOME/.volta"
export PATH="$VOLTA_HOME/bin:$PATH"
eval "$(starship init zsh)"
eval "$(atuin init zsh --disable-up-arrow)"
source /opt/homebrew/share/zsh-autosuggestions/zsh-autosuggestions.zsh
eval "$(zoxide init zsh)"

# Added by Antigravity
export PATH="/Users/vbongale/.antigravity/antigravity/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"
