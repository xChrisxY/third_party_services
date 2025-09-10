class BusinessException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NotFoundException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ValidationException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UnauthorizedException(Exception):
    def __init__(self, message: str = "Unauthorized"):
        self.message = message
        super().__init__(self.message)


class ConflictException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)