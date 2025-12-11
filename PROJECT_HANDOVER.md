# ALS Caregiver's Compass - Project Handover Summary

**Date**: 2025-12-11
**Status**: Production-Ready Prototype (Local)
**Version**: 1.0.0

## 1. Project Overview
A full-stack web application providing AI-powered assistance to ALS caregivers. It features a RAG (Retrieval-Augmented Generation) system that combines trusted medical data with community experiences (e.g., WhatsApp logs) to provide accurate, empathetic, and sourced answers.

## 2. Architecture & Tech Stack
*   **Backend**: Flask (Python 3.11+)
*   **Database**: ChromaDB (Vector Store for AI memory)
*   **AI Engine**: OpenAI (GPT-4o-mini)
*   **Frontend**: HTML5, Vanilla CSS (Responsive, Modern Design)
*   **Privacy**: Automatic PII scrubbing for community data.

## 3. Critical Dependencies (Versions)
We explicitly pinned these versions to ensure stability and compatibility:
*   `numpy<2.0` (Fixed 2.0 incompatibility with ChromaDB)
*   `openai>=1.55.0` (Fixed `proxies` argument conflict with new `httpx`)
*   `chromadb==0.4.18`
*   `sentence-transformers==2.2.2`

## 4. File Structure & Purpose
| File | Purpose |
| :--- | :--- |
| **`app.py`** | Main Flask web server. Handles routes and API endpoints. |
| **`ai_system.py`** | Core AI logic. Handles querying ChromaDB, prompt engineering, and attribution. |
| **`vector_store.py`** | Manages ChromaDB connections, multi-collection logic (`medical` vs `community`). |
| **`ingest_data.py`** | **Offline Script**. Reads source files, scrubs PII, and builds the database. |
| **`data/sources.yaml`** | Trusted medical sources configuration. |
| **`data/whatsapp_anonymized.txt`** | Placeholder for user's community chat logs. |

## 5. Recent Changes & Fixes
1.  **Offline Ingestion**: Separated database building from app startup to improve performance.
    *   Created `ingest_data.py`.
2.  **Privacy & Safety**:
    *   Added PII scrubber (removes phones/emails) in ingestion script.
    *   Added **Attribution Rules**: AI explicitly distinguishes between "Medical Source" and "Community Discussion".
3.  **Dependnecy Hell Solved**:
    *   Downgraded `numpy` to `1.26.4`.
    *   Upgraded `openai` to `2.9.0`.

## 6. How to Run (Step-by-Step)
**Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 2: Ingest Data (One-Time Setup)**
*   This reads your `sources.yaml` and `whatsapp_anonymized.txt`.
*   It is interactive—it will ask to confirm before overwriting.
```bash
python ingest_data.py
# Type 'y' when prompted
```

**Step 3: Start Server**
```bash
python app.py
```

**Step 4: Verify**
*   Visit `http://localhost:5000`
*   Go to **AI Assistant**
*   Ask: *"What are the early symptoms?"* (Checks Medical Source)
*   Ask: *"Has anyone found a good portable suction machine?"* (Checks Community Source)


ALS Caregiver's Compass - Project Handover Summary
Date: 2025-12-11 Status: Production-Ready Prototype (Local) Version: 1.0.0

1. Project Overview
A full-stack web application providing AI-powered assistance to ALS caregivers. It features a RAG (Retrieval-Augmented Generation) system that combines trusted medical data with community experiences (e.g., WhatsApp logs) to provide accurate, empathetic, and sourced answers.

2. Architecture & Tech Stack
Backend: Flask (Python 3.11+)
Database: ChromaDB (Vector Store for AI memory)
AI Engine: OpenAI (GPT-4o-mini)
Frontend: HTML5, Vanilla CSS (Responsive, Modern Design)
Privacy: Automatic PII scrubbing for community data.
3. Critical Dependencies (Versions)
We explicitly pinned these versions to ensure stability and compatibility:

numpy<2.0 (Fixed 2.0 incompatibility with ChromaDB)
openai>=1.55.0 (Fixed proxies argument conflict with new httpx)
chromadb==0.4.18
sentence-transformers==2.2.2
4. File Structure & Purpose
File	Purpose
app.py
Main Flask web server. Handles routes and API endpoints.
ai_system.py
Core AI logic. Handles querying ChromaDB, prompt engineering, and attribution.
vector_store.py
Manages ChromaDB connections, multi-collection logic (
medical
 vs community).
ingest_data.py
Offline Script. Reads source files, scrubs PII, and builds the database.
data/sources.yaml
Trusted medical sources configuration.
data/whatsapp_anonymized.txt
Placeholder for user's community chat logs.
5. Recent Changes & Fixes
Offline Ingestion: Separated database building from app startup to improve performance.
Created 
ingest_data.py
.
Privacy & Safety:
Added PII scrubber (removes phones/emails) in ingestion script.
Added Attribution Rules: AI explicitly distinguishes between "Medical Source" and "Community Discussion".
Dependnecy Hell Solved:
Downgraded numpy to 1.26.4.
Upgraded openai to 2.9.0.
6. How to Run (Step-by-Step)
Step 1: Install Dependencies

pip install -r requirements.txt
Step 2: Ingest Data (One-Time Setup)

This reads your 
sources.yaml
 and 
whatsapp_anonymized.txt
.
It is interactive—it will ask to confirm before overwriting.
python ingest_data.py
# Type 'y' when prompted
Step 3: Start Server

python app.py
Step 4: Verify

Visit http://localhost:5000
Go to AI Assistant
Ask: "What are the early symptoms?" (Checks Medical Source)
Ask: "Has anyone found a good portable suction machine?" (Checks Community Source)