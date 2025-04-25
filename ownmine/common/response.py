from typing import Optional

class Response:
    SUCCESS         =  0
    DEFAULT_FAILURE = -1

    def __init__(self, err_code: int, msg: Optional[str] = None):
        self.err_code = err_code
        self.msg      = msg

    def __str__(self):
        if self.err_code == Response.SUCCESS:
            return "Success" + (f':\n{self.msg}' if self.msg is not None else "")
        return f"Failure" + (f':\n{self.msg}' if self.msg is not None else "")

    def __repr__(self):
        return str(self)

    def is_success(self):
        return self.err_code == 0

    def is_failure(self):
        return self.err_code != 0

    def errno(self):
        return self.err_code

    def message(self):
        return self.msg

    @staticmethod
    def success(msg: Optional[str] = None):
        return Response(Response.SUCCESS, msg)

    @staticmethod
    def failure(msg: str, err_code: Optional[int] = None):
        return Response(err_code if err_code is not None else Response.DEFAULT_FAILURE, msg)
