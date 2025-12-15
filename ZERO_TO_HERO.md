# ALS Caregiver Compass - Zero to Hero Setup Guide

> **Complete guide to understanding, setting up, and deploying the ALS Caregiver Compass platform**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Code Structure](#architecture--code-structure)
3. [Prerequisites](#prerequisites)
4. [Installation Steps](#installation-steps)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Features & Usage](#features--usage)
8. [File Structure Explained](#file-structure-explained)
9. [Troubleshooting](#troubleshooting)
10. [Development & Deployment](#development--deployment)

---

## 🎯 Project Overview

**ALS Caregiver Compass** is a comprehensive AI-powered web platform designed to support ALS caregivers with:

- **Multi-Model AI Assistant**: Supports OpenAI GPT-4, Claude, Gemini, and Grok
- **Agentic Reasoning**: Advanced query analysis with multi-step reasoning
- **Knowledge Base**: RAG system with ChromaDB vector database
- **Research Updates**: AI-powered research tracking system
- **Caregiver Resources**: Emergency protocols, daily schedules, communication tools
- **India-Focused**: Prioritizes India-specific ALS resources and information

---

## 🏗️ Architecture & Code Structure

### **Core Components**

#### 1. **Flask Web Application** (`app.py`)
- Main web server handling 9 routes
- API endpoints for AI chat, research updates, health checks
- Session management for chat history
- Error handling (404/500 pages)
- Production-ready with Gunicorn configuration

#### 2. **Agentic AI System** (`ai_system_agentic.py`)
- **Query Analyzer**: Intelligent query classification
- **Multi-Step Reasoning**: Plans and executes retrieval strategy
- **Multi-Model Support**: Claude, OpenAI (GPT-4/o1), Gemini, Grok
- **Emergency Detection**: Prioritizes critical health queries
- **Advanced Features**:
  - India-priority mode
  - Cost-awareness detection
  - Technical detail extraction
  - Citation tracking
  - Confidence scoring

#### 3. **Unified AI System** (`ai_system_unified.py`)
- Simplified AI system for basic queries
- Fallback when agentic mode is disabled
- Supports same multi-model providers

#### 4. **Vector Store** (`vector_store_enhanced.py`)
- ChromaDB-based semantic search
- YAML data source ingestion
- Category-based filtering
- India-priority retrieval
- Multi-strategy search (semantic, keyword, hybrid)

#### 5. **Data Ingestion** (`ingest_data_intelligent.py`)
- Processes YAML sources into vector embeddings
- Chunks documents intelligently
- Metadata enrichment
- Progress tracking with tqdm

#### 6. **Research Manager** (`manage_research.py`)
- Desktop GUI application (Tkinter)
- Manual research entry
- AI-powered research fetching
- JSON database management
- No web server required

---

## ✅ Prerequisites

### **Required**
- **Python 3.10 or 3.11** (recommended)
- **pip** (Python package manager)
- **Git** (for cloning repository)

### **Optional but Recommended**
- **Virtual environment** (venv or conda)
- **API Keys** (at least one):
  - OpenAI API key
  - Anthropic (Claude) API key
  - Google Gemini API key
  - xAI Grok API key

---

## 🚀 Installation Steps

### **Step 1: Clone the Repository**

```bash
# Navigate to your desired directory
cd ~/projects

# Clone the repository
git clone <your-repo-url> als-caregiver-compass
cd als-caregiver-compass
```

### **Step 2: Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### **Step 3: Install Dependencies**

```bash
# Install all required packages
pip install -r requirements.txt
```

**Dependencies Installed:**
- `Flask` - Web framework
- `gunicorn` - Production server
- `openai` - OpenAI API client
- `anthropic` - Claude API client
- `google-generativeai` - Gemini API client
- `chromadb` - Vector database
- `sentence-transformers` - Embeddings
- `numpy`, `PyYAML`, `tqdm`, `python-dotenv`, `requests`

---

## ⚙️ Configuration

### **Step 1: Create `.env` File**

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

### **Step 2: Add API Keys**

```env
# Required: At least ONE API key
OPENAI_API_KEY=sk-...your-key-here...
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
GEMINI_API_KEY=...your-key-here...
GROK_API_KEY=xai-...your-key-here...

# Choose default AI model (openai, claude, gemini, or grok)
DEFAULT_MODEL_PROVIDER=openai

# Flask Configuration
SECRET_KEY=your-secret-key-for-sessions
FLASK_ENV=development
PORT=5000

# Optional: OpenAI Model Selection
# For standard models: gpt-4, gpt-4-turbo
# For reasoning models: o1-preview, o1-mini
OPENAI_MODEL=gpt-4

# Vector Database (default works fine)
CHROMA_PERSIST_DIR=./chroma_db_enhanced
```

### **Step 3: Prepare Data Sources**

The application comes with pre-configured trusted sources in `data/sources.yaml`. You can:

1. **Use Default Sources** (recommended for first run)
2. **Add Custom Sources** - Edit `data/sources.yaml`
3. **Initialize Vector Database**:

```bash
python ingest_data_intelligent.py
```

This will:
- Load all sources from `data/sources.yaml`
- Create embeddings
- Store in ChromaDB
- Takes 2-5 minutes depending on data size

---

## 🎮 Running the Application

### **Development Mode**

```bash
# Make sure virtual environment is activated
# venv\Scripts\activate (Windows) or source venv/bin/activate (Mac/Linux)

# Run the Flask development server
python app.py
```

**Expected output:**
```
✅ Flask app initialized
   Default model: openai
 * Running on http://0.0.0.0:5000
```

**Access the app:**
- Open browser: `http://localhost:5000`

### **Production Mode**

```bash
# Set environment to production
export FLASK_ENV=production  # Mac/Linux
set FLASK_ENV=production     # Windows

# Run with Gunicorn (included in app.py)
python app.py
```

---

## 🎯 Features & Usage

### **1. Home Page** (`/`)
- Hero section with tagline
- Latest research updates (dynamic from JSON)
- Resource cards (Home ICU, Daily Schedule, Communication, etc.)
- Inspirational quote section
- Trusted sources with clickable links

### **2. AI Assistant** (`/ai-assistant`)
**Features:**
- Multi-model selector (GPT-4, Claude, Gemini, Grok)
- Agentic mode toggle
- Chat interface with markdown support
- Source citations
- Confidence scores
- Emergency query detection

**How to Use:**
1. Select AI model from dropdown
2. Toggle agentic mode (ON for advanced reasoning)
3. Type your question
4. Get AI response with citations and confidence

### **3. Understanding ALS** (`/understanding-als`)
- Comprehensive ALS information
- Medical terminology
- Symptom progression
- Treatment options

### **4. Emergency Protocols** (`/emergency-protocol`)
- Critical emergency procedures
- Respiratory distress protocols
- Quick action guides

### **5. Daily Care Schedule** (`/daily-schedule`)
- Structured daily routines
- Medication schedules
- Nutrition management

### **6. Communication Tools** (`/communication`)
- Adaptive communication aids
- Technology recommendations
- Communication techniques

### **7. Home ICU Guide** (`/home-icu-guide`)
- Setting up home ICU
- Equipment requirements
- Safety standards

### **8. Shared Experiences** (`/experiences`)
- Caregiver stories
- Community wisdom
- Real-life resilience examples

### **9. FAQ** (`/faq`)
- Common questions
- Quick answers

---

## 📁 File Structure Explained

### **Root Directory**
```
als-caregiver-compass/
├── app.py                      # Main Flask application
├── ai_system_agentic.py        # Advanced AI with reasoning
├── ai_system_unified.py        # Simple AI system
├── vector_store_enhanced.py    # ChromaDB vector database
├── ingest_data_intelligent.py  # Data ingestion script
├── manage_research.py          # Research manager GUI
├── test_models.py              # Test AI model connections
├── clear_database.py           # Reset vector database
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .env.example                # Example environment file
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── ZERO_TO_HERO.md            # This guide
```

### **Directories**

#### **`data/`** - Configuration & Research Data
```
data/
├── sources.yaml                # Trusted ALS sources
└── research_updates.json       # Latest ALS research
```

#### **`templates/`** - HTML Templates
```
templates/
├── base.html                   # Base layout with navbar
├── index.html                  # Homepage
├── ai_assistant.html           # AI chat interface
├── understanding_als.html      # ALS information
├── emergency_protocol.html     # Emergency guides
├── daily_schedule.html         # Daily care schedules
├── communication.html          # Communication tools
├── home_icu_guide.html         # Home ICU setup
├── experiences.html            # Shared stories
├── faq.html                    # FAQ page
├── 404.html                    # Not found page
└── 500.html                    # Error page
```

#### **`static/`** - Static Assets
```
static/
├── css/
│   ├── style.css               # Main stylesheet
│   └── quote-section.css       # Quote section styles
├── js/
│   └── (JavaScript files)
└── images/
    └── (Image assets)
```

#### **`chroma_db_enhanced/`** - Vector Database (auto-generated)
- ChromaDB persistence directory
- Created after running `ingest_data_intelligent.py`

#### **`venv/`** - Virtual Environment (auto-generated)
- Python virtual environment
- Not tracked in git

---

## 🔧 Troubleshooting

### **Issue 1: ModuleNotFoundError**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### **Issue 2: API Key Errors**
```
Error: No API key found
```

**Solution:**
1. Check `.env` file exists
2. Ensure at least one API key is set
3. Restart the application

### **Issue 3: Vector Database Empty**
```
Warning: No documents in vector store
```

**Solution:**
```bash
# Reinitialize the database
python ingest_data_intelligent.py
```

### **Issue 4: Port Already in Use**
```
Error: Address already in use
```

**Solution:**
```bash
# Change port in .env
PORT=5001

# Or kill the process using port 5000
# Windows: netstat -ano | findstr :5000
# Mac/Linux: lsof -i :5000
```

### **Issue 5: Slow AI Responses**
- **Use GPT-4-turbo** instead of o1-preview for faster responses
- **Disable agentic mode** for simple queries
- **Check API quotas** - you may have hit rate limits

---

## 🔨 Development & Deployment

### **Running Research Manager**

```bash
# Desktop GUI for managing research updates
python manage_research.py
```

**Features:**
- View current research
- Add new research manually
- AI-powered automatic research fetching
- Export to JSON

### **Testing AI Models**

```bash
# Test your API keys and models
python test_models.py
```

### **Clearing Vector Database**

```bash
# Reset the vector database
python clear_database.py

# Reinitialize
python ingest_data_intelligent.py
```

### **Adding New Sources**

1. Edit `data/sources.yaml`
2. Add your source under appropriate tier
3. Run: `python ingest_data_intelligent.py`
4. Restart the app

### **Deployment Checklist**

1. ✅ Set `FLASK_ENV=production` in `.env`
2. ✅ Use strong `SECRET_KEY`
3. ✅ Configure production database (if using external DB)
4. ✅ Set up SSL/HTTPS
5. ✅ Configure firewall rules
6. ✅ Use Gunicorn (automatically used in production mode)
7. ✅ Set up monitoring/logging
8. ✅ Backup vector database regularly

---

## 🎓 Understanding the Code

### **How AI Processing Works**

1. **User sends query** → `/api/ai-assistant`
2. **Model selection** → Choose GPT-4, Claude, Gemini, or Grok
3. **Agentic mode check**:
   - **ON**: Use `AgenticAISystem` with query analysis
   - **OFF**: Use `UnifiedAISystem` for simple processing
4. **Query analysis** (if agentic):
   - Classify query type (emergency, medical, equipment, etc.)
   - Determine search strategy
   - Detect India-priority needs
5. **Retrieval**:
   - Search vector database (ChromaDB)
   - Apply filters (category, India-priority)
   - Rank by relevance
6. **Synthesis**:
   - Build context from retrieved documents
   - Generate AI response with citations
   - Calculate confidence score
7. **Response** → Return JSON with answer, sources, confidence

### **Vector Database Flow**

```
YAML Sources → Chunking → Embeddings → ChromaDB → Semantic Search
```

1. **sources.yaml** contains trusted sources
2. **Chunking** splits content into digestible pieces
3. **Embeddings** convert text to vectors (sentence-transformers)
4. **ChromaDB** stores and indexes vectors
5. **Search** finds semantically similar content

---

## 📝 Next Steps

1. **Run the application** - Follow installation steps
2. **Test AI assistant** - Try different models and queries
3. **Customize sources** - Add your own trusted resources
4. **Explore features** - Navigate through all pages
5. **Deploy** - Set up production environment
6. **Monitor** - Track usage and errors
7. **Iterate** - Add new features based on user feedback

---

## 🆘 Need Help?

- **Check logs** - Flask outputs detailed error messages
- **Review `.env`** - Ensure all keys are correct
- **Test models** - Run `test_models.py`
- **Reinitialize DB** - Clear and re-ingest data
- **Check dependencies** - Ensure all packages installed

---

## 📜 License & Credits

Built with ❤️ for ALS caregivers worldwide.

**Every Journey Matters**

---

*Last Updated: December 2024*
