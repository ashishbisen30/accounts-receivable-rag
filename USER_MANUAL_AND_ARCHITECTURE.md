================================================================================
AI ACCOUNTS RECEIVABLE ASSISTANT — COMPLETE MANUAL & ARCHITECTURE GUIDE[cite: 1]
================================================================================

--------------------------------------------------------------------------------
1. EXECUTIVE SUMMARY & BUSINESS IMPACT[cite: 1]
--------------------------------------------------------------------------------

The Problem in Enterprise Accounts Receivable (AR):[cite: 1]
In corporate finance operations, Accounts Receivable teams face two distinct 
data silos that hinder efficiency and delay cash collection[cite: 1]:

1. Structured Financial Data: Recorded in relational ERP systems or databases 
   (e.g., SQLite, PostgreSQL, SAP)[cite: 1]. This includes invoice numbers, due dates, 
   outstanding amounts, and payment histories[cite: 1].
2. Unstructured Credit & Collection Policies: Documented in PDFs, Word files, 
   and internal handbooks[cite: 1]. This includes credit terms, late payment interest 
   schedules, escalation steps, and legal action thresholds[cite: 1].

How Traditional Systems Fail:[cite: 1]
- Manual Cross-Referencing: A financial collector inquiring about an overdue 
  account must manually pull up the customer's balance in an ERP system, open 
  a separate policy PDF, manually calculate days past due, and locate the 
  matching escalation clause[cite: 1].
- Rigid Dashboarding: Standard dashboards show raw numbers but cannot answer 
  dynamic questions like "Which customers are past due beyond Level 2 escalation 
  and need immediate legal notices?"[cite: 1]
- Human Error & Delay: Manual review leads to missed follow-ups, inconsistent 
  fee applications, and prolonged Days Sales Outstanding (DSO)[cite: 1].

The Solution: Hybrid Agentic AI System:[cite: 1]
The AI Accounts Receivable Assistant solves this by bridging structured SQL 
data and unstructured vector documents into a unified conversational intelligence 
engine[cite: 1]. By combining SQL Query Generation with Retrieval-Augmented Generation 
(RAG) under a central router, financial teams can ask natural-language questions 
and receive grounded, accurate answers backed by database records and company policy[cite: 1].


--------------------------------------------------------------------------------
2. TECH STACK: WHAT WE USED & WHY[cite: 1]
--------------------------------------------------------------------------------

1. Backend Framework: FastAPI (Python)[cite: 1]
   - Why We Used It: High performance, automatic OpenAPI (Swagger) documentation, 
     asynchronous execution, and seamless integration with Python AI libraries[cite: 1].
   - Role: Serves REST API endpoints (/customers/summary, /invoices/overdue, 
     /assistant/query) to bridge the UI with the DB and AI models[cite: 1].

2. Relational Database: SQLite (finance.db)[cite: 1]
   - Why We Used It: Lightweight, zero-configuration serverless SQL database 
     ideal for local development, fast query execution, and structured tracking[cite: 1].
   - Role: Stores structured AR data, including customer profiles, outstanding 
     balances, invoice details, and overdue payment statuses[cite: 1].

3. Vector Database: ChromaDB (/data/chroma_db)[cite: 1]
   - Why We Used It: Open-source, local-first vector database optimized for 
     similarity search and fast retrieval without external cloud infrastructure[cite: 1].
   - Role: Stores chunked and embedded policy documents (late payment fees, 
     escalation rules, collections procedures) to support RAG[cite: 1].

4. LLM Orchestration: Local LLM (gemma-4-26b-it) + LangChain / LangGraph[cite: 1]
   - Why We Used It: Secure, privacy-focused local intelligence without sending 
     sensitive corporate financial records to public cloud APIs[cite: 1].
   - Role: Dynamically routes prompts to execute SQL queries, retrieve policy 
     text from ChromaDB, or perform hybrid reasoning across both sources[cite: 1].

