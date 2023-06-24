
# Defined by ownMine in .ownmine.d
if [ ! -d "$HOME"/.ownmine.d ]; then
    mkdir -p "$HOME"/.ownmine.d;
fi

for cfg in "$HOME"/.ownmine.d/*.zsh; do
    . "$cfg"
done
unset -v cfg

# ownMine scripts initialization
ownmine_server_declare_pwd
ownmine_server_declare_stdout
ownmine_debug_off
