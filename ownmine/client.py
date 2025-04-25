import socket
import sys
from typing import List, Optional

from common.response import Response
from common.socketcfg import SocketMessageFormat, DEFAULT_SOCKET_PATH

from dataclasses import dataclass
class Font:
    from common.escape import Ansi
    font    = Ansi.escape
    reset   = font('reset')
    command = font('bg', 238)
    title   = font('bold', 'fg_cyan')
    section = font('bold', 'underline')
    emph    = font('italic')
    emphoff = font('italic_off')
    text    = font('fg', 249)
    error   = font('fg_red')
    success = font('fg_green')
    faded   = font('fg', 238)


@dataclass

class OwnmineClient:
    class Command:
        _general:    List[str] = ['list', 'reload', 'sync']
        _for_server: List[str] = ['start', 'stop', 'exit', 'status', 'exec', 'push', 'pull', 'backup', 'sync']
        _help:       List[str] = ['--help', '-h', 'help']
        _debug:      List[str] = ['--debug', '-d']

        @staticmethod
        def is_general(cmd: str) -> bool:
            return cmd in OwnmineClient.Command._general

        @staticmethod
        def is_for_server(cmd: str) -> bool:
            return cmd in OwnmineClient.Command._for_server

        @staticmethod
        def is_help(cmd: str) -> bool:
            return cmd in OwnmineClient.Command._help

        @staticmethod
        def is_debug(cmd: str) -> bool:
            return cmd in OwnmineClient.Command._debug


    @staticmethod
    def _send_command(command: str) -> str:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(DEFAULT_SOCKET_PATH)
                client.sendall(command.encode())
                response = client.recv(1024).decode()
            return response
        except FileNotFoundError:
            return SocketMessageFormat.encode_error("The ownmine daemon does not seem to be running.")
        except Exception as e:
            return SocketMessageFormat.encode_error(f"Command execution failed: {e}")


    @staticmethod
    def _exec_command(cmd: str, options: Optional[List[str]] = None, server: Optional[str] = None, isdbg: bool = False):
        _print = lambda msg: print(msg) if isdbg else lambda msg: None

        _print(f"• Command: {cmd}\n• Options: {str(options)}\n•  Server: {server}")

        command = cmd
        if server is not None:
            command += f" {server}"
        if options is not None:
            command += f" {' '.join(options)}"
        _print(f'   TX > "{command}"')

        result = OwnmineClient._send_command(command)
        _print(f'   RX < "{result}"')

        return SocketMessageFormat.decode_as_response(result)


    @staticmethod
    def help():
        print(
f"""
           {Font.title}ownmine - Self-hosted Minecraft Servers Management Toolkit{Font.reset}
   ──────────────────────────────────────────────────────────────────────────
   {Font.section}Usage{Font.reset}:             {Font.command} ownmine [--debug | -d] [{Font.emph}server{Font.emphoff}] command [options] {Font.reset}

   There are 2 types of commands:
      • {Font.emph}General{Font.emphoff} - {Font.text}Applies to ownmine itself, or to all servers{Font.reset}
      • {Font.emph}Server{Font.emphoff}  - {Font.text}Applies to a single server identified by name with{Font.reset} {Font.command}{Font.emph} server {Font.reset}

   {Font.section}General commands{Font.reset}:
     {Font.command} list {Font.reset}          {Font.text}Retrieves list of configured servers on daemon.{Font.reset}
     {Font.command} sync {Font.reset}          {Font.text}Runs {Font.reset}{Font.command} sync {Font.reset}{Font.text} for all configured servers.{Font.reset}
     {Font.command} reload {Font.reset}        {Font.text}Reloads daemon configuration from disk.{Font.reset}
                        └── {Font.text}{Font.emph}Not recommended, do it AYOR!{Font.reset}

      • {Font.emph}Example{Font.reset}: {Font.command} ownmine list {Font.reset}

   {Font.section}Server commands{Font.reset}:
     {Font.command} status {Font.reset}        {Font.text}Checks for the server status.{Font.reset}
     {Font.command} start {Font.reset}         {Font.text}Starts the server.{Font.reset}
     {Font.command} stop {Font.reset}          {Font.text}Stops the server.{Font.reset}
     {Font.command} exit {Font.reset}          {Font.text}Executes 'stop' and 'push' sequentially.{Font.reset}
     {Font.command} push {Font.reset}          {Font.text}Pushes a mirror to the remote server.{Font.reset}
     {Font.command} pull {Font.reset}          {Font.text}Recovers from the remote mirror. Makes a local backup first.{Font.reset}
     {Font.command} backup {Font.reset}        {Font.text}Makes a local backup.{Font.reset}
     {Font.command} sync {Font.reset}          {Font.text}Syncs local backups with the remote server's archive.{Font.reset}
     {Font.command} exec {Font.emph}cmd{Font.emphoff} {Font.reset}      {Font.text}Executes a Minecraft command {Font.reset}{Font.command}{Font.emph} cmd {Font.reset}{Font.text} on server.{Font.reset}

      • {Font.emph}Example{Font.reset}: {Font.command} ownmine {Font.emph}survival{Font.emphoff} push {Font.reset}
                        └── {Font.text}Where {Font.command}{Font.emph} survival {Font.reset}{Font.text} is the name of the server{Font.reset}

   {Font.section}Flags{Font.reset}:
     {Font.command} --debug | -d {Font.reset}        {Font.text}Outputs debug information (only applies to the client).{Font.reset}
                              └── {Font.text}{Font.emph}Must be first argument.{Font.reset}
     {Font.command} --help | -h | help {Font.reset}  {Font.text}Shows this help. Same as no arguments provided.{Font.reset}
                              └── {Font.text}{Font.emph}Must be only argument.{Font.reset}
"""
        )
        return Response.success("§help§")


    @staticmethod
    def _parse_debug(args: List[str]) -> tuple[bool, List[str]]:
        if len(args) == 0:
            return (False, args)
        if OwnmineClient.Command.is_debug(args[0]):
            return (True, args[1:])
        return (False, args)


    @staticmethod
    def run(exe_path: str, args: List[str]):
        dbg, args = OwnmineClient._parse_debug(args)

        if dbg:
            print(f"Path: {exe_path}\nArgs: {str(args)}")

        match len(args):
            # No arguments provided: help
            case 0:
                return OwnmineClient.help()

            # 1 argument: either help or a general command
            case 1:
                command = args[0]
                if OwnmineClient.Command.is_help(command):
                    return OwnmineClient.help()
                if not OwnmineClient.Command.is_general(command):
                    return Response.failure(f'`{command}` is not a recognized general command.')
                return OwnmineClient._exec_command(command, isdbg=dbg)

        # 2+ arguments: server command
        server  = args[0]
        command = args[1]
        options = args[2:]

        if not OwnmineClient.Command.is_for_server(command):
            return Response.failure(f'`{command}` is not a recognized server command.')
        return OwnmineClient._exec_command(command, options, server, isdbg=dbg)


def _format_dryrun(s: str):
    return s.replace("(Dry-run)", f"{Font.faded}{Font.emph}(Dry-run){Font.reset}")

# Somewhat convuluted code, but didn't have the patience for better when I wrote it tbh
def print_response(result: Response):
    if result.is_failure():
        if result.message() is None:
            print(f"{Font.error}Error{Font.reset}")
        else:
            print(f"{Font.error}Error:{Font.reset} {_format_dryrun(result.message())}")
    else:
        if result.message() is None:
            print(f"{Font.success}Success{Font.reset}")
        elif result.message() != "§help§":
            print(f"{Font.success}Success:{Font.reset}\n{_format_dryrun(result.message())}")


if __name__ == "__main__":
    ret = OwnmineClient.run(sys.argv[0], sys.argv[1:])
    print_response(ret)
    exit(ret.errno())
