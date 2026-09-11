const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const PowerPlanning = require('../static/js/power/calculations.js');
const source = fs.readFileSync(path.join(__dirname, '../static/js/power/calculator-ui.js'), 'utf8');

// Exercise UI events against the actual calculation module, without a browser.
function fixture(model = PowerPlanning) {
    class Element {
        constructor(tag = 'div') { this.tag = tag; this.children = []; this.dataset = {}; this.attrs = {}; this.events = {}; this.value = ''; this.hidden = false; this.disabled = false; this.checked = false; this._text = ''; }
        set textContent(value) { this._text = String(value); this.children = []; }
        get textContent() { return this._text + this.children.map(c => c.textContent).join(''); }
        set innerHTML(_) { throw new Error('Calculator output must use text, never HTML.'); }
        addEventListener(name, fn) { (this.events[name] ||= []).push(fn); }
        fire(name) { (this.events[name] || []).forEach(fn => fn({ preventDefault() {} })); if (this.parent) this.parent.fire(name); }
        setAttribute(name, value) { this.attrs[name] = value; }
        appendChild(child) { if (child.tag === 'fragment') { [...child.children].forEach(c => this.appendChild(c)); return; } child.parent = this; this.children.push(child); }
        append(...children) { children.forEach(c => this.appendChild(c)); }
        replaceChildren(...children) { this.children.forEach(c => { c.parent = null; }); this.children = []; this._text = ''; this.append(...children); }
        remove() { this.parent.children = this.parent.children.filter(c => c !== this); this.parent = null; }
        matches(selector) {
            if (selector[0] === '.') return this.className === selector.slice(1);
            if (selector.startsWith('[data-field=')) return this.dataset.field === selector.slice(12, -1);
            return this.tag === selector;
        }
        querySelectorAll(selector) { return this.children.flatMap(c => [...(c.matches(selector) ? [c] : []), ...c.querySelectorAll(selector)]); }
        querySelector(selector) { return this.querySelectorAll(selector)[0]; }
        closest(tag) { return this.matches(tag) ? this : this.parent?.closest(tag); }
        focus() { this.focused = true; }
    }
    const ids = Object.fromEntries([...source.matchAll(/\$\('([^']+)'\)/g)].map(m => [m[1], new Element()]));
    const form = new Element('form'); ids.powerPlanningForm = form;
    ids.powerDeviceTemplate.content = { cloneNode() {
        const fragment = new Element('fragment'), row = new Element(); row.className = 'power-device';
        const heading = new Element('strong'); heading.className = 'power-device-number'; row.append(heading, new Element('button'));
        for (const field of ['name', 'watts', 'usagePct', 'va']) {
            const label = new Element('label'), input = new Element('input'); input.dataset.field = field;
            input.value = field === 'usagePct' ? '100' : ''; label.appendChild(input); row.appendChild(label);
        }
        fragment.appendChild(row); return fragment;
    } };
    for (const id of ['powerDeviceList', 'includeBatteryModel', 'desiredBackupHours', 'energyAllowance', 'powerHeadroom', 'bankVoltage', 'bankAh', 'usableFraction']) form.appendChild(ids[id]);
    ids.desiredBackupHours.value = '8'; ids.energyAllowance.value = '20'; ids.powerHeadroom.value = '25';
    ids.powerCalculatorControls.disabled = true; ids.calcResults.hidden = true; ids.calculatorError.hidden = true; ids.batteryModelFields.hidden = true; ids.batteryModelFields.disabled = true;
    const document = { getElementById: id => ids[id], createElement: tag => new Element(tag) };
    vm.runInNewContext(source, { document, window: { PowerPlanning: model }, Intl });
    const rows = () => ids.powerDeviceList.querySelectorAll('.power-device');
    const field = (row, key) => row.querySelector('[data-field=' + key + ']');
    return { ids, form, rows, field };
}

test('initial load requires real device entries; missing module leaves controls disabled', () => {
    const f = fixture(); assert.equal(f.rows().length, 1);
    assert.equal(f.field(f.rows()[0], 'watts').value, ''); assert.equal(f.field(f.rows()[0], 'usagePct').value, '100');
    assert.equal(f.ids.powerCalculatorControls.disabled, false);
    f.form.fire('submit'); assert.equal(f.ids.calcResults.hidden, true); assert.equal(f.ids.calculatorError.hidden, false);
    assert.equal(f.ids.calculatorError.focused, true);
    const unavailable = fixture(null); assert.equal(unavailable.ids.powerCalculatorControls.disabled, true); assert.equal(unavailable.ids.powerCalculatorUnavailable.hidden, false);
});

test('examples start continuous and use real calculator results; edits clear stale output', () => {
    const f = fixture(); f.ids.loadPowerExample.fire('click');
    assert.equal(f.rows().length, 3); assert.ok(f.rows().every(r => f.field(r, 'usagePct').value === '100'));
    f.form.fire('submit'); assert.equal(f.ids.resultWorstCase.textContent, '805 W'); assert.equal(f.ids.resultEffective.textContent, '805 W');
    assert.equal(f.ids.resultEnergy.textContent, '7,728 Wh'); assert.equal(f.ids.batteryModelResults.hidden, true);
    assert.equal(f.ids.intermittentWarning.hidden, true);
    assert.match(f.ids.resultCapacity.textContent, /VA not determined/);
    f.field(f.rows()[1], 'usagePct').value = '25'; f.field(f.rows()[1], 'usagePct').fire('input'); assert.equal(f.ids.calcResults.hidden, true);
    f.form.fire('submit'); assert.equal(f.ids.resultEffective.textContent, '347.5 W'); assert.equal(f.ids.intermittentWarning.hidden, false);
    f.ids.energyAllowance.value = '-1'; f.ids.energyAllowance.fire('change'); f.form.fire('submit');
    assert.equal(f.ids.calcResults.hidden, true); assert.equal(f.ids.calculatorError.hidden, false);
});

test('battery estimates require an explicit fraction and include the energy allowance', () => {
    const f = fixture(); f.ids.loadPowerExample.fire('click');
    f.field(f.rows()[1], 'usagePct').value = '25'; f.field(f.rows()[2], 'usagePct').value = '25';
    f.ids.includeBatteryModel.checked = true; f.ids.includeBatteryModel.fire('change');
    assert.equal(f.ids.batteryModelFields.hidden, false); assert.equal(f.ids.batteryModelFields.disabled, false);
    f.ids.bankVoltage.value = '72'; f.ids.bankAh.value = '42'; f.form.fire('submit');
    assert.equal(f.ids.calcResults.hidden, true); assert.match(f.ids.calculatorError.textContent, /usable fraction/);
    f.ids.usableFraction.value = '75'; f.form.fire('submit');
    assert.equal(f.ids.batteryModelResults.hidden, false); assert.match(f.ids.bankResults.textContent, /51\.78 Ah/);
    assert.match(f.ids.bankResults.textContent, /short by 528 Wh/); assert.match(f.ids.bankSummary.textContent, /not been measured/);
    assert.equal(f.ids.bankResults.querySelectorAll('table').length, 2);
    f.ids.includeBatteryModel.checked = false; f.ids.includeBatteryModel.fire('change');
    assert.equal(f.ids.calcResults.hidden, true); assert.equal(f.ids.batteryModelFields.disabled, true);
    f.form.fire('submit'); assert.equal(f.ids.batteryModelResults.hidden, true); assert.equal(f.ids.bankResults.children.length, 0);
});

test('add and remove invalidate results, preserve unique input labels and prevent empty calculations', () => {
    const f = fixture(); f.ids.loadPowerExample.fire('click'); f.form.fire('submit');
    f.ids.addPowerDevice.fire('click'); assert.equal(f.ids.calcResults.hidden, true);
    const inputs = f.rows().flatMap(r => r.querySelectorAll('input'));
    assert.equal(new Set(inputs.map(i => i.id)).size, inputs.length);
    assert.ok(inputs.every(i => i.closest('label').htmlFor === i.id));
    for (const row of [...f.rows()]) row.querySelector('button').fire('click');
    assert.equal(f.rows().length, 0); assert.equal(f.ids.addPowerDevice.focused, true);
    f.form.fire('submit'); assert.match(f.ids.calculatorError.textContent, /at least one device/); assert.equal(f.ids.calcResults.hidden, true);
});

test('device names render as literal text and known VA is calculated without an assumed power factor', () => {
    const f = fixture(), row = f.rows()[0];
    f.field(row, 'name').value = '<img src=x onerror=alert(1)>';
    f.field(row, 'watts').value = '120'; f.field(row, 'va').value = '150'; f.form.fire('submit');
    assert.match(f.ids.resultBreakdown.textContent, /<img src=x onerror=alert\(1\)>/);
    assert.equal(f.ids.resultBreakdown.children.length, 0);
    assert.match(f.ids.resultCapacity.textContent, /150 W; 187\.5 VA/);
});
