# ownMine
**Management scripts self-hosted Minecraft server**

TODO: write a proper README.

## Installation

```
zsh -c "$(curl -fsSL https://raw.githubusercontent.com/ibnunes/ownMine/master/setup.zsh)"
```

## Usage

**Call:** `mine [option]`
| Option | Description |
| --- | --- |
| `start         ` | Starts the server. |
| `stop          ` | Stops the server. |
| `startall      ` | Starts both the server and the Discord bot. |
| `stopall       ` | Stops both the server and the Discord bot. |
| `exit          ` | Executes 'stop' and 'push' sequentially. |
| `status        ` | Checks for the server daemon status. |
| `push          ` | Pushes a main backup to the remote server. |
| `pull          ` | Recovers from the main remote backup. Makes a local backup first. |
| `backup        ` | Makes a local backup. |
| `sync          ` | Syncs local backups with the remote server. |
| `debug <on/off>` | Turns Debug Mode on or off |


**Call:** `minebot [option]`
| Option | Description |
| --- | --- |
| `start ` | Starts the bot service|
| `stop  ` | Stops the bot service|
| `status` | Checks for the bot daemon status. |

## Configuration

TODO: this section
