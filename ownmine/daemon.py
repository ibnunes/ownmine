import os
from daemon.core import OwnmineDaemon
from common.log import OwnmineLog

def main():
    daemon = OwnmineDaemon()

    # DEBUG: Loaded configuration
    # if OwnmineLog.type_const(daemon.config.log.level) <= OwnmineLog.DEBUG or daemon.config.mode.is_debug():
    if daemon.config.log.enabled:
        daemon.print(f"Daemon logger: Enabled ({ os.path.join(daemon.config.log.path, daemon.config.log.file) })")
    else:
        daemon.print("Daemon logger: Disabled")

    for name, server in daemon.config.servers.items():
        daemon.print(f"- {name}")
        daemon.print(f"  Path:               {server.path}")
        daemon.print(f"  Port:               {server.port}")
        if server.rcon.enabled:
            daemon.print("  RCON client:        Enabled")
            daemon.print(f"    IP:               {server.rcon.ip}")
            daemon.print(f"    Port:             {server.rcon.port}")
        else:
            daemon.print("  RCON client:        Disabled")
        daemon.print(f"  Local Backup Path:  {server.backup.local}")
        if server.backup.smb.enabled:
            daemon.print("  SMB Remote Backups: Enabled")
            daemon.print(f"    Server:           {server.backup.smb.server}")
            daemon.print(f"    Share:            {server.backup.smb.share}")
            daemon.print(f"    Mirror:           {server.backup.smb.mirror}")
            daemon.print(f"    Archive:          {server.backup.smb.archive}")
            daemon.print(f"    User:             {server.backup.smb.username}")
        else:
            daemon.print("  SMB Remote Backups: Disabled")
        if server.log.enabled:
            daemon.print(f"  Logger:             Enabled ({
                    os.path.join(server.log.path, server.log.file)
                    if server.log.path is not None and server.log.file is not None
                    else 'no file configured'
                })")
        else:
            daemon.print("  Logger:             Disabled")
    daemon.print()

    try:
        daemon.run()
    except KeyboardInterrupt:
        daemon.print("\nShutting down...")
        daemon.stop()
    except Exception as e:
        daemon.print(f"\nFATAL: {e}")


if __name__ == "__main__":
    main()
