# Atlas of the Blessed Lands — project source

`index.html` is the finished page, the same file that is published as the Claude artifact. Open it in a browser to view it (it needs an internet connection for fonts and the d3 / topojson libraries).

## What's where
- `src/` — the page's source. Edit these, not index.html.
  - `body.html` (page text and layout), `style.css` (all styles)
  - `head.js`, `old_data.js`, `new_info.js`, `new_geom.js` — data and the texts of the notes
  - `eng_a.js` … `eng_e.js`, `start.js` — the map engine, in order
  - `caliph.json` — the outlines (made by `caliph_gen.js`), `generated.json`, `grain*.b64` (paper texture)
- `build.js` — joins everything into `index.html` (and `test.html`, a local test copy). It also adds ﷻ after the name of Allah.
- `geo2.json`, `landlo.json`, `relief_full.webp` — the prepared base map, read by build.js.
- `build_geo3.js` (and older `build_geo*.js`) — remake `geo2.json` and `landlo.json` from the Natural Earth files (`ne_10m_*.geojson`, `lakes`, `rivers`, …). Since the 2026-10-06 widening the exact settings are recorded: `npm run data:map` (`node build_geo3.js 0 6e-8 1e5 1.5e-6 3e-4 0 4e-9`) reproduces the published files. You only need this to change the base map; the included `geo2.json` and `landlo.json` are the published ones.
- `caliph_gen.js` — remakes `src/caliph.json` (outline areas and state tables). Run `node tools/make_data_mod.js` first (it builds `tools/data_mod.js`, which caliph_gen reads), then `node --stack-size=30000 caliph_gen.js` (the large stack is needed for the historical lands; on Linux/macOS run `ulimit -s unlimited` first if it crashes). It reads `admin1_used.geojson` (Natural Earth provinces for the historical lands). The Muslim-majority African countries are the `AFR` array near the top of the Greater Middle East section (country id, Pew 2020 share, optional "sources differ" flag): add or drop a country there and re-run. Checked: this reproduces the published outlines exactly. The lists near the top (`HIST`, `AFR`, `JOIN`) decide which lands are added: `HIST` = lands once ruled (ruled part only), `AFR` = Muslim-majority African countries (drawn whole), `JOIN` = lands added only to join the outline up (the rest of Italy, Corsica and the Alpes-Maritimes; Slovenia, the rest of Croatia and Hungary; Ukraine; and Russia's Southern and North Caucasus districts, whose provinces come from `admin1_used.geojson`, Natural Earth admin-1, public domain; none of these is known to have been ruled by a counted caliphate). To drop a joined land, delete its `JOIN` entry and its line in `REG`, then run `npm run data:outlines` and `node build.js`; the texts in `src/eng_e.js` (`JOIN_BODY`, the Greater Caliphate paragraphs) and `src/body.html` also name them.
- `tools/relief/make_relief.py` — remakes the shaded relief (now to 36.5°S) from `shadedrelief.jpg` (it expects to run from the folder *above* the project, with paths `dem/` and `atlas/`; adjust the paths at the top if needed). It now covers the wider sheet (30°W–104°E, 12.5°S–60°N) at 20 px per degree, quality 66.
- `tests/` — the automated checks used during development (Playwright screenshots at phone/tablet/desktop sizes, full-screen and rotation checks, accessibility scan, speed checks).
- `notes.md` — the log of verified Qur'an, tafsir and hadith texts, and what was still to verify.

## Also
- `SPEC.md` — what the atlas is: the outline specifications, standing rules and open items. Read this first in a new chat.
- `reference/` — the Greater Middle East reference map you supplied.

## Rebuild
```
npm install                     # d3, topojson, polygon-clipping, …
npm install esbuild             # optional: minifies the output (the published page is minified)
node build.js                   # writes index.html and test.html
node build.js --nomin           # same, without minifying
```
Tests also need Playwright and Chromium (`npm install playwright`, `npx playwright install chromium`), and `test-fonts.css` with local fonts for offline runs. The test scripts were written for the Linux workspace they ran in, so paths such as `/opt/pw-browsers/chromium` may need changing.

## Sources of the data
Natural Earth (public domain) for borders, coasts, lakes, rivers and shaded relief. Texts: quran.com via quran.ai (Saheeh International, al-Baghawī, al-Ṭabarī, Ibn Kathīr), sunnah.com, dorar.net, and the classical geographers cited on the page.

## Complete Caliphate V2 history data
- `v2_history.json` holds the province-by-province history of the 13 lands V2 adds (category, rulers, dates, notes, uncertainty, sources). It is made by `python3 tools/make_v2_history.py research/v2` (the raw research files are kept in `research/v2/`); the `ADJ` list in that script records Claude's own changes to the researchers' calls. `caliph_gen.js` reads it (it needs those countries' provinces in `admin1_used.geojson`) and writes `CALIPH.v2` into `src/caliph.json`.
- `build.js` adds ﷻ after Allah everywhere except inside a person's name such as ʿAbd Allāh.

## Natural borders data
- `src/nat.json` (the natural ring: its territory as lines by kind, the states inside it, and the internal lines). Made by `node --stack-size=30000 tools/nat_gen.js` (about a minute) from `geo2.json`, `rivers.geojson` and the two Natural Earth extracts in `tools/data/` (the Kupa from rivers_europe, the historic Aral from lakes_historic). `NAT_DEBUG=<dir>` writes the territory, the loop and the ring segments for checking.
