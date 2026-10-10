/* ================= v4 engine, part A: merge data, layers, presets, labels ================= */
Object.assign(INFO, INFO_NEW);
const ALL_LIMITS = LIMITS.concat(LIMITS_NEW);

const LAYERS = [
  {g:"Sacred status", items:[
    {id:"st-haram", name:"Ḥaram", sub:"Sanctuary with its own rulings", color:"--st-haram", disc:true, on:true, info:"status"},
    {id:"st-muq", name:"Muqaddas", sub:"Called holy", color:"--st-muq", disc:true, on:true, info:null},
    {id:"st-mub", name:"Mubārak", sub:"Called blessed, or prayed over for blessing", color:"--st-mub", disc:true, on:true, info:null},
    {id:"st-fad", name:"Faḍīla", sub:"A stated virtue", color:"--st-fad", disc:true, on:true, info:null},
    {id:"st-link", name:"Links", sub:"Mīqāt, Isrāʾ, qibla, routes", color:"--miqat", disc:true, on:true, info:null},
    {id:"st-none", name:"None established", sub:"Included so the gaps are visible", color:"--st-none", disc:true, on:true, info:null}
  ]},
  {g:"Sacred places", items:[
    {id:"haram", name:"The two ḥarams", sub:"Makkah and Madinah, with markers", color:"--haram", cert:"approx", on:true, info:"makkah"},
    {id:"aqsa", name:"al-Masjid al-Aqṣā", sub:"Jerusalem", color:"--sacred", cert:"firm", on:true, info:"aqsa"},
    {id:"miqat", name:"The mīqāts", sub:"Fixed by the Prophet ﷺ", color:"--miqat", cert:"approx", on:false, info:"miqat"},
    {id:"muq", name:"al-Arḍ al-Muqaddasah", sub:"al-Māʾidah 5:21, five early views", color:"--muq", cert:"uncertain", on:false, info:"muq"},
    {id:"tuwa", name:"Ṭuwā and Mount Sinai", sub:"Location uncertain", color:"--sacred", cert:"uncertain", on:true, info:"tuwa"},
    {id:"sites", name:"Qur'anic and sīrah sites", sub:"Ḥirāʾ, Thawr, Badr, al-Ḥijr and more", color:"--site", cert:"firm", on:false, info:null},
    {id:"links", name:"al-Isrāʾ and the qibla", sub:"Schematic line; arrows at Madinah", color:"--miqat", cert:"uncertain", on:false, info:"isra"},
    {id:"saba", name:"Sabaʾ and al-Aḥqāf", sub:"Maʾrib; three reports on ʿĀd", color:"--yemen", cert:"approx", on:false, info:"saba"},
    {id:"eschat", name:"End-of-time hadith places", sub:"al-Ghūṭah, Dābiq, Ludd and more", color:"--eschat", cert:"approx", on:false, info:"eschat"}
  ]},
  {g:"Classical regions", items:[
    {id:"histreg", name:"Historical region names", sub:"al-Maghrib, Khurāsān, Mā warāʾ al-Nahr and more · placed approximately", color:"--gold", cert:"uncertain", on:false, info:"histreg"},
    {id:"sham", name:"Bilād al-Shām", sub:"Core and contested edges", color:"--sham", cert:"approx", on:true, info:"sham"},
    {id:"filastin", name:"Filasṭīn and al-Urdunn", sub:"The two southern ajnād", color:"--fil", cert:"approx", on:true, info:"filastin"},
    {id:"ajnad", name:"Other ajnād", sub:"Dimashq, Ḥimṣ, Qinnasrīn", color:"--j3", cert:"uncertain", on:false, info:"ajnad"},
    {id:"hijaz", name:"al-Ḥijāz", sub:"Core and contested edges", color:"--hijaz", cert:"approx", on:true, info:"hijaz"},
    {id:"limits", name:"Named limits (A–P)", sub:"Places a source names as an edge", color:"--ink", cert:"approx", on:false, info:"seam"},
    {id:"hijazfiqh", name:"al-Ḥijāz of the jurists", sub:"For the residence ruling", color:"--hijaz", cert:"uncertain", on:false, info:"hijazfiqh"},
    {id:"jazirah", name:"Jazīrat al-ʿArab", sub:"Arabian Peninsula", color:"--jaz", cert:"uncertain", on:false, info:"jazirah"},
    {id:"yemen", name:"al-Yaman", sub:"Named in the Prophet's ﷺ duʿā", color:"--yemen", cert:"uncertain", on:false, info:"yemen"}
  ]},
  {g:"Neighbouring lands", items:[
    {id:"upper", name:"al-Jazīrah", sub:"Upper Mesopotamia", color:"--upper", cert:"approx", on:false, info:"upper"},
    {id:"iraq", name:"al-ʿIrāq and the Sawād", sub:"The river plain", color:"--iraq", cert:"uncertain", on:false, info:"iraq"},
    {id:"misr", name:"Miṣr and Sinai", sub:"Nile valley and Yāqūt's reckoning", color:"--misr", cert:"approx", on:false, info:"misr"},
    {id:"najd", name:"Najd", sub:"The interior plateau", color:"--najd", cert:"uncertain", on:false, info:"najd"},
    {id:"bahrayn", name:"al-Baḥrayn", sub:"The Gulf coast of Arabia", color:"--bahr", cert:"uncertain", on:false, info:"bahrayn"},
    {id:"tihamah", name:"Tihāmah", sub:"The Red Sea plain", color:"--tiham", cert:"uncertain", on:false, info:"tihamah"},
    {id:"rum", name:"Bilād al-Rūm", sub:"Beyond the frontier fortresses", color:"--rum", cert:"uncertain", on:false, info:"rum"},
    {id:"habashah", name:"al-Ḥabashah", sub:"Aksūm, the Najāshī's kingdom", color:"--hab", cert:"approx", on:false, info:"habashah"}
  ]},
  {g:"Roads", items:[
    {id:"trade", name:"Winter and summer journeys", sub:"Quraysh 106:2, and the Sabaʾ road", color:"--trade", cert:"approx", on:false, info:"quraysh"},
    {id:"hajj", name:"Old Hajj roads", sub:"Kūfah, Syrian, Egyptian", color:"--hajj", cert:"approx", on:false, info:"hajj"}
  ]},
  {g:"Thought experiment", items:[
    {id:"caliph", name:"One outline around the best lands", sub:"A caliphate as a thought experiment · my synthesis", color:"--ink", cert:"uncertain", on:false, info:"caliph"},
    {id:"caliphx", name:"Your complete outline", sub:"Arabia, the Levant, Iraq, Iran, Türkiye, the Caucasus, Cyprus, Egypt, Sudan and the Horn, with Libya, Greece and northern Uganda · not from the sources", color:"--xcal", cert:"uncertain", on:false, info:"caliphx"},
    {id:"natb", name:"Natural line", sub:"The line of seas, deserts and mountain crests, drawn over any version; chokepoints and passes · your design", color:"--natb", cert:"approx", on:false, info:"natb"},
    {id:"intl", name:"Internal lines", sub:"The Taurus divide; the Nile, Tigris and Euphrates; the Red Sea as the axis · your design", color:"--natb", cert:"approx", on:false, info:"intl"}
  ]},
  {g:"Land", items:[
    {id:"relief", name:"Relief shading", sub:"Mountains and escarpments", color:"--muted", cert:"firm", on:true, info:null},
    {id:"desert", name:"Deserts", sub:"al-Nufūd, al-Rubʿ al-Khālī, Bādiyat al-Shām", color:"--sand", cert:"approx", on:true, info:null},
    {id:"lava", name:"Lava fields (ḥarrah)", sub:"Approximate", color:"--lava", cert:"approx", on:false, info:"lava"},
    {id:"graticule", name:"Graticule", sub:"Latitude and longitude", color:"--muted", cert:"firm", on:true, info:null}
  ]},
  {g:"Present day", items:[
    {id:"modern", name:"Modern borders", sub:"With country names", color:"--border", cert:"firm", on:true, info:"modern"},
    {id:"disputed", name:"Disputed areas", sub:"Golan, East Jerusalem, Shebaa, Ḥalāʾib", color:"--border", cert:"uncertain", on:true, info:"modern"},
    {id:"cities", name:"Cities", sub:"Modern and classical names", color:"--ink", cert:"firm", on:true, info:null}
  ]}
];
const LAYER_IDS = []; LAYERS.forEach(g=>g.items.forEach(l=>LAYER_IDS.push(l.id)));
/* Complete Caliphate V2: how each added land was held, province by province (see v2_history.json) */
const V2CAT = {
  direct:{label:'Ruled by a caliphate, directly', tip:'governors, garrisons and taxes of a counted caliphate'},
  dynasty:{label:'Ruled by a dynasty under a caliph', tip:'a dynasty that named the caliph in the khutbah or on its coins, or was invested by him'},
  tributary:{label:'Tributary to a caliphate', tip:'kept its own rulers but paid tribute or tax to a caliphate'},
  islamic:{label:'Ruled by other Islamic states only', tip:'Muslim rulers who did not acknowledge a counted caliph'},
  temporary:{label:'Briefly held or raided only', tip:'a short occupation or raids, with no lasting rule'},
  influence:{label:'Influence only', tip:'Islam came by trade and preaching; no Muslim state ruled it'}
};
const layerOn = {}; LAYERS.forEach(g=>g.items.forEach(l=>layerOn[l.id]=l.on));
const STAT_LAYERS = ["st-haram","st-muq","st-mub","st-fad","st-link","st-none"];
const BASE_LAYERS = ["relief","desert","modern","disputed","cities","graticule"];
const PRESETS = [
  {id:"overview", n:"Overview", tip:"The main lands, the two ḥarams and the numbered status discs", on:BASE_LAYERS.concat(STAT_LAYERS, ["sham","filastin","hijaz","haram","aqsa","tuwa"])},
  {id:"lands", n:"Lands & boundaries", tip:"Every classical region and the places sources name as limits", on:BASE_LAYERS.concat(["histreg","sham","filastin","hijaz","limits","jazirah","yemen","upper","iraq","misr","najd","bahrayn","tihamah","rum","habashah","haram","aqsa"])},
  {id:"status", n:"Sacred status", tip:"Only the numbered discs and the sacred places", on:BASE_LAYERS.concat(STAT_LAYERS, ["haram","aqsa","miqat","muq","tuwa","sites","links"])},
  {id:"roads", n:"Roads", tip:"Caravan and Hajj roads", on:BASE_LAYERS.concat(["trade","hajj","haram","aqsa","saba"])},
  {id:"caliph", n:"Caliphate outline", tip:"The best-lands outline (my synthesis) inside your complete outline (your specification)", on:BASE_LAYERS.concat(STAT_LAYERS, ["histreg","caliph","caliphx","sham","filastin","hijaz","yemen","haram","aqsa","tuwa"]), b:[[-18.5,-3.6],[78.0,45.6]], keep:["natb","intl"]},
  {id:"everything", n:"Everything", tip:"Every layer at once", all:true}
];

