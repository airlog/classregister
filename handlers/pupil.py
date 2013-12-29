# coding=utf-8

# tornado framework
from tornado.web import authenticated, RequestHandler, HTTPError

# nasze
from base import BaseHandler

class GradeHandler(BaseHandler):

    @authenticated
    def get(self, courseStr):
        session = self.get_session()
        if session["type"] != "UCZEN": raise HTTPError(403)
    
        courseId = None
        if courseStr != "all": courseId = int(courseStr)      

        grades = self.db.get_user_grades(session["userId"], courseId)
        self.render("pupil/grades.html", grades = grades)

