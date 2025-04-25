import os
import socket
import threading
from typing import Optional
from dataclasses import dataclass

from common.config import OwnmineConfig
from common.socketcfg import SocketMessageFormat, DEFAULT_SOCKET_PATH
from daemon.commands import CommandHandler
from common.execmgr import ExecutionMode

from common.log import OwnmineLog


@dataclass
class OwnmineDaemonLogger:
    daemon: OwnmineLog
    server: dict[str, OwnmineLog]


class OwnmineDaemon:

    def __init__(self, config_path: Optional[str] = None):
        self.config:      OwnmineConfig       = OwnmineConfig(config_path)

        # Load loggers immediately and start logging as soon as possible
        self.logger:      OwnmineDaemonLogger = self.get_loggers()

        self.handler:     CommandHandler      = CommandHandler(daemon=self)
        self.running:     bool                = False
        self.socket_path: str                 = DEFAULT_SOCKET_PATH


    def reload_config(self, config_path: Optional[str] = None):
        self.config.set_path(new_path=config_path, do_reload=True)
        self.logger = self.get_loggers()


    def get_loggers(self):
        return OwnmineDaemonLogger(
            daemon = OwnmineLog(
                enable   = self.config.log.enabled,
                minlevel = OwnmineLog.type_const(self.config.log.level),
                filepath =
                    os.path.join(self.config.log.path, self.config.log.file)
                    if self.config.log.enabled and self.config.log.path is not None and self.config.log.file is not None
                    else None,
                execmode = self.config.mode
            ),
            server = {
                name: OwnmineLog(
                    enable   = cfg.log.enabled,
                    minlevel = OwnmineLog.type_const(cfg.log.level),
                    filepath =
                        os.path.join(cfg.log.path, cfg.log.file)
                        if cfg.log.enabled and cfg.log.path is not None and cfg.log.file is not None
                        else None,
                    execmode = self.config.mode     # Same as daemon
                ) for name, cfg in self.config.servers.items()
            }
        )


    def log(self, level: int, msg: str, server_name: str | None = None, skip_file: bool = False):
        if server_name is None and self.logger.daemon.log is not None:
            self.logger.daemon.log(level, msg, skip_file)
        logger = self.logger.server.get(server_name)
        if logger is not None:
            logger.log(level, msg, skip_file)


    def logs(self, level: int, msg: str, server_name: str | None = None, skip_file: bool = False):
        if server_name is None and self.logger.daemon.logs is not None:
            self.logger.daemon.logs(level, msg, skip_file)
        logger = self.logger.server.get(server_name)
        if logger is not None:
            logger.logs(level, msg, skip_file)


    def print(self, msg: str = "", server_name: str | None = None):
        self.logs(OwnmineLog.MESSAGE, msg, server_name, skip_file=True)


    def handle_client(self, conn):
        """Handle an incoming client request."""
        with conn:
            try:
                data = conn.recv(1024).decode().strip()
                self.print(f'Received "{data}"')
                result = self.handler.handle(data)
                response = SocketMessageFormat.encode_from_response(result)
            except Exception as e:
                response = SocketMessageFormat.encode_error(str(e))

            self.print(f'Sending "{response}"')
            conn.sendall(response.encode())


    def run(self):
        """Run the daemon to listen for client requests."""
        if self.running:
            return      # Already running

        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(self.socket_path)
            os.chmod(self.socket_path, 0o600)    # Set permissions to owner only
            server.listen()

            print(f"ownmine daemon running... (socket: {self.socket_path})\n")

            self.running = True
            while self.running:
                conn, _ = server.accept()
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()


    def stop(self):
        """Stop the daemon."""
        self.running = False
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
