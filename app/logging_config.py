from logging.config import dictConfig

def setup_logging():
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "[%(levelname)s] %(name)s: %(message)s"
                
            },
            "simple": {
                "format": "[%(levelname)s %(name)s: %(message)s]"
            }
        },
        "handlers":  {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "DEBUG"
                
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "json",
                "level": "INFO"
            }
        },

        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG"
        }
    })
