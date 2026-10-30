from fastapi import HTTPException, status

class AppBaseException(Exception):
    """Base domain exception"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class DocumentNotFoundError(AppBaseException):
    def __init__(self, document_id: int):
        super().__init__(f"Document with ID {document_id} was not found", status.HTTP_404_NOT_FOUND)

class ConversationNotFoundError(AppBaseException):
    def __init__(self, conversation_id: int):
        super().__init__(f"Conversation with ID {conversation_id} was not found", status.HTTP_404_NOT_FOUND)

class InvalidFileError(AppBaseException):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

class IngestionError(AppBaseException):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)

class AIProviderError(AppBaseException):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY)

class SearchServiceError(AppBaseException):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY)
