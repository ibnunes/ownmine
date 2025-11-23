function ownmine_server_declare_const() {
    # Server identifier (no spaces nor special chars, stick to letters, numbers, dots, underscores and dashes)
    OWNMINE_ID="my_server"

    # Ownmine fundamental directories
    OWNMINE_BASE_DIR="/mnt"                                         # Ownmine base directory
    OWNMINE_CONFIG="$HOME/.ownmine.d"                               # Ownmine scripts and configurations
    OWNMINE_TOOLS="$OWNMINE_BASE_DIR/tools"                         # Ownmine auxiliary tools

    # Ownmine server directories
    OWNMINE_SERVER="$OWNMINE_BASE_DIR/srv"                          # Active Minecraft server
    OWNMINE_MIRROR="$OWNMINE_BASE_DIR/mirror"                       # Daily server mirror
    OWNMINE_SNAPSHOTS="$OWNMINE_BASE_DIR/snapshots"                 # Permanent manual snapshots

    # Users
    OWNMINE_LOCAL_USER="$USER"                                      # Local username
    OWNMINE_REMOTE_UID=""                                           # Remote UID - to set root Proxmox locations with approppriate UID - leave empty if unsure
    OWNMINE_REMOTE_GID=""                                           # Remote GID - to set root Proxmox locations with approppriate GID - leave empty if unsure

    # Logging
    OWNMINE_LOG_DIR="$OWNMINE_BASE_DIR/log"
    OWNMINE_LOG_FILE="ownmine-$OWNMINE_ID.log"

    # RCON server
    OWNMINE_RCON_BIN="$OWNMINE_TOOLS/mcrcon/mcrcon"
    OWNMINE_RCON_IP="127.0.0.1"                                     # RCON server IP
    OWNMINE_RCON_PORT=25575                                         # RCON server port
    OWNMINE_RCON_PASS="my_awesome_password"                         # RCON server password

    # If running in a root environment where 'sudo' does not exist, uncomment the following alias
    # alias sudo=""

    # Function automation and communication - DO NOT CHANGE THESE
    OWNMINE_SERVER_OPERATION_SUCCESS=0
    OWNMINE_SERVER_OPERATION_DESCRIPTION=""
}
