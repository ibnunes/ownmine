# Turns on error for the operation
function mine_define_error() {
    if [ $1 -ne 0 ]; then
        MINE_SERVER_OPERATION_SUCCESS=$1
    fi
}

# Turns Debug Mode on
function mine_debug_on() {
    echo "ownMine Server: DEBUG mode"
    MINE_SERVER_DEBUG=1
}

# Turns Debug Mode off
function mine_debug_off() {
    # Optional output: uncomment next line if you want it
    # echo "ownMine Server: PRODUCTION mode"
    MINE_SERVER_DEBUG=0
}


function minebot() {
    if [ $# -ne 1 ]; then
        echo "Too many arguments"
        return 1
    fi

    case $1 in
        ("start")
            echo "ownMine Discord Bot: Start service"
            sudo systemctl start minebot.service
            ;;
        ("stop")
            echo "ownMine Discord Bot: Stop service"
            sudo systemctl stop minebot.service
            ;;
        ("status")
            echo "ownMine Discord Bot: Service status"
            sudo systemctl status minebot.service
            ;;
        (*)
            echo "Unknown option $1"
            return 1 ;;
    esac
}


function mine() {
    # === REGION Auxiliary Functions ===
    # General function to sync with remote server
    function mine_server_general_sync() {
        # 1. Make temporary folder
        TMP=$(mktemp -d)
        echo "Temporary folder: $TMP"

        # 1.5. Assign human readable variables
        REMOTE_DIR=$1
        if [[ $2 == $MINE_TEMP ]]; then DIR_SOURCE="$TMP";      else DIR_SOURCE=$2      fi
        if [[ $3 == $MINE_TEMP ]]; then DIR_DESTINATION="$TMP"; else DIR_DESTINATION=$3 fi

        # Debug Mode: halt!
        if [ $MINE_SERVER_DEBUG -eq 1 ]; then
            echo "Variables {
    REMOTE_DIR      :  $REMOTE_DIR
    DIR_SOURCE      :  $DIR_SOURCE
    DIR_DESTINATION :  $DIR_DESTINATION
}"
            rmtemp "$TMP"
            echo "$MINE_SERVER_STDOUT_DEBUG_HALT"
            return 0
        fi

        # 2. Mount remote server
        mountremote "//$MINE_SAMBA_REMOTE/$REMOTE_DIR" "$TMP"
        if [ $MINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
            rmtemp "$TMP"
            return $MINE_SERVER_OPERATION_SUCCESS
        fi

        # 3. Sync with remote server
        echo "$MINE_SERVER_OPERATION_DESCRIPTION... (this might take a while)"
        syncremote "$DIR_SOURCE/*" "$DIR_DESTINATION"
        if [ $MINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
            rmtemp "$TMP"
            return $MINE_SERVER_OPERATION_SUCCESS
        fi

        # 4. Unmount remote server and delete temporary folder
        umountremote "$TMP"
        mine_define_error $?
        rmtemp "$TMP"
        return $MINE_SERVER_OPERATION_SUCCESS
    }

    # Proxy for push
    function mine_server_push() {
        MINE_SERVER_OPERATION_DESCRIPTION="Pushing updates to remote server"
        mine_server_general_sync "$MINE_SAMBA_FOLDER_MAIN" "$MINE_LOCAL_SERVER" "$MINE_TEMP"
        return $MINE_SERVER_OPERATION_SUCCESS
    }

    # Proxy for pull
    function mine_server_pull() {
        MINE_SERVER_OPERATION_DESCRIPTION="Pulling backup from remote server"
        mine_server_general_sync "$MINE_SAMBA_FOLDER_MAIN" "$MINE_TEMP" "$MINE_LOCAL_SERVER"
        return $MINE_SERVER_OPERATION_SUCCESS
    }

    # Proxy for backup sync
    function mine_server_sync() {
        MINE_SERVER_OPERATION_DESCRIPTION="Syncing backups with remote server"
        mine_server_general_sync "$MINE_SAMBA_FOLDER_BACKUP" "$MINE_LOCAL_BACKUP" "$MINE_TEMP"
        return $MINE_SERVER_OPERATION_SUCCESS
    }

    # Local backup
    function mine_server_backup() {
        echo "Making local backup..."
        if [ $MINE_SERVER_DEBUG -eq 1 ]; then echo "$MINE_SERVER_STDOUT_DEBUG_HALT"; return 0; fi
        sudo cp -rp "$MINE_LOCAL_SERVER" "$MINE_LOCAL_BACKUP/minecraft-$(date +%Y%m%d%H%M%S)"
        mine_define_error $?
        if [ $MINE_SERVER_OPERATION_SUCCESS -eq 0 ]; then
            echo "Local backup successful."
            return $MINE_SERVER_OPERATION_SUCCESS
        fi
        echo "Local backup failed."
    }

    # Help output
    function minehelp() {
        echo "$MINE_SERVER_STDOUT_HELP"
    }
    # === END REGION ===================


    # === Function =====================
    # Resets success flag
    MINE_SERVER_OPERATION_SUCCESS=0

    # Checks if first argument is null
    if [ -z "$1" ]; then
        minehelp
        return 0
    fi
    
    # Checks number of arguments
    case $# in
        (1) ;;
        (2) if [[ $1 != "debug" ]]; then
                echo "Too many arguments"
                return 1
            fi ;;
        (*) echo "Too many arguments"
            return 1 ;;
    esac
    
    # Checks if help is asked for
    if [[ "$1" == "help" ]]; then
        minehelp
        return 0
    fi

    # Checks if debug mode is asked for
    if [[ "$1" == "debug" ]]; then
        case $2 in
            ("on")  mine_debug_on  ;;
            ("off") mine_debug_off ;;
            (*)     echo "Unknow option $2 for $1" ;;
        esac
        return 0
    fi

    # Executes option: requires sudo
    if [[ $(sudo echo -n) ]]; then
        echo "Invalid password. Cannot execute."
        return 1
    fi

    # Debug Mode: halt!
    if [ $MINE_SERVER_DEBUG -eq 1 ]; then
        case $1 in
            ("start" | "stop" | "startall" | "stopall" | "status" )
                echo "$MINE_SERVER_STDOUT_DEBUG_HALT"
                return 0 ;;
        esac
    fi

    case $1 in
        ("start")
            echo "ownMine Server: Start service"
            sudo systemctl start minecraft.service
            ;;
        ("stop")
            echo "ownMine Server: Stop service"
            sudo systemctl stop minecraft.service
            ;;
        ("startall")
            mine start
            minebot start
            ;;
        ("stopall")
            mine stop
            minebot stop
            ;;
        ("status")
            echo "ownMine Server: Service status"
            sudo systemctl status minecraft.service
            ;;
        ("push")
            echo "ownMine Server: Push remote backup"
            mine_server_push
            ;;
        ("sync")
            echo "ownMine Server: Sync backups"
            mine_server_sync
            ;;
        ("backup")
            echo "ownMine Server: Local Backup"
            mine_server_backup
            ;;
        ("pull")
            echo "ownMine Server: Recover from remote backup"
            echo "This will:
  1) Make a local backup;
  2) Sync all backups with remote server;
  3) Recover from main remote backup."
            confirm "Are you sure you want to proceed?"
            if [ $? -eq 1 ]; then return 0; fi
            mine backup
            mine sync
            mine_server_pull
            ;;
        ("exit")
            mine stop
            mine push
            ;;
        (*)
            echo "Unknown option $1"
            return 1 ;;
    esac

    # Final message
    if [ $1 -eq 0 ]; then
        echo "[$1: SUCCESS]"
    else
        echo "[$1: FAILED]"
    fi
    return $MINE_SERVER_OPERATION_SUCCESS
}
