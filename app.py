from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import database session and metrics from local module
from financial_metrics import (
    Session,
    generate_followup_list,
    get_customer_outstanding_summary,
    get_invoice_financial_summary,
)
# Import vector search
from rag import retrieve_relevant_context

# Import compiled LangGraph workflow app
from workflow import ar_assistant_app

# ==========================================
# FastAPI App Initialization & Middleware
# ==========================================
app = FastAPI(
    title="Finance Assistant API",
    description="Task 7 - Accounts Receivable REST API & AI Assistant Integration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Health Check Endpoint
# ==========================================
@app.get("/", tags=["Health Check"])
def read_root():
    return {
        "status": "online",
        "message": "Finance Assistant API is running",
        "documentation": "http://127.0.0.1:8000/docs",
    }


# ==========================================
# Pydantic Schemas
# ==========================================
class PolicySearchRequest(BaseModel):
    query: str = Field(
        ..., example="What is our policy for overdue invoices past 30 days?"
    )
    top_k: int = Field(default=2, ge=1, le=10)


class PolicySearchResult(BaseModel):
    document: str
    source: str


class AssistantQueryRequest(BaseModel):
    question: str = Field(
        ...,
        example="Which customers are overdue and what collection actions should we take based on policy?",
    )


class AssistantQueryResponse(BaseModel):
    question: str
    route_decision: Optional[str]
    answer: Optional[str]


# ==========================================
# 1. VIEWING CUSTOMER RECORDS & BALANCES
# ==========================================
@app.get("/customers/summary", tags=["Customers & Balances"])
def get_all_customer_summaries():
    """Retrieve outstanding and overdue balances grouped by customer."""
    session = Session()
    try:
        data = get_customer_outstanding_summary(session)
        return {"status": "success", "data": data}
    finally:
        session.close()


@app.get("/customers/followup", tags=["Customers & Balances"])
def list_customers_requiring_followup():
    """Retrieve customers that currently require payment follow-up."""
    session = Session()
    try:
        data = generate_followup_list(session)
        return {"status": "success", "data": data}
    finally:
        session.close()


# ==========================================
# 2. INVOICE DETAILS & OVERDUE LISTING
# ==========================================
@app.get("/invoices/summary", tags=["Invoices"])
def list_invoice_summaries():
    """Retrieve financial summary for all invoices."""
    session = Session()
    try:
        data = get_invoice_financial_summary(session)
        return {"status": "success", "data": data}
    finally:
        session.close()


@app.get("/invoices/overdue", tags=["Invoices"])
def list_overdue_invoices():
    """Filter and list all invoices that are currently overdue."""
    session = Session()
    try:
        invoices = get_invoice_financial_summary(session)
        overdue = [inv for inv in invoices if inv.get("is_overdue")]
        return {"status": "success", "count": len(overdue), "data": overdue}
    finally:
        session.close()


# ==========================================
# 3. SEARCHING FINANCE POLICIES
# ==========================================
@app.post(
    "/policies/search",
    response_model=List[PolicySearchResult],
    tags=["Policy Search"],
)
def search_policies(payload: PolicySearchRequest):
    """Search policy documentation stored in ChromaDB vector store."""
    try:
        chunks, sources = retrieve_relevant_context(
            payload.query, top_k=payload.top_k
        )
        results = [
            {"document": chunk, "source": src}
            for chunk, src in zip(chunks, sources)
        ]
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying vector database: {str(e)}",
        )


# ==========================================
# 4. AI ASSISTANT QUERY ENDPOINT
# ==========================================
@app.post(
    "/assistant/query",
    response_model=AssistantQueryResponse,
    tags=["AI Assistant"],
)
def query_assistant(payload: AssistantQueryRequest):
    """
    Execute natural language queries through the LangGraph AR Assistant workflow.
    Routes between SQL, RAG, and HYBRID nodes.
    """
    try:
        initial_state = {
            "question": payload.question,
            "route": None,
            "sql_data": None,
            "rag_context": None,
            "sources": None,
            "final_answer": None,
        }

        result = ar_assistant_app.invoke(initial_state)

        return AssistantQueryResponse(
            question=payload.question,
            route_decision=result.get("route"),
            answer=result.get("final_answer"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing AI Assistant workflow: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)