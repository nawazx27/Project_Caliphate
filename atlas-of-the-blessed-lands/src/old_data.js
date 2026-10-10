/* ---------------- geometry ---------------- */
const SHAM_CORE = [
  {c:"sea", p:[[34.25,31.29],[34.0,31.45],[34.6,32.6],[35.2,33.6],[35.6,34.8],[35.6,35.8],[35.75,36.3],[36.05,36.75],[36.2,36.95]]},
  {c:"approx", p:[[36.2,36.95],[36.6,37.15],[37.4,37.2],[37.95,37.05],[38.0,36.8],[38.1,36.45],[38.07,35.99],[37.6,36.05],[37.05,35.0],[36.85,34.2],[36.8,33.45],[36.95,32.45],[36.25,31.7],[35.95,30.9],[35.3,30.05],[34.8,30.6],[34.25,31.29]]}
];
const SHAM_OUTER = [
  {c:"sea", p:[[33.80,31.13],[33.3,31.4],[34.2,32.7],[34.75,33.7],[35.6,34.8],[35.6,35.8],[35.6,36.5],[35.3,36.45],[34.6,36.62]]},
  {c:"uncertain", p:[[34.6,36.62],[34.55,36.9],[34.9,37.3],[35.8,37.55],[36.95,37.75],[37.6,38.15],[38.3,38.45],[38.75,38.0],[38.55,37.5],[38.2,37.15],[38.0,36.85],[38.1,36.45],[38.07,35.99],[39.0,35.92],[40.1,35.3],[40.45,34.95],[41.2,34.45],[41.97,34.47],[41.2,33.3],[40.4,32.0],[39.87,29.81],[41.6,27.45],[38.54,27.63],[37.92,26.6],[36.6,26.25]]},
  {c:"sea", p:[[36.6,26.25],[36.2,26.3],[35.4,27.2],[34.8,28.0],[34.8,28.9],[34.92,29.45]]},
  {c:"approx", p:[[34.92,29.45],[34.6,29.9],[34.2,30.5],[33.80,31.13]]}
];
const HIJAZ_CORE = [
  {c:"sea", p:[[37.7,24.6],[37.85,24.0],[38.4,23.0],[38.9,21.9],[39.05,21.2],[39.45,20.85]]},
  {c:"approx", p:[[39.45,20.85],[40.0,20.85],[40.6,20.95],[40.95,21.45],[41.0,22.5],[40.95,23.8],[40.9,25.3],[40.75,26.1],[39.6,26.15],[38.9,25.6],[38.3,24.7],[37.7,24.6]]}
];
const HIJAZ_OUTER = [
  {c:"sea", p:[[34.92,29.45],[34.8,28.9],[34.8,28.0],[35.4,27.2],[36.3,26.0],[37.0,25.0],[37.85,24.0],[38.4,23.0],[38.9,21.9],[39.05,21.2],[39.8,20.0],[40.6,19.0],[41.2,18.4]]},
  {c:"uncertain", p:[[41.2,18.4],[42.0,18.9],[42.6,19.6],[42.3,20.3],[41.6,21.3],[41.4,22.4],[41.29,24.63],[41.59,25.55],[41.9,26.5],[41.6,27.45],[38.54,27.63],[36.57,28.38],[35.99,29.32],[34.92,29.45]]}
];
const FIL_CORE = [
  {c:"sea", p:[[34.25,31.29],[34.0,31.45],[34.45,32.2],[34.65,32.55],[34.9,32.53]]},
  {c:"approx", p:[[34.9,32.53],[35.18,32.57],[35.38,32.45],[35.45,32.1],[35.38,31.85],[35.37,31.5],[35.33,31.15],[35.1,30.95],[34.75,30.85],[34.45,30.95],[34.25,31.29]]}
];
const FIL_OUTER = [
  {c:"sea", p:[[33.80,31.13],[33.3,31.4],[34.45,32.2],[34.65,32.55],[34.9,32.53]]},
  {c:"approx", p:[[34.9,32.53],[35.18,32.57],[35.4,32.45]]},
  {c:"uncertain", p:[[35.4,32.45],[35.6,32.2],[36.05,32.0],[36.1,31.6],[35.95,31.2],[35.85,30.9],[35.75,30.4],[35.85,30.15],[35.4,29.75],[35.0,29.52],[34.9,29.49],[34.6,29.9],[34.2,30.5],[33.80,31.13]]}
];
const URDUNN = [
  {c:"sea", p:[[34.9,32.53],[34.65,32.6],[34.85,33.0],[35.0,33.35],[35.25,33.38]]},
  {c:"approx", p:[[35.25,33.38],[35.6,33.3],[35.85,33.2],[36.0,32.95],[36.05,32.55],[35.95,32.2],[35.7,32.15],[35.55,32.3],[35.4,32.45],[35.18,32.57],[34.9,32.53]]}
];
const JAZIRAH = [
  {c:"sea", p:[[34.85,29.45],[34.5,28.0],[35.6,26.6],[36.8,24.8],[38.3,22.0],[40.0,19.0],[41.4,16.5],[42.4,14.4],[43.3,12.6],[44.5,12.3],[47.0,12.9],[49.5,14.0],[52.0,15.2],[54.5,16.3],[56.5,17.6],[58.2,19.4],[59.4,21.4],[60.2,22.6],[59.2,23.6],[57.2,24.6],[56.7,25.6],[56.6,26.6],[55.5,25.9],[54.0,25.0],[52.2,26.2],[51.0,26.8],[50.3,27.0],[49.4,28.4],[48.6,29.4],[48.4,29.9]]},
  {c:"uncertain", p:[[48.4,29.9],[47.85,30.48],[46.3,31.05],[45.2,31.4],[44.35,31.7],[42.5,32.0],[40.0,32.4],[38.0,32.5],[37.3,31.9],[36.7,30.9],[36.3,29.95],[35.6,29.6],[34.85,29.45]]}
];
const YEMEN = [
  {c:"uncertain", p:[[40.6,19.4],[41.6,19.3],[43.0,19.0],[44.8,18.4],[46.8,17.8],[49.0,17.3],[51.4,16.8],[52.2,15.6]]},
  {c:"sea", p:[[52.2,15.6],[52.6,15.2],[49.5,13.6],[47.0,12.7],[44.5,12.2],[43.3,12.5],[42.4,14.3],[41.4,16.4],[40.6,19.4]]}
];
const LAVA = [
  {n:"Ḥarrat Rahat", at:[40.05,23.25], p:[[39.55,24.42],[39.75,24.45],[40.05,24.0],[40.30,23.2],[40.35,22.5],[40.15,22.05],[39.95,22.2],[39.80,22.9],[39.65,23.6],[39.50,24.1]]},
  {n:"Ḥarrat Khaybar", at:[40.25,25.75], p:[[39.6,25.3],[40.2,25.0],[40.9,25.5],[40.8,26.3],[40.1,26.5],[39.6,26.0]]},
  {n:"Ḥarrat al-Shām", at:[37.6,31.6], p:[[36.6,33.1],[37.0,33.0],[37.6,32.3],[38.3,31.6],[38.7,30.9],[38.4,30.6],[37.8,31.0],[37.1,31.8],[36.5,32.5]]},
  {n:"Ḥarrat ʿUwayriḍ", at:[37.75,27.1], p:[[37.3,27.6],[37.9,27.3],[38.2,26.9],[37.9,26.6],[37.4,27.0]]},
  {n:"Ḥarrat Kishb", at:[41.35,22.95], p:[[41.0,23.4],[41.6,23.3],[41.7,22.6],[41.2,22.5]]}
];
const AJNAD = [
  {id:"dimashq", name:"Jund Dimashq", ar:"جند دمشق", col:"--j3", at:[36.85,33.05],
   ring:[[34.9,33.35],[35.3,34.35],[35.75,34.35],[36.45,34.30],[37.50,34.00],[37.80,33.00],[37.30,32.00],[36.60,31.15],[35.75,31.10],[35.58,31.30],[35.55,31.75],[35.56,32.40],[35.86,32.18],[36.02,32.50],[35.92,32.90],[35.62,33.22],[35.25,33.32]],
   body:`<p>Its capital was Dimashq. It covered much of present-day Lebanon and, east of the Jordan, al-Balqāʾ around ʿAmmān.</p>`},
  {id:"hims", name:"Jund Ḥimṣ", ar:"جند حمص", col:"--j4", at:[37.7,34.95],
   ring:[[35.3,34.35],[35.2,35.0],[35.4,35.65],[36.2,35.75],[37.0,35.60],[38.0,35.70],[38.70,35.45],[39.00,34.60],[38.70,33.60],[37.80,33.00],[37.50,34.00],[36.45,34.30],[35.75,34.35]],
   body:`<p>Its capital was Ḥimṣ. It included Ḥamāh, Tadmur (Palmyra) in the desert, and part of the coast. Qinnasrīn was later carved out of its northern part.</p>`},
  {id:"qinnasrin", name:"Jund Qinnasrīn", ar:"جند قنسرين", col:"--j5", at:[37.45,36.35],
   ring:[[35.4,35.65],[35.6,36.1],[35.9,36.5],[36.3,36.95],[37.1,37.05],[37.95,36.95],[38.1,36.45],[38.08,36.00],[38.70,35.45],[38.0,35.70],[37.0,35.60],[36.2,35.75]],
   body:`<p>Created out of the northern part of Jund Ḥimṣ by Muʿāwiyah or by Yazīd b. Muʿāwiyah. Its capital was Qinnasrīn, later overshadowed by Ḥalab (Aleppo); it included Anṭākiyah and Manbij.</p><p>In 786 CE Hārūn al-Rashīd made its northern frontier into a separate province, <i>al-ʿAwāṣim wa al-Thughūr</i>, facing the Byzantines.</p>`}
];
const MAKKAH_HARAM = [[39.792,21.466],[39.86,21.495],[39.908,21.499],[39.955,21.492],[39.975,21.43],[39.952,21.358],[39.88,21.33],[39.815,21.315],[39.72,21.34],[39.665,21.449],[39.73,21.47]];
const MADINAH_HARAM = [[39.617,24.540],[39.665,24.520],[39.682,24.462],[39.645,24.405],[39.592,24.393],[39.540,24.425],[39.548,24.495]];
const AQSA_ENCL = [[35.2336,31.7804],[35.2371,31.7803],[35.2368,31.7756],[35.2340,31.7755]];
const AQSA_PTS = [{n:"Qubbat al-Ṣakhrah", ll:[35.2354,31.7780], a:"r"},{n:"al-Jāmiʿ al-Qiblī", ll:[35.2361,31.7762], a:"r"}];

