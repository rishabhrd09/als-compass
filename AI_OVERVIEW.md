# ALS Caregiver's Compass - System Architecture, AI Flow & Database Schema

This document serves as the "System Bible," providing a deep-dive comprehensive technical overview of the ALS Caregiver's Compass platform. It details the end-to-end data flow, technology stack, file responsibilities, Generative AI concepts, and the specific mechanics of the Vector Database (ChromaDB) integration.

---

## 1. Technology Stack

### Backend Core
- **Python 3.x**: Primary language for robust AI/ML capabilities.
- **Flask**: Micro-framework handling HTTP requests, routing, and serving as the bridge between UI and AI logic.
- **Werkzeug**: Handling lower-level WSGI details for the web server.

### AI & Logic Layer
- **Unified AI System**: Custom class (`UnifiedAISystem`) abstracting interactions with multiple AI providers.
- **Multi-Provider Support**: Integrated SDKs for **OpenAI (GPT-4)**, **Google Gemini**, and **Anthropic (Claude 3)**.
- **Agentic Design Pattern**: Uses a "ReAct-lite" approach for intelligent response generation.
- **LangChain (Implicit/Explicit)**: utilized for chain management and retrieval logic.
- **ChromaDB**: The **Vector Database** used for storing and retrieving high-dimensional embeddings of our knowledge base.

### Frontend
- **HTML5 & Jinja2**: Server-side rendering for dynamic content injection.
- **Vanilla JavaScript**: Lightweight client-side interactivity.
- **Custom CSS3**: "Claude-style" minimalist aesthetic design system.

### Data Layer
- **JSON Data Store**: Structured files (`als_community_faq.json`) for structured, editable content.
- **ChromaDB (Vector Store)**: for semantic search and Retrieval Augmented Generation (RAG).

---

## 2. End-to-End Chatbot Flow (Browser to DB to LLM)

This detailed flow explains exactly what happens when a user asks a question.

**The Journey of a Query:**

1.  **User Input (Browser)**:
    *   User types: *"What are the warning signs for BiPAP?"* on `ai_assistant.html`.
    *   JavaScript captures this and sends a `POST` request to `/api/ai-assistant`.

2.  **Flask Reception (`app.py`)**:
    *   The route receives the JSON payload.
    *   It initializes the `UnifiedAISystem` (or uses the active session instance).

3.  **Knowledge Retrieval (The "R" in RAG)**:
    *   **Embedding**: The system takes the user's query ("warning signs for BiPAP") and uses an embedding model (e.g., `text-embedding-3-small` or `feature-extraction`) to convert it into a vector (a list of numbers representing meaning).
    *   **ChromaDB Query**: This vector is sent to **ChromaDB**.
    *   **Semantic Search**: ChromaDB calculates the "distance" (similarity) between the query vector and all stored document vectors.
    *   **Retrieval**: It returns the top `k` (e.g., 3-5) most relevant chunks of text. *Example return: "BiPAP Warning Signs: Morning headaches, inability to sleep flat..."*

4.  **Prompt Construction (`ai_system_unified.py`)**:
    *   The system constructs a **System Prompt**.
    *   **Context Injection**: It appends the retrieved text from ChromaDB into the prompt.
    *   *Prompt looks like:*
        > "You are an expert ALS assistant. Use this context to answer: [BiPAP Warning Signs context...]. User Question: What are the warning signs for BiPAP?"

5.  **LLM Inference (The "G" in RAG)**:
    *   This enriched prompt is sent to the LLM (OpenAI/Gemini/Claude).
    *   The LLM generates an answer based *specifically* on the injected context, minimizing hallucinations.

6.  **Response Delivery**:
    *   The LLM's text response is parsed by Python.
    *   Flask wraps it in JSON and sends it back to the browser.
    *   Frontend JavaScript renders the answer bubble.

---

## 3. Database Architecture & ChromaDB Schema

### How the Database is populated (`manage_research.py` / `ingest.py`)

