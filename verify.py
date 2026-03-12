#!/usr/bin/env python3
"""ALS Compass verification -- run from project root."""
import sys, os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def chk(label, ok):
    icon = 'PASS' if ok else 'FAIL'
    print(f'  {icon}  {label}')
    return ok

results = []

try:
    from app import app
    c = app.test_client()

    # All routes must return 200
    routes = [
        '/', '/understanding-als', '/ai-assistant', '/home-icu-guide',
        '/faq', '/emergency-protocol', '/diet-chart-tool',
        '/inventory-management', '/power-backup-guide', '/ups-faq',
        '/daily-schedule', '/communication', '/research-updates',
        '/communication-technology', '/verified-communication-solutions',
        '/eye-tracker-setup', '/comm-tech-research',
    ]
    for r in routes:
        resp = c.get(r)
        results.append(chk(f'HTTP 200 {r}  ({len(resp.data):,}b)', resp.status_code == 200))

    # CSS integrity
    with open('static/css/style.css', encoding='utf-8') as f:
        css = f.read()
    rules = css.count('{')
    results.append(chk(f'CSS rules: {rules} (need >= 214)', rules >= 214))

    # Feature presence -- understanding_als
    als = c.get('/understanding-als').data.decode(errors='ignore')
    for label, kw in {
        'Three.js globe canvas':  'three-cvs',
        'Globe container div':    'hero__3d',
        'Mouse parallax':         'mousemove',
        'GSAP loaded':            'gsap.min.js',
        'ScrollTrigger':          'ScrollTrigger',
        'Scroll progress bar':    'scroll-progress',
        'Copyright 2026':         '2026',
    }.items():
        results.append(chk(f'ALS page -- {label}', kw in als))

    # Feature presence -- index
    home = c.get('/').data.decode(errors='ignore')
    for label, kw in {
        'GSAP script':      'gsap.min.js',
        'ScrollTrigger':    'ScrollTrigger',
        'Copyright 2026':   '2026',
    }.items():
        results.append(chk(f'Home -- {label}', kw in home))

    # CSS features
    for label, kw in {
        'Global animations block':   'GLOBAL ANIMATION',
        'Card hover lift':           'translateY(-5px)',
        'Font size base 1.125':      '--font-size-base: 1.125rem',
        'Hero title clamp':          'clamp(2.75rem',
        'Container 1400 breakpoint': 'max-width: 1400px',
    }.items():
        results.append(chk(f'style.css -- {label}', kw in css))

    # base.html
    with open('templates/base.html', encoding='utf-8') as f:
        base_html = f.read()
    for label, kw in {
        'DM Sans in fonts link':     'DM+Sans',
        'Crimson Pro in fonts link': 'Crimson+Pro',
        'preconnect hints':          'preconnect',
        'Copyright 2026':            '2026',
    }.items():
        results.append(chk(f'base.html -- {label}', kw in base_html))

    # Task 4 -- AI Assistant
    ai = c.get('/ai-assistant').data.decode(errors='ignore')
    results.append(chk('AI -- ai-assistant.css linked', 'ai-assistant.css' in ai))
    results.append(chk('AI -- showTypingIndicator JS', 'showTypingIndicator' in ai))
    results.append(chk('AI -- suggestion-btn preserved', 'suggestion-btn' in ai))

    # Task 6 -- FAQ
    faq = c.get('/faq').data.decode(errors='ignore')
    results.append(chk('FAQ -- faq-item preserved', 'faq-item' in faq))
    results.append(chk('FAQ -- faqSearch preserved', 'faqSearch' in faq))
    results.append(chk('FAQ -- faq-no-results added', 'faq-no-results' in faq))

except Exception as e:
    print(f'  FAIL  Exception: {e}')
    import traceback; traceback.print_exc()
    results.append(False)

passed = sum(results)
total = len(results)
print(f'\n{"="*52}')
status = 'ALL PASSED' if all(results) else 'SOME FAILED'
print(f'{status} -- {passed}/{total}')
if not all(results):
    sys.exit(1)