/* ---------------- labels data ---------------- */
// [name, classical, lon, lat, minK, anchor, priority]
const CITIES = [
  ["Makkah","Bakkah · Umm al-Qurā",39.8262,21.4225,0,"r",3],
  ["Madinah","Yathrib · Ṭaybah",39.6111,24.4672,0,"r",3],
  ["Damascus","Dimashq",36.2919,33.5131,0,"r",4],
  ["Aleppo","Ḥalab",37.1343,36.2021,0,"r",5],
  ["Cairo","al-Fusṭāṭ",31.2357,30.0444,0,"l",5],
  ["Baghdad","",44.3661,33.3152,0,"r",5],
  ["Ṣanʿāʾ","",44.1910,15.3694,0,"r",5],
  ["Riyadh","near Ḥajr al-Yamāmah",46.6753,24.7136,0,"r",6],
  ["Istanbul","Qusṭanṭīniyyah",28.9784,41.0082,0,"r",6],
  ["Homs","Ḥimṣ",36.7137,34.7324,1.3,"r",7],
  ["Amman","ʿAmmān",35.9106,31.9539,1.5,"r",7],
  ["Gaza","Ghazzah",34.4668,31.5017,1.8,"l",7],
  ["Hebron","al-Khalīl",35.0998,31.5326,3.5,"l",8],
  ["Ramla","al-Ramlah",34.8656,31.9293,3.5,"l",8],
  ["Tiberias","Ṭabariyyah",35.5309,32.7959,2.4,"r",8],
  ["Beirut","Bayrūt",35.5018,33.8938,2,"l",8],
  ["Antakya","Anṭākiyah",36.1613,36.2023,2,"l",8],
  ["Tarsus","Ṭarsūs",34.8953,36.9177,2,"l",9],
  ["Jericho","Arīḥāʾ",35.4444,31.8569,3.5,"r",8],
  ["Tadmur","Palmyra",38.2684,34.5503,1.6,"r",9],
  ["al-Ṭāʾif","",40.4158,21.2703,1.3,"r",7],
  ["Jeddah","Juddah",39.1925,21.4858,1.3,"l",7],
  ["Yanbuʿ","",38.0618,24.0895,1.6,"l",8],
  ["Khaybar","",39.2908,25.6966,1.6,"r",7],
  ["Taymāʾ","",38.5397,27.6293,1.6,"r",8],
  ["Tabūk","",36.5662,28.3835,1.1,"r",6],
  ["al-ʿUlā","Wādī al-Qurā",37.9232,26.6085,2.2,"l",8],
  ["Aqaba","Aylah",35.0078,29.5267,1.2,"r",6],
  ["al-ʿArīsh","",33.8033,31.1316,1.5,"l",8],
  ["Dūmat al-Jandal","",39.8687,29.8117,1.8,"r",9],
  ["Najrān","",44.1277,17.4924,1.5,"r",8],
  ["ʿAdan","Aden",45.0187,12.7855,1.2,"r",7],
  ["Baṣrah","",47.7804,30.5085,1.5,"l",8],
  ["Kūfah","",44.40,32.03,1.8,"l",8],
  ["Bīshah","",42.60,19.99,2.4,"r",9],
  /* v4 additions */
  ["Mosul","al-Mawṣil",43.13,36.34,1.1,"r",7],
  ["al-Raqqah","",39.01,35.95,1.4,"l",8],
  ["Ḥarrān","",39.03,36.87,2.0,"r",9],
  ["Urfa","al-Ruhā · Edessa",38.79,37.16,1.4,"r",8],
  ["Diyarbakır","Āmid",40.22,37.91,1.3,"r",7],
  ["Nuṣaybīn","",41.22,37.07,2.2,"r",9],
  ["Tikrīt","",43.68,34.60,1.8,"r",9],
  ["Sāmarrāʾ","",43.88,34.20,1.8,"r",9],
  ["Hīt","",42.84,33.64,2.4,"l",9],
  ["al-Madāʾin","Ctesiphon",44.58,33.09,2.4,"r",9],
  ["Alexandria","al-Iskandariyyah",29.92,31.20,1.0,"r",7],
  ["Suez","al-Suways",32.55,29.97,2.0,"r",9],
  ["Luxor","al-Uqṣur",32.64,25.70,1.6,"r",9],
  ["Malatya","Malaṭyah",38.31,38.35,1.4,"r",8],
  ["Kahramanmaraş","Marʿash",36.94,37.58,1.8,"r",9],
  ["Rabat","Ribāṭ al-Fatḥ",-6.84,34.02,0.9,"r",6],["Fez","Fās",-5.00,34.03,0,"r",6],["Marrakesh","Marrākush",-7.99,31.63,1.0,"r",7],
  ["Algiers","al-Jazāʾir",3.06,36.75,0,"r",6],["Tlemcen","Tilimsān",-1.32,34.88,1.6,"l",8],["Tunis","",10.18,36.81,0.9,"r",6],["Kairouan","al-Qayrawān",10.10,35.68,1.2,"l",7],
  ["Tripoli","Ṭarābulus al-Gharb",13.19,32.89,0,"r",6],["Benghazi","in old Barqah",20.07,32.12,1.1,"r",7],["Nouakchott","",-15.98,18.08,1.2,"r",8],
  ["Lagos","",3.38,6.45,1.2,"l",7],["Accra","",-0.19,5.56,1.5,"l",8],["Kinshasa","",15.31,-4.32,1.4,"r",8],["Luanda","",13.23,-8.84,1.2,"r",7],["Dar es Salaam","",39.28,-6.80,1.3,"r",7],["Lusaka","",28.28,-15.42,1.8,"r",8],["Antananarivo","",47.52,-18.91,1.5,"r",8],["Windhoek","",17.08,-22.56,1.8,"r",8],["Maputo","",32.57,-25.97,1.4,"r",8],["Johannesburg","",28.05,-26.20,1.2,"r",7],["Cape Town","",18.42,-33.92,1.0,"l",6],
  ["Timbuktu","Tunbuktū",-3.00,16.77,1.1,"r",7],["Kano","",8.52,12.00,1.4,"r",8],["N'Djamena","",15.04,12.13,1.3,"r",8],
  ["Córdoba","Qurṭubah",-4.78,37.88,1.0,"l",6],["Granada","Gharnāṭah",-3.60,37.18,1.3,"r",7],["Seville","Ishbīliyah",-5.98,37.39,1.4,"l",8],["Toledo","Ṭulayṭulah",-4.02,39.86,1.6,"r",8],
  ["Lisbon","al-Ushbūnah",-9.14,38.72,1.4,"r",8],["Palermo","Balarm",13.36,38.12,1.2,"r",7],["Rome","Rūmiyah",12.50,41.90,0,"r",6],["Athens","",23.73,37.98,1.3,"l",8],
  ["Karachi","near old Daybul",67.01,24.86,0,"l",6],["Multan","Multān",71.47,30.20,1.3,"r",7],["Lahore","",74.34,31.55,1.0,"r",7],["Islamabad","",73.05,33.68,1.3,"r",8],["Delhi","",77.21,28.61,0,"l",6],
  ["Kabul","",69.18,34.53,0,"r",6],["Herat","Harāt",62.20,34.35,1.0,"r",7],["Kandahar","",65.71,31.61,1.3,"r",8],["Balkh","",66.90,36.76,1.4,"r",8],
  ["Samarqand","",66.96,39.65,0,"r",6],["Bukhārā","",64.42,39.77,1.1,"l",7],["Tashkent","al-Shāsh",69.24,41.30,1.0,"r",7],["Merv","Marw, ruins",61.84,37.66,1.4,"r",8],
  ["Khiva","Khwārazm",60.36,41.38,1.4,"l",8],["Ashgabat","",58.38,37.95,1.3,"l",8],["Dushanbe","",68.78,38.56,1.6,"r",9],
  ["Tangier","Ṭanjah",-5.81,35.77,1.4,"r",8],["Ceuta","Sabtah",-5.32,35.89,2.2,"l",8],["Sijilmāsah","ruins",-4.27,31.28,1.8,"r",9],["Oran","Wahrān",-0.63,35.70,1.6,"r",8],
  ["Constantine","Qusanṭīnah",6.61,36.36,1.6,"r",8],["Bijāyah","Béjaïa",5.08,36.75,2.2,"l",9],["al-Mahdiyyah","Mahdia",11.06,35.50,2.0,"r",9],["Ghadāmis","",9.50,30.13,1.8,"r",9],
  ["Murzuq","",13.92,25.92,2.0,"r",9],["Sabha","",14.43,27.04,1.6,"l",9],["Shinqīṭ","Chinguetti",-12.36,20.46,1.6,"r",9],["Wādān","Ouadane",-11.62,20.93,2.4,"r",9],
  ["Laayoune","al-ʿAyyūn",-13.20,27.15,1.6,"r",9],["Gao","Kawkaw",-0.04,16.27,1.6,"r",8],["Djenné","",-4.55,13.91,2.0,"r",9],["Dakar","",-17.45,14.69,1.4,"r",8],
  ["Bamako","",-8.00,12.64,1.4,"r",8],["Niamey","",2.11,13.51,1.6,"r",9],["Agadez","",7.99,16.97,1.6,"r",9],
  ["Astana","",71.43,51.13,1.0,"r",7],["Almaty","",76.89,43.24,1.0,"r",7],["Bishkek","",74.59,42.87,1.3,"l",8],["Osh","Ūsh",72.80,40.51,1.8,"r",9],["Khujand","Khujandah",69.62,40.28,1.8,"l",9],
  ["Turkistan","Yasī",68.25,43.30,1.6,"r",8],["Otrar","Fārāb, ruins",68.30,42.85,2.4,"l",9],["Taraz","Ṭarāz",71.37,42.90,1.8,"r",9],["Termez","Tirmidh",67.28,37.22,1.4,"r",8],
  ["Urgench","Gurganj",60.63,41.55,2.2,"r",9],["Kashgar","Kāshghar",75.99,39.47,1.3,"r",8],["Aktau","",51.20,43.65,1.8,"r",9],["Atyrau","",51.88,47.11,1.8,"r",9],
  ["Shymkent","",69.60,42.32,2.2,"r",9],["Astrakhan","",48.03,46.35,1.6,"r",9],
  ["Peshawar","Purshāwar",71.58,34.01,1.4,"r",8],["Quetta","",67.00,30.18,1.6,"r",9],["al-Manṣūrah","ruins, capital of Sind",68.78,25.88,2.2,"r",9],
  ["Mazār-i Sharīf","",67.11,36.71,1.4,"l",8],["Ghazni","Ghaznah",68.42,33.55,1.4,"r",8],["Bāmiyān","",67.83,34.82,1.8,"r",9],["Gwadar","",62.32,25.13,2.0,"r",9],
  ["Mumbai","",72.88,19.08,1.0,"r",7],["Kathmandu","",85.32,27.72,1.4,"r",8],["Dhaka","",90.41,23.81,1.2,"l",8],["Calicut","Kozhikode",75.78,11.26,1.8,"r",9],["Colombo","",79.86,6.93,1.6,"r",9],
  ["Nairobi","",36.82,-1.29,1.0,"r",7],["Mombasa","Manbasah",39.67,-4.04,1.4,"r",8],["Kampala","",32.58,0.35,1.4,"r",8],
  ["London","",-0.13,51.51,1.2,"r",8],["Paris","",2.35,48.86,1.0,"r",7],["Madrid","",-3.70,40.42,1.2,"r",8],["Vienna","",16.37,48.21,1.2,"r",8],["Venice","",12.33,45.44,1.6,"r",9],
  ["Budapest","",19.04,47.50,1.4,"r",8],["Belgrade","",20.46,44.79,1.6,"r",9],["Bucharest","",26.10,44.43,1.4,"r",9],["Kyiv","",30.52,50.45,1.2,"r",8],["Moscow","",37.62,55.76,1.2,"r",8],
  ["Bulghār","Volga Bulgaria, ruins",49.06,54.98,2.0,"r",9],
  ["Berbera","Barbarā",45.01,10.44,0.8,"r",8],["Massawa","Muṣawwaʿ",39.45,15.61,0.9,"r",8],["Port Sudan","",37.22,19.62,0.8,"r",8],["Kismayo","",42.54,-0.36,1.2,"r",8],
  ["Kassala","",36.40,15.45,1.6,"r",9],["El Obeid","al-Ubayyiḍ",30.22,13.18,1.4,"r",8],["Sennar","Sinnār",33.63,13.55,1.6,"r",9],["Malakal","",31.66,9.53,1.6,"r",9],["Wau","",28.00,7.70,1.8,"r",9],
  ["Gondar","",37.47,12.60,1.6,"l",9],["Dire Dawa","",41.86,9.59,1.8,"r",9],["Bosaso","",49.18,11.28,1.6,"l",9],["Garowe","",48.48,8.40,2.0,"r",9],["Baidoa","",43.65,3.12,1.8,"r",9],
  ["Ankara","",32.85,39.93,0.8,"r",7],
  ["Tbilisi","Tiflīs",44.79,41.72,0.9,"r",6],["Yerevan","near old Dabīl",44.51,40.18,1.0,"l",6],["Baku","Bākūh",49.87,40.41,0.9,"l",6],
  ["Bardhaʿah","Barda, old capital of Arrān",47.12,40.37,1.8,"r",8],["Ganja","Janzah",46.36,40.68,1.8,"l",9],["Nakhchivan","Nashawā",45.41,39.21,2.2,"r",9],
  ["Derbent","Bāb al-Abwāb",48.29,42.06,1.6,"r",8],["Batumi","",41.64,41.64,2.2,"r",9],
  ["Tabrīz","",46.29,38.08,1.0,"r",6],["Ardabīl","",48.29,38.25,1.6,"r",8],["Marāghah","",46.24,37.39,2.2,"l",9],["Urmia","Urmiyah",45.07,37.55,2.0,"l",9],
  ["Rasht","",49.58,37.28,1.8,"r",9],["Gorgān","Jurjān",54.43,36.84,1.8,"r",8],["Dāmghān","Qūmis",54.34,36.17,2.4,"r",9],
  ["Mashhad","beside old Ṭūs",59.61,36.30,0.9,"r",6],["Nīshāpūr","Naysābūr",58.80,36.21,1.6,"l",8],
  ["Shīrāz","",52.53,29.59,0.9,"r",6],["Iṣṭakhr","Persepolis, ruins",52.89,29.98,2.2,"r",9],["Yazd","",54.37,31.90,1.2,"r",7],["Kirmān","",57.08,30.28,1.1,"r",7],
  ["Bandar ʿAbbās","",56.27,27.18,1.3,"l",7],["Hurmuz","Hormuz island",56.46,27.06,2.6,"r",9],["Sīrāf","old Gulf port",52.34,27.67,2.2,"r",9],["Bushehr","",50.84,28.97,1.8,"l",8],
  ["Zāhedān","",60.86,29.50,1.4,"l",8],
  ["Tehran","near old Rayy",51.39,35.69,0.8,"r",6],["Iṣfahān","Iṣbahān",51.67,32.65,1.0,"r",7],["Hamadān","Hamadhān · Ecbatana",48.51,34.80,1.2,"l",7],
  ["Qum","",50.88,34.64,1.6,"r",8],["Kāshān","",51.44,33.98,2.0,"r",9],["Kirmānshāh","Qirmīsīn",47.07,34.31,1.4,"l",8],["Qazvīn","",50.00,36.27,1.6,"l",8],
  ["Zanjān","",48.48,36.68,2.0,"l",9],["Nihāwand","",48.37,34.19,2.4,"r",9],["Khorramābād","",48.35,33.49,2.2,"l",9],
  ["Ahvāz","al-Ahwāz",48.67,31.32,1.2,"r",7],["Shūshtar","Tustar",48.85,32.05,2.2,"r",9],["Ābādān","ʿAbbādān",48.30,30.34,1.8,"r",8],["Khorramshahr","al-Muḥammarah",48.18,30.44,2.6,"l",9],
  ["Konya","Qūniyah · Iconium",32.49,37.87,1.2,"r",7],["Kayseri","Qayṣariyyah",35.48,38.73,1.4,"r",8],["Erzurum","Arzan al-Rūm",41.27,39.90,1.4,"r",8],
  ["Trabzon","Ṭarābazundah",39.72,41.00,1.4,"r",8],["Sivas","Sīwās",37.02,39.75,1.8,"r",9],["Van","",43.38,38.50,1.8,"l",9],
  ["Bursa","Brūsah",29.06,40.19,1.6,"r",8],["İzmir","Smyrna",27.14,38.42,1.2,"r",7],["Edirne","Adrianople",26.56,41.68,1.6,"r",8],
  ["İznik","Nīqiyah · Nicaea",29.72,40.43,3,"r",9],["ʿAmmūriyah","Amorium, site",31.29,39.02,2.2,"r",9],["Üsküdar","Scutari, the Asian shore",29.02,41.02,9,"r",9],
  ["Adana","Adhanah",35.32,37.0,2.4,"l",9],
  ["Ḥāʾil","",41.69,27.52,1.4,"r",7],
  ["Buraydah","al-Qaṣīm",43.97,26.33,1.8,"r",8],
  ["al-Ḥufūf","al-Aḥsāʾ",49.58,25.38,1.6,"r",8],
  ["al-Qaṭīf","",50.01,26.56,1.9,"r",9],
  ["Jāzān","",42.55,16.89,1.8,"r",9],
  ["al-Ḥudaydah","",42.95,14.80,1.8,"l",9],
  ["Zabīd","",43.31,14.20,2.4,"l",9],
  ["al-Lith","",40.28,20.15,2.2,"l",9],
  ["al-Qunfudhah","",41.08,19.13,2.2,"l",9],
  ["al-Shiḥr","",49.60,14.76,1.8,"l",9],
  ["al-Mukallā","",49.13,14.54,2.6,"l",9],
  ["Ṣalālah","",54.09,17.02,1.6,"r",8],
  ["Muscat","Masqaṭ",58.41,23.59,1.0,"l",7],
  ["Doha","",51.53,25.29,1.5,"r",8],
  ["Manama","",50.58,26.23,2.4,"r",9],
  ["Kuwait","",47.98,29.37,1.5,"l",8],
  ["Haifa","Ḥayfā",34.99,32.79,2.4,"l",9],
  ["Jaffa","Yāfā",34.75,32.05,3.2,"l",9],
  ["Nablus","Nābulus",35.26,32.22,3.5,"r",9],
  ["Acre","ʿAkkā",35.07,32.93,3.4,"l",9],
  ["Hama","Ḥamāh",36.75,35.13,2.2,"r",9],
  ["Latakia","al-Lādhiqiyyah",35.78,35.52,2.2,"l",9],
  ["Dayr al-Zawr","",40.14,35.34,1.6,"r",9],
  ["al-Karak","",35.70,31.18,2.5,"r",9],
  ["Tripoli","Ṭarābulus",35.84,34.44,2.4,"l",9],
  ["Sidon","Ṣaydā",35.37,33.56,3.6,"l",9],
  ["Khartoum","al-Kharṭūm",32.53,15.55,0.35,"r",5],["Sawākin","Suakin, old Red Sea port",37.33,19.10,1.0,"r",8],["ʿAydhāb","old pilgrims' port",36.49,22.33,1.6,"l",8],
  ["Dunqulah","Old Dongola",30.74,18.22,1.5,"r",8],["Aswān","Uswān",32.90,24.09,1.6,"l",7],["Addis Ababa","",38.74,9.03,0.35,"r",5],["Asmara","",38.93,15.33,0.55,"l",7],
  ["Djibouti","",43.15,11.59,0.55,"l",7],["Zaylaʿ","Zeila",43.47,11.35,1.6,"r",8],["Harar","",42.12,9.31,1.2,"l",8],["Hargeisa","",44.06,9.56,0.6,"r",8],
  ["Mogadishu","Maqdishū",45.34,2.04,0.35,"r",6],["Juba","",31.58,4.85,0.4,"r",7],["Nicosia","Lefkoşa · Lefkosia",33.36,35.17,1.6,"r",7],["Abu Dhabi","",54.37,24.45,1.4,"l",7],
  ["Karbalāʾ","",44.03,32.62,2.2,"l",9],
  ["Tyre","Ṣūr",35.20,33.27,3.6,"l",9]
];
const HARAM_PTS = [
  {n:"al-Tanʿīm · 3 mīl", s:"Madinah road", ll:[39.792,21.466], a:"l", k:28, info:"makkah"},
  {n:"al-Maqṭaʿ · 7 mīl", s:"Iraq road", ll:[39.908,21.499], a:"l", k:28, info:"makkah"},
  {n:"Shiʿb Āl ʿAbdillāh · 9 mīl", s:"al-Jiʿrānah road", ll:[39.955,21.492], a:"r", k:28, info:"makkah"},
  {n:"Baṭn Namirah · 7 mīl", s:"facing ʿArafāt, Ṭāʾif road", ll:[39.952,21.358], a:"l", k:28, info:"makkah"},
  {n:"Aḍāt Libn · 7 mīl", s:"Yemen road", ll:[39.815,21.315], a:"r", k:28, info:"makkah"},
  {n:"Munqaṭaʿ al-Aʿshāsh · 10 mīl", s:"Jeddah road, al-Ḥudaybiyah", ll:[39.665,21.449], a:"l", k:28, info:"makkah"},
  {n:"ʿArafah", s:"outside the ḥaram", ll:[39.985,21.355], a:"r", k:28, info:"makkah", out:true},
  {n:"Minā", s:"inside", ll:[39.893,21.413], a:"r", k:55, info:"makkah"},
  {n:"Muzdalifah", s:"inside", ll:[39.935,21.392], a:"r", k:55, info:"makkah"},
  {n:"Thawr", s:"hill north of Uḥud", ll:[39.617,24.540], a:"r", k:45, info:"madinah"},
  {n:"ʿAyr", s:"mountain to the south", ll:[39.592,24.393], a:"r", k:45, info:"madinah"},
  {n:"Eastern lava field", s:"Ḥarrat Wāqim", ll:[39.682,24.462], a:"r", k:45, info:"madinah"},
  {n:"Western lava field", s:"Ḥarrat al-Wabarah", ll:[39.540,24.440], a:"l", k:45, info:"madinah"},
  {n:"Uḥud", s:"", ll:[39.615,24.505], a:"r", k:60, info:"madinah"}
];
const HIST_LBL = [   /* historical-geographical regions: names only, placed approximately, no borders */
  ["al-Andalus","الأندلس",-4.6,38.7,0.4],["al-Maghrib al-Aqṣā","",-7.4,30.2,0.7],["al-Maghrib al-Awsaṭ","",2.6,34.3,0.7],["Ifrīqiyah","إفريقية",9.7,33.2,0.6],
  ["Barqah","برقة",22.4,31.7,0.7],["Fazzān","فزان",14.4,26.3,0.7],["Bilād al-Sūdān","بلاد السودان",-1.5,13.4,0.45],["al-Nūbah","النوبة",31.7,20.3,0.8],
  ["Bilād al-Zanj","بلاد الزنج",38.6,-3.2,0.6],["Bilād al-Barbar","",48.6,6.9,1.0],["Khurāsān","خراسان",61.4,35.7,0.45],["Mā warāʾ al-Nahr","ما وراء النهر",66.6,40.6,0.45],
  ["Khwārazm","خوارزم",59.4,42.9,0.8],["Farghānah","فرغانة",71.7,40.9,0.9],["Sijistān","سجستان",61.9,30.8,0.8],["Makrān","مكران",62.2,26.0,0.8],["al-Sind","السند",68.3,26.2,0.6],
  ["al-Hind","الهند",77.4,22.4,0.45],["Ṭabaristān","طبرستان",52.6,36.8,1.2],["Ādharbayjān","أذربيجان",47.3,37.6,1.1],["Arrān","أران",47.7,40.75,1.3],["Armīniyah","أرمينية",44.0,39.95,1.3],
  ["Fāris","فارس",53.4,29.2,0.9],["Dārfūr","دارفور",24.2,14.6,0.6],["Kurdufān","كردفان",29.6,12.4,0.7],["Sinnār","سنار",34.4,12.4,1.1],["Bilād al-Bujah","بلاد البجة",35.6,20.4,1.0],["Dasht-i Qipchāq","",58.6,49.4,0.45],["Bilād al-Turk","بلاد الترك",78.4,46.9,0.6],["Bilād al-Ṣīn","بلاد الصين",86.2,38.2,0.6],["Bulghār","بلغار",50.2,54.2,1.0]
];
const PASSES = [["Khyber Pass",71.15,34.07,1.5,"r"],["Bolan Pass",67.62,29.86,2.0,"r"],["Darial Pass · Bāb al-Lān",44.64,42.74,1.8,"r"],["Cilician Gates",34.77,37.29,2.4,"l"],["Salang Pass",69.06,35.32,2.4,"l"],["Khunjerab Pass",75.42,36.85,2.0,"r"]];
const ISLAND_LBL = [["Canary Islands · al-Khālidāt",-15.6,29.45,0.8],["Madeira",-16.95,33.05,1.4],["Cape Verde",-24.0,15.6,1.0],["Mayūrqah · Majorca",2.95,39.75,1.4],["Ṣiqilliyah · Sicily",14.2,37.65,1.2],
  ["Sardāniyah · Sardinia",9.0,40.15,1.4],["Iqrīṭish · Crete",24.9,35.3,1.3],["Rūdis · Rhodes",28.05,36.3,2.4],["Māliṭah · Malta",14.43,35.95,2.4],["Suquṭrā · Socotra",53.95,12.55,1.2],
  ["Zanjibār · Zanzibar",39.3,-6.05,1.4],["Sarandīb · Sri Lanka",80.7,7.9,0.8],["Maldives",73.4,3.7,1.4]];
