from fastapi import status

class APIError(Exception):
    def __init__(self, message: str, status_code: int, data=None):
        self.message = message
        self.status_code = status_code
        self.data = data

def bad_request(msg: str, data=None):   return APIError(msg, status.HTTP_400_BAD_REQUEST, data)
def unauthorized(msg="unauthorized_user"): return APIError(msg, status.HTTP_401_UNAUTHORIZED)
def forbidden(msg="forbidden"):         return APIError(msg, status.HTTP_403_FORBIDDEN)
def not_found(msg: str):                return APIError(msg, status.HTTP_404_NOT_FOUND)
def conflict(msg: str):                 return APIError(msg, status.HTTP_409_CONFLICT)
def unprocessable(msg: str, data=None): return APIError(msg, status.HTTP_422_UNPROCESSABLE_ENTITY, data)
def payload_too_large(msg: str, data=None): return APIError(msg, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, data)
