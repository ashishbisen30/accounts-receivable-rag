📖 AI Accounts Receivable Assistant — Complete Manual & Architecture Guide

📌 Overview

The AI Accounts Receivable (AR) Assistant is an enterprise-grade financial management platform that combines structured accounting data with unstructured company policies. It provides a real-time financial KPI dashboard and a hybrid AI chat assistant capable of answering database queries (SQL) and policy questions (RAG) in real time.

🛠️ Tech Stack: What We Used & Why

1. Backend Framework: FastAPI (Python)

Why We Used It: FastAPI provides high performance, automatic OpenAPI (Swagger) documentation, asynchronous execution, and seamless integration with Python-based AI/ML libraries.

Role: Serves REST API endpoints (/customers/summary, /invoices/overdue, /assistant/query) to bridge the React frontend with the database and AI models.

2. Relational Database: SQLite (finance.db)

Why We Used It: A lightweight, serverless SQL database ideal for local development, fast query execution, and accurate structured financial tracking.

Role: Stores structured accounts receivable data, including customer profiles, outstanding balances, invoice details, and overdue payment statuses.

3. Vector Database: ChromaDB (/data/chroma_db)

Why We Used It: ChromaDB is an open-source, local-first vector database optimized for AI similarity search and fast retrieval without requiring external cloud infrastructure.

Role: Stores chunked and embedded policy documents (late payment fees, escalation rules, collections procedures) to support Retrieval-Augmented Generation (RAG).

4. Language Model & Orchestration: Local LLM (gemma-4-26b-it) + LangChain / LangGraph

Why We Used It: Offers secure, privacy-focused local intelligence without sending sensitive corporate financial records to public cloud APIs.

Role: LangGraph/LangChain dynamically routes user prompts to execute SQL database queries, retrieve policy text from ChromaDB, or perform hybrid reasoning across both sources.

5. Frontend Framework: React + Vite + Tailwind CSS v4

Why We Used It: Vite delivers instant server startup and Hot Module Replacement (HMR). Tailwind CSS provides utility-first styling for quick, modern UI development.

Role: Displays KPI dashboard cards, customer balance tables, and an interactive chat drawer.

6. Markdown Renderer: react-markdown + @tailwindcss/typography

Why We Used It: LLMs naturally generate structured text containing headers (###), bold markers (**), and tables (| ... |).

Role: Translates raw Markdown response strings into clean, styled HTML tables and text elements inside the chat UI.

🗺️ System Architecture & Responsibilities

                                +-------------------+
                                |  React Frontend   |
                                |  (Port 5173 / UI) |
                                +---------+---------+
                                          |
                                    REST API (Axios)
                                          |
                                          v
                                +-------------------+
                                |  FastAPI Backend  |
                                |  (Port 8000 / API)|
                                +---------+---------+
                                          |
                       +------------------+------------------+
                       |                                     |
                       v                                     v
             +------------------+                  +-------------------+
             | SQLite DB        |                  | ChromaDB          |
             | (finance.db)     |                  | (Vector Store)    |
             | Structured SQL   |                  | Unstructured RAG  |
             +------------------+                  +-------------------+


🚀 Step-by-Step Guide: How to Run the Application

1. Prerequisites

Ensure you have the following installed on your machine:

Python 3.10+

Node.js 18+ and npm

Git

2. Backend Setup & Run

Open a terminal and navigate to the root directory:

cd D:\AashishDev\RAG_POC\first_rag_poc


Create and activate a Python virtual environment:

python -m venv venv
.\venv\Scripts\activate


Install required Python packages:

pip install fastapi uvicorn langchain chromadb sqlite3 pydantic


Launch the FastAPI server:

uvicorn main:app --reload --port 8000


Backend URL: http://localhost:8000

Swagger API Docs: http://localhost:8000/docs

3. Frontend Setup & Run

Open a second terminal and navigate to the frontend folder:

cd D:\AashishDev\RAG_POC\first_rag_poc\frontend


Install Node dependencies:

npm install


Start the Vite development server:

npm run dev


Open your browser and go to:

http://localhost:5173


💡 How to Use the AI Financial Assistant

1. Executive Dashboard Navigation

KPI Metrics: View instant summary cards for Total Outstanding Balance, Overdue Amount, and Total Active Customers.

Customer Table: Review individual customer balances, overdue totals, and status indicators.

2. Interacting with the AI Chat

Type natural language questions into the AI Financial Assistant input box at the bottom right.

Sample Queries by Domain:

Database Queries (SQL):

"What is the total outstanding amount across all customers?"

"Which customers have overdue invoices?"

Policy Queries (RAG):

"What is the policy for late payment fees?"

"What is the policy for invoices overdue by more than 60 days?"

Cross-Domain / Action Queries (Hybrid):

"What action should be taken for Client I Corp based on its overdue invoices and company policy?"

"Generate a payment reminder for Client I Corp for their overdue invoice."