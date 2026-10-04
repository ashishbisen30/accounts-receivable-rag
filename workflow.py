import os
import time
import warnings
from typing import TypedDict, Optional, Dict, Any
from dotenv import load_dotenv

# 1. Suppress unnecessary Hugging Face and SDK warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

from google.genai import types
from google.genai.errors import ServerError, ClientError, APIError
from langgraph.graph import StateGraph, END

# Import RAG and Database utilities
from rag import retrieve_relevant_context, gemini_client
from financial_metrics import (
    Session,
    generate_followup_list,
    get_customer_outstanding_summary,
    get_invoice_financial_summary
)

load_dotenv()

# ============================================================
# Dynamic Model Discovery & Fallback Filtering
# ============================================================
def discover_available_models():
    """Queries the Gemini API at startup to filter stable text-generation models."""
    try:
        available = []
        # Keywords to skip (audio, specialized, or non-text models)
        banned_keywords = ["tts", "audio", "embed", "imagen", "vision", "realtime", "live"]
        
        for m in gemini_client.models.list():
            model_name = m.name.lower()
            
            # Skip non-text/specialized models
            if any(banned in model_name for banned in banned_keywords):
                continue

            # Keep valid content generation models
            if hasattr(m, "supported_generation_methods"):
                if "generateContent" in m.supported_generation_methods:
                    available.append(m.name)
            else:
                available.append(m.name)
                
        return available
    except Exception as e:
        print(f"[Warning] Could not list models dynamically: {e}")
        return []

# Discover available text models at runtime
DISCOVERED_MODELS = discover_available_models()

# Hardcoded priority text models
DEFAULT_TEXT_MODELS = [
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash"
]

if DISCOVERED_MODELS:
    # Filter discovered list against known working general-purpose text targets
    valid_discovered = [m for m in DISCOVERED_MODELS if "2.5-flash" not in m and "2.5-pro" not in m]
    if valid_discovered:
        PRIMARY_MODEL = valid_discovered[0]
        FALLBACK_MODELS = [m for m in valid_discovered if m != PRIMARY_MODEL] + DEFAULT_TEXT_MODELS
    else:
        PRIMARY_MODEL = DEFAULT_TEXT_MODELS[0]
        FALLBACK_MODELS = DEFAULT_TEXT_MODELS[1:]
else:
    PRIMARY_MODEL = DEFAULT_TEXT_MODELS[0]
    FALLBACK_MODELS = DEFAULT_TEXT_MODELS[1:]

print(f"[Info] Selected Active Model: '{PRIMARY_MODEL}'")


