"""Editorial regression checks for the restored caregiver FAQ, not clinical validation."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAQ = json.loads((ROOT / 'data/als_comprehensive_faq.json').read_text())
QUESTIONS = {q['question']: q for c in FAQ['categories'] for q in c['questions']}


class AnswerMarkup(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.parts = [], [], []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'iframe', 'img', 'style', 'object'}:
            self.errors.append(f'Unexpected {tag}')
        if tag in {'p', 'div', 'table', 'ul', 'ol', 'h4'} and 'p' in self.stack:
            self.errors.append(f'{tag} nested inside paragraph')
        if tag == 'th' and dict(attrs).get('scope') not in {'row', 'col'}:
            self.errors.append('Table heading without scope')
        if any(name.lower().startswith('on') for name, _ in attrs):
            self.errors.append('Inline event handler')
        if tag not in {'br', 'hr'}:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f'Unbalanced closing {tag}')
        else:
            self.stack.pop()

    def handle_data(self, data):
        self.parts.append(data)

    @property
    def text(self):
        return ' '.join(' '.join(self.parts).split())


class FAQRestorationTests(unittest.TestCase):
    def test_original_caregiver_explanation_is_not_lost_to_generic_summary(self):
        text = AnswerMarkup(QUESTIONS['Why Do Families Delay BiPAP Even After Knowing the Signs?']['answer']).text
        # These approved original sentences are deliberately protected. An
        # intentional editorial change should review these expectations too.
        for sentence in [
            'When we are in the caregiver role, we are often overwhelmed with anxiety and fear.',
            'Even after reading messages and knowing the signs, actually making the decision feels very different',
            'What seems obvious to those already using BiPAP is not obvious to those facing the decision for the first time.',
        ]:
            self.assertIn(sentence, text)

    def test_specific_everyday_details_survive_content_updates(self):
        examples = {
            'How Do I Manage Excessive Saliva/Drooling?': ['Keep a soft cloth handy at all times.', 'Yankauer', 'Oral Care'],
            'When should we consider a feeding tube (PEG)?': ['Meal takes too long', 'Fear of eating', 'Exhaustion after meals'],
            'How to Set Up a Home ICU Room for BiPAP + Tracheostomy?': ['Keep things simple and organized.', 'Backup Items', 'Syringes'],
            'Will using a power wheelchair or lift make the PALS weaker faster?': ['maintain energy for essential activities', 'breathing, swallowing, and communicating'],
        }
        for title, details in examples.items():
            text = AnswerMarkup(QUESTIONS[title]['answer']).text
            for detail in details:
                with self.subTest(question=title, detail=detail):
                    self.assertIn(detail, text)
        self.assertIn('Rent first, then decide if purchase makes sense.', QUESTIONS['What Equipment Do We Need as ALS Progresses?']['recommendation'])

    def test_restored_answers_have_balanced_readable_markup(self):
        for title, question in QUESTIONS.items():
            with self.subTest(question=title):
                parsed = AnswerMarkup(question['answer'])
                self.assertEqual(parsed.errors, [])
                self.assertEqual(parsed.stack, [])
                self.assertTrue(parsed.text.strip())


if __name__ == '__main__':
    unittest.main()
