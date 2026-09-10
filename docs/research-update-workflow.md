# Updating the ALS research review

Use the same workflow whenever you want a new edition. It has two parts: Python collects public leads and checks the update files; a browsing-capable research assistant or researcher reads the evidence and edits the draft. **The script alone does not perform a medical literature review or write clinical conclusions.** No new Python package or paid API key is needed for the collector.

## Simplest option: reuse this instruction

Paste this into the project conversation:

> Follow `prompts/update_als_research.md` to perform a deep research refresh through today. Review every category, preserve the design, validate the draft, apply the completed update locally with a backup, and show me the changes and preview.

For a historical cutoff, replace “today” with the exact date. The fixed prompt reads the **current** edition and prepares a fresh run; it has no hardcoded drug milestones or year. It requires checking every existing entry and discovering new developments across all seven sections. If you only want a draft, say “prepare a draft only” in your instruction.

## Terminal option: prepare the next review

```sh
cd /Users/rishabh/coding_claude_projects/als_knowledgebase_compass/als_mnd_info_compass/als-compass
venv/bin/python scripts/research_update.py prepare
```

The cutoff defaults to today's local date. To specify one:

```sh
venv/bin/python scripts/research_update.py prepare --as-of YYYY-MM-DD
```

Replace `YYYY-MM-DD` with an actual date between the existing edition and today. The command works from any working directory if you invoke the Python interpreter and script by their absolute paths. It creates a unique folder under `.research-updates/`; repeated runs never overwrite one another.

The collector:

- Refreshes every NCT ID referenced by the current review and saves raw records.
- Reports changed status, phase, locations, posted results and registry update dates.
- Searches for recently updated ALS studies and recently indexed PubMed papers, overlapping the old cutoff by 14 days. Discovery leads can include older papers newly indexed; confirm their publication dates before using them.
- Records network failures, records newer than the cutoff and search truncation explicitly. These gaps must be resolved during research.
- Copies the current edition into a draft without changing the live content or its review date.

It uses the [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/about-api/api-migration) and [NCBI ESearch](https://www.ncbi.nlm.nih.gov/books/NBK25499/). Set `NCBI_EMAIL` if you wish to supply NCBI with a contact address for the requests. The script does not send patient information, project documents or API keys. `--offline` prepares the files without fetching anything and leaves a mandatory source-collection gap in the audit.

## Finish a prepared run

The command prints its exact folder and `PROMPT.md` path. Ask the research assistant:

> Read and follow the PROMPT.md at the path printed by the prepare command. Use that existing run and complete its research review.

The run includes:

| File | Purpose |
| --- | --- |
| `baseline.json` | Exact original content, used to detect concurrent changes |
| `draft.json` | The proposed complete edition |
| `registry/*.json` | Raw retrieved public trial records |
| `registry_changes.json` | Before/after differences in tracked records |
| `discovery.json` | Candidate studies and PubMed links to investigate |
| `registry_snapshot.json` | Candidate registry summary to reconcile with the draft |
| `manifest.json` | Cutoff, original content hash and collection issues |
| `review.json` | Explicit review coverage for each entry, topic and collection gap |
| `PROMPT.md` | The fixed research instructions plus this run's path and cutoff |
| `REPORT.md` | Collection summary, not a claim that research is complete |

After source review, set each entry's audit `reviewed` flag, cited `source_ids`, and substantive note. Record discovery sources/findings for every section and evidence resolving collection issues. New entries need audit records too. Use actual source access dates within the review run. Remove sources that are no longer cited from the page library; retain useful historical references in `RESEARCH_REVIEW.md`.

Use the printed run path in place of `RUN_DIRECTORY`:

```sh
venv/bin/python scripts/research_update.py validate --run RUN_DIRECTORY
venv/bin/python scripts/research_update.py apply --run RUN_DIRECTORY
venv/bin/python -m unittest test_research test_research_update
venv/bin/python verify.py
```

Validation produces `CHANGES.diff` and `VALIDATION.md`. It checks source references, dates, category coverage, retained IDs, registry consistency, communication compatibility and declared review coverage. It cannot determine whether a claim is medically correct or a reviewer actually read a paper. The source-based research step remains essential.

Apply reruns validation, refuses to overwrite a concurrently changed edition, creates `backup/research_categorized.json` in the run folder, and atomically replaces the local content and matching dated registry snapshot. The homepage, research page title and downloaded filename follow the new edition automatically. Existing dated snapshots remain available. If an interrupted apply leaves a lock or backup, inspect it before retrying; do not discard the saved original.

The local packets, review audit and backups are ignored by Git. Keep the run folder if you need its audit trail, and include the reviewed JSON, dated registry snapshot and any intentionally selected review report when saving project changes. A fresh run can be started if another person or task updates the live file meanwhile.

## Review scope and limits

Registry and PubMed searches are discovery aids. They do not cover all regulatory decisions, sponsor announcements, unindexed papers, technology documentation or Indian access changes. The fixed prompt requires those additional checks. It preserves negative findings, distinguishes endpoints from exploratory signals, and treats approval, trial authorization and planned milestones separately.

The older `manage_research.py` GUI still generates an obsolete, date-specific draft format. Use this workflow for new reviews; its save guard prevents those older drafts from erasing the current schema. No automatic schedule or production deployment is configured by this workflow. Run it when you want a refresh.
