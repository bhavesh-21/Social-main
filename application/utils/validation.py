from werkzeug.exceptions import HTTPException
from flask import make_response
import json
class SchemaValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = { "error_code" : error_code, "error_message": error_message }
        self.response = make_response(json.dumps(data), status_code)

class UserValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = { "error_code" : error_code, "error_message": error_message }
        self.response = make_response(json.dumps(data), status_code)

class PostValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = { "error_code" : error_code, "error_message": error_message }
        self.response = make_response(json.dumps(data), status_code)

class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)

class AlreadyExistError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)
