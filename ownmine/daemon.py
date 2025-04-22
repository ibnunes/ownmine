from daemon.core import OwnMineDaemon

def main():
    daemon = OwnMineDaemon()

    # DEBUG: Loaded configuration
    for name, server in daemon.config.servers.items():
        print(f"- {name}")
        print(f"  Path: {server.path}")
        print(f"  Port: {server.port}")
        print(f"  RCON Enabled: {server.rcon.enabled}")
        print(f"  Local Backup Path: {server.backup.local}")
        if server.backup.smb.enabled:
            print(f"  SMB Path: {server.backup.smb.path}")
            print(f"  SMB User: {server.backup.smb.username}")

    try:
        daemon.run()
    except KeyboardInterrupt:
        print("Shutting down...")
        daemon.stop()


if __name__ == "__main__":
    main()
