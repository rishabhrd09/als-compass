# Reusable prompt: static ALS CareKosh deployment

This replaces the earlier Render/Flask-server prompt. Copy the prompt below into a coding assistant with the repository open. Fill in the exact domain when known; local preparation can proceed without it.

---

Prepare ALS CareKosh — Caregiver’s Compass as a static website for GitHub-connected Cloudflare Pages.

Project:
`/Users/rishabh/coding_claude_projects/als_knowledgebase_compass/als_mnd_info_compass/als-compass`

Expected existing remote:
`https://github.com/rishabhrd09/als-compass.git`

Full registered Cloudflare domain: [FILL IN INCLUDING THE SUFFIX]
Preferred hostname: [ROOT DOMAIN OR als.YOUR_DOMAIN]
Hosting plan: Cloudflare Pages Free; no paid services or AI integration.

Read `docs/deployment-guide.md` and verify current official Cloudflare documentation. Preserve the design, branding, page URLs, medical content, references, review dates and existing browser interactions. Keep Flask/Jinja available for building or local development if useful; the deployed website must require no running Python backend, Pages Functions, Worker, database or AI keys.

First complete the local preparation:

1. Inspect repository instructions, current branch, actual remote/default branch and uncommitted work. Preserve changes and new assets. If needed, use `codex/prepare-static-deployment` from the current working state. Do not discard work, force-push, rewrite history, create a duplicate repository or change repository visibility.

2. Audit public page routes and browser network requests. Build an explicit export manifest instead of crawling arbitrary routes. Implement `scripts/build_static.py` to render the real public pages and copy only required assets into generated `dist/`. Export `/` as `index.html`, other pages as `<slug>/index.html`, and a top-level `404.html`. Preserve request-dependent navigation/disclaimer context while rendering. Exclude legacy AI, image-server and animation-job endpoints from the export. Never invoke them during the build.

3. Export only the reviewed JSON needed by the public site, using `/content/faq.json`, `/content/communication-tech.json` and `/content/research-categorized.json` or a documented equivalent. Update all frontend consumers to use those static files in the export. Keep local development functional with a shared source of truth. Do not maintain manually duplicated FAQ answers. Preserve the seven suggested answers with their notes and sources; typed questions must remain local and show the coming-soon message. Keep the three model options explicitly preview-only.

4. Create minimal, pinned `requirements-static.txt`, starting from the imports needed for Flask/Jinja rendering and python-dotenv. Verify in a clean environment without AI keys, embeddings, ChromaDB, PyTorch, Gunicorn or Manim. Keep the existing development/research tooling separate. Commit a tested full Python version in `.python-version` that Cloudflare supports.

5. Create `scripts/build_pages.sh` with fail-fast error handling. It must install only `requirements-static.txt`, invoke the exporter and exit unsuccessfully if export validation fails. Document the Pages build command as `bash scripts/build_pages.sh`, output `dist`, preset None and build variable `SKIP_DEPENDENCY_INSTALL=1` for production and preview. This avoids automatically installing the existing AI-heavy root requirements file.

6. Make export deterministic and safe to rerun. Clean only the generated output directory, verifying its location. Do not copy the repository wholesale, follow asset symlinks outside approved directories or publish `.env`, source code, raw private material, local environments, caches, backup files or render intermediates. Check asset references, missing JSON, template syntax, broken internal links and Cloudflare's per-file/count limits. Include required fonts, imagery, PDFs and pre-rendered videos; do not start rendering jobs during hosting builds.

7. Add meaningful export tests and run the relevant existing Node and Python tests with their appropriate development dependencies. Serve `dist` alone with a static file server while the Flask server is not needed by the browser. Verify every page, deep link, refresh, JSON request, research filter, FAQ topic/search, all seven suggestions, the typed-question notice, power calculator, image viewer, media, PDFs, keyboard interaction and mobile layout. Use a Pages-compatible local preview to check redirects, headers and 404 behaviour. Verify there are no calls to Flask APIs or localhost endpoints. Repeat the build from a clean checkout to catch untracked dependencies.

8. Audit the intended Git commit and repository history for secrets or private source material without revealing values or conversations. `.gitignore` does not erase tracked history. Include all reviewed new assets, tests and build files; exclude generated `dist/` and `.venv-static/` from Git. Preserve intended repository visibility. Fix README launch instructions to match the static build, document exact tested commands and list the final export manifest. Use default Pages caching unless a tested requirement calls for something else. Do not change medical claims or research dates to make a build pass.

9. Report the finished local changes, actual test results, generated artifact location, remaining blockers and exact Pages settings. Do not push, merge, create a public preview, change DNS or purchase services in this preparation phase. Ask for the final launch go-ahead only after the build is reviewable.

After I explicitly approve publishing the reviewed release:

- Verify authentication, remote, intended repository visibility and the full staged file list. Commit and push a feature branch to the existing GitHub repository, open a pull request and complete the approved merge after checks pass. Do not overwrite other branches.
- In the Cloudflare account containing the domain zone, create or reuse the correct Pages project with Git integration. Select only the approved repository, verified production branch, build command, output directory and build variables. Deploy generated `dist` only. Stay on the Free plan; do not enable a backend or add provider secrets.
- Test the actual assigned `pages.dev` URL before moving the domain. Treat preview URLs as public unless actual access protection has been configured.
- Obtain the exact domain if missing. Associate the chosen hostname through Pages Custom domains first and follow its DNS confirmation. Keep Cloudflare nameservers, preserve email records/unrelated subdomains and record existing affected DNS. Do not reuse Render DNS instructions. For the root-domain choice, configure and verify www-to-root redirection while preserving paths and queries. Wait for valid HTTPS.
- Verify the production site, static-only behaviour, real 404s, canonical domain and deployment commit. Provide the final URL, GitHub commit/PR, build settings, update workflow and rollback instructions. Never claim an action succeeded without confirming its actual result.
- If account access is unavailable, finish all independent work and provide precise remaining dashboard steps. Do not ask me to paste tokens, passwords or private source conversations into chat.
