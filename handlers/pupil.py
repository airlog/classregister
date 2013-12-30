# coding=utf-8

# tornado framework
from tornado.web import authenticated, RequestHandler, HTTPError

# standardowe
from functools import wraps as func_wraps
from re import compile as Regex

# nasze
from base import BaseHandler

def __parse_template(template, session, args):
    for i in xrange(len(args)): template = template.replace("ARG{}".format(i), str(args[i]))
    return template.replace("SESSION_USER", session["user"])

def require_pupil(redirectUrl = "/"):
    def actual_wrapper(method):
        @func_wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.session or self.session["type"] != "UCZEN":
                self.redirect(__parse_template(redirectUrl, self.session, args))
            return method(self, *args, **kwargs)
        return wrapper    
    return actual_wrapper

class MainHandler(BaseHandler):
    
    def _validate_pesel(self, pesel):
        if self.db.get_type(pesel) != "UCZEN": raise HTTPError(404) # PESEL w URL nie jest ucznia
        elif self.session["user"] != pesel: raise HTTPError(403)    # PESEL w URL jest inny niż PESEL aktywnego użytkownika
        
    @authenticated
    @require_pupil("/teacher/SESSION_USER/pupil/ARG0")
    def get(self, pesel):
        self._validate_pesel(pesel)
        self.render("pupil/main.html")

class GradeHandler(MainHandler):

    @authenticated
    @require_pupil("/teacher/SESSION_USER/pupil/ARG0/grades")
    def get(self, pesel, courseStr):
        self._validate_pesel(pesel)
        
        courseId = None
        if courseStr not in ["", "/", "all"]: courseId = int(courseStr)

        grades = self.db.get_user_grades(self.session["userId"], courseId)
        self.render("pupil/grades.html", grades = grades)

