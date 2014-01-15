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

from tornado.escape import json_encode        
class EventHandler(MainHandler):

    def __fill_attributes(self, attrs):        
        for key in attrs: attrs[key] = self.get_argument(key)
        return attrs
    
    def __assert_attributes(self, attrs):
        for key, value in attrs.items():
            if value is None or value == "": raise HTTPError(405, "Illegal value of '{}': '{}'".format(key, value))

    def __new_event(self):
        attrs = self.__fill_attributes({"_xsrf": None, "data": None, "lekcja": None, "przedmiot": None, "klasa": None, "tresc": None,})
        self.__assert_attributes(attrs)
    
        self.db.add_teacher_event(
                self.session["userId"],
                attrs["data"],
                attrs["lekcja"],
                attrs["przedmiot"],
                attrs["klasa"],
                attrs["tresc"]
            )
        self.flash_message("Dodano wydarzenie", "Pomyślnie dodano wydarzenie!")
        self.redirect("/teacher/{}/events/".format(self.session["user"]))
    
    def __edit_event(self, eventId):
        attrs = self.__fill_attributes({"_xsrf": None, "eventid": None, "data": None, "lekcja": None, "przedmiot": None, "klasa": None, "tresc": None,})
        self.__assert_attributes(attrs)
        if eventId == int(attrs["eventid"]): raise HTTPError(403, "Different eventId security check failed!")
        
        self.db.edit_teacher_event(
                self.session["userId"],
                attrs["eventid"],
                attrs["data"],
                attrs["lekcja"],
                attrs["przedmiot"],
                attrs["klasa"],
                attrs["tresc"]
            )
        self.flash_message("Edytowano wydarzenie", "Pomyślnie edytowano wydarzenie nr.{}!".format(eventId))
        self.redirect("/teacher/{}/events/".format(self.session["user"]))
    
    def __del_event(self, eventId):
        attrs = self.__fill_attributes({"_xsrf": None, "eventid": None,})
        self.__assert_attributes(attrs)
        if eventId == int(attrs["eventid"]): raise HTTPError(403, "Different eventId security check failed!")
        
        self.db.delete_teacher_event(attrs["eventid"])
        self.flash_message("Usunięto wydarzenie", "Pomyślnie usunięto wydarzenie nr.{}!".format(eventId))
        self.redirect("/teacher/{}/events/".format(self.session["user"]))
    
    @authenticated
    @require_teacher()
    def get(self, pesel, task = None, eventId = None):
        self._validate_pesel(pesel)
        if task is not None and task != "": raise HTTPError(403)
        
        events = self.db.get_teacher_events(self.session["userId"])        
        self.render("teacher/events.html", events = events)

    @authenticated
    @require_teacher()
    def post(self, pesel, task, eventId = None):
        self._validate_pesel(pesel)
        
        task = task.split("/")[0]        
        if task == "new": self.__new_event()
        elif task == "edit": self.__edit_event(eventId)
        elif task == "del": self.__del_event(eventId)
        else: raise HTTPError(403)

class GroupHandler(MainHandler):

    def __get_groups(self, pesel):
        groups = self.db.get_teacher_groups(self.session["userId"])
        self.render("teacher/groups.html", groups = groups)
        
    def __get_groupview(self, pesel, courseId):
        cid = int(courseId) # regex broni, regex chroni!
        pupils = self.db.get_pupils_in_class(cid)
        self.render("teacher/groupview.html", pupils = pupils)
        
    def __get_pupil(self, pesel, courseId, pupilId):
        cid, pid = int(courseId), int(pupilId)
        grades = self.db.get_teacher_pupil_grades(cid, pid)
        absence = self.db.get_pupil_absence(pid, cid)
        pupilData = self.db.get_pupil_data(pid, cid)
        self.render("teacher/pupil.html", grades = grades, absence = absence, pupilData = pupilData)

    @authenticated
    @require_teacher()
    def get(self, pesel, courseId = None, pupilId = None):
        self._validate_pesel(pesel)
          
        if pupilId is not None: self.__get_pupil(pesel, courseId, pupilId)
        elif courseId is not None: self.__get_groupview(pesel, courseId);
        else: self.__get_groups(pesel)

