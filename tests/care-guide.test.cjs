const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'static/js/care-guide.js'), 'utf8');

function fixture(mobileView = false) {
    const events = {}, media = { matches: mobileView, addEventListener(n, fn) { this.change = fn; }, removeEventListener() { this.removed = true; } };
    const directory = { open: true }, references = [{ open: false }, { open: true }];
    const headings = ['Equipment List', 'Suction'].map(text => ({ textContent: text, childNodes: [{ nodeType: 3, textContent: text }] }));
    const sections = headings.map((h, i) => ({ id: 'section-' + i, querySelector: () => h, matches: () => false }));
    const nav = { children: [], parentElement: { hidden: true }, appendChild(child) { this.children.push(child); }, addEventListener(n, fn) { this.click = fn; } };
    const main = { querySelectorAll: selector => selector === '[data-care-section]' ? sections : selector === '.care-equipment-reference' ? references : [] };
    let observer;
    class Observer { constructor(fn) { this.fn = fn; observer = this; } observe() {} disconnect() { this.disconnected = true; } }
    const doc = { querySelector: selector => ({ '.care-main': main, '.care-directory': directory, '.care-section-nav': nav }[selector]), createElement() { return { attrs: {}, set href(href) { this.hash = href; }, setAttribute(k, v) { this.attrs[k] = v; }, removeAttribute(k) { delete this.attrs[k]; } }; } };
    const win = { matchMedia: () => media, IntersectionObserver: Observer, addEventListener(n, fn) { events[n] = fn; } };
    vm.runInNewContext(source, { window: win, document: doc, IntersectionObserver: Observer });
    return { directory, references, nav, observer, sections, events, media };
}

test('the directory follows viewport size and produces links to existing section IDs', () => {
    const f = fixture(true); assert.equal(f.directory.open, false); assert.equal(f.nav.parentElement.hidden, false);
    assert.deepEqual(f.nav.children.map(a => a.hash), ['#section-0', '#section-1']);
    assert.deepEqual(f.nav.children.map(a => a.textContent), ['Equipment List', 'Suction']);
    f.directory.open = true; f.nav.click(); assert.equal(f.directory.open, false);
    f.media.matches = false; f.media.change(); assert.equal(f.directory.open, true);
});

test('section visibility updates the current location without changing page content', () => {
    const f = fixture(); f.observer.fn([{ target: f.sections[1], isIntersecting: true }]);
    assert.equal(f.nav.children[1].attrs['aria-current'], 'location');
    f.observer.fn([{ target: f.sections[0], isIntersecting: true }]);
    assert.equal(f.nav.children[0].attrs['aria-current'], 'location'); assert.equal(f.nav.children[1].attrs['aria-current'], undefined);
});

test('printing expands the equipment reference and restores the reader’s previous choices', () => {
    const f = fixture(); f.events.beforeprint(); assert.ok(f.references.every(r => r.open));
    f.events.afterprint(); assert.deepEqual(f.references.map(r => r.open), [false, true]);
    f.events.pagehide({ persisted: true }); assert.notEqual(f.observer.disconnected, true);
    f.events.pagehide({ persisted: false }); assert.equal(f.observer.disconnected, true); assert.equal(f.media.removed, true);
});
