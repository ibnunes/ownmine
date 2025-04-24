import os
import json
from dataclasses import dataclass
from typing import Optional

from common.secret import OwnmineSecret
from common.response import Response


DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'servers.json')


from dataclasses import dataclass, asdict
from typing import Optional, Dict

@dataclass
class SMBBackupConfig:
    enabled:  bool
    path:     Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

@dataclass
class BackupConfig:
    local: Optional[str]             = None
    smb:   Optional[SMBBackupConfig] = None

@dataclass
class RCONConfig:
    enabled:  bool
    ip:       Optional[str] = None
    port:     Optional[int] = None
    password: Optional[str] = None

@dataclass
class ServerConfig:
    path:   str
    jar:    str
    port:   int
    rcon:   RCONConfig
    backup: BackupConfig



class OwnmineConfig:
    def __init__(self, path: Optional[str] = None, secretmgr: Optional[OwnmineSecret] = None):
        self.path      = path if path else DEFAULT_CONFIG_PATH
        self.secretmgr = secretmgr if secretmgr else OwnmineSecret()
        self.servers   = {}
        self.load()


    def __del__(self):
        # TODO: Safeguard if config is somehow lost
        try:
            self.save()
        except Exception as e:
            print(f"Error saving config on destruction: {e}")


    def load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.servers = {
            name: OwnmineConfig.server_from_dict(cfg, self.secretmgr)
            for name, cfg in raw.items()
        }


    def set_path(self, new_path: str, do_reload: bool = False):
        self.path = new_path
        if do_reload:
            self.load()


    def save(self):
        raw = {
            name: OwnmineConfig.server_to_dict(cfg, self.secretmgr)
            for name, cfg in self.servers.items()
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=4)


    @staticmethod
    def server_from_dict(data: dict, secretmgr: OwnmineSecret) -> ServerConfig:
        rcon = data.get("rcon", {})
        if rcon.get("password") is not None:
            if secretmgr.is_encrypted(rcon["password"]):
                rcon["password"] = secretmgr.decrypt(rcon["password"])

        # Pre-fill IP with localhost if not provided
        if rcon.get("ip") is None:
            rcon["ip"] = "127.0.0.1"

        smb = data.get("backup", {}).get("smb", {})
        if smb.get("enabled", False) and smb.get("password") is not None:
            if secretmgr.is_encrypted(smb.get("password")):
                smb["password"] = secretmgr.decrypt(smb["password"])

        return ServerConfig(
            path=data["path"],
            jar=data["jar"],
            port=data["port"],
            rcon=RCONConfig(**rcon),
            backup=BackupConfig(
                local=data["backup"].get("local"),
                smb=SMBBackupConfig(**smb) if smb else None
            )
        )


    @staticmethod
    def server_to_dict(server: ServerConfig, secretmgr: OwnmineSecret) -> dict:
        data = asdict(server)

        if server.rcon.password and not secretmgr.is_encrypted(server.rcon.password):
            data["rcon"]["password"] = secretmgr.encrypt(server.rcon.password)

        if server.backup.smb and server.backup.smb.password and not secretmgr.is_encrypted(server.backup.smb.password):
            data["backup"]["smb"]["password"] = secretmgr.encrypt(server.backup.smb.password)

        return data
