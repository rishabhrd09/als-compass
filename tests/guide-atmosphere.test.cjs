const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const THREE = require(path.join(root, 'static/vendor/three-r128.min.js'));
const source = fs.readFileSync(path.join(root, 'static/js/guide-atmosphere.js'), 'utf8');

function fixture({ page = 'communication_technology_page', reduced = false, saveData = false, library = true, webglFails = false } = {}) {
    class Element {
        constructor(tag) { this.tag = tag; this.events = {}; this.attrs = {}; this.children = []; this.clientWidth = 1440; this.clientHeight = 380; }
        addEventListener(name, fn) { (this.events[name] ??= new Set()).add(fn); }
        removeEventListener(name, fn) { this.events[name]?.delete(fn); }
        fire(name, event = {}) { this.events[name]?.forEach(fn => fn(event)); }
        setAttribute(name, value) { this.attrs[name] = value; }
        appendChild(child) { child.parent = this; this.children.push(child); }
        remove() { if (this.parent) this.parent.children = this.parent.children.filter(child => child !== this); }
        getBoundingClientRect() { return { left: 0, top: 0, width: this.clientWidth, height: this.clientHeight }; }
        getContext() { return { createRadialGradient() { return { addColorStop() {} }; }, fillRect() {} }; }
    }
    const hero = new Element('section');
    const doc = new Element('document');
    doc.body = { dataset: { page } }; doc.head = new Element('head'); doc.hidden = false;
    doc.querySelector = () => hero; doc.createElement = tag => new Element(tag);
    const media = new Element('media'); media.matches = reduced;
    const win = new Element('window'); win.matchMedia = () => media; win.devicePixelRatio = 3;
    const renders = [], renderers = [], intersections = [], resizes = [], frames = new Map();
    class Renderer {
        constructor(options) { if (webglFails) throw Error('WebGL unavailable'); this.options = options; this.disposeCount = 0; renderers.push(this); }
        setPixelRatio(value) { this.ratio = value; }
        setSize(width, height) { this.size = [width, height]; }
        render(scene, camera) { scene.updateMatrixWorld(true); camera.updateMatrixWorld(true); renders.push({ scene, camera }); }
        dispose() { this.disposeCount++; }
    }
    const libraryValue = { ...THREE, WebGLRenderer: Renderer };
    if (library) win.THREE = libraryValue;
    class IntersectionObserver {
        constructor(fn) { this.fn = fn; intersections.push(this); }
        observe() {}
        trigger(visible) { this.fn([{ isIntersecting: visible }]); }
        disconnect() { this.disconnected = true; }
    }
    class ResizeObserver {
        constructor(fn) { this.fn = fn; resizes.push(this); }
        observe() {}
        disconnect() { this.disconnected = true; }
    }
    let id = 0;
    vm.runInNewContext(source, {
        window: win, document: doc, navigator: { connection: { saveData } }, IntersectionObserver, ResizeObserver,
        requestAnimationFrame: fn => { frames.set(++id, fn); return id; }, cancelAnimationFrame: key => frames.delete(key),
    });
    return {
        win, doc, hero, media, renders, renderers, frames, intersections, resizes, libraryValue,
        enter: () => intersections[0].trigger(true),
        advance(now) { const callbacks = [...frames.values()]; frames.clear(); callbacks.forEach(fn => fn(now)); },
        control: () => hero.children.find(child => child.tag === 'button'),
    };
}

test('loads local Three.js only on entering the viewport and honors Save-Data', () => {
    const f = fixture({ library: false });
    assert.equal(f.doc.head.children.length, 0); assert.equal(f.hero.children.length, 0);
    f.enter(); f.enter(); assert.equal(f.doc.head.children.length, 1);
    const script = f.doc.head.children[0]; assert.equal(script.src, '/static/vendor/three-r128.min.js');
    f.win.THREE = f.libraryValue; script.onload(); assert.equal(f.renderers.length, 1);
    assert.equal(f.hero.children.length, 2); assert.equal(f.frames.size, 1);
    const limited = fixture({ saveData: true, library: false }); limited.enter();
    assert.equal(limited.doc.head.children.length, 0); assert.equal(limited.hero.children.length, 0); assert.equal(limited.frames.size, 0);
});

test('the communication scene uses finite lightweight geometry and adapts its camera framing', () => {
    for (const page of ['communication_technology_page']) {
        const f = fixture({ page }); f.enter();
        const { scene, camera } = f.renders.at(-1);
        const geometries = []; scene.traverse(o => { if (o.geometry) geometries.push(o.geometry); });
        assert.equal(geometries.length, 6);
        geometries.forEach(g => assert.ok(g.attributes.position.array.every(Number.isFinite)));
        let signals; scene.traverse(o => { if (o.isPoints) signals = o; });
        assert.equal(signals.geometry.attributes.position.count, 144);
        assert.equal(f.renderers[0].ratio, 1.5);
        const desktopZ = camera.position.z;
        f.hero.children[0].clientWidth = 280; f.resizes[0].fn();
        assert.equal(camera.aspect, 280 / 380); assert.ok(camera.position.z > desktopZ);
        assert.deepEqual(f.renderers[0].size, [280, 380]);
        assert.equal(f.hero.children[0].attrs['aria-hidden'], 'true');
    }
});

