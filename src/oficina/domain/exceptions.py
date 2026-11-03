class DomainError(Exception):
    """Erro de regra de negócio."""

class NotFoundError(DomainError):
    pass

class ConflictError(DomainError):
    pass

class InvalidTransitionError(DomainError):
    pass

class ValidationError(DomainError):
    pass
