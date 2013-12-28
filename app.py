# coding=utf-8

# tornado framework
from tornado.ioloop import IOLoop
from tornado.web import Application, HTTPError, RequestHandler
from tornado.options import define, options

# inne
from database import DatabaseManager

# konfiguracja modułu options
define("config", help = "Specify configuration file")
define("port", default = 8080, help = "Application's listening port")
define("db_host", help = "MySQL database server address")
define("db_user", help = "MySQL user")
define("db_pass", help = "MySQL user's password")
define("db_dbbs", help = "MySQL database")
define("secret_key", default = "mySampleCookieSecret", help = "a secret key used in encryption/decryption")

class ClassRegisterApplication(Application):

    def __init__(self):
        handlers = [
            # mapowanie url do klas
        ]
        
        Application.__init__(self, handlers,
            debug = True,
            template_path = "templates/",
            static_path = "statics/",
            cookie_secret = options.secret_key
        )
        
        self.database = DatabaseManager(options.db_host, options.db_user, options.db_pass,
                options.db_dbbs)

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
