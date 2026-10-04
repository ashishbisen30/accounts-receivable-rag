from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# Customer Schemas
class CustomerResponse(BaseModel):
    customer_id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


# Invoice Schemas
class InvoiceResponse(BaseModel):
    invoice_id: int
    customer_id: int
    amount: float
    paid_amount: float
    outstanding_balance: float
    status: str
    due_date: date
    days_overdue: int

    class Config:
        from_attributes = True


# Balance Summary Schema
class CustomerBalanceSummary(BaseModel):
    customer_id: int
    customer_name: str
    total_outstanding: float
    total_overdue: float
    overdue_invoice_count: int


# Policy Search Schemas
class PolicySearchRequest(BaseModel):
    query: str = Field(..., example="What is our policy for overdue invoices past 30 days?")
    top_k: int = Field(default=3, ge=1, le=10)


class PolicySearchResult(BaseModel):
    document: str
    metadata: Dict[str, Any]
    score: Optional[float] = None


# AI Assistant Request/Response
class AssistantQueryRequest(BaseModel):
    question: str = Field(..., example="Which customers are overdue and what collection actions should we take based on policy?")
    thread_id: Optional[str] = Field(default="default_session", description="Thread ID for conversation state persistence")


class AssistantQueryResponse(BaseModel):
    question: str
    route_decision: str
    answer: str