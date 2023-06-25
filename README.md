# ownMine

**Automation scripts for self-hosted Minecraft servers**

**TODO:** Complete this README. 😅


## Installation

This script has not been properly tested yet! Use at your own risk!

```
zsh -c "$(curl -fsSL https://raw.githubusercontent.com/ibnunes/ownMine/master/setup.zsh)"
```


## Configuration

The file `const.zsh` contains all internal variables used by **ownMine**. This file is to be properly filled by the user.

* ✅ You must define the values by yourself.
* ⚠️ These are pre-filled with default values, but can be modified.
* ❌ Do **NOT** change theses values!

| Variable | Should be edited | Description |
| --- | --- | --- |
| **Remote SMB share &mdash; directory** |
| `OWNMINE_SAMBA_SERVER`             | ✅ | Server IP or domain. |
| `OWNMINE_SAMBA_SHARE`              | ✅ | SMB share. |
| `OWNMINE_SAMBA_SUBDIR`             | ✅ | Directory/ies inside SMB share. |
| `OWNMINE_SAMBA_FOLDER_MAIN`        | ✅ | Folder for main backup. Used by `push` option. |
| `OWNMINE_SAMBA_FOLDER_BACKUP`      | ✅ | Folder for older backups. Used by `sync` option. |
| **Remote SMB share &mdash; login data** |
| `SMB_USER`                         | ✅ | Remote SMB username. |
| `SMB_DOMAIN`                       | ✅ | Remote SMB domain. <br> *E.g.* Usually `WORKGROUP` for Windows networks. |
| `SMB_PASSWORD`                     | ✅ | SMB password for the username defined in `SMB_USER`. |
| `SMB_GID`                          | ✅ | Remote SMB user UID. |
| `SMB_UID`                          | ✅ | Remote SMB user GID. |
| `SMB_FILE_MODE`                    | ⚠️ | File mode. <br> Default: `0770`. |
| `SMB_DIR_MODE`                     | ⚠️ | Directory mode. <br> Default: `0770`. |
| **Local directory** |
| `OWNMINE_LOCAL_HOME`               | ⚠️ | Local machine home folder for current user. <br> Default: `$HOME`. |
| `OWNMINE_LOCAL_USER`               | ⚠️ | Local machine username. Used to fix ownership when the option `pull` is used.  <br> Default: `$USER`. |
| `OWNMINE_LOCAL_SERVER`             | ⚠️ | Main folder where the server will run from. <br> Default: `ownmine`. |
| `OWNMINE_LOCAL_BACKUP`             | ⚠️ | Folder for local backups. Used by `sync` and `backup` options. <br> Default: `ownmine.bk`. |
| **Logging** |
| `OWNMINE_LOG_FOLDER`               | ⚠️ | Local folder where the logfiles are located. <br> Default: `/var/log`. |
| `OWNMINE_LOG_FILE`                 | ⚠️ | Local logging file. <br> Default: `ownmine.log`. |
| **RCON server** |
| `OWNMINE_RCON_BIN`                 | ❌ | Location of the `mcrcon` tool binary. Used to send commands to the RCON server. <br> Defined as `$OWNMINE_LOCAL_HOME/tools/mcrcon/mcrcon`. |
| `OWNMINE_RCON_IP`                  | ⚠️ | IP of the RCON server. <br> Default: `127.0.0.1`. |
| `OWNMINE_RCON_PORT`                | ⚠️ | Port used by the RCON server. <br> Default: `25575`. |
| `OWNMINE_RCON_PASS`                | ✅ | RCON server password. <br> Can be defined on setup. |
| **Remote SMB directory** |
| `OWNMINE_SAMBA_REMOTE`             | ❌ | Complete remote URL to the SMB directory. <br> Defined as `$OWNMINE_SAMBA_SERVER/$OWNMINE_SAMBA_SHARE/$OWNMINE_SAMBA_SUBDIR`. |
| **Reserved** |
| `OWNMINE_TEMP`                     | ❌ | Flag to indicate the usage of local temporary folders. <br> Defined as `{TMP}`. |
| `OWNMINE_SERVER_OPERATION_SUCCESS` | ❌ | Self-control flag for operations success. <br> Defined as `0`. |


Add your Discord bot token to the `ownminebot.py` file, namely on the variable `_TOKEN`.


## Usage

### ownMine Minecraft Server

**Call:** `ownmine [option]`
| Option | Description |
| --- | --- |
| `start`          | Starts the server. |
| `stop`           | Stops the server. |
| `startall`       | Starts both the server and the Discord bot. |
| `stopall`        | Stops both the server and the Discord bot. |
| `exit`           | Executes 'stop' and 'push' sequentially. |
| `status`         | Checks for the server daemon status. |
| `push`           | Pushes a main backup to the remote server. |
| `pull`           | Recovers from the main remote backup. Makes a local backup first. |
| `backup`         | Makes a local backup. |
| `sync`           | Syncs local backups with the remote server. |
| `debug <on/off>` | Turns Debug Mode on or off. It is off by default. |


### ownMine Discord Bot

**Call:** `ownminebot [option]`
| Option | Description |
| --- | --- |
| `start`  | Starts the bot service|
| `stop`   | Stops the bot service|
| `status` | Checks for the bot daemon status. |
