class DatabaseError(Exception):
    """Base class for database exceptions"""
    pass
        
class ResourceNotFoundError(Exception):
    """Raised when a required record isn't found"""
    pass

class DataValidationError(DatabaseError):
    """Raised when the data provided is invalid for the DB"""
    pass