5. Frontend Framework: React + Vite + Tailwind CSS v4[cite: 1]
   - Why We Used It: Vite delivers instant server startup and Hot Module 
     Replacement (HMR)[cite: 1]. Tailwind CSS provides utility-first styling for 
     modern UI development[cite: 1].
   - Role: Displays dynamic KPI dashboard cards, customer balance tables, and 
     an interactive chat drawer[cite: 1].

6. Markdown Renderer: react-markdown + @tailwindcss/typography[cite: 1]
   - Why We Used It: LLMs naturally generate structured text containing headers, 
     bold markers, and tables[cite: 1].
   - Role: Translates raw Markdown response strings into clean, styled HTML 
     tables and text elements inside the chat UI[cite: 1].


--------------------------------------------------------------------------------
3. END-TO-END SYSTEM ARCHITECTURE & DATA FLOW[cite: 1]
--------------------------------------------------------------------------------

                                    +-----------------------+
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


--------------------------------------------------------------------------------
4. KEY LLM & AI CONCEPTS (SIMPLIFIED WITH EXAMPLES)[cite: 1]
--------------------------------------------------------------------------------

1. Vector Embeddings:[cite: 1]
   - What it is: Vector embedding converts text (words, sentences, documents) 
     into mathematical arrays of floating-point numbers (dense vectors)[cite: 1]. These 
     vectors place semantically similar ideas close to each other in 
     high-dimensional space[cite: 1].
   - Analogy: Think of a 3D grid where words are placed by meaning rather than 
     spelling[cite: 1]. "Dog" and "Puppy" sit right next to each other, while "Computer" 
     is far away[cite: 1].
   - Example:
     Phrase A: "Fee for late payment" -> Vector: [0.12, -0.85, 0.43, ...][cite: 1]
     Phrase B: "Overdue interest charge" -> Vector: [0.14, -0.82, 0.41, ...][cite: 1]
     (Even though Phrase A and B share zero words in common, their vector 
     distance is almost zero because their business meanings match.)[cite: 1]

2. Chunking & Overlap:[cite: 1]
   - What it is: Breaking long policy documents (e.g., a 20-page PDF) into 
     smaller, manageable blocks of text (e.g., 500 characters) with overlapping 
     margins before storing them in a vector database[cite: 1].
   - Why it matters: LLMs have context limits and perform better when fed 
     precise, concise context rather than full documents[cite: 1]. Overlapping prevents 
     critical policy rules from being split across boundaries.

3. Cosine Similarity & Vector Search:
   - What it is: The mathematical distance metric used by ChromaDB to measure 
     the cosine of the angle between two vectors (the user question vector and 
     stored document vectors).
   - How it works: A similarity score close to 1.0 indicates that the semantic 
     meaning of the retrieved policy document closely answers the user's intent.

4. Retrieval-Augmented Generation (RAG):[cite: 1]
   - What it is: A technique that enhances LLM generation by retrieving 
     real-time external facts from a vector database before letting the model 
     draft an answer[cite: 1].
   - Analogy: Taking an open-book exam vs. a closed-book exam[cite: 1]. Instead of 
     relying solely on what the LLM learned during pre-training (closed book), 
     RAG lets the LLM read company policies in real time (open book)[cite: 1].
   - Example Process:
     1. User asks: "When does Level 2 escalation start?"[cite: 1]
     2. System converts the question into a vector embedding[cite: 1].
     3. ChromaDB performs a similarity search and retrieves: "Level 2 Escalation 
        occurs when an account is 46-60 days past due."[cite: 1]
     4. The LLM receives the question + retrieved excerpt and writes the final answer[cite: 1].

5. Text-to-SQL (Structured Query Generation):
   - What it is: The ability of the LLM to inspect the SQLite database schema 
     and convert natural language prompts directly into standard SQL queries 
     (e.g., SELECT SUM(outstanding_balance) FROM customers).
   - Safety Mechanism: SQL execution is constrained to read-only SELECT 
     statements to ensure zero accidental modification or deletion of 
     financial records.

