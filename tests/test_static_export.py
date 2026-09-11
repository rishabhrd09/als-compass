"""Release checks against generated files, with no AI dependencies or network."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

from app import app
from public_site import PAGE_ROUTES, PUBLIC_DATA_FILES, ROOT, canonical_path, page_output
from scripts import build_static as builder

ORIGIN = 'https://als.carekosh.com'


class StaticExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.output = Path(cls.temporary.name) / 'production'
        cls.result = builder.export_site(cls.output, ORIGIN)

    def test_export_contains_exactly_the_public_surface(self):
        assets = json.loads((ROOT / 'config/static-assets.json').read_text())['assets']
        expected = set(assets) | {page_output(route) for route in PAGE_ROUTES}
        expected |= {url.lstrip('/') for url in PUBLIC_DATA_FILES}
        expected |= {'404.html', '_headers', 'robots.txt', 'sitemap.xml'}
        actual = {p.relative_to(self.output).as_posix() for p in self.output.rglob('*') if p.is_file()}
        self.assertEqual(actual, expected)
        self.assertFalse(any(name.startswith(('api/', 'data/', 'templates/')) for name in actual))
        self.assertFalse(any(name.endswith(('.py', '.bak', '.backup', '.md')) for name in actual))
        self.assertGreater(self.result['references'], 1000)

    def test_public_json_matches_the_reviewed_sources_and_local_development(self):
        client = app.test_client()
        for route, filename in PUBLIC_DATA_FILES.items():
            with self.subTest(route=route):
                expected = json.loads((ROOT / filename).read_text())
                self.assertEqual(json.loads((self.output / route.lstrip('/')).read_text()), expected)
                self.assertEqual(client.get(route).get_json(), expected)
        faq = (self.output / 'static/js/faq-assistant.js').read_text()
        self.assertIn("fetchFAQ('/content/faq.json'", faq)
        self.assertNotIn('/api/', faq)
        self.assertIn('AI answers to your own questions are coming soon.', faq)

    def test_canonical_navigation_and_search_metadata(self):
        for route in PAGE_ROUTES:
            html = (self.output / page_output(route)).read_text()
            self.assertIn(f'<link rel="canonical" href="{ORIGIN}{canonical_path(route)}">', html)
            self.assertNotIn('content="noindex', html)
        faq = (self.output / 'faq/index.html').read_text()
        self.assertIn('class="nav-link nav-link-active">FAQ', faq)
        self.assertIn('These FAQs are prepared', faq)
        self.assertIn('Last updated:', (self.output / 'research-updates/index.html').read_text())
        not_found = (self.output / '404.html').read_text()
        self.assertIn('404 - Page Not Found', not_found)
        self.assertIn('noindex, nofollow', not_found)
        self.assertNotIn('rel="canonical"', not_found)
        sitemap = ET.parse(self.output / 'sitemap.xml')
        urls = [element.text for element in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        self.assertEqual(urls, [ORIGIN + canonical_path(route) for route in PAGE_ROUTES])
        self.assertIn(f'Sitemap: {ORIGIN}/sitemap.xml', (self.output / 'robots.txt').read_text())

    def test_repeat_build_is_identical_and_never_calls_legacy_apis(self):
        output = Path(self.temporary.name) / 'repeat'
        called = []
        original = app.full_dispatch_request
        def dispatch():
            from flask import request
            called.append(request.path)
            self.assertFalse(request.path.startswith('/api/'))
            return original()
        with patch.object(app, 'full_dispatch_request', side_effect=dispatch):
            builder.export_site(output, ORIGIN)
        self.assertEqual(set(called), set(PAGE_ROUTES) | set(PUBLIC_DATA_FILES) | {'/_static-export-not-found'})
        for source in self.output.rglob('*'):
            if source.is_file():
                other = output / source.relative_to(self.output)
                self.assertEqual(hashlib.sha256(source.read_bytes()).digest(), hashlib.sha256(other.read_bytes()).digest())

    def test_preview_blocks_indexing_and_uses_production_canonical(self):
        output = Path(self.temporary.name) / 'preview'
        builder.export_site(output, ORIGIN, noindex=True)
        for route in PAGE_ROUTES:
            html = (output / page_output(route)).read_text()
            self.assertIn('noindex, nofollow', html)
            self.assertIn(ORIGIN + canonical_path(route), html)
        self.assertEqual((output / 'robots.txt').read_text(), 'User-agent: *\nDisallow: /\n')
        self.assertIn('X-Robots-Tag: noindex, nofollow', (output / '_headers').read_text())
        with patch.dict(os.environ, {'CF_PAGES_BRANCH': 'codex/test-export'}, clear=True):
            self.assertEqual(builder.settings(), (ORIGIN, True))
        with patch.dict(os.environ, {'CF_PAGES_BRANCH': 'main'}, clear=True):
            self.assertEqual(builder.settings(), (ORIGIN, False))

    def test_only_valid_https_origins_are_accepted(self):
        self.assertEqual(builder.normalize_origin(ORIGIN + '/'), ORIGIN)
        for value in ['http://als.carekosh.com', '//als.carekosh.com', 'https://localhost',
                      ORIGIN + '/path', ORIGIN + '?x=1', ORIGIN + '#a', ORIGIN + ':443',
                      'https://name:secret@carekosh.com', 'https://carekosh.com\\bad']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                builder.normalize_origin(value)

    def test_missing_sources_do_not_silently_publish_flask_fallbacks(self):
        output = Path(self.temporary.name) / 'missing'
        with patch.dict(builder.PUBLIC_DATA_FILES, {'/content/faq.json': 'data/missing-static-test.json'}):
            with self.assertRaises(FileNotFoundError):
                builder.export_site(output, ORIGIN)

    def test_validator_catches_missing_assets_and_backend_calls(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'index.html').write_text('<img src="/static/missing.png">')
            with self.assertRaisesRegex(ValueError, 'missing'):
                builder.validate_output(root)
            (root / 'index.html').write_text('<script>fetch("/api/community-faq")</script>')
            with self.assertRaisesRegex(ValueError, 'Backend URL'):
                builder.validate_output(root)
            (root / 'index.html').write_text('{{ unfinished }}')
            with self.assertRaisesRegex(ValueError, 'Unresolved template'):
                builder.validate_output(root)

    def test_asset_allowlist_rejects_traversal_symlinks_backups_and_oversize(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'static').mkdir()
            (root / 'outside.js').write_text('private')
            (root / 'static/linked.js').symlink_to(root / 'outside.js')
            (root / 'static/large.png').touch()
            with (root / 'static/large.png').open('r+b') as file:
                file.truncate(builder.MAX_FILE_BYTES + 1)
            for relative in ['../outside.js', '/static/x.js', 'static/../outside.js',
                             'static/.secret.js', 'static/style.css.backup', 'static/linked.js',
                             'static/missing.js', 'static/large.png', 'static/private.txt']:
                with self.subTest(relative=relative), self.assertRaises(ValueError):
                    builder.checked_asset(relative, root)

    def test_export_refuses_nonempty_output_and_unsafe_replace_targets(self):
        with self.assertRaisesRegex(ValueError, 'empty'):
            builder.export_site(self.output, ORIGIN)
        sentinel = self.output / 'index.html'
        original = sentinel.read_bytes()
        with self.assertRaisesRegex(ValueError, 'Only the real project dist'):
            builder.publish_output(Path(self.temporary.name) / 'unused', self.output)
        self.assertEqual(sentinel.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
