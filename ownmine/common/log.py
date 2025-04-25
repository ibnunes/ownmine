import datetime
from typing import Optional

from common.execmgr import ExecutionMode


class OwnmineLog:
    FATAL   =  4
    ERROR   =  3
    WARNING =  2
    INFO    =  1
    MESSAGE =  0
    DEBUG   = -1

    _log_levels_descriptions = {
        DEBUG:   "[Debug]",
        MESSAGE: "",
        INFO:    "[Info]",
        WARNING: "[Warning]",
        ERROR:   "[Error]",
        FATAL:   "[FATAL]",
    }

    _log_levels_consts = {
        "FATAL":   FATAL,
        "ERROR":   ERROR,
        "WARNING": WARNING,
        "INFO":    INFO,
        "MESSAGE": MESSAGE,
        "DEBUG":   DEBUG,
    }


    def __init__(self, enable = True, minlevel: int = WARNING, filepath: Optional[str] = None, execmode: Optional[ExecutionMode] = None):
        self.log      = self._noop_log
        self.logs     = self._noop_log
        self.filepath = filepath
        self.minlevel = minlevel
        self.execmode = execmode if execmode is not None else ExecutionMode()
        if enable:
            self.enable()


    @staticmethod
    def type_description(level: int) -> str:
        """Get the log level description string."""
        return OwnmineLog._log_levels_descriptions.get(level, "")


    @staticmethod
    def type_const(level: str | None) -> int:
        """Get the log level int constant."""
        if level is None:
            return OwnmineLog.MESSAGE
        return OwnmineLog._log_levels_consts.get(level.strip().upper(), OwnmineLog.MESSAGE)


    def _simple_log(self, level: int, msg: str, skip_file = False):
        if level < self.minlevel and not self.execmode.is_debug():
            return      # If execution mode is DEBUG, minlevel is ignored
        print(msg)
        if self.filepath is not None and not skip_file:
            self._fprint(msg)


    def _full_log(self, level: int, msg: str, skip_file = False):
        """Log message with timestamp and level, output to stderr and file."""
        if level < self.minlevel and not self.execmode.is_debug():
            return      # If execution mode is DEBUG, minlevel is ignored

        level_desc = OwnmineLog.type_description(level)
        now        = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        formatted_message = f"[{now}] {level_desc} " + msg

        # THINK: Print to stderr?
        print(formatted_message)  # file=sys.stderr

        if self.filepath is not None and not skip_file:
            self._fprint(formatted_message)


    def _noop_log(self, simple: bool, level: int, msg: str, skip_file = False):
        """No-op log, does nothing, except if exec mode is DEBUG."""
        if self.execmode.is_debug():
            (self._simple_log if simple else self._full_log)(level, msg, skip_file)
        # pass


    def _fprint(self, message: str):
        """Write log message to a file."""
        try:
            with open(self.filepath, "a") as f:
                print(message, file=f)
        except Exception as e:
            pass
            # print(f"Internal OwnmineLog ERROR: {e}")


    def enable(self):
        """Enable logging."""
        self.log  = self._full_log
        self.logs = self._simple_log

    def disable(self):
        """Disable logging."""
        self.log  = lambda level, msg, skip_file: self._noop_log(False, level, msg, skip_file)
        self.logs = lambda level, msg, skip_file: self._noop_log(True, level, msg, skip_file)


    def f(self, msg: str, skip_file = False):
        return self.log(OwnmineLog.FATAL, msg, skip_file)

    def e(self, msg: str, skip_file = False):
        return self.log(OwnmineLog.ERROR, msg, skip_file)

    def w(self, msg: str, skip_file = False):
        return self.log(OwnmineLog.WARNING, msg, skip_file)

    def i(self, msg: str, skip_file = False):
        return self.log(OwnmineLog.INFO, msg, skip_file)

    def m(self, msg: str, skip_file = False):
        return self.log(OwnmineLog.MESSAGE, msg, skip_file)

    def d(self, msg: str, skip_file = False):
        return self.log(OwnmineLog.DEBUG, msg, skip_file)
