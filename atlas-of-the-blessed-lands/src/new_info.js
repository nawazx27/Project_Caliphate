/* ================= v4: new info texts ================= */
const sn = (c, n, t) => `<a href="https://sunnah.com/${c}:${n}" target="_blank" rel="noopener">${t || (c + " " + n)}</a>`;
const LVL = {
  rev:{label:"Qur'an or authentic Sunnah", ring:"solid"},
  salaf:{label:"Understanding of the Salaf", ring:"dashed"},
  later:{label:"Later scholars", ring:"dotted"},
  disp:{label:"Disputed", ring:"dotted"}
};
const KIND = {
  haram:{label:"Ḥaram", sub:"sanctuary with its own rulings", col:"--st-haram", layer:"st-haram"},
  muq:{label:"Muqaddas", sub:"called holy", col:"--st-muq", layer:"st-muq"},
  mub:{label:"Mubārak", sub:"called blessed, or prayed over for blessing", col:"--st-mub", layer:"st-mub"},
  fad:{label:"Faḍīla", sub:"a stated virtue", col:"--st-fad", layer:"st-fad"},
  link:{label:"Link", sub:"mīqāt, Isrāʾ, qibla, routes", col:"--miqat", layer:"st-link"},
  none:{label:"None established", sub:"no sacred status for the land", col:"--st-none", layer:"st-none"}
};

