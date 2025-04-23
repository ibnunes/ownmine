import os
import socket
import threading
from typing import Optional

from common.config import OwnmineConfig
from common.socketcfg import SocketMessageFormat, DEFAULT_SOCKET_PATH
from daemon.commands import CommandHandler


class OwnMineDaemon:

    def __init__(self, config_path: Optional[str] = None):
        self.config      = OwnmineConfig(config_path)
        self.handler     = CommandHandler(daemon=self)
        self.running     = True
        self.socket_path = DEFAULT_SOCKET_PATH


    def reload_config(self, config_path: Optional[str] = None):
        self.config.set_path(new_path=config_path, do_reload=True)


    def handle_client(self, conn):
        """Handle an incoming client request."""
        with conn:
            try:
                data = conn.recv(1024).decode().strip()
                print(f'Received "{data}"')
                result = self.handler.handle(data)
                response = SocketMessageFormat.encode_from_response(result)
            except Exception as e:
                response = SocketMessageFormat.encode_error(str(e))

            print(f'Sending "{response}"')
            conn.sendall(response.encode())


    def run(self):
        """Run the daemon to listen for client requests."""
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(self.socket_path)
            os.chmod(self.socket_path, 0o600)    # Set permissions to owner only
            server.listen()

            print(f"OwnMine daemon running... (socket: {self.socket_path})")

            while self.running:
                conn, _ = server.accept()
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()


    def stop(self):
        """Stop the daemon."""
        self.running = False
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
