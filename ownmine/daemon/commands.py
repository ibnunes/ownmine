import subprocess
# import psutil
import shutil
import os
import functools
from datetime import datetime
from typing import Callable

from common.response import Response


class CommandHandler:

    commands: dict[str, tuple[Callable, str]] = {}

    def cmd(name: str = None):
        def decorator(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)
            wrapped.__command__ = (name or func.__name__, func, "general")
            return wrapped
        return decorator

    def cmd_server(name: str = None):
        def decorator(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)
            wrapped.__command__ = (name or func.__name__, func, "server")
            return wrapped
        return decorator


    def __init__(self, daemon):
        from daemon.core import OwnMineDaemon
        self.daemon: OwnMineDaemon = daemon
        # DEBUG: CommandHandler.commands
        # for cmd_name, (func, context) in CommandHandler.commands.items():
        #     print(f"{context}::{cmd_name} @ {func}")


    def handle(self, command: str) -> str:
        parts = command.strip().split()
        if not parts:
            return Response.failure("Empty command")

        cmd, *args = parts
        entry = CommandHandler.commands.get(cmd)

        if not entry:
            return Response.failure(f"Unknown command '{cmd}'")

        method, context = entry

        try:
            if context == "server":
                if args:
                    return method(self, args[0], *args[1:])
                return Response.failure("Missing server name")

            if context == "general":
                return method(self, *args)

            return Response.failure(f"Invalid context for '{cmd}'")

        except Exception as e:
            return Response.failure(f"Got '{e}' while executing '{cmd}'")


    @cmd("list")
    def _list(self):
        """List all configured servers."""
        print("CMD: list")
        server_list = '\n'.join([server for server in self.daemon.config.servers.keys()])
        return Response.success(server_list if server_list != "" else "No servers configured")


    @cmd("sync")
    def _syncall(self):
        """Syncs all servers."""
        print(f"CMD: sync (all servers)")
        # TODO: Sync all servers backups
        return Response.success(f"CMD: sync (all servers)")


    @cmd("reload")
    def _reload_config(self):
        print(f"CMD: reload")
        self.daemon.reload_config()
        return Response.success("Configuration reloaded successfully.")


    @cmd_server("start")
    def _start(self, server_name: str):
        """Starts the server."""
        print(f"CMD: start {server_name}")
        # TODO: Start server
        return Response.success(f"CMD: start {server_name}")


    @cmd_server("stop")
    def _stop(self, server_name: str):
        """Stops the server."""
        print(f"CMD: stop {server_name}")
        # TODO: Stop server
        return Response.success(f"CMD: stop {server_name}")


    @cmd_server("exit")
    def _exit(self, server_name: str):
        """Executes 'stop' and 'push' sequentially."""
        print(f"CMD: exit {server_name}")
        # TODO: Exit server
        return Response.success(f"CMD: exit {server_name}")


    @cmd_server("status")
    def _status(self, server_name: str):
        """Get the status of a specific server."""
        print(f"CMD: status {server_name}")

        server_config = next((server for server in self.daemon.config.servers.keys() if server == server_name), None)
        if not server_config:
            return Response.failure(f"Server '{server_name}' not found.")

        # TODO: Get server status from systemd
        return Response.success(f"CMD: status {server_name}")

        # process_name = server_config['name']  # Assuming the server name is used for the process
        # for proc in psutil.process_iter(['pid', 'name']):
        #     if process_name in proc.info['name']:
        #         return f"Server '{server_name}' is running (PID: {proc.info['pid']})."
        # return f"Server '{server_name}' is not running."


    @cmd_server("exec")
    def _exec(self, server_name: str):
        """Relays a command to be executed via the RCON server."""
        print(f"CMD: exec {server_name}")
        # TODO: Execute command in server
        return Response.success(f"CMD: exec {server_name}")


    @cmd_server("push")
    def _push(self, server_name: str):
        """Pushes a main backup to the remote server."""
        print(f"CMD: push {server_name}")
        # TODO: Push server backup
        return Response.success(f"CMD: push {server_name}")


    @cmd_server("pull")
    def _pull(self, server_name: str):
        """Recovers from the main remote backup. Makes a local backup first."""
        print(f"CMD: pull {server_name}")
        # TODO: Pull server backup
        return Response.success(f"CMD: pull {server_name}")


    @cmd_server("backup")
    def _backup(self, server_name: str):
        """Trigger a backup for a specific server."""
        print(f"CMD: backup {server_name}")

        server_config = next((server for server in self.daemon.config['servers'] if server['name'] == server_name), None)
        if not server_config:
            return Response.failure(f"Server '{server_name}' not found.")

        # Handle the backup
        backup = self._get_backup_config(server_config)

        if not backup:
            return Response.failure(f"Backup for server '{server_name}' is not properly configured.")

        backup_results = []
        command = ""

        # TODO: Perform local backup if configured
        if backup.get('local'):
            local_backup_path = backup['local']
            source_dir = server_config['path']
            command = f"rsync -av --delete {source_dir} {local_backup_path}"
            # backup_results.append(self._run_backup_command(command, server_name))

        # TODO: Perform SMB backup if enabled
        if backup.get('smb', {}).get('enabled', False):
            smb_backup_config = backup['smb']
            smb_share = smb_backup_config['path']
            username = smb_backup_config['username']
            password = smb_backup_config['password']
            command = f"smbclient {smb_share} -U {username}%{password} -c 'put {server_config['path']} {local_backup_path}'"
            # backup_results.append(self._run_backup_command(command, server_name))

        return Response.success(command if command != "" else f"CMD: backup {server_name}")
        # return "\n".join(backup_results)


    @cmd_server("sync")
    def _sync(self, server_name: str):
        """Syncs local backups with the remote server."""
        print(f"CMD: sync {server_name}")
        # TODO: Sync server backups
        return Response.success(f"CMD: sync {server_name}")


    def _get_backup_config(self, server_config):
        """Helper method to get the backup configuration."""
        # TODO: properly retrieve backup configuration for server
        return Response.success(str(server_config.get('backup', {})))


    def _run_backup_command(self, command, server_name):
        """Helper method to execute the backup command and handle errors."""
        try:
            subprocess.run(command, shell=True, check=True)
            return Response.success(f"Backup for '{server_name}' completed successfully.")
        except subprocess.CalledProcessError as e:
            return Response.failure(f"Error: Backup for '{server_name}' failed: {e}")


    def _backup_local(self, server_name, source, destination):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        backup_path = os.path.join(destination, f"{server_name}_{timestamp}")
        shutil.copytree(source, backup_path)



def load_commands():
    for attr_name in dir(CommandHandler):
        attr = getattr(CommandHandler, attr_name)
        if callable(attr) and hasattr(attr, "__command__"):
            cmd_name, func, context = getattr(attr, "__command__")
            CommandHandler.commands[cmd_name] = (func, context)


if __name__ != "__main__":
    load_commands()
