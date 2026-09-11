# Power guide technical audit — 11 September 2026

The Power Backup Guide, its calculator and the linked Power Backup FAQ were reviewed and corrected. The Emergency Protocol page received a prominent attribution and usage disclaimer. This is a source and software review, not clinical validation, certification of a home installation, or a measured runtime test. No generic calculator can guarantee uninterrupted life-support power under every condition.

## Corrections made

| Original issue | Correction | Basis / remaining limit |
|---|---|---|
| Indian brands and kVA specifications described as following BIS standards in general | Retained nominal 230 V AC / 50 Hz context; require exact model/registration verification | A brand or kVA number is not evidence of certification or life-support suitability |
| Outages described as 4–12+ hours across India | Removed unsupported general range; use local history and contingency planning | No nationwide outage dataset was supplied |
| Rounded effective load of 292 W | Exact original example is 120 + 610 × .25 + 75 × .25 = **291.25 W** | No intermediate rounding |
| Oxygen and suction defaulted to 25% | Blank device wattages; all new/example devices start at 100% operation; explicit warning for intermittent patterns | Care requirements determine operation; percentages apply to the entered outage interval |
| A fixed 75% factor treated as runtime efficiency | Optional battery model, off initially, with a required explicit nominal-to-AC usable fraction | Must encompass discharge rate, cutoff, charge state, age, temperature and UPS conversion/idle losses; not just inverter efficiency |
| Headline margin ignored by recommendations and 90% of required duration accepted | All energy targets include the entered allowance; every positive modeled shortfall is reported | No automatic hardware recommendation or near-target acceptance remains |
| UPS kVA, watts and battery voltage/count inferred from generic mappings | Removed the preset purchase mappings and unverified prices | UPS W and VA limits, battery bus, charger and device compatibility are independent checks |
| Average watts used as if they were peak/output demand | Separate average-energy calculation from simultaneous running W and optional VA | Start-up/inrush and overload duration still require device-specific data; 25% headroom is only an illustrative screening input |
| “20+ hours” for a 72 V / 42 Ah bank at 120 W | **18.90 hours** under the old hypothetical 75% assumption, before any extra allowance | This is arithmetic, not a tested runtime claim |
| Summer heat assigned a universal 10–20% immediate capacity penalty | Explain accelerated aging in heat and reduced capacity in cold; no seasonal percentage | Follow model-specific temperature and charging instructions |
| Six batteries of at least 45 Ah suggested for an 8-hour example | Corrected example including 20% allowance gives **51.78 Ah at 72 V**, assuming 75% usability | Even this number is not a purchase approval or runtime guarantee |
| Different universal two-UPS groupings and unsafe plug-switching implications | Explain that splitting loads is not automatic failover; all clinically essential devices require a verified continuity path | No UPS daisy-chaining or improvised output joining; manufacturer-approved transfer arrangements only |
| Beep patterns treated as diagnoses and household experience as a universal derating rule | Require exact alarm/manual interpretation; retain 6.5-hour backup and roughly 10-hour outage as attributed experiences | No outage log, battery condition evidence or controlled test was supplied |
| Duplicate obsolete calculator in the Home ICU template | Removed unused legacy code | Avoid contradictory formulas in a second implementation |
| Emergency notes read as universally applicable protocols | Added first-content disclaimer describing personal/community experience, individualized instructions and training, plus emergency escalation | Existing clinical procedures were not independently validated by this task |

## Reference equipment and the author's clarification

The supplied UPS photograph identifies **Uniline MF1103L6, 3 kVA / 2.4 kW, 230 V AC / 50 Hz, 72 V DC**. Its label lists IS 16242 (Part 1):2014 / IEC 62040-1:2008. The battery photograph identifies **Exide PowerSafe Plus EP 42-12, 12 V / 42 Ah**. These observations do not verify current certification, installation condition or clinical suitability. The author reports two UPS units, six batteries per unit.

Six identical 12 V / 42 Ah batteries in series give 72 V / 42 Ah and 3,024 nominal Wh. Exide's technical table specifies EP42-12 capacity at 27°C as 42 Ah at the 20-hour rate, 38.5 Ah at 10 hours and 31.5 Ah at 3 hours, with stated cutoff conditions. A 20-hour Ah rating is not constant across discharge rates.

The author subsequently reported:

- A Trilogy ventilator running full time. The supplied wording was “Trilogy 330V”; an exact model match was not established. Philips publishes a Trilogy EV300 model, but this review does **not** assume it is the author's device. The old 120 W remains an illustrative value.
- A 10 L/min Oxymed concentrator, operated at 5 L/min for approximately two hours a day. Oxymed's official 10 LPM Dual Flow specification lists **610 W**. The actual unit/nameplate match and consumption at 5 L/min remain unmeasured. Do not infer half the watts at half the flow.
- A Yuwell suction machine, without a model identifier or recorded run time. The old 75 W remains illustrative. Do not silently treat a manufacturer's VA figure as watts.

Two hours divided by 24 hours is approximately 8.33% of a day. Two hours falling within an eight-hour outage is 25% of that outage. Daily usage does not establish when treatment will be needed during an outage or whether needs will increase. No patient's prescribed care should be reduced to make a battery calculation fit.

## Calculation contract

For each device, `averageWatts = watts × usagePct / 100`.

