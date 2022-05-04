# Turns on error for the operation
function ownmine_define_error() {
    if [ $1 -ne 0 ]; then
        OWNMINE_SERVER_OPERATION_SUCCESS=$1
    fi
}

# Turns Debug Mode on
function ownmine_debug_on() {
    echo "ownMine Server: DEBUG mode"
    OWNMINE_SERVER_DEBUG=1
}

# Turns Debug Mode off
function ownmine_debug_off() {
    # Optional output: uncomment next line if you want it
    # echo "ownMine Server: PRODUCTION mode"
    OWNMINE_SERVER_DEBUG=0
}


function ownminebot() {
    # Help output
    function ownminebothelp() {
        echo "$OWNMINE_SERVER_STDOUT_HELP"
    }

    if [ $# -ne 1 ]; then
        echo "Too many arguments"
        return 1
    fi

    case $1 in
        ("help")
            ownminebothelp
            ;;
        ("start")
            echo "ownMine Discord Bot: Start service"
            sudo systemctl start ownminebot.service
            ;;
        ("stop")
            echo "ownMine Discord Bot: Stop service"
            sudo systemctl stop ownminebot.service
            ;;
        ("status")
            echo "ownMine Discord Bot: Service status"
            sudo systemctl status ownminebot.service
            ;;
        (*)
            echo "Unknown option $1"
            return 1 ;;
    esac
}


function ownmine() {
    # === REGION Auxiliary Functions ===
    # General function to sync with remote server
    function ownmine_server_general_sync() {
        # 1. Make temporary folder
        TMP=$(mktemp -d)
        echo "Temporary folder: $TMP"

        # 1.5. Assign human readable variables
        REMOTE_DIR=$1
        if [[ $2 == $OWNMINE_TEMP ]]; then DIR_SOURCE="$TMP";      else DIR_SOURCE=$2      fi
        if [[ $3 == $OWNMINE_TEMP ]]; then DIR_DESTINATION="$TMP"; else DIR_DESTINATION=$3 fi

        # Debug Mode: halt!
        if [ $OWNMINE_SERVER_DEBUG -eq 1 ]; then
            echo "Variables {
    REMOTE_DIR      :  $REMOTE_DIR
    DIR_SOURCE      :  $DIR_SOURCE
    DIR_DESTINATION :  $DIR_DESTINATION
}"
            rmtemp "$TMP"
            echo "$OWNMINE_SERVER_STDOUT_DEBUG_HALT"
            return 0
        fi

        # 2. Mount remote server
        mountremote "//$OWNMINE_SAMBA_REMOTE/$REMOTE_DIR" "$TMP"
        if [ $OWNMINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
            rmtemp "$TMP"
            return $OWNMINE_SERVER_OPERATION_SUCCESS
        fi

        # 3. Sync with remote server
        echo "$OWNMINE_SERVER_OPERATION_DESCRIPTION... (this might take a while)"
        syncremote "$DIR_SOURCE" "$DIR_DESTINATION"
        if [ $OWNMINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
            rmtemp "$TMP"
            return $OWNMINE_SERVER_OPERATION_SUCCESS
        fi

        # 4. Unmount remote server and delete temporary folder
        umountremote "$TMP"
        ownmine_define_error $?
        rmtemp "$TMP"
        return $OWNMINE_SERVER_OPERATION_SUCCESS
    }

    # Proxy for push
    function ownmine_server_push() {
        OWNMINE_SERVER_OPERATION_DESCRIPTION="Pushing updates to remote server"
        ownmine_server_general_sync "$OWNMINE_SAMBA_FOLDER_MAIN" "$OWNMINE_LOCAL_SERVER" "$OWNMINE_TEMP"
        return $OWNMINE_SERVER_OPERATION_SUCCESS
    }

    # Proxy for pull
    function ownmine_server_pull() {
        OWNMINE_SERVER_OPERATION_DESCRIPTION="Pulling backup from remote server"
        ownmine_server_general_sync "$OWNMINE_SAMBA_FOLDER_MAIN" "$OWNMINE_TEMP" "$OWNMINE_LOCAL_SERVER"
        return $OWNMINE_SERVER_OPERATION_SUCCESS
    }

    # Proxy for backup sync
    function ownmine_server_sync() {
        OWNMINE_SERVER_OPERATION_DESCRIPTION="Syncing backups with remote server"
        ownmine_server_general_sync "$OWNMINE_SAMBA_FOLDER_BACKUP" "$OWNMINE_LOCAL_BACKUP" "$OWNMINE_TEMP"
        return $OWNMINE_SERVER_OPERATION_SUCCESS
    }

    # Local backup
    function ownmine_server_backup() {
        echo "Making local backup..."
        if [ $OWNMINE_SERVER_DEBUG -eq 1 ]; then echo "$OWNMINE_SERVER_STDOUT_DEBUG_HALT"; return 0; fi
        sudo cp -rp "$OWNMINE_LOCAL_SERVER" "$OWNMINE_LOCAL_BACKUP/minecraft-$(date +%Y%m%d%H%M%S)"
        ownmine_define_error $?
        if [ $OWNMINE_SERVER_OPERATION_SUCCESS -eq 0 ]; then
            echo "Local backup successful."
            return $OWNMINE_SERVER_OPERATION_SUCCESS
        fi
        echo "Local backup failed."
    }

    # Help output
    function ownminehelp() {
        echo "$OWNMINE_SERVER_STDOUT_HELP"
    }
    # === END REGION ===================


    # === Function =====================
    # Resets success flag
    OWNMINE_SERVER_OPERATION_SUCCESS=0

    # Checks if first argument is null
    if [ -z "$1" ]; then
        ownminehelp
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
        ownminehelp
        return 0
    fi

    # Checks if debug mode is asked for
    if [[ "$1" == "debug" ]]; then
        case $2 in
            ("on")  ownmine_debug_on  ;;
            ("off") ownmine_debug_off ;;
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
    if [ $OWNMINE_SERVER_DEBUG -eq 1 ]; then
        case $1 in
            ("start" | "stop" | "startall" | "stopall" | "status" )
                echo "$OWNMINE_SERVER_STDOUT_DEBUG_HALT"
                return 0 ;;
        esac
    fi

    case $1 in
        ("start")
            echo "ownMine Server: Start service"
            sudo systemctl start ownmine.service
            ;;
        ("stop")
            echo "ownMine Server: Stop service"
            sudo systemctl stop ownmine.service
            ;;
        ("startall")
            ownmine start
            ownminebot start
            ;;
        ("stopall")
            ownmine stop
            ownminebot stop
            ;;
        ("status")
            echo "ownMine Server: Service status"
            sudo systemctl status ownmine.service
            ;;
        ("push")
            echo "ownMine Server: Push remote backup"
            ownmine_server_push
            ;;
        ("sync")
            echo "ownMine Server: Sync backups"
            ownmine_server_sync
            ;;
        ("backup")
            echo "ownMine Server: Local Backup"
            ownmine_server_backup
            ;;
        ("pull")
            echo "ownMine Server: Recover from remote backup"
            echo "This will:
  1) Make a local backup;
  2) Sync all backups with remote server;
  3) Recover from main remote backup."
            confirm "Are you sure you want to proceed?"
            if [ $? -eq 1 ]; then return 0; fi
            ownmine backup
            ownmine sync
            ownmine_server_pull
            ;;
        ("exit")
            ownmine stop
            ownmine push
            ;;
        (*)
            echo "Unknown option $1"
            return 1 ;;
    esac

    # Final message
    if [ $OWNMINE_SERVER_OPERATION_SUCCESS -eq 0 ]; then
        echo "[$1: SUCCESS]"
    else
        echo "[$1: FAILED]"
    fi
    return $OWNMINE_SERVER_OPERATION_SUCCESS
}
