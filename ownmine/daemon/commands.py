import subprocess
import shutil
import os
import tempfile
import time
import functools
from datetime import datetime
from typing import Callable, Optional
from mcrcon import MCRcon

from common.response import Response
from common.procmgr import *
from common.log import OwnmineLog

import common.utils as utils


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
        from daemon.core import OwnmineDaemon
        self.daemon:          OwnmineDaemon  = daemon
        self.running_servers: dict[str, int] = {}

        # DEBUG: CommandHandler.commands
        # for cmd_name, (func, context) in CommandHandler.commands.items():
        #     self.daemon.log(OwnmineLog.MESSAGE, f"{context}::{cmd_name} @ {func}")


    def is_dryrun(self):
        return self.daemon.config.mode.is_dryrun()


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
                    if args[0] not in self.daemon.config.servers.keys():
                        return Response.failure(f'Server "{args[0]}" not configured')
                    return method(self, args[0], *args[1:])
                return Response.failure("Missing server name")

            if context == "general":
                return method(self, *args)

            return Response.failure(f"Invalid context for '{cmd}' (got '{context}'')")

        except Exception as e:
            return Response.failure(f"Got '{e}' while executing '{cmd}'")


    @cmd("list")
    def _list(self):
        """List all configured servers."""
        # Dry-run: this command does not have special behaviour
        self.daemon.log(OwnmineLog.MESSAGE, "CMD: list")
        server_list = ';'.join([server for server in self.daemon.config.servers.keys()])
        return Response.success(server_list if server_list != "" else "No servers configured")


    @cmd("sync")
    def _syncall(self):
        """Syncs all servers."""
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: sync (all servers)")

        err_srv    = []
        err_count  = 0
        ok_count   = 0
        dryrun_msg = []

        for server in self.daemon.config.servers.keys():
            r = self._sync(server)
            if r.is_failure():
                err_count += 1
                err_srv.append(server)
            else:
                ok_count += 1
                if self.is_dryrun():
                    dryrun_msg.append(r.message())

        if self.is_dryrun():
            return Response.success('\n'.join(dryrun_msg) + "\n(Dry-run) Sync All: end of operation.")

        if err_count > 0:
            return Response.failure(f"Sync All had {ok_count} successes and {err_count} failures (affected servers: { ', '.join(err_srv) })")
        return Response.success(f"Synced all server backups with remote archive successfully")


    @cmd("reload")
    def _reload_config(self):
        """Reloads configuration from disk. Use AYOR, this is usually not recommended."""
        # Dry-run: this command does not have special behaviour
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: reload")
        self.daemon.reload_config()
        return Response.success("Configuration reloaded successfully")


    @cmd_server("start")
    def _start(self, server_name: str):
        """Starts the server."""
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: start {server_name}")

        server_path = self.daemon.config.servers[server_name].path
        jar_path    = self.daemon.config.servers[server_name].jar
        total_path  = os.path.join(server_path, jar_path)

        cmd        = ["/usr/bin/java", "-Xmx4096M", "-Xms4096M", "-jar", str(total_path), "nogui"]
        jar_exists = os.path.exists(total_path)

        if self.is_dryrun():
            return Response.success(f"(Dry-run) Sync would execute command `{ ' '.join(cmd) }`. Server JAR { 'not ' if not jar_exists else '' }found.")

        if not jar_exists:
            return Response.failure(f"Server JAR not found at {total_path}")

        try:
            process = subprocess.Popen(
                cmd,
                cwd=server_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.running_servers[server_name] = process.pid
        except Exception as e:
            return Response.failure(f"Server start failed: {e}")

        return Response.success(f"Started server {server_name} with PID {self.running_servers[server_name]}")


    @cmd_server("stop")
    def _stop(self, server_name: str):
        """Stops the server."""
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: stop {server_name}")

        server_config = self.daemon.config.servers.get(server_name)
        if not server_config.rcon.enabled:
            if self.is_dryrun():
                return Response.success(f"(Dry-run) RCON is not enabled for server {server_name}")
            return Response.failure(f"RCON is not enabled for server {server_name}")

        ip       = server_config.rcon.ip if server_config.rcon.ip is not None else "127.0.0.1"
        port     = server_config.rcon.port
        password = server_config.rcon.password

        if self.is_dryrun():
            return Response.success(f"(Dry-run) Stop would send mcrcon command `stop` to server {ip}:{port} (password: <hidden>).")

        try:
            with MCRcon(ip, password, port=port) as mcr:
                resp = mcr.command("stop")
                self.daemon.log(OwnmineLog.MESSAGE, f"RCON response: {resp}")
        except Exception as e:
            return Response.failure(f"Failed to send RCON stop command: {e}")

        # Check if process is still running
        pid = self.running_servers.get(server_name)
        if pid:
            for _ in range(10):         # Wait up to ~10 seconds
                if not is_process_running(pid):
                    break               # Process is gone
                time.sleep(1.0)
            else:
                return Response.failure(f"Server is still running after stop command")

            self.running_servers.pop(server_name, None)
            return Response.success(f'Stopped server {server_name} with "{resp}"')

        else:
            return Response.success(f"RCON stop command sent to '{server_name}', no PID found for verification")


    @cmd_server("exit")
    def _exit(self, server_name: str):
        """Executes 'stop' and 'push' sequentially."""
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: exit {server_name}")

        response = self._stop(server_name)
        if response.is_failure():
            return Response.failure(f"Exit server failed at 'stop' with {response.message()}")
        if self.is_dryrun():
            dryrun_msg = [response.message()]

        response = self._push(server_name)
        if response.is_failure():
            return Response.failure(f"Exit server failed at 'stop' with {response.message()}")
        if self.is_dryrun():
            dryrun_msg.append(response.message())

        if self.is_dryrun():
            return Response.success('\n'.join(dryrun_msg) + "\n(Dry-run) Exit: end of operation.")

        return Response.success(f"Exited server {server_name}")


    @cmd_server("status")
    def _status(self, server_name: str):
        """Get the status of a specific server."""
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: status {server_name}")

        pid = self.running_servers.get(server_name)

        if self.is_dryrun():
            return Response.success(f"(Dry-run) PID for server {server_name}: {pid}.")

        if not pid:
            return Response.success(f"Server {server_name} is not running")

        status = get_process_status(pid)
        return Response.success(f"Server {server_name} is in status `{status}`")


    @cmd_server("exec")
    def _exec(self, server_name: str, *args):
        """Relays a command to be executed via the RCON server."""
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: exec {server_name}")

        server_config = self.daemon.config.servers.get(server_name)

        if not server_config.rcon.enabled:
            if self.is_dryrun():
                return Response.success(f"(Dry-run) RCON is not enabled for server {server_name}")
            return Response.failure(f"RCON is not enabled for server {server_name}")

        ip           = server_config.rcon.ip if server_config.rcon.ip is not None else "127.0.0.1"
        port         = server_config.rcon.port
        password     = server_config.rcon.password
        exec_command = ' '.join(args)

        if self.is_dryrun():
            return Response.success(f"(Dry-run) Exec would send mcrcon command `exec {exec_command}` to server {ip}:{port} (password: <hidden>).")

        try:
            with MCRcon(ip, password, port=port) as mcr:
                resp = mcr.command(f"exec {exec_command}")
                self.daemon.log(OwnmineLog.MESSAGE, f"RCON response: {resp}")
        except Exception as e:
            return Response.failure(f"Failed to send RCON exec command: {e}")

        return Response.success(f'Executed command on {server_name} with "{resp}"')


    @cmd_server("push")
    def _push(self, server_name: str):
        """Pushes a main backup to the remote server."""
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: push {server_name}")

        smb_config = self.daemon.config.servers[server_name].backup.smb

        if not smb_config.enabled:
            if self.is_dryrun():
                return Response.success(f"(Dry-run) Remote backups are not enabled for {server_name}")
            return Response.failure(f"Remote backups are not enabled for {server_name}")

        source = self.daemon.config.servers[server_name].path
        user   = self.daemon.config.servers[server_name].user

        # with tempfile.TemporaryDirectory() as tmp:
        with utils.mktemp(dry_run=self.is_dryrun()) as tmp:
            # 1. Mount remote share
            r = self._mount_remote_smb(
                mount_point = tmp,
                remote      = f'{smb_config.server}/{smb_config.share}',
                username    = smb_config.username,
                password    = smb_config.password,
                domain      = smb_config.domain,
                filemode    = smb_config.filemode,
                dirmode     = smb_config.dirmode,
                uid         = smb_config.uid,
                gid         = smb_config.gid
            )
            if r.is_failure():
                return Response.failure(f"Push failed to mount the remote share with {r.message()}")
            if self.is_dryrun():
                dryrun_msg = [r.message()]

            # 2. Sync with remote server
            r = self._dispatch_rsync(
                source      = source,
                destination = f'{tmp}/{smb_config.mirror}',
                chown       = f'{user}:{user}'
            )
            if r.is_failure():
                r2 = self._unmount_remote_smb(tmp)
                if r2.is_failure():
                    return Response.failure(f"Push failed at rsync with '{r.message()}', and could not unmount the remote share afterwards with {r2.message()}")
                return Response.failure(f"Push failed at rsync with '{r.message()}', but successfully unmounted the remote share")
            if self.is_dryrun():
                dryrun_msg.append(r.message())

            # 3. Unmount remote share
            r = self._unmount_remote_smb(tmp)
            if r.is_failure():
                return Response.failure(f"Push successfully ran rsync, but could not unmount the remote share afterwards with {r.message()}")
            if self.is_dryrun():
                dryrun_msg.append(r.message())

        if self.is_dryrun():
            return Response.success('\n'.join(dryrun_msg) + "\n(Dry-run) Push: end of operation.")

        return Response.success("Push completed successfully")


    @cmd_server("pull")
    def _pull(self, server_name: str):
        """Recovers from the main remote backup. Makes a local backup first."""
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: pull {server_name}")

        smb_config = self.daemon.config.servers[server_name].backup.smb

        if not smb_config.enabled:
            if self.is_dryrun():
                return Response.success(f"(Dry-run) Remote backups are not enabled for {server_name}")
            return Response.failure(f"Remote backups are not enabled for {server_name}")

        destination = self.daemon.config.servers[server_name].path
        # user        = self.daemon.config.servers[server_name].user

        # with tempfile.TemporaryDirectory() as tmp:
        with utils.mktemp(dry_run=self.is_dryrun()) as tmp:
            # 1. Mount remote share
            r = self._mount_remote_smb(
                mount_point = tmp,
                remote      = f'{smb_config.server}/{smb_config.share}',
                username    = smb_config.username,
                password    = smb_config.password,
                domain      = smb_config.domain,
                filemode    = smb_config.filemode,
                dirmode     = smb_config.dirmode,
                uid         = smb_config.uid,
                gid         = smb_config.gid
            )
            if r.is_failure():
                return Response.failure(f"Pull failed to mount the remote share with {r.message()}")
            if self.is_dryrun():
                dryrun_msg = [r.message()]

            # 2. Sync with remote server
            r = self._dispatch_rsync(
                source      = f'{tmp}/{smb_config.mirror}',
                destination = destination,
                # chown       = f'{user}:{user}'
            )
            if r.is_failure():
                r2 = self._unmount_remote_smb(tmp)
                if r2.is_failure():
                    return Response.failure(f"Pull failed at rsync with '{r.message()}', and could not unmount the remote share afterwards with {r2.message()}")
                return Response.failure(f"Pull failed at rsync with '{r.message()}', but successfully unmounted the remote share")
            if self.is_dryrun():
                dryrun_msg.append(r.message())

            # 3. Unmount remote share
            r = self._unmount_remote_smb(tmp)
            if r.is_failure():
                return Response.failure(f"Pull successfully ran rsync, but could not unmount the remote share afterwards with {r.message()}")
            if self.is_dryrun():
                dryrun_msg.append(r.message())

        if self.is_dryrun():
            return Response.success('\n'.join(dryrun_msg) + "\n(Dry-run) Pull: end of operation.")

        return Response.success("Pull completed successfully")


    @cmd_server("backup")
    def _backup(self, server_name: str):
        """Triggers a local backup for a specific server."""
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: backup {server_name}")

        server_config = self.daemon.config.servers.get(server_name)
        destination   = server_config.backup.local

        if not destination:
            if self.is_dryrun():
                return Response.success(f"(Dry-run) Backup for server '{server_name}' is not properly configured")
            return Response.failure(f"Backup for server '{server_name}' is not properly configured")

        return self._backup_local(server_name, source=server_config.path, destination=destination)


    @cmd_server("sync")
    def _sync(self, server_name: str):
        """Syncs local backups with the remote server."""
        self.daemon.log(OwnmineLog.MESSAGE, f"CMD: sync {server_name}")

        smb_config = self.daemon.config.servers[server_name].backup.smb

        if not smb_config.enabled:
            if self.is_dryrun():
                return Response.success(f"(Dry-run) Remote backups are not enabled for {server_name}")
            return Response.failure(f"Remote backups are not enabled for {server_name}")

        source = self.daemon.config.servers[server_name].backup.local
        user   = self.daemon.config.servers[server_name].user

        # with tempfile.TemporaryDirectory() as tmp:
        with utils.mktemp(dry_run=self.is_dryrun()) as tmp:
            # 1. Mount remote share
            r = self._mount_remote_smb(
                mount_point = tmp,
                remote      = f'{smb_config.server}/{smb_config.share}',
                username    = smb_config.username,
                password    = smb_config.password,
                domain      = smb_config.domain,
                filemode    = smb_config.filemode,
                dirmode     = smb_config.dirmode,
                uid         = smb_config.uid,
                gid         = smb_config.gid
            )
            if r.is_failure():
                return Response.failure(f"Pull failed to mount the remote share with {r.message()}")
            if self.is_dryrun():
                dryrun_msg = [r.message()]

            # 2. Sync with remote server
            r = self._dispatch_rsync(
                source      = source,
                destination = f'{tmp}/{smb_config.archive}',
                chown       = f'{user}:{user}'
            )
            if r.is_failure():
                r2 = self._unmount_remote_smb(tmp)
                if r2.is_failure():
                    return Response.failure(f"Pull failed at rsync with '{r.message()}', and could not unmount the remote share afterwards with {r2.message()}")
                return Response.failure(f"Pull failed at rsync with '{r.message()}', but successfully unmounted the remote share")
            if self.is_dryrun():
                dryrun_msg.append(r.message())

            # 3. Unmount remote share
            r = self._unmount_remote_smb(tmp)
            if r.is_failure():
                return Response.failure(f"Pull successfully ran rsync, but could not unmount the remote share afterwards with {r.message()}")
            if self.is_dryrun():
                dryrun_msg.append(r.message())

        if self.is_dryrun():
            return Response.success('\n'.join(dryrun_msg) + "\n(Dry-run) Sync: end of operation.")

        return Response.success("Pull completed successfully")


    def _dispatch_rsync(self,
                        source:      str,
                        destination: str,
                        syncmode:    str           = "-u",
                        chown:       Optional[str] = None,
                        delete:      bool          = False,
                        progress:    bool          = False) -> Response:
        """Syncs source to destination using rsync."""
        if not os.path.exists(source) and not self.is_dryrun():
            return Response.failure(f"Source path does not exist: {source}")

        cmd = [
            "rsync",
            "-artmEP",
            "--chmod=770",
            syncmode,
            source.rstrip("/") + "/",
            destination.rstrip("/") + "/"
        ]
        if chown is not None:
            cmd.insert(4, chown)
        if delete:
            cmd.insert(2, "--delete")
        if progress:
            cmd.insert(2, "--info=progress2")
        self.daemon.log(OwnmineLog.MESSAGE, f"• {cmd}")

        if self.is_dryrun():
            return Response.success(f"(Dry-run) _dispatch_rsync would run command `{ ' '.join(cmd) }`.")

        try:
            os.makedirs(destination, exist_ok=True)
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
            return Response.success(f"rsync completed successfully: '{result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            return Response.failure(f"rsync failed with code {e.returncode}: {e.stderr.strip()}")
        except Exception as e:
            return Response.failure(f"rsync failed: {e}")


    def _backup_local(self, server_name, source, destination):
        timestamp   = datetime.now().strftime('%Y%m%d%H%M%S')
        backup_path = os.path.join(destination, f"{server_name}_{timestamp}")

        if self.is_dryrun():
            return Response.success(f"(Dry-run) _backup_local would copy from '{source}' to '{backup_path}'.")

        try:
            shutil.copytree(source, backup_path)
        except FileExistsError:
            return Response.failure(f"Backup destination '{backup_path}' already exists.")
        except Exception as e:
            return Response.failure(f"Failed to create backup: {e}")

        return Response.success(f"Backup created at {backup_path}")


    def _mount_remote_smb(self,
                          mount_point,
                          remote,
                          username,
                          password,
                          domain,
                          filemode,
                          dirmode,
                          uid,
                          gid):
        options  = f"username={username},password={password if not self.is_dryrun() else '<hidden>' },domain={domain},vers=3.0,file_mode={filemode},dir_mode={dirmode}"
        if uid:
            options += f",uid={uid}"
        if gid:
            options += f",gid={gid}"

        cmd = ["mount", "-t", "cifs", remote, mount_point, "-o", options]

        if self.is_dryrun():
            return Response.success(f"(Dry-run) _mount_remote_smb would run command `{ ' '.join(cmd) }`.")

        try:
            os.makedirs(mount_point, exist_ok=True)
            subprocess.run(cmd, check=True)
            return Response.success("SMB share mounted")
        except subprocess.CalledProcessError as e:
            return Response.failure(f"Failed to mount SMB share: {e}")


    def _unmount_remote_smb(self, mount_point):
        cmd = ["umount", mount_point]

        if self.is_dryrun():
            return Response.success(f"(Dry-run) _unmount_remote_smb would run command `{ ' '.join(cmd) }`.")

        try:
            subprocess.run(cmd, check=True)
            return Response.success("SMB share unmounted")
        except subprocess.CalledProcessError as e:
            return Response.failure(f"Failed to unmount SMB share: {e}")



def load_commands():
    for attr_name in dir(CommandHandler):
        attr = getattr(CommandHandler, attr_name)
        if callable(attr) and hasattr(attr, "__command__"):
            cmd_name, func, context = getattr(attr, "__command__")
            CommandHandler.commands[cmd_name] = (func, context)


if __name__ != "__main__":
    load_commands()
