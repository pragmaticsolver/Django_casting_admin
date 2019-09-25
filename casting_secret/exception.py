from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_406_NOT_ACCEPTABLE


class DataNotFoundException(APIException):
    status_code = HTTP_204_NO_CONTENT
    default_detail = 'No data found'


class GeneralException(APIException):
    status_code = HTTP_500_INTERNAL_SERVER_ERROR


class UnsupportedMimeTypeException(APIException):
    status_code = HTTP_406_NOT_ACCEPTABLE
    default_detail = 'Unsupported mime type'

# class ObjectDoesNotExist(ObjectDoesNotExist):
#     pass
