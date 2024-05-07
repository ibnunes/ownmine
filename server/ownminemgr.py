import os
import functools

PLACEHOLDER_SERVER_NAME = "$\{SRV\}"


class OwnmineSettings:
    def __init__(self, cfg : dict):
        self.group   = cfg['group']
        self.rconbin = cfg['rcon']['dir'] + os.sep + cfg['rcon']['bin']
        self.logfile = cfg['log']['dir'] + os.sep + cfg['log']['file']



class OwnmineDirectory:
    def __init__(self, cfg : dict):
        self.enabled    = cfg['enabled']
        self.dir        = cfg['dir']
        self.exclusions = cfg['exclusions']

    def withName(self, name : str):
        self.dir = self.dir.replace(PLACEHOLDER_SERVER_NAME, name)
        return self

    def copy_from(self, pathfrom : str):
        if self.enabled:
            pass

    def copy_to(self, pathto : str):
        if self.enabled:
            pass



class OwnmineRcon:
    def __init__(self, cfg : dict, binpath : str = "mcrcon"):
        self.bin      = binpath
        self.ip       = cfg['ip']
        self.port     = cfg['port']
        self.password = cfg['password']

    def exec(self, cmd : str):
        pass



class OwnmineLog:
    def __init__(self, logpath : str, servername : str):
        self.logpath = logpath.replace(PLACEHOLDER_SERVER_NAME, servername)

    def log(self, msg : str):
        pass



class OwnmineServer:
    def ifenabled(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.enabled:
                return func(self, *args, **kwargs)
        return wrapper

    def __init__(self, name : str, cfg : dict):
        self.name    = name
        self.enabled = cfg['enabled']
        self.user    = cfg['user']
        self.dir     = cfg['dir'].replace(PLACEHOLDER_SERVER_NAME, name)
        self.jar     = cfg['jar']
        self.backup  = OwnmineDirectory(cfg['backup']).withName(name)
        self.archive = OwnmineDirectory(cfg['archive']).withName(name)
        self.rcon    = OwnmineRcon(cfg['rcon'])
        self.log     = None

    def withLog(self, logfile : str):
        self.log = logfile.replace(PLACEHOLDER_SERVER_NAME, self.name)
        return self

    def withRcon(self, binpath : str):
        self.rcon.bin = binpath.replace(PLACEHOLDER_SERVER_NAME, self.name)
        return self

    @ifenabled
    def start(self):
        pass



class OwnmineManager(object):
    def __init__(self, cfg : dict):
        self.settings = OwnmineSettings(cfg['ownmine'])
        for srv_name, srv_cfg in cfg['servers'].items():
            self.server[srv_name] =                     \
                OwnmineServer(srv_name, srv_cfg)        \
                    .withLog(self.settings.logfile)     \
                    .withRcon(self.settings.rconbin)



