class DatabaseConnectionException(Exception):
    """Raised when a connection to the database cannot be established."""
    pass


class InvalidArgumentException(Exception):
    """Raised when a function receives an invalid argument which fails validation."""
    pass


class NameAlreadyExistsException(Exception):
    """Raised when attempting to create a resource with a name that already exists in the database."""
    pass
