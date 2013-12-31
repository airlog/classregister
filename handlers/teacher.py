# coding=utf-8

# tornado framework
from tornado.web import authenticated, RequestHandler, HTTPError

# standardowe
from functools import wraps as func_wraps

# nasze
from base import BaseHandler

def __parse_template(template, session, args):
    for i in xrange(len(args)): template = template.replace("ARG{}".format(i), str(args[i]))
    return template.replace("SESSION_USER", session["user"])

def require_teacher():
    def actual_wrapper(method):
        @func_wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.session or self.session["type"] != "NAUCZYCIEL": raise HTTPError(403)
            return method(self, *args, **kwargs)
        return wrapper    
    return actual_wrapper

class MainHandler(BaseHandler):
    
    def _validate_pesel(self, pesel):
        if self.db.get_type(pesel) != "NAUCZYCIEL": raise HTTPError(404) # PESEL w URL nie jest nauczyciela
        elif self.session["user"] != pesel: raise HTTPError(403)         # PESEL w URL jest inny niż PESEL aktywnego użytkownika
        
    @authenticated
    @require_teacher()
    def get(self, pesel):
        self._validate_pesel(pesel)
        self.render("teacher/main.html")

class ScheduleHandler(MainHandler):

    @authenticated
    @require_teacher()
    def get(self, pesel):
        self._validate_pesel(pesel)
        
        schedule = self.db.get_teacher_schedule(self.session["userId"])        
        self.render("teacher/schedule.html", schedule = schedule)

class EventHandler(MainHandler):

    @authenticated
    @require_teacher()
    def get(self, pesel):
        self._validate_pesel(pesel)
        
        events = self.db.get_teacher_events(self.session["userId"])        
        self.render("teacher/events.html", events = events)


