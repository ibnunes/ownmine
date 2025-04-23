import os
import socket
import threading
from typing import Optional

from common.config import load_config
from common.response import Response
from common.socketmsgfmt import SocketMessageFormat
from daemon.commands import CommandHandler


SOCKET_PATH = "/tmp/ownmine.sock"

class OwnMineDaemon:

    def __init__(self, config_path: Optional[str] = None):
        self.config  = load_config(config_path)
        self.handler = CommandHandler(daemon=self)
        self.running = True


    def reload_config(self, config_path: Optional[str] = None):
        self.config = load_config(config_path)


    def handle_client(self, conn):
        """Handle an incoming client request."""
        with conn:
            try:
                data = conn.recv(1024).decode().strip()
                print(f'Received "{data}"')
                response = SocketMessageFormat.enconde_from_response(self.handler.handle(data))
                print(f'Sending "{response}"')
                conn.sendall(response.encode())
            except Exception as e:
                response = SocketMessageFormat.enconde_error(str(e))
                print(f'Sending "{response}"')
                conn.sendall(response.encode())


    def run(self):
        """Run the daemon to listen for client requests."""
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(SOCKET_PATH)
            os.chmod(SOCKET_PATH, 0o600)    # Set permissions to owner only
            server.listen()

            print(f"OwnMine daemon running... (socket: {SOCKET_PATH})")

            while self.running:
                conn, _ = server.accept()
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()


    def stop(self):
        """Stop the daemon."""
        self.running = False
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
