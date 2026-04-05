# app/logging/filters/logging_filters.py
import logging
from flask import request, g

# Adds request info to every log record if inside a requst context
class RequestFilter(logging.Filter):
    def filter(self, record):
        record.method = None
        record.path = None
        record.user_id = None

        try:
            record.method = request.method
            record.path = request.path
            record.user_id = getattr(g, "user_id", None)
        except RuntimeError:
            pass
        return True
    
