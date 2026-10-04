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


📖 AI Accounts Receivable Assistant — Deep Dive Architecture & Operational Manual📌 Executive Summary & Business ImpactThe Problem in Enterprise Accounts Receivable (AR)In corporate finance operations, Accounts Receivable teams face two distinct data silos that hinder efficiency and delay cash collection:Structured Financial Data: Recorded in relational ERP systems or databases (e.g., SQLite, PostgreSQL, SAP). This includes invoice numbers, due dates, outstanding amounts, and payment histories.Unstructured Credit & Collection Policies: Documented in PDFs, Word files, and internal handbooks. This includes credit terms, late payment interest schedules, escalation steps, and legal action thresholds.How Traditional Systems FailManual Cross-Referencing: A financial collector inquiring about an overdue account must manually pull up the customer's balance in an ERP system, open a separate policy PDF, manually calculate days past due, and locate the matching escalation clause.Rigid Dashboarding: Standard dashboards show raw numbers but cannot answer dynamic questions like "Which customers are past due beyond Level 2 escalation and need immediate legal notices?"Human Error & Delay: Manual review leads to missed follow-ups, inconsistent fee applications, and prolonged Days Sales Outstanding (DSO).The Solution: Hybrid Agentic AI SystemThe AI Accounts Receivable Assistant solves this by bridging structured SQL data and unstructured vector documents into a unified conversational intelligence engine. By combining SQL Query Generation with Retrieval-Augmented Generation (RAG) under a central router, financial teams can ask natural-language questions and receive grounded, accurate answers backed by database records and company policy.🏗️ End-to-End System Architecture & Data Flow                                    +-----------------------+
                                    |   React + Vite UI     |
                                    | (Tailwind v4 / Chat)  |
                                    +-----------+-----------+
                                                |
                                    HTTP POST /assistant/query
                                                |
                                                v
                                    +-----------------------+
                                    |   FastAPI Gateway     |
                                    +-----------+-----------+
                                                |
                                                v
                                    +-----------------------+
                                    |  Orchestrator Router  |
                                    | (Intent Classifier)   |
                                    +---+-------+-------+---+
                                        |       |       |
                 +----------------------+       |       +----------------------+
                 | (Structured Intent)          | (Hybrid Intent)              | (Unstructured Intent)
                 v                              v                              v
      +--------------------+         +--------------------+         +--------------------+
      |  SQL Executor Node |         |    Hybrid Node     |         | Vector Search Node |
      |  (Text-to-SQL)     |         |  (SQL + Vector)    |         | (ChromaDB / RAG)   |
      +---------+----------+         +---------+----------+         +---------+----------+
                |                              |                              |
                v                              v                              v
      +--------------------+         +--------------------+         +--------------------+
      | SQLite DB          |         | DB + ChromaDB      |         | ChromaDB           |
      | (finance.db)       |         | Combined Context   |         | (Vector Store)     |
      +---------+----------+         +---------+----------+         +---------+----------+
                |                              |                              |
                +------------------------------+------------------------------+
                                                |
                                                v
                                    +-----------------------+
                                    | LLM Response Synthesizer |
                                    | (gemma-4-26b-it)      |
                                    +-----------+-----------+
                                                |
                                    Markdown Formatted Payload
                                                |
                                                v
                                    +-----------------------+
                                    |   React Markdown UI   |
                                    +-----------------------+
