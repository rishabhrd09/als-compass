"""Explicit public surface shared by local Flask development and static export."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PAGE_ROUTES = (
    '/', '/understanding-als', '/ai-assistant', '/diet-chart-tool',
    '/inventory-management', '/power-backup-guide', '/ups-faq', '/home-icu-guide',
    '/daily-schedule', '/communication', '/faq', '/emergency-protocol',
    '/research-updates', '/communication-technology',
    '/verified-communication-solutions', '/eye-tracker-setup', '/comm-tech-research',
)

PUBLIC_DATA_FILES = {
    '/content/faq.json': 'data/als_comprehensive_faq.json',
    '/content/communication-tech.json': 'data/communication_technology.json',
    '/content/research-categorized.json': 'data/research_categorized.json',
}


def page_output(route):
    return 'index.html' if route == '/' else route.strip('/') + '/index.html'


def canonical_path(route):
    return '/' if route == '/' else route.rstrip('/') + '/'