We do **not** manually type into the database. We use an **Ingestion Pipeline**:

1.  **Source Data**: We start with raw files:
    *   `data/als_community_faq.json` (Structured Q&A)
    *   `data/research_updates.json` (Trials info)
    *   PDFs/Text files (Unstructured protocols)

2.  **Chunking**:
    *   The ingestion script reads these files.
    *   It splits long text into smaller "chunks" (e.g., 500-1000 characters). This ensures we retrieve specific answer paragraphs, not whole books.

3.  **Embedding**:
    *   Each chunk is passed through an Embedding Model to create a vector.

4.  **Storage in ChromaDB**:
    *   We create a **Collection** (like a table in SQL) named `als_knowledge_base`.
    *   **Schema of a Stored Item**:
        *   **`ids`**: Unique ID (e.g., "faq_resp_1")
        *   **`embeddings`**: [0.12, -0.45, 0.88, ...] (The vector)
        *   **`documents`**: "BiPAP is needed when SpO2 drops..." (The actual text content)
        *   **`metadatas`**: `{"source": "als_community_faq.json", "category": "respiratory"}` (Tags for filtering)

### What Data We Capture
*   **Medical Protocols**: Steps for emergency intervention.
*   **Equipment Costs**: Specific INR pricing for India context.
*   **Community Wisdom**: "Soft" knowledge derived from caregiver chats (e.g., "how to convince a patient").
*   **Research News**: Summaries of recent trials.

---

## 4. Key File Explanations (Responsibility & Connections)

*   **`app.py`**
    *   **Role**: The central coordinator. It runs the server, handles URL routing (who sees what page), and manages the user's "Session" (memory of the current chat).
    *   **Connection**: Imports the `UnifiedAISystem` class to process intelligence; reads `json` files to render static pages.

*   **`ai_system_unified.py`**
    *   **Role**: The "Brain" wrapper. It standardizes the different "languages" of OpenAI, Gemini, and Claude so `app.py` doesn't strictly care which model is running. It handles the API keys and error recovery.
    *   **Connection**: Called by `app.py`; calls the LLM provider APIs.

*   **`ai_system_agentic.py`** (Concept/Advanced)
    *   **Role**: The "Planner". Unlike the unified system which is reactive (Input->Output), this system can "think" in steps (Plan -> Execute -> Reflect). Used for complex, multi-step user queries.
    *   **Connection**: Can be swapped in by `app.py` for "Pro" mode.

*   **`manage_research.py` / `create_db.py`** (The Ingestion Engines)
    *   **Role**: The "Librarian". These scripts run *offline* (not during chat). They read the PDF/JSON source content, chunk it, embed it, and save it into the ChromaDB folder (`chroma_db/`).
    *   **Connection**: Populates the database that `ai_system_unified.py` queries.

*   **`templates/emergency_protocol.html`**
    *   **Role**: Critical visualization. Uses pure CSS/HTML to draw the decision trees (Flowcharts) for respiratory failure.
    *   **Connection**: Rendered by `app.py`; links to `base.html` for layout.

*   **`data/als_community_faq.json`**
    *   **Role**: The "Gold Standard" knowledge. Editable text file containing verified Q&A.
    *   **Connection**: Read by `manage_research.py` to be put into the AI's brain; read by `app.py` to be shown on the FAQ webpage.

---

## 5. Overview of Concepts

1.  **Generative AI**: Using models (LLMs) to create new text based on patterns learned from vast internet data.
2.  **RAG (Retrieval Augmented Generation)**: The technique of *forcing* the Generative AI to look at our specific notes (ChromaDB) before answering, ensuring accuracy over creativity.
3.  **Embeddings**: Translating text into numbers so computers can understand "concept similarity" (e.g., understanding that "trouble breathing" and "dyspnea" are related concepts) rather than just keyword matching.
4.  **Vector Database**: A specialized database (ChromaDB) designed specifically to search these number-lists (vectors) extremely fast.
