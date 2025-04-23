# from dataclasses import dataclass
from common.response import Response

# @dataclass
class SocketMessageFormat:
    ERROR_PREFIX   = "[ERROR]"  # len: 7
    SUCCESS_PREFIX = "[OK]"     # len: 4

    @staticmethod
    def enconde_error(s: str):
        return f"{SocketMessageFormat.ERROR_PREFIX} {s}"

    @staticmethod
    def encode_success(s: str):
        return f"{SocketMessageFormat.SUCCESS_PREFIX} {s}"

    @staticmethod
    def enconde_from_response(r: Response):
        if r.is_success():
            return SocketMessageFormat.encode_success(r.message())
        return SocketMessageFormat.enconde_error(r.message())

    @staticmethod
    def decode_as_response(s: str):
        if s.startswith(SocketMessageFormat.ERROR_PREFIX):
            return Response.failure(s[7:].strip())
        if s.startswith(SocketMessageFormat.SUCCESS_PREFIX):
            return Response.success(s[4:].strip())
        # Even if no SUCCESS_PREFIX is present, we'll consider it a success
        return Response.success(s.strip())
