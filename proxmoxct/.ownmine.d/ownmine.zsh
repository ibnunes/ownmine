# Turns on error for the operation
function ownmine_define_error() {
    if [ $1 -ne 0 ]; then
        OWNMINE_SERVER_OPERATION_SUCCESS=$1
    fi
}

# Turns Debug Mode on
function ownmine_debug_on() {
    echo "ownmine Server: DEBUG mode"
    OWNMINE_SERVER_DEBUG=1
}

# Turns Debug Mode off
function ownmine_debug_off() {
    # Optional output: uncomment next line if you want it
    # echo "ownmine Server: PRODUCTION mode"
    OWNMINE_SERVER_DEBUG=0
}


function ownmine() {
    # === REGION Auxiliary Functions ========

    # General function to sync Ownmine server directories
    # Args:
    #    $1   Source path
    #    $2   Destination path
    #    $3   Sync mode (default: none)
    function ownmine_server_general_sync() {
        # Assign dirs
        DIR_SOURCE=$1
        DIR_DESTINATION=$2

        # Assign sync mode
        if [[ $3 == "" ]]; then SYNC_MODE="-u"; else SYNC_MODE=$3; fi

        # Determine chown
        if [[ $OWNMINE_REMOTE_UID != "" && $OWNMINE_REMOTE_GID != "" ]]; then
            SYNC_CHOWN="--chown=$OWNMINE_REMOTE_UID:$OWNMINE_REMOTE_GID"
        else
            SYNC_CHOWN=""
        fi

        # Debug Mode: halt!
        if [ $OWNMINE_SERVER_DEBUG -eq 1 ]; then
            echo "Variables {
    DIR_SOURCE      :  $DIR_SOURCE
    DIR_DESTINATION :  $DIR_DESTINATION
    SYNC_MODE       :  $SYNC_MODE
    SYNC_CHOWN      :  $SYNC_CHOWN
}"
            echo "$OWNMINE_SERVER_STDOUT_DEBUG_HALT"
            return 0
        fi

        # Execute rsync
        echo "$OWNMINE_SERVER_OPERATION_DESCRIPTION... (this might take a while)"
        sudo rsync -artmEP $SYNC_MODE --chmod=770 $SYNC_CHOWN "$DIR_SOURCE/" "$DIR_DESTINATION"
        ownmine_define_error $?
        if [ $OWNMINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
            echo "Failed to sync"
        else
            echo "Successfully synced."
        fi
        return $OWNMINE_SERVER_OPERATION_SUCCESS
    }

    # Proxy for push
    function ownmine_server_push() {
        OWNMINE_SERVER_OPERATION_DESCRIPTION="Pushing updates to mirror"
        ownmine_server_general_sync "$OWNMINE_SERVER" "$OWNMINE_MIRROR"
        return $OWNMINE_SERVER_OPERATION_SUCCESS
    }

    # Proxy for pull
    function ownmine_server_pull() {
        OWNMINE_SERVER_OPERATION_DESCRIPTION="Pulling last mirror"
        ownmine_server_general_sync "$OWNMINE_SERVER" "$OWNMINE_MIRROR"
        return $OWNMINE_SERVER_OPERATION_SUCCESS
    }

    # Permanent snapshot
    function ownmine_server_snapshot() {
        echo "Making a permanent snapshot..."

        # Debug mode: halt!
        if [ $OWNMINE_SERVER_DEBUG -eq 1 ]; then echo "$OWNMINE_SERVER_STDOUT_DEBUG_HALT"; return 0; fi

        ownmine stop

        sudo cp -pr "$OWNMINE_SERVER" "$OWNMINE_SNAPSHOTS/$(date +%Y%m%d%H%M%S)"
        ownmine_define_error $?
        if [ $OWNMINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
            echo "Snapshot failed."
        else
            echo "Snapshot successful."
        fi

        ownmine start

        return $OWNMINE_SERVER_OPERATION_SUCCESS
    }

    # Help output
    function ownminehelp() {
        echo "$OWNMINE_SERVER_STDOUT_HELP"
    }

    # Command relay for RCON server
    function ownmine_rcon_command() {
        $OWNMINE_RCON_BIN                   \
            -H $OWNMINE_RCON_IP             \
            -P $OWNMINE_RCON_PORT           \
            -p $OWNMINE_RCON_PASS "$*"
        ownmine_define_error $?
        if [ $OWNMINE_SERVER_OPERATION_SUCCESS -ne 0 ]; then
            echo "Command relay to RCON server failed."
        fi
    }
    # === END REGION Auxiliary Functions ====


    # === REGION Function ===================
    # Reset success flag
    OWNMINE_SERVER_OPERATION_SUCCESS=0

    # Show help if first argument is null
    if [ -z "$1" ]; then
        ownminehelp
        return 0
    fi

    # Check number of arguments
    case $# in
        (1) ;;
        (2) if [[ $1 != "debug" && $1 != "exec" ]]; then
                echo "Too many arguments"
                return 1
            fi ;;
        (*) if [[ $1 != "exec" ]]; then
                echo "Too many arguments"
                return 1
            fi ;;
    esac

    # Check if help is asked for
    if [[ "$1" == "help" ]]; then
        ownminehelp
        return 0
    fi

    # Check if debug mode is asked for
    if [[ "$1" == "debug" ]]; then
        case $2 in
            ("on")  ownmine_debug_on  ;;
            ("off") ownmine_debug_off ;;
            (*)     echo "Unknow option $2 for $1" ;;
        esac
        return 0
    fi

    # Executes option: requires sudo
    if [[ $1 != "exec" ]]; then
        if [[ $(sudo echo -n) ]]; then
            echo "Invalid password. Cannot execute."
            return 1
        fi
    fi

    # Debug Mode: halt! (just for start, stop and status commands)
    if [ $OWNMINE_SERVER_DEBUG -eq 1 ]; then
        case $1 in
            ("start" | "stop" | "status" )
                echo "$OWNMINE_SERVER_STDOUT_DEBUG_HALT"
                return 0 ;;
        esac
    fi

    case $1 in
        ("start")
            echo "ownmine ($OWNMINE_ID): Start service"
            sudo systemctl start ownmine.service
            ;;
        ("stop")
            echo "ownmine ($OWNMINE_ID): Stop service"
            sudo systemctl stop ownmine.service
            ;;
        ("status")
            echo "ownmine ($OWNMINE_ID): Service status"
            sudo systemctl status ownmine.service
            ;;
        ("exec")
            ownmine_rcon_command "${@:2}"
            ;;
        ("push")
            echo "ownmine ($OWNMINE_ID): Push to mirror"
            ownmine_server_push
            ;;
        ("snapshot")
            echo "ownmine ($OWNMINE_ID): Permanent snapshot"
            ownmine_server_snapshot
            ;;
        ("pull")
            echo "ownmine ($OWNMINE_ID): Pull from mirror"
            echo "This will:
  1) Make a permanent snapshot;
  3) Recover from mirror."
            confirm "Are you sure you want to proceed?"
            if [ $? -eq 1 ]; then return 0; fi
            ownmine_server_snapshot
            ownmine_server_pull
            ;;
        ("exit")
            ownmine stop
            ownmine_server_push
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
