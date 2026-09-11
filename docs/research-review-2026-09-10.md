# ALS research review — 10 September 2026

Evidence cutoff: **10 September 2026**. Retrieval/review date: **11 September 2026**.

The reader-facing research artifact is `/research-updates`. It includes summaries, limitations, India/access context, inline references, full source metadata, a glossary, review method and changes. The review covers every previous topic, consolidates duplicate Neon entries, moves observational Indian genetics to the India section, and adds selected important developments. It is not an exhaustive registry of every ALS study and does not claim specialist medical sign-off.

## Evidence and important corrections

The edition contains 54 entries, seven visible topics, 78 sources and 26 preserved registry summaries. `data/research_categorized.json` is the content source for the page, homepage preview and existing communication consumers. `data/research_registry_snapshot_2026-09-10.json` records the public registry statuses, update dates, countries, phases and results-posted flags retrieved for this review.

Regulatory decisions establish indications; registries document study designs and recorded recruitment; controlled papers inform efficacy. Sponsor announcements are identified and used for operational milestones or explicitly preliminary findings. A negative primary endpoint remains visible even where later subgroup, biomarker or extension analyses are encouraging. Undated product documentation does not establish availability on the cutoff date.

Notable corrections include:

- CNM-Au8: the August sponsor update plans a submission in early Q4 2026; it is not an approval or completed submission.
- NurOwn and masitinib: distinguish planned confirmatory trials from established treatment and active enrollment.
- PrimeC: the August 31 PARAGON redesign is subject to FDA alignment.
- NUZ-001: enrollment closed; the cohort is in follow-up.
- Dazucorilant: primary functional endpoint missed; secondary/extension survival findings and Phase 3 plans remain qualified. Its recruiting registry label does not establish enrollment in the planned pivotal study.
- Rozebalamin: mecobalamin/E0302, not MT-1186; Japan-specific approval.
- Nuedexta: a symptom treatment for pseudobulbar affect, separated in the data from ALS-directed medicines.
- OptiKey: version 4 removed support for Tobii Eye Tracker 5/4C/EyeX; legacy compatibility is explained.
- India: remove unverified price, supply and future-access promises. Form 12A is the personal-import application; Form 12B is the permit.

The complete citations and dates are in the JSON `source_library` and the page's Source library. Links may change; registry status can lag behind operational events. “No results posted” refers only to the registry and must not be used to infer that no paper or announcement exists.

## Maintaining schema version 2

Edit the reviewed JSON deliberately. Preserve stable entry/source IDs because the homepage and citations use deep links. Each category must be assigned to exactly one section. Every entry needs a name, subtitle, status/status kind, summary, evidence, limitations and valid `source_ids`. Keep legacy communication aliases and fields until those consumers are migrated.

Source records include `id`, `publisher`, `title`, `published_on` (ISO day/month or null), `accessed_on`, `url` (HTTPS), and `kind`. Do not invent a day for a source that only states a month. Update both source dates and entry `evidence_date` when replacing evidence. The review date and evidence cutoff are separate fields.

The older LLM Research Manager generates drafts in the previous format. A save-time schema check now prevents those incomplete drafts from overwriting this edition. Its JSON editor can accept a fully reviewed version-2 payload; the draft generator itself has not been upgraded. Structural validation does not verify medical accuracy or replace source checking.

The page is server-rendered: all entries and references remain available without JavaScript. JavaScript adds global search, topic/status filtering, hash navigation, citation disclosure and print expansion. Recruitment filtering uses the cited registry record, independently of the editorial status badge. Printing includes every topic and the sources.

## Local verification

```sh
cd /Users/rishabh/coding_claude_projects/als_knowledgebase_compass/als_mnd_info_compass/als-compass
venv/bin/python -m unittest test_research
venv/bin/python verify.py
node --check static/js/research.js
PORT=5001 bash run_dev_macos.sh
```

Open `http://localhost:5001/research-updates`. The existing development script's printed browser hint may still say port 5000; `PORT=5001` sets the actual Flask port. No new dependency, database migration or production deployment is required.
