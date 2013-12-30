# coding=utf-8

# tornado framework
from tornado.web import authenticated, RequestHandler, HTTPError

# standardowe
from functools import wraps as func_wraps

# nasze
from base import BaseHandler

def require_pupil(method):
    """ Decorate methods with this to require that the user be a pupil. """
    
    @func_wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.session or self.session["type"] != "UCZEN": raise HTTPError(403)
        return method(self, *args, **kwargs)
    
    return wrapper

class MainHandler(BaseHandler):
    
    def _validate_pesel(self, pesel):
        if self.db.get_type(pesel) != "UCZEN": raise HTTPError(404) # PESEL w URL nie jest ucznia
        elif self.session["user"] != pesel: raise HTTPError(403)    # PESEL w URL jest inny niż PESEL aktywnego użytkownika
        
    @authenticated
    @require_pupil
    def get(self, pesel):
        self._validate_pesel(pesel)
        self.render("pupil/main.html")

class GradeHandler(MainHandler):

    @authenticated
    @require_pupil
    def get(self, pesel, courseStr):
        self._validate_pesel(pesel)
        
        courseId = None
        if courseStr not in ["", "/", "all"]: courseId = int(courseStr)

        grades = self.db.get_user_grades(self.session["userId"], courseId)
        self.render("pupil/grades.html", grades = grades)

