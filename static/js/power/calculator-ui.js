(() => {
    'use strict';
    const form = document.getElementById('powerPlanningForm');
    if (!form || !window.PowerPlanning) return;
    const $ = id => document.getElementById(id);
    const results = $('calcResults'), errors = $('calculatorError');
    const format = value => new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(value);
    let counter = 0;
    const invalidate = () => { results.hidden = true; errors.hidden = true; };
    function addDevice(name = '', watts = '') {
        const id = ++counter;
        const fragment = $('powerDeviceTemplate').content.cloneNode(true);
        const row = fragment.querySelector('.power-device');
        row.querySelector('.power-device-number').textContent = 'Device ' + id;
        row.querySelectorAll('input').forEach(input => {
            input.id = 'power-device-' + id + '-' + input.dataset.field;
            input.closest('label').htmlFor = input.id;
        });
        row.querySelector('[data-field=name]').value = name;
        row.querySelector('[data-field=watts]').value = watts;
        row.querySelector('button').setAttribute('aria-label', 'Remove device ' + id);
        row.querySelector('button').addEventListener('click', () => { row.remove(); invalidate(); $('addPowerDevice').focus(); });
        $('powerDeviceList').appendChild(fragment); invalidate();
        return row;
    }
    function collect() {
        return {
            devices: [...$('powerDeviceList').querySelectorAll('.power-device')].map(row => Object.fromEntries([...row.querySelectorAll('input')].map(input => [input.dataset.field, input.value]))),
            hours: $('desiredBackupHours').value, allowancePct: $('energyAllowance').value, headroomPct: $('powerHeadroom').value,
            bank: $('includeBatteryModel').checked ? { voltage: $('bankVoltage').value, ah: $('bankAh').value, usablePct: $('usableFraction').value } : null,
        };
    }
    function line(label, value) {
        const row = document.createElement('tr');
        const heading = document.createElement('th'); heading.scope = 'row'; heading.textContent = label;
        const cell = document.createElement('td'); cell.textContent = value;
        row.append(heading, cell); return row;
    }
    function render(result) {
        $('resultWorstCase').textContent = format(result.simultaneousWatts) + ' W';
        $('resultEffective').textContent = format(result.plannedWatts) + ' W';
        $('resultEnergy').textContent = format(result.continuous.targetAcWh) + ' Wh';
        $('resultCapacity').textContent = 'Continuous-output screening targets with ' + format(result.headroomPct) + '% headroom: ' + format(result.wattScreeningTarget) + ' W; ' + (result.vaScreeningTarget === null ? 'VA not determined — enter VA for every device or ask the supplier to measure it.' : format(result.vaScreeningTarget) + ' VA.');
        $('intermittentWarning').hidden = !result.hasIntermittentLoads;
        const scenarios = [['All devices continuous', result.continuous], ['Entered run-time pattern', result.planned]];
        const body = $('scenarioResults'); body.replaceChildren();
        for (const [label, scenario] of scenarios) {
            const row = document.createElement('tr');
            [label, format(scenario.watts) + ' W', format(scenario.acWh) + ' Wh', format(scenario.targetAcWh) + ' Wh'].forEach((value, i) => {
                const cell = document.createElement(i ? 'td' : 'th'); if (!i) cell.scope = 'row'; cell.textContent = value; row.appendChild(cell);
            }); body.appendChild(row);
        }
        $('batteryModelResults').hidden = !result.bank;
        $('bankResults').replaceChildren();
        if (result.bank) {
            $('bankSummary').textContent = 'Illustrative model only: ' + format(result.bank.voltage) + ' V × ' + format(result.bank.ah) + ' Ah = ' + format(result.bank.nominalWh) + ' Wh nominal; at your assumed ' + format(result.bank.usablePct) + '%, modeled AC energy is ' + format(result.bank.usableWh) + ' Wh. Actual available energy has not been measured by this calculator.';
            for (const [label, scenario] of scenarios) {
                const target = document.createElement('section'); const title = document.createElement('h4'); title.textContent = label;
                const table = document.createElement('table'); table.className = 'pb-table';
                table.append(line('Modeled runtime, without extra allowance', format(scenario.modeledHours) + ' hours'));
                table.append(line('Planning hours with ' + format(result.allowancePct) + '% extra energy allowance', format(scenario.planningHours) + ' hours'));
                table.append(line('Nominal energy needed under this assumption', format(scenario.requiredNominalWh) + ' Wh'));
                table.append(line('Bank capacity needed at the entered voltage', format(scenario.requiredBankAh) + ' Ah (arithmetic only; compatibility unverified)'));
                const note = document.createElement('p');
                note.textContent = scenario.modeledShortfallWh > 0
                    ? 'Below target: the model is short by ' + format(scenario.modeledShortfallWh) + ' Wh of AC energy, including the extra allowance.'
                    : 'The arithmetic reaches the entered energy target under this assumption. This does not confirm real runtime, transfer safety or suitability for life support.';
                const wrapper = document.createElement('div'); wrapper.className = 'care-table-scroll'; wrapper.tabIndex = 0;
                wrapper.setAttribute('role', 'region'); wrapper.setAttribute('aria-label', label + ' battery model'); wrapper.appendChild(table);
                note.className = 'pb-info-box'; target.append(title, wrapper, note); $('bankResults').appendChild(target);
            }
        }
        const breakdown = result.devices.map(d => d.name + ': ' + format(d.watts) + ' W × ' + format(d.usagePct) + '% = ' + format(d.averageWatts) + ' W average');
        breakdown.push('All devices continuous: ' + format(result.simultaneousWatts) + ' W × ' + format(result.hours) + ' h × ' + format(1 + result.allowancePct / 100) + ' = ' + format(result.continuous.targetAcWh) + ' Wh AC, including extra allowance.');
        breakdown.push('Entered pattern: ' + format(result.plannedWatts) + ' W × ' + format(result.hours) + ' h × ' + format(1 + result.allowancePct / 100) + ' = ' + format(result.planned.targetAcWh) + ' Wh AC, including extra allowance.');
        $('resultBreakdown').textContent = breakdown.join('\n');
        results.hidden = false; results.focus();
    }
    form.addEventListener('submit', event => {
        event.preventDefault(); invalidate();
        try { render(window.PowerPlanning.calculate(collect())); }
        catch (error) { errors.textContent = error.message; errors.hidden = false; errors.focus(); }
    });
    form.addEventListener('input', invalidate);
    form.addEventListener('change', invalidate);
    $('addPowerDevice').addEventListener('click', () => addDevice().querySelector('input').focus());
    $('includeBatteryModel').addEventListener('change', () => {
        const active = $('includeBatteryModel').checked;
        $('batteryModelFields').hidden = !active;
        $('batteryModelFields').disabled = !active;
    });
    $('loadPowerExample').addEventListener('click', () => {
        $('powerDeviceList').replaceChildren();
        addDevice('Ventilator (example)', 120); addDevice('Oxygen concentrator (example)', 610); addDevice('Suction machine (example)', 75);
        $('powerExampleNotice').hidden = false;
    });
    addDevice();
    $('powerCalculatorControls').disabled = false;
    $('powerCalculatorUnavailable').hidden = true;
})();
