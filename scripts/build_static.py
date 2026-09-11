#!/usr/bin/env python3
"""Export the explicitly reviewed public website. Never execute legacy APIs."""
import argparse
from contextlib import contextmanager
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['CAREKOSH_STATIC_BUILD'] = '1'

from app import app  # noqa: E402
from public_site import PAGE_ROUTES, PUBLIC_DATA_FILES, canonical_path, page_output  # noqa: E402
from research_schema import validate_research  # noqa: E402

MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_FILES = 20_000
ASSET_SUFFIXES = {'.css', '.js', '.woff2', '.woff', '.ttf', '.svg', '.png', '.jpg',
                  '.jpeg', '.webp', '.gif', '.ico', '.mp4', '.webm', '.vtt', '.pdf', '.txt'}
ROOT_REFERENCE = re.compile(r'''["'`](/(?:static|content)/[^\s"'`<>]+)''')
CSS_REFERENCE = re.compile(r'''url\(\s*["']?([^\s)'"<>]+)''')
BACKEND_REFERENCE = re.compile(r'''["'`](?:/api/|https?://(?:localhost|127\.0\.0\.1)(?::|/))''')


class References(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.urls = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        for key in ('href', 'src', 'poster', 'data-original'):
            if attributes.get(key):
                self.urls.append(attributes[key])
        if attributes.get('srcset') and not attributes['srcset'].startswith('data:'):
            self.urls.extend(part.strip().split()[0] for part in attributes['srcset'].split(',') if part.strip())


def references(text, kind):
    urls = ROOT_REFERENCE.findall(text) + CSS_REFERENCE.findall(text)
    if kind == '.html' or '<a ' in text or '<img ' in text:
        urls.extend(References(text).urls)
    return urls


def checked_asset(relative, root=ROOT):
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or path.parts[0] != 'static' or any(
        part in ('.', '..') or part.startswith('.') for part in path.parts
    ) or '\\' in relative:
        raise ValueError(f'Invalid public asset path: {relative}')
    source = root / relative
    if source.suffix.lower() not in ASSET_SUFFIXES:
        raise ValueError(f'Unsupported public asset type: {relative}')
    if source.suffix == '.txt' and not (path.parts[1] == 'fonts' and source.name.endswith('-OFL.txt')):
        raise ValueError(f'Only font license text belongs in public assets: {relative}')
    if any(parent.is_symlink() for parent in (source, *source.parents)):
        raise ValueError(f'Public asset must not be a symlink: {relative}')
    if not source.resolve().is_relative_to((root / 'static').resolve()) or not source.is_file():
        raise ValueError(f'Missing public asset: {relative}')
    if source.stat().st_size > MAX_FILE_BYTES:
        raise ValueError(f'Public asset exceeds 25 MiB: {relative}')
    return source


def normalize_origin(value):
    parts = urlsplit(value)
    if (parts.scheme != 'https' or not parts.hostname or '.' not in parts.hostname
            or parts.username or parts.password or parts.port or parts.path not in ('', '/')
            or parts.query or parts.fragment or any(c.isspace() for c in value)
            or '<' in value or '>' in value or '\\' in value):
        raise ValueError('SITE_URL must be an HTTPS origin, such as https://als.carekosh.com')
    return 'https://' + parts.hostname.lower()


def settings(preview=False):
    config = json.loads((ROOT / 'config/static-site.json').read_text())
    origin = normalize_origin(os.environ.get('SITE_URL', config['site_url']))
    branch = os.environ.get('CF_PAGES_BRANCH', config['production_branch'])
    return origin, preview or branch != config['production_branch']


@contextmanager
def render_settings(origin, noindex):
    previous = dict(app.config)
    app.config.update(TESTING=True, PUBLIC_SITE_URL=origin, PUBLIC_NOINDEX=noindex)
    try:
        yield app.test_client()
    finally:
        app.config.clear()
        app.config.update(previous)


def write_text(output, relative, content):
    destination = output / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding='utf-8')


def write_search_files(output, origin, noindex):
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    sitemap = ET.Element(f'{{{namespace}}}urlset')
    for route in PAGE_ROUTES:
        url = ET.SubElement(sitemap, f'{{{namespace}}}url')
        ET.SubElement(url, f'{{{namespace}}}loc').text = origin + canonical_path(route)
    write_text(output, 'sitemap.xml', ET.tostring(sitemap, encoding='unicode', xml_declaration=True) + '\n')
    robots = 'User-agent: *\nDisallow: /\n' if noindex else f'User-agent: *\nAllow: /\nSitemap: {origin}/sitemap.xml\n'
    write_text(output, 'robots.txt', robots)
    headers = ('/*\n  X-Content-Type-Options: nosniff\n'
               '  Referrer-Policy: strict-origin-when-cross-origin\n'
               '  X-Frame-Options: SAMEORIGIN\n')
    if noindex:
        headers += '  X-Robots-Tag: noindex, nofollow\n'
    headers += '/content/*\n  Cache-Control: public, max-age=0, must-revalidate\n'
    write_text(output, '_headers', headers)


