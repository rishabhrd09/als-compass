# ALS Caregiver Compass

A comprehensive web application and AI assistant for ALS caregivers that brings daily care routines, trusted ALS information, and an intelligent chatbot together in one place.

## Features

- **Multi-Model AI Assistant** - Choose from GPT-4, Claude Sonnet 4, Gemini 2.0, or Grok with agentic reasoning
- **Knowledge Base** - Curated information from trusted medical sources and caregiver experiences
- **Emergency Protocols** - Critical action guides for emergency situations
- **Care Resources** - Daily schedules, home ICU setup, communication tools
- **Research Updates** - Latest ALS research, clinical trials, and treatment options
- **India-Specific Information** - Costs, availability, and resources for Indian caregivers

## Quick Start

### Prerequisites
- Python 3.10+
- API key (at least one: OpenAI, Claude, or Gemini)

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd als-caregiver-compass

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your API key to .env file

# Initialize database
python ingest_data_intelligent.py

# Run application
python app.py
```

Open http://localhost:5000 in your browser.

## Configuration

Create a `.env` file with at least one API key:

```env
# Choose one or more AI providers
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...
# OR
GEMINI_API_KEY=...

# App settings
DEFAULT_MODEL_PROVIDER=openai
SECRET_KEY=your-random-secret-key
PORT=5000
```

## Project Structure

```
├── app.py                      # Main Flask application
├── ai_system_agentic.py        # Advanced agentic AI with multi-step reasoning
├── ai_system_unified.py        # Unified multi-model AI system
├── vector_store_enhanced.py    # Enhanced vector store with multi-collection hierarchy
├── ingest_data_intelligent.py  # Intelligent data ingestion with semantic chunking
├── manage_research.py          # GUI tool for managing research updates
├── clear_database.py           # Database reset utility
├── test_models.py              # AI model testing utility
├── data/
│   ├── sources.yaml            # Trusted ALS medical sources
│   ├── research_categorized.json   # Categorized research data
│   ├── research_updates.json   # Legacy research updates
│   ├── bipap_faq.json          # BiPAP FAQ content
│   └── communication_technology.json  # Communication technology data
├── templates/                  # HTML pages (16 templates)
│   ├── index.html              # Homepage
│   ├── ai_assistant.html       # AI chatbot interface
│   ├── understanding_als.html  # ALS information
│   ├── emergency_protocol.html # Emergency procedures
│   ├── faq.html                # Frequently asked questions
│   ├── home_icu_guide.html     # Home ICU setup guide
│   ├── daily_schedule.html     # Daily care schedule
│   ├── communication.html      # Communication resources
│   ├── communication_technology.html  # Eye trackers, AAC devices
│   ├── research_updates.html   # Latest research and trials
│   ├── experiences.html        # Caregiver experiences
│   └── ...                     # Error pages and partials
└── static/                     # CSS, JavaScript, and images
    ├── css/
    ├── js/
    └── images/
```

## Usage

### AI Assistant
Navigate to `/ai-assistant` to chat with the AI. Features include:
- **Model Selection** - Choose between OpenAI, Claude, Gemini, or Grok
- **Agentic Mode** - Advanced reasoning with multi-step query analysis
- **India Priority** - Automatically prioritizes India-specific information
- **Source Citations** - Responses include citations from trusted sources

Ask questions about:
- ALS symptoms and progression
- Daily care routines and schedules
- Emergency procedures
- Equipment and resources
- India-specific costs and availability

### Care Resources
- **Daily Schedule** (`/daily-schedule`) - Structured care routines
- **Emergency Protocols** (`/emergency-protocol`) - Critical action guides
- **Home ICU Guide** (`/home-icu-guide`) - Setup and equipment information
- **Communication Tools** (`/communication`) - Adaptive communication aids
- **Communication Technology** (`/communication-technology`) - Eye trackers, AAC devices
- **FAQ** (`/faq`) - Frequently asked questions including BiPAP support

### Research Updates
View latest ALS research, clinical trials, and treatment options at `/research-updates`. Includes:
- Approved treatments with India availability and costs
- Active clinical trials (Phase 2-3)
- Pre-clinical research and GWAS studies
- India-specific research hubs (NIMHANS, etc.)

## Tech Stack

- **Backend**: Flask (Python)
- **AI Models**: OpenAI GPT-4, Claude Sonnet 4, Gemini 2.0, Grok
- **Vector Database**: ChromaDB with sentence-transformers embeddings
- **Frontend**: HTML, CSS, JavaScript
- **Production Server**: Gunicorn (auto-configured)

## Development

### Testing AI Models
```bash
# Test all configured AI models
python test_models.py
```

### Managing Research Updates
```bash
# Launch GUI tool for updating research data
python manage_research.py
```

### Database Management
```bash
# Reset and reinitialize database
python clear_database.py
python ingest_data_intelligent.py
```

## API Endpoints

- `POST /api/ai-assistant` - Chat with AI (supports model selection and agentic mode)
- `GET /api/research-categorized` - Get categorized research data
- `GET /api/research-updates` - Get legacy research updates
- `GET /api/communication-tech` - Get communication technology data
- `GET /api/health` - Health check and API key status
- `POST /api/clear-history` - Clear chat history

## Features in Detail

### Agentic AI System
The advanced AI system includes:
- **Query Analysis** - Intelligent categorization and planning
- **Multi-Stage Retrieval** - Hierarchical search across collections
- **Emergency Detection** - Automatic priority handling for urgent queries
- **India Prioritization** - Boosts India-specific content in responses
- **Confidence Scoring** - Evaluates response reliability

### Vector Store
Enhanced vector database with:
- **Multi-Collection Hierarchy** - Separate collections for medical knowledge, equipment, caregiving, etc.
- **Hybrid Search** - Combines semantic search with priority routing
- **Source Diversity** - Ensures varied sources in results
- **Trust Scoring** - Weights sources by reliability

### Data Ingestion
Intelligent data processing with:
- **Semantic Chunking** - Context-aware text segmentation
- **PII Scrubbing** - Automatic removal of personal information
- **Metadata Extraction** - Detects symptoms, costs, India-specific content
- **FAQ Integration** - Structured Q&A ingestion

## Contributing

When adding new features:
1. Update relevant data files in `data/`
2. Run `python ingest_data_intelligent.py` to update vector store
3. Test with `python test_models.py`
4. Update this README if adding new routes or features

## License

[Your License Here]

## Support

For questions or issues, please [contact information or issue tracker].
