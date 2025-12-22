"""
Main Flask application for ALS Caregiver's Compass
Multi-model AI system with runtime selection
"""
import os
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import logging
import json

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
    """Handle AI assistant chat with model selection and agentic mode"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        selected_model = data.get('model', os.getenv('DEFAULT_MODEL_PROVIDER', 'openai'))
        use_agentic = data.get('agentic', True)  # Default to agentic mode
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Choose AI system based on mode
        if use_agentic:
            try:
                from ai_system_agentic import AgenticAISystem
                ai_system = AgenticAISystem(model_provider=selected_model)
                logger.info(f"Using Agentic AI System with {selected_model}")
            except Exception as e:
                logger.warning(f"Agentic system failed, falling back: {e}")
                from ai_system_unified import UnifiedAISystem
                ai_system = UnifiedAISystem(model_provider=selected_model)
        else:
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

@app.route('/api/image/<path:image_path>')
def serve_image(image_path):
    """Serve images from ai_assistant_images folder (security validated)"""
    try:
        from pathlib import Path
        
        # Security: Ensure path is within ai_assistant_images directory
        images_base = Path('ai_assistant_images').absolute()
        requested_path = (images_base / image_path).absolute()
        
        # Validate that requested path is within images directory
        if not str(requested_path).startswith(str(images_base)):
            logger.warning(f"Security: Path traversal attempt blocked: {image_path}")
            return jsonify({'error': 'Invalid path'}), 403
        
        # Check if file exists
        if not requested_path.is_file():
            return jsonify({'error': 'Image not found'}), 404
        
        # Serve the image
        from flask import send_file
        return send_file(requested_path, mimetype=f'image/{requested_path.suffix[1:]}')
        
    except Exception as e:
        logger.error(f"Error serving image {image_path}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/research-updates')
def get_research_updates():
    """Get active research updates for homepage (legacy)"""
    try:
        with open('data/research_updates.json', 'r') as f:
            research_data = json.load(f)
        # Return only active research
        active_research = [r for r in research_data if r.get('status') == 'active']
        return jsonify(active_research)
    except FileNotFoundError:
        return jsonify([])
    except Exception as e:
        logger.error(f"Error loading research updates: {e}")
        return jsonify([])

@app.route('/api/research-categorized')
def get_research_categorized():
    """Get categorized research data for research page"""
    try:
        with open('data/research_categorized.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({
            "last_updated": "2025-12-14",
            "categories": {}
        })
    except Exception as e:
        logger.error(f"Error loading categorized research: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/research-updates')
def research_updates_page():
    """Research updates page"""
    return render_template('research_updates.html')

@app.route('/communication-technology')
def communication_technology_page():
    """Communication Technology page - Eye trackers, head tracking, AAC devices"""
    return render_template('communication_technology.html')

@app.route('/verified-communication-solutions')
def verified_communication_solutions_page():
    """Verified Communication Solutions page - Research-verified eye tracking and AAC solutions"""
    return render_template('verified_communication_solutions.html')

@app.route('/api/communication-tech')
def get_communication_tech():
    """Get communication technology data for the page"""
    try:
        with open('data/communication_technology.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({
            "last_updated": "2025-12-14",
            "categories": {}
        })
    except Exception as e:
        logger.error(f"Error loading communication tech data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/research-initiatives')
def get_research_initiatives():
    """Get research initiatives data for the research updates page"""
    try:
        with open('data/research_initiatives_india.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({
            "last_updated": "2025-12-15",
            "categories": {}
        })
    except Exception as e:
        logger.error(f"Error loading research initiatives data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/community-faq')
def get_community_faq():
    """Get comprehensive FAQ data with practical wisdom from caregivers"""
    try:
        with open('data/als_comprehensive_faq.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        # Fallback to old file if new one not found
        try:
            with open('data/als_community_faq_enhanced.json', 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except:
            return jsonify({
                "metadata": {"title": "FAQ not found"},
                "categories": []
            })
    except Exception as e:
        logger.error(f"Error loading community FAQ data: {e}")
        return jsonify({"error": str(e)}), 500

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
