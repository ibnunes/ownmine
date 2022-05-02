function mine_server_declare_pwd() {
    # Samba share for Minecraft Server
    MINE_SAMBA_SERVER=              # Server IP
    MINE_SAMBA_SHARE=               # Samba share
    MINE_SAMBA_SUBDIR=              # Directory inside share
    MINE_SAMBA_FOLDER_MAIN=         # Folder for main backup
    MINE_SAMBA_FOLDER_BACKUP=       # Folder for synced older backups

    # Samba login data
    SMB_USER=                       # Samba username
    SMB_DOMAIN=                     # Samba domain (traditionally WORKGROUP)
    SMB_PASSWORD=                   # Samba password
    SMB_GID=                        # Remote GID for username
    SMB_UID=                        # Remote UID for username
    SMB_FILE_MODE=                  # File mode (suggestion: 0770)
    SMB_DIR_MODE=                   # Directory mode (suggestion: 0770)

    # Local directories
    MINE_LOCAL_SERVER="ownmine"     # Local directory where server is located
    MINE_LOCAL_BACKUP="ownmine.bk"  # Directory of local backups

    # === DO NOT CHANGE FROM HERE ON! ===
    # Complete remote directory
    MINE_SAMBA_REMOTE="$MINE_SAMBA_SERVER/$MINE_SAMBA_SHARE/$MINE_SAMBA_SUBDIR"

    # Function automation and communication
    MINE_TEMP="{TMP}"
    MINE_SERVER_OPERATION_SUCCESS=0
}