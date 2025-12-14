# ALS Caregiver Compass - Setup Guide

Complete setup guide for developers and contributors.

## System Requirements

- **Python**: 3.10 or higher (tested on 3.11)
- **RAM**: Minimum 4GB (8GB recommended for vector database operations)
- **Disk Space**: ~2GB for dependencies and vector database
- **OS**: Windows, macOS, or Linux

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd als-caregiver-compass
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- OpenAI, Anthropic, Google Generative AI (AI providers)
- ChromaDB (vector database)
- Sentence Transformers (embeddings)
- And other required packages

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# AI Provider API Keys (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
XAI_API_KEY=...  # For Grok (optional)

# Default AI Provider
DEFAULT_MODEL_PROVIDER=openai  # Options: openai, claude, gemini, grok

# Flask Configuration
SECRET_KEY=your-random-secret-key-here
PORT=5000
FLASK_ENV=development  # Use 'production' for deployment

# Model Selection (optional)
CLAUDE_MODEL=claude-sonnet-4-20250514
OPENAI_MODEL=gpt-4o-mini
GEMINI_MODEL=gemini-2.0-flash-exp
GROK_MODEL=grok-2-latest
```

**Getting API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic (Claude)**: https://console.anthropic.com/
- **Google (Gemini)**: https://makersuite.google.com/app/apikey
- **xAI (Grok)**: https://x.ai/api

### 5. Initialize Vector Database

```bash
python ingest_data_intelligent.py
```

This will:
- Load trusted medical sources from `data/sources.yaml`
- Process FAQ data from `data/bipap_faq.json`
- Create semantic embeddings
- Build the ChromaDB vector store in `chroma_db_enhanced/`

**Expected output:**
```
✅ Enhanced Vector Store initialized
📚 Loading medical sources...
✅ Ingested X medical sources
📋 Loading FAQ data...
✅ Ingested Y FAQ entries
✅ Database initialization complete!
```

### 6. Run the Application

```bash
python app.py
```

The application will start on http://localhost:5000

**Expected output:**
```
✅ Flask app initialized
   Default model: openai
 * Running on http://0.0.0.0:5000
```

### 7. Verify Installation

Open your browser and navigate to:
- http://localhost:5000 - Homepage
- http://localhost:5000/ai-assistant - AI chatbot
- http://localhost:5000/api/health - Health check endpoint

## Testing

### Test AI Models

```bash
python test_models.py
```

This will test all configured AI providers and show which ones are working.

### Test Import Fix

```bash
python -c "from ai_system_unified import UnifiedAISystem; print('✓ Import successful')"
```

## Development Tools

### Research Manager GUI

Launch the GUI tool for managing research updates:

```bash
python manage_research.py
```

Features:
- LLM-powered research gathering
- Multi-step confirmation workflow
- Source citation tracking
- Direct website updates

### Database Management

**Reset database:**
```bash
python clear_database.py
```

**Reinitialize database:**
```bash
python ingest_data_intelligent.py
```

## Troubleshooting

### Issue: Import Error for `vector_store`

**Error:**
```
ModuleNotFoundError: No module named 'vector_store'
```

**Solution:**
This was a bug in older versions. Ensure you have the latest code where `ai_system_unified.py` imports `vector_store_enhanced` instead of `vector_store`.

### Issue: Emoji Syntax Error in manage_research.py

**Error:**
```
SyntaxError: invalid character '🔬' (U+1F52C)
```

**Solution:**
This has been fixed in the latest version. The emoji was removed from the multi-line string.

### Issue: ChromaDB Initialization Fails

**Error:**
```
Error: Could not create ChromaDB collection
```

**Solution:**
1. Delete the `chroma_db_enhanced/` directory
2. Run `python ingest_data_intelligent.py` again

### Issue: API Key Not Found

**Error:**
```
ValueError: OPENAI_API_KEY not found in .env
```

**Solution:**
1. Ensure `.env` file exists in project root
2. Check that API key is correctly formatted
3. Restart the application after adding keys

### Issue: Model Not Responding

**Symptoms:**
- AI assistant returns errors
- Long response times

**Solution:**
1. Check API key is valid
2. Verify internet connection
3. Try switching to a different model provider
4. Check API provider status pages

### Issue: Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
1. Change PORT in `.env` to a different value (e.g., 5001)
2. Or stop the other process using port 5000

## Project Structure Explained

```
als-caregiver-compass/
├── app.py                      # Main Flask app with routes
├── ai_system_agentic.py        # Advanced AI with reasoning
├── ai_system_unified.py        # Multi-model AI system
├── vector_store_enhanced.py    # Vector database wrapper
├── ingest_data_intelligent.py  # Data ingestion pipeline
├── manage_research.py          # Research management GUI
├── clear_database.py           # DB reset utility
├── test_models.py              # Model testing utility
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── data/                       # Data files
│   ├── sources.yaml            # Medical sources
│   ├── research_categorized.json
│   ├── bipap_faq.json
│   └── communication_technology.json
├── templates/                  # HTML templates
│   ├── base.html               # Base template
│   ├── index.html              # Homepage
│   ├── ai_assistant.html       # AI chat
│   └── ...
├── static/                     # Static assets
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript
│   └── images/                 # Images
├── chroma_db_enhanced/         # Vector database (created on init)
└── venv/                       # Virtual environment (created by you)
```

## Adding New Features

### Adding a New Route

1. Add route in `app.py`:
```python
@app.route('/new-page')
def new_page():
    return render_template('new_page.html')
```

2. Create template in `templates/new_page.html`

3. Update README.md with new route

### Adding New Data Sources

1. Add source to `data/sources.yaml`:
```yaml
- title: "New Source"
  url: "https://example.com"
  trust_score: 8
  category: "medical"
  content: "Source content here..."
```

2. Reingest data:
```bash
python ingest_data_intelligent.py
```

### Adding New Research

Use the GUI tool:
```bash
python manage_research.py
```

Or manually edit `data/research_categorized.json`

## Deployment

### Production Configuration

1. Set environment to production in `.env`:
```env
FLASK_ENV=production
```

2. Use a strong secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

3. The app will automatically use Gunicorn in production mode

### Deployment Platforms

**Heroku:**
- Add `Procfile`: `web: python app.py`
- Set environment variables in Heroku dashboard

**Railway/Render:**
- Set build command: `pip install -r requirements.txt && python ingest_data_intelligent.py`
- Set start command: `python app.py`

**Docker:**
- Create `Dockerfile` with Python 3.11 base image
- Install dependencies and initialize database
- Expose port 5000

## Best Practices

1. **Always activate virtual environment** before running commands
2. **Never commit `.env` file** (it's in `.gitignore`)
3. **Reingest data** after modifying `data/` files
4. **Test with `test_models.py`** after configuration changes
5. **Use agentic mode** for complex queries requiring reasoning
6. **Check API costs** - some models are more expensive than others

## Getting Help

- Check the main [README.md](README.md) for feature documentation
- Review error messages carefully - they often indicate the solution
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify API keys are valid and have sufficient credits

## Contributing

When contributing:
1. Create a new branch for your feature
2. Test thoroughly with `test_models.py`
3. Update documentation (README.md and this guide)
4. Submit a pull request with clear description

## License

[Your License Here]
