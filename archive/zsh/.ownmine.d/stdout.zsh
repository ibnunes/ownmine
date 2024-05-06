function ownmine_server_declare_stdout() {
    # Help output
    OWNMINE_SERVER_STDOUT_HELP="ownmine --- help
Call:             ownmine [option]
Options:
  start           Starts the server.
  stop            Stops the server.
  exit            Executes 'stop' and 'push' sequentially.
  status          Checks for the server daemon status.
  push            Pushes a main backup to the remote server.
  pull            Recovers from the main remote backup. Makes a local backup first.
  backup          Makes a local backup.
  sync            Syncs local backups with the remote server.
  debug <on/off>  Turns Debug Mode on or off
"

    OWNMINE_SERVER_STDOUT_DEBUG_HALT="HALT: Debug mode"
}