"""
Main Flask application for ALS Caregiver's Compass
Multi-model AI system with runtime selection
"""
import os
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SESSION_TYPE'] = 'filesystem'

# Note: AI system will be initialized per request with selected model
logger.info("✅ Flask app initialized")
logger.info(f"   Default model: {os.getenv('DEFAULT_MODEL_PROVIDER', 'openai')}")

# ==================== ROUTES ====================

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')

@app.route('/understanding-als')
def understanding_als():
    """Understanding ALS page"""
    return render_template('understanding_als.html')

@app.route('/ai-assistant')
def ai_assistant():
    """AI Assistant page"""
    return render_template('ai_assistant.html')

@app.route('/experiences')
def experiences():
    """Caregiver experiences page"""
    return render_template('experiences.html', page='experiences')

@app.route('/home-icu-guide')
def home_icu_guide():
    """Home ICU guide page"""
    return render_template('home_icu_guide.html', page='icu_guide')

@app.route('/daily-schedule')
def daily_schedule():
    """Daily care schedule page"""
    return render_template('daily_schedule.html', page='schedule')

@app.route('/communication')
def communication():
    """Communication tools page"""
    return render_template('communication.html', page='communication')

@app.route('/faq')
def faq():
    """FAQ page"""
    return render_template('faq.html', page='faq')

@app.route('/emergency-protocol')
def emergency_protocol():
    """Emergency Protocol page"""
    return render_template('emergency_protocol.html', page='emergency_protocol')

# ==================== AI API ENDPOINTS ====================

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant_chat():
    """Handle AI assistant chat with model selection"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        selected_model = data.get('model', os.getenv('DEFAULT_MODEL_PROVIDER', 'openai'))
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Initialize AI system with selected model
        from ai_system_unified import UnifiedAISystem
        ai_system = UnifiedAISystem(model_provider=selected_model)
        
        # Process with AI system
        response = ai_system.process_query(user_message)
        
        # Store in session (optional)
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append({
            'user': user_message,
            'ai': response['response'],
            'timestamp': response['timestamp'],
            'model_used': response.get('model_used', selected_model)
        })
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'response': f"I'm having trouble connecting. Error: {str(e)}"
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    has_keys = bool(os.getenv('OPENAI_API_KEY') or os.getenv('GEMINI_API_KEY') or os.getenv('ANTHROPIC_API_KEY'))
    
    status = {
        'status': 'healthy' if has_keys else 'degraded',
        'ai_system': 'ready' if has_keys else 'needs_api_keys',
        'openai_api': 'configured' if os.getenv('OPENAI_API_KEY') else 'missing',
        'gemini_api': 'configured' if os.getenv('GEMINI_API_KEY') else 'missing',
        'claude_api': 'configured' if os.getenv('ANTHROPIC_API_KEY') else 'missing',
        'default_model': os.getenv('DEFAULT_MODEL_PROVIDER', 'openai'),
        'version': '1.0.0'
    }
    return jsonify(status)

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear chat history"""
    session.pop('chat_history', None)
    return jsonify({'success': True})

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    if debug:
        # Development server
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        # Production server
        from gunicorn.app.base import BaseApplication
        
        class FlaskApplication(BaseApplication):
            def __init__(self, app, options=None):
                self.application = app
                self.options = options or {}
                super().__init__()
            
            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key.lower(), value)
            
            def load(self):
                return self.application
        
        options = {
            'bind': f'0.0.0.0:{port}',
            'workers': 4,
            'threads': 2,
            'timeout': 120
        }
        
        FlaskApplication(app, options).run()
