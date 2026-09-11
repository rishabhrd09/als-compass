"""Structural checks for reviewed research snapshots, not medical validation."""
from datetime import date
from urllib.parse import urlparse


def validate_research(data):
    """Reject incomplete drafts before they replace or render a reviewed edition."""
    try:
        if data['schema_version'] != 2:
            raise ValueError('The reviewed page requires research schema version 2.')
        cutoff = date.fromisoformat(data['last_updated'])
        if date.fromisoformat(data['reviewed_on']) < cutoff:
            raise ValueError('The review date cannot precede the evidence cutoff.')
        sources = {item['id']: item for item in data['source_library']}
        if not sources or len(sources) != len(data['source_library']):
            raise ValueError('Sources must have unique IDs.')
        for source in sources.values():
            if not all(source.get(key) for key in ('title', 'publisher', 'kind', 'accessed_on')):
                raise ValueError('Every reference needs its title, publisher, kind and access date.')
            url = urlparse(source['url'])
            if url.scheme != 'https' or not url.netloc:
                raise ValueError('Source URLs must use HTTPS.')
            if source['published_on']:
                published = source['published_on']
                if date.fromisoformat(published + '-01' if len(published) == 7 else published) > cutoff:
                    raise ValueError('A source is later than the evidence cutoff.')
        covered = [key for section in data['sections'] for key in section['categories']]
        if len(covered) != len(set(covered)) or set(covered) != set(data['categories']):
            raise ValueError('Each category must appear in exactly one visible section.')
        if len({section['id'] for section in data['sections']}) != len(data['sections']):
            raise ValueError('Section IDs must be unique.')
        entries = [entry for group in data['categories'].values() for entry in group]
        ids = [entry['id'] for entry in entries]
        if len(set(ids)) != len(ids):
            raise ValueError('Entry IDs must be unique.')
        for entry in entries:
            if not all(entry.get(key) for key in ('name', 'subtitle', 'status', 'status_kind', 'summary', 'evidence', 'limitations', 'source_ids')):
                raise ValueError('Every entry needs evidence, limitations and references.')
            if not set(entry['source_ids']).issubset(sources):
                raise ValueError('An entry refers to a missing source.')
            if 'registry' in entry and date.fromisoformat(entry['registry']['updated_on']) > cutoff:
                raise ValueError('A registry update is later than the evidence cutoff.')
        if not set(data['homepage_entries']).issubset(ids):
            raise ValueError('A homepage preview refers to a missing entry.')
        for highlight in data['highlights']:
            if highlight['entry_id'] not in ids or highlight['source_id'] not in sources:
                raise ValueError('A recent-development link has no corresponding entry or source.')
        if not data['methodology'] or not data['coverage'] or not data['review_changes']:
            raise ValueError('The review needs a method, coverage statement and change record.')
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError('Incomplete research schema. See docs/research-review-2026-09-10.md.') from error
