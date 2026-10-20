class LibraryException(Exception):
    """Base exception for all application-specific errors."""
    pass

class ResourceNotFoundError(LibraryException):
    """Raised when a Book or Member does not exist."""
    pass

class DataConflictError(LibraryException):
    """Raised when a unique constraint fails (e.g., duplicate ISBN or email)."""
    pass

class BusinessRuleError(LibraryException):
    """Raised when a business rule is broken (like deleting a member who has books)."""
    pass
