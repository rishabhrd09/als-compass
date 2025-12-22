# ALS Caregiver Compass

A comprehensive web application and AI assistant for ALS caregivers that brings daily care routines, trusted ALS information, and an intelligent chatbot together in one place. Developed in collaboration with the **ALSCAS (ALS Care and Support India)** community.

## Features

- **Multi-Model AI Assistant** - Choose from GPT-4, Claude Sonnet, Gemini 2.0, or Grok with agentic reasoning
- **Community-Curated FAQ** - Over 68 curated Q&A entries with decision matrices and flowchart-based guidance
- **Knowledge Base** - Curated information from trusted medical sources and 134,000+ WhatsApp community discussions
- **Emergency Protocols** - Critical action guides for emergency situations
- **Care Resources** - Daily schedules, home ICU setup, communication tools
- **Research Updates** - Latest ALS research, clinical trials, and India-specific research initiatives
- **India-Specific Information** - Costs, availability, and resources for Indian caregivers

## Quick Start

### Prerequisites
- Python 3.10+
- API key (at least one: OpenAI, Anthropic/Claude, or Gemini)

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd als-compass

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
│                               #   - RelevanceAnalyzer with misspelling tolerance
│                               #   - Enhanced system prompts with flowchart formatting
├── ai_system_unified.py        # Unified multi-model AI system
├── vector_store_enhanced.py    # Enhanced vector store with multi-collection hierarchy
├── ingest_data_intelligent.py  # Intelligent data ingestion with semantic chunking
├── manage_research.py          # GUI tool for managing research updates
├── data/
│   ├── sources.yaml                # Trusted ALS medical sources
│   ├── research_categorized.json   # Categorized research data
│   ├── research_initiatives_india.json  # India research collaborations (verified)
│   ├── bipap_faq.json              # BiPAP FAQ content
│   ├── als_comprehensive_faq.json  # Complete FAQ with decision matrices
│   ├── practical_wisdom_faq.json   # Hindsight stories, "What I Wish I Knew"
│   ├── community_wisdom_faq.json   # Curated high-quality community Q&A
│   ├── flowchart_based_faq.json    # Ready Reckoner 9-stage flowchart guidance
│   ├── top10_community_faq.json    # Most-asked questions with exact answers
│   └── whatsapp_detailed_faq.json  # Detailed FAQ with IF/THEN logic
├── templates/                  # HTML pages (16 templates)
│   ├── index.html              # Homepage
│   ├── ai_assistant.html       # AI chatbot interface
│   ├── understanding_als.html  # ALS information
│   ├── emergency_protocol.html # Emergency procedures
│   ├── faq.html                # Community FAQ with conditional guidance
│   ├── home_icu_guide.html     # Home ICU setup guide
│   ├── daily_schedule.html     # Daily care schedule
│   ├── communication.html      # Communication resources
│   ├── research_updates.html   # Research initiatives & collaborations
│   └── ...                     # Error pages and partials
└── static/                     # CSS, JavaScript, and images
```

## Data Sources

The knowledge base is built from:
- **WhatsApp Community Discussions** - 134,000+ messages from ALSCAS groups (2021-2025)
- **ALSCAS Website** - [alslifemanagement.weebly.com](https://alslifemanagement.weebly.com)
- **Curated FAQ Files** - 6 specialized FAQ collections with 68+ entries
- **Research Initiatives** - Verified collaborations with Target ALS, NIMHANS, AIIMS

### Database Statistics
| Collection | Documents |
|------------|-----------|
| community_qa_pairs | ~7,400 |
| emergency_experiences | ~680 |
| community_discussions | ~14,000 |
| medical_authoritative | 1 |
| **Total** | **~22,000** |

## Usage

### AI Assistant
Navigate to `/ai-assistant` to chat with the AI. Features include:
- **Model Selection** - Choose between OpenAI, Claude Sonnet, Gemini, or Grok
- **Agentic Mode** - Advanced reasoning with multi-step query analysis
- **Misspelling Tolerance** - Handles common misspellings (BiPap, AlS, trakeostomy)
- **Flowchart-Style Answers** - Structured IF→THEN decision guidance
- **Source Citations** - Responses include citations from trusted sources

Ask questions about:
- BiPAP timing and settings ("When should BiPAP be started?")
- Tracheostomy decision criteria ("When is tracheostomy needed?")
- PEG/feeding tube timing ("When to consider feeding tube?")
- Daily care routines and equipment
- India-specific costs and availability

### Community FAQ
Navigate to `/faq` for curated community wisdom including:
- **Decision Matrices** - IF→THEN conditional guidance
- **Hindsight Stories** - "What I Wish I Knew Earlier"
- **Practical Tips** - Equipment, costs, and care protocols
- **Key Principles** - Community-tested caregiving wisdom

### Research Updates
Navigate to `/research-updates` for:
- **India Research Initiatives** - AIIMS, NIMHANS, Target ALS collaboration
- **Genetic Testing Programs** - CSIR-IGIB free testing, commercial options
- **Treatment Access** - Tofersen, clinical trials, compassionate use
- **Global Research** - Latest clinical trials and pipeline therapies

## Tech Stack

- **Backend**: Flask (Python 3.10+)
- **AI Models**: OpenAI GPT-4, Claude Sonnet, Gemini 2.0, Grok
- **Vector Database**: ChromaDB with sentence-transformers embeddings
- **Embeddings**: all-MiniLM-L6-v2
- **Frontend**: HTML, CSS, JavaScript
- **Production Server**: Gunicorn (auto-configured)

## Development

### Testing AI Models
```bash
# Test all configured AI models
python test_models.py
```

### Database Rebuild
```bash
# Rebuild vector database (if schema errors occur)
python ingest_data_intelligent.py --clear
# Type REBUILD when prompted
```

### Adding New FAQ Content
1. Add entries to appropriate JSON file in `data/`
2. Run `python ingest_data_intelligent.py` to update vector store
3. Restart `python app.py`

## API Endpoints

- `POST /api/ai-assistant` - Chat with AI (supports model selection and agentic mode)
- `GET /api/community-faq` - Get community FAQ data for FAQ page
- `GET /api/research-categorized` - Get categorized research data
- `GET /api/research-initiatives` - Get India research initiatives
- `GET /api/health` - Health check and API key status
- `POST /api/clear-history` - Clear chat history

## Features in Detail

### Relevance Analyzer
The AI includes intelligent query filtering:
- **Keyword Matching** - 200+ ALS-related terms across 15 categories
- **Misspelling Tolerance** - 50+ common misspelling mappings
- **Threshold Scoring** - Configurable relevance threshold (default: 0.5)
- **Out-of-Scope Detection** - Politely redirects non-ALS queries

### Agentic AI System
The advanced AI system includes:
- **Query Analysis** - Intelligent categorization and planning
- **Multi-Stage Retrieval** - Hierarchical search across collections
- **Emergency Detection** - Automatic priority handling for urgent queries
- **Flowchart Formatting** - Structures answers with IF→THEN logic
- **Confidence Scoring** - Evaluates response reliability

### Vector Store
Enhanced vector database with:
- **Multi-Collection Hierarchy** - 6 separate collections for different content types
- **Hybrid Search** - Combines semantic search with priority routing
- **Source Diversity** - Ensures varied sources in results
- **Trust Scoring** - Weights sources by reliability

## Contributing

When adding new features:
1. Update relevant data files in `data/`
2. Run `python ingest_data_intelligent.py` to update vector store
3. Test with `python test_models.py`
4. Update this README if adding new routes or features

## Acknowledgments

- **ALSCAS Community** - For sharing invaluable caregiving wisdom
- **Target ALS** - For research collaboration
- **NIMHANS & AIIMS** - For clinical partnership

## License

[Your License Here]

## Support

For questions or issues, contact the ALSCAS community or open an issue on GitHub.
