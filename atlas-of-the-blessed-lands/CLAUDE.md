# Atlas of the Blessed Lands — instructions for Claude Code

This is Nawaz's project: an interactive map ("Atlas of the Blessed Lands"). Pick it up where it was left off.

## Start of every new session
1. Read `notes.md` first (full history, version by version; latest is Version 53: all of Algeria, Morocco (without Western Sahara), Spain, Portugal, Uzbekistan, Tajikistan, Sicily with its islands and Malta in Complete (Version 52: ʿUthmān map; 51: Cyprus, Derbent, Arwad)).
2. Then `SPEC.md` (what the atlas is, standing rules; it is behind, it stops around Version 34 — `notes.md` is more current) and `README.md` (how it is built).
3. Run `npm install` once, then `node build.js` to make `index.html`. Edit files in `src/`, never `index.html`.

## How Nawaz likes to work
- He is a complete beginner (Windows 11, PowerShell). Use plain language. Go ONE step at a time and wait for his confirmation (a screenshot is best) before the next step.
- Push back honestly if a request is contradictory or unclear. Do not just agree.
- Keep what the classical sources say clearly separate from your own reasoning or general knowledge. Label every claim: Qur'an / hadith / early scholars / classical geographers / modern borders / Claude's synthesis / Nawaz's specification. Say plainly when something is unverified; do not present inference as established scholarly consensus.
- Always write "Allah ﷻ" with the honorific (build.js adds ﷻ automatically after the name, except inside names such as ʿAbd Allāh).

## Standing rules for the content
- Qur'an, translation and tafsir only from quran.ai (Saheeh International; al-Baghawī, al-Ṭabarī on 5:21, Ibn Kathīr on 24:55). If the quran.ai connector is not set up, do not quote verses from memory — say so and ask Nawaz to connect it (`claude mcp add --transport http quran_ai https://mcp.quran.ai`).
- Hadith only with collection, number and grading (sunnah.com, dorar.net). Leave out anything not verified; `notes.md` lists what was verified and what was not.
- The outlines are a thought experiment / Nawaz's specification, not from the sources and not a ruling. Say so wherever it matters.

## After EVERY change
1. `node build.js`
2. Check it with a screenshot at desktop size AND phone size (scripts in `tests/`, e.g. `tests/shot2.js`, `tests/smoke.js`; they were written for Linux, paths like `/opt/pw-browsers/chromium` may need changing on Windows).
3. Add a short entry to `notes.md` (what was asked, what was done, what is unverified).
4. Publish `index.html` and give Nawaz a new zip of the project (without `node_modules`).

## Publishing
- The published page is the Claude artifact https://claude.ai/artifact/LUPQgg2w4dGSFdLcmR1a4F . Republish to that SAME link. NEVER create a new artifact.
- If this Claude Code session cannot publish to that artifact (no Artifact tool), do not invent another way. Tell Nawaz, hand him the rebuilt `index.html` and zip, and let him republish from his claude.ai chat.

## Open items waiting on Nawaz
Nigeria / Guinea-Bissau inclusion; southern Sardinia 1015–16; Sokoto width; Bosphorus gap; unchecked weak V2 calls; approximate African card region names; relief image not re-encoded; Amānī vs Amīnī; whether natural/internal lines should be on by default in every version. Version 45 (Maximum): Caspian-basin provinces chosen by a "about a third or more drains to the Caspian" rule (no drainage data was reachable); not checked against the natural ring. Version 46/47: Turkmenistan kept whole in Complete (Nawaz's choice), so ~17,500 km² of it lies outside the natural ring. Version 51: Derbent/Arwad dates come from Nawaz's brief (modern Arabic works), not checked; Derbent + Samur strip (16,783 km²) is outside the natural ring. Version 52: Algeria/Morocco north, Spain's SE coast, eastern Sicily, Dagestan coast and an Uzbek strip added from Nawaz's ʿUthmān map (traced approximately; mostly raids in standard histories, which the page says); ~72,000 km² of Complete now outside the natural ring. Version 53: Western Sahara left out of 'entire Morocco' (base map draws Morocco de facto with it) — ask Nawaz; Natural + political now takes Spain, Portugal, Uzbekistan, Tajikistan, Malta whole by its rule; ~1.24 million km² of Complete outside the natural ring. Offered: splitting the startup into steps so the map appears sooner on slow phones (engine restructuring).
