const test = require('node:test');
const assert = require('node:assert/strict');
const { calculate } = require('../static/js/power/calculations.js');
const devices = [
    {name:'Ventilator', watts:120, usagePct:100},
    {name:'Oxygen', watts:610, usagePct:25},
    {name:'Suction', watts:75, usagePct:25},
];
const base = {devices, hours:8, allowancePct:20, headroomPct:25};
const bank = {voltage:72, ah:42, usablePct:75};
const close = (actual, expected) => assert.ok(Math.abs(actual-expected) <= Math.max(1, Math.abs(expected))*1e-12, `${actual} != ${expected}`);

test('reference arithmetic retains fractional watts and applies the allowance to every energy target', () => {
    const r = calculate(base);
    close(r.simultaneousWatts,805); close(r.plannedWatts,291.25);
    close(r.devices[1].averageWatts,152.5); close(r.devices[2].averageWatts,18.75);
    close(r.planned.acWh,2330); close(r.planned.targetAcWh,2796);
    close(r.continuous.acWh,6440); close(r.continuous.targetAcWh,7728);
    close(r.wattScreeningTarget,1006.25);
    assert.equal(r.totalVA,null); assert.equal(r.vaScreeningTarget,null); assert.equal(r.bank,null);
    assert.equal(r.planned.modeledHours,null); assert.equal(r.hasIntermittentLoads,true);
});

test('battery Wh uses bank voltage and bank Ah; a shortfall cannot be passed as sufficient', () => {
    const r = calculate({...base,bank});
    close(r.bank.nominalWh,3024); close(r.bank.usableWh,2268);
    close(r.planned.modeledHours,2268/291.25); close(r.planned.planningHours,2268/291.25/1.2);
    close(r.planned.requiredNominalWh,3728); close(r.planned.requiredBankAh,3728/72);
    close(r.planned.modeledShortfallWh,528); close(r.continuous.modeledShortfallWh,5460);
    assert.ok(r.planned.planningHours < 8);
});

test('the old 90%-of-duration acceptance and ignored reserve are eliminated', () => {
    const r = calculate({devices:[{name:'Load',watts:100,usagePct:100}],hours:10,allowancePct:20,headroomPct:0,bank:{voltage:10,ah:110,usablePct:100}});
    close(r.continuous.modeledHours,11); close(r.continuous.targetAcWh,1200); close(r.continuous.modeledShortfallWh,100);
    assert.ok(r.continuous.planningHours < 10);
    const shorter = calculate({devices:[{name:'Load',watts:100,usagePct:100}],hours:10,allowancePct:0,headroomPct:0,bank:{voltage:10,ah:90,usablePct:100}});
    close(shorter.continuous.modeledShortfallWh,100);
});

test('continuous operation never gets duty-cycle discounts in W or VA capacity', () => {
    const r = calculate({...base,devices:devices.map((d,i)=>({...d,va:[150,800,100][i]}))});
    close(r.totalVA,1050); close(r.vaScreeningTarget,1312.5); close(r.wattScreeningTarget,1006.25);
    const continuous = calculate({...base,devices:devices.map(d=>({...d,usagePct:100}))});
    close(continuous.plannedWatts,805); assert.deepEqual(continuous.planned,continuous.continuous);
    assert.equal(continuous.hasIntermittentLoads,false);
});

test('a partial VA entry stays unknown; a device VA rating cannot be below its watts', () => {
    const r=calculate({...base,devices:devices.map((d,i)=>({...d,va:i===0?150:''}))});
    assert.equal(r.totalVA,null); assert.equal(r.vaScreeningTarget,null);
    assert.throws(()=>calculate({...base,devices:[{name:'Load',watts:100,usagePct:100,va:90}]}),/VA/);
});

test('blank, zero, negative, nonfinite and out-of-range inputs produce errors, not silent defaults', () => {
    for(const value of ['', ' ', 0,-1,NaN,Infinity,169]) assert.throws(()=>calculate({...base,hours:value}));
    for(const value of ['',0,-1,NaN,Infinity,100001]) assert.throws(()=>calculate({...base,devices:[{name:'Load',watts:value,usagePct:100}]}));
    for(const value of ['',0,-1,101,NaN,Infinity]) assert.throws(()=>calculate({...base,devices:[{name:'Load',watts:100,usagePct:value}]}));
    for(const key of ['allowancePct','headroomPct']) for(const value of ['',-1,101,NaN,Infinity]) assert.throws(()=>calculate({...base,[key]:value}));
    assert.throws(()=>calculate({...base,devices:[]}));
    assert.throws(()=>calculate({...base,devices:[{name:' ',watts:100,usagePct:100}]}));
    assert.throws(()=>calculate({...base,devices:[null]}));
});

test('an enabled battery model needs explicit valid voltage, Ah and usable fraction', () => {
    for(const key of ['voltage','ah','usablePct']) for(const value of ['',0,-1,NaN,Infinity]) assert.throws(()=>calculate({...base,bank:{...bank,[key]:value}}));
    assert.throws(()=>calculate({...base,bank:{...bank,usablePct:101}}));
    assert.throws(()=>calculate({...base,bank:{voltage:72,ah:42}}));
    assert.throws(()=>calculate({...base,bank:{...bank,usablePct:1e-320}}),/numeric range/);
});

test('zero extra allowances are explicit valid choices; the calculation does not mutate inputs', () => {
    const input=JSON.parse(JSON.stringify({...base,bank,allowancePct:0,headroomPct:0}));const copy=JSON.parse(JSON.stringify(input));
    const r=calculate(input);assert.deepEqual(input,copy);close(r.planned.targetAcWh,2330);close(r.wattScreeningTarget,805);
    close(r.planned.requiredBankAh,2330/.75/72);
});

test('larger energy allowances cannot shrink requirements and lower usability cannot extend runtime', () => {
    for(const allowancePct of [0,10,20,50,100]) {
        const r=calculate({...base,bank,allowancePct});
        close(r.planned.targetAcWh,r.planned.acWh*(1+allowancePct/100));
        close(r.planned.planningHours*r.planned.watts*(1+allowancePct/100),r.bank.usableWh);
    }
    let last=0;
    for(const usablePct of [20,40,60,75,90,100]) {const r=calculate({...base,bank:{...bank,usablePct}});assert.ok(r.planned.modeledHours>last);last=r.planned.modeledHours;}
});

test('worked table values and alternative-load totals agree with the model', () => {
    for(const [voltage,ah,watts,hours] of [[24,100,120,15],[24,200,120,30],[48,150,272.5,19.81651376146789],[48,150,805,6.708074534161491],[72,150,291.25,27.811158798283263]]) {
        const r=calculate({devices:[{name:'Example',watts,usagePct:100}],hours:8,allowancePct:0,headroomPct:0,bank:{voltage,ah,usablePct:75}});
        close(r.continuous.modeledHours,hours);
    }
    close(2268/120,18.9);close(2268/171.25,13.243795620437956);close(4536/291.25,15.574248927038628);
});
