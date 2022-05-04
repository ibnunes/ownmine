function ownmine_server_declare_stdout() {
    # Help output
    OWNMINE_SERVER_STDOUT_HELP="Minecraft Server: Help
Call:             mine [option]
Options:
  start           Starts the server.
  stop            Stops the server.
  startall        Starts both the server and the Discord bot.
  stopall         Stops both the server and the Discord bot.
  exit            Executes 'stop' and 'push' sequentially.
  status          Checks for the server daemon status.
  push            Pushes a main backup to the remote server.
  pull            Recovers from the main remote backup. Makes a local backup first.
  backup          Makes a local backup.
  sync            Syncs local backups with the remote server.
  debug <on/off>  Turns Debug Mode on or off
"

    OWNMINEBOT_STDOUT_HELP="Minecraft Discord Bot: Help
Call:             minebot [option]
Options:
  start           Starts the bot service
  stop            Stops the bot service
  status          Checks for the bot daemon status.
"

    OWNMINE_SERVER_STDOUT_DEBUG_HALT="HALT: Debug mode"
}