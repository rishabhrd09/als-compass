# Final deployment guide: ALS CareKosh on Cloudflare Pages

Updated 11 September 2026. This replaces the earlier recommendation to run the website on Render.

**Use GitHub for the source code, Cloudflare Pages for the generated static website, and your existing CareKosh domain on Cloudflare.** The published site needs no running Flask server, Gunicorn, database, AI provider key or Pages Function for its current features.

**Current status:** the static exporter is implemented on `prepare-static-deployment`, created from your merged `main`. The generated site runs without Flask. The production address is configured as **https://als.carekosh.com**. Commit, push, merge and the actual Cloudflare deployment are still separate launch steps.

## 1. What the static build does

The appearance and interactions can stay the same. Use Flask/Jinja during a build to generate finished HTML once; visitors then receive those HTML files directly. FAQ search, suggested answers, research filters, calculators and animations continue to run in the browser.

The following files now implement the build. The reusable `prompts/deploy_als_carekosh.md` describes how to maintain and validate this setup:

| File | Purpose |
| --- | --- |
| `requirements-static.txt` | Eight pinned packages for HTML/JSON builds, with no AI or animation-rendering dependencies. |
| `.python-version` | Python 3.11.15, tested in the isolated build environment. |
| `scripts/build_static.py` | Render an explicit list of public pages, export published JSON, copy required assets and validate the generated website. |
| `scripts/build_pages.sh` | Install only the static-build dependencies and run the exporter, stopping on any failure. |
| `dist/` | Generated deployment output. Only this folder is published; regenerate it from GitHub instead of maintaining it manually. |

The implemented build:

- Produces the home page and every public guide, including FAQ, research, communication, assistant and equipment pages. Preserve source references, review dates and branding.
- Uses `/content/faq.json`, `/content/communication-tech.json` and `/content/research-categorized.json` in every frontend consumer. Flask serves the same URLs during local development. Legacy APIs are not exported.
- Keeps all seven suggested answers tied to the same FAQ source data. Typed questions must still show the coming-soon message, without sending or storing their text.
- Copies 176 required assets from `config/static-assets.json`, including fonts, license notices, photos, scripts and pre-rendered media. New assets require an explicit manifest entry. Current PDF links point to external sources; print-to-PDF remains a browser feature.
- Generates a top-level `404.html`. Excludes legacy AI/image/rendering endpoints, `.env`, Python source, raw private material, local environments, caches and backups from the public output.
- Fails on missing content, broken internal links, unresolved template syntax or assets larger than the hosting limit.

The generated structure is:

```text
dist/
  index.html
  404.html
  faq/index.html
  ai-assistant/index.html
  research-updates/index.html
  communication-technology/index.html
  home-icu-guide/index.html
  ...remaining public pages...
  content/
    faq.json
    communication-tech.json
    research-categorized.json
  static/
    css/
    js/
    fonts/
    images/
    videos/
```

Directory pages support direct visits and refreshes. Preserve existing links with suitable redirects or consistent URL generation. Cloudflare documents its URL matching and custom `404.html` behaviour in [Serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/).

**Do not upload the raw `templates/` folder or select `static/` as the whole website.** Neither currently contains a complete, standalone site.

## 2. Build and check it on your Mac

Run these commands in your existing Mac checkout:

```sh
cd "/Users/rishabh/coding_claude_projects/als_knowledgebase_compass/als_mnd_info_compass/als-compass"
./venv/bin/python -m venv .venv-static
source .venv-static/bin/activate
bash scripts/build_pages.sh --preview
python -m http.server 8080 --bind 127.0.0.1 --directory dist
```

