"""Render the power guidance and check its form, links and evidence boundaries."""
import unittest
from collections import Counter
from html.parser import HTMLParser

from app import app


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.text = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)

    def by_id(self, target):
        return next(attrs for _, attrs in self.nodes if attrs.get('id') == target)


class PowerPageTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def page(self, route):
        response = self.client.get(route)
        self.assertEqual(response.status_code, 200)
        return Page(response.get_data(as_text=True))

    def test_related_pages_render_with_valid_local_assets_and_section_links(self):
        for route in ['/power-backup-guide', '/ups-faq', '/emergency-protocol', '/home-icu-guide']:
            with self.subTest(route=route):
                page = self.page(route)
                ids = Counter(attrs['id'] for _, attrs in page.nodes if 'id' in attrs)
                self.assertTrue(all(count == 1 for count in ids.values()), ids)
                for tag, attrs in page.nodes:
                    if tag in ('script', 'img') or (tag == 'link' and attrs.get('rel') == 'stylesheet'):
                        url = attrs.get('src') or attrs.get('href', '')
                        if url.startswith('/static/'):
                            with self.client.get(url) as asset:
                                self.assertEqual(asset.status_code, 200, url)
                    if tag == 'a' and attrs.get('href', '').startswith('#') and len(attrs['href']) > 1:
                        self.assertIn(attrs['href'][1:], ids)

    def test_calculator_loads_model_before_ui_and_fails_closed(self):
        page = self.page('/power-backup-guide')
        scripts = [attrs['src'] for tag, attrs in page.nodes if tag == 'script' and 'src' in attrs]
        self.assertLess(scripts.index('/static/js/power/calculations.js'), scripts.index('/static/js/power/calculator-ui.js'))
        self.assertIn('disabled', page.by_id('powerCalculatorControls'))
        self.assertIn('hidden', page.by_id('calcResults'))
        self.assertIn('disabled', page.by_id('batteryModelFields'))
        self.assertNotIn('checked', page.by_id('includeBatteryModel'))
        runtime = next(attrs for tag, attrs in page.nodes if attrs.get('data-field') == 'usagePct')
        self.assertEqual(runtime['value'], '100')
        self.assertNotIn('value', page.by_id('usableFraction'))

    def test_power_pages_share_corrected_reference_and_source_links(self):
        for route in ['/power-backup-guide', '/ups-faq']:
            page = self.page(route)
            text = ' '.join(page.text)
            for required in ['291.25 W', '3,024 Wh', 'Reported household use', 'two hours per day', 'not a treatment schedule']:
                self.assertIn(required, text)
            hrefs = [attrs.get('href', '') for _, attrs in page.nodes]
            self.assertIn('https://oxymedindia.com/oxymed-10', hrefs)
            self.assertIn('https://www.crsbis.in/BIS/registration-page.do', hrefs)

    def test_emergency_page_attributes_experience_and_provides_escalation(self):
        page = self.page('/emergency-protocol')
        text = ' '.join(page.text)
        self.assertIn('not a clinician-validated emergency protocol', text)
        self.assertIn('personal caregiving experience', text)
        self.assertTrue(any(attrs.get('href') == 'tel:112' for _, attrs in page.nodes))


if __name__ == '__main__':
    unittest.main()
