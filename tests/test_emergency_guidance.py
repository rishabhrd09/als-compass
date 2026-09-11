"""Guard against unsafe duplicated emergency instructions and delayed escalation."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

from app import app

ROOT = Path(__file__).resolve().parents[1]


class Markup(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.words, self.links = [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs).get('href'))

    def handle_data(self, data):
        self.words.append(data)

    @property
    def text(self):
        return ' '.join(' '.join(self.words).split())


class EmergencyGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_emergency_page_puts_call_and_training_boundaries_before_decisions(self):
        response = self.client.get('/emergency-protocol')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        notice = html.split('id="experienceNoticeTitle"', 1)[1].split('</aside>', 1)[0]
        text = Markup(notice).text
        for phrase in ['Call 112 immediately', 'trained', 'respiratory therapist', 'ICU nurse',
                       'technician', 'at the same time', 'stop repeated attempts', 'speakerphone']:
            self.assertIn(phrase, text)
        self.assertLess(html.index('id="experienceNoticeTitle"'), html.index('id="decision-flowchart"'))
        self.assertIn('https://112.gov.in/', Markup(html).links)
        self.assertNotIn('emergency_protocol_infographic.png', html)

    def test_both_flowchart_and_written_situation_explain_blocked_tube_escalation(self):
        html = self.client.get('/emergency-protocol').get_data(as_text=True)
        for start, end in [('<!-- Situation A Detail -->', '<!-- Situation B Detail -->'),
                           ('id="care-section-4"', 'id="care-section-5"'),
                           ('id="airway-escalation"', '<!-- Quick Reference -->')]:
            text = Markup(html.split(start, 1)[1].split(end, 1)[0]).text.lower()
            with self.subTest(section=start):
                for phrase in ['blocked or displaced', 'call 112', 'do not force', 'patency', 'trained']:
                    self.assertIn(phrase, text)
                self.assertRegex(text, r'replacement|removal')

    def test_unsafe_cycles_are_not_left_in_visible_page_or_fallback_sources(self):
        texts = [self.client.get('/emergency-protocol').get_data(as_text=True)]
        for name in ['als_community_faq', 'als_community_faq_enhanced',
                     'practical_wisdom_faq', 'whatsapp_detailed_faq']:
            texts.append((ROOT / f'data/{name}.json').read_text())
        for text in texts:
            normalized = ' '.join(text.split()).lower()
            for pattern in [r'aggressive ambu', r'firm ambu squeezes', r'ns.{0,15}\+.{0,15}ambu',
                            r'repeat until pals', r'when in doubt, give ambu', r'continue aggressive']:
                self.assertNotRegex(normalized, pattern)

    def test_main_and_fallback_faq_include_same_urgent_airway_boundary(self):
        data = self.client.get('/api/community-faq').get_json()
        question = data['categories'][2]['questions'][0]
        text = Markup(question['answer']).text
        for phrase in ['Call 112 immediately', 'respiratory therapist', 'ICU nurse',
                       'specific clinical training', 'Do not force', 'stop repeated attempts']:
            self.assertIn(phrase, text)
        self.assertIn('/emergency-protocol#airway-escalation', Markup(question['answer']).links)
        for name in ['als_community_faq', 'als_community_faq_enhanced']:
            data = json.loads((ROOT / f'data/{name}.json').read_text())
            emergency = next(c for c in data['categories'] if c['id'] == 'emergency')
            self.assertIn('individualized emergency plan', emergency['description'])
            for q in emergency['questions']:
                self.assertIn('Call 112 immediately', q['answer'])
                self.assertIn('patency', q['answer'])
                self.assertTrue(q['sources'])
            blocked = emergency['questions'][0]['conditional']['if_then'][2]
            self.assertIn('respiratory therapist', blocked['then'])

    def test_situation_lists_are_in_the_correct_sections_and_tags_are_balanced(self):
        # Parse just the changed content, so inherited layout or scripts do not hide mismatched tags.
        source = (ROOT / 'templates/emergency_protocol.html').read_text().split('{% block care_content %}', 1)[1]
        class Balanced(HTMLParser):
            def __init__(self):
                super().__init__(); self.stack = []; self.errors = []
            def handle_starttag(self, tag, attrs):
                if tag not in {'br', 'img', 'hr', 'input', 'meta', 'link', 'source'}:
                    self.stack.append(tag)
            def handle_endtag(self, tag):
                if not self.stack or self.stack[-1] != tag:
                    self.errors.append((tag, self.stack[-3:]))
                else:
                    self.stack.pop()
        parser = Balanced(); parser.feed(source)
        self.assertEqual(parser.errors, [])
        self.assertEqual(parser.stack, [])
        suction = Markup(source.split('PRESCRIBED SUCTION', 1)[1].split('</ol>', 1)[0]).text
        self.assertIn('Suction only if indicated', suction)
        self.assertNotIn('blood pressure', suction)
        pulse = Markup(source.split('id="care-section-5"', 1)[1].split('id="care-section-6"', 1)[0]).text
        self.assertIn('Contact the treating doctor', pulse)
        self.assertNotIn('clearance cycle', pulse)


if __name__ == '__main__':
    unittest.main()
