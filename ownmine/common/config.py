import os
import json
import getpass
from dataclasses import dataclass, asdict
from typing import Optional

from common.secret import OwnmineSecret
from common.response import Response
from common.execmgr import ExecutionMode


DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'servers.json')


@dataclass
class SMBBackupConfig:
    enabled:  bool
    server:   Optional[str] = None
    share:    Optional[str] = None
    mirror:   Optional[str] = None
    archive:  Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    domain:   str           = "WORKGROUP"
    gid:      Optional[str] = None
    uid:      Optional[str] = None
    filemode: str           = "0770"
    dirmode:  str           = "0770"

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
class LogConfig:
    enabled: bool
    path:    Optional[str] = None
    file:    Optional[str] = None
    level:   Optional[str] = None

@dataclass
class ServerConfig:
    path:   str
    jar:    str
    port:   int
    rcon:   RCONConfig
    log:    LogConfig
    backup: BackupConfig
    user:   Optional[str] = None



class OwnmineConfig:
    def __init__(self, path: Optional[str] = None, secretmgr: Optional[OwnmineSecret] = None):
        self.path:      str                     = path if path else DEFAULT_CONFIG_PATH
        self.secretmgr: OwnmineSecret           = secretmgr if secretmgr else OwnmineSecret()
        self.servers:   dict[str, ServerConfig] = {}
        self.log:       LogConfig               = None
        self.mode:      ExecutionMode           = None
        self._original_raw                      = None
        self.load()


    def __del__(self):
        # TODO: Better safeguard if config is somehow lost
        if self.servers == {}:
            print("No configuration in memory on destruction: skipping")
            return
        try:
            self.save()
        except Exception as e:
            print(f"Error saving config on destruction: {e}")
            if self._original_raw is not None:
                print("Saving original raw file...")
                with open(self.path, "w", encoding="utf-8") as f:
                    json.dump(self._original_raw, f, indent=4)
            else:   # We should NEVER hit this
                print("PANIC! No raw backup available! Your configuration may have been lost!")


    def load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            f.seek(0, os.SEEK_SET)
            self._original_raw = json.load(f)   # Loaded as an independent object, `= raw` will just point to a reference of `raw`
        self.servers = {
            name: OwnmineConfig.server_from_dict(cfg, self.secretmgr)
            for name, cfg in raw.get("servers", {}).items()
        }
        self.log  = LogConfig(**raw.get("log", {}))
        self.mode = ExecutionMode(raw.get("mode", 0))


    def save(self):
        raw = {
            "mode": self.mode.flag,
            "log": asdict(self.log),
            "servers": {
                name: OwnmineConfig.server_to_dict(cfg, self.secretmgr)
                for name, cfg in self.servers.items()
            }
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(raw, f, indent=4)


    def set_path(self, new_path: str, do_reload: bool = False):
        self.path = new_path
        if do_reload:
            self.load()


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

        user = data["user"]
        if user is None:
            user = getpass.getuser()

        return ServerConfig(
            path   = data["path"],
            jar    = data["jar"],
            port   = data["port"],
            user   = user,
            log    = LogConfig(**data.get("log", {})),
            rcon   = RCONConfig(**rcon),
            backup = BackupConfig(
                local = data["backup"].get("local"),
                smb   = SMBBackupConfig(**smb) if smb else None
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
