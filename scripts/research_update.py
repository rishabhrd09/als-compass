#!/usr/bin/env python3
"""Prepare, validate and apply sourced ALS research updates. No LLM/API key required.

Collection produces leads, never clinical conclusions. Run the generated research
prompt in a browsing-capable assistant before validating/applying the draft.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research_schema import validate_research

LIVE_FILE = Path('data/research_categorized.json')
REGISTRY_API = 'https://clinicaltrials.gov/api/v2/studies'
PUBMED_API = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def json_text(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + '\n'


def write_json(path, data):
    path.write_text(json_text(data), encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries(data):
    return {entry['id']: entry for group in data['categories'].values() for entry in group}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def get_json(url, params=None):
    if params:
        url += '?' + urlencode(params)
    for attempt in range(2):
        try:
            request = Request(url, headers={'User-Agent': 'ALSCompassResearchReview/1.0', 'Accept': 'application/json'})
            with urlopen(request, timeout=20) as response:
                payload = json.load(response)
            if 'error' in payload:
                raise ValueError(str(payload['error']))
            return payload
        except (OSError, ValueError):
            if attempt:
                raise
            time.sleep(1)


def registry_summary(raw):
    protocol = raw['protocolSection']
    record_id = protocol['identificationModule']['nctId']
    status = protocol['statusModule']
    return dict(id=record_id, url='https://clinicaltrials.gov/study/' + record_id,
                status=status['overallStatus'], updated_on=status['lastUpdatePostDateStruct']['date'],
                phase=protocol.get('designModule', {}).get('phases', []),
                countries=sorted({site['country'] for site in protocol.get('contactsLocationsModule', {}).get('locations', []) if site.get('country')}),
                results_posted=raw.get('hasResults', False))


def collect(run, baseline, cutoff, snapshot):
    """Fetch tracked studies and discovery leads; preserve every failure explicitly."""
    issues, changes = {}, []
    records = {record['id']: record for record in snapshot['records']}
    nct_ids = sorted(set(re.findall(r'\bNCT\d{8}\b', json.dumps(baseline))))
    (run / 'registry').mkdir()
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(get_json, REGISTRY_API + '/' + nct): nct for nct in nct_ids}
        for job in as_completed(jobs):
            nct = jobs[job]
            try:
                raw = job.result()
                current = registry_summary(raw)
                require(current['id'] == nct, 'Registry returned a different study ID.')
                write_json(run / 'registry' / (nct + '.json'), raw)
                if current['updated_on'] > cutoff:
                    issues[nct] = f'Latest record is dated {current["updated_on"]}, after the cutoff; find the historical version.'
                    continue
                previous = records.get(nct)
                if previous != current:
                    changes.append({'id': nct, 'before': previous, 'after': current})
                records[nct] = current
            except (OSError, ValueError, KeyError, TypeError) as error:
                issues[nct] = str(error)

    # Overlap catches delayed indexing and corrections around the previous edition.
    since = (date.fromisoformat(baseline['last_updated']) - timedelta(days=14)).isoformat()
    discovery = {'since': since, 'through': cutoff, 'registry_studies': [], 'pubmed': {}}
    try:
        params = {'query.cond': 'amyotrophic lateral sclerosis',
                  'query.term': f'AREA[LastUpdatePostDate]RANGE[{since},{cutoff}]',
                  'pageSize': 100, 'countTotal': 'true', 'format': 'json'}
        for _ in range(10):
            result = get_json(REGISTRY_API, params)
            discovery['registry_total'] = result.get('totalCount')
            for raw in result.get('studies', []):
                summary = registry_summary(raw)
                if summary['updated_on'] <= cutoff:
                    summary['title'] = raw['protocolSection']['identificationModule']['briefTitle']
                    discovery['registry_studies'].append(summary)
                    write_json(run / 'registry' / (summary['id'] + '.json'), raw)
            token = result.get('nextPageToken')
            if not token:
                break
            params['pageToken'] = token
        else:
            issues['registry-discovery'] = 'Discovery exceeded 1,000 records. Complete the remaining search manually.'
    except (OSError, ValueError, KeyError, TypeError) as error:
        issues['registry-discovery'] = str(error)
    try:
        term = '("amyotrophic lateral sclerosis"[MeSH Terms] OR "amyotrophic lateral sclerosis"[Title/Abstract] OR "motor neuron disease"[Title/Abstract])'
        params = dict(db='pubmed', term=term, retmode='json', retmax=500, sort='pub_date',
                      datetype='edat', mindate=since.replace('-', '/'), maxdate=cutoff.replace('-', '/'), tool='ALSCompass')
        # Set an NCBI contact only if the person running the tool supplies one.
        if os.environ.get('NCBI_EMAIL'):
            params['email'] = os.environ['NCBI_EMAIL']
        result = get_json(PUBMED_API, params)['esearchresult']
        require(not result.get('errorlist'), f'PubMed search error: {result.get("errorlist")}')
        pmids = result['idlist']
        discovery['pubmed'] = {'count': int(result['count']), 'query': term,
                               'date_type': 'indexing date; verify publication dates separately',
                               'urls': ['https://pubmed.ncbi.nlm.nih.gov/' + pmid + '/' for pmid in pmids]}
        if int(result['count']) > len(pmids):
            issues['pubmed-discovery'] = 'PubMed returned more than 500 candidates. Complete the remaining search manually.'
    except (OSError, ValueError, KeyError, TypeError) as error:
        issues['pubmed-discovery'] = str(error)
    write_json(run / 'discovery.json', discovery)
    write_json(run / 'registry_changes.json', sorted(changes, key=lambda item: item['id']))
    snapshot['records'] = sorted(records.values(), key=lambda record: record['id'])
    return issues, changes


def prepare(root=ROOT, as_of=None, offline=False):
    today = date.today()
    cutoff = as_of or today.isoformat()
    baseline_path = root / LIVE_FILE
    baseline_bytes = baseline_path.read_bytes()
    baseline = json.loads(baseline_bytes)
    validate_research(baseline)
    require(date.fromisoformat(baseline['last_updated']) <= date.fromisoformat(cutoff) <= today,
            'Choose a cutoff from the current edition date through today; future-dated reviews are not allowed.')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run = root / '.research-updates' / (cutoff + '_' + stamp)
    run.mkdir(parents=True)
    (run / 'baseline.json').write_bytes(baseline_bytes)
    (run / 'draft.json').write_bytes(baseline_bytes)
    snapshot_path = root / 'data' / f'research_registry_snapshot_{baseline["last_updated"]}.json'
    if snapshot_path.exists():
        snapshot = read_json(snapshot_path)
    else:
        snapshot = {'records': [entry['registry'] for entry in entries(baseline).values() if 'registry' in entry]}
    snapshot.update(evidence_cutoff=cutoff, retrieved_on=today.isoformat())
    print(f'Preparing review through {cutoff} in {run}', flush=True)
    if offline:
        issues, changes = {'offline': 'No live sources were fetched. Complete registry and discovery checks manually.'}, []
    else:
        issues, changes = collect(run, baseline, cutoff, snapshot)
    write_json(run / 'registry_snapshot.json', snapshot)
    discovery = read_json(run / 'discovery.json') if (run / 'discovery.json').exists() else {}
    registry_candidates = len(discovery.get('registry_studies', []))
    paper_candidates = len(discovery.get('pubmed', {}).get('urls', []))
    manifest = dict(cutoff=cutoff, prepared_on=today.isoformat(), baseline_sha256=digest(run / 'baseline.json'),
                    issues=issues, baseline_cutoff=baseline['last_updated'])
    write_json(run / 'manifest.json', manifest)
    review_item = lambda: dict(reviewed=False, source_ids=[], note='')
    audit = dict(cutoff=cutoff, reviewed_on=None,
                 entries={key: review_item() for key in entries(baseline)},
                 discovery={section['id']: dict(reviewed=False, source_urls=[], note='') for section in baseline['sections']},
                 issues={key: dict(resolved=False, source_urls=[], note='') for key in issues})
    write_json(run / 'review.json', audit)
    template = (ROOT / 'prompts/update_als_research.md').read_text(encoding='utf-8')
    (run / 'PROMPT.md').write_text(f'# Prepared review run\n\nUse this existing run: `{run}`\nCutoff: **{cutoff}**. Do not prepare another run.\n\n' + template, encoding='utf-8')
    lines = ['# Research update preparation', '', f'Evidence target: {cutoff}; previous edition: {baseline["last_updated"]}.',
             f'{len(changes)} tracked registry records changed. {len(issues)} collection issue(s) need resolution.',
             f'Discovery returned {registry_candidates} recently updated study leads and {paper_candidates} paper leads. These require relevance and evidence review.',
             '', 'The published JSON and its review date were not changed. This is an unreviewed research packet.', '', '## Registry changes', '']
    for change in changes:
        before = change['before'] or {}
        changed_fields = [key for key, value in change['after'].items() if before.get(key) != value]
        lines.append(f'- {change["id"]}: {", ".join(changed_fields)}. See registry_changes.json for exact values.')
    lines += ['', '## Collection issues', ''] + [f'- {key}: {value}' for key, value in issues.items()]
    lines += ['', '## Next step', '', 'Ask your browsing-capable research assistant to follow PROMPT.md in this folder.',
              'FDA/EMA/PMDA/CDSCO decisions, full papers, sponsor milestones, communication tools and India access still require source review.']
    (run / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Collected {len(changes)} tracked registry changes; {registry_candidates} study leads; {paper_candidates} paper leads; {len(issues)} issue(s). Live page unchanged.\nPrompt: {run / "PROMPT.md"}\nReport: {run / "REPORT.md"}', flush=True)
    return run


def valid_urls(urls):
    return bool(urls) and all(isinstance(url, str) and urlparse(url).scheme == 'https' and urlparse(url).netloc for url in urls)


def validate_run(run, root=ROOT):
    manifest, baseline, draft, audit, snapshot = [read_json(run / name) for name in
        ('manifest.json', 'baseline.json', 'draft.json', 'review.json', 'registry_snapshot.json')]
    require(digest(run / 'baseline.json') == manifest['baseline_sha256'], 'The saved baseline was edited; prepare a new run.')
    require(digest(root / LIVE_FILE) == manifest['baseline_sha256'], 'The live review changed since preparation; prepare a new run to avoid overwriting newer work.')
    validate_research(draft)
    require(audit.get('reviewed_on') is not None, 'This packet is still unreviewed. Complete the source research described in its PROMPT.md first.')
    require(draft['last_updated'] == audit['cutoff'] == manifest['cutoff'], 'Draft and audit must use this run’s evidence cutoff.')
    require(audit['reviewed_on'] == draft['reviewed_on'], 'Record the actual review date in the draft and audit.')
    require(date.fromisoformat(manifest['prepared_on']) <= date.fromisoformat(draft['reviewed_on']) <= date.today(), 'Review date must be between preparation and today.')
    require(set(baseline['categories']).issubset(draft['categories']), 'Do not silently remove existing categories.')
    before, after = entries(baseline), entries(draft)
    require(set(before).issubset(after), 'Keep existing entry IDs, moving stopped programs to the appropriate category.')
    require(set(audit['entries']) == set(after), 'The audit must cover every draft entry, including additions.')
    sources = {source['id']: source for source in draft['source_library']}
    for entry_id, entry in after.items():
        record = audit['entries'][entry_id]
        require(record['reviewed'] is True and bool(record['note'].strip()), f'{entry_id}: complete the evidence review and note.')
        require(set(record['source_ids']) == set(entry['source_ids']), f'{entry_id}: record review of every cited source.')
        require(entry['sources'] == [sources[key]['url'] for key in entry['source_ids']], f'{entry_id}: synchronize legacy source URLs.')
        expected_date = max((sources[key]['published_on'] for key in entry['source_ids'] if sources[key]['published_on']), default=None)
        require(entry['evidence_date'] == expected_date, f'{entry_id}: evidence_date must match its latest dated reference.')
        require(isinstance(entry['limitations'], list), f'{entry_id}: limitations must remain a list.')
    for source in sources.values():
        require(date.fromisoformat(manifest['prepared_on']) <= date.fromisoformat(source['accessed_on']) <= date.fromisoformat(draft['reviewed_on']), 'Every cited source needs an actual access date within this review run.')
    used_sources = {key for entry in after.values() for key in entry['source_ids']}
    require(used_sources == set(sources), 'Remove unreferenced sources from the page library; preserve them in the review report if useful.')
    require(set(audit['discovery']) == {section['id'] for section in draft['sections']}, 'Complete discovery across every visible section.')
    for section_id, record in audit['discovery'].items():
        require(record['reviewed'] is True and record['note'].strip() and valid_urls(record['source_urls']), f'{section_id}: document discovery searches and findings, including no relevant change.')
    for issue_id in manifest['issues']:
        record = audit['issues'].get(issue_id, {})
        require(record.get('resolved') is True and record.get('note', '').strip() and valid_urls(record.get('source_urls', [])), f'{issue_id}: resolve the collection issue using documented sources.')
    require(snapshot['evidence_cutoff'] == manifest['cutoff'], 'Registry snapshot cutoff does not match the run.')
    require(date.fromisoformat(manifest['prepared_on']) <= date.fromisoformat(snapshot['retrieved_on']) <= date.fromisoformat(draft['reviewed_on']), 'Record the actual registry retrieval date.')
    registry = {record['id']: record for record in snapshot['records']}
    require(len(registry) == len(snapshot['records']), 'Registry snapshot contains duplicate IDs.')
    for record in registry.values():
        require(record['updated_on'] <= manifest['cutoff'], 'A registry record postdates the cutoff.')
    for entry in after.values():
        if 'registry' in entry:
            require(entry['registry'] == registry.get(entry['registry']['id']), f'{entry["id"]}: synchronize the registry snapshot and draft.')
    for source in sources.values():
        if re.fullmatch(r'NCT\d{8}', source['id']):
            record = registry.get(source['id'])
            require(record and record['updated_on'] == source['published_on'] and record['url'] == source['url'], f'{source["id"]}: synchronize registry source metadata.')
    # Existing communication pages still consume these fields.
    for entry in draft['categories']['communication_technology']:
        require(all(entry.get(key) for key in ('solution_name', 'category', 'form_factor', 'what_it_is', 'how_it_works', 'india_availability')), 'Preserve communication compatibility fields.')
    for entry in draft['categories']['experimental_communication_tech']:
        require(all(entry.get(key) for key in ('technology', 'risk_level', 'what_it_is', 'who_can_try', 'cost', 'recommendation')), 'Preserve experimental-technology compatibility fields.')
    changed = [key for key in before if before[key] != after[key]]
    added = sorted(set(after) - set(before))
    (run / 'CHANGES.diff').write_text(''.join(difflib.unified_diff(json_text(baseline).splitlines(True), json_text(draft).splitlines(True), fromfile='current review', tofile='reviewed draft')), encoding='utf-8')
    (run / 'VALIDATION.md').write_text(f'# Reviewed draft\n\n{len(after)} entries; {len(changed)} changed; {len(added)} added.\n\nChanged: {", ".join(changed) or "none"}\n\nAdded: {", ".join(added) or "none"}\n\nStructural and declared-coverage checks passed. This does not verify medical accuracy.\n', encoding='utf-8')
    return draft, snapshot


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply_run(run, root=ROOT):
    lock = root / '.research-updates' / 'apply.lock'
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError('Another update is applying. If it crashed, inspect and remove .research-updates/apply.lock before retrying.') from error
    try:
        os.close(fd)
        draft, snapshot = validate_run(run, root)
        target = root / LIVE_FILE
        require(not (run / 'APPLIED.json').exists(), 'This run has already been applied.')
        backup = run / 'backup'
        require(not backup.exists(), 'A previous apply attempt created a backup. Inspect it before retrying.')
        backup.mkdir()
        shutil.copy2(target, backup / 'research_categorized.json')
        snapshot_path = root / 'data' / f'research_registry_snapshot_{draft["last_updated"]}.json'
        old_snapshot = snapshot_path.read_text(encoding='utf-8') if snapshot_path.exists() else None
        if old_snapshot is not None:
            (backup / snapshot_path.name).write_text(old_snapshot, encoding='utf-8')
        try:
            atomic_write(snapshot_path, json_text(snapshot))
            atomic_write(target, json_text(draft))
        except OSError:
            if old_snapshot is None:
                snapshot_path.unlink(missing_ok=True)
            else:
                atomic_write(snapshot_path, old_snapshot)
            raise
        write_json(run / 'APPLIED.json', dict(applied_at=datetime.now(timezone.utc).isoformat(), live_sha256=digest(target), backup=str(backup)))
        print(f'Applied locally: {target}\nBackup: {backup}\nPreview: http://localhost:5001/research-updates')
    finally:
        lock.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prepare_command = commands.add_parser('prepare', help='Collect public leads and generate an unreviewed draft + prompt')
    prepare_command.add_argument('--as-of', help='Evidence cutoff YYYY-MM-DD; defaults to today')
    prepare_command.add_argument('--offline', action='store_true', help='Prepare files only; manual source collection remains mandatory')
    for command in ('validate', 'apply'):
        sub = commands.add_parser(command, help='Validate the reviewed draft' if command == 'validate' else 'Validate, back up, and replace the local review')
        sub.add_argument('--run', type=Path, required=True, help='Run directory printed by prepare')
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            prepare(as_of=args.as_of, offline=args.offline)
        elif args.command == 'validate':
            validate_run(args.run.resolve())
            print(f'Validation passed. Review {args.run / "CHANGES.diff"} and {args.run / "VALIDATION.md"}.')
        else:
            apply_run(args.run.resolve())
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'Research update stopped: {error}\n')


if __name__ == '__main__':
    main()