- `simultaneousWatts = sum(watts)`; duty cycle never discounts running output capacity.
- `plannedWatts = sum(averageWatts)`.
- For each scenario: `acWh = scenarioWatts × hours`.
- `targetAcWh = acWh × (1 + allowancePct / 100)`.
- Optional: `nominalWh = bankVoltage × bankAh` and `usableWh = nominalWh × usablePct / 100`.
- `requiredNominalWh = targetAcWh / (usablePct / 100)`.
- `requiredBankAh = requiredNominalWh / bankVoltage`.
- `modeledHours = usableWh / scenarioWatts`.
- `planningHours = modeledHours / (1 + allowancePct / 100)`.
- `shortfallWh = max(0, targetAcWh - usableWh)`.

The 20% initial energy allowance means 20% **additional required energy**, not a promise to retain 20% battery state of charge. The initial 25% continuous headroom is not a validated inrush allowance or medical standard. All VA inputs are needed to calculate a VA screening target; no fixed power factor is invented.

Both scenarios use the user's single hypothetical usable fraction for comparison. Real usable fraction can vary with load, so these comparisons do not validate runtime in either scenario. Manufacturer runtime curves and installation testing remain necessary.

Validation rejects blank or nonfinite numbers, nonpositive watts/hours/battery inputs, invalid percentages, VA below W, missing device names, empty device lists and unsupported numerical ranges. Duration is limited to 168 hours, devices to 100, per-device W/VA to 100,000, voltage to 1,000 V and bank capacity to 100,000 Ah as software bounds, **not safe equipment specifications**. The UI clears results on edits, adds/removals and optional-bank changes. A missing calculation module leaves controls disabled. Device names are inserted using textContent.

## Checked examples

All battery runtime examples below use **unverified 75% usability** and constant average load. They have no added allowance unless stated.

| Example | Arithmetic result |
|---|---:|
| Oxygen 610 W × 25% | 152.50 W average |
| Suction 75 W × 25% | 18.75 W average |
| Ventilator plus the above | 291.25 W average |
| All three running simultaneously | 805 W |
| 72 V × 42 Ah nominal energy | 3,024 Wh |
| Nominal energy × 75% | 2,268 Wh modeled AC energy |
| 2,268 Wh / 805 W | 2.82 h |
| 2,268 Wh / 291.25 W | 7.79 h |
| 2,268 Wh / 120 W | 18.90 h |
| 2,268 Wh / 685 W | 3.31 h |
| 2,268 Wh / 171.25 W | 13.24 h |
| 291.25 W × 8 h | 2,330 Wh AC |
| Previous row × 1.20 | 2,796 Wh AC target |
| 2,796 Wh / .75 | 3,728 Wh nominal required |
| 3,728 Wh / 72 V | 51.78 Ah arithmetic requirement |
| Target minus 2,268 Wh available in model | 528 Wh shortfall |

## Sources

- [Exide EP-series technical brochure](https://docs.exideindustries.com/pdf/industrial-export-batteries/products/ups-batteries/12v-agm-vrla-ep-series.pdf), especially the specification table on PDF page 5.
- [Eaton: VA versus watts](https://www.eaton.com/us/en-us/products/backup-power-ups-surge-it-power-distribution/backup-power-ups/va-versus-watts--eaton.html).
- [Oxymed 10 LPM Dual Flow](https://oxymedindia.com/oxymed-10): published 610 W; other flow-specific power claims are not inferred.
- [Yuasa VRLA operating instructions](https://www.yuasa.com/media/akeneo_connector/asset_files/I/n/Instructions_NP_REW_2b57.pdf).
- [Schneider medical-grade guidance](https://www.se.com/us/en/faqs/FAQ000271638/) and [life-support policy](https://www.se.com/us/en/faqs/FAQ000270822/). Product-specific manufacturer restrictions cannot be generalized as approval of another brand.
- [Schneider daisy-chaining guidance](https://www.se.com/sg/en/faqs/FA157424/) and [parallel-output guidance](https://www.se.com/us/en/faqs/FA157484/).
- [ResMed Astral clinical guide](https://document.resmed.com/documents/rc-clinical-guides/astral-series/clinical-guide/astral-100-150_clinical-guide_row_eng.pdf): example of device-specific power management, not instructions for the author's Trilogy.
- [BIS registration information](https://www.crsbis.in/BIS/registration-page.do) and [BIS visitor information on India's nominal electricity supply](https://www.bis.gov.in/other/31_PM_Hydrometry.pdf).
- [CDC generator safety](https://www.cdc.gov/natural-disasters/psa-toolkit/use-a-generator-safely.html).
- [Government of India emergency service](https://112.gov.in/).
- [Philips Trilogy EV300 specification](https://www.philips.co.in/healthcare/product/HCIN2200X15B/trilogy-ev300-hospital-ventilator), consulted to resolve the model wording; not confirmed as the household device.

## Verification and unresolved limits

Automated checks cover the arithmetic, margins, shortfalls, invalid inputs, W/VA separation, UI updates, literal-text output, model-loading failure, rendered templates, local assets, anchor targets and disclaimer presence. Commands:

```sh
node --test tests/*.test.cjs
venv/bin/python -m unittest discover -s tests -p test_power_pages.py -v
git diff --check
```

Results: all **40 JavaScript tests** and **4 Flask page tests** passed; `git diff --check` passed. HTTP reads from the existing local server also confirmed that the updated Power Backup Guide and emergency disclaimer are being served.

No browser visual test, electrical measurement, battery discharge test or clinical assessment was performed in this audit. Still needed for a real installation: exact device models/manuals; measured running and start-up loads with accessories/charging; current battery health and charge; manufacturer runtime data; charger and wiring compatibility; approved transfer/backup arrangements; and a documented commissioning and escalation plan. The emergency page's underlying clinical procedures remain experience-based and require review by the treating team.