const MIQATS = [
  {n:"Dhū al-Ḥulayfah", s:"for Madinah · today Abyār ʿAlī", ll:[39.543,24.414], a:"l"},
  {n:"al-Juḥfah", s:"for al-Shām · near Rābigh", ll:[39.14,22.70], a:"l"},
  {n:"Qarn al-Manāzil", s:"for Najd · today al-Sayl al-Kabīr", ll:[40.43,21.63], a:"r"},
  {n:"Yalamlam", s:"for Yemen · near al-Saʿdiyyah", ll:[39.86,20.53], a:"r"},
  {n:"Dhāt ʿIrq", s:"for Iraq", ll:[40.45,21.95], a:"r"}
];
const ROUTES = {
  summer:{cls:"trade", info:"quraysh", name:"Summer journey to al-Shām", pts:[[39.826,21.4225],[39.37,21.95],[39.14,22.70],[38.79,23.78],[38.45,24.6],[37.92,26.61],[37.95,26.79],[36.57,28.38],[35.73,30.19],[35.95,31.25],[36.48,32.52]]},
  summerGaza:{cls:"trade", info:"quraysh", name:"Summer journey, branch to Ghazzah", pts:[[35.73,30.19],[35.3,30.55],[34.85,31.0],[34.47,31.50]]},
  winter:{cls:"trade", info:"quraysh", name:"Winter journey to Yemen", pts:[[39.826,21.4225],[40.42,21.27],[41.63,21.21],[42.25,19.97],[42.70,18.15],[43.76,16.94],[44.19,15.37]]},
  zubaydah:{cls:"hajj", info:"hajj", name:"Darb Zubaydah (Kūfah to Makkah)", pts:[[44.40,32.03],[44.0,31.0],[43.613,29.625],[43.562,29.399],[42.522,27.120],[41.587,25.545],[41.290,24.631],[40.834,22.195],[40.45,21.95],[39.826,21.4225]]},
  zubaydahMadinah:{cls:"hajj", info:"hajj", name:"Darb Zubaydah, branch to Madinah", pts:[[41.587,25.545],[40.6,25.0],[39.611,24.467]]},
  shami:{cls:"hajj", info:"hajj", name:"Syrian Hajj road (Damascus to Madinah)", pts:[[36.29,33.51],[36.10,32.62],[36.09,32.07],[36.04,31.25],[35.73,30.19],[36.0,29.32],[36.57,28.38],[37.95,26.79],[37.92,26.61],[38.6,25.4],[39.611,24.467]]},
  madinahMakkah:{cls:"hajj", info:"hajj", name:"Madinah to Makkah road", pts:[[39.611,24.467],[39.543,24.414],[39.25,23.9],[38.79,23.78],[39.14,22.70],[39.37,21.95],[39.826,21.4225]]},
  misri:{cls:"hajj", info:"hajj", name:"Egyptian Hajj road (later coastal course)", pts:[[31.24,30.04],[32.45,30.05],[33.75,29.91],[35.0,29.53],[34.94,29.29],[35.48,27.68],[36.47,26.24],[37.27,25.05],[38.06,24.09],[38.79,23.78],[39.03,22.80],[39.37,21.95],[39.826,21.4225]]}
};
const STATIONS = [
  ["Zabālah",43.562,29.399,"r",2.2,"hajj"],["Fayd",42.522,27.120,"r",1.6,"hajj"],["al-Nuqrah",41.587,25.545,"r",2.2,"hajj"],["al-Rabadhah",41.290,24.631,"r",2.2,"hajj"],
  ["Maʿān",35.73,30.19,"l",2,"hajj"],["Darʿā",36.10,32.62,"l",3,"hajj"],["Nakhl",33.75,29.91,"r",2.2,"hajj"],["al-Muwayliḥ",35.48,27.68,"r",2.4,"hajj"],["al-Wajh",36.47,26.24,"r",2.2,"hajj"],
  ["Tabālah",42.25,19.97,"r",2.4,"trade"],["Jurash",42.70,18.15,"r",2.4,"trade"],["Ṣaʿdah",43.76,16.94,"r",2,"trade"],["ʿUsfān",39.37,21.95,"l",4,"hajj"]
];
const SITES = [
  {id:"hira", n:"Ghār Ḥirāʾ", s:"Jabal al-Nūr", ll:[39.8592,21.4575], a:"r", k:20, cert:"firm",
   body:`<p>The cave on Jabal al-Nūr where revelation began. In the hadith of ʿĀʾishah رضي الله عنها in al-Bukhārī, the Prophet ﷺ used to retreat to Ḥirāʾ, and the first revelation, ${q("اقْرَأْ بِاسْمِ رَبِّكَ الَّذِي خَلَقَ")} (al-ʿAlaq 96:1), came to him there.</p>`, src:["rev"]},
  {id:"thawrm", n:"Ghār Thawr", s:"cave of the Hijrah", ll:[39.8506,21.3772], a:"l", k:20, cert:"firm",
   body:`<p>Al-Tawbah 9:40 mentions the Prophet ﷺ and his companion ${q("إِذْ هُمَا فِي الْغَارِ")}, "when they were in the cave". The sīrah and hadith identify the cave as the one on Jabal Thawr south of Makkah, where he ﷺ and Abū Bakr رضي الله عنه hid at the start of the Hijrah. This Thawr is different from the Thawr that bounds Madinah's ḥaram.</p>`, src:["rev","early"]},
  {id:"quba", n:"Qubāʾ", s:"first masjid of the Hijrah", ll:[39.6172,24.4393], a:"l", k:18, cert:"firm",
   body:`<p>The masjid built at Qubāʾ when the Prophet ﷺ arrived on the Hijrah, south of Madinah and inside its ḥaram.</p>`, src:["early"]},
  {id:"badr", n:"Badr", s:"2 AH", ll:[38.7908,23.7816], a:"r", k:2, cert:"firm",
   body:`<p>Āl ʿImrān 3:123: ${q("وَلَقَدْ نَصَرَكُمُ اللَّهُ بِبَدْرٍ")}, "And already had Allah given you victory at [the battle of] Badr" (Saheeh International). The wells of Badr lay on the coastal road used by the Makkan caravans to and from al-Shām.</p>`, src:["rev"]},
  {id:"hijr", n:"al-Ḥijr", s:"Hegra · Madāʾin Ṣāliḥ", ll:[37.9532,26.7919], a:"r", k:1.8, cert:"firm",
   body:`<p>Al-Ḥijr 15:80: ${q("وَلَقَدْ كَذَّبَ أَصْحَابُ الْحِجْرِ الْمُرْسَلِينَ")}. Al-Baghawī explains al-Ḥijr as the city of Thamūd, the people of Ṣāliḥ عليه السلام, between Madinah and al-Shām. It is identified with Hegra (Madāʾin Ṣāliḥ) near al-ʿUlā, on the road the Prophet ﷺ took to Tabūk.</p>`, src:["rev","early"]},
  {id:"madyan", n:"Madyan", s:"traditional site, uncertain", ll:[35.01,28.49], a:"r", k:2.2, cert:"uncertain",
   body:`<p>Al-Aʿrāf 7:85: ${q("وَإِلَىٰ مَدْيَنَ أَخَاهُمْ شُعَيْبًا")}, "And to [the people of] Madyan [We sent] their brother Shuʿayb" (Saheeh International). The Qur'an does not give the location. It is traditionally identified with al-Badʿ (Maghāʾir Shuʿayb) in north-west Arabia, a station on the early Egyptian Hajj road; this rests on later tradition.</p>`, src:["rev","classical"]},
  {id:"mutah", n:"Muʾtah", s:"8 AH", ll:[35.7036,31.0628], a:"r", k:3, cert:"firm",
   body:`<p>Site of the expedition of 8 AH in which Zayd b. Ḥārithah, Jaʿfar b. Abī Ṭālib and ʿAbdullāh b. Rawāḥah رضي الله عنهم were killed (al-Bukhārī). It lies south of al-Karak in present-day Jordan.</p>`, src:["early"]},
  {id:"busra", n:"Buṣrā", s:"Bostra", ll:[36.4815,32.5186], a:"r", k:2.2, cert:"firm",
   body:`<p>A market town at the southern edge of al-Shām where caravans from the Ḥijāz arrived. It appears in sīrah reports of the Prophet's ﷺ journeys to al-Shām before prophethood; scholars have assessed some of those reports differently.</p>`, src:["early"]},
  {id:"yarmuk", n:"al-Yarmūk", s:"15 AH · site approximate", ll:[35.95,32.78], a:"r", k:3.5, cert:"approx",
   body:`<p>The battle near the Yarmūk river in 15 AH (636 CE) that opened al-Shām to the Muslims in the time of ʿUmar رضي الله عنه. The exact battlefield is approximate.</p>`, src:["early"]},
  {id:"aqiq", n:"Wādī al-ʿAqīq", s:"\"this blessed valley\"", ll:[39.575,24.47], a:"l", k:30, cert:"firm",
   body:`<p>ʿUmar رضي الله عنه heard the Prophet ﷺ say, while in Wādī al-ʿAqīq, that a messenger from his Lord had come to him that night and told him to pray "in this blessed valley" (al-Bukhārī 1534). The hadith names the valley west of Madinah, not its limits.</p>`, src:["rev"]},
  {id:"wajj", n:"Wajj", s:"ḥaram status disputed", ll:[40.40,21.25], a:"l", k:4, cert:"uncertain",
   body:`<p>Abū Dāwūd 2032 (al-Zubayr) reports the Prophet ﷺ declared the game and thorn trees of Wajj, the valley of al-Ṭāʾif, forbidden; al-Albānī grades it ḍaʿīf. Ibn Taymiyyah رحمه الله called it the only third place whose ḥaram status was disputed: al-Shāfiʿī accepted the report, while most scholars did not.</p>`, src:["classical"]}
];

