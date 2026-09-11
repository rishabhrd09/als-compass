# Emergency guidance follow-up, 11 September 2026

The user asked for explicit boundaries between immediate trained caregiver actions and emergency airway procedures, and for clear escalation to skilled help. This is a focused content correction, not clinical validation of the website.

## Changes

- Replaced forceful bagging, routine saline instillation and repeated clearance cycles with immediate escalation for a catheter that will not pass, possible blockage/displacement, ineffective ventilation or severe deterioration.
- Calls to 112 and the treating respiratory/ICU team occur alongside trained support. Caregivers do not need to exhaust troubleshooting or wait for an SpO2 threshold.
- The top notice, flowchart, written scenarios and critical warnings distinguish external equipment checks, prescribed/trained suction, and airway procedures requiring specific competence and authorization. Equipment technician qualifications alone are insufficient for TT replacement.
- Removed unqualified cuff-adjustment sequences and claims that high pulse/BP proves retained secretions or that Ambu offers general relief.
- Unlinked the old infographic because its instructions did not include these boundaries. The original asset remains on disk.
- Updated the matching existing FAQ answer, emergency fallback records and source FAQ records used by ingestion. Other FAQ topics and counts remain intact. Source changes do not by themselves refresh an existing vector database; no vector database rebuild was performed.

## Primary references

- [NTSP adult emergency guidance](https://tracheostomy.org.uk/healthcare-staff/emergency-care/emergency-algorithm-tracheostomy)
- [NTSP emergency tracheostomy management](https://tracheostomy.org.uk/storage/files/Emergency%20tracheostomy%20management.pdf): risks of vigorous ventilation through a displaced tube and assessment of patency.
- [AARC artificial airway suctioning guideline](https://www.aarc.org/wp-content/uploads/2022/10/cpg-artificial-airway-suctioning.pdf): routine saline instillation generally avoided; trained, appropriate suction technique.
- [Government of India emergency response](https://112.gov.in/): 112.

These professional resources inform the cautions. The website does not reproduce a clinical airway algorithm as an untrained caregiver procedure, and does not override a person's trained, individualized emergency plan.

## Verification

Five focused emergency regression tests check early escalation, trained roles, blocked-tube wording in both presentations, removal of unsafe duplicate instructions, correct scenario placement and balanced content markup. Nine existing Flask page tests pass for rendering, local links/assets and FAQ structure. Four communication rendering tests pass after restoring the two original Tobii records. No browser visual inspection was performed in this pass.