🧠 Key LLM & AI Concepts (Simplified with Examples)1. Vector EmbeddingsWhat it is: Vector embedding converts text (words, sentences, documents) into mathematical arrays of floating-point numbers (dense vectors). These vectors place semantically similar ideas close to each other in high-dimensional space.Analogy: Think of a 3D grid where words are placed by meaning rather than spelling. "Dog" and "Puppy" sit right next to each other, while "Computer" is far away.Example:Phrase A: "Fee for late payment" $\rightarrow$ Vector: [0.12, -0.85, 0.43, ...]Phrase B: "Overdue interest charge" $\rightarrow$ Vector: [0.14, -0.82, 0.41, ...]Even though Phrase A and Phrase B share zero words in common, their vector distance is almost zero because their business meanings match.2. ChunkingWhat it is: Breaking long policy documents (e.g., a 20-page PDF) into smaller, manageable blocks of text (e.g., 500 characters) with overlapping margins before storing them in a vector database.Why it matters: Large Language Models have context limits and perform better when fed precise, concise context rather than full documents.3. Retrieval-Augmented Generation (RAG)What it is: A technique that enhances LLM generation by retrieving real-time external facts from a vector database before letting the model draft an answer.Analogy: Taking an open-book exam vs. a closed-book exam. Instead of relying solely on what the LLM learned during pre-training (closed book), RAG lets the LLM read company policies in real time (open book).Example Process:User asks: "When does Level 2 escalation start?"System converts the question into a vector embedding.ChromaDB performs a similarity search and retrieves: "Level 2 Escalation occurs when an account is 46–60 days past due."The LLM receives the question + retrieved excerpt and writes the final answer.4. Intent Classification & RoutingWhat it is: An intelligent node that analyzes the user's prompt and decides which system components are required to fulfill the request.Routes:SQL_ONLY: For quantitative questions requiring exact calculation (e.g., "What is the total balance owed?").RAG_ONLY: For textual policy inquiries (e.g., "What are payment terms?").HYBRID: For reasoning tasks combining database records and text policies (e.g., "Which collection policy applies to Client I Corp?").🔬 Tech Stack Deep Dive: Why We Used It, Pros & ConsTechnologyWhat it isWhy We Used ItProsConsFastAPIPython REST API frameworkLightweight, highly scalable, asynchronous native support for AI pipelines.• Blazing fast performance.• Automatic OpenAPI/Swagger UI generation.• Clean integration with Python LLM libraries.• Requires manual async architecture planning for heavy CPU tasks.SQLite (finance.db)Embedded SQL Relational DatabaseZero-configuration database for structured transaction and customer records.• Zero overhead setup.• Native Python support.• Instant query execution.• Limited concurrent write scalability compared to PostgreSQL.ChromaDBLocal Vector DatabaseStores embedding vectors and metadata locally without cloud infrastructure dependencies.• Fully open-source and local.• Simple API.• No external database subscription required.• Best suited for small-to-medium dataset collections; requires indexing adjustments at massive enterprise scale.Local LLM (gemma-4-26b-it)26B-parameter Instruction ModelPerforms SQL generation, policy reasoning, and response generation securely.• High data privacy (data stays local).• Zero API cost per token.• Strong instruction-following capability.• Requires local CPU/GPU RAM resources.React + ViteModern Frontend FrameworkDelivers rapid development cycles and responsive user interfaces.• Instant hot module replacement (HMR).• Clean component structure.• Minimal bundle size.• Client-side routing/state management requires upfront organization.Tailwind CSS v4Utility-first CSS frameworkRapid interface styling and typography controls.• Fast design workflow.• Built-in responsive breakpoints.• Clean typography styling via @tailwindcss/typography.• Utility classes can clutter HTML/JSX if unorganized.React MarkdownReact component for parsing MarkdownRenders raw LLM text outputs (tables, lists, headers) as clean HTML elements.• Formats complex LLM tables cleanly.• Prevents raw ### or `` strings from cluttering UI.🛠️ Complete Technical Execution PipelineStep 1: User Request LifecycleUser Types Query: Client types "What is the policy for late payment fees?" in React (localhost:5173).Axios POST: Request sent to FastAPI (localhost:8000/assistant/query).Intent Classification: Router evaluates prompt intent $\rightarrow$ maps to RAG_ONLY.Embedding Query: Query string converted to vector representation.Vector Search: ChromaDB returns top $k$ matching chunks from /data/chroma_db.LLM Prompt Synthesis: System prompt constructed:Context: [Retrieved ChromaDB Chunk: "1.5% late fee per month applies after 45 days"]
User Question: "What is the policy for late payment fees?"
Instructions: Answer concisely using Markdown formatting.
LLM Execution: Model generates structured Markdown response.Frontend Render: react-markdown converts response to styled HTML tags.🚀 Step-by-Step Execution GuidePrerequisitesPython 3.10 or higherNode.js 18+ and npmGitBackend Operations# Navigate to project root
cd D:\AashishDev\RAG_POC\first_rag_poc

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn langchain chromadb sqlite3 pydantic

# Launch backend server
uvicorn main:app --reload --port 8000
Backend API: http://localhost:8000Interactive API Documentation (Swagger): http://localhost:8000/docsFrontend Operations# Open a secondary terminal
cd D:\AashishDev\RAG_POC\first_rag_poc\frontend

# Install dependencies
npm install

# Start development server
npm run dev
Frontend Application UI: http://localhost:5173🧪 Comprehensive Verification & Test SuiteRun these test queries in your chat window to verify system capabilities:#Test PromptRouting PathExpected Verification1What is the total outstanding amount across all customers?SQL_ONLYReturns $59,625 (Exact database aggregate SUM).2Which customers have overdue invoices?SQL_ONLYDisplays table listing Client I Corp, Client J Corp, and Client A Corp with invoice amounts and days overdue.3What is the policy for late payment fees?RAG_ONLYRetrieves policy stating 1.5% per month (18% annually) fee during Level 2 Escalation (46–60 days).4What is the policy for invoices overdue by more than 60 days?RAG_ONLYReturns Level 3 Escalation protocol (collections process, credit hold, legal notice).5What action should be taken for Client I Corp based on its overdue invoices and company policy?HYBRIDFetches Client I Corp's overdue status (14 days past due) and recommends Level 1 Soft Reminder.6Generate a payment reminder for Client I Corp for their overdue invoice.HYBRIDGenerates a professionally drafted email template populated with Invoice #1009 ($2,150.00) details.🔒 Security, Maintenance & Git WorkflowFile Exclusion Strategy (.gitignore)Heavy binary artifacts, virtual environments, and build outputs are strictly excluded from version control to maintain a lightweight repository:node_modules/ and frontend/node_modules/Virtual environments (venv/, .venv/)Local vector stores and database binaries (data/chroma_db/, *.bin, *.sqlite3)Environment variable secrets (.env)Pushing Code UpdatesTo sync changes with GitHub:git add .
git commit -m "Update documentation and application configuration"
git push origin main