The `.venv-static` environment should be excluded from Git. This server only previews files from `dist`; it does not run the Flask application. Open [the local static preview](http://localhost:8080/). Press Control+C to stop it.

Test the complete static site, including:

- Every navigation item, a direct visit to each page, and page refreshes.
- FAQ search, topic filters, seven assistant suggestions and the typed-question notice.
- Research filters, the power calculator, communication guides, image viewers and videos.
- Mobile layout, keyboard controls, PDF downloads and external source links.
- No browser requests to a Flask API or to `localhost:5001`.

For a Cloudflare-compatible preview (Node.js/npm required), stop the Python file server with Control+C and run:

```sh
bash scripts/preview_pages.sh
```

Open http://127.0.0.1:8788/. This uses pinned Wrangler 4.131.1 locally, without publishing or loading your `.env` AI configuration. It tests the same directory routing, custom 404 and `_headers` behaviour used by Pages. The preview script does not rebuild: rerun the build and refresh after source edits.

Run the release checks in the activated `.venv-static` environment:

```sh
python -m unittest discover -s tests -p 'test_*.py'
python -m unittest test_research test_research_update
node --test tests/*.test.cjs
```

The 110 automated tests pass locally, including export validation, deterministic rebuilds, missing-file failures, seven FAQ suggestions and the existing research checks. `.github/workflows/static-site.yml` runs this build and test sequence on pull requests and pushes to `main`; its first GitHub run occurs after you push it.

The route/data manifest is `public_site.py`. The exporter checks that all 17 public page routes are accounted for and exports only three reviewed JSON datasets. It validates staging output before replacing a recognized generated `dist/`. Changes to medical text or review dates belong in the source-review workflow, not the build.

## 3. Push the reviewed release to the existing GitHub repository

The configured remote is [rishabhrd09/als-compass](https://github.com/rishabhrd09/als-compass). Reuse it. The deployment work is on `prepare-static-deployment`, based on the already-merged `main`. Verify the current branch before publishing.

Start with:

```sh
cd "/Users/rishabh/coding_claude_projects/als_knowledgebase_compass/als_mnd_info_compass/als-compass"
git status --short
git branch --show-current
git remote -v
git diff --stat
```

Review and stage the complete release, including new images, data, tests and build files. `git add -p` stages selected changes to tracked files; add reviewed new files explicitly. Do not blindly upload all local material. Keep the repository's intended visibility and check its history for previously committed secrets. A private repository still produces a public website when deployed.

After staging the reviewed files:

```sh
git diff --cached --stat
git diff --cached --check
git diff --cached
git commit -m "Prepare static deployment"
git push -u origin HEAD
```

Open a pull request into the verified default branch, review the changes and checks, then merge the release into `main`. Do not force-push or discard other work. The reusable prompt includes assembling the release files and running the project tests.

GitHub's [existing-code publishing guide](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github) covers authentication and handling an existing repository.

## 4. Connect GitHub to Cloudflare Pages

In the Cloudflare account that holds your domain:

1. Open **Workers & Pages → Create application → Pages**.
2. Choose **Import an existing Git repository / Connect to Git**. Use the Pages flow, not a Worker or manual upload project.
3. Connect GitHub and grant access to the existing `als-compass` repository.
4. Select that repository and enter the settings below.

| Setting | Value |
| --- | --- |
| Project name | `als-carekosh`, if available |
| Production branch | `main`, after the reviewed release is merged |
| Framework preset | `None` |
| Root directory | Repository root; leave blank unless the repository structure changes |
| Build command | `bash scripts/build_pages.sh` |
| Build output directory | `dist` |
| Build variable | `SKIP_DEPENDENCY_INSTALL=1` |
| Python version | Commit the tested version in `.python-version` |
| API keys / server start command | None |

The production address defaults to `https://als.carekosh.com` in `config/static-site.json`. No `SITE_URL` override is required. An optional HTTPS `SITE_URL` build variable can override it later. Feature-branch Pages builds automatically receive noindex metadata and headers; `main` builds enable indexing. Preview indexing controls do not make a URL private.

The skip-install setting matters because the existing root `requirements.txt` contains unused AI dependencies. It prevents automatic installation; the build script installs only `requirements-static.txt`. Configure the same build settings for production and preview environments. Cloudflare supports Python during the build, version pinning and skipping automatic dependency installation. [Build image settings](https://developers.cloudflare.com/pages/configuration/build-image/).

Save and deploy. The first build should generate `dist` and publish it at the actual assigned `https://PROJECT.pages.dev` address. Test that address before adding your domain. It is publicly reachable unless you configure access protection.

Cloudflare supports custom static-build commands and an explicit output directory. [Static HTML deployment](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/), [build configuration](https://developers.cloudflare.com/pages/configuration/build-configuration/).

## 5. Connect the CareKosh domain you already own

Use **als.carekosh.com** as the primary address. This keeps the main `carekosh.com` domain available for a wider CareKosh website and requires no additional domain purchase.

1. Open the deployed **Pages project → Custom domains → Set up a custom domain**.
2. Enter **als.carekosh.com**.
3. Follow Cloudflare’s DNS confirmation. In the `carekosh.com` DNS zone, the relevant record is a **CNAME named `als`** pointing to the **actual assigned Pages hostname**, for example `als-carekosh.pages.dev` only if that is the hostname Cloudflare assigned. Let the Pages wizard create it when offered. Do not guess the target or add a duplicate record.
4. Wait until the custom domain and HTTPS certificate are active.
5. Test **https://als.carekosh.com**, including deep links, JSON and the assistant.

Associate the hostname through Pages first; adding a CNAME alone is insufficient. Keep Cloudflare nameservers, the root domain’s existing website, email MX/TXT records and unrelated subdomains. If an `als` record already exists, record its current value and replace only that record when ready. [Pages custom-domain setup](https://developers.cloudflare.com/pages/configuration/custom-domains/).

The website name remains **ALS CareKosh — Caregiver’s Compass**. A `www` hostname or root-domain redirect is not needed for this subdomain setup. The generated sitemap and canonical links already use `https://als.carekosh.com`; verify them on the deployed site.

No domain transfer or additional domain purchase is needed. Your existing domain renewal remains separate from hosting.

## 6. Cost and limits

Start with **Cloudflare Pages Free** for this static release. Static asset requests that do not invoke Functions are free and unlimited under the current pricing. No paid Flask host or AI API subscription is required for this deployment. [Static asset pricing](https://developers.cloudflare.com/pages/functions/pricing/).

Current Free-plan limits include **500 builds per month**, **20,000 files per site** and **25 MiB per individual asset**. Check all generated assets, including new videos and images, before publishing. If a file is too large, optimize it or separately plan media storage such as R2; that is not part of this initial setup. [Pages limits](https://developers.cloudflare.com/pages/platform/limits/).

Vercel or ordinary static web hosting can also serve a generated HTML/CSS/JavaScript site. The earlier Hostinger VPS requirement applied to running the Python application. For this release, keeping the domain and static hosting together on Cloudflare is the recommended route.

## 7. Final launch checks

Before sharing the domain, confirm:

- The deployed commit matches the reviewed GitHub release.
- HTTPS works at the chosen address, and alternate-host redirects behave correctly.
- All current pages and tools pass the static-site checks from Step 2.
- Unknown URLs show the proper 404 page rather than returning the home page.
- Only intended public HTML, JSON and media are in the deployment output.
- The assistant stays in FAQ mode with its three preview-only model names.
- Canonical URLs and sitemap use the actual domain; research review dates remain unchanged by a rebuild.

Use Pages' normal caching initially. Broad custom cache rules can cause outdated content after a deployment. [Pages caching guidance](https://developers.cloudflare.com/pages/configuration/serving-pages/).

## 8. Update the website and roll back

Edit source content locally, run the static build and tests, push a branch, review its preview and merge to the production branch. Git-connected Pages automatically builds and deploys updates, with separate branch previews. [Pages Git integration](https://developers.cloudflare.com/pages/configuration/git-integration/).

For research updates, keep using the existing source-review workflow. Commit the reviewed JSON, then let the same build produce the updated page. Do not manually maintain a second copy of the FAQ or change “last updated” merely because a deployment ran.

If a release breaks, open **Pages project → Deployments**, locate a successful previous **production** deployment and choose **Rollback to this deployment**. Then fix the source on a branch. Preview deployments are not rollback targets. [Pages rollback instructions](https://developers.cloudflare.com/pages/configuration/rollbacks/).

A future AI integration can use a separate secure API. It does not need to change the static hosting plan for the rest of the website.