/* ---------------- info texts ---------------- */
const INFO = {
  intro:{title:"How to use this map", src:[], cert:null, body:`<p>Drag to move; pinch or scroll to zoom. Tap any shaded region, line, marker or country to read where it comes from and how certain it is.</p><p>The small maps under the main map show the two ḥarams and the ring of mīqāts at full detail; tap one to fly there. Use <b>Go to</b> for other places.</p><p>Turn on the caravan and Hajj roads, the ajnād, and the five early views of <i>al-arḍ al-muqaddasah</i> from the layer list.</p>`},
  makkah:{title:"Ḥaram of Makkah", ar:"حرم مكة", src:["rev","early","classical"], cert:"approx", body:`
    <p>That Makkah is a ḥaram is established by revelation and agreed on by the Muslims. The Qur'an speaks of the Lord of this city ${q("الَّذِي حَرَّمَهَا")}, "who made it sacred" (al-Naml 27:91), and says ${q("وَمَن دَخَلَهُ كَانَ آمِنًا")}, "whoever enters it shall be safe" (Āl ʿImrān 3:97). In an authentic hadith the Prophet ﷺ said that Allah made Makkah sacred on the day He created the heavens and the earth.</p>
    <p>Its limits are known from boundary markers on the roads into Makkah. Historical reports say Ibrāhīm عليه السلام first set them up and that they were renewed in the Prophet's ﷺ time and after; how authentic each report is, is a separate question.</p>
    <p>Al-Nawawī gives the limits in mīl: al-Tanʿīm, at the houses of Banū Nifār, 3; the Yemen road at Aḍāt Libn, 7; the Ṭāʾif road at Baṭn Namirah facing ʿArafāt, 7; the Iraq road at the pass of al-Maqṭaʿ, 7; the al-Jiʿrānah road at Shiʿb Āl ʿAbdillāh b. Khālid, 9; and the Jeddah road at Munqaṭaʿ al-Aʿshāsh, 10. ʿArafah is outside the ḥaram; Minā and Muzdalifah are inside it. The points are placed approximately and the line between them is interpolated.</p>`,
    refs:["Qur'an, al-Naml 27:91; Āl ʿImrān 3:96–97","Al-Bukhārī and Muslim: Makkah made sacred by Allah (khuṭbah at the conquest)",`Al-Nawawī, al-Majmūʿ, quoted in <a href="https://www.islamweb.net/ar/fatwa/71668/" target="_blank" rel="noopener">Islamweb fatwa 71668</a>`]},
  madinah:{title:"Ḥaram of Madinah", ar:"حرم المدينة", src:["rev"], cert:"approx", body:`
    <p>The Prophet ﷺ declared Madinah a ḥaram. He said that Ibrāhīm عليه السلام made Makkah sacred and that he ﷺ made Madinah sacred, and he prayed for Madinah to be given double the blessing given to Makkah.</p>
    <p>The Sunnah itself names its limits: ${q("الْمَدِينَةُ حَرَمٌ مَا بَيْنَ عَيْرٍ إِلَى ثَوْرٍ")}, "Madinah is a ḥaram from ʿAyr to Thawr" (hadith of ʿAlī رضي الله عنه), and between its two <i>lābah</i>s, the black lava fields to the east and west (hadith of Abū Hurayrah رضي الله عنه). ʿAyr lies about 8.5 km south of the Prophet's Masjid and Thawr about 8 km north.</p>
    <p>Some scholars questioned whether a mountain called Thawr exists at Madinah, since the famous Thawr is in Makkah; others identified a small hill of that name behind Uḥud. Most scholars hold Madinah to be a ḥaram in the legal sense; the Ḥanafī school is reported to differ (I did not re-check each school's position). The outline is approximate, and drawn by hand between the named landmarks.</p>
    <p>Around it lies a wider <i>ḥimā</i>, a protected pasture: in Muslim 1372 Abū Hurayrah رضي الله عنه says the Prophet ﷺ made twelve mīl around Madinah a <i>ḥimā</i>. The hadith gives the distance, not a line, so the map draws a dotted ring of twelve mīl around the Prophet's Masjid, taking a mīl as about 1.85 km (about 22 km in all; the length of the mīl is an estimate).</p>`,
    refs:[`Al-Bukhārī 6755, Muslim 1370: "from ʿAyr to Thawr" (al-Bukhārī 1870 has the same ʿAyr but leaves the second place unnamed; <a href="https://dorar.net/hadith/sharh/2171" target="_blank" rel="noopener">dorar.net</a>)`,"Al-Bukhārī and Muslim: \"between its two lava fields\" (Abū Hurayrah)",`<a href="https://sunnah.com/muslim:1372b" target="_blank" rel="noopener">Muslim 1372</a>: twelve mīl around Madinah made a ḥimā (Abū Hurayrah)`,"Al-Bukhārī and Muslim: Ibrāhīm made Makkah sacred, and I made Madinah sacred","Ibn Taymiyyah, Majmūʿ al-Fatāwā 27/14–15"]},
  aqsa:{title:"al-Masjid al-Aqṣā", ar:"المسجد الأقصى", src:["rev","early"], cert:"firm", body:`
    <p>Named in al-Isrāʾ 17:1 as the masjid ${q("الَّذِي بَارَكْنَا حَوْلَهُ")}, "whose surroundings We have blessed". Al-Baghawī explains the blessing as rivers, trees and fruit, and reports from Mujāhid that it is the dwelling place of the prophets and the place where revelation and the angels descended.</p>
    <p>It is one of the three masjids to which a journey may be made for worship. Many scholars apply the name to the whole walled enclosure, not only the prayer hall at its southern end; the small outline shows that enclosure when you zoom in.</p>
    <p>No ḥaram boundary is drawn around Jerusalem. Ibn Taymiyyah رحمه الله wrote that there is no place called a ḥaram at Bayt al-Maqdis or at the tomb of Ibrāhīm; the ḥaram is where Allah forbade hunting and cutting vegetation. He named only Makkah, Madinah, and Wajj near al-Ṭāʾif, whose report al-Shāfiʿī accepted and most scholars did not.</p>`,
    refs:["Qur'an, al-Isrāʾ 17:1; tafsir of al-Baghawī","Al-Bukhārī and Muslim: travel for worship only to the three masjids",`Ibn Taymiyyah, Majmūʿ al-Fatāwā 26/118 (<a href="https://islamqa.info/ar/answers/5419" target="_blank" rel="noopener">islamqa.info</a>) and 27/14–15 (<a href="https://islamqa.info/ar/34751" target="_blank" rel="noopener">islamqa.info</a>)`]},
  muq:{title:"al-Arḍ al-Muqaddasah", ar:"الأرض المقدسة", src:["rev","early"], cert:"uncertain", body:`
    <p>In al-Māʾidah 5:21 Mūsā عليه السلام tells his people: ${q("ادْخُلُوا الْأَرْضَ الْمُقَدَّسَةَ")}, "enter the blessed land [i.e., Palestine]" (Saheeh International; the bracket is the translators' gloss, not in the Arabic; "the Holy Land" is this atlas's own name for <i>al-arḍ al-muqaddasah</i>). The verse names the land but does not mark its extent. Mujāhid explained <i>al-muqaddasah</i> as "the blessed".</p>
    <p>Al-Ṭabarī records these answers:</p>
    <ul>
      <li><b>Mujāhid, and Ibn ʿAbbās:</b> al-Ṭūr and what surrounds it. The reports do not say which mountain, so it is not drawn.</li>
      <li><b>Qatādah:</b> al-Shām.</li>
      <li><b>Ibn ʿAbbās (via ʿIkrimah), al-Suddī, Ibn Zayd:</b> Arīḥāʾ (Jericho).</li>
      <li><b>An unattributed view</b> (al-Baghawī gives it to al-Kalbī): Dimashq, Filasṭīn and part of al-Urdunn.</li>
    </ul>
    <p>Al-Ṭabarī's own verdict: it cannot be pinned to one land without a sound report, but all the commentators and historians agree it lies somewhere ${q("ما بين الفرات وعريش مصر")}, between the Euphrates and al-ʿArīsh of Egypt. Al-Baghawī adds al-Ḍaḥḥāk's view: Īliyāʾ and Bayt al-Maqdis.</p>`,
    refs:["Qur'an, al-Māʾidah 5:21","Tafsir of al-Ṭabarī and of al-Baghawī on 5:21"]},
  tuwa:{title:"The valley of Ṭuwā and Mount Sinai", ar:"الوادي المقدس طوى · طور سينين", src:["rev","classical"], cert:"uncertain", body:`
    <p>Ṭā Hā 20:12: ${q("إِنَّكَ بِالْوَادِ الْمُقَدَّسِ طُوًى")}, "you are in the blessed valley of Ṭuwā" (Saheeh International, which renders the same Arabic "sacred valley" in al-Nāziʿāt 79:16). Al-Baghawī glosses <i>al-muqaddas</i> as "purified" and says Ṭuwā is the valley's name. Al-Qaṣaṣ 28:30 speaks of ${q("الْبُقْعَةِ الْمُبَارَكَةِ")}, "a blessed spot", and al-Tīn 95:2 swears by ${q("طُورِ سِينِينَ")}.</p>
    <p>The Qur'an does not give the location. The marker shows the traditional identification at Jabal Mūsā in southern Sinai. That identification rests on later tradition, and other sites have been proposed.</p>`,
    refs:["Qur'an, Ṭā Hā 20:12; al-Qaṣaṣ 28:30; al-Tīn 95:2","Tafsir of al-Baghawī on 20:12"]},
  sham:{title:"Bilād al-Shām", ar:"بلاد الشام", src:["rev","early","classical"], cert:"approx", body:`
    <p>Revelation praises this land without drawing its edges. Al-Baghawī explains ${q("الْأَرْضِ الَّتِي بَارَكْنَا فِيهَا")} in al-Anbiyāʾ 21:71 and 21:81 as al-Shām, and the blessed villages of Sabaʾ 34:18 as its villages. The Prophet ﷺ prayed, ${q("اللَّهُمَّ بَارِكْ لَنَا فِي شَامِنَا وَفِي يَمَنِنَا")} (al-Bukhārī 1037). The word al-Shām itself does not occur in the Qur'an.</p>
    <p><b>Solid core:</b> the settled lands every major source includes, roughly Abū al-Fidāʾ's line from Rafaḥ, between al-Shawbak and Aylah, along al-Balqāʾ, east of Ṣarkhad and the Ghūṭah, by Salamiyyah and east of Aleppo to Bālis on the Euphrates.</p>
    <p><b>Hatched edges:</b> land some sources add. Ibn Ḥawqal makes the eastern edge the desert ${q("من أيلة إلى الفرات")} and counts the Byzantine frontier fortresses (<i>al-thughūr</i>) as al-Shām. Yāqūt gives its length from the Euphrates to al-ʿArīsh and its width from the two mountains of Ṭayyiʾ to the Mediterranean. Al-Balādhurī reports that ʿUmar counted Taymāʾ and Wādī al-Qurā as al-Shām. Tap the lettered badges for each source's words.</p>`,
    refs:["Qur'an, al-Anbiyāʾ 21:71, 21:81; Sabaʾ 34:18; tafsir of al-Baghawī","Al-Bukhārī 1037",`Ibn Ḥawqal and Abū al-Fidāʾ in <a href="https://ar.wikisource.org/wiki/%D9%85%D8%AC%D9%84%D8%A9_%D8%A7%D9%84%D9%85%D9%82%D8%AA%D8%A8%D8%B3/%D8%A7%D9%84%D8%B9%D8%AF%D8%AF_70/%D8%A8%D9%8A%D9%86_%D8%A7%D9%84%D9%81%D9%8A%D8%AD%D8%A7%D8%A1_%D9%88%D8%A7%D9%84%D8%B4%D9%87%D8%A8%D8%A7%D8%A1" target="_blank" rel="noopener">al-Muqtabas no. 70</a>`,"Yāqūt, Muʿjam al-Buldān, s.v. al-Shām"]},
  seam:{title:"Where al-Shām meets al-Ḥijāz", ar:"آخر الشام وأول الحجاز", src:["early","classical"], cert:"uncertain", body:`
    <p>The seam between the two regions is a band, not a line, and the map shows it as the place where the two hatchings cross.</p>
    <ul><li><b>ʿUmar (al-Balādhurī):</b> Taymāʾ and Wādī al-Qurā are in al-Shām; what lies below Wādī al-Qurā to Madinah is al-Ḥijāz. This fits al-Bukhārī 2338, where ʿUmar moved the Jews of Khaybar out of al-Ḥijāz to Taymāʾ and Arīḥāʾ.</li>
    <li><b>Al-Ḥāzimī (via Yāqūt):</b> Sargh, north of Tabūk, is "the first of al-Ḥijāz and the last of al-Shām".</li>
    <li><b>Hishām b. al-Kalbī:</b> al-Ḥijāz runs between the two mountains of Ṭayyiʾ and the Iraq road.</li>
    <li><b>Ibrāhīm al-Ḥarbī (via Yāqūt):</b> Tabūk and Filasṭīn are of al-Ḥijāz. An outlier, not drawn.</li></ul>
    <p>Each reading reflects its author's time; the map shows them overlapping rather than choosing.</p>`,
    refs:[`Al-Balādhurī, Futūḥ al-Buldān (<a href="https://www.islamweb.net/ar/library/content/200/17435/" target="_blank" rel="noopener">Islamweb</a>)`,`Yāqūt, Muʿjam al-Buldān, s.v. al-Ḥijāz (<a href="https://www.islamic-content.com/t/5632" target="_blank" rel="noopener">text</a>) and s.v. Sargh`]},
  ajnad:{title:"The other ajnād of al-Shām", ar:"أجناد الشام", src:["early","classical"], cert:"uncertain", body:`
    <p>Between 637 and 640 CE, in the time of ʿUmar رضي الله عنه, al-Shām was organised into four military and administrative districts called <i>ajnād</i>: Filasṭīn, al-Urdunn, Dimashq and Ḥimṣ. When ʿUmar reached Sargh, "the commanders of the ajnād" met him (al-Bukhārī and Muslim), so the districts existed in the Companions' time. Qinnasrīn was carved out of Ḥimṣ under Muʿāwiyah or Yazīd, and Hārūn al-Rashīd later made the northern frontier a separate province.</p>
    <p>Filasṭīn and al-Urdunn have their own layer. This layer adds Dimashq, Ḥimṣ and Qinnasrīn, whose borders shifted over time and are drawn only schematically.</p>`,
    refs:[`<a href="https://en.wikipedia.org/wiki/Bilad_al-Sham" target="_blank" rel="noopener">Bilād al-Shām</a> (Wikipedia, citing al-Balādhurī and others)`]},
  filastin:{title:"Filasṭīn and al-Urdunn", ar:"جند فلسطين وجند الأردن", src:["early","classical"], cert:"approx", body:`
    <p>The name Filasṭīn does not occur in the Qur'an. Early usage treats it as a named part inside al-Shām: Ibn Isḥāq says Ibrāhīm عليه السلام went "to al-Shām and settled at al-Sabʿ, of the land of Filasṭīn" (quoted by al-Baghawī on 21:71).</p>
    <p><b>Solid core (Jund Filasṭīn):</b> from Rafaḥ in the south to al-Lajjūn in the north, west of the Jordan valley: al-Ramlah, Bayt al-Maqdis, Ghazzah, ʿAsqalān, Yāfā, Qaysāriyyah, Nābulus and Bayt Jibrīn. Its capital was Ludd, then al-Ramlah, founded around 715 CE.</p>
    <p><b>Hatched edges:</b> land some sources or periods add: the Negev down to Aylah, the Rafaḥ–al-ʿArīsh coast, and east of the Jordan the mountains of Edom (al-Sharāh), Zughar and, in the Fatimid period, ʿAmmān.</p>
    <p><b>Jund al-Urdunn</b> (blue) held Galilee, Ṭabariyyah, Baysān, ʿAkkā and Ṣūr. The modern Mandate border of Palestine took in this Galilee, which the old Filasṭīn did not, and left out the east-bank lands.</p>`,
    refs:[`<a href="https://en.wikipedia.org/wiki/Jund_Filastin" target="_blank" rel="noopener">Jund Filasṭīn</a> (Wikipedia, citing al-Balādhurī, Le Strange and others)`,"Al-Baghawī on al-Anbiyāʾ 21:71 (Ibn Isḥāq)"]},
  hijaz:{title:"al-Ḥijāz", ar:"الحجاز", src:["early","classical"], cert:"approx", body:`
    <p>The word does not occur in the Qur'an; its root appears only as <i>ḥājiz</i>, a barrier. Hishām b. al-Kalbī: ${q("سمي حجازا لأنه حجز بين تهامة ونجد")}, "it is called al-Ḥijāz because it bars Tihāmah from Najd". In that strict sense it is the mountain chain itself, and al-Aṣmaʿī says ${q("فمكة تهامية والمدينة حجازية والطائف حجازية")}: Makkah is Tihāmī, Madinah and al-Ṭāʾif Ḥijāzī.</p>
    <p><b>Solid core:</b> what every broad usage includes: Makkah, al-Ṭāʾif, Madinah, Yanbuʿ, Khaybar and Fadak.</p>
    <p><b>Hatched edges:</b> al-Aṣmaʿī stretches it ${q("من تخوم صنعاء من العبلاء وتبالة إلى تخوم الشام")}, from the marches of Ṣanʿāʾ at al-ʿAblāʾ and Tabālah to the marches of al-Shām. Hishām b. al-Kalbī bounds it between the two mountains of Ṭayyiʾ and the Iraq road. In the north it overlaps al-Shām between Wādī al-Qurā and Sargh.</p>
    <p>For the narrower legal definition, turn on the jurists' layer.</p>`,
    refs:[`Yāqūt, Muʿjam al-Buldān, s.v. al-Ḥijāz (<a href="https://www.islamic-content.com/t/5632" target="_blank" rel="noopener">text</a>)`]},
  hijazfiqh:{title:"al-Ḥijāz in the jurists' definition", ar:"الحجاز عند الفقهاء", src:["rev","classical"], cert:"uncertain", body:`
    <p>This layer matters for one ruling: where non-Muslims may not settle permanently. The Prophet ﷺ commanded that the <i>mushrikūn</i> be expelled from Jazīrat al-ʿArab (al-Bukhārī and Muslim). In al-Bukhārī 2338, ʿUmar رضي الله عنه expelled the Jews and Christians from the land of al-Ḥijāz and moved the Jews of Khaybar to Taymāʾ and Arīḥāʾ (Jericho), which shows he did not count those two places as within it.</p>
    <p>The jurists differed on how far the ruling reaches. Some restricted it to al-Ḥijāz; al-Shāfiʿī is reported to have defined that as Makkah, Madinah, al-Yamāmah and their districts, and Aḥmad as a list that adds Khaybar, Yanbuʿ and Fadak. Others applied it to all of Jazīrat al-ʿArab. <span class="fine">These definitions come from the earlier atlas; the jurists' own texts were not re-read.</span></p>
    <p>The circles mark these places only. The sources do not give the size of each district, so the circle sizes are illustrative.</p>`,
    refs:["Al-Bukhārī 3053, Muslim 1637: expel the mushrikūn from Jazīrat al-ʿArab (Ibn ʿAbbās)",`<a href="https://sunnah.com/bukhari:2338" target="_blank" rel="noopener">Al-Bukhārī 2338</a>: ʿUmar moves the Jews of Khaybar to Taymāʾ and Arīḥāʾ`]},
  jazirah:{title:"Jazīrat al-ʿArab", ar:"جزيرة العرب", src:["rev","classical"], cert:"uncertain", body:`
    <p>Named in the authentic Sunnah, for example in the command to expel the <i>mushrikūn</i> from it (al-Bukhārī and Muslim). It is bounded by the Red Sea, the Arabian Sea and the Gulf on three sides.</p>
    <p>On land the classical definitions differ. Yāqūt cites al-Aṣmaʿī for its length, from the far end of ʿAdan Abyan to the countryside of Iraq, and its breadth, from Juddah and the sea coast beyond it to the edges of al-Shām; and al-Haytham b. ʿAdī for its running from al-ʿUdhayb on the edge of Iraq to Ḥaḍramawt. Others describe its northern edge as the farmland of Iraq and the fringes of al-Shām.</p>
    <p>The seaward sides are firm. The northern edge is dotted because the sources describe it differently.</p>`,
    refs:["Yāqūt, Muʿjam al-Buldān, s.v. Jazīrat al-ʿArab (al-Aṣmaʿī; al-Haytham b. ʿAdī)","Al-Bukhārī 3053, Muslim 1637"]},
  yemen:{title:"al-Yaman", ar:"اليمن", src:["rev","classical"], cert:"uncertain", body:`
    <p>The Prophet ﷺ prayed for blessing on al-Yaman together with al-Shām (al-Bukhārī 1037), and Yalamlam is the mīqāt he fixed for its people.</p>
    <p>Classical usage applied the name to the south-west of Arabia. Whether it included regions such as Ḥaḍramawt and Najrān varied between authors, and its northern limit against Tihāmah and al-Ḥijāz is not fixed. The outline is a rough indication only.</p>`,
    refs:["Al-Bukhārī 1037"]},
  miqat:{title:"The mīqāts", ar:"المواقيت", src:["rev","early","modern"], cert:"approx", body:`
    <p>Ibn ʿAbbās رضي الله عنهما reported that the Prophet ﷺ fixed Dhū al-Ḥulayfah for the people of Madinah, al-Juḥfah for al-Shām, Qarn al-Manāzil for Najd and Yalamlam for Yemen, and said: ${q("هُنَّ لَهُنَّ وَلِمَنْ أَتَى عَلَيْهِنَّ مِنْ غَيْرِ أَهْلِهِنَّ")}, "they are for them and for those who come to them from elsewhere".</p>
    <p>Dhāt ʿIrq, for the people of Iraq, was fixed by ʿUmar رضي الله عنه according to al-Bukhārī (1531). Some reports attribute it to the Prophet ﷺ himself; I did not re-check those reports here.</p>
    <p>Today pilgrims use Abyār ʿAlī for Dhū al-Ḥulayfah; Rābigh, about 17 km from the old site, in place of al-Juḥfah; al-Sayl al-Kabīr for Qarn al-Manāzil, with Wādī Muḥrim at its upper end; and al-Saʿdiyyah for Yalamlam. Note that the mīqāt of the people of al-Shām lies inside al-Ḥijāz. Positions are approximate.</p>`,
    refs:["Al-Bukhārī 1524, Muslim 1181 (Ibn ʿAbbās)","Al-Bukhārī 1531 (ʿUmar and Dhāt ʿIrq)",`Present-day sites: <a href="https://saudipedia.com/en/mawaqit-al-ihram" target="_blank" rel="noopener">Saudipedia</a>`]},
  quraysh:{title:"The journeys of winter and summer", ar:"رحلة الشتاء والصيف", src:["rev","early"], cert:"approx", body:`
    <p>Quraysh 106:1–2: ${q("لِإِيلَافِ قُرَيْشٍ ۝ إِيلَافِهِمْ رِحْلَةَ الشِّتَاءِ وَالصَّيْفِ")}. Al-Baghawī gives two explanations. Ibn ʿAbbās رضي الله عنهما (through ʿIkrimah and Saʿīd b. Jubayr) said they wintered in Makkah and summered in al-Ṭāʾif. Others said they made two trading journeys a year: in winter to Yemen, because it is warmer, and in summer to al-Shām.</p>
    <p>The map draws the second explanation. Al-Baghawī also mentions Tabālah and Jurash in the lands of Yemen. For Sabaʾ 34:18 he describes a chain of villages along the trade road from Yemen to al-Shām. Ghazzah and Buṣrā appear in sīrah reports as destinations of the Makkan caravans.</p>
    <p>The courses are approximate: the highland road south through al-Ṭāʾif, Tabālah and Jurash, and the road north past Badr, Wādī al-Qurā, al-Ḥijr and Tabūk.</p>`,
    refs:["Qur'an, Quraysh 106:1–2; Sabaʾ 34:18","Tafsir of al-Baghawī on 106:2 and 34:18"]},
  hajj:{title:"The old Hajj roads", ar:"طرق الحج القديمة", src:["classical","modern"], cert:"approx", body:`
    <p><b>Darb Zubaydah</b> ran about 1,300 km from al-Kūfah to Makkah, with some 27 main stations about 50 km apart. It was developed in the Abbasid period and named after Zubaydah, wife of Hārūn al-Rashīd. Fayd marked the halfway point, and a branch to Madinah left near al-Nuqrah.</p>
    <p><b>The Syrian road</b> ran from Damascus through Buṣrā and Adhruʿāt (Darʿā), Maʿān, Tabūk, al-Ḥijr and al-ʿUlā to Madinah. <b>The Egyptian road</b> crossed Sinai to Aylah; one course then went by Ḥaql and Madyan inland to Madinah, while the later course followed the Red Sea coast by al-Muwayliḥ, al-Wajh, Yanbuʿ and Rābigh. <b>The Yemeni highland road</b> came north by Ṣaʿdah, Bīshah, Tabālah and Turabah.</p>
    <p>These roads are later history, not revelation. Courses between stations are approximate.</p>`,
    refs:[`<a href="https://saudipedia.com/en/historical-hajj-routes-list" target="_blank" rel="noopener">Saudipedia: historical Hajj routes</a>`,`<a href="https://en.wikipedia.org/wiki/Zubaydah_Trail" target="_blank" rel="noopener">Zubaydah Trail</a>`]},
  lava:{title:"Lava fields (ḥarrah)", ar:"الحرار", src:["rev","modern"], cert:"approx", body:`
    <p>Western Arabia is scattered with black basalt lava fields. Madinah's ḥaram is defined in the Sunnah partly by two of them: its eastern and western <i>lābah</i>s. Ḥarrat Rahat stretches south from Madinah toward Makkah; Ḥarrat al-Shām lies across the desert edge of al-Shām.</p>
    <p>The outlines are approximate and drawn only for orientation.</p>`},
  modern:{title:"Modern borders", src:["modern"], cert:"firm", body:`
    <p>Present-day international borders from the Natural Earth dataset, drawn as de facto lines. They are here only for comparison and say nothing about the classical regions.</p>
    <p>Several are disputed or not universally recognised: the status of Jerusalem, the West Bank and Gaza; the Golan Heights, which Israel has administered since 1967 and most states regard as Syrian territory; and Hatay (Antakya), long claimed by Syria.</p>`}
};
SITES.forEach(s=>{ if(!s.info) INFO['site_'+s.id] = {title:s.n, src:s.src, cert:s.cert, body:s.body}; });
const LIMITS = [
  {id:"A", n:"al-ʿArīsh", ll:[33.80,31.13], layer:"sham", src:["classical","early"], cert:"approx", body:`<p>${q("وأما حدها فمن الفرات إلى العريش المتاخم للديار المصرية")}: "its length runs from the Euphrates to al-ʿArīsh, which borders Egypt" (Yāqūt on al-Shām). Al-Ṭabarī uses the same pair for the Holy Land of 5:21: all agree it lies ${q("ما بين الفرات وعريش مصر")}.</p>`, refs:["Yāqūt, Muʿjam al-Buldān, s.v. al-Shām","Al-Ṭabarī on 5:21"]},
  {id:"B", n:"Rafaḥ", ll:[34.25,31.29], layer:"sham", src:["classical"], cert:"approx", body:`<p>Abū al-Fidāʾ starts al-Shām at Rafaḥ, and Jund Filasṭīn ran "from Rafaḥ to al-Lajjūn". Yāqūt puts the limit further west at al-ʿArīsh, so the Rafaḥ–al-ʿArīsh strip is al-Shām for some writers and Egypt for others.</p>`, refs:["Abū al-Fidāʾ, Taqwīm al-Buldān (via al-Muqtabas no. 70)"]},
  {id:"C", n:"Aylah", ll:[35.0,29.52], layer:"sham", src:["classical"], cert:"approx", body:`<p>Ibn Ḥawqal: ${q("وشرقيها البادية من أيلة إلى الفرات")}, "its east is the desert, from Aylah to the Euphrates". Aylah (al-ʿAqabah) sits on the seam of al-Shām, al-Ḥijāz and Egypt.</p>`, refs:["Ibn Ḥawqal, Ṣūrat al-Arḍ (via al-Muqtabas no. 70)"]},
  {id:"D", n:"Sargh", ll:[35.99,29.32], layer:"sham", src:["classical","early"], cert:"approx", body:`<p>Al-Ḥāzimī, quoted by Yāqūt: Sargh is "the first of al-Ḥijāz and the last of al-Shām", between al-Mughīthah and Tabūk, a station of the Syrian pilgrims. It is identified with al-Mudawwarah on today's Jordan–Saudi border.</p><p>It was at Sargh, in 17 AH, that ʿUmar رضي الله عنه was met by the commanders of the ajnād with news of the plague in al-Shām (al-Bukhārī and Muslim).</p>`, refs:[`Yāqūt, s.v. Sargh; <a href="https://alsahra.org/2019/02/%D8%AF%D8%B1%D8%A8-%D8%A7%D9%84%D8%AD%D8%AC-%D8%A7%D9%84%D8%B4%D8%A7%D9%85%D9%8A-18-%D9%85%D9%86%D8%B2%D9%84%D8%A9-%D8%B3%D9%8E%D8%B1%D8%BA-%D8%A7%D9%84%D9%85%D8%AF%D9%88%D8%B1%D8%A9" target="_blank" rel="noopener">al-Saḥrāʾ</a>`]},
  {id:"E", n:"Wādī al-Qurā & Taymāʾ", ll:[37.92,26.61], layer:"sham", src:["early"], cert:"approx", body:`<p>Al-Balādhurī reports that when ʿUmar expelled the Jews of Khaybar and Fadak, ${q("لم يخرج أهل تيماء ووادي القرى، لأنهما داخلتان في أرض الشام")}, "he did not expel the people of Taymāʾ and Wādī al-Qurā, because both lie within the land of al-Shām", and that he held ${q("ما دون وادي القرى إلى المدينة حجاز، وما وراء ذلك من الشام")}.</p><p>This is a historian's report, not a graded hadith.</p>`, refs:[`Al-Balādhurī, Futūḥ al-Buldān (<a href="https://www.islamweb.net/ar/library/content/200/17435/" target="_blank" rel="noopener">Islamweb</a>)`]},
  {id:"F", n:"Jabalā Ṭayyiʾ", ll:[41.6,27.45], layer:"sham", src:["classical","early"], cert:"uncertain", body:`<p>Yāqūt: ${q("وأما عرضها فمن جبلي طيئ من نحو القبلة إلى بحر الروم")}, al-Shām's width runs from the two mountains of Ṭayyiʾ (Ajaʾ and Salmā, near Ḥāʾil) to the Mediterranean. Hishām b. al-Kalbī uses the same mountains for al-Ḥijāz: ${q("الحجاز ما بين جبلي طيّء إلى طريق العراق لمن يريد مكة")}.</p>`, refs:["Yāqūt, s.v. al-Shām and al-Ḥijāz"]},
  {id:"G", n:"Bālis", ll:[38.07,35.99], layer:"sham", src:["classical"], cert:"approx", body:`<p>Ibn Ḥawqal: Bālis, on the west bank of the Euphrates, ${q("وهي أول مدن الشام من العراق")}, "is the first city of al-Shām coming from Iraq". Abū al-Fidāʾ's eastern line also reaches the Euphrates here.</p>`, refs:["Ibn Ḥawqal (via al-Muqtabas no. 70)"]},
  {id:"H", n:"al-Thughūr", ll:[35.4,37.25], layer:"sham", src:["classical"], cert:"uncertain", body:`<p>The Byzantine frontier fortresses: Ṭarsūs, Adana, al-Maṣṣīṣah, Marʿash, Malaṭyah. Ibn Ḥawqal runs al-Shām's edge ${q("ثم من الفرات إلى حد الروم")}, "then from the Euphrates to the border of the Rūm", taking them in. Abū al-Fidāʾ's line runs by Marʿash, Sīs and Ṭarsūs. The frontier moved with the wars, so it is hatched.</p>`, refs:["Ibn Ḥawqal and Abū al-Fidāʾ (via al-Muqtabas no. 70)"]},
  {id:"I", n:"Tabālah & al-ʿAblāʾ", ll:[42.25,19.97], layer:"hijaz", src:["early"], cert:"uncertain", body:`<p>Al-Aṣmaʿī, quoted by Yāqūt: ${q("الحجاز من تخوم صنعاء من العبلاء وتبالة إلى تخوم الشام")}, "al-Ḥijāz runs from the marches of Ṣanʿāʾ, from al-ʿAblāʾ and Tabālah, to the marches of al-Shām". The southern end of the widest Ḥijāz.</p>`, refs:["Yāqūt, s.v. al-Ḥijāz"]},
  {id:"J", n:"al-Yamāmah", ll:[46.85,24.45], layer:"hijazfiqh", src:["classical"], cert:"uncertain", body:`<p>For the ruling on non-Muslim residence, al-Shāfiʿī is reported to define al-Ḥijāz as Makkah, Madinah, al-Yamāmah and their districts, and Aḥmad as a list that adds Khaybar, Yanbuʿ and Fadak. This legal Ḥijāz reaches far further east than the geographical one. <span class="fine">From the earlier atlas; the jurists' own texts were not re-read.</span></p>`, refs:["See the jurists' layer"]},
  {id:"K", n:"al-Lajjūn", ll:[35.18,32.57], layer:"filastin", src:["classical"], cert:"approx", body:`<p>Roughly the northern limit of Jund Filasṭīn, which ran "from Rafaḥ to al-Lajjūn". North of it lay Jund al-Urdunn.</p>`, refs:[`<a href="https://en.wikipedia.org/wiki/Jund_Filastin" target="_blank" rel="noopener">Jund Filasṭīn</a>`]},
  {id:"L", n:"ʿAmmān", ll:[35.93,31.95], layer:"filastin", src:["classical"], cert:"uncertain", body:`<p>Usually part of al-Balqāʾ in Jund Dimashq, but counted among the centres of Filasṭīn in the Fatimid period. One reason Filasṭīn's hatching crosses the Jordan.</p>`, refs:[`<a href="https://en.wikipedia.org/wiki/Jund_Filastin" target="_blank" rel="noopener">Jund Filasṭīn</a>`]},
  {id:"M", n:"al-Sabʿ", ll:[34.79,31.25], layer:"filastin", src:["early"], cert:"approx", body:`<p>Of Ibrāhīm عليه السلام: ${q("ثم خرج من مصر إلى الشام، فنزل السبع من أرض فلسطين")}, "then he went from Egypt to al-Shām and settled at al-Sabʿ, of the land of Filasṭīn". An early usage that treats Filasṭīn as a part inside al-Shām. Al-Sabʿ is today's Beersheba.</p>`, refs:["Ibn Isḥāq, quoted by al-Baghawī on al-Anbiyāʾ 21:71"]},
  {id:"N", n:"al-Dārūm", ll:[34.33,31.42], layer:"filastin", src:["early"], cert:"approx", body:`<p>In the sīrah, the Prophet ﷺ sent Usāmah b. Zayd toward the marches of al-Balqāʾ and al-Dārūm "of the land of Filasṭīn". The phrase is Ibn Isḥāq's and is not a definition of borders.</p>`, refs:["Ibn Hishām, al-Sīrah"]},
  {id:"O", n:"Adhriʿāt & Buṣrā", ll:[36.10,32.62], layer:"sham", src:["early"], cert:"approx", body:`<p>On ${q("فِي أَدْنَى الْأَرْضِ")} (al-Rūm 30:3), al-Baghawī says the armies met ${q("بأذرعات وبصرى، وهي أدنى الشام إلى أرض العرب والعجم")}, "at Adhriʿāt and Buṣrā, the nearest part of al-Shām to the land of the Arabs and Persians". Other early views he gives: ʿIkrimah, Adhriʿāt and Kaskar; Mujāhid, al-Jazīrah; Muqātil, al-Urdunn and Filasṭīn.</p>`, refs:["Tafsir of al-Baghawī on al-Rūm 30:3"]}
];
LIMITS.forEach(l=>{ INFO['lim_'+l.id] = {title:`${l.id} · ${l.n}`, src:l.src, cert:l.cert, body:l.body, refs:l.refs}; });

