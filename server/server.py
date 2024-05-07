# Flask dependencies
from flask import Flask
from flask import request

# Python libraries
import json
import functools

# Self dependencies
from utils.appauth import *
from utils.response import Response


# Global singletons
app     = Flask(__name__)
db      = DBControl()
appAuth = AppAuthenticationServer(db)


# Decorators
def authenticate_app(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ok = appAuth.authenticateApp(request.headers, request.method)
            if not ok:
                return Response.error("Unknown error authenticating app")
        except (InvalidAppAuthenticationChallenge, AppAuthHeaderNotFound) as ex:
            return Response.error(ex.message)
        return func(*args, **kwargs)
    return wrapper


# ----------
#   Server
# ----------

@app.route("/auth/hmac", methods=['GET'])
@authenticate_app
def getHMACKey():
    try:
        return Response.success(db.getHMACKey())
    except Exception as ex:
        return Response.error(str(ex))




# if __name__ == "__main__":
#     app.run(host='0.0.0.0')