def safe_generate_content(prompt: str, max_retries: int = 3, initial_delay: float = 2.0) -> str:
    """Executes Gemini requests with exponential backoff and text-model failover."""
    # Deduplicate model list while preserving order
    models_to_try = []
    for m in [PRIMARY_MODEL] + FALLBACK_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)
    
    # Disable AFC configuration to silence deprecation warnings
    config = types.GenerateContentConfig(
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    for model_name in models_to_try:
        delay = initial_delay
        for attempt in range(max_retries):
            try:
                response = gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                return response.text
            except (ServerError, ClientError, APIError) as e:
                # If 404 or unsupported model, skip immediately to next model
                if isinstance(e, ClientError) and getattr(e, 'code', None) == 404:
                    print(f"[Notice] Model '{model_name}' unavailable (404). Switching to next fallback...")
                    break
                
                # Retry on temporary rate limit or 503 capacity issues
                if attempt < max_retries - 1:
                    print(f"[Warning] Model '{model_name}' busy ({e}). Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    print(f"[Notice] Model '{model_name}' failed after {max_retries} attempts. Switching fallback...")
            except Exception as e:
                print(f"[Error] Unexpected error on model '{model_name}': {e}")
                break

    raise RuntimeError("All configured Gemini text models are currently busy or unavailable. Please check your API quota and try again.")


# ============================================================
# 1. State Definition
# ============================================================
class ARState(TypedDict):
    question: str
    route: Optional[str]              # "SQL", "RAG", or "HYBRID"
    sql_data: Optional[Dict[str, Any]]
    rag_context: Optional[str]
    sources: Optional[list]
    final_answer: Optional[str]


# ============================================================
# 2. Router Node
# ============================================================
def route_query_node(state: ARState) -> ARState:
    """Classifies user intent into SQL, RAG, or HYBRID using Gemini."""
    question = state["question"]
    
    prompt = f"""You are an expert query router for an Accounts Receivable system.
Analyze the user's input question and classify it into exactly ONE of these three categories:

1. 'SQL': Use when the user asks for specific customer balances, invoice numbers, overdue accounts, payment lists, or numerical financial data.
2. 'RAG': Use when the user asks general questions about company finance policies, late fees, credit terms, dispute procedures, or guidelines.
3. 'HYBRID': Use when the question asks for recommendations or actions that require BOTH specific customer data AND finance policy guidance (e.g., "What action should we take for Customer X based on their overdue days?").

Respond ONLY with one word: SQL, RAG, or HYBRID.

USER QUESTION: {question}
CATEGORY:"""

    raw_response = safe_generate_content(prompt)
    route = raw_response.strip().upper()
    
    if route not in ["SQL", "RAG", "HYBRID"]:
        route = "HYBRID"  # Fallback default
        
    return {"route": route}


# ============================================================
# 3. Execution Nodes
# ============================================================
def sql_node(state: ARState) -> ARState:
    """Retrieves financial metrics from SQLite using SQLAlchemy Session."""
    session = Session()
    try:
        followups = generate_followup_list(session)
        customer_summaries = get_customer_outstanding_summary(session)
    finally:
        session.close()

    return {
        "sql_data": {
            "customers_requiring_followup": followups,
            "all_customer_summaries": customer_summaries
        }
    }


def rag_node(state: ARState) -> ARState:
    """Retrieves policy context from ChromaDB."""
    question = state["question"]
    chunks, sources = retrieve_relevant_context(question, top_k=2)
    context_text = "\n\n---\n\n".join(chunks)
    
    return {
        "rag_context": context_text,
        "sources": sources
    }


def hybrid_node(state: ARState) -> ARState:
    """Executes both SQL data lookup and Vector RAG retrieval."""
    question = state["question"]
    
    # 1. Fetch SQL metrics
    session = Session()
    try:
        followups = generate_followup_list(session)
        invoices = get_invoice_financial_summary(session)
        overdue_invoices = [i for i in invoices if i["is_overdue"]]
    finally:
        session.close()
    
    # 2. Fetch RAG policy chunks
    chunks, sources = retrieve_relevant_context(question, top_k=2)
    context_text = "\n\n---\n\n".join(chunks)
    
    return {
        "sql_data": {
            "customers_requiring_followup": followups,
            "overdue_invoices": overdue_invoices
        },
        "rag_context": context_text,
        "sources": sources
    }


# ============================================================
# 4. Synthesizer Node
# ============================================================
def generate_response_node(state: ARState) -> ARState:
    """Generates the final response based on collected state context."""
    question = state["question"]
    route = state.get("route")
    sql_data = state.get("sql_data")
    rag_context = state.get("rag_context")
    
    prompt = f"""You are an Accounts Receivable AI Assistant. Answer the user question based on the provided context.

USER QUESTION: {question}
QUERY TYPE: {route}
"""
    
    if sql_data:
        prompt += f"\nFINANCIAL DATA (SQL):\n{sql_data}\n"
        
    if rag_context:
        prompt += f"\nFINANCE POLICY CONTEXT (RAG):\n{rag_context}\n"
        
    prompt += """
INSTRUCTIONS:
- For SQL queries: Summarize financial metrics clearly with exact amounts, invoice IDs, and customer details.
- For RAG queries: Answer based strictly on the policy context provided.
- For HYBRID queries: Combine the customer's financial situation with official policies to recommend clear, actionable next steps.
"""

    answer = safe_generate_content(prompt)
    return {"final_answer": answer}


# ============================================================
# 5. Conditional Router Callback
# ============================================================
def decide_next_node(state: ARState) -> str:
    route = state.get("route", "HYBRID")
    if route == "SQL":
        return "sql_node"
    elif route == "RAG":
        return "rag_node"
    else:
        return "hybrid_node"


# ============================================================
# 6. Build Graph
# ============================================================
workflow = StateGraph(ARState)

# Add Nodes
workflow.add_node("router", route_query_node)
workflow.add_node("sql_node", sql_node)
workflow.add_node("rag_node", rag_node)
workflow.add_node("hybrid_node", hybrid_node)
workflow.add_node("synthesizer", generate_response_node)

# Set Entry Point
workflow.set_entry_point("router")

# Add Conditional Edges from Router
workflow.add_conditional_edges(
    "router",
    decide_next_node,
    {
        "sql_node": "sql_node",
        "rag_node": "rag_node",
        "hybrid_node": "hybrid_node"
    }
)

# Connect Execution Nodes to Synthesizer and End
workflow.add_edge("sql_node", "synthesizer")
workflow.add_edge("rag_node", "synthesizer")
workflow.add_edge("hybrid_node", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compile Application
ar_assistant_app = workflow.compile()


def run_query(user_question: str):
    """Executes the query through the LangGraph workflow."""
    initial_state = {
        "question": user_question,
        "route": None,
        "sql_data": None,
        "rag_context": None,
        "sources": None,
        "final_answer": None
    }
    
    result = ar_assistant_app.invoke(initial_state)
    return result


if __name__ == "__main__":
    print("==================================================")
    print(" TESTING LANGGRAPH QUERY ROUTING WORKFLOW ")
    print("==================================================\n")
    
    test_queries = [
        "Which customers currently require payment follow-up?",
        "What is our policy for overdue invoices past 30 days?",
        "Which customers are overdue and what collection actions should we take based on policy?"
    ]
    
    for q in test_queries:
        print(f"QUERY: {q}")
        output = run_query(q)
        print(f"ROUTE DECISION: [{output['route']}]")
        print(f"ANSWER:\n{output['final_answer']}")
        print("-" * 50)