#!/bin/zsh

echo "ownMine: self-hosted Minecraft server"
echo "Automated configuration script
"

echo "Initializing configuration script..."
OWNMINE_HOME="$HOME"
OWNMINE_ZSHRC=".zshrc"
OWNMINE_REPO="https://raw.githubusercontent.com/ibnunes/ownMine/master"
OWNMINE_SERVER-"minecraft"
OWNMINE_FOLDER=".minecraft.d"
OWNMINE_FILES=("mine" "pwd" "remote" "stdout" "utils")

echo "Config: .zshrc"
echo "# Defined by ownMine in .minecraft.d
if [ ! -d \"\$HOME\"/.minecraft.d ]; then
    mkdir -p \"\$HOME\"/.minecraft.d;
fi

for cfg in \"\$HOME\"/.minecraft.d/*.zsh; do
    . \"\$cfg\"
done
unset -v cfg

# ownMine scripts initialization
mine_server_declare_pwd
mine_server_declare_stdout
mine_debug_off" >> $OWNMINE_HOME/$OWNMINE_ZSHRC

echo "Get: ownMine zsh scripts"
for file in OWNMINE_FILES; do
    echo "    $file.zsh"
    curl -s "$OWNMINE_REPO/$OWNMINE_FOLDER/$file.zsh" -o "$OWNMINE_HOME/$OWNMINE_FOLDER/$file.zsh"
done

echo "Get: ownMine Discord bot"
curl -s "$OWNMINE_REPO/$OWNMINE_FOLDER/bot.py" -o "$OWNMINE_HOME/$OWNMINE_FOLDER/bot.py"

echo "Get: mcrcon (from Tiiffi GitHub repository)"
git clone https://github.com/Tiiffi/mcrcon.git "$OWNMINE_HOME/tools/mcrcon"

echo "Apply: zsh configurations"
source $OWNMINE_HOME/$OWNMINE_ZSHRC

echo "Add: Minecraft service"
read "What is your rcon password? " OWNMINE_RCON_PASS
echo "[Unit]
Description=ownMine Server
After=network.target

[Service]
User=$USER
Nice=1
KillMode=none
SuccessExitStatus=0 1
NoNewPrivileges=true
WorkingDirectory=$OWNMINE_HOME/$OWNMINE_SERVER
ExecStart=/usr/bin/java -Xmx2048M -Xms2048M -jar $OWNMINE_HOME/$OWNMINE_SERVER/server.jar nogui
ExecStop=$OWNMINE_HOME/tools/mcrcon/mcrcon -H 127.0.0.1 -P 25575 -p $OWNMINE_RCON_PASS stop
SyslogIdentifier=ownmine-server
Restart=always
RestartSec=120

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/minecraft.service

echo "Add: Discord bot service"
echo "[Unit]
Description=ownMine Discord Bot
After=network.target

[Service]
User=$USER
Nice=1
KillMode=none
SuccessExitStatus=0 1
NoNewPrivileges=true
WorkingDirectory=$OWNMINE_HOME/$OWNMINE_FOLDER
ExecStart=/usr/bin/python3 $OWNMINE_HOME/$OWNMINE_FOLDER/bot.py
ExecStop=/usr/bin/sh -c \"kill $(ps -ef | grep bot | awk '{print $2}' | head -1)\"
SyslogIdentifier=ownmine-discord
Restart=always
RestartSec=120

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/minebot.service

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

echo "ownMine has been configured. Check out out to use the commands with:
    mine help
    minebot help"

echo "Enjoy ownMine!"