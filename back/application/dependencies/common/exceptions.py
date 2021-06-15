class Error(Exception):
    """Base class for other exceptions"""
    pass

class FilterByParameterError(Error):
    """Raised when the filter_by parameter is ill-structured"""
    pass

class MissedParameterError(Error):
    """Raised when the missing parameter"""
    pass

class DateFormatInvalidError(Error):
    """Raised when date format is invalid"""
    pass

class UserCreationError(Error):
    """Raised when error during user creation"""
    pass
