# FAQ content restoration — 14 September 2026

The user approved a content-only restoration after comparing the practical caregiver FAQ with the broader editorial rewrite. This restores version 3.1's language and concrete routines where possible, retaining specific factual and emergency-care corrections. It is not a byte-for-byte rollback or a new clinical review.

## Evidence and scope

- Baseline: `git show 3d14d7c^:data/als_comprehensive_faq.json`, version 3.1, dated 30 December 2025. This is the same content blob as commit `e6e25a9`.
- Rewrite: `3d14d7c` (11 September 2026), version 4.0: all 22 answers changed, while six categories and the question count stayed the same.
- FAQ data did not change in the static deployment, mobile fixes or `c473694` assistant UI update.
- The local `docs/care-handbook-refactor.md` note about 22 unchanged records described the layout pass, not the final combined content commit. It must not be used as evidence that the September FAQ wording was preserved.
- Current source: `data/als_comprehensive_faq.json`. `public_site.py` maps it to `/content/faq.json`; both the FAQ page and assistant read that file. The static export verifies the JSON equals the source.
- All current question titles, categories, tags and per-question sources remain. In particular, the hospital question keeps its current title so the seventh assistant suggestion continues to match it.
- No HTML templates, CSS, frontend JavaScript, backend integration or deployment settings were changed. Existing emergency fallback datasets are intentionally not rolled back.
- Metadata identifies this as version 4.1, dated 14 September 2026, with the historical baseline. Misleading references to knowledge cards were removed from metadata. The user-requested page disclaimer is unchanged.
- The original published FAQ supplies the caregiver wording. Raw WhatsApp messages were not rechecked, and no new testimonial, family count or firsthand quotation is being asserted.

## Per-answer restoration and retained corrections

| Topic | Restoration and exception to the old version |
|---|---|
| What is BiPAP? | Original brief introduction and three bullets restored. Corrected EPAP/CO₂ explanation and removed the promise of preventing rapid decline. |
| When Does a PALS Need BiPAP, How to Decide? | Original sleep, pillow, headache and mealtime observations restored. Kept accurate ventilation explanation; removed the requirement to wait for several signs. |
| How BiPAP Usage Progresses Over Time? How many hours should PALS use BiPAP daily? | Restored the progression/dependency explanation. Retained individual hours, assessment of new symptoms and no automatic tracheostomy threshold. |
| Can early BiPAP help delay tracheostomy? | Original practical list retained. Removed fixed 6-month-to-2-year claims, guaranteed prevention and advice for peers to set pressures. |
| When Should we use oxygen concentrator along with BiPAP? | Kept the corrected oxygen guidance in shorter practical language. Did not restore the universal SpO₂ trigger, 2–4 L/min dose or assumed connection port. |
| When Is Tracheostomy Needed? What are the decision criteria? | Original personal introduction and ALSCAS discussion tip restored. Replaced automatic SpO₂/hour/intubation decision rules and unverified quotations with practical discussion questions. |
| How to delay or avoid emergency tracheostomy? | Restored the preparation checklist. Kept individual equipment/training requirements and removed guarantees about aspiration and tracheostomy prevention. |
| Why Do Families Delay BiPAP Even After Knowing the Signs? | Restored the original caregiver anxiety, unfamiliarity and decision-making paragraphs verbatim where factual. Removed the unattributed first-person quote, blaming language and disease-progression claims. |
| What are HME filters and why are they important? | Original short explanation restored; retained compatibility, blockage and humidification correction. |
| When should we consider a feeding tube (PEG)? | Original practical mealtime signs restored. Removed guaranteed lung/weight protection and the 20-minute procedural rule. |
| Can PALS still eat by mouth after PEG? | Original concern about losing the pleasure of eating retained. Kept swallowing assessment and aspiration limitations. |
| How to thicken water for PALS with swallowing difficulty (dysphagia)? | Restored the simple explanation and two historical product examples. Excluded unverified prices/availability, kitchen-gum substitution and automatic PEG claims. |
| How can families work with hospital staff during an ALS emergency? | Restored caregiver advocacy and practical hospital handover. Preserved the entire existing emergency escalation passage, moved after the main answer. Kept the current question title for assistant matching; did not restore blanket accusations or automatic early discharge. |
| How Do I Manage Excessive Saliva/Drooling? | Original cloth, bedside suction, mouth-care and bib routines restored. Retained positioning/training boundaries; removed seller claims and blanket dairy restriction. |
| Is glycopyrrolate safe for reducing saliva? | Restored original short benefits/side-effects format. Retained prescription, monitoring and urgent breathing boundaries; removed unverified brand assumptions. |
| How to manage constipation and bowel movements in a bedridden PALS? | Restored daily food, fluid, timing and medicine-review emphasis. Excluded fixed laxative doses/day-count escalation, blanket fluid targets, unsupported remedies and side-effect-free claims. |
| How to prevent bedsores? | Original prevention-first opening, pump checks and dry-skin routine restored. Kept individual turning schedule, early skin checks and no massage/oil/powder treatment claims. |
| Electrolyte Imbalance in PALS - What to Know and How to Manage | Restored feed tracking, illness and hospital handover emphasis. Kept tests/individual treatment, no automatic monthly schedule or salt/ORS self-treatment, and immediate escalation for altered responsiveness. |
| What Equipment Do We Need as ALS Progresses? | Original concrete equipment list restored in needs-based groups. Kept prescriptions/training and removed universal oxygen/Ambu requirements. |
| How to Set Up a Home ICU Room for BiPAP + Tracheostomy? | Original simple room-setup introduction, two equipment tables and backup checklist restored. Kept circuit compatibility, prescription, privacy, generator and airway-training corrections. |
| How do I manage if there is a power cut while PALS is on BiPAP or ventilator? | Original direct introduction and both guide links restored. Kept tested runtime and immediate outage response instead of estimates as guarantees. |
| Will using a power wheelchair or lift make the PALS weaker faster? | Original reassurance and energy-for-daily-activities paragraph restored. Kept individualized movement and removed categorical exercise/disease-progression claims. |

