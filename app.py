"""
Main Flask application for ALS Caregiver's Compass
Multi-model AI system with runtime selection
"""
import os
import subprocess
import threading
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import logging
import json
from datetime import date
from pathlib import Path
from research_schema import validate_research

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

RESEARCH_DATA_PATH = Path(__file__).resolve().parent / 'data' / 'research_categorized.json'


def load_research_data():
    """Read the reviewed snapshot shared by the page, homepage and JSON API."""
    with RESEARCH_DATA_PATH.open(encoding='utf-8') as research_file:
        research = json.load(research_file)
    validate_research(research)
    return research


@app.template_filter('research_date')
def research_date(value):
    """Display partial dates without inventing a publication day."""
    if not value:
        return 'Publication date not stated'
    if len(value) == 7:
        return date.fromisoformat(value + '-01').strftime('%B %Y')
    return date.fromisoformat(value).strftime('%d %B %Y').lstrip('0')

# ==================== ROUTES ====================

@app.route('/')
def home():
    """Home page"""
    try:
        research = load_research_data()
        entries = {item['id']: item for group in research['categories'].values() for item in group}
        research_preview = [entries[item_id] for item_id in research['homepage_entries']]
    except (OSError, ValueError, KeyError, TypeError):
        logger.exception('Research preview unavailable')
        research, research_preview = {}, []
    return render_template('index.html', research=research, research_preview=research_preview)

@app.route('/understanding-als')
def understanding_als():
    """Understanding ALS page"""
    return render_template('understanding_als.html')

@app.route('/ai-assistant')
def ai_assistant():
    """AI Assistant page"""
    return render_template('ai_assistant.html')

@app.route('/diet-chart-tool')
def diet_chart_tool():
    """Diet Chart Tool - Coming Soon page"""
    return render_template('diet_chart_tool.html', page='diet_chart')

@app.route('/inventory-management')
def inventory_management():
    """Home ICU Inventory Management - Coming Soon page"""
    return render_template('inventory_management.html', page='inventory')

@app.route('/power-backup-guide')
def power_backup_guide():
    """Power Backup Guide page - UPS and battery calculations"""
    return render_template('power_backup_guide.html', page='power_backup')

@app.route('/ups-faq')
def ups_faq():
    """UPS FAQ page - Comprehensive power backup FAQ for home ICU"""
    return render_template('ups_faq.html', page='ups_faq')

@app.route('/home-icu-guide')
def home_icu_guide():
    """Home ICU guide page"""
    with (Path(__file__).resolve().parent / 'data' / 'icu_equipment_images.json').open(encoding='utf-8') as file:
        equipment_gallery = json.load(file)
    return render_template('home_icu_guide.html', page='icu_guide', equipment_gallery=equipment_gallery)

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
        return jsonify(load_research_data())
    except (OSError, ValueError):
        logger.exception('Research data unavailable')
        return jsonify({'error': 'Research data is temporarily unavailable.'}), 503

@app.route('/research-updates')
def research_updates_page():
    """Render the full evidence review; JavaScript enhances filtering only."""
    try:
        research = load_research_data()
        sections = []
        for section in research['sections']:
            items = [item for category in section['categories'] for item in research['categories'][category]]
            sections.append(dict(section, entries=items))
        sources = {source['id']: dict(source, number=index + 1)
                   for index, source in enumerate(research['source_library'])}
        return render_template('research_updates.html', research=research,
                               sections=sections, sources=sources,
                               total_entries=sum(len(section['entries']) for section in sections))
    except (OSError, ValueError, KeyError, TypeError):
        logger.exception('Research review unavailable')
        return render_template('research_updates.html', research=None), 503

@app.route('/communication-technology')
def communication_technology_page():
    """Communication Technology page - Eye trackers, head tracking, AAC devices"""
    return render_template('communication_technology.html')

@app.route('/verified-communication-solutions')
def verified_communication_solutions_page():
    """Verified Communication Solutions page - Research-verified eye tracking and AAC solutions"""
    return render_template('verified_communication_solutions.html')

@app.route('/eye-tracker-setup')
def eye_tracker_setup_page():
    """Eye Tracker Setup Guide - Detailed setup instructions for Tobii Eye Trackers"""
    return render_template('eye_tracker_setup.html')

@app.route('/comm-tech-research')
def comm_tech_research_page():
    """Communication Technology Research - Wearable eye-tracking and BCI research"""
    with open(os.path.join(app.root_path, 'data', 'communication_technology.json'), encoding='utf-8') as f:
        communication_data = json.load(f)
    return render_template('comm_tech_research.html', communication_data=communication_data)

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

# ==================== MANIM ANIMATION RENDERING ====================

# Track render state in memory
_render_state = {'status': 'idle', 'message': ''}

