# coding=utf-8

# tornado framework
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.options import define, options

# nasze
from database import DatabaseManager
from handlers.base import BaseHandler
from handlers.auth import SigninHandler, SignoutHandler
from handlers import pupil

# konfiguracja modułu options
define("config", help = "Specify configuration file")
define("debug", default = False, help = "Specify debug mode state")
define("port", default = 8080, help = "Application's listening port")
define("db_host", help = "MySQL database server address")
define("db_user", help = "MySQL user")
define("db_pass", help = "MySQL user's password")
define("db_dbbs", help = "MySQL database")
define("secret_key", default = "mySampleCookieSecret", help = "A secret key used in encryption/decryption")
define("admin_password", default = "mySampleAdminPassword", help = "Password to login to any account")

class ClassRegisterApplication(Application):

    def __init__(self):
        handlers = [
            # mapowanie url do klas
            (r'/', BaseHandler),
            
            (r'/auth/signin', SigninHandler),
            (r'/auth/signout', SignoutHandler),
            
            (r'/pupil/(\d{1,11})/{0,1}', pupil.MainHandler),
            (r'/pupil/(\d{1,11})/grades/(.{0}|all|\d+)', pupil.GradeHandler),
            (r'/pupil/(\d{1,11})/schedule/{0,1}', pupil.ScheduleHandler),
            (r'/pupil/(\d{1,11})/events/{0,1}', pupil.EventHandler),
        ]
        
        Application.__init__(self, handlers,
            debug = options.debug,
            template_path = "templates/",
            static_path = "statics/",
            static_url_prefix = "/statics/",
            login_url = "/auth/signin",
            cookie_secret = options.secret_key,
            xsrf_cookie = True
        )
        
        self.database = DatabaseManager(options.db_host, options.db_user, options.db_pass,
                options.db_dbbs, charset = "cp1250")

def validate_option(dict, key):
    try:
        value = dict[key]
        if value == None: return False
    except KeyError: return False
    return True

if __name__ == "__main__":
    options.parse_command_line()
    if options.config is not None: options.parse_config_file(options.config)

    # wymagana konfiguracja aplikacji
    opt = options.as_dict()
    assert validate_option(opt, "db_host")
    assert validate_option(opt, "db_user")
    assert validate_option(opt, "db_pass")
    assert validate_option(opt, "db_dbbs")

    app = ClassRegisterApplication()
    app.listen(options.port)
    IOLoop.instance().start()