6. Intent Classification & Routing:[cite: 1]
   - What it is: An intelligent node powered by LangGraph that analyzes the 
     user's prompt and decides which system components are required to fulfill 
     the request[cite: 1].
   - Routes:
     - SQL_ONLY: For quantitative questions requiring exact calculation[cite: 1].
     - RAG_ONLY: For textual policy inquiries[cite: 1].
     - HYBRID: For reasoning tasks combining database records and text policies[cite: 1].

7. Prompt Engineering & Grounding:
   - What it is: Designing strict system prompts that instruct the LLM to base 
     its response strictly on retrieved facts rather than making up 
     information (hallucination).


--------------------------------------------------------------------------------
5. TECH STACK DEEP DIVE: PROS & CONS[cite: 1]
--------------------------------------------------------------------------------

1. FastAPI[cite: 1]
   - Pros: Blazing fast performance; automatic OpenAPI/Swagger UI generation; 
     clean integration with Python LLM libraries[cite: 1].
   - Cons: Requires manual async architecture planning for heavy CPU tasks[cite: 1].

2. SQLite (finance.db)[cite: 1]
   - Pros: Zero overhead setup; native Python support; instant query execution[cite: 1].
   - Cons: Limited concurrent write scalability compared to PostgreSQL[cite: 1].

3. ChromaDB[cite: 1]
   - Pros: Fully open-source and local; simple API; no external database 
     subscription required[cite: 1].
   - Cons: Requires indexing adjustments at massive enterprise scale[cite: 1].

4. Local LLM (gemma-4-26b-it)[cite: 1]
   - Pros: High data privacy (data stays local); zero API cost per token; strong 
     instruction-following capability[cite: 1].
   - Cons: Requires local CPU/GPU RAM resources[cite: 1].

5. React + Vite[cite: 1]
   - Pros: Instant hot module replacement (HMR); clean component structure; 
     minimal bundle size[cite: 1].
   - Cons: Client-side routing/state management requires upfront organization[cite: 1].

6. Tailwind CSS v4[cite: 1]
   - Pros: Fast design workflow; built-in responsive breakpoints; clean 
     typography styling via @tailwindcss/typography[cite: 1].
   - Cons: Utility classes can clutter HTML/JSX if unorganized[cite: 1].

7. React Markdown[cite: 1]
   - Pros: Formats complex LLM tables cleanly; prevents raw Markdown strings 
     from cluttering the UI[cite: 1].
   - Cons: Requires typography CSS setup for proper table borders.


--------------------------------------------------------------------------------
6. COMPLETE TECHNICAL EXECUTION PIPELINE[cite: 1]
--------------------------------------------------------------------------------

Step 1: User Request Lifecycle[cite: 1]
1. User Types Query: Client types "What is the policy for late payment fees?" 
   in React (localhost:5173)[cite: 1].
2. Axios POST: Request sent to FastAPI (localhost:8000/assistant/query)[cite: 1].
3. Intent Classification: Router evaluates prompt intent -> maps to RAG_ONLY[cite: 1].
4. Embedding Query: Query string converted to vector representation[cite: 1].
5. Vector Search: ChromaDB returns top k matching chunks from /data/chroma_db[cite: 1].
6. LLM Prompt Synthesis: System prompt constructed[cite: 1]:
   Context: [Retrieved ChromaDB Chunk: "1.5% late fee per month applies after 45 days"][cite: 1]
   User Question: "What is the policy for late payment fees?"[cite: 1]
   Instructions: Answer concisely using Markdown formatting[cite: 1].
7. LLM Execution: Model generates structured Markdown response[cite: 1].
8. Frontend Render: react-markdown converts response to styled HTML tags[cite: 1].


--------------------------------------------------------------------------------
7. STEP-BY-STEP EXECUTION GUIDE[cite: 1]
--------------------------------------------------------------------------------

Prerequisites:[cite: 1]
- Python 3.10 or higher[cite: 1]
- Node.js 18+ and npm[cite: 1]
- Git[cite: 1]