const INFO_NEW = {
  intro:{title:"How to use this map", src:[], cert:null, body:`
    <p>Drag to move; pinch or scroll to zoom. Tap any shaded region, line, marker or number to read where it comes from and how sure we can be of it.</p>
    <p><b>Numbered discs</b> are sacred-status entries; the table under the map explains each one. The disc's colour says whether the sources call the place a ḥaram, muqaddas or mubārak, or give it a faḍīla; its outline says what the claim rests on. <b>Lettered circles</b> are places a source names as the limit of a region.</p>
    <p><b>Who drew it</b> shows one kind of source at a time: revelation, the early scholars, the geographers or today's borders. Compare them to see that no land's edge comes from revelation.</p>
    <p>The <b>View</b> buttons switch between the overview, lands and boundaries, sacred status and the roads. <b>Find a place</b> works without diacritics, so "aqsa" or "makkah" is enough. Every note has a link you can copy and share.</p>`},
  status:{title:"Reading the numbered discs", src:[], cert:null, body:`
    <p>Each disc is one row of the sacred-status table. <b>Colour</b> is the kind of status: red for ḥaram, violet for muqaddas, teal for mubārak, gold for faḍīla, plum for a link (mīqāt, Isrāʾ, qibla, route) and grey where no sacred status is established.</p>
    <p><b>Outline</b> is what the claim rests on: solid for the Qur'an or authentic Sunnah, dashed for the Salaf, dotted for later scholars, and a small "?" where it is disputed.</p>
    <p>A disc marks a place or a whole land, never an area. Where it sits away from its site, a thin line leads back to the site.</p>`},
  upper:{title:"al-Jazīrah (Upper Mesopotamia)", ar:"الجزيرة", src:["early","classical"], cert:"approx", body:`
    <p><i>Al-Jazīrah</i> means "the island": the upland between the upper Euphrates and the Tigris. It is a different place from Jazīrat al-ʿArab, the Arabian peninsula.</p>
    <p>No verse names it. On ${q("في أدنى الأرض")} (al-Rūm 30:3) al-Baghawī records Mujāhid's view that "the nearest land" is al-Jazīrah, among other views.</p>
    <p>The classical geographers divide it into three <i>diyār</i>: Diyār Muḍar around al-Raqqah, Ḥarrān and al-Ruhā; Diyār Rabīʿah around al-Mawṣil and Nuṣaybīn; Diyār Bakr around Āmid and Mayyāfāriqīn. Al-Iṣṭakhrī gives al-Jazīrah a chapter of its own (<i>Arḍ al-Jazīrah</i>). I did not re-read each list, so the three names are not drawn as areas.</p>
    <p><b>On the map:</b> the colour fills the land between the two rivers, with both rivers taken from the real courses, which is what the name means. The dashed sides follow the rivers. The dotted north and south ends are mine: the geographers fix them by towns, and I could not confirm a source for a line.</p>`,
    refs:["Tafsir of al-Baghawī on al-Rūm 30:3",`Al-Iṣṭakhrī, <i>al-Masālik wa-l-Mamālik</i>, chapter <i>Arḍ al-Jazīrah</i> (<a href="https://shamela.ws/book/11680/66" target="_blank" rel="noopener">al-Shāmilah</a>)`]},
  iraq:{title:"al-ʿIrāq and the Sawād", ar:"العراق", src:["early","classical"], cert:"uncertain", body:`
    <p>I found no verse and no authentic hadith that calls Iraq a ḥaram, holy or blessed. What the Sunnah does give it is its <b>mīqāt</b>, Dhāt ʿIrq, which al-Bukhārī (1531) reports that ʿUmar رضي الله عنه fixed.</p>
    <p>In Abū Dāwūd 2483 (ṣaḥīḥ, al-Albānī) the Prophet ﷺ said the matter would come to armed troops, one in al-Shām, one in Yemen and one in Iraq, and told the Companion to go to al-Shām, "Allah's chosen land". That is a statement about al-Shām, not a judgment on Iraq. Other authentic hadith warn of trials from the east (al-Bukhārī 7093). Commentators differ on whether "the east" and "Najd" there mean Iraq or central Arabia, and the warnings are about trials, not about a people.</p>
    <p>Geography: <i>al-Sawād</i>, "the dark land", is the irrigated plain of the Tigris and Euphrates. Al-Iṣṭakhrī says that between Baghdad and al-Kūfah lies an unbroken <i>sawād</i>.</p>
    <p><b>On the map:</b> the shaded plain follows the two rivers with a margin on each side. Every edge is dotted: the geographers define al-ʿIrāq by named towns, and I could not re-read their formula in a source this session, so I draw no line I cannot source.</p>`,
    refs:[sn("bukhari",1531,"Al-Bukhārī 1531 (Dhāt ʿIrq)"),sn("abudawud",2483,"Abū Dāwūd 2483"),sn("bukhari",7093,"Al-Bukhārī 7093"),`Al-Iṣṭakhrī, chapter <i>al-ʿIrāq</i> (<a href="https://shamela.ws/book/11680/70" target="_blank" rel="noopener">al-Shāmilah</a>)`]},
  misr:{title:"Miṣr (Egypt) and Sinai", ar:"مصر", src:["rev","classical"], cert:"approx", body:`
    <p>The Qur'an names Miṣr: ${q("ادخلوا مصر إن شاء الله آمنين")}, "Enter Egypt, Allah ﷻ willing, safe [and secure]" (Yūsuf 12:99; also 10:87, 12:21, 43:51). The word also occurs in 2:61, but there it is <i>miṣran</i>, with tanwīn, and al-Ṭabarī reports Qatādah, al-Suddī, Mujāhid and Ibn Zayd reading it as "any town"; only Abū al-ʿĀliyah says Egypt, and al-Ṭabarī leaves the question open. Al-Baghawī reads "the eastern regions of the land and the western ones, which We had blessed" (al-Aʿrāf 7:137, Saheeh International) as Miṣr and al-Shām, blessed with water, trees, fruit and abundance.</p>
    <p>In the Sunnah (Muslim 2543, Abū Dharr) the Prophet ﷺ said the Muslims would conquer Egypt and told them to treat its people well, for they have a covenant (<i>dhimmah</i>) and kinship (<i>raḥim</i>). The status belongs to its people and, by tafsīr, to the land; no text draws a boundary.</p>
    <p><b>Solid colour:</b> the Nile valley and Delta, the cultivated land. Al-Iṣṭakhrī describes the cultivation as running from the limit of Aswān to the limit of Alexandria.</p>
    <p><b>Hatching:</b> Yāqūt's reckoning of the whole land, ${q("طولها من الشجرتين اللتين كانتا بين رفح والعريش إلى أسوان، وعرضها من برقة إلى أيلة")}: its length from the two trees that stood between Rafaḥ and al-ʿArīsh to Aswān, and its width from Barqah to Aylah. On that reckoning Sinai lies inside Miṣr (my reading), and the west edge sits at Barqah in Libya, off the left of the usual view. Where this hatching crosses al-Shām's near al-ʿArīsh and Rafaḥ, the sources disagree about which land the strip belongs to.</p>`,
    refs:[`Yāqūt, <i>Muʿjam al-Buldān</i>, s.v. Miṣr (<a href="https://arabiclexicon.hawramani.com/%d9%85%d9%90%d8%b5%d9%92%d8%b1%d9%8f/" target="_blank" rel="noopener">text</a>)`,`Al-Iṣṭakhrī, <i>Diyār Miṣr</i> (<a href="https://shamela.ws/book/11680/52" target="_blank" rel="noopener">al-Shāmilah</a>)`,sn("muslim","2543","Muslim 2543"),"Qur'an, Yūsuf 12:99; al-Aʿrāf 7:137; tafsir of al-Baghawī"]},
  najd:{title:"Najd", ar:"نجد", src:["early","classical"], cert:"uncertain", body:`
    <p>Najd means the high ground: the interior plateau east of the Ḥijāz mountains. Hishām b. al-Kalbī derived al-Ḥijāz from its being a barrier between Tihāmah and Najd, and al-Aṣmaʿī says the beginning of Tihāmah on the Najd side is Dhāt ʿIrq (both via Yāqūt).</p>
    <p>The Sunnah fixes Qarn al-Manāzil as the mīqāt of the people of Najd (al-Bukhārī 1524, Muslim 1181). In al-Bukhārī 1037 the Prophet ﷺ prayed for blessing on al-Shām and Yemen, and when the people asked about Najd he said that earthquakes and trials would appear there and that the side of the head of Satan would rise from it. Scholars differ on which Najd is meant, and I give no verdict.</p>
    <p><b>On the map:</b> a dotted outline around the Qaṣīm–Ḥāʾil–Riyadh plateau. No source I read draws classical Najd as a polygon, and later usage narrowed the name, so treat the outline as a rough indication. Al-Yamāmah, around the old Ḥajr near today's Riyadh, is marked on the jurists' layer; I did not read a source that places it inside or outside Najd.</p>`,
    refs:["Yāqūt, Muʿjam al-Buldān, s.v. al-Ḥijāz and Tihāmah",sn("bukhari",1037,"Al-Bukhārī 1037"),"Al-Bukhārī 1524, Muslim 1181"]},
  bahrayn:{title:"al-Baḥrayn", ar:"البحرين", src:["early","classical"], cert:"uncertain", body:`
    <p>In the early sources al-Baḥrayn means the Gulf coast of Arabia, with al-Aḥsāʾ and al-Qaṭīf, and not only today's island state. In al-Bukhārī 892 (Ibn ʿAbbās) the first Friday prayer held after the one in the mosque of the Prophet ﷺ was in the mosque of ʿAbd al-Qays at Jawāthā in al-Baḥrayn.</p>
    <p><b>On the map:</b> a dotted belt along the coast. The sources I read this session do not give its limits, so the belt shows where the name was used, not a boundary. Jawāthā is placed at al-Aḥsāʾ by tradition; its exact site is approximate.</p>
    <p class="fine">The wider sense of the name is general history, not a text I fetched.</p>`,
    refs:[sn("bukhari",892,"Al-Bukhārī 892")]},
  tihamah:{title:"Tihāmah", ar:"تهامة", src:["early","classical"], cert:"uncertain", body:`
    <p>Tihāmah is the low coastal plain of the Red Sea, below the Sarāt mountains. Al-Aṣmaʿī (via Yāqūt): ${q("فمكة تهامية والمدينة حجازية والطائف حجازية")}, Makkah is Tihāmī, Madinah and al-Ṭāʾif are Ḥijāzī. So Makkah lies in Tihāmah in the strict sense and in al-Ḥijāz in the wider sense; the map shows the two overlapping.</p>
    <p>Also via Yāqūt: Tihāmah runs alongside the sea, and Makkah is of it; its edge toward al-Ḥijāz is the passes of al-ʿUrj; and its beginning on the Najd side is Dhāt ʿIrq.</p>
    <p><b>On the map:</b> a dotted belt from Bāb al-Mandab to near Yanbuʿ, clipped to the Arabian coast. Its inland edge follows the foot of the Sarāt roughly, and its northern end is my guess: no source I read fixes it.</p>`,
    refs:[`Yāqūt, <i>Muʿjam al-Buldān</i>, s.v. Tihāmah (<a href="https://arabiclexicon.hawramani.com/%d8%aa%d9%87%d9%8e%d8%a7%d9%85%d9%8e%d8%a9/" target="_blank" rel="noopener">text</a>) and s.v. al-Ḥijāz`]},
  saba:{title:"Sabaʾ and Maʾrib", ar:"سبأ · مأرب", src:["rev","early"], cert:"approx", body:`
    <p>Sabaʾ 34:15: ${q("لقد كان لسبإ في مسكنهم آية جنتان عن يمين وشمال")}, "There was for [the tribe of] Saba’ in their dwelling place a sign: two [fields of] gardens on the right and on the left"; and to them, ${q("بلدة طيبة ورب غفور")}, "A good land [have you], and a forgiving Lord" (Saheeh International). Then ${q("فأرسلنا عليهم سيل العرم")} (34:16), "so We sent upon them the flood of the dam".</p>
    <p>Al-Baghawī places their dwellings at Maʾrib in Yemen. On 34:18, ${q("وجعلنا بينهم وبين القرى التي باركنا فيها قرى ظاهرة")}, he describes a chain of villages along the trade road between Sabaʾ and the blessed land, al-Shām. Verse 19 ends ${q("ومزقناهم كل ممزق")}, "and We dispersed them in total dispersion".</p>
    <p>Who was Sabaʾ? Asked whether Sabaʾ was a land or a woman, the Prophet ﷺ said neither: a man with ten sons (al-Tirmidhī 3222, graded ḥasan by Darussalam). Six settled in Yemen (Kindah, the Ashʿarīs, Azd, Madhḥij, Anmār, Ḥimyar) and four went to al-Shām (ʿĀmilah, Judhām, Lakhm, Ghassān). Al-Baghawī cites the same hadith.</p>
    <p>The marker is Maʾrib. The road from Maʾrib by Najrān to Tabālah, joining the Quraysh winter road, is approximate; turn on the roads layer to see it.</p>`,
    refs:["Qur'an, Sabaʾ 34:15–19; tafsir of al-Baghawī on 34:15 and 34:18",sn("tirmidhi",3222,"Al-Tirmidhī 3222 (Farwah b. Musayk)")]},
  ahqaf:{title:"al-Aḥqāf and Ḥaḍramawt", ar:"الأحقاف", src:["rev","early"], cert:"uncertain", body:`
    <p>Al-Aḥqāf 46:21: ${q("واذكر أخا عاد إذ أنذر قومه بالأحقاف")}, "And mention, [O Muḥammad], the brother of ʿAad, when he warned his people in [the region of] al-Aḥqāf" (Saheeh International). <i>Aḥqāf</i> is the plural of <i>ḥiqf</i>, a long curved dune (al-Baghawī).</p>
    <p>Where? Al-Baghawī gives three early reports. <b>Ibn ʿAbbās:</b> a valley between ʿUmān and Mahrah. <b>Muqātil:</b> the homes of ʿĀd were in Yemen, in Ḥaḍramawt, at a place called Mahrah. <b>Qatādah:</b> in sands overlooking the sea, in a land called al-Shiḥr. The Qur'an does not name Ḥaḍramawt; it appears only in the commentary.</p>
    <p>The three dotted rings mark the three reports. Their size is illustrative: no ring is a boundary. All three point to the south-eastern coast of Arabia.</p>`,
    refs:["Qur'an, al-Aḥqāf 46:21; tafsir of al-Baghawī on 46:21"]},
  habashah:{title:"al-Ḥabashah (Abyssinia)", ar:"الحبشة", src:["rev","early"], cert:"approx", body:`
    <p>The Qur'an does not name al-Ḥabashah: the root ح ب ش does not occur in it (quran.ai concordance). The Sunnah does. The Prophet ﷺ announced the death of the Najāshī on the day he died, went out to the prayer ground and prayed over him with four takbīrs (al-Bukhārī 1245, Abū Hurayrah). And: "leave the Abyssinians alone as long as they leave you alone" (Abū Dāwūd 4302, graded ḥasan by al-Albānī).</p>
    <p>No sacred status is established for the land. The marker is Aksūm, which I use for the heart of the Najāshī's kingdom; that placement is my gloss from general history, not a text I fetched. The sea crossing of the first emigration to al-Ḥabashah is told in the sīrah, and I have not drawn it.</p>`,
    refs:[sn("bukhari",1245,"Al-Bukhārī 1245"),sn("abudawud",4302,"Abū Dāwūd 4302")]},
  rum:{title:"Bilād al-Rūm", ar:"بلاد الروم", src:["rev","early","classical"], cert:"uncertain", body:`
    <p>The Qur'an names the Byzantines: ${q("غلبت الروم في أدنى الأرض")}, "the Byzantines have been defeated in the nearest land" (al-Rūm 30:2–3). Al-Baghawī's views on "the nearest land" are on the lettered badge at Adhriʿāt and Buṣrā.</p>
    <p>In the Sunnah, "The first army amongst my followers who will invade Caesar's City will be forgiven their sins" (al-Bukhārī 2924, from Umm Ḥarām). Muslim 2897 places the conquest of Constantinople among the events before the Hour. The virtue belongs to an army, not to the land.</p>
    <p><b>On the map:</b> the land beyond the frontier fortresses (<i>al-thughūr</i>). Its dotted edge is the outer limit of al-Shām as Ibn Ḥawqal and Abū al-Fidāʾ draw it, and that frontier moved with the wars. The eastern edge toward Armenia is not taken from any source; the other edges are only where the land ends.</p>`,
    refs:["Qur'an, al-Rūm 30:2–4; tafsir of al-Baghawī on 30:3",sn("bukhari",2924,"Al-Bukhārī 2924"),sn("muslim",2897,"Muslim 2897")]},
  eschat:{title:"Places named in hadith about the end of time", src:["rev"], cert:"approx", body:`
    <p>These are reports about events that have not happened. I give the wording and the grading; I do not interpret or date them. Positions are approximate, and each marker opens its own note.</p>
    <ul>
      <li><b>al-Ghūṭah, near Damascus:</b> Abū Dāwūd 4298, ṣaḥīḥ (al-Albānī).</li>
      <li><b>Dābiq or al-Aʿmāq:</b> Muslim 2897.</li>
      <li><b>Bāb Ludd:</b> Muslim 2937.</li>
      <li><b>Caesar's city:</b> al-Bukhārī 2924; Muslim 2897.</li>
      <li><b>Buṣrā:</b> al-Bukhārī 7118, the fire from the land of al-Ḥijāz.</li>
    </ul>`},
  eg_ghutah:{title:"al-Ghūṭah", ar:"الغوطة", src:["rev"], cert:"approx", body:`
    <p>Abū al-Dardāʾ رضي الله عنه reported that the Prophet ﷺ said: "The place of assembly of the Muslims at the time of war will be in al-Ghūṭah, near a city called Damascus, one of the best cities of al-Shām." Graded <b>ṣaḥīḥ</b> by al-Albānī, as sunnah.com gives it.</p>
    <p>The Ghūṭah is the belt of orchards around Damascus. The marker is on its eastern side; the hadith gives no more precise place.</p>`,
    refs:[sn("abudawud",4298,"Abū Dāwūd 4298")]},
  eg_dabiq:{title:"Dābiq", ar:"دابق", src:["rev"], cert:"approx", body:`
    <p>Abū Hurayrah رضي الله عنه reported that the Prophet ﷺ said the Hour would not come until the Romans landed at al-Aʿmāq or at Dābiq, and that an army of the best of the people of the earth at that time would come from Madinah against them (Muslim 2897).</p>
    <p>Dābiq is a village in the north of Aleppo province, near Aʿzāz. The position here is approximate.</p>`,
    refs:[sn("muslim",2897,"Muslim 2897")]},
  eg_amaq:{title:"al-Aʿmāq", ar:"الأعماق", src:["rev"], cert:"uncertain", body:`
    <p>Named beside Dābiq in the same hadith (Muslim 2897). It is commonly identified with the ʿAmuq plain by Antioch (Anṭākiyah), today in Hatay, Türkiye; that identification is general geography, not part of the hadith. The ring marks the plain loosely.</p>`,
    refs:[sn("muslim",2897,"Muslim 2897")]},
  eg_ludd:{title:"Bāb Ludd", ar:"باب لد", src:["rev"], cert:"approx", body:`
    <p>In the long hadith of al-Nawwās b. Samʿān رضي الله عنه (Muslim 2937) the Prophet ﷺ describes the Dajjāl, who appears "between al-Shām and Iraq", and then the descent of ʿĪsā ibn Maryam عليه السلام at the white minaret on the eastern side of Damascus, who kills the Dajjāl at the gate of Ludd.</p>
    <p>Ludd is Lydda, today Lod in Israel. The marker is the town.</p>`,
    refs:[sn("muslim","2937","Muslim 2937")]},
  eg_qust:{title:"Qusṭanṭīniyyah (Caesar's city)", ar:"القسطنطينية", src:["rev"], cert:"firm", body:`
    <p>Al-Bukhārī 2924 (from Umm Ḥarām, the wife of ʿUbādah b. al-Ṣāmit): "The first army amongst my followers who will invade Caesar's City will be forgiven their sins." Umm Ḥarām asked whether she would be among them, and he said she would not. Muslim 2897 places the conquest of Constantinople in the sequence of events before the Hour.</p>
    <p>The marker is Istanbul. The virtue is for an army, and no sacred status attaches to the city.</p>`,
    refs:[sn("bukhari",2924,"Al-Bukhārī 2924"),sn("muslim",2897,"Muslim 2897")]},
  isra:{title:"al-Isrāʾ and the qibla", ar:"الإسراء والقبلة", src:["rev"], cert:"approx", body:`
    <p>Al-Isrāʾ 17:1: the night journey from the Sacred Mosque to the Furthest Mosque, "whose surroundings We have blessed". The verse does not describe the route, so the thin dotted line is schematic only.</p>
    <p>The first qibla was Bayt al-Maqdis. The Prophet ﷺ prayed toward it for sixteen or seventeen months after reaching Madinah, and then the direction was changed to the Kaʿbah (al-Bukhārī 40, al-Barāʾ b. ʿĀzib; al-Baqarah 2:144). The two short arrows at Madinah show the two directions.</p>`,
    refs:["Qur'an, al-Isrāʾ 17:1; al-Baqarah 2:144",sn("bukhari",40,"Al-Bukhārī 40")]}
};

