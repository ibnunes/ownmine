import typer
import socket
import sys
# from typing import Optional


app        = typer.Typer()
server_app = typer.Typer()

app.add_typer(server_app, name="server", help="Server-specific operations")


SOCKET_PATH = "/tmp/ownmine.sock"

def send_command(command: str) -> str:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(SOCKET_PATH)
        client.sendall(command.encode())
        response = client.recv(1024).decode()
    return response



# === Top-level global commands ===

@app.command("list")
def list():
    """List all configured servers."""
    response = send_command("list")
    typer.echo(response)


@app.command("reload")
def reload():
    """Reload servers configurations."""
    response = send_command("reload")
    typer.echo(response)



# === Server commands ===

@server_app.command("status")
def status(server_name: str):
    """Handles commands for servers."""
    response = send_command(f"status {server_name}")
    typer.echo(response)


@server_app.command("backup")
def backup(server_name: str):
    """Backup a server."""
    response = send_command(f"backup {server_name}")
    typer.echo(response)



if __name__ == "__main__":
    match len(sys.argv[1:]):
        case 0:
            sys.argv[1:] = ['--help']
        case l if l >= 2:
            # Support for syntax-sugar "ownmine server_name command [options]" instead of "ownmine server command [options] server_name"
            sys.argv[1:] = ['server'] + sys.argv[2:] + ([sys.argv[1]] if sys.argv[1] != 'server' else [])
    app()
