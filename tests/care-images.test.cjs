const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/js/care-images.js'), 'utf8');

function fixture({ supported = true, count = 3 } = {}) {
    class Element {
        constructor() {
            this.events = {}; this.attrs = {}; this.dataset = {}; this.style = {}; this.classes = new Set();
            this.classList = { toggle: (key, active) => active ? this.classes.add(key) : this.classes.delete(key) };
        }
        addEventListener(name, callback) { this.events[name] = callback; }
        fire(name, values = {}) {
            const event = { target: this, button: 0, preventDefault() { this.prevented = true; }, ...values };
            this.events[name]?.(event); return event;
        }
        setAttribute(name, value) { this.attrs[name] = value; }
        removeAttribute(name) { delete this[name]; delete this.attrs[name]; }
        focus() { this.focused = true; }
        querySelector() { return { alt: 'Fallback photograph caption' }; }
    }
    const names = ['Viewer', 'Full', 'Stage', 'Zoom', 'Error', 'Title', 'Position', 'Credit', 'Original', 'Previous', 'Next', 'Close'];
    const nodes = Object.fromEntries(names.map(name => [name, new Element()]));
    const links = Array.from({ length: count }, (_, index) => {
        const link = new Element(); link.href = `/static/images/photo-${index}.png`;
        link.dataset = { caption: `Photograph ${index}`, credit: `Source ${index}` }; return link;
    });
    const body = new Element(); body.style.overflow = 'auto';
    if (supported) nodes.Viewer.showModal = () => { nodes.Viewer.open = true; };
    nodes.Viewer.close = () => { nodes.Viewer.open = false; nodes.Viewer.fire('close'); };
    vm.runInNewContext(source, { document: { body, querySelectorAll: () => links, getElementById: id => nodes[id.replace('careImage', '')] } });
    return { nodes, links, body };
}

test('opens the selected original with its caption and credit, and restores focus and scrolling on close', () => {
    const { nodes: n, links, body } = fixture();
    assert.equal(links[1].fire('click').prevented, true);
    assert.equal(n.Viewer.open, true); assert.equal(body.style.overflow, 'hidden');
    assert.equal(n.Full.src, links[1].href); assert.equal(n.Original.href, links[1].href);
    assert.equal(n.Title.textContent, 'Photograph 1'); assert.equal(n.Full.alt, 'Photograph 1');
    assert.equal(n.Credit.textContent, 'Source 1'); assert.equal(n.Position.textContent, 'Image 2 of 3');
    n.Close.fire('click'); assert.equal(n.Viewer.open, false); assert.equal(body.style.overflow, 'auto');
    assert.equal(links[1].focused, true); assert.equal(n.Full.src, undefined);
    // Native Escape closes the dialog and emits the same close event.
    links[0].fire('click'); n.Viewer.close();
    assert.equal(links[0].focused, true); assert.equal(body.style.overflow, 'auto');
});

test('navigation wraps in both directions and resets zoom for each image', () => {
    const { nodes: n, links } = fixture(); links[0].fire('click');
    n.Previous.fire('click'); assert.equal(n.Full.src, links[2].href);
    n.Next.fire('click'); assert.equal(n.Full.src, links[0].href);
    assert.equal(n.Viewer.fire('keydown', { key: 'ArrowRight' }).prevented, true);
    assert.equal(n.Full.src, links[1].href);
    n.Zoom.fire('click'); assert.equal(n.Zoom.attrs['aria-pressed'], 'true');
    assert.equal(n.Zoom.textContent, 'Fit image'); assert.ok(n.Stage.classes.has('is-zoomed'));
    assert.equal(n.Viewer.fire('keydown', { key: 'ArrowRight' }).prevented, undefined);
    assert.equal(n.Full.src, links[1].href); // Arrows can pan the zoomed image.
    n.Next.fire('click'); assert.equal(n.Zoom.attrs['aria-pressed'], 'false');
    assert.equal(n.Stage.scrollTop, 0); assert.equal(n.Stage.scrollLeft, 0);
    n.Viewer.fire('keydown', { key: 'ArrowLeft' }); assert.equal(n.Full.src, links[1].href);
});

test('failed images retain an original link and recover when navigating to another photograph', () => {
    const { nodes: n, links } = fixture(); links[0].fire('click'); n.Full.fire('error');
    assert.equal(n.Full.hidden, true); assert.equal(n.Error.hidden, false); assert.equal(n.Zoom.disabled, true);
    assert.equal(n.Original.href, links[0].href);
    n.Next.fire('click'); n.Full.fire('load');
    assert.equal(n.Full.hidden, false); assert.equal(n.Error.hidden, true); assert.equal(n.Zoom.disabled, false);
});

test('original links remain native without dialog support or with modified clicks', () => {
    const absent = fixture({ supported: false });
    assert.equal(absent.links[0].events.click, undefined);
    const { nodes: n, links } = fixture();
    for (const modifier of [{ ctrlKey: true }, { metaKey: true }, { shiftKey: true }, { altKey: true }, { button: 1 }]) {
        assert.equal(links[0].fire('click', modifier).prevented, undefined);
        assert.equal(n.Viewer.open, undefined);
    }
});

test('backdrop clicks close the viewer; clicks inside it do not', () => {
    const { nodes: n, links } = fixture({ count: 1 }); links[0].fire('click');
    assert.equal(n.Previous.disabled, true); assert.equal(n.Next.disabled, true);
    n.Viewer.fire('click', { target: n.Full }); assert.equal(n.Viewer.open, true);
    n.Viewer.fire('click'); assert.equal(n.Viewer.open, false);
});
