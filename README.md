# ALS CareKosh — Caregiver’s Compass

Practical ALS caregiving guides, community FAQs, communication resources and evidence-based research updates. The public website is a static export intended for **https://als.carekosh.com**, hosted on Cloudflare Pages.

The assistant currently answers seven suggested questions from the same FAQ data used by the FAQ page. Typed questions receive a coming-soon notice. Its three model options are placeholders; the published website makes no LLM calls and requires no API keys.

## Build and preview on your Mac

In your existing checkout:

```sh
cd "/Users/rishabh/coding_claude_projects/als_knowledgebase_compass/als_mnd_info_compass/als-compass"
./venv/bin/python -m venv .venv-static
source .venv-static/bin/activate
bash scripts/build_pages.sh --preview
bash scripts/preview_pages.sh
```

Open **http://127.0.0.1:8788/**. Stop the preview with Control+C. Subsequent builds only need activation and the last two commands. The preview does not rebuild automatically; rebuild and refresh after edits.

For a new checkout, install Python **3.11.15** (the version in `.python-version`) and create the environment with `python3.11 -m venv .venv-static`. The build uses eight pinned Python packages from `requirements-static.txt`. Node.js/npm is needed for the optional Cloudflare preview and JavaScript tests. The preview script uses pinned Wrangler 4.131.1 locally and disables dotenv/process-variable loading. It does not publish the site.

For a basic file-server preview instead:

```sh
python -m http.server 8080 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8080/. This previews HTML and interactions but does not emulate Cloudflare headers, redirects or custom 404 handling.

## How the public build works

- `public_site.py` lists all 17 public page routes and the three published JSON datasets.
- `config/static-assets.json` explicitly lists public assets. Add new required files deliberately; unlisted files are never copied.
- `config/static-site.json` sets the production origin to `https://als.carekosh.com` and production branch to `main`.
- `scripts/build_static.py` renders Flask/Jinja templates at build time, validates content and local references, then replaces the generated `dist/` directory. Visitors receive ordinary HTML, CSS, JavaScript, images and JSON.
- FAQ/assistant, communication and research consumers load `/content/faq.json`, `/content/communication-tech.json` and `/content/research-categorized.json`. These paths also work in Flask development.
- The export includes canonical links, a sitemap, robots instructions, a custom 404 and Pages headers. `--preview` and non-production Pages branches discourage indexing. They do not make a preview private.
- Legacy AI/image/rendering APIs, Python source, private source material, backups, `.env` and local environments are not published. Existing AI and research tooling remains in the repository for separate development.

The build stops for missing pages/assets, invalid data, backend references, unresolved templates, unreviewed routes or hosting-limit violations. It preserves research review dates. `dist/`, `.venv-static/` and local Wrangler state are ignored by Git.

## Tests

From the activated `.venv-static` environment:

```sh
python -m unittest discover -s tests -p 'test_*.py'
python -m unittest test_research test_research_update
node --test tests/*.test.cjs
```

The local suite contains 110 tests covering rendered pages, static export, research validation, FAQ interactions, equipment galleries, the power calculator and neuron animations. The GitHub workflow in `.github/workflows/static-site.yml` builds and runs them on pull requests and pushes to `main`. No AI integration or provider credentials are needed.

## Deploy on Cloudflare Pages

Follow the [deployment guide](docs/deployment-guide.md). Connect the existing GitHub repository to Pages using:

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Framework preset | None |
| Root directory | Repository root |
| Build command | `bash scripts/build_pages.sh` |
| Output directory | `dist` |
| Build variable | `SKIP_DEPENDENCY_INSTALL=1` |
| Python version | `.python-version` |
| Custom domain | `als.carekosh.com` |

Set the skip-install variable for production and preview environments so Pages does not install the legacy AI-heavy `requirements.txt`. An optional `SITE_URL` build variable overrides the configured origin; otherwise no domain variable or API key is required. Only `main` enables search indexing by default.

Test the assigned `pages.dev` address, then add **als.carekosh.com** under **Pages → Custom domains**. Follow the wizard to create the `als` CNAME in the `carekosh.com` zone, targeting the actual assigned Pages hostname. Keep the root domain, email records and other subdomains unchanged.

The [reusable deployment prompt](prompts/deploy_als_carekosh.md) covers further preparation and an explicitly approved launch. Source changes alone do not push, merge or deploy anything.

## Local Flask development

Flask remains useful for editing templates. With the minimal environment activated, run:

```sh
python -m flask --app app run --host 127.0.0.1 --port 5001
```

Open http://127.0.0.1:5001/. This development server is not part of the static deployment. Rebuild `dist/` to preview changes on the static server.

## Refreshing research content

Ask the project assistant to follow [`prompts/update_als_research.md`](prompts/update_als_research.md) through the intended review date. The workflow collects trial/paper leads, reviews every topic, validates a draft and applies an approved update with a backup.

To prepare a review packet:

```sh
python scripts/research_update.py prepare
```

See the [research update workflow](docs/research-update-workflow.md) for dated runs, validation, backups and limitations. Preparation does not update the page or replace evidence review. After reviewing and applying the source changes, rebuild and test the static site before committing them.

## Optional existing tooling

`requirements.txt` contains the older server-side AI/embedding dependencies. They are unnecessary for the current public website. Keep that tooling in a separate development environment if working on future integration. `requirements-optional.txt` contains Manim; the public site ships pre-rendered media and never starts rendering jobs during its build.
