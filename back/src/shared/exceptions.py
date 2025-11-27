from typing import Optional


class BaseAppException(Exception):
    """Exceção base da aplicação"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(BaseAppException):
    """Recurso não encontrado"""
    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} não encontrado"
        if identifier:
            message += f" com identificador: {identifier}"
        super().__init__(message, status_code=404)


class ValidationException(BaseAppException):
    """Erro de validação"""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class UnauthorizedException(BaseAppException):
    """Não autorizado"""
    def __init__(self, message: str = "Não autorizado"):
        super().__init__(message, status_code=401)


class ForbiddenException(BaseAppException):
    """Acesso negado"""
    def __init__(self, message: str = "Acesso negado"):
        super().__init__(message, status_code=403)


class ConflictException(BaseAppException):
    """Conflito de recursos"""
    def __init__(self, message: str):
        super().__init__(message, status_code=409)

