from rest_framework import exceptions

class AlreadyBangListedException(exceptions.APIException):
	status_code = 403
	detail = "This person is already on your Bang List!"

class AlreadyBangedException(exceptions.APIException):
	status_code = 403
	detail = "AlreadyBangedException: You two have already agreed to Bang!"