def validate_output(output):
    files = sorted(p for p in output.rglob('*') if p.is_file())
    if len(files) > MAX_FILES:
        raise ValueError('Export exceeds the Pages Free limit of 20,000 files')
    failures = []
    reference_count = 0
    for path in files:
        if path.is_symlink() or path.stat().st_size > MAX_FILE_BYTES:
            failures.append(f'Invalid or oversized output: {path.relative_to(output)}')
        if path.suffix not in {'.html', '.css', '.js', '.json'}:
            continue
        text = path.read_text(encoding='utf-8')
        if path.suffix == '.json':
            json.loads(text)
        if path.suffix == '.html' and re.search(r'{{|{%|{#', text):
            failures.append(f'Unresolved template in {path.relative_to(output)}')
        if BACKEND_REFERENCE.search(text):
            failures.append(f'Backend URL in {path.relative_to(output)}')
        # Parse decoded JSON strings too, including authored FAQ answer markup.
        chunks = [(text, path.suffix)]
        if path.suffix == '.json':
            def strings(value):
                if isinstance(value, str):
                    yield value
                elif isinstance(value, dict):
                    for child in value.values():
                        yield from strings(child)
                elif isinstance(value, list):
                    for child in value:
                        yield from strings(child)
            chunks = [(value, '.html') for value in strings(json.loads(text))]
        for chunk, kind in chunks:
            for reference in references(chunk, kind):
                parts = urlsplit(reference)
                if parts.scheme or parts.netloc or unquote(reference).startswith('#') or '${' in reference:
                    continue
                if not parts.path:
                    continue
                base = '/' + path.relative_to(output).as_posix()
                relative = unquote(urlsplit(urljoin(base, reference)).path).lstrip('/')
                target = output / relative
                if not target.resolve().is_relative_to(output.resolve()):
                    failures.append(f'Escaping URL in {path.relative_to(output)}')
                elif not target.is_file() and not (target / 'index.html').is_file():
                    failures.append(f'{path.relative_to(output)} → missing {reference}')
                reference_count += 1
    if failures:
        raise ValueError('\n'.join(sorted(set(failures))))
    return {'files': len(files), 'bytes': sum(p.stat().st_size for p in files), 'references': reference_count}


def export_site(output, origin, noindex=False):
    """Write to an empty directory. Validation must pass before dist is replaced."""
    output = Path(output)
    if output.is_symlink() or (output.exists() and any(output.iterdir())):
        raise ValueError('Export requires an empty, non-symlink directory')
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / 'config/static-assets.json').read_text())
    assets = manifest['assets']
    if len(set(assets)) != len(assets):
        raise ValueError('Duplicate public asset in static-assets.json')
    for relative in assets:
        source = checked_asset(relative)
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    with render_settings(origin, noindex) as client:
        for url, source_file in PUBLIC_DATA_FILES.items():
            # Do not allow a Flask fallback/error response to become a successful export.
            source_data = json.loads((ROOT / source_file).read_text(encoding='utf-8'))
            if not isinstance(source_data, dict) or not source_data.get('categories'):
                raise ValueError(f'Missing public categories: {source_file}')
            if url.endswith('research-categorized.json'):
                validate_research(source_data)
            response = client.get(url)
            if response.status_code != 200 or response.get_json() != source_data:
                raise ValueError(f'Public JSON differs from its source: {url}')
            write_text(output, url.lstrip('/'), json.dumps(source_data, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
        actual_routes = {r.rule for r in app.url_map.iter_rules() if 'GET' in r.methods
                         and not r.rule.startswith(('/api/', '/static/', '/content/'))}
        if actual_routes != set(PAGE_ROUTES):
            raise ValueError('Public routes changed; review PAGE_ROUTES before publishing')
        for route in PAGE_ROUTES:
            response = client.get(route)
            if response.status_code != 200:
                raise ValueError(f'Failed to render {route}: {response.status_code}')
            write_text(output, page_output(route), response.get_data(as_text=True))
        response = client.get('/_static-export-not-found')
        if response.status_code != 404:
            raise ValueError('Expected a real 404 response')
        write_text(output, '404.html', response.get_data(as_text=True))
    write_search_files(output, origin, noindex)
    return validate_output(output)


def publish_output(staging, destination):
    # No user-supplied delete target. Refuse to replace an unrecognized directory.
    if destination != ROOT / 'dist' or destination.is_symlink():
        raise ValueError('Only the real project dist directory may be replaced')
    if destination.exists():
        if not (destination / 'index.html').is_file() or not (destination / 'content/faq.json').is_file():
            raise ValueError('Existing dist is not a recognized CareKosh export; inspect it first')
        shutil.rmtree(destination)
    staging.rename(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true', help='Block indexing in local/preview exports')
    args = parser.parse_args()
    origin, noindex = settings(args.preview)
    with tempfile.TemporaryDirectory(prefix='.dist-build-', dir=ROOT) as temporary:
        staging = Path(temporary) / 'site'
        result = export_site(staging, origin, noindex)
        publish_output(staging, ROOT / 'dist')
    print(f'Built {len(PAGE_ROUTES)} pages + 404, {len(PUBLIC_DATA_FILES)} JSON files; '
          f'{result["files"]} files, {result["bytes"] / 1048576:.1f} MiB; '
          f'{result["references"]} local references checked.')
    print(f'Output: {ROOT / "dist"}')
    print(f'Canonical origin: {origin}; indexing: {"blocked (preview)" if noindex else "enabled"}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print(f'Static build failed: {error}', file=sys.stderr)
        sys.exit(1)
