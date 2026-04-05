from logging.config import dictConfig

def setup_logging():
    dictConfig({
        "version": 1,

        
        "disable_existing_loggers": False,
        "loggers": {
            "peewee": {
                "level": "WARNING"
            },
            "wekzeug": {
                "level": "WARNING"
            }
        },

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
                "level": "DEBUG",
                "filters": [ "request_filters" ]
                
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "./app/logging/logs/app.log",
                "formatter": "json",
                "level": "DEBUG",
                "filters": [ "request_filters" ]
            }
        },

        "filters": {
            "request_filters": {
                "()": "app.logging.filters.logging_filters.RequestFilter"
            }
        },

        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG"
        }
    })
