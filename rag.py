import os
import certifi
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Setup SSL Certificates for Gemini Client
cert_file = os.environ.get("SSL_CERT_FILE")
if not cert_file or not os.path.exists(cert_file):
    os.environ["SSL_CERT_FILE"] = certifi.where()

if os.environ.get("SSL_CERT_DIR") and not os.path.isdir(os.environ["SSL_CERT_DIR"]):
    os.environ.pop("SSL_CERT_DIR", None)

# Initialize Gemini Client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Configuration & Paths
CHROMA_DATA_PATH = "data/chroma_db"
COLLECTION_NAME = "finance_policies"

# Initialize ChromaDB persistent client and embedding function
chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def retrieve_relevant_context(query: str, top_k: int = 2):
    """Queries ChromaDB to retrieve top_k semantically relevant policy chunks."""
    collection = chroma_client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef
    )

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    retrieved_chunks = []
    sources = []

    for doc, meta in zip(documents, metadatas):
        retrieved_chunks.append(doc)
        sources.append({
            "source": meta.get("source", "company_policy.txt"),
            "title": meta.get("title", "Finance Policy")
        })

    return retrieved_chunks, sources


def generate_rag_answer(user_question: str):
    """Retrieves policy context and generates grounded answer using Gemini LLM."""
    context_chunks, sources = retrieve_relevant_context(user_question, top_k=2)
    context_text = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are an expert corporate Accounts Receivable & Finance Policy Assistant.
Answer the user's question strictly based on the provided policy context below.
If the answer cannot be found in the context, state clearly that the context does not contain enough information.

CONTEXT FROM POLICY DOCUMENTS:
{context_text}

USER QUESTION:
{user_question}

INSTRUCTIONS:
Provide a concise, accurate answer based ONLY on the context provided above.
"""

    response = gemini_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return {
        "question": user_question,
        "answer": response.text,
        "sources": sources
    }