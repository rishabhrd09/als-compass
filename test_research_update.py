"""Update-workflow tests use temporary copies; they never edit the live review."""
from contextlib import redirect_stdout
from datetime import date, timedelta
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import research_update as updater


class UpdateWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'data').mkdir()
        self.live = self.root / updater.LIVE_FILE
        shutil.copy2(updater.ROOT / updater.LIVE_FILE, self.live)
        self.original = self.live.read_bytes()
        baseline = updater.read_json(self.live)
        snapshot_name = f'research_registry_snapshot_{baseline["last_updated"]}.json'
        shutil.copy2(updater.ROOT / 'data' / snapshot_name, self.root / 'data' / snapshot_name)
        with redirect_stdout(io.StringIO()):
            self.run = updater.prepare(self.root, offline=True)

    def reviewed_fixture(self):
        """Simulate review declarations for validation tests, not real research."""
        draft = updater.read_json(self.run / 'draft.json')
        today = date.today().isoformat()
        draft.update(last_updated=today, reviewed_on=today)
        for source in draft['source_library']:
            source['accessed_on'] = today
        audit = updater.read_json(self.run / 'review.json')
        audit['reviewed_on'] = today
        for key, entry in updater.entries(draft).items():
            audit['entries'][key] = dict(reviewed=True, source_ids=entry['source_ids'], note='Test fixture only; not a medical review.')
        for group in ('discovery', 'issues'):
            for item in audit[group].values():
                item.update(reviewed=True, resolved=True, source_urls=['https://clinicaltrials.gov/'], note='Test fixture evidence.')
        updater.write_json(self.run / 'draft.json', draft)
        updater.write_json(self.run / 'review.json', audit)
        return draft, audit

    def test_prepare_never_changes_live_content_or_dates(self):
        self.assertEqual(self.live.read_bytes(), self.original)
        self.assertEqual((self.run / 'draft.json').read_bytes(), self.original)
        self.assertIn('offline', updater.read_json(self.run / 'manifest.json')['issues'])
        self.assertTrue((self.run / 'PROMPT.md').exists())
        with self.assertRaises(ValueError):
            updater.validate_run(self.run, self.root)

    def test_missing_entry_review_and_silent_deletion_are_blocked(self):
        draft, audit = self.reviewed_fixture()
        first = next(iter(audit['entries']))
        audit['entries'][first]['reviewed'] = False
        updater.write_json(self.run / 'review.json', audit)
        with self.assertRaisesRegex(ValueError, 'complete the evidence review'):
            updater.validate_run(self.run, self.root)
        self.reviewed_fixture()
        draft['categories']['clinical_trials'].pop()
        updater.write_json(self.run / 'draft.json', draft)
        with self.assertRaisesRegex(ValueError, 'Keep existing entry IDs'):
            updater.validate_run(self.run, self.root)

    def test_discovery_and_fetch_failures_require_resolution(self):
        draft, audit = self.reviewed_fixture()
        audit['issues']['offline']['resolved'] = False
        updater.write_json(self.run / 'review.json', audit)
        with self.assertRaisesRegex(ValueError, 'resolve the collection issue'):
            updater.validate_run(self.run, self.root)
        _, audit = self.reviewed_fixture()
        audit['discovery']['india']['reviewed'] = False
        updater.write_json(self.run / 'review.json', audit)
        with self.assertRaisesRegex(ValueError, 'document discovery'):
            updater.validate_run(self.run, self.root)

    def test_stale_baseline_blocks_overwriting_newer_work(self):
        self.reviewed_fixture()
        self.live.write_bytes(self.original + b'\n')
        with self.assertRaisesRegex(ValueError, 'live review changed'):
            updater.apply_run(self.run, self.root)
        self.assertEqual(self.live.read_bytes(), self.original + b'\n')
        self.assertFalse((self.root / '.research-updates/apply.lock').exists())

    def test_registry_and_source_dates_must_agree(self):
        draft, _ = self.reviewed_fixture()
        entry = next(item for item in updater.entries(draft).values() if 'registry' in item)
        entry['registry']['status'] = 'COMPLETED'
        updater.write_json(self.run / 'draft.json', draft)
        with self.assertRaisesRegex(ValueError, 'synchronize the registry snapshot'):
            updater.validate_run(self.run, self.root)

    def test_validated_apply_backs_up_and_writes_matching_snapshot(self):
        draft, _ = self.reviewed_fixture()
        updater.validate_run(self.run, self.root)
        self.assertTrue((self.run / 'CHANGES.diff').exists())
        with redirect_stdout(io.StringIO()):
            updater.apply_run(self.run, self.root)
        self.assertEqual(updater.read_json(self.live), draft)
        self.assertEqual((self.run / 'backup/research_categorized.json').read_bytes(), self.original)
        snapshot_path = self.root / 'data' / f'research_registry_snapshot_{draft["last_updated"]}.json'
        self.assertEqual(updater.read_json(snapshot_path)['evidence_cutoff'], draft['last_updated'])
        self.assertTrue((self.run / 'APPLIED.json').exists())

    def test_failed_write_preserves_live_json_and_unlocks(self):
        self.reviewed_fixture()
        atomic_write = updater.atomic_write
        def fail_live_write(path, content):
            if path == self.live:
                raise OSError('Simulated disk error')
            return atomic_write(path, content)
        with patch.object(updater, 'atomic_write', side_effect=fail_live_write):
            with self.assertRaisesRegex(OSError, 'Simulated disk error'):
                updater.apply_run(self.run, self.root)
        self.assertEqual(self.live.read_bytes(), self.original)
        self.assertFalse((self.root / '.research-updates/apply.lock').exists())

    def test_future_cutoff_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'future-dated'):
            updater.prepare(self.root, as_of=(date.today() + timedelta(days=1)).isoformat(), offline=True)

    def test_collector_records_network_errors_without_touching_live(self):
        snapshot = updater.read_json(self.run / 'registry_snapshot.json')
        with patch.object(updater, 'get_json', side_effect=OSError('Network unavailable')):
            issues, changes = updater.collect(self.run, updater.read_json(self.live), date.today().isoformat(), snapshot)
        self.assertIn('pubmed-discovery', issues)
        self.assertIn('registry-discovery', issues)
        self.assertTrue(any(key.startswith('NCT') for key in issues))
        self.assertEqual(changes, [])
        self.assertEqual(self.live.read_bytes(), self.original)

    def test_collector_preserves_new_status_and_flags_truncation(self):
        baseline = updater.read_json(self.live)
        snapshot = updater.read_json(self.run / 'registry_snapshot.json')
        by_id = {item['id']: item for item in snapshot['records']}
        def fake_get(url, params=None):
            if url == updater.PUBMED_API:
                return {'esearchresult': {'idlist': ['12345'], 'count': '501'}}
            if url == updater.REGISTRY_API:
                return {'studies': [], 'totalCount': 0}
            record_id = url.rsplit('/', 1)[-1]
            old = by_id[record_id]
            return {'protocolSection': {
                'identificationModule': {'nctId': record_id},
                'statusModule': {'overallStatus': 'COMPLETED', 'lastUpdatePostDateStruct': {'date': date.today().isoformat()}},
                'designModule': {'phases': old['phase']},
                'contactsLocationsModule': {'locations': [{'country': country} for country in old['countries']]}
            }, 'hasResults': True}
        with patch.object(updater, 'get_json', side_effect=fake_get):
            issues, changes = updater.collect(self.run, baseline, date.today().isoformat(), snapshot)
        self.assertGreater(len(changes), 0)
        self.assertIn('pubmed-discovery', issues)
        self.assertTrue(all(item['after']['results_posted'] for item in changes))

    def test_page_title_and_download_follow_next_edition(self):
        from app import app
        draft = updater.read_json(self.live)
        draft['last_updated'] = '2030-01-02'
        with patch('app.load_research_data', return_value=draft):
            html = app.test_client().get('/research-updates').get_data(as_text=True)
        self.assertIn('Evidence through 2 January 2030 | ALS Compass</title>', html)
        self.assertIn('download="als-research-2030-01-02.json"', html)


if __name__ == '__main__':
    unittest.main()
