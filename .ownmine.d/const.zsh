function ownmine_server_declare_const() {
    # Samba share for Minecraft Server
    OWNMINE_SAMBA_SERVER=                                           # Server IP
    OWNMINE_SAMBA_SHARE=                                            # Samba share
    OWNMINE_SAMBA_SUBDIR=                                           # Directory inside share
    OWNMINE_SAMBA_FOLDER_MAIN=                                      # Folder for main backup
    OWNMINE_SAMBA_FOLDER_BACKUP=                                    # Folder for synced older backups

    # Samba login data
    SMB_USER=                                                       # Samba username
    SMB_DOMAIN=                                                     # Samba domain (usually "WORKGROUP")
    SMB_PASSWORD=                                                   # Samba password
    SMB_GID=                                                        # Samba user GID
    SMB_UID=                                                        # Samba user UID
    SMB_FILE_MODE=0770                                              # File mode (suggestion: 0770)
    SMB_DIR_MODE=0770                                               # Directory mode (suggestion: 0770)

    # Local directories
    OWNMINE_LOCAL_HOME="$HOME"                                      # Local base directory of the server
    OWNMINE_LOCAL_USER="$USER"                                      # Local username
    OWNMINE_LOCAL_SERVER="$OWNMINE_LOCAL_HOME/ownmine"              # Local directory where server is located
    OWNMINE_LOCAL_BACKUP="$OWNMINE_LOCAL_HOME/ownmine.bk"           # Directory of local backups

    # Logging
    OWNMINE_LOG_FOLDER="/var/log"
    OWNMINE_LOG_FILE="ownmine.log"

    # RCON server
    OWNMINE_RCON_BIN="$OWNMINE_LOCAL_HOME/tools/mcrcon/mcrcon"      # Complete path to 'mcrcon' tool
    OWNMINE_RCON_IP="127.0.0.1"                                     # RCON server IP
    OWNMINE_RCON_PORT=25575                                         # RCON server port
    OWNMINE_RCON_PASS=$TBD_OWNMINE_RCON_PASS                        # RCON server password

    # === DO NOT CHANGE FROM HERE ON! ===
    # Complete remote directory
    OWNMINE_SAMBA_REMOTE="$OWNMINE_SAMBA_SERVER/$OWNMINE_SAMBA_SHARE/$OWNMINE_SAMBA_SUBDIR"

    # Function automation and communication
    OWNMINE_TEMP="{TMP}"
    OWNMINE_SERVER_OPERATION_SUCCESS=0
}