## Supporting references checked for the retained corrections

These references support specific medical boundaries, not attribution of community experiences or product endorsements. Existing question-level links remain available as further reading.

- [MND Association: breathing support](https://www.mndassociation.org/sites/default/files/public/2026-01/8A-Support-for-breathing-problems.pdf): breathing assessment, support and individual needs.
- [NICE NG42 full guideline](https://www.nice.org.uk/guidance/ng42/evidence/full-guideline-pdf-2361774637): NIV assessment; indexed excerpt checked because the recommendations webpage returned HTTP 403 in this session.
- [MND Association: swallowing and feeding](https://www.mndassociation.org/professionals/management-of-mnd/dysphagia) and [Hull NHS: PEG](https://www.hey.nhs.uk/patient-leaflet/percutaneous-endoscopic-gastrostomy-peg/).
- [RCSLT: thickened fluids](https://www.rcslt.org/members/clinical-guidance/eating-drinking-and-swallowing/thickened-fluids/): swallowing assessment and individual preparation.
- [MND Association: saliva](https://www.mndassociation.org/professionals/management-of-mnd/saliva).
- [NHS: constipation](https://www.nhs.uk/conditions/constipation/) and [NHS: laxatives](https://www.nhs.uk/medicines/laxatives/).
- [NICE CG179 recommendations](https://www.nice.org.uk/guidance/cg179/chapter/Recommendations): indexed recommendations checked; the direct page returned HTTP 403. Individual pressure care and no massage/rubbing to prevent pressure injury.
- [MedlinePlus: low blood sodium](https://medlineplus.gov/ency/article/000394.htm): investigation and cause-specific treatment.
- [St George's NHS: tracheostomy humidification](https://www.stgeorges.nhs.uk/gps-and-clinicians/clinical-resources/tracheostomy-guidelines/humidification/).
- [MND Association: acute and emergency care](https://www.mndassociation.org/professionals/management-of-mnd/management-by-specific-professions/acute-urgent-and-emergency-care-staff) and [NTSP emergency guidance](https://tracheostomy.org.uk/healthcare-staff/emergency-care/emergency-algorithm-tracheostomy). The existing emergency escalation passage is retained word-for-word after the hospital handover answer.
- [MND Association: muscle weakness](https://www.mndassociation.org/professionals/management-of-mnd/management-by-symptoms/muscle-weakness).

## Rules for future FAQ edits

1. Presentation, model-label and deployment work must preserve the content file.
2. Start from the approved caregiver answer. Keep useful everyday details and plain sentences; do not turn each answer into a uniform clinical summary.
3. Correct the specific sentence that needs correction. Document the reason rather than silently rewriting the whole answer.
4. Keep lived experience distinct from medical claims. Do not invent quotes, case histories, product availability or promises of benefit.
5. Keep necessary warnings next to the relevant action; avoid repeating the general disclaimer in every paragraph.
6. Preserve question titles used by the assistant, or deliberately update and test the matching suggestions.
7. Review prose as well as counts and layout. Tests protect representative caregiver passages and practical details, but cannot judge the whole editorial quality.

## Verification

- 38 tests passed: 15 Node FAQ/assistant checks, 3 editorial/markup checks, 5 equipment/page checks, 5 emergency checks and 10 static-export checks.
- Preview export succeeded: 17 pages plus 404, 3 JSON files, 201 files, 1,147 local references checked.
- Exported FAQ JSON equals the edited source. All 22 titles/tags/source lists match the pre-restoration version. The prior emergency escalation passage is present verbatim.
- Browser: original caregiver paragraph visible; searching “Rent first” returns the equipment answer; all seven suggested assistant questions display the restored answers; typed questions still show coming soon. No assistant console errors observed.
- Existing desktop layout inspected; mobile widths 320 and 390 checked. Both equipment tables scroll inside their containers and neither width produces horizontal page overflow. No physical-device test was performed.
- `git diff --check` passed. No application templates, styles, scripts, backend code or deployment settings changed.

Run from the repository root:

```sh
node --test tests/care-faq.test.cjs tests/faq-assistant.test.cjs
PYTHONPATH=tests CAREKOSH_STATIC_BUILD=1 .venv-static/bin/python -m unittest tests.test_faq_restoration tests.test_equipment_pages tests.test_emergency_guidance tests.test_static_export
.venv-static/bin/python scripts/build_static.py --preview
```

The preview is local. Commit, push and merge are separate actions; this restoration has not been deployed by the editing task.

## Initial ALSCAS further-reading review — 14 September 2026

This records the initial review. The selective-reading policy below supersedes its 17-link selection.

Follow-up request: inspect ALSCAS and add relevant further-reading links without rewriting the restored answers. The supplied `https://alscas.com/` did not resolve in this session, including a direct network check. [ALSCAS's own Linktree](https://linktr.ee/alscasindia) identifies [alslifemanagement.weebly.com](https://alslifemanagement.weebly.com/) as its website. Links use that verified host, not an assumed redirect or invented path.

Seventeen question-level references were appended to `sources`. All 22 answers, warnings, tips, titles, tags, metadata and previous source entries are unchanged from the start of this follow-up. The existing FAQ and assistant renderers display the additions automatically. Clinical references remain first; the new labels explicitly identify caregiver perspectives, guides or checklists. These links do not constitute endorsement of every instruction on the external site.

### Reviewed destinations

- [Ventilator](https://alslifemanagement.weebly.com/ventilator.html): background terminology. It also contains personal device settings, historical prices and categorical mode recommendations, which are not adopted as instructions.
- [Ready Reckoner](https://alslifemanagement.weebly.com/ready-reckoner-for-als-journey.html): dated 28 June 2025; sections 2, 3, 6 and 7 cover the linked topics. Links name the section because the headings have no HTML anchor IDs. Its treatment thresholds and timelines are not adopted into our answers.
- [Swallowing difficulties](https://alslifemanagement.weebly.com/als-swallowing-issues.html): swallowing signs, texture support, feeding tubes and mouth care. The existing individualized swallowing guidance remains authoritative for our answers.
- [Home equipment and supplies](https://alslifemanagement.weebly.com/home-vent-care-management-procedures-equipments-and-required-supplies.html): practical inventory and room organization. Historical prices and one family's quantities/frequencies are not universal requirements.
- [Assistive Devices for ALS Journey](https://alslifemanagement.weebly.com/uploads/2/6/5/5/26556882/assistive_devices_for_als_journey.pdf): dated 11 December 2024; page 8 HME, page 12 air mattress, page 17 oxygen equipment, page 22 batteries. PDF links use the corresponding `#page=` fragment, with page numbers also in the visible labels for readers whose PDF viewer ignores fragments. These are equipment background, not circuit, dosing or runtime prescriptions.

Also reviewed the site's Learnings, Daily Routine, Feed Preparation and PEG Feeding, Knowledge Nuggets, Health Monitoring Guide and hospital experience material. Relevant mentions alone were not enough to add a link where the requested question was not answered, or where the relevant passage conflicted with retained factual corrections.

### Mapping of all 22 FAQs

| FAQ topic | Added reading or reason for retaining existing references only |
|---|---|
| BiPAP basics | Ventilator: terminology and explanation. |
| When BiPAP is needed | Ready Reckoner, section 3. |
| Increasing BiPAP hours | Ready Reckoner, section 6. |
| Early BiPAP and tracheostomy | Ready Reckoner, section 6; background on support, not evidence of guaranteed delay. |
| Oxygen alongside BiPAP | Assistive Devices, page 17. |
| Tracheostomy decisions | Ready Reckoner, section 6; caregiver planning perspective, not a fixed decision rule. |
| Preparing before an emergency tracheostomy | Ready Reckoner, section 7. |
| Family hesitation about BiPAP | Ready Reckoner, section 7; familiarity through visiting a family with experience. |
| HME filters | Assistive Devices, page 8. |
| When to consider PEG | Swallowing difficulties. |
| Eating by mouth after PEG | No direct explanation of this specific question was found in the reviewed material; retain existing references. |
| Thickening liquids | Swallowing difficulties. |
| Working with hospital staff | Reviewed material includes individual complaints and generalized treatment claims, rather than a suitable collaborative emergency-handover guide; retain existing references. |
| Saliva and drooling | Swallowing difficulties: saliva pooling and oral hygiene. |
| Glycopyrrolate safety | Health Monitoring Guide names the drug but does not explain its safety, contraindications or side effects; retain existing references. |
| Constipation | Learnings gives a personal herbal/laxative escalation regimen; retain existing references rather than present it as a general bowel-care plan. |
| Bedsores | Assistive Devices, page 12; mattress experience only. |
| Electrolytes | Learnings and Daily Routine describe homemade salt/sugar feeds, which do not establish treatment for a diagnosed electrolyte imbalance; retain existing references. |
| Equipment as needs change | Home equipment and supplies. |
| Home ICU room | Home equipment and supplies. |
| Power cut | Assistive Devices, page 22. |
| Wheelchairs and lifts | Ready Reckoner, section 2; aids and transfers, not evidence about disease progression. |

### Follow-up verification

- Direct article reads succeeded on the working ALSCAS host; the equipment PDF returned HTTP 200 with PDF content. The PDF text/page mapping was checked; the web screenshot service could not render the PDF, so no visual review of its diagrams is claimed.
- Comparing JSON before and after this follow-up confirms exactly 17 appended sources, with no changes to any other field and no duplicate source URLs within a question.
- The same 38 FAQ, assistant, restoration, equipment, emergency and export tests passed again. The static preview build passed with 17 pages plus 404 and 1,147 local references checked.
- Browser inspection found all 17 ALSCAS links in the rendered FAQ, including the four intended PDF page fragments, `target="_blank"` and `rel="noopener"`. The BiPAP answer visibly shows the new link after its existing NHS reference.
- Changes remain local and uncommitted on `restore-practical-faq`.

## Selective further reading — 15 September 2026

The user requested fewer references: ALSCAS only for major BiPAP, PEG and home ICU topics, with other links retained only where they add useful guidance. No answer, warning, tip, title, tag, metadata or layout was changed in this follow-up. Only the `sources` lists were reduced; prior research notes above remain an editorial record.

The final selection has 14 links across 11 FAQs; the other 11 have empty source lists and therefore show no further-reading heading. ALSCAS appears only three times:

| FAQ | Retained further reading |
|---|---|
| What is BiPAP? | ALSCAS ventilation background, then NHS ventilation explanation. |
| When is BiPAP needed? | MND Association breathing-support guide. |
| Oxygen alongside BiPAP | MND Association acute/emergency guidance. |
| Tracheostomy decisions | MND Association breathing-support guide. |
| HME filters | St George's Hospital humidification guidance. |
| When to consider PEG | ALSCAS swallowing/feeding-tube guide, then Hull NHS PEG information. |
| Thickening liquids | RCSLT thickened-fluid guidance. |
| Working with hospital staff in an emergency | MND Association acute care and NTSP tracheostomy emergency guidance. |
| Glycopyrrolate safety | NHS glycopyrronium prescribing and adverse-effects information. |
| Electrolytes | MedlinePlus fluid/electrolyte overview. |
| Home ICU room | ALSCAS home equipment and supplies checklist. |

Routine answers and repeated subtopics have no external reading block. Existing links within the answer text, including the local power-backup guides, remain intact. The assistant uses the same curated lists. Existing tests now accept an empty list rather than requiring references on every answer; the rendering check also verifies that absent/empty sources produce no empty reading section.

Reading order: whenever an ALSCAS link is present, place it first in the question's `sources` list, before other references. Preserve this order in future editorial updates. Both the FAQ page and suggested assistant answers display the stored source order. This does not add ALSCAS links to any additional FAQs.

Verification: all 38 existing tests passed, and the static preview exported 17 pages plus 404 with 1,147 local references checked. Comparing the pre-selection JSON confirms only source lists changed, and the exported FAQ matches the source file. Browser inspection confirmed the family-hesitation answer has no further-reading section, while the home ICU answer retains its specific ALSCAS equipment checklist.
