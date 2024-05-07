import json

class Response:
    ATTRIBUTE_ERROR   = "error"
    ATTRIBUTE_SUCCESS = "success"

    @staticmethod
    def success(value):
        return json.dumps({ Response.ATTRIBUTE_SUCCESS : value })

    @staticmethod
    def error(msg : str):
        return json.dumps({ Response.ATTRIBUTE_ERROR : msg })
