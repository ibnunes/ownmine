import socket
import sys
from typing import List, Optional

from common.response import Response
from common.socketmsgfmt import SocketMessageFormat


class OwnmineClient:
    class Command:
        _general:    List[str] = ['list', 'reload', 'sync']
        _for_server: List[str] = ['start', 'stop', 'exit', 'status', 'exec', 'push', 'pull', 'backup', 'sync']
        _help:       List[str] = ['--help', '-h', 'help']

        @staticmethod
        def is_general(cmd: str) -> bool:
            return cmd in OwnmineClient.Command._general

        @staticmethod
        def is_for_server(cmd: str) -> bool:
            return cmd in OwnmineClient.Command._for_server

        @staticmethod
        def is_help(cmd: str) -> bool:
            return cmd in OwnmineClient.Command._help


    SOCKET_PATH = "/tmp/ownmine.sock"

    @staticmethod
    def _send_command(command: str) -> str:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(OwnmineClient.SOCKET_PATH)
            client.sendall(command.encode())
            response = client.recv(1024).decode()
        return response


    @staticmethod
    def _exec_command(cmd: str, options: Optional[List[str]] = None, server: Optional[str] = None):
        print(f"• Command: {cmd}\n• Options: {str(options)}\n•  Server: {server}")
        command = cmd
        if options is not None:
            command += f" {' '.join(options)}"
        if server is not None:
            command += f" {server}"
        print(f'   TX > "{command}"')
        result = OwnmineClient._send_command(command)
        print(f'   RX < "{result}"')
        return SocketMessageFormat.decode_as_response(result)
        # if result.startswith("Error: "):
        #     return Response.failure(result[6:])
        # return Response.success()


    @staticmethod
    def help():
        print("ownmine 2.0 help")
        return Response.success()


    @staticmethod
    def run(exe_path: str, args: List[str]):
        print(f"Path: {exe_path}\nArgs: {str(args)}")

        args_len = len(args)

        # No arguments provided: help
        if args_len == 0:
            OwnmineClient.help()
            return Response.success()

        # 1 argument: either help or a general command
        if args_len == 1:
            command = args[0]
            if OwnmineClient.Command.is_help(command):
                OwnmineClient.help()
                return Response.success()
            if not OwnmineClient.Command.is_general(command):
                return Response.failure(f'`{command}` is not a recognized general command.')
            return OwnmineClient._exec_command(command)

        # 2+ arguments: it has to be a server command
        server  = args[0]
        command = args[1]
        options = args[2:]

        if not OwnmineClient.Command.is_for_server(command):
            return Response.failure(f'`{command}` is not a recognized server command.')
        return OwnmineClient._exec_command(command, options, server)



if __name__ == "__main__":
    ret = OwnmineClient.run(sys.argv[0], sys.argv[1:])
    print(ret)
    exit(ret.errno())
