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