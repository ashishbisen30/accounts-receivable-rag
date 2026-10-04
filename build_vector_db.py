import os
import chromadb
from chromadb.utils import embedding_functions

# -----------------------------------------------------------------------------
# Configuration & Paths
# -----------------------------------------------------------------------------
POLICY_FILE = "data/company_policy.txt"
CHROMA_DATA_PATH = "data/chroma_db"
COLLECTION_NAME = "finance_policies"

# Initialize ChromaDB persistent client (saves vectors locally on disk)
chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

# Use sentence-transformers embedding model (all-MiniLM-L6-v2)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


# -----------------------------------------------------------------------------
# 1. Load Policy Documents
# -----------------------------------------------------------------------------
def load_policy_documents(file_path):
    """
    Reads the full policy text file from disk.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found at {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# -----------------------------------------------------------------------------
# 2. Document Chunking
# -----------------------------------------------------------------------------
def chunk_policy_documents(text):
    """
    Splits policy documents into logical sections/paragraphs.
    Each 'DOCUMENT X:' section is split into distinct chunks.
    """
    raw_sections = text.strip().split("DOCUMENT ")
    chunks = []
    metadata = []

    for idx, section in enumerate(raw_sections):
        if not section.strip():
            continue

        lines = [line.strip() for line in section.strip().split("\n") if line.strip()]
        doc_title = lines[0] if lines else f"Policy Section {idx}"
        full_content = "\n".join(lines)

        chunks.append(full_content)
        metadata.append({"source": "company_policy.txt", "doc_id": idx, "title": doc_title})

    return chunks, metadata


# -----------------------------------------------------------------------------
# 3. Store Embeddings in ChromaDB
# -----------------------------------------------------------------------------
def build_vector_database():
    """
    Chunks documents, generates embeddings, and stores them in ChromaDB.
    """
    print("Loading policy text...")
    text = load_policy_documents(POLICY_FILE)

    chunks, metadatas = chunk_policy_documents(text)
    print(f"Generated {len(chunks)} document chunks.")

    # Get or create ChromaDB collection
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef,
        metadata={"description": "Accounts Receivable Policy Vectors"}
    )

    # Generate unique IDs for each chunk
    ids = [f"policy_doc_{i+1}" for i in range(len(chunks))]

    # Add documents, metadata, and IDs to ChromaDB
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Successfully stored {collection.count()} chunks into ChromaDB at '{CHROMA_DATA_PATH}'.")
    return collection


# -----------------------------------------------------------------------------
# 4. Semantic Search Implementation
# -----------------------------------------------------------------------------
def search_policy(query, top_k=2):
    """
    Performs semantic search against ChromaDB to retrieve relevant policy chunks.
    """
    collection = chroma_client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef
    )

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    print(f"\n--- Search Query: '{query}' ---")
    for i in range(len(results["documents"][0])):
        doc_text = results["documents"][0][i]
        meta = results["metadatas"][0][i]
        
        # Fixed formatting logic for distance
        distance_val = results["distances"][0][i] if "distances" in results and results["distances"] else None
        dist_str = f"{distance_val:.4f}" if distance_val is not None else "N/A"
        
        print(f"\n[Result {i+1}] (ID: {results['ids'][0][i]} | Distance: {dist_str})")
        print(f"Title: {meta.get('title')}")
        print(f"Content:\n{doc_text}")

    return results

# -----------------------------------------------------------------------------
# Execution Verification
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("TASK 4: CHROMADB VECTOR DATABASE SETUP")
    print("=" * 60)

    # Step 1: Build Database
    build_vector_database()

    # Step 2: Test Semantic Search
    search_policy("What is the penalty for overdue invoices past 30 days?")
    search_policy("How do we handle invoice disputes?")