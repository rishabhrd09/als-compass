# ALS Caregiver Compass

A simple web application and AI agent for ALS caregivers that brings daily care routines, trusted ALS information, and a ai chatbot together in one plac

## Features

- Multi-model AI assistant (GPT-4, Claude, Gemini, Grok)
- Knowledge base from  trusted medical sources
- Emergency protocols and care guides
- Daily care schedules and routines
- Communication tools and resources
- Latest ALS research updates

## Quick Start

### Prerequisites
- Python 3.10+
- API key (OpenAI, Claude, or Gemini)

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
# Choose one AI provider
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
├── ai_system_agentic.py        # AI assistant with reasoning
├── vector_store_enhanced.py    # Knowledge base (ChromaDB)
├── data/
│   ├── sources.yaml            # Trusted ALS sources
│   └── research_updates.json   # Latest research
├── templates/                  # HTML pages
└── static/                     # CSS and JavaScript
```

## Usage

### AI Assistant
Navigate to `/ai-assistant` to chat with the AI. Select your preferred model and ask questions about:
- ALS symptoms and progression
- Daily care routines
- Emergency procedures
- Equipment and resources
- India-specific information

### Care Resources
- **Daily Schedule** - Structured care routines
- **Emergency Protocols** - Critical action guides
- **Home ICU Guide** - Setup and equipment
- **Communication Tools** - Adaptive communication aids

### Research Updates
View latest ALS research and clinical trials on the homepage.

## Tech Stack

- **Backend**: Flask (Python)
- **AI**: OpenAI, Claude, Gemini, Grok
- **Database**: ChromaDB (vector database)
- **Frontend**: HTML, CSS, JavaScript

## Development

```bash
# Test AI models
python test_models.py

# Manage research updates
python manage_research.py

# Reset database
python clear_database.py
python ingest_data_intelligent.py
```

## API Endpoints

- `POST /api/ai-assistant` - Chat with AI
- `GET /api/research-updates` - Get latest research
- `GET /api/health` - Health check

