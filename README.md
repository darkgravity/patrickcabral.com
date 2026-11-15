# Patrick Cabral portfolio

**[Open the website](https://darkgravity.github.io/patrickcabral.com/)** · [Works](https://darkgravity.github.io/patrickcabral.com/portfolio/index.html) · [Lab](https://darkgravity.github.io/patrickcabral.com/lab/index.html) · [Deployment status](https://github.com/darkgravity/patrickcabral.com/actions/workflows/pages.yml)

An elegant, responsive static artist portfolio, designed around layered paper ornament and Cormorant Garamond typography. Starbucks Reserve is the featured project. The current source has Home, Works, Lab, About, and Contact pages plus 72 active project pages and 3 archived lettering pages retained at their existing URLs. Works contains 50 sculpture projects; Lab contains 22 digital experiments. The media archive contains 130 usable images: 99 from the original artwork set, 26 Techsugi additions comprising 15 stills and 11 film poster frames, one Galleon still for Modern Patterns Version 2, and four Our Lady of Manaoag photographs. Eleven films accompany the digital studies. The one blank original image is excluded.

The source includes the sculpture and technology focus, artist-supplied Lab descriptions, Instagram caption corrections, media expansion, and image-loading optimizations. The website links above open the latest successful GitHub Pages deployment; check Deployment status to confirm which commit is live. Preview the current `docs` folder locally to review source changes before deployment.

## Preview

Double-click `Preview.command` in Finder. It serves the actual `docs` folder, chooses an available port, and opens the website in your default browser. Keep the Terminal window open while viewing the site. Press Control+C in that window to stop it.

The launcher works regardless of the current terminal directory and does not reuse an existing server on port 8765. Use the new address it opens, not the old localhost:8765 tab.

To launch from Terminal instead:

```sh
python3 scripts/preview.py
```

After moving the project, use the new location of `scripts/preview.py`, or double-click the launcher. To verify paths without starting a server, run `python3 scripts/preview.py --check` from the project folder.

## Publish on GitHub

The repository and GitHub Pages workflow are configured. Deployment status identifies the latest workflow result and deployed commit.

To publish an update, sync `docs`, `src`, `scripts`, `tests`, and `.github`, then push to `main` or run **Publish portfolio to GitHub Pages** from the Actions tab. The workflow rebuilds HTML, validates the portfolio, and deploys `docs`. Include only optimized media under `docs/assets`; do not upload the full raw `art` or `techsugi` folders, generated mockups, or preparation intermediates. Relative links support both a user site and a repository subpath.

Alternatively, publish from the `main` branch's `/docs` folder in Pages settings; the generated site is already included.

No domain or DNS changes have been made. Add a custom domain in GitHub Pages when ready. The repository is https://github.com/darkgravity/patrickcabral.com.

## Activate the contact form

The form posts to FormSubmit for **peacabral@gmail.com**, with provider spam verification retained. GitHub Pages alone cannot send email.

After publishing, submit one test inquiry on the live site. Open the confirmation email sent by FormSubmit to `peacabral@gmail.com` and activate the endpoint. Then send another test inquiry and verify receipt, including the Reply-To address. Check spam if necessary. Until activation, email delivery is not verified. No test email was sent during development.

Visitors are taken to FormSubmit for its spam check and confirmation. A direct email link is available as an alternative. A privacy note identifies the service and links to its policy. The form uses native browser validation, a honeypot, and input length limits.

Service documentation: https://formsubmit.co/documentation
Activation help: https://formsubmit.co/help

## Edit projects and rebuild

- `src/projects.json`: titles, descriptions, categories, image galleries, cover images, optional film entries, `study_sections` for developments such as Modern Patterns Version 2, verified metadata, and source links. `archived: true` retains a project’s existing page and assets while excluding it from the main collections and adjacent-project navigation. Titles marked `descriptive` are editorial labels based on the photos, not asserted formal artwork titles. Artist-supplied titles replace earlier provisional names while retaining each project’s existing URL; `content_source` distinguishes those notes from published source links. Dates, dimensions, availability, client names, and material claims are omitted where unverified.
- `src/assets.json`: original filenames and the optimized web-image mapping, with `thumb`, `display`, and `full` derivatives for each image. IDs 0–99 retain the original artwork mapping; IDs 100–125 are appended Techsugi stills and poster frames; ID 126 is the artist-supplied `Galleon/art.png` still; IDs 127–130 are the four artist-supplied Manaoag photographs. Derivatives do not count as additional artwork assets. Keep IDs and list positions stable.
- `src/grouping.json`: visual grouping audit and notes, before final editorial refinements. `projects.json` is the current publication source.
- `PROJECT_INVENTORY.md`: a manifest-derived inventory of every project, source image, poster frame, and film, including the excluded blank file.
- `src/about.html` and `src/contact.html`: dedicated inner-page content.
- `src/styles.css`: layout, colours, typography, and responsive rules.
- `src/app.js`: theme switching, project search, category filters, mobile menu, image viewer, and inquiry context.
- `scripts/build.py`: generates the homepage, archive, and individual HTML project pages.

```sh
python3 scripts/build.py
node tests/app.test.cjs
python3 tests/validate_site.py
```

The site requires no npm installation, framework, database, or runtime server. Only Python's standard library is used to build. All images and page content are static. All page links explicitly include index.html so the portfolio and project pages also open when browsing files locally. Google Fonts supplies Cormorant Garamond and Manrope; local serif and sans-serif fallbacks are included.

### Media preparation

Use the included optimized web copies for ordinary builds. `scripts/prepare-assets.py` processes only the original `art` directory, using macOS `sips` to create 720-pixel JPEG thumbnails and 2000-pixel detail images. All 12 TIFF originals retain full PNG web copies; other original images use JPEG. Their earlier PNG thumbnails are retained, but pages now use separate JPEG thumbnails.

`scripts/prepare-previews.py` refreshes lightweight derivatives across the complete asset manifest, using existing web copies rather than modifying original source files. It creates JPEG display previews with a maximum dimension of 1,400 pixels at quality 82 and converts PNG thumbnail references to separate JPEG copies. `scripts/prepare-assets.py` invokes it after refreshing the original set. Run `python3 scripts/prepare-previews.py` when only these previews need refreshing, then rebuild the site.

Cards and project galleries request thumbnails only, with no full-image candidate in `srcset`. Larger page images use responsive thumbnail and display-preview candidates. Full images remain available through `data-full` and load when the image viewer is opened. This prevents high-density screens from selecting full-size files for small previews while preserving detailed viewing.

The preparation script preserves appended media IDs and source provenance when refreshing the original images. It stops if the original filenames or ordering have changed, preventing silent reassignment of project images. Adding or renaming originals requires an explicit update to the stable ID mapping. GitHub Actions uses the included web copies and must not run asset preparation.

Techsugi media comes from the user-supplied local `techsugi` archive. Appended assets carry `source_type: "techsugi"` and a relative original source path. Selected stills are optimized as JPEG galleries; poster frames retain the path of the original film as provenance. Project `videos` entries map the optimized MP4, poster image, and display title. The inventory lists these mappings. Modern Patterns Version 2 adds a still from `Galleon/art.png`, recorded with `source_type: "user-supplied"` and displayed in a dedicated study section. Topographical Beads was matched to the existing original asset at ID 22, so no duplicate image was added. No Instagram image download is included in this update.

Our Lady of Manaoag uses four photographs from the artist-supplied Google Drive folder `art/Manaoag`, with `source_type: "user-supplied"`. Separate JPEG copies under `docs/assets/manaoag` have a maximum dimension of 2,000 pixels for full images and 720 pixels for thumbnails, at quality 85. The original PNG files remain unchanged. The full composition is the cover, followed by three detail views.

The 11 films total 76.26 MB and use H.264 video with AAC audio. They are optimized for browser playback and stored under `docs/assets/techsugi`. Native playback controls, `playsinline`, and `preload="none"` keep films idle until a visitor chooses to play them. Video posters use thumbnail copies. Keep original films and image sequences in the raw archive, outside the published files.

## Design and behaviour

- Automatic theme follows the visitor's system preference. The theme button cycles Auto, Light, Dark and remembers their selection. No location access is required.
- Desktop and mobile layouts, keyboard-visible focus, reduced-motion support, and labelled controls.
- Paper sculpture and technology lead the homepage and artist introduction, with four featured tech projects and direct links to Works and Lab.
- Our Lady of Manaoag appears as the second card in Selected sculptures, in the first row. It replaces Bee in the homepage selection; Bee remains available in Works.
- Project cards use a thin right-pointing SVG arrow; the “View project” label and media-view counts are removed.
- Small previews load thumbnails only; larger page views use lightweight responsive display images, with full images reserved for zoom. Images below the main content remain lazy-loaded.
- Lab copy presents the work as code-driven experiments in craft, culture, and organic systems, rather than AI-generated imagery.
- Real individual project URLs, with breadcrumbs and adjacent-project navigation kept within active Works or Lab. Older lettering pages are archived and absent from the main portfolio.
- Full-size image viewer with keyboard navigation, focus restoration, and close controls.
- Techsugi film sections with poster images and user-controlled playback; no autoplay or full-video preloading.
- All original artwork photos are preserved as photographs. The decorative corner ornament is a separate generated interface asset, not a portfolio work.

## Verification

Automated interaction tests and static checks cover theme behaviour, storage failure, filters, lightbox controls, image coverage, Works/Lab membership, local links, media paths, and video playback settings. The current inventory contains 75 project routes, 130 uniquely assigned images, and 81 HTML pages. Run the checks above after changes to verify rendered pages, media assignments, and local references. All 11 optimized films passed decoded-frame and aspect-ratio checks. Deployment success is recorded separately in GitHub Actions and does not replace these content checks. Browser security blocked access to local-file pages, so a visual browser pass on desktop/mobile remains unverified. A live email delivery test also remains to be completed.

## Content sources

Patrick’s project notes supplied on November 14, 2026 are the primary reference for the updated Lab titles and descriptions: Philippine Weave AR, Modern Patterns and Version 2, Textile Physics, Grown, Kalinga Tattoo Patterns, Philippine Basketry, Topographical Beads, and Cypher. The copy identifies these as code-driven visual experiments and keeps the Baybayin version of Cypher explicitly in development. Supplied media references were matched to local assets; private Gmail attachment URLs are not embedded in the website.

Instagram captions were read through Patrick’s signed-in Chrome session using read-only browsing. They support existing sculpture descriptions and technical context for footwear, panels, armour, and Quantum Dance, now presented within Textile Physics. The Our Lady of Peñafrancia identity was confirmed by Patrick, and its story was cross-checked against his caption about Sweet, Joseph, and Ina. Exact public post links remain with each project in `src/projects.json`; `content_source` records artist-supplied notes separately. Unverified titles remain marked `descriptive`. Our Lady of Manaoag is identified from the artist-supplied project folder, with its description based on the four photographs. Media comes from the original artwork set and local Techsugi, Galleon, and Manaoag files, not Instagram downloads.

Additional published references:

- Starbucks Reserve installation and coffee regions: https://www.adobomagazine.com/global-news/starbucks-opens-newest-reserve-store-featuring-masterpieces-by-filipino-artist-patrick-cabral/
- Starbucks material and detail: https://www.thisiscolossal.com/2019/01/animals-patrick-cabral/
- Dinagyang masks: https://www.thisiscolossal.com/2021/03/patrick-cabral-dinagyang-masks/
- Rooster, Parol, and Fudog: https://www.thisiscolossal.com/2024/08/paper-sculptures-patrick-cabral/
- Artist practice: https://plainmagazine.com/patrick-cabral-paper-cut-animals/
- GitHub Pages workflow reference: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

The Starbucks Reserve installation is layered MDF, not paper. It is separate from the 2020 Starbucks Sarimanok merchandise collection. No merchandise photos were identified in the supplied folder, so that separate collaboration is not illustrated with unrelated artwork.

All original artwork and photography remain the property of Patrick Cabral and their respective rights holders.
