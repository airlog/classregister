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

class GradeHandler(BaseHandler):

    @authenticated
    @require_pupil
    def get(self, courseStr):    
        courseId = None
        if courseStr != "all": courseId = int(courseStr)      

        grades = self.db.get_user_grades(self.session["userId"], courseId)
        self.render("pupil/grades.html", grades = grades)

