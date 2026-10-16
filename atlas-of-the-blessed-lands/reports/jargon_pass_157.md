Plain-words pass on the page text (part of Version 158)

Asked by the author: "remove the jargon if it has any". Only text the reader sees was changed.
No map data (src/caliph.json), no tools/ scripts, no geometry were touched.

WHAT WAS REPLACED (counts are of reader-visible strings, before -> after)

1. Internal version numbers in reader paragraphs ("Version 154", "Versions 96-105",
   "since Version 139", "before Version 66", "as in Version 150" ...): 162 -> 0.
   The buttons V1, V2, V2-B, V4, V5, V6 stay. The old names "Complete", "V1 before
   Version 66", "V2N" were dropped from running text (one plain sentence in the
   versions paragraph still says V2N was merged into V2).
2. Build-history narration in V2's long note (src/eng_e.js, the "full" note, about
   52,000 characters of change-by-change history): rewritten as about 24,000
   characters organised by topic (gaps, Central Asia's edges, Greater Turkey,
   Balkans, Caucasus, Caspian shore, Nile and Lake Albert, Comoros, "everything in",
   Ustyurt pocket, Manqishlaq and Ustyurt, Greater Khurasan, Kashgar, India border,
   towns on the line, frontier posts, how big Khurasan was). Kept: what each land is,
   why it is in or out, all areas and counts that still describe the outline, every
   quotation of the author, every source citation and caveat.
3. "my method" (13): removed or replaced by a plain description ("found by closing the
   outline by about 50 km", "fitted to three points ...").
4. "sliver(s)" meaning a thin uncovered strip (14): "hairline strips" or "thin strip".
5. "over five/six/seven passes" and "after the last pass none is cut" (10): dropped;
   the count of settlements and buildings is kept.
6. "grid estimates" -> "estimates from a map of where people live"; "stored on a grid
   of a thousandth of a degree" -> "stored to a thousandth of a degree".
7. File and tool names shown to the reader: "reports/settlements_on_the_line.md" ->
   "the project's report on settlements on the line"; quran.ai tool names
   (fetch_quran, fetch_translation, fetch_tafsir, fetch_word_concordance and edition
   ids like ar-baghawi) -> "the Qur'an text, the translation (Saheeh International),
   the tafsir (al-Baghawi; al-Tabari ...; Ibn Kathir ...) and a word-root search".
8. Map-making words: "schematic" (6) -> "rough sketch" / "simplified" / "roughly";
   "interpolated" (2) -> "estimated"; "waypoints" -> "series of points"; "stipple" ->
   "dots"; "1:10m" (2) -> "1:10 million scale"; "polygon" in the Najd note -> "closed
   area with fixed edges"; "overlays" -> "extra lines"; "de facto lines" now glossed
   ("as they stand in practice (de facto)"); OpenStreetMap "relation 4016746" ->
   "item 4016746".
9. V6 province notes (data in src/caliph.json, not edited): internal category names
   such as islamic_state_ruled, caliphate_ruled, via_dynasty, 'temporary', 'influence',
   and the words "admin-1" and "polygon" are turned into the key's own names at display
   time (small function PLAIN_V2 in src/eng_e.js). 23 text fields change on screen.
10. Search-box text and button tooltips: "as it was before Version 107" -> "as it was
   before the Balkan Peninsula was added".

DELIBERATELY NOT CHANGED

- km2, "outline", "Natural line", "Internal lines": the author said they stay.
- Arabic and Islamic terms (Dar al-Islam, thughur, ribat, miqat, Haram, hadith grades,
  khutbah ...): the subject of the atlas; glosses already present were kept.
- First-person voice ("my rough measurement", "my reading", "I checked"): the page's
  existing way of labelling its own work as separate from the sources (CLAUDE.md rule);
  only the label "(my method)" was removed.
- Quotes of the author and of sources, all citations, all dates, all numbers that still
  describe the outline.
- "Tier 1-4" (reading levels), "disc(s)", "hatching", "graticule/grid" (the latitude and
  longitude lines): plain enough for a map reader and used throughout the key.
- "buffer zone", "union", "de facto" in political sentences: ordinary political words
  (de facto is now glossed).
- Comments inside the code (/* Version 120: ... */, tools/..., XV, CALIPH.x): not shown
  to readers.
- src/caliph.json: the metadata keys with "Version 43 ..." and the word "sliver" in
  "slivers: filled 213" are not displayed; left alone.

THINGS TO KNOW

- Some paragraphs that described superseded intermediate lines (Version 124-131 straight
  Caucasus line, district borders, Kazakh border lines, Version 135/136 wider Khurasan) are
  now a single plain sentence each ("Several earlier Caucasus lines ... were each replaced
  by the lines above"; "Before this choice the Central Asian edge went through several
  wider and narrower stages ...") because the later paragraphs replace them.
- Two statements that were already out of date in the old text were kept as written
  but now carry a pointer: the "Left out (about 2.4 million km2): ... Aktau and the
  Mangystau coast" figure (those lands were added again afterwards).
- tests: v3rm/v2bpanel.js prints "Balkan para: false" because it looks for the old
  heading "The Balkan Peninsula (Version 107)"; the paragraph is on the page under
  "The Balkan Peninsula, at the author's request" (checked separately: present in V2,
  absent in V2-B, as before). Its error list is empty.
