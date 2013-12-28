# coding=utf-8

# tornado framework
from tornado.web import RequestHandler, HTTPError
from tornado.escape import json_encode, json_decode

class BaseHandler(RequestHandler):
    
    SESSION_COOKIE  = "session"
    
    @property
    def db(self):
        return self.application.database
    
    def set_session(self, data):
        if not isinstance(data, dict): raise ValueError("data should be a dictionary")
        encoded = json_encode(data)
        self.set_secure_cookie(BaseHandler.SESSION_COOKIE, encoded)

    def get_session(self):
        json = self.get_secure_cookie(BaseHandler.SESSION_COOKIE)
        if json is not None: return json_decode(json)
        return None

    def clear_session(self):
        self.clear_cookie(BaseHandler.SESSION_COOKIE)

