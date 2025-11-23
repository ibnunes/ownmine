function ownmine_server_declare_stdout() {
    # Help output
    OWNMINE_SERVER_STDOUT_HELP="ownmine --- help
Call:             ownmine [option]
Options:
  start           Starts the server.
  stop            Stops the server.
  exit            Executes 'stop' and 'push' sequentially.
  status          Checks for the server daemon status.
  push            Pushes current active server files to the mirror backup directory.
  pull            Recovers from the mirror backup. Makes a permanent snapshot first.
  snapshot        Makes a permanent snapshot.
  exec            Executes command via RCON server.
  debug <on/off>  Turns Debug Mode on or off
"

    OWNMINE_SERVER_STDOUT_DEBUG_HALT="HALT: Debug mode"
}
