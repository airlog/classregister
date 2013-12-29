# coding=utf-8

# tornado framework
from tornado.web import RequestHandler, HTTPError
from tornado.escape import json_encode, json_decode

class BaseHandler(RequestHandler):
    
    SESSION_COOKIE  = "session"
    FLASH_COOKIE   = "flash"
    
    @property
    def db(self):
        return self.application.database
        
    def render(self, *args, **kwargs):
        # każde wywołanie render przekazuje dodatkowo następujące obiekty
        mykwargs = {
                    "get_flash": self.get_flash,
                }
                
        # wywołaj render od ojca
        RequestHandler.render(self, *args, **dict(kwargs.items() + mykwargs.items()))
    
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

    def flash_message(self, caption, message):
        flash = self.get_secure_cookie(BaseHandler.FLASH_COOKIE)
        if flash is None: flash = []
        else: flash = json_decode(flash)
        
        flash.append((caption, message))
        self.set_secure_cookie(BaseHandler.FLASH_COOKIE, json_encode(flash))
        
    def get_flash(self):
        flash = self.get_secure_cookie(BaseHandler.FLASH_COOKIE)
        if flash is None: return []
        self.clear_cookie(BaseHandler.FLASH_COOKIE)
        return json_decode(flash)
