#!/bin/zsh

echo "ownMine: self-hosted Minecraft server"
echo "Automated configuration script
"

echo "Initializing configuration script..."
OWNMINE_HOME="$HOME"
OWNMINE_ZSHRC=".zshrc"
OWNMINE_REPO="https://raw.githubusercontent.com/ibnunes/ownMine/master"
OWNMINE_SERVER-"ownmine"
OWNMINE_FOLDER=".ownmine.d"
OWNMINE_FILES=("ownmine" "pwd" "remote" "stdout" "utils")
OWNMINE_SERVICE_FOLDER="systemd/system"
OWNMINE_SERVICE_FILES=("ownmine" "ownminebot")

echo "Config: .zshrc"
echo "$(curl -s $OWNMINE_REPO/$OWNMINE_ZSHRC)" >> $OWNMINE_HOME/$OWNMINE_ZSHRC

echo "Get: ownMine zsh scripts"
for file in OWNMINE_FILES; do
    echo "    $file.zsh"
    curl -s "$OWNMINE_REPO/$OWNMINE_FOLDER/$file.zsh" -o "$OWNMINE_HOME/$OWNMINE_FOLDER/$file.zsh"
done

echo "Get: ownMine Discord bot"
curl -s "$OWNMINE_REPO/$OWNMINE_FOLDER/ownminebot.py" -o "$OWNMINE_HOME/$OWNMINE_FOLDER/ownminebot.py"

echo "Get: mcrcon (from Tiiffi GitHub repository)"
git clone https://github.com/Tiiffi/mcrcon.git "$OWNMINE_HOME/tools/mcrcon"

echo "Apply: zsh configurations"
source $OWNMINE_HOME/$OWNMINE_ZSHRC

echo "Add: Minecraft and Discord bot services"
read "What is your Minecraft server rcon password? (You can define it later manually) " OWNMINE_RCON_PASS
for file in OWNMINE_SERVICE_FILES; do
    sudo curl -s "$OWNMINE_REPO/$OWNMINE_SERVICE_FOLDER/$file.service" -o "/etc/$OWNMINE_SERVICE_FOLDER/$file.service"
    sudo sed -i                                             \
        -e "s|\$USER|$USER|g"                               \
        -e "s|\$OWNMINE_HOME|$OWNMINE_HOME|g"               \
        -e "s|\$OWNMINE_SERVER|$OWNMINE_SERVER|g"           \
        -e "s|\$OWNMINE_RCON_PASS|$OWNMINE_RCON_PASS|g"     \
        -e "s|\$OWNMINE_FOLDER|$OWNMINE_FOLDER|g"           \
        "$file.service"
done

echo "Config: systemd services (your root password is necessary)"
sudo systemctl daemon-reload

echo "Cleaning up..."
unset OWNMINE_HOME
unset OWNMINE_ZSHRC
unset OWNMINE_REPO
unset OWNMINE_SERVER
unset OWNMINE_FOLDER
unset OWNMINE_FILES
unset OWNMINE_RCON_PASS

echo "ownMine has been configured.
Check out out to use the commands with:
    ownmine help
    ownminebot help"

echo "Enjoy ownMine!"