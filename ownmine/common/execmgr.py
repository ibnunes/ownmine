class ExecutionMode:
    # RUN    = 1  # 0b0001
    DRYRUN: int = 2  # 0b0010
    DEBUG:  int = 4  # 0b0100

    def __init__(self, flag: int = 0):
        self.flag = flag

    def is_dryrun(self) -> bool:
        return self.flag & ExecutionMode.DRYRUN != 0

    def is_debug(self) -> bool:
        return self.flag & ExecutionMode.DEBUG != 0

    def set_dryrun(self) -> int:
        return self.flag | ExecutionMode.DRYRUN

    def set_debug(self) -> int:
        return self.flag | ExecutionMode.DEBUG
