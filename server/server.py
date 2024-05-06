from flask import Flask
from flask import request

import json
import functools

from utils.appauth import *


app     = Flask(__name__)
db      = DBControl()
appAuth = AppAuthenticationServer(db)



def authenticate_app(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ok = appAuth.authenticateApp(request.headers, request.method)
            if not ok:
                return json.dumps({ "error": "Unknown error authenticating app" })
        except (
            #ConnectionNotEstablished,
            InvalidAppAuthenticationChallenge, AppAuthHeaderNotFound) as ex:
            return json.dumps({ "error": ex.message })
        return func(*args, **kwargs)
    return wrapper



@app.route("/auth/hmac", methods=['GET'])
@authenticate_app
def getHMACKey():
    try:
        return json.dumps({"success" : db.getHMACKey()})
    except Exception as ex:
        return json.dumps({"error" : str(ex)})




# if __name__ == "__main__":
#     app.run(host='0.0.0.0')
