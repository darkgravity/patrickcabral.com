# Patrick Cabral portfolio

An elegant, responsive static artist portfolio, designed around layered paper ornament and Cormorant Garamond typography. Starbucks Reserve is the featured project. Separate Home, Portfolio, About, and Contact pages lead to 64 dedicated project pages using 99 usable original images, with related views grouped together. The one blank image is excluded.

## Preview

Double-click `Preview.command` in Finder. It serves the actual `docs` folder, chooses an available port, and opens the website in your default browser. Keep the Terminal window open while viewing the site. Press Control+C in that window to stop it.

The launcher works regardless of the current terminal directory and does not reuse an existing server on port 8765. Use the new address it opens, not the old localhost:8765 tab.

To launch from Terminal instead:

```sh
python3 "/Users/camycabral/Desktop/patrickcabral.com/scripts/preview.py"
```

After moving the project, use the new location of `scripts/preview.py`, or double-click the launcher. To verify paths without starting a server, run `python3 scripts/preview.py --check` from the project folder.

## Publish on GitHub

1. Create a GitHub repository and upload this project, including `docs`, `src`, `scripts`, `tests`, and `.github`. Do not upload the 1.3 GB `art` folder or the generated design mockups. The `.gitignore` already excludes these when using Git.
2. Use `main` as the repository's default branch.
3. In repository **Settings → Pages**, choose **GitHub Actions** as the source.
4. Push to `main`, or run **Publish portfolio to GitHub Pages** from the Actions tab. The included workflow rebuilds the HTML, runs validation, and deploys `docs`.
5. GitHub provides the published URL. Relative links support both a user site and a repository subpath.

Alternatively, publish from the `main` branch's `/docs` folder in Pages settings; the generated site is already included.

No domain or DNS changes have been made. Add a custom domain in GitHub Pages when ready. The repository is https://github.com/darkgravity/patrickcabral.com.

## Activate the contact form

The form posts to FormSubmit for **peacabral@gmail.com**, with provider spam verification retained. GitHub Pages alone cannot send email.

After publishing, submit one test inquiry on the live site. Open the confirmation email sent by FormSubmit to `peacabral@gmail.com` and activate the endpoint. Then send another test inquiry and verify receipt, including the Reply-To address. Check spam if necessary. Until activation, email delivery is not verified. No test email was sent during development.

Visitors are taken to FormSubmit for its spam check and confirmation. A direct email link is available as an alternative. A privacy note identifies the service and links to its policy. The form uses native browser validation, a honeypot, and input length limits.

Service documentation: https://formsubmit.co/documentation
Activation help: https://formsubmit.co/help

## Edit projects and rebuild

- `src/projects.json`: titles, descriptions, categories, images, cover images, and source links. Titles marked `descriptive` are editorial labels based on the photos, not asserted formal artwork titles. Dates, dimensions, availability, client names, and material claims are omitted where unverified.
- `src/assets.json`: original filenames and the optimized web-image mapping. Keep the existing IDs stable when editing the archive.
- `src/grouping.json`: visual grouping audit and notes, before final editorial refinements. `projects.json` is the current publication source.
- `PROJECT_INVENTORY.md`: every project and its source images, including the excluded blank file.
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

Images are already prepared. To regenerate them from the original `art` directory on macOS:

```sh
python3 scripts/prepare-assets.py
python3 scripts/build.py
```

The preparation script uses macOS `sips`, preserves the original files, and produces 720-pixel thumbnails and 2000-pixel detail images. All 12 TIFF originals use PNG web copies; other images use JPEG. If adding, removing, or renaming originals, the sorted numerical IDs may shift; update the asset and project mappings together. Do not run asset preparation in GitHub Actions, which intentionally uses the included web copies.

## Design and behaviour

- Automatic theme follows the visitor's system preference. The theme button cycles Auto, Light, Dark and remembers their selection. No location access is required.
- Desktop and mobile layouts, keyboard-visible focus, reduced-motion support, and labelled controls.
- Real individual project URLs, not modal-only project content.
- Full-size image viewer with keyboard navigation, focus restoration, and close controls.
- All original artwork photos are preserved as photographs. The decorative corner ornament is a separate generated interface asset, not a portfolio work.

## Verification

Automated interaction tests and static checks cover theme behaviour, storage failure, filters, lightbox controls, image coverage, and local links. Local HTTP preview could not be started in the restricted execution environment, and the in-app browser blocks file URLs. A visual browser pass on desktop/mobile and a live email delivery test remain to be completed after opening locally or publishing. No deployment is claimed.

## Content sources

Instagram was supplied as the primary reference but could not be fetched directly. No private Instagram content was accessed. Verified project context comes from these published sources; uncertain projects use descriptive, image-based copy.

- Starbucks Reserve installation and coffee regions: https://www.adobomagazine.com/global-news/starbucks-opens-newest-reserve-store-featuring-masterpieces-by-filipino-artist-patrick-cabral/
- Starbucks material and detail: https://www.thisiscolossal.com/2019/01/animals-patrick-cabral/
- Dinagyang masks: https://www.thisiscolossal.com/2021/03/patrick-cabral-dinagyang-masks/
- Rooster, Parol, and Fudog: https://www.thisiscolossal.com/2024/08/paper-sculptures-patrick-cabral/
- Artist practice: https://plainmagazine.com/patrick-cabral-paper-cut-animals/
- GitHub Pages workflow reference: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

The Starbucks Reserve installation is layered MDF, not paper. It is separate from the 2020 Starbucks Sarimanok merchandise collection. No merchandise photos were identified in the supplied folder, so that separate collaboration is not illustrated with unrelated artwork.

All original artwork and photography remain the property of Patrick Cabral and their respective rights holders.
