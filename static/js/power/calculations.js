/* Electrical planning arithmetic, not a medical-device or installation approval. */
(function (root, factory) {
    if (typeof module === 'object' && module.exports) module.exports = factory();
    else root.PowerPlanning = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';
    function number(value, label, min, max, includeMin = true) {
        if ((typeof value !== 'number' && typeof value !== 'string') || String(value).trim() === '') throw new Error(label + ' is required.');
        const result = Number(value);
        if (!Number.isFinite(result) || (includeMin ? result < min : result <= min) || result > max) throw new Error(label + ' must be ' + (includeMin ? 'at least ' : 'greater than ') + min + ' and no more than ' + max + '.');
        return result;
    }
    function calculate(input) {
        if (!input || !Array.isArray(input.devices) || input.devices.length === 0) throw new Error('Add at least one device.');
        if (input.devices.length > 100) throw new Error('This calculator supports up to 100 devices.');
        const hours = number(input.hours, 'Backup hours', 0, 168, false);
        const allowancePct = number(input.allowancePct, 'Extra energy allowance (%)', 0, 100);
        const headroomPct = number(input.headroomPct, 'Continuous power headroom (%)', 0, 100);
        const devices = input.devices.map((device, index) => {
            const label = 'Device ' + (index + 1);
            if (!device || typeof device.name !== 'string' || !device.name.trim()) throw new Error(label + ': enter a name.');
            const watts = number(device.watts, label + ' watts', 0, 100000, false);
            const usagePct = number(device.usagePct, label + ' run time (%)', 0, 100, false);
            const va = device.va == null || (typeof device.va === 'string' && device.va.trim() === '') ? null : number(device.va, label + ' VA', watts, 100000);
            return { name: device.name.trim(), watts, usagePct, va, averageWatts: watts * usagePct / 100 };
        });
        const simultaneousWatts = devices.reduce((sum, d) => sum + d.watts, 0);
        const plannedWatts = devices.reduce((sum, d) => sum + d.averageWatts, 0);
        const totalVA = devices.every(d => d.va !== null) ? devices.reduce((sum, d) => sum + d.va, 0) : null;
        let bank = null;
        if (input.bank != null) {
            const voltage = number(input.bank.voltage, 'Battery bank voltage', 0, 1000, false);
            const ah = number(input.bank.ah, 'Battery bank Ah', 0, 100000, false);
            const usablePct = number(input.bank.usablePct, 'Assumed nominal-to-AC usable fraction (%)', 0, 100, false);
            bank = { voltage, ah, usablePct, nominalWh: voltage * ah, usableWh: voltage * ah * usablePct / 100 };
        }
        const scenario = watts => {
            const acWh = watts * hours;
            const targetAcWh = acWh * (1 + allowancePct / 100);
            return {
                watts, acWh, targetAcWh,
                requiredNominalWh: bank ? targetAcWh / (bank.usablePct / 100) : null,
                requiredBankAh: bank ? targetAcWh / (bank.usablePct / 100) / bank.voltage : null,
                modeledHours: bank ? bank.usableWh / watts : null,
                planningHours: bank ? bank.usableWh / watts / (1 + allowancePct / 100) : null,
                modeledShortfallWh: bank ? Math.max(0, targetAcWh - bank.usableWh) : null,
            };
        };
        const result = {
            devices, hours, allowancePct, headroomPct, simultaneousWatts, plannedWatts, totalVA, bank,
            wattScreeningTarget: simultaneousWatts * (1 + headroomPct / 100),
            vaScreeningTarget: totalVA === null ? null : totalVA * (1 + headroomPct / 100),
            hasIntermittentLoads: devices.some(d => d.usagePct < 100),
            continuous: scenario(simultaneousWatts), planned: scenario(plannedWatts),
        };
        const finite = value => typeof value === 'number' ? Number.isFinite(value) : value && typeof value === 'object' ? Object.values(value).every(finite) : true;
        if (!finite(result) || result.continuous.targetAcWh <= 0 || result.planned.targetAcWh <= 0 || (bank && bank.usableWh <= 0)) throw new Error('These inputs are outside the supported numeric range. Check units and values.');
        return result;
    }
    return Object.freeze({ calculate });
});
