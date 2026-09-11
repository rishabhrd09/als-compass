"""Regression checks for the sourced research page and its shared data."""
import copy
import json
import re
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from app import app, load_research_data, research_date
from research_schema import validate_research


class ResearchReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_research_data()
        cls.client = app.test_client()

    def test_source_graph_and_cutoff(self):
        validate_research(self.data)
        self.assertLessEqual(date.fromisoformat(self.data['last_updated']), date.fromisoformat(self.data['reviewed_on']))
        used = {key for group in self.data['categories'].values() for entry in group for key in entry['source_ids']}
        self.assertEqual(used, {source['id'] for source in self.data['source_library']})

    def test_registry_statuses_match_preserved_snapshot(self):
        snapshot = json.loads((Path(__file__).parent / 'data' / f'research_registry_snapshot_{self.data["last_updated"]}.json').read_text())
        records = {record['id']: record for record in snapshot['records']}
        for group in self.data['categories'].values():
            for entry in group:
                if 'registry' in entry:
                    self.assertEqual(entry['registry'], records[entry['registry']['id']])

    def test_every_entry_and_reference_exists_without_javascript(self):
        response = self.client.get('/research-updates')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        ids = re.findall(r'\bid="([^"]+)"', html)
        self.assertEqual(len(ids), len(set(ids)), 'Duplicate DOM IDs break deep links')
        for group in self.data['categories'].values():
            for entry in group:
                self.assertIn('research-' + entry['id'], ids)
        for source in self.data['source_library']:
            self.assertIn('source-' + source['id'], ids)
        for target in re.findall(r'href="#([^"]+)"', html):
            self.assertIn(target, ids, 'Broken internal link: ' + target)
        self.assertNotIn('data-entry hidden', html)
        self.assertIn('Last updated: <time datetime="' + self.data['last_updated'] + '">' + research_date(self.data['last_updated']) + '</time>', html)

    def test_homepage_and_api_share_review(self):
        self.assertEqual(self.client.get('/api/research-categorized').get_json(), self.data)
        html = self.client.get('/').get_data(as_text=True)
        for entry_id in self.data['homepage_entries']:
            self.assertIn('/research-updates#research-' + entry_id, html)
        self.assertIn('Evidence through ' + research_date(self.data['last_updated']), html)

    def test_unavailable_snapshot_does_not_fabricate_a_review_date(self):
        with patch('app.RESEARCH_DATA_PATH', Path('/tmp/als-compass-missing-research-file.json')), self.assertLogs('app', level='ERROR'):
            self.assertEqual(self.client.get('/research-updates').status_code, 503)
            response = self.client.get('/api/research-categorized')
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('last_updated', response.get_json())
            self.assertEqual(self.client.get('/').status_code, 200)

    def test_rejects_legacy_and_broken_reference_drafts(self):
        for mutate in [lambda data: data.pop('schema_version'),
                       lambda data: data['source_library'].pop(0),
                       lambda data: data['source_library'][0].update(published_on=(date.fromisoformat(data['last_updated']) + timedelta(days=1)).isoformat()),
                       lambda data: data['sections'].pop(),
                       lambda data: data['homepage_entries'].append('missing-entry')]:
            draft = copy.deepcopy(self.data)
            mutate(draft)
            with self.assertRaises(ValueError):
                validate_research(draft)

    def test_autoescaping_keeps_research_text_as_text(self):
        draft = copy.deepcopy(self.data)
        draft['categories']['approved_treatments'][0]['name'] = '<script>alert("bad")</script>'
        with patch('app.load_research_data', return_value=draft):
            html = self.client.get('/research-updates').get_data(as_text=True)
            self.assertNotIn('<script>alert(', html)
            self.assertIn('&lt;script&gt;', html)

    def test_communication_consumers_keep_required_fields(self):
        for entry in self.data['categories']['communication_technology']:
            for key in ['solution_name', 'category', 'form_factor', 'status', 'what_it_is', 'how_it_works', 'india_availability']:
                self.assertTrue(entry[key])
            self.assertIsInstance(entry['limitations'], list)
        for entry in self.data['categories']['experimental_communication_tech']:
            for key in ['technology', 'status', 'risk_level', 'what_it_is', 'who_can_try', 'cost', 'recommendation']:
                self.assertTrue(entry[key])

    def test_partial_dates_do_not_invent_a_day(self):
        self.assertEqual(research_date('2025-06'), 'June 2025')
        self.assertEqual(research_date('2026-09-10'), '10 September 2026')
        self.assertEqual(research_date(None), 'Publication date not stated')


if __name__ == '__main__':
    unittest.main()