const SEA_LBL = [
  ["Baḥr al-Rūm","Mediterranean",31.6,33.9,0],["Baḥr al-Qulzum","Red Sea",38.0,21.8,0],["Baḥr Fāris","the Gulf",51.9,27.3,0],["Arabian Sea","",58.0,15.6,0],
  ["Gulf of Aden","",47.5,12.2,0.4],["Gulf of Oman","",58.9,24.8,1.2],["Baḥr al-Aswad","Black Sea",34.0,42.6,0.8],["Indian Ocean","Baḥr al-Hind",56.0,6.0,0.4],["Somali Sea","",50.6,3.2,0.4],["Gulf of Tadjoura","",43.0,11.75,3.2],["Strait of Hormuz","",56.55,26.45,2.2],["Bay of Bengal","",88.4,15.4,0.4],["Laccadive Sea","",74.3,9.6,1.0],["Gulf of Guinea","",3.0,2.6,0.5],["Tyrrhenian Sea","",11.9,40.0,1.0],["Alboran Sea","",-3.6,36.05,2.2],["Sea of Azov","",36.6,46.1,1.2],["North Sea","",3.2,55.2,0.8],["Bay of Biscay","",-4.6,45.4,0.8],["Atlantic Ocean","al-Baḥr al-Muḥīṭ",-16.5,35.2,0],["Strait of Gibraltar","al-Zuqāq",-5.5,35.85,2.4],["Gulf of Sidra","Khalīj Surt",18.4,31.35,1.3],["Ionian Sea","",18.6,37.6,1.3],["Adriatic Sea","",16.2,42.6,1.6],["Sea of Marmara","Baḥr Marmara",28.15,40.72,2.2],["Bosphorus","Khalīj al-Qusṭanṭīniyyah",29.10,41.16,5],["Dardanelles","",26.45,40.22,3.2],["Golden Horn","",28.96,41.03,14],["Aegean Sea","",25.6,38.9,0.8],["Bāb al-Mandab","",43.2,12.45,1.4],["Caspian Sea","Baḥr al-Khazar",51.0,41.2,0.6]
];
const RIVER_LBL = [["Aral Sea",59.9,45.0,1.0],["Lake Chad",14.4,13.4,1.3],["Indus · Mihrān",68.4,27.3,1.3],["Jayḥūn · Amu Darya",62.2,40.4,1.4],["Sayḥūn · Syr Darya",66.4,43.7,1.6],["Niger",-4.6,14.6,0],["Lake Urmia",45.55,37.95,1.2],["Lake Sevan",45.32,40.36,2.4],["Kura · al-Kurr",47.6,40.15,2.0],["Aras",46.2,39.3,2.4],["Lake Van",42.85,38.66,1.4],["Tuz Gölü",33.42,38.78,2.2],["Kızılırmak",34.6,40.75,2.2],["Lake Victoria",33.0,-1.0,0.6],["Lake Turkana",36.05,3.5,0.5],["Lake Tana",37.3,12.0,0.6],["al-Nīl al-Azraq · Blue Nile",34.2,12.1,0.6],["al-Nīl al-Abyaḍ · White Nile",32.85,12.9,0.6],["Shabeelle",44.7,4.0,1.0],["Jubba",42.6,1.9,1.0],["al-Furāt · Euphrates",40.6,34.7],["Dijlah · Tigris",44.6,34.9],["al-Nīl · Nile",31.4,27.3],["al-Urdunn · Jordan",35.62,32.2,4]];
const PHYS_LBL = [["Rās ʿAsīr · Cape Guardafui",51.0,11.95,0.6],["Red Sea Hills",36.6,18.0,0.8],["Darfur Plateau · Jabal Marrah",24.3,13.1,1.2],["Great Rift Valley",39.6,6.6,1.4],["Tian Shan",79.6,42.4,0.6],["Karakoram",76.6,35.7,1.0],["Himalaya",82.6,29.4,0.6],["Kopet Dag",57.6,38.05,1.2],["Sulaiman Range",69.9,30.9,1.2],["Ahaggar",5.6,23.1,0.9],["Aïr",8.6,18.3,1.2],["Tassili n’Ajjer",8.6,25.7,1.4],["Ustyurt Plateau",56.6,43.7,1.0],["Betpak-Dala",70.2,45.7,1.0],["Registan",65.5,30.6,1.2],["Taklamakan",83.4,38.7,0.6],["Libyan Desert",22.6,24.4,0.8],["Deccan",77.2,17.4,0.8],["Atlas Mountains",-4.4,32.4,1.0],["Sahara · al-Ṣaḥrāʾ",6.0,24.0,0],["Tibesti",18.3,21.0,1.4],["Hindu Kush",70.2,35.7,1.1],["Pamir",73.2,38.4,1.4],["Thar Desert",71.3,26.6,1.2],["Karakum",60.2,38.7,1.2],["Kyzylkum",64.5,42.4,1.3],["Caucasus · Jabal al-Qabq",45.2,42.75,1.0],["Zagros",51.2,30.6,0.9],["Alborz",52.6,36.3,1.3],["Dasht-e Kavīr",54.6,34.55,1.2],["Dasht-e Lūt",58.7,30.9,1.2],["Armenian Highland",42.6,39.55,1.6],["Anatolian Plateau",33.6,39.35,1.1],["Pontic Mountains",37.6,40.62,1.4],["Thrace",27.2,41.45,2.4],["Ethiopian Highlands",38.4,11.0,0.4],["Nubian Desert",33.6,20.7,0.45],["Western Desert",27.4,25.2,1.1],["the Sudd",30.2,8.7,0.55],["Danakil",41.1,13.7,0.7],["Ogaden",44.6,6.9,0.5],["Troodos",32.9,34.92,4],["al-Sarāt",42.9,18.4,1.6],["al-Nufūd",41.6,28.6,0.9],["al-Rubʿ al-Khālī",50.5,19.6,0],["Bādiyat al-Shām",39.9,32.2,0.9],["al-Naqab",34.85,30.55,2.6],["Sīnāʾ · al-Tīh",33.55,29.75,1.4],["Ṭuwayq",46.25,23.2,1.4],["Jabal Lubnān",35.98,34.05,2.4],["Ṭūrus · Taurus",33.3,37.2,1],["al-Ghūṭah",36.37,33.62,3.5]];
const COUNTRY_LBL = [
  ["Syria",39.7,35.4,1],["Lebanon",35.95,34.25,3],["Jordan",37.0,30.9,1.4],["Israel",34.82,30.75,2.4],["Palestine",35.27,32.05,3.4],["Gaza",34.37,31.38,4.5],
  ["Golan (disputed)",35.78,33.05,4.5],["Saudi Arabia",44.8,22.4,0],["Yemen",46.6,14.9,0],["Egypt",29.8,26.6,0],["Iraq",43.0,32.6,0],["Türkiye",36.2,38.7,0],
  ["Oman",56.9,21.0,0],["UAE",54.4,23.6,1.6],["Qatar",51.2,25.2,2.4],["Kuwait",47.6,29.3,2.2],["Bahrain",50.55,26.0,3.5],["Iran",51.5,31.0,0],["Sudan",33.0,18.5,0],["Cyprus",33.2,35.1,1.2],
  ["Eritrea",38.6,15.7,0.35],["Ethiopia",39.4,10.0,0],["Somalia",45.4,4.2,0.3],["Somaliland",46.0,9.7,0.4],["Djibouti",42.7,11.7,0.4],["Armenia",44.9,40.2,1],["Azerbaijan",47.6,40.5,1],["Georgia",43.4,42.0,1],["Turkmenistan",58.2,40.3,0],["Greece",22.0,39.5,1.0],["Libya",17.6,27.0,0],["Pakistan",69.4,29.6,0],["South Sudan",30.6,7.4,0.3],["Kenya",37.9,0.9,0.6],["Uganda",32.5,1.6,1],["DR Congo",25.0,0.5,0.8],["Central African Rep.",21.6,7.0,1],["Chad",21.4,16.4,0],["Tanzania",34.4,-3.2,1.2],["Rwanda",29.9,-1.9,3],["Russia",45.6,45.4,0.8],["Nepal",84.2,28.3,1.4],["Bangladesh",90.2,24.1,1.4],["Morocco",-6.6,31.9,0],["Algeria",2.5,28.0,0],["Tunisia",9.4,34.0,1.2],["Mauritania",-10.6,20.4,0],["Western Sahara",-13.0,24.6,1.2],["Mali",-2.0,17.6,0],["Niger",9.5,17.4,0.6],["Nigeria",8.0,10.0,0],["Senegal",-14.6,14.5,1.4],["Burkina Faso",-1.6,12.3,1.3],["Cameroon",12.6,5.6,1.1],["Guinea",-10.9,10.5,1.3],["Sierra Leone",-11.8,8.5,2.4],["Guinea-Bissau",-15.0,12.0,3.2],["Gambia",-15.4,13.45,4.6],["Comoros",43.9,-11.85,4],["Spain",-3.7,40.1,0],["Portugal",-8.0,39.7,1.3],["France",2.6,45.1,0.9],["Italy",12.8,42.8,0],["Bulgaria",25.3,42.7,1.4],["Romania",25.0,45.4,1.3],["India",76.0,23.0,0],["Tajikistan",71.0,38.7,1.3],["Kyrgyzstan",74.6,41.4,1.3],["Uzbekistan",63.6,41.6,0],["Kazakhstan",67.8,45.3,0],["China",76.4,38.6,1.3],["Afghanistan",66.0,33.4,0],
  ["Angola",17.5,-12.2,0.8],["Zambia",27.8,-13.4,1.0],["Malawi",34.2,-13.4,2.6],["Mozambique",35.6,-17.2,0.9],["Zimbabwe",29.8,-19.0,1.4],["Botswana",24.0,-22.0,1.0],["Namibia",17.3,-21.5,0.8],["South Africa",24.6,-29.6,0.6],["Lesotho",28.3,-29.6,4],["Eswatini",31.5,-26.5,5],["Madagascar",46.8,-19.5,0.9],["Burundi",29.9,-3.35,4],["Congo",15.4,-0.7,1.4],["Gabon",11.8,-0.6,1.6],["Ghana",-1.2,7.9,2.0],["Côte d’Ivoire",-5.5,7.6,1.6],["Liberia",-9.4,6.5,2.8],["Benin",2.3,9.5,3.4],["Togo",1.0,8.5,4],["Eq. Guinea",10.3,1.7,4.5],["Cabo Verde",-23.9,15.9,3]
];
const FIQH = [{n:"Makkah",c:[39.95,21.40],km:40},{n:"Madinah",c:[39.61,24.47],km:45},{n:"Khaybar",c:[39.29,25.70],km:30},{n:"Yanbuʿ",c:[38.20,24.12],km:30},{n:"al-Yamāmah",c:[46.85,24.45],km:95}];
const MUQ_VIEWS = [
  {id:"tabari", label:"al-Ṭabarī's outer limit: between the Euphrates and al-ʿArīsh"},
  {id:"qatadah", label:"Qatādah: al-Shām (core shown)"},
  {id:"kalbi", label:"al-Kalbī: Dimashq, Filasṭīn and part of al-Urdunn"},
  {id:"dahhak", label:"al-Ḍaḥḥāk: Īliyāʾ and Bayt al-Maqdis"},
  {id:"ikrimah", label:"Ibn ʿAbbās (via ʿIkrimah), al-Suddī, Ibn Zayd: Arīḥāʾ"},
  {id:"mujahid", label:"Mujāhid and Ibn ʿAbbās: al-Ṭūr and around it (not drawn)"}
];
