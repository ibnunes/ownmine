#!/bin/zsh

# ownmine 1.2.0
# Igor Nunes, 2024

# This script is a very simple "automated" (cof cof) installation script for ownmine.
# A more complete version might be done in the future, no promises.
# This only supports zshell for now.

echo "ownmine: simple self-hosted Minecraft server management"
echo "Automated configuration script for ZSH"

# 1. Constants declaration
echo "Initializing configuration script..."
local OWNMINE_HOME="$HOME"
local OWNMINE_ZSHRC=".zshrc"
local OWNMINE_REPO="https://raw.githubusercontent.com/ibnunes/ownMine/master"
local OWNMINE_SERVER="ownmine"
local OWNMINE_FOLDER=".ownmine.d"
local OWNMINE_FILES=("ownmine" "const" "remote" "stdout" "utils")
local OWNMINE_SERVICE_FOLDER="systemd/system"
local OWNMINE_SERVICE_FILES=("ownmine")
local OWNMINE_LOG_FOLDER="rsyslog.d"
local OWNMINE_LOG_FILES=("ownmine")

# 2. Append configuration to .zshrc file
echo "Config: .zshrc"
local OWNMINE_ZSH_CONFIG=$(curl -s $OWNMINE_REPO/$OWNMINE_ZSHRC)
if ! grep -q $OWNMINE_ZSH_CONFIG $OWNMINE_HOME/$OWNMINE_ZSHRC; then
    echo $OWNMINE_ZSH_CONFIG >> $OWNMINE_HOME/$OWNMINE_ZSHRC
fi

# 3. Get all scripts for server management
echo "Get: ownmine ZSH server management scripts"
for file in $OWNMINE_FILES; do
    echo "    $file.zsh"
    curl -s "$OWNMINE_REPO/$OWNMINE_FOLDER/$file.zsh" -o "$OWNMINE_HOME/$OWNMINE_FOLDER/$file.zsh"
done

# 5. Get mcrcon tool to be able to stop the server safely
echo "Get: mcrcon (from Tiiffi GitHub repository)"
git clone -q https://github.com/Tiiffi/mcrcon.git "$OWNMINE_HOME/tools/mcrcon"
(cd "$OWNMINE_HOME/tools/mcrcon" && make)

# 6. Apply new configurations
echo "Apply: zsh configurations"
echo -n "What is your Minecraft server rcon password? (You can define it later manually) "
read OWNMINE_RCON_PASS
sed -i                                                      \
    -e "s|\$TBD_OWNMINE_RCON_PASS|$OWNMINE_RCON_PASS|g"     \
    "$OWNMINE_HOME/$OWNMINE_FOLDER/const.zsh"
source $OWNMINE_HOME/$OWNMINE_ZSHRC

# 7. Get systemd services
echo "Get: Minecraft services"
for file in $OWNMINE_SERVICE_FILES; do
    echo "    $file.service"
    sudo curl -s "$OWNMINE_REPO/$OWNMINE_SERVICE_FOLDER/$file.service" -o "/etc/$OWNMINE_SERVICE_FOLDER/$file.service"
    sudo sed -i                                             \
        -e "s|\$USER|$USER|g"                               \
        -e "s|\$OWNMINE_HOME|$OWNMINE_HOME|g"               \
        -e "s|\$OWNMINE_SERVER|$OWNMINE_SERVER|g"           \
        -e "s|\$OWNMINE_RCON_PASS|$OWNMINE_RCON_PASS|g"     \
        -e "s|\$OWNMINE_FOLDER|$OWNMINE_FOLDER|g"           \
        "$file.service"
done

# 8. Get logging configuration
echo "Get: ownmine logging services"
for file in $OWNMINE_LOG_FILES; do
    echo "    $file.conf"
    sudo curl -s "$OWNMINE_REPO/$OWNMINE_LOG_FOLDER/$file.conf" -o "/etc/$OWNMINE_LOG_FOLDER/$file.log"
    sudo sed -i                                             \
        -e "s|\$OWNMINE_LOG_FOLDER|$OWNMINE_LOG_FOLDER|g"   \
        -e "s|\$OWNMINE_LOG_FILE|$OWNMINE_LOG_FILE|g"       \
        "$file.conf"
done

# 9. Loads new systemd services
echo "Config: systemd services (your root password is necessary)"
sudo systemctl daemon-reload

# 10. Constants cleanup
echo "Cleaning up..."
unset OWNMINE_HOME
unset OWNMINE_ZSHRC
unset OWNMINE_REPO
unset OWNMINE_SERVER
unset OWNMINE_FOLDER
unset OWNMINE_FILES
unset OWNMINE_SERVICE_FOLDER
unset OWNMINE_SERVICE_FILES
unset OWNMINE_LOG_FOLDER
unset OWNMINE_LOG_FILES
unset OWNMINE_RCON_PASS

echo "ownmine has been configured.
Check out out to use the commands with:  ownmine help"

echo "Enjoy ownmine!"