const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const template = fs.readFileSync(path.join(root, 'templates/communication_technology.html'), 'utf8');
const script = template.split('<script>').at(-1).split('</script>')[0];
const data = JSON.parse(fs.readFileSync(path.join(root, 'data/communication_technology.json'), 'utf8'));
const ids = ['eyeTrackingDevices', 'headTrackingDevices', 'freeSoftware', 'mobileApps', 'lowTechSolutions', 'bciDevices'];
function fixture(failed = false) {
    const elements = Object.fromEntries(ids.map(id => [id, { innerHTML: '' }]));
    const requests = [];
    const context = vm.createContext({
        URL, console: { error() {} },
        document: { getElementById: id => elements[id], addEventListener() {}, querySelectorAll: selector => selector.includes('.ct-device-grid') ? Object.values(elements) : [] },
        window: { addEventListener() {} },
        fetch: async url => { requests.push(url); return { ok: !failed, json: async () => data }; },
    });
    vm.runInContext(script, context);
    return { context, elements, requests };
}

test('overview renders complete compatibility notes, prices and source links without a research API dependency', async () => {
    const f = fixture();
    await vm.runInContext('loadTechData()', f.context);
    assert.deepEqual(f.requests, ['/content/communication-tech.json']);
    for (const [section, key, field] of [
        ['eyeTrackingDevices', 'eye_tracking', 'devices'], ['headTrackingDevices', 'head_tracking', 'devices'],
        ['freeSoftware', 'free_software', 'software'], ['mobileApps', 'mobile_apps', 'apps'], ['bciDevices', 'bci', 'devices'],
    ]) {
        const html = f.elements[section].innerHTML;
        for (const item of data.categories[key][field]) {
            for (const note of item.key_notes || item.features) {
                assert.ok(html.includes(vm.runInContext(`escapeTech(${JSON.stringify(note)})`, f.context)));
            }
            for (const source of item.sources || []) assert.ok(html.includes(source.url.replaceAll('&', '&amp;')));
        }
        assert.ok(html.includes('rel="noopener noreferrer"'));
        assert.ok(!html.includes('ct-rating-dot'));
    }
    assert.ok(f.elements.eyeTrackingDevices.innerHTML.includes('US$150'));
    assert.ok(f.elements.eyeTrackingDevices.innerHTML.includes('US$229'));
    assert.ok(f.elements.eyeTrackingDevices.innerHTML.includes('/eye-tracker-setup?tab=tobii4c'));
    assert.ok(f.elements.mobileApps.innerHTML.includes('Not accepting new users'));
    assert.ok(f.elements.lowTechSolutions.innerHTML.includes('Alphabet Board'));
});

test('restored Tobii community cards retain their prices, original guidance and setup links', async () => {
    const f = fixture();
    await vm.runInContext('loadTechData()', f.context);
    const html = f.elements.eyeTrackingDevices.innerHTML;
    const [fourC, five] = data.categories.eye_tracking.devices;
    assert.equal(fourC.category, 'Budget Eye Tracker');
    assert.equal(fourC.price_inr, '₹15,000-20,000 (used)');
    assert.equal(fourC.works_with_windows_eye_control, true);
    assert.equal(five.price_inr, '₹25,000-40,000');
    assert.equal(five.works_with_windows_eye_control, false);
    assert.ok(html.includes('Install Tobii Core Software for full functionality'));
    assert.ok(html.includes('Requires beta driver installation to work with windows eye control'));
    assert.ok(html.includes('Works with OptiKey'));
    assert.ok(!html.includes('Community reference price; confirm the current seller quote and software setup.'));
    assert.ok(html.includes('/eye-tracker-setup?tab=tobii5-optikey'));
    assert.ok(html.includes('Compatibility note:'));
    assert.ok(!html.includes('undefined'));
});

test('API failure gives an actionable message in every comparison section', async () => {
    const f = fixture(true); await vm.runInContext('loadTechData()', f.context);
    for (const element of Object.values(f.elements)) assert.match(element.innerHTML, /role="status".*refresh/s);
});

test('fetched names and notes are escaped and non-HTTPS source links are rejected', () => {
    const f = fixture();
    const html = vm.runInContext(`renderSoftwareCard({name:'<img onerror="alert(1)">',features:['<script>bad()</script>'],sources:[{label:'unsafe',url:'javascript:alert(1)'},{label:'safe',url:'https://example.com/'}]})`,f.context);
    assert.ok(!html.includes('<img')); assert.ok(!html.includes('<script>')); assert.ok(!html.includes('javascript:'));
    assert.ok(html.includes('https://example.com/'));
});
