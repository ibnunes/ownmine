# Removes temporary folder (must be given by argument)
function rmtemp() {
    rmdir "$1"
    mine_define_error $?
    if [ $MINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
        echo "Failed to remove temporary folder"
        return $MINE_SERVER_OPERATION_SUCCESS
    fi
    echo "Temporary folder removed."
}

# Mounts remote server
function mountremote() {
    if [ $MINE_SERVER_DEBUG -eq 1 ]; then echo "$MINE_SERVER_STDOUT_DEBUG_HALT"; return 0; fi
    sudo mount -t cifs "$1" "$2" -o username=$SMB_USER,password=$SMB_PASSWORD,domain=$SMB_DOMAIN,vers=2.0,uid=$SMB_UID,gid=$SMB_GID,file_mode=$SMB_FILE_MODE,dir_mode=$SMB_DIR_MODE
    mine_define_error $?
    if [ $MINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
        echo "Failed to mount remote server"
        return $MINE_SERVER_OPERATION_SUCCESS
    fi
    echo "Mounted remote server."
}

# Unmounts remote server
function umountremote() {
    if [ $MINE_SERVER_DEBUG -eq 1 ]; then echo "$MINE_SERVER_STDOUT_DEBUG_HALT"; return 0; fi
    sudo umount "$1"
    mine_define_error $?
    if [ $MINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
        echo "Failed to unmount remote server"
        return $MINE_SERVER_OPERATION_SUCCESS
    fi
    echo "Remote server unmounted."
}

# Syncs with remote server
function syncremote() {
    if [ $MINE_SERVER_DEBUG -eq 1 ]; then echo "$MINE_SERVER_STDOUT_DEBUG_HALT"; return 0; fi
    sudo rsync -arutEP --prune-empty-dirs "$1" "$2"
    mine_define_error $?
    if [ $MINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
        echo "Failed to sync with remote server"
        return $MINE_SERVER_OPERATION_SUCCESS
    fi
    echo "Synced with remote server."
}