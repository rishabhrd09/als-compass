"""Integration checks for the optional neuron lesson and its readable fallback."""
import unittest
from html.parser import HTMLParser

from app import app


class Markup(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class NeuronLessonPageTests(unittest.TestCase):
    def test_page_loads_dependencies_in_order_and_accessible_descriptions_resolve(self):
        client = app.test_client()
        response = client.get('/understanding-als')
        self.assertEqual(response.status_code, 200)
        markup = Markup(response.get_data(as_text=True))
        scripts = [attrs['src'] for tag, attrs in markup.tags if tag == 'script' and 'src' in attrs]
        dependencies = ['/static/vendor/three-r128.min.js',
                        '/static/js/education/neuron-lesson.js',
                        '/static/js/education/neuron-model.js',
                        '/static/js/education/understanding.js']
        positions = [scripts.index(src) for src in dependencies]
        self.assertEqual(positions, sorted(positions))
        for src in dependencies:
            with self.subTest(asset=src):
                with client.get(src) as asset:
                    self.assertEqual(asset.status_code, 200)
        ids = [attrs['id'] for _, attrs in markup.tags if 'id' in attrs]
        self.assertEqual(len(ids), len(set(ids)))
        canvas = next(attrs for _, attrs in markup.tags if attrs.get('id') == 'neuron-canvas')
        for identifier in canvas['aria-describedby'].split():
            self.assertIn(identifier, ids)
        for _, attrs in markup.tags:
            if any(key in attrs for key in ('data-camera', 'data-neuron-state')):
                self.assertIn('disabled', attrs, 'controls must stay disabled until the 3D view initializes')

    def test_plain_html_explains_the_sequence_and_limits_without_animation(self):
        html = app.test_client().get('/understanding-als').get_data(as_text=True)
        lesson = html.split('id="neuron-explorer"', 1)[1].split('class="film-section"', 1)[0]
        for phrase in ['lower motor neuron', 'upper motor neurons', 'Electrical signal',
                       'Chemical messenger', 'Muscle response', 'acetylcholine',
                       'junction gap is enlarged', 'signals are slowed down',
                       'Wasting happens over time', 'does not represent recovery']:
            self.assertIn(phrase, lesson)
        self.assertNotIn('THE COMPLETE PATHWAY', lesson)
        self.assertIn('without JavaScript', lesson)


if __name__ == '__main__':
    unittest.main()