test('static care and FAQ pages create no animation, controls or library requests', () => {
    for (const page of ['home_icu_guide', 'faq', 'power_backup_guide', 'ups_faq', 'inventory_management', 'emergency_protocol']) {
        const f = fixture({ page, library: false });
        assert.equal(f.hero.children.length, 0);
        assert.equal(f.doc.head.children.length, 0);
        assert.equal(f.intersections.length, 0);
        assert.equal(f.renderers.length, 0);
        assert.equal(f.frames.size, 0);
    }
});

test('pause, hidden tabs and offscreen heroes stop rendering without losing the scene', () => {
    const f = fixture(); f.enter(); f.advance(100); f.advance(132);
    f.control().fire('click'); assert.equal(f.frames.size, 0); assert.equal(f.control().textContent, 'Play motion');
    const count = f.renders.length; f.advance(200); assert.equal(f.renders.length, count);
    f.control().fire('click'); assert.equal(f.frames.size, 1);
    f.intersections[0].trigger(false); assert.equal(f.frames.size, 0);
    f.enter(); assert.equal(f.frames.size, 1);
    f.doc.hidden = true; f.doc.fire('visibilitychange'); assert.equal(f.frames.size, 0);
    f.doc.hidden = false; f.doc.fire('visibilitychange'); assert.equal(f.frames.size, 1);
    assert.equal(f.renderers.length, 1);
});

test('reduced motion starts static, allows explicit playback and responds to preference changes', () => {
    const f = fixture({ reduced: true }); f.enter();
    assert.ok(f.renders.length > 0); assert.equal(f.frames.size, 0); assert.equal(f.control().textContent, 'Play motion');
    f.control().fire('click'); assert.equal(f.frames.size, 1);
    f.media.fire('change'); assert.equal(f.frames.size, 0);
    f.media.matches = false; f.media.fire('change'); assert.equal(f.frames.size, 1);
    f.media.matches = true; f.media.fire('change'); assert.equal(f.frames.size, 0);
});

test('WebGL or library failures preserve the original hero and remove inactive controls', () => {
    const failed = fixture({ webglFails: true }); failed.enter();
    assert.equal(failed.hero.children.length, 0); assert.equal(failed.frames.size, 0);
    assert.equal(failed.intersections[0].disconnected, true);
    const absent = fixture({ library: false }); absent.enter(); absent.doc.head.children[0].onerror();
    assert.equal(absent.hero.children.length, 0); assert.equal(absent.frames.size, 0);
    const late = fixture({ library: false }); late.enter(); late.win.fire('pagehide', { persisted: false });
    late.win.THREE = late.libraryValue; late.doc.head.children[0].onload();
    assert.equal(late.hero.children.length, 0); assert.equal(late.renderers.length, 0);
});

test('bfcache resumes; teardown frees graphics and disconnects all observers and listeners', () => {
    const f = fixture(); f.enter();
    const resources = new Set(); f.renders.at(-1).scene.traverse(o => {
        if (o.geometry) resources.add(o.geometry);
        if (o.material) { resources.add(o.material); if (o.material.map) resources.add(o.material.map); }
    });
    let disposals = 0; resources.forEach(r => r.addEventListener('dispose', () => disposals++));
    f.win.fire('pagehide', { persisted: true }); assert.equal(f.frames.size, 0); assert.equal(disposals, 0);
    f.win.fire('pageshow', { persisted: true }); assert.equal(f.frames.size, 1);
    f.win.fire('pagehide', { persisted: false }); assert.equal(f.frames.size, 0); assert.equal(f.hero.children.length, 0);
    assert.equal(disposals, resources.size); assert.equal(f.renderers[0].disposeCount, 1);
    assert.ok([...f.intersections, ...f.resizes].every(observer => observer.disconnected));
    for (const target of [f.win, f.doc, f.hero, f.media]) assert.ok(Object.values(target.events).every(set => set.size === 0));
});

test('lost WebGL context releases resources and falls back without an animation retry loop', () => {
    const f = fixture(); f.enter(); let prevented = false;
    const canvas = f.hero.children[0].children[0];
    canvas.fire('webglcontextlost', { preventDefault() { prevented = true; } });
    assert.equal(prevented, true); assert.equal(f.hero.children.length, 0);
    assert.equal(f.renderers[0].disposeCount, 1); assert.equal(f.frames.size, 0);
});