Backend Operations:[cite: 1]
  cd D:\AashishDev\RAG_POC\first_rag_poc
  .\venv\Scripts\activate
  pip install fastapi uvicorn langchain chromadb sqlite3 pydantic
  uvicorn main:app --reload --port 8000

  - Backend API: http://localhost:8000[cite: 1]
  - Swagger Documentation: http://localhost:8000/docs[cite: 1]

Frontend Operations:[cite: 1]
  cd D:\AashishDev\RAG_POC\first_rag_poc\frontend
  npm install
  npm run dev

  - Frontend Application UI: http://localhost:5173[cite: 1]


--------------------------------------------------------------------------------
8. HOW TO USE THE AI FINANCIAL ASSISTANT[cite: 1]
--------------------------------------------------------------------------------

1. Executive Dashboard Navigation:[cite: 1]
   - KPI Metrics: View instant summary cards for Total Outstanding Balance, 
     Overdue Amount, and Total Active Customers[cite: 1].
   - Customer Table: Review individual customer balances, overdue totals, and 
     status indicators[cite: 1].

2. Interacting with the AI Chat:[cite: 1]
   - Type natural language questions into the AI Financial Assistant input box 
     at the bottom right[cite: 1].


--------------------------------------------------------------------------------
9. COMPREHENSIVE VERIFICATION & TEST SUITE[cite: 1]
--------------------------------------------------------------------------------

Test Prompt 1: "What is the total outstanding amount across all customers?"[cite: 1]
- Route Path: SQL_ONLY[cite: 1]
- Expected Verification: Returns $59,625 (Exact database aggregate SUM()).[cite: 1]

Test Prompt 2: "Which customers have overdue invoices?"[cite: 1]
- Route Path: SQL_ONLY[cite: 1]
- Expected Verification: Displays table listing Client I Corp, Client J Corp, 
  and Client A Corp with invoice amounts and days overdue[cite: 1].

Test Prompt 3: "What is the policy for late payment fees?"[cite: 1]
- Route Path: RAG_ONLY[cite: 1]
- Expected Verification: Retrieves policy stating 1.5% per month (18% annually) 
  fee during Level 2 Escalation (46-60 days)[cite: 1].

Test Prompt 4: "What is the policy for invoices overdue by more than 60 days?"[cite: 1]
- Route Path: RAG_ONLY[cite: 1]
- Expected Verification: Returns Level 3 Escalation protocol (collections 
  process, credit hold, legal notice)[cite: 1].

Test Prompt 5: "What action should be taken for Client I Corp based on its overdue invoices and company policy?"[cite: 1]
- Route Path: HYBRID[cite: 1]
- Expected Verification: Fetches Client I Corp's overdue status (14 days past 
  due) and recommends Level 1 Soft Reminder[cite: 1].

Test Prompt 6: "Generate a payment reminder for Client I Corp for their overdue invoice."[cite: 1]
- Route Path: HYBRID[cite: 1]
- Expected Verification: Generates a professionally drafted email template 
  populated with Invoice #1009 ($2,150.00) details[cite: 1].


--------------------------------------------------------------------------------
10. SECURITY, MAINTENANCE & GIT WORKFLOW[cite: 1]
--------------------------------------------------------------------------------

File Exclusion Strategy (.gitignore):[cite: 1]
Heavy binary artifacts, virtual environments, and build outputs are strictly 
excluded from version control[cite: 1]:
- node_modules/ and frontend/node_modules/[cite: 1]
- Virtual environments (venv/, .venv/)[cite: 1]
- Local vector stores and database binaries (data/chroma_db/, *.bin, *.sqlite3)[cite: 1]
- Environment variable secrets (.env)[cite: 1]

Pushing Code Updates:[cite: 1]
  git add USER_MANUAL_AND_ARCHITECTURE.md
  git commit -m "Update comprehensive documentation with complete architecture and execution guide"
  git push origin main