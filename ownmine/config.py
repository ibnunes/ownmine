import tomllib
from dataclasses import dataclass, field
from typing import Optional #, List
import os

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'servers.toml')

@dataclass
class SMBBackupConfig:
    enabled:  bool
    path:     Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

@dataclass
class BackupConfig:
    local: str
    smb:   SMBBackupConfig = field(default_factory=SMBBackupConfig)

@dataclass
class RCONConfig:
    enabled:  bool
    port:     Optional[int] = None
    password: Optional[str] = None

@dataclass
class ServerConfig:
    # name:   str
    path:   str
    port:   int
    rcon:   RCONConfig
    backup: BackupConfig

@dataclass
class OwnMineConfig:
    servers: dict[str, ServerConfig]    # List[ServerConfig]


def load_config(path: Optional[str] = None) -> OwnMineConfig:
    if (path is None):
        path = DEFAULT_CONFIG_PATH

    with open(path, 'rb') as f:
        raw_config = tomllib.load(f)

    if 'servers' not in raw_config:
        raise ValueError("No 'servers' section found in TOML config")

    # servers = []
    servers = {}
    for entry in raw_config['servers']:
        rcon_data = entry.get('rcon', {})
        backup_data = entry.get('backup', {})

        smb_data = backup_data.get('smb', {})
        smb = SMBBackupConfig(
            enabled=smb_data.get('enabled', False),
            path=smb_data.get('path'),
            username=smb_data.get('username'),
            password=smb_data.get('password'),
        )

        rcon = RCONConfig(
            enabled=rcon_data.get('enabled', False),
            port=rcon_data.get('port'),
            password=rcon_data.get('password'),
        )

        backup = BackupConfig(
            local=backup_data['local'],
            smb=smb,
        )

        server = ServerConfig(
            # name=entry['name'],
            path=entry['path'],
            port=entry['port'],
            rcon=rcon,
            backup=backup,
        )

        # servers.append(server)
        servers[entry['name']] = server

    return OwnMineConfig(servers=servers)