def _find_manim():
    """Locate manim executable."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, 'venv', 'Scripts', 'manim.exe'),
        os.path.join(base_dir, 'venv', 'bin', 'manim'),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    # Check PATH
    import shutil as _sh
    if _sh.which('manim'):
        return 'manim'
    return None

def _videos_exist():
    """Check if rendered videos are already present."""
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'videos')
    return (os.path.isfile(os.path.join(base, 'motor_neuron_als.webm'))
            or os.path.isfile(os.path.join(base, 'motor_neuron_als.mp4')))

def _render_manim_videos(quality='l'):
    """Background task to render Manim animations.
    quality: 'l' = 480p (fast, ~30s), 'm' = 720p (~2min), 'h' = 1080p (~8min)
    """
    global _render_state
    _render_state = {'status': 'rendering', 'message': 'Starting Manim render...'}

    base_dir = os.path.dirname(os.path.abspath(__file__))
    videos_dir = os.path.join(base_dir, 'static', 'videos')
    os.makedirs(videos_dir, exist_ok=True)

    manim_cmd = _find_manim()
    if not manim_cmd:
        _render_state = {'status': 'error', 'message': 'Manim not installed. Run setup with optional animations enabled.'}
        return

    scene_file = os.path.join(base_dir, 'manim_scenes', 'motor_neuron.py')
    if not os.path.isfile(scene_file):
        _render_state = {'status': 'error', 'message': 'manim_scenes/motor_neuron.py not found'}
        return

    media_dir = os.path.join(base_dir, 'manim_media')
    quality_flag = f'-q{quality}'

    renders = [
        ('MotorNeuronALS', 'mp4', 'motor_neuron_als.mp4'),
        ('MotorNeuronComparison', 'mp4', 'motor_neuron_comparison.mp4'),
    ]

    for i, (scene_name, fmt, out_name) in enumerate(renders, 1):
        _render_state['message'] = f'Rendering {scene_name} ({i}/{len(renders)})...'
        logger.info(f"Manim: rendering {scene_name} at {quality_flag}...")
        try:
            result = subprocess.run(
                [manim_cmd, quality_flag, f'--format={fmt}',
                 f'--media_dir={media_dir}', scene_file, scene_name],
                capture_output=True, text=True, timeout=600, cwd=base_dir
            )
            if result.returncode != 0:
                err = result.stderr[:300] if result.stderr else 'Unknown error'
                logger.warning(f"Manim render {scene_name} failed: {err}")
                _render_state = {'status': 'error', 'message': f'Failed: {err[:150]}'}
                return
        except FileNotFoundError:
            _render_state = {'status': 'error', 'message': 'Manim not found in PATH.'}
            return
        except subprocess.TimeoutExpired:
            _render_state = {'status': 'error', 'message': f'{scene_name} timed out (10 min limit)'}
            return

        # Find and copy rendered file
        import glob as _glob
        pattern = os.path.join(media_dir, '**', f'{scene_name}.{fmt}')
        matches = _glob.glob(pattern, recursive=True)
        if matches:
            import shutil as _sh
            _sh.copy2(matches[0], os.path.join(videos_dir, out_name))
            logger.info(f"  -> Copied {out_name} to static/videos/")

    _render_state = {'status': 'done', 'message': 'All animations rendered successfully!'}
    logger.info("Manim animations rendered successfully")


@app.route('/api/render-animation', methods=['POST'])
def render_animation():
    """Trigger Manim animation rendering in background."""
    if _render_state['status'] == 'rendering':
        return jsonify({'status': 'rendering', 'message': 'Already rendering, please wait...'})

    # Use medium quality (720p) for user-triggered renders — good balance
    thread = threading.Thread(target=_render_manim_videos, args=('m',), daemon=True)
    thread.start()
    return jsonify({'status': 'started', 'message': 'Rendering started (720p)...'})


@app.route('/api/render-status')
def render_status():
    """Check the current Manim render status."""
    return jsonify(_render_state)


@app.route('/api/animation-available')
def animation_available():
    """Check if pre-rendered Manim videos exist."""
    return jsonify({'available': _videos_exist()})


def _auto_render_on_startup():
    """Auto-render animations in background if not present. Uses 480p for speed."""
    if not _videos_exist() and _find_manim():
        import shutil as _sh
        if _sh.which('ffmpeg'):
            logger.info("Auto-rendering Manim animations in background (480p)...")
            thread = threading.Thread(target=_render_manim_videos, args=('l',), daemon=True)
            thread.start()
        else:
            logger.info("Skipping auto-render: FFmpeg not found")


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

    # Auto-render Manim animations in background (non-blocking)
    # In debug mode, Flask reloads twice — only render on the reloader process
    if not debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        _auto_render_on_startup()

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
