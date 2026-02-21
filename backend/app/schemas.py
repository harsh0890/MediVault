"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    user_id: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    redirect_url: str = None


class ChatbotRequest(BaseModel):
    question: str


class ChatbotResponse(BaseModel):
    answer: str
    recommendations: list[str] = []  # Empty by default, only populated when user requests
    sources: list[str] = []  # Source citations - which documents were used
    needs_followup: bool = False  # Indicates if bot is asking a question/offering help
    has_records: bool = False  # Indicates if answer came from medical records


class SummaryResponse(BaseModel):
    summary: str


class RAGRebuildResponse(BaseModel):
    status: str
    message: str
    documents_processed: int = 0
    chunks_created: int = 0
