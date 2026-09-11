"""Check the real gallery data and rendered routes, including original image links."""
import json
import unittest
from pathlib import Path
from collections import Counter

from test_power_pages import Page
from app import app

ROOT = Path(__file__).resolve().parents[1]


class EquipmentPageTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.gallery = json.loads((ROOT / 'data/icu_equipment_images.json').read_text())

    def page(self, route):
        response = self.client.get(route)
        self.assertEqual(response.status_code, 200)
        return Page(response.get_data(as_text=True))

    def test_every_equipment_entry_has_a_local_preview_and_original(self):
        self.assertEqual(len(self.gallery['groups']), 9)
        items = [item for group in self.gallery['groups'] for item in group['items']]
        self.assertEqual(len(items), 45)
        items += self.gallery['caregiver_gallery']
        for item in items:
            with self.subTest(item=item['name']):
                self.assertTrue(item['images'])
                for photo in item['images']:
                    self.assertTrue(photo['caption'])
                    self.assertTrue(photo['credit'])
                    self.assertGreater(photo['width'], 0)
                    self.assertGreater(photo['height'], 0)
                    for kind in ['src', 'preview']:
                        with self.client.get(photo[kind]) as response:
                            self.assertEqual(response.status_code, 200, photo[kind])
                            self.assertTrue(response.content_type.startswith('image/'))
                    if photo.get('source'):
                        self.assertTrue(photo['source'].startswith('https://'))

    def test_gallery_renders_every_photo_as_an_expandable_link(self):
        page = self.page('/home-icu-guide')
        ids = Counter(attrs['id'] for _, attrs in page.nodes if 'id' in attrs)
        self.assertTrue(all(count == 1 for count in ids.values()))
        expected = [photo['src'] for group in self.gallery['groups'] for item in group['items'] for photo in item['images']]
        expected += [photo['src'] for item in self.gallery['caregiver_gallery'] for photo in item['images']]
        expected += ['/static/images/icu-guide/alscas-home-icu-setup.png']
        links = [attrs for tag, attrs in page.nodes if tag == 'a' and 'data-care-image' in attrs]
        self.assertCountEqual([link['href'] for link in links], expected)
        for link in links:
            self.assertTrue(link['data-caption'])
            self.assertTrue(link['data-credit'])
        self.assertEqual(page.by_id('careImageViewer')['aria-labelledby'], 'careImageTitle')
        for route in ['/power-backup-guide', '/ups-faq']:
            page = self.page(route)
            self.assertEqual(sum(tag == 'a' and 'data-care-image' in attrs for tag, attrs in page.nodes), 3)

    def test_static_pages_omit_hero_motion_script_and_share_the_experience_note(self):
        for route in ['/home-icu-guide', '/faq', '/inventory-management', '/power-backup-guide', '/ups-faq', '/emergency-protocol']:
            page = self.page(route)
            scripts = [attrs.get('src', '') for tag, attrs in page.nodes if tag == 'script']
            self.assertNotIn('/static/js/guide-atmosphere.js', scripts)
            if route in ['/home-icu-guide', '/faq']:
                subject = 'FAQs' if route == '/faq' else 'knowledge cards'
                self.assertEqual(' '.join(page.text).count(f'These {subject} are prepared from conversations in the ALSCAS WhatsApp group'), 1)
            elif route == '/inventory-management':
                self.assertEqual(' '.join(page.text).count('This guide shares personal experience'), 1)
        page = self.page('/understanding-als')
        # The user's preferred neural animation remains on the educational page.
        self.assertTrue(any('three' in attrs.get('src', '') for tag, attrs in page.nodes if tag == 'script'))

    def test_disclaimer_guidance_is_shared_and_new_poster_expands(self):
        pages = [self.page(route) for route in ['/faq', '/home-icu-guide']]
        disclaimers = [next(text for text in page.text if 'are prepared from conversations' in text).split('are prepared', 1)[1].strip() for page in pages]
        self.assertEqual(disclaimers[0], disclaimers[1])
        self.assertIn('do not replace medical advice', disclaimers[0])
        self.assertIn('choose what is best for your loved one', disclaimers[0])
        poster = next(attrs for tag, attrs in pages[1].nodes if tag == 'a' and attrs.get('href') == '/static/images/icu-guide/alscas-home-icu-setup.png')
        self.assertIn('data-care-image', poster)
        with self.client.get(poster['href']) as response:
            self.assertEqual(response.status_code, 200)

    def test_faq_api_retains_existing_topics_and_only_text_answers(self):
        response = self.client.get('/api/community-faq')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual([(group['id'], len(group['questions'])) for group in data['categories']], [
            ('respiratory', 9), ('feeding', 3), ('mindset', 1), ('daily-care', 5), ('equipment', 3), ('mobility', 1)])
        for group in data['categories']:
            for question in group['questions']:
                answer = Page(question['answer'])
                self.assertTrue(question['sources'])
                self.assertFalse(any(tag == 'img' for tag, _ in answer.nodes))
                self.assertTrue(any(tag == 'h4' or tag == 'table' for tag, _ in answer.nodes))
                for tag, attrs in answer.nodes:
                    if tag == 'th':
                        self.assertIn(attrs.get('scope'), ['row', 'col'])
                    if tag == 'a' and attrs.get('href', '').startswith('/'):
                        with self.client.get(attrs['href'].split('#')[0]) as result:
                            self.assertEqual(result.status_code, 200)


if __name__ == '__main__':
    unittest.main()