/* ---------- sacred-status rows (numbers match the discs and the table) ---------- */
const STATUS = [
 {n:1, name:"al-Masjid al-Ḥarām and the Ḥaram of Makkah", kinds:["haram","mub","fad"], kind:"haram", level:"rev", lvl:"Qur'an & Sunnah", ll:[39.8262,21.4225], off:[-17,-17], pri:1, minK:0, focus:4,
  rests:`Qur'an: the Lord of this city ${q("الَّذِي حَرَّمَهَا")}, "who made it sacred" (27:91); ${q("حرما آمنا")}, "a safe sanctuary" (28:57); the first House, at Bakkah, ${q("مباركا")}, "blessed" (3:96). Sunnah: Allah ﷻ made it sacred on the day He created the heavens and the earth (al-Bukhārī 1834, Ibn ʿAbbās); one of the three masjids to which a journey is made (al-Bukhārī 1189); the best of the land of Allah ﷻ (al-Tirmidhī 3925, which al-Tirmidhī calls ḥasan ṣaḥīḥ gharīb; also Ibn Mājah 3108).`,
  where:`<b>Fixed.</b> Boundary markers stand on the roads in. Al-Nawawī's distances, in mīl: al-Tanʿīm 3, the Yemen road 7, the Iraq road 7, the Ṭāʾif road 7, the al-Jiʿrānah road 9, the Jeddah road 10. Ibn Taymiyyah: the one ḥaram all agree on. Drawn in the inset.`,
  refs:[sn("bukhari",1834,"Al-Bukhārī 1834"),sn("bukhari",1189,"Al-Bukhārī 1189"),"Al-Tirmidhī 3925, Ibn Mājah 3108","Al-Nawawī, al-Majmūʿ (Islamweb fatwa 71668)","Ibn Taymiyyah, Majmūʿ al-Fatāwā 27/14–15"]},
 {n:2, name:"ʿArafah, Muzdalifah and Minā", kinds:["muq"], kind:"muq", level:"rev", lvl:"Qur'an & Sunnah", ll:[39.935,21.392], off:[18,16], pri:5, minK:7, focus:4,
  rests:`Qur'an 2:198: remember Allah ﷻ at al-Mashʿar al-Ḥarām, "the sacred monument". Al-Baghawī: al-Mashʿar al-Ḥarām lies between the two mountains of Muzdalifah, from the two passes of ʿArafah to Muḥassir, and neither the passes nor Muḥassir are part of it.`,
  where:`<b>ʿArafah itself is outside the ḥaram</b>; Minā and Muzdalifah are inside it. The ḥaram line on the ʿArafah side runs at Baṭn Namirah.`,
  refs:["Qur'an, al-Baqarah 2:198; tafsir of al-Baghawī"]},
 {n:3, name:"The Ḥaram of Madinah and al-Masjid al-Nabawī", kinds:["haram","mub","fad"], kind:"haram", level:"rev", lvl:"Sunnah · rulings disputed", ll:[39.6111,24.4672], off:[-17,-17], pri:1, minK:0, focus:5,
  rests:`Sunnah: Madinah is a sanctuary (ḥaram) from ʿAyr to Thawr (al-Bukhārī 6755, Muslim 1370); the ground between its two lava fields is a sanctuary (Abū Hurayrah, Muslim 1372, where he also made twelve mīl around it a ḥimā, a protected pasture); the Prophet ﷺ prayed that Madinah be given twice the blessing of Makkah (al-Bukhārī 1885, Anas); one prayer in his mosque is better than a thousand elsewhere except al-Masjid al-Ḥarām (al-Bukhārī 1190, Abū Hurayrah).`,
  where:`<b>Landmarks given, line approximate:</b> ʿAyr to the south, Thawr to the north, the two lava fields (Ḥarrat Wāqim in the east, Ḥarrat al-Wabarah in the west). Most scholars hold it is a true ḥaram; the Ḥanafī school is reported to differ (not re-checked here). Ibn Taymiyyah takes ʿAyr as a mountain near the mīqāt and Thawr as a hill near Uḥud, not the Thawr of Makkah.`,
  refs:[sn("bukhari",6755,"Al-Bukhārī 6755")+", "+sn("muslim",1370,"Muslim 1370")+" (al-Bukhārī 1870 has the same ʿAyr but leaves the second place unnamed)",sn("muslim",1372,"Muslim 1372"),sn("bukhari",1885,"Al-Bukhārī 1885"),sn("bukhari",1190,"Al-Bukhārī 1190")]},
 {n:4, name:"Masjid Qubāʾ", kinds:["fad"], kind:"fad", level:"rev", lvl:"Sunnah · Salaf differ on 9:108", ll:[39.6172,24.4393], off:[-16,14], pri:6, minK:4, focus:5,
  rests:`Sunnah: the Prophet ﷺ used to go to Qubāʾ every Saturday, walking or riding (al-Bukhārī 1193, Ibn ʿUmar). On the masjid "founded on righteousness from the first day" (al-Tawbah 9:108) the Salaf differ, as al-Baghawī reports: some said the Prophet's Mosque, with a hadith in Muslim (1398, Abū Saʿīd), others Qubāʾ.`,
  where:`A known masjid south of the Prophet's Mosque, inside Madinah's ḥaram.`,
  refs:[sn("bukhari",1193,"Al-Bukhārī 1193"),sn("muslim",1398,"Muslim 1398"),"Tafsir of al-Baghawī on 9:108"]},
 {n:5, name:"Wādī al-ʿAqīq", kinds:["mub"], kind:"mub", level:"rev", lvl:"Sunnah", ll:[39.575,24.47], off:[-18,-12], pri:7, minK:6, focus:5,
  rests:`ʿUmar رضي الله عنه heard the Prophet ﷺ say, in Wādī al-ʿAqīq, that a messenger from his Lord had come to him that night and told him to pray "in this blessed valley" (al-Bukhārī 1534).`,
  where:`The valley west of Madinah. The hadith names the valley, not its limits.`,
  refs:[sn("bukhari",1534,"Al-Bukhārī 1534")]},
 {n:6, name:"Uḥud", kinds:["fad"], kind:"fad", level:"rev", lvl:"Sunnah", ll:[39.615,24.505], off:[16,-12], pri:7, minK:6, focus:5,
  rests:`Returning from Tabūk, the Prophet ﷺ called Madinah Ṭābah and said Uḥud is a mountain that loves us and that we love (al-Bukhārī 4422, Abū Ḥumayd).`,
  where:`The mountain itself. The hill of Thawr that bounds Madinah's ḥaram lies behind it, on Ibn Taymiyyah's reading.`,
  refs:[sn("bukhari",4422,"Al-Bukhārī 4422")]},
 {n:7, name:"Wajj, the valley of al-Ṭāʾif", kinds:["haram"], kind:"haram", level:"disp", lvl:"Disputed", ll:[40.40,21.25], off:[14,16], pri:5, minK:2, focus:4,
  rests:`Abū Dāwūd 2032 (al-Zubayr) reports that the Prophet ﷺ declared the game and thorn trees of Wajj forbidden; al-Albānī grades it <b>ḍaʿīf</b>. Ibn Taymiyyah called Wajj the only third place whose ḥaram status was disputed: al-Shāfiʿī accepted the report, while most scholars, including Aḥmad, did not.`,
  where:`The valley is known; no boundary text exists.`,
  refs:[sn("abudawud",2032,"Abū Dāwūd 2032"),"Ibn Taymiyyah, Majmūʿ al-Fatāwā 27/14–15"]},
 {n:8, name:"al-Masjid al-Aqṣā · Bayt al-Maqdis", kinds:["mub","fad"], kind:"mub", level:"rev", lvl:"Qur'an & Sunnah", ll:[35.2355,31.7779], off:[-17,-15], pri:1, minK:0, focus:3,
  rests:`Qur'an 17:1: ${q("الَّذِي بَارَكْنَا حَوْلَهُ")}, "whose surroundings We have blessed". Sunnah: one of the three masjids to which a journey is made (al-Bukhārī 1189); the second masjid built on earth, forty years after al-Masjid al-Ḥarām (al-Bukhārī 3366, Muslim 520, Abū Dharr); the first qibla, for sixteen or seventeen months (al-Bukhārī 40). Narrations about a multiple of reward for prayer there are graded differently.`,
  where:`The masjid is the walled enclosure. <b>The "surroundings" have no stated extent</b>: al-Baghawī explains the blessing as rivers, trees and fruit and, from Mujāhid, as the home of the prophets and the place where revelation came down. <b>Not a ḥaram in fiqh</b>: "there is no ḥaram in the world, neither Bayt al-Maqdis nor anything else, except these two ḥarams" (Ibn Taymiyyah). "al-Ḥaram al-Sharīf" is an honorific name.`,
  refs:["Qur'an 17:1; tafsir of al-Baghawī",sn("bukhari",3366,"Al-Bukhārī 3366"),sn("muslim",520,"Muslim 520"),sn("bukhari",40,"Al-Bukhārī 40"),`Ibn Taymiyyah, Majmūʿ al-Fatāwā 26/118 for the quoted sentence (<a href="https://islamqa.info/ar/answers/5419" target="_blank" rel="noopener">islamqa.info</a>); see also 27/14–15`]},
 {n:9, name:"al-Arḍ al-Muqaddasah, the Holy Land", kinds:["muq"], kind:"muq", level:"rev", lvl:"Qur'an: the status · Salaf differ: the extent", ll:[36.9,32.9], off:[22,-14], pri:3, minK:0, focus:1, goto:"muq",
  rests:`Qur'an 5:21: Mūsā عليه السلام says to his people ${q("ادخلوا الأرض المقدسة")}, "enter the blessed land [i.e., Palestine]" (Saheeh International; the bracket is the translators' gloss, not in the Arabic; "the Holy Land" is this atlas's own name for <i>al-arḍ al-muqaddasah</i>). The verse names it but does not mark its extent.`,
  where:`<b>The extent was differed on.</b> Al-Ṭabarī records al-Ṭūr and its surroundings (Mujāhid, Ibn ʿAbbās); al-Shām (Qatādah); Arīḥāʾ (Ibn ʿAbbās via ʿIkrimah, al-Suddī, Ibn Zayd); and, unattributed, Dimashq, Filasṭīn and part of al-Urdunn. His verdict: it cannot be pinned to one land without a sound report, but all agree it lies between the Euphrates and al-ʿArīsh of Egypt. Turn on the Muqaddasah layer for each view.`,
  refs:["Qur'an 5:21; tafsir of al-Ṭabarī and al-Baghawī"]},
 {n:10, name:"\"The land We blessed\"", kinds:["mub"], kind:"mub", level:"rev", lvl:"Qur'an: the status · tafsīr: which land", ll:[36.2,35.55], off:[-20,-14], pri:4, minK:0, focus:1,
  rests:`Qur'an 21:71 (Ibrāhīm and Lūṭ are brought to ${q("الأرض التي باركنا فيها")}), 21:81 (Sulaymān's wind), 34:18 ("the cities which We had blessed"), 7:137 ("the eastern regions of the land and the western ones, which We had blessed").`,
  where:`Al-Baghawī identifies it as al-Shām in 21:71 and 21:81 and the towns of al-Shām in 34:18; for 7:137 he says "Miṣr and al-Shām", blessed with water, trees, fruit, fertility and abundance. No boundary beyond the name.`,
  refs:["Tafsir of al-Baghawī on 7:137, 21:71, 21:81, 34:18"]},
 {n:11, name:"al-Shām in the Sunnah", kinds:["fad"], kind:"fad", level:"rev", lvl:"Sunnah · Muʿādh: a Companion's reading", ll:[38.4,33.2], off:[18,16], pri:3, minK:0, focus:1,
  rests:`The Prophet ﷺ prayed for blessing on "our Sham and our Yemen" (al-Bukhārī 1037, Ibn ʿUmar). "Ṭūbā for al-Shām … the angels of al-Raḥmān spread their wings over it" (al-Tirmidhī 3954, Zayd b. Thābit; ḥasan, Darussalam). "Go to Syria, for it is Allah's chosen land, to which his best servants will be gathered" (Abū Dāwūd 2483, Ibn Ḥawālah; ṣaḥīḥ, al-Albānī). Muʿādh b. Jabal said the group that stays on the truth are in al-Shām (al-Bukhārī 3641): a Companion's understanding.`,
  where:`No text fixes al-Shām's boundary; see the geography layers.`,
  refs:[sn("bukhari",1037,"Al-Bukhārī 1037"),sn("tirmidhi",3954,"Al-Tirmidhī 3954"),sn("abudawud",2483,"Abū Dāwūd 2483"),sn("bukhari",3641,"Al-Bukhārī 3641")]},
 {n:12, name:"al-Ṭūr, the valley of Ṭuwā, the blessed spot", kinds:["muq","mub"], kind:"muq", level:"rev", lvl:"Qur'an: the status · tradition: the exact peak", ll:[33.975,28.539], off:[-18,-14], pri:2, minK:0, focus:20, goto:"tuwa",
  rests:`Qur'an: ${q("بالواد المقدس طوى")} (20:12; also 79:16): the Arabic is the same in both; Saheeh International renders it "blessed valley" in 20:12 and "sacred valley" in 79:16. 28:30: ${q("البقعة المباركة")}, "a blessed spot" (Saheeh International). Oaths by the mountain (52:1) and by Ṭūr Sīnīn (95:2).`,
  where:`Al-Baghawī: Ṭuwā is the name of the valley and <i>muqaddas</i> means purified; the spot is blessed because Allah ﷻ spoke to Mūsā there and made him a prophet. The Qur'an names the valley and the spot, not a peak: the triangle marker at Jabal Mūsā is a later tradition. <b>Dhū Ṭuwā near Makkah is a different place</b> (al-Bukhārī 1573, where Ibn ʿUmar spent the night before entering Makkah).`,
  refs:["Qur'an 20:12, 79:16, 28:30, 52:1, 95:2; tafsir of al-Baghawī",sn("bukhari",1573,"Al-Bukhārī 1573")]},
 {n:13, name:"The fig and the olive", kinds:[], kind:"none", level:"disp", lvl:"Salaf differ", ll:[36.2919,33.5131], off:[-20,-18], pri:7, minK:2.2, focus:1,
  rests:`Qur'an 95:1: ${q("والتين والزيتون")}, "by the fig and the olive". Al-Baghawī: Ibn ʿAbbās, al-Ḥasan, Mujāhid, Ibrāhīm, ʿAṭāʾ, Muqātil and al-Kalbī take the fruits themselves. ʿIkrimah: two mountains. Qatādah: the mountain of Damascus and the mountain of Bayt al-Maqdis. Al-Ḍaḥḥāk: two masjids in al-Shām; Ibn Zayd: the masjid of Damascus and the masjid of Bayt al-Maqdis. Muḥammad b. Kaʿb: the masjid of the People of the Cave and the masjid of Īliyāʾ.`,
  where:`Any place reading is a minority view; the oath is not established as a sacred status for a place.`,
  refs:["Tafsir of al-Baghawī on 95:1–3"]},
 {n:14, name:"al-Yaman", kinds:["fad"], kind:"fad", level:"rev", lvl:"Qur'an & Sunnah", ll:[45.9,15.7], off:[-18,-14], pri:3, minK:0, focus:16, goto:"yemen",
  rests:`Sunnah: "Belief is Yemenite and Wisdom is Yemenite" (al-Bukhārī 4388, Abū Hurayrah), said of its people; the Prophet ﷺ prayed for blessing on "our Sham and our Yemen" (al-Bukhārī 1037). Qur'an: to Sabaʾ, ${q("بلدة طيبة ورب غفور")}, "A good land [have you], and a forgiving Lord" (34:15, Saheeh International).`,
  where:`The texts name Yemen and Sabaʾ, not boundaries. Al-Aṣmaʿī's al-Ḥijāz ends at Yemen's marches (Tabālah, badge I).`,
  refs:[sn("bukhari",4388,"Al-Bukhārī 4388"),sn("bukhari",1037,"Al-Bukhārī 1037"),"Qur'an, Sabaʾ 34:15"]},
 {n:15, name:"Miṣr (Egypt)", kinds:["fad"], kind:"fad", level:"rev", lvl:"Sunnah: its people · tafsīr: the blessing", ll:[31.0,28.1], off:[-18,-14], pri:3, minK:0, focus:14, goto:"misr",
  rests:`Sunnah: "You would soon conquer Egypt … So when you conquer it, treat its inhabitants well", for "protection and blood-relationship" apply to them (Muslim 2543, Abū Dharr). The Qur'an names it: ${q("ادخلوا مصر إن شاء الله آمنين")} (12:99). Al-Baghawī reads the land "which We had blessed" in 7:137 as Miṣr and al-Shām.`,
  where:`No boundary text. Sinai's sacred places (12) lie in today's Egypt. Yāqūt's and al-Iṣṭakhrī's reckonings are on the Miṣr layer.`,
  refs:[sn("muslim","2543","Muslim 2543"),"Qur'an, Yūsuf 12:99; tafsir of al-Baghawī on 7:137"]},
 {n:16, name:"Iraq and the East", kinds:[], kind:"none", level:"rev", lvl:"Sunnah: warnings · which land: disputed", ll:[44.3661,33.3152], off:[-18,-16], pri:3, minK:0, focus:13, goto:"iraq",
  rests:`I found no text in the Qur'an or the authentic Sunnah that calls Iraq a ḥaram, holy or blessed. The Sunnah does fix its mīqāt, Dhāt ʿIrq (set by ʿUmar, per al-Bukhārī 1531). Iraq is one of the three troops in Abū Dāwūd 2483 (the Companion is told to choose al-Shām). Authentic hadith warn of trials from the east: "afflictions are there, from where the side of the head of Satan comes out" (al-Bukhārī 7093, Ibn ʿUmar). Asked about "our Najd" after the duʿā for al-Shām and Yemen, the Prophet ﷺ said that earthquakes and trials would appear there (al-Bukhārī 1037).`,
  where:`Commentators differ on whether "the east" and "Najd" there mean Iraq or central Arabia. These are warnings about trials, not judgments on a people.`,
  refs:[sn("bukhari",1531,"Al-Bukhārī 1531"),sn("bukhari",7093,"Al-Bukhārī 7093"),sn("bukhari",1037,"Al-Bukhārī 1037"),sn("abudawud",2483,"Abū Dāwūd 2483")]},
 {n:17, name:"The mawāqīt", kinds:["link"], kind:"link", level:"rev", lvl:"Sunnah", ll:[40.45,21.95], off:[20,-18], pri:4, minK:1.4, focus:6, goto:"miqat",
  rests:`Ibn ʿAbbās رضي الله عنهما: the Prophet ﷺ fixed Dhū al-Ḥulayfah for the people of Madinah, al-Juḥfah for al-Shām, Qarn al-Manāzil for Najd and Yalamlam for Yemen (al-Bukhārī 1524, Muslim 1181). Dhāt ʿIrq, for Iraq, was fixed by ʿUmar (al-Bukhārī 1531).`,
  where:`Fixed points, not areas: the Sunnah's own map of how each land comes to the Ḥaram.`,
  refs:["Al-Bukhārī 1524, Muslim 1181",sn("bukhari",1531,"Al-Bukhārī 1531")]},
 {n:18, name:"al-Isrāʾ and the qibla", kinds:["link"], kind:"link", level:"rev", lvl:"Qur'an & Sunnah", ll:[37.4,26.4], off:[18,-14], pri:4, minK:0, focus:0, goto:"links",
  rests:`Qur'an 17:1: the night journey from the Sacred Mosque to the Furthest Mosque; 2:144: turn your face toward the Sacred Mosque. Sunnah: the first qibla was Bayt al-Maqdis, for sixteen or seventeen months (al-Bukhārī 40).`,
  where:`The line on the map is schematic: the route is not given. The arrows at Madinah show the two qibla directions.`,
  refs:["Qur'an 17:1, 2:144",sn("bukhari",40,"Al-Bukhārī 40")]},
 {n:19, name:"Sabaʾ, the blessed towns and Quraysh's journeys", kinds:["link"], kind:"link", level:"rev", lvl:"Qur'an · tafsīr: the route", ll:[44.13,17.49], off:[-18,-14], pri:4, minK:0.9, focus:16, goto:"trade",
  rests:`Qur'an 34:18: ${q("وجعلنا بينهم وبين القرى التي باركنا فيها قرى ظاهرة")}, "And We placed between them and the cities which We had blessed [many] visible cities"; 106:2, the winter and summer journeys. Al-Baghawī: the towns ran continuously from Sabaʾ to al-Shām along their trade road; one view of 106:2 is winter to Yemen and summer to al-Shām.`,
  where:`The dotted route is approximate. Sabaʾ's own note has the hadith on its ten sons.`,
  refs:["Qur'an 34:18; 106:1–4; tafsir of al-Baghawī",sn("tirmidhi",3222,"Al-Tirmidhī 3222")]},
 {n:20, name:"al-Ḥabashah", kinds:[], kind:"none", level:"rev", lvl:"Sunnah (a king and a people) · not in the Qur'an", ll:[38.72,14.13], off:[-18,-14], pri:4, minK:0, focus:17, goto:"habashah",
  rests:`Not named in the Qur'an. Sunnah: the Prophet ﷺ prayed over the Najāshī on the day he died (al-Bukhārī 1245); "leave the Abyssinians alone as long as they leave you alone" (Abū Dāwūd 4302, ḥasan, al-Albānī).`,
  where:`No sacred status for the land is established. Aksūm is my marker for the kingdom's heart.`,
  refs:[sn("bukhari",1245,"Al-Bukhārī 1245"),sn("abudawud",4302,"Abū Dāwūd 4302")]},
 {n:21, name:"Bilād al-Rūm", kinds:[], kind:"none", level:"rev", lvl:"Qur'an names it · Sunnah: a virtue for an army", ll:[32.8,38.9], off:[0,0], pri:4, minK:0, focus:18, goto:"rum",
  rests:`Qur'an 30:2–3: ${q("غلبت الروم في أدنى الأرض")}. Sunnah: the first army to invade Caesar's city is forgiven (al-Bukhārī 2924); Muslim 2897 sets the conquest of Constantinople among the events before the Hour.`,
  where:`The virtue is for an army, not for the land. The frontier at the thughūr moved with the wars.`,
  refs:[sn("bukhari",2924,"Al-Bukhārī 2924"),sn("muslim",2897,"Muslim 2897")]},
 {n:22, name:"Places named in hadith about the end of time", kinds:[], kind:"none", level:"rev", lvl:"Sunnah (al-Ghūṭah: ṣaḥīḥ, al-Albānī)", ll:[36.0,35.6], off:[22,-12], pri:5, minK:1.2, focus:1, goto:"eschat",
  rests:`al-Ghūṭah near Damascus (Abū Dāwūd 4298, ṣaḥīḥ per al-Albānī); Dābiq or al-Aʿmāq (Muslim 2897); the gate of Ludd (Muslim 2937); Caesar's city (al-Bukhārī 2924); the fire from the land of al-Ḥijāz that lights the necks of the camels at Buṣrā (al-Bukhārī 7118).`,
  where:`Reports about events that have not happened; I give the wording and the grading and no interpretation. Positions are approximate.`,
  refs:[sn("abudawud",4298,"Abū Dāwūd 4298"),sn("muslim",2897,"Muslim 2897"),sn("muslim","2937","Muslim 2937"),sn("bukhari",7118,"Al-Bukhārī 7118")]}
];
STATUS.forEach(s=>{
  INFO['st'+s.n] = {title:`${s.n} · ${s.name}`, src:[], cert:null, status:s, body:`<p>${s.rests}</p><p><b>Where, and how far.</b> ${s.where}</p>`, refs:s.refs};
});

/* ---------- extra named limits ---------- */
const LIMITS_NEW = [
  {id:"P", n:"Aswān", ll:[32.90,24.09], layer:"misr", src:["classical"], cert:"approx", body:`<p>Yāqūt on Miṣr: ${q("طولها من الشجرتين اللتين كانتا بين رفح والعريش إلى أسوان")}, "its length runs from the two trees that were between Rafaḥ and al-ʿArīsh to Aswān". Al-Iṣṭakhrī describes the cultivation as running from the limit of Aswān to the limit of Alexandria. Aswān is the southern end of Miṣr on both.</p>`, refs:["Yāqūt, Muʿjam al-Buldān, s.v. Miṣr","Al-Iṣṭakhrī, Diyār Miṣr"]}
];
LIMITS_NEW.forEach(l=>{ INFO['lim_'+l.id] = {title:`${l.id} · ${l.n}`, src:l.src, cert:l.cert, body:l.body, refs:l.refs}; });
