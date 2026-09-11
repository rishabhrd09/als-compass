# Final deployment guide: ALS CareKosh on Cloudflare Pages

Updated 11 September 2026. This replaces the earlier recommendation to run the website on Render.

**Use GitHub for the source code, Cloudflare Pages for the generated static website, and your existing CareKosh domain on Cloudflare.** The published site needs no running Flask server, Gunicorn, database, AI provider key or Pages Function for its current features.

**Current status:** the project still uses Flask templates and JSON endpoints. Static export has not been implemented, and nothing has been pushed or deployed by this guide. Complete Step 1 before using the proposed build commands below.

## 1. Prepare the website for static hosting

The appearance and interactions can stay the same. Use Flask/Jinja during a build to generate finished HTML once; visitors then receive those HTML files directly. FAQ search, suggested answers, research filters, calculators and animations continue to run in the browser.

Ask the coding assistant to follow `prompts/deploy_als_carekosh.md`. It should create and test these files:

| Planned file | Purpose |
| --- | --- |
| `requirements-static.txt` | Minimal, pinned build dependencies. Inspect imports; Flask and python-dotenv are the current starting point. No unused AI or animation-rendering packages. |
| `.python-version` | A full, tested Python version supported by the Cloudflare build image. |
| `scripts/build_static.py` | Render an explicit list of public pages, export published JSON, copy required assets and validate the generated website. |
| `scripts/build_pages.sh` | Install only the static-build dependencies and run the exporter, stopping on any failure. |
| `dist/` | Generated deployment output. Only this folder is published; regenerate it from GitHub instead of maintaining it manually. |

The build must:

- Produce the home page and every public guide, including FAQ, research, communication, assistant and equipment pages. Preserve source references, review dates and branding.
- Replace the browser's `/api/community-faq`, `/api/communication-tech` and `/api/research-categorized` requests with generated JSON files, for example under `/content/`. Audit for any additional API requests before release.
- Keep all seven suggested answers tied to the same FAQ source data. Typed questions must still show the coming-soon message, without sending or storing their text.
- Include required images, fonts, PDFs, videos and scripts. Copy published assets through an explicit allowlist; do not copy the entire repository or all source data into the output.
- Generate a top-level `404.html`. Exclude legacy AI/image/rendering endpoints, `.env`, Python source, raw private material, local environments, caches and backups from the public output.
- Fail on missing content, broken internal links, unresolved template syntax or assets larger than the hosting limit.

A suitable generated structure is:

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

After the files in Step 1 have been implemented, use:

```sh
cd "/Users/rishabh/coding_claude_projects/als_knowledgebase_compass/als_mnd_info_compass/als-compass"
./venv/bin/python -m venv .venv-static
source .venv-static/bin/activate
bash scripts/build_pages.sh
python -m http.server 8080 --bind 127.0.0.1 --directory dist
```

The `.venv-static` environment should be excluded from Git. This server only previews files from `dist`; it does not run the Flask application. Open [the local static preview](http://localhost:8080/). Press Control+C to stop it.

Test the complete static site, including:

- Every navigation item, a direct visit to each page, and page refreshes.
- FAQ search, topic filters, seven assistant suggestions and the typed-question notice.
- Research filters, the power calculator, communication guides, image viewers and videos.
- Mobile layout, keyboard controls, PDF downloads and external source links.
- No browser requests to a Flask API or to `localhost:5001`.

Use a Pages-compatible preview as well to test platform-specific redirects, headers and 404 status; Python's file server does not emulate those Cloudflare features. Test the build again from a clean checkout so untracked local files cannot conceal a missing release asset.

## 3. Push the reviewed release to the existing GitHub repository

The configured remote is [rishabhrd09/als-compass](https://github.com/rishabhrd09/als-compass). Reuse it. At the time of review the local branch is `feature/static-faq-assistant-placeholder`, and the local default-branch reference is `origin/main`; verify these before publishing.

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
git commit -m "Prepare ALS CareKosh for static Cloudflare Pages deployment"
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

| Setting | Value for the planned static build |
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

**These settings assume Step 1 is complete.** No `build_pages.sh` or `dist/` exists yet as part of this documentation change.

The skip-install setting matters because the existing root `requirements.txt` contains unused AI dependencies. It prevents automatic installation; the build script installs only `requirements-static.txt`. Configure the same build settings for production and preview environments. Cloudflare supports Python during the build, version pinning and skipping automatic dependency installation. [Build image settings](https://developers.cloudflare.com/pages/configuration/build-image/).

Save and deploy. The first build should generate `dist` and publish it at the actual assigned `https://PROJECT.pages.dev` address. Test that address before adding your domain. It is publicly reachable unless you configure access protection.

Cloudflare supports custom static-build commands and an explicit output directory. [Static HTML deployment](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/), [build configuration](https://developers.cloudflare.com/pages/configuration/build-configuration/).

## 5. Connect the CareKosh domain you already own

Use the full domain shown in your Cloudflare account. `YOUR_DOMAIN` below is a placeholder; it does not assume you bought `.com` rather than `.in` or another suffix.

Choose one primary address:

- **`YOUR_DOMAIN`** if this is the main CareKosh website.
- **`als.YOUR_DOMAIN`** if the root domain serves another purpose or you want a separate ALS section.

Keep the name on the website as **ALS CareKosh — Caregiver’s Compass**.

In your **Pages project → Custom domains → Set up a custom domain**, enter the exact chosen hostname. Use the same Cloudflare account as the domain's DNS zone for a root-domain setup. Follow the offered DNS confirmation; Cloudflare can create the Pages CNAME automatically for a zone it manages. Wait for the domain and certificate to become active, then test HTTPS. [Pages custom-domain setup](https://developers.cloudflare.com/pages/configuration/custom-domains/).

Keep Cloudflare nameservers. Preserve email MX/TXT records and unrelated subdomains. If an existing website occupies the hostname, record its current DNS before replacing the relevant record. Do not apply the old Render CNAME or DNS-only instructions to this Pages deployment. Associate the hostname with the Pages project first instead of adding a guessed DNS record.

If you choose the root domain, configure `www.YOUR_DOMAIN` to redirect to it, preserving paths and query strings. Follow Cloudflare's [www-to-apex redirect instructions](https://developers.cloudflare.com/pages/how-to/www-redirect/), including its DNS setup. Check for an existing `www` record before adding or replacing one, and test both addresses.

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
