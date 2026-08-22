
(function(){
'use strict';
/* IELTS band -> equivalents. CEFR per ielts.org, TOEFL per ETS linking study, DET approximate. */
var MAP={
 '4.0':{cefr:'B1',ml:'B1',toefl:'32–34',det:'55–70'},
 '4.5':{cefr:'B1',ml:'B1',toefl:'32–34',det:'70–80'},
 '5.0':{cefr:'B1',ml:'B1',toefl:'35–45',det:'85–90'},
 '5.5':{cefr:'B2',ml:'B2',toefl:'46–59',det:'95–100'},
 '6.0':{cefr:'B2',ml:'B2',toefl:'60–78',det:'105–110'},
 '6.5':{cefr:'B2',ml:'B2',toefl:'79–93',det:'115–120'},
 '7.0':{cefr:'C1',ml:'C1',toefl:'94–101',det:'125–130'},
 '7.5':{cefr:'C1',ml:'C1',toefl:'102–109',det:'135–140'},
 '8.0':{cefr:'C1',ml:'C1',toefl:'110–114',det:'145–150'},
 '8.5':{cefr:'C2',ml:'C1',toefl:'115–117',det:'155–160'},
 '9.0':{cefr:'C2',ml:'C1',toefl:'118–120',det:'160'}
};
var T={
 uz:{kicker:"Bepul · Ro'yxatsiz · 2026",
     lead:"IELTS balingizni tanlang — CEFR darajasi, Multilevel ekvivalenti, TOEFL iBT va Duolingo bali, hamda DTM'dagi imtiyozingiz bir sekundda chiqadi.",
     cefrSub:"Yevropa darajasi", mlSub:"milliy sertifikat", toeflSub:"rasmiy ETS jadvali", detSub:"taxminiy",
     tblH:"To'liq taqqoslash jadvali", thDtm:"DTM (chet tili)", faqH:"Ko'p so'raladigan savollar",
     ctaT:"Darajangizni bilib oldingizmi? Endi ballni oshiring", ctaS:"100+ bepul IELTS mock test — real formatda, bir zumda band ball",
     lnkCalc:"Band kalkulyator →", lnkNews:"IELTS yangiliklari →",
     tblNote:"* Multilevel sertifikati eng yuqori daraja sifatida C1 beriladi. IELTS↔CEFR — ielts.org rasmiy moslamasi; IELTS↔TOEFL — ETS linking study; Duolingo — taxminiy, rasmiy konvertorda tekshiring. DTM imtiyozi amaldagi (muddati o'tmagan) sertifikatlarga beriladi.",
     dtmMax:"🎓 <b>DTM:</b> bu daraja (B2+) chet tilidan <b>maksimal ball</b> beradi — 1-fan bo'lsa <b>93.0</b>, 2-fan bo'lsa <b>63.0</b>. <a href='/news/ielts-dtm-maksimal-ball-2026/'>Qoidalarni o'qing →</a>",
     dtm75:"🎓 <b>DTM:</b> B1 daraja 2026-yildan maksimal ballning <b>75%</b> ini beradi. 5.5 ga yetsangiz — to'liq maksimal. <a href='/news/ielts-dtm-maksimal-ball-2026/'>Qoidalar →</a>",
     q1:"IELTS 6.5 — bu qaysi daraja?", q2:"Multilevel B2 IELTS nechchiga teng?", q3:"DTM'da maksimal ball olish uchun nima kerak?", q4:"TOEFL 90 — IELTS nechchi?", q5:"Duolingo testi IELTS o'rnini bosadimi?"},
 en:{kicker:"Free · No sign-up · 2026",
     lead:"Pick your IELTS band — instantly see the CEFR level, Uzbekistan Multilevel equivalent, TOEFL iBT and Duolingo scores, plus what it earns you at DTM.",
     cefrSub:"European level", mlSub:"national certificate", toeflSub:"official ETS table", detSub:"approximate",
     tblH:"Full comparison table", thDtm:"DTM (foreign language)", faqH:"Frequently asked questions",
     ctaT:"Know your level? Now raise the band", ctaS:"100+ free IELTS mocks — real format, instant band scores",
     lnkCalc:"Band calculator →", lnkNews:"IELTS news →",
     tblNote:"* Multilevel issues C1 as its highest level. IELTS↔CEFR per ielts.org; IELTS↔TOEFL per the ETS linking study; Duolingo is approximate — verify in the official converter. DTM privileges apply to valid (unexpired) certificates.",
     dtmMax:"🎓 <b>DTM:</b> this level (B2+) earns the <b>maximum foreign-language score</b> — <b>93.0</b> as first subject, <b>63.0</b> as second. <a href='/news/ielts-dtm-maksimal-ball-2026/'>Read the rules →</a>",
     dtm75:"🎓 <b>DTM:</b> B1 earns <b>75%</b> of the maximum from 2026. Reach 5.5 for the full maximum. <a href='/news/ielts-dtm-maksimal-ball-2026/'>Rules →</a>",
     q1:"What level is IELTS 6.5?", q2:"Multilevel B2 equals which IELTS band?", q3:"What do I need for the maximum DTM score?", q4:"TOEFL 90 — what IELTS band?", q5:"Does the Duolingo test replace IELTS?"}
};
var ui=(window.FSPaper&&FSPaper.locale())||'en';
var $=function(s){return document.querySelector(s)};
function applyUI(){
  var d=T[ui];
  document.querySelectorAll('[data-k]').forEach(function(el){var k=el.getAttribute('data-k'); if(d[k]!=null) el.innerHTML=d[k];});
  render(cur);
}
document.addEventListener('fs:lang',function(e){ui=e.detail.locale;applyUI();});
var bandsBox=$('#bands'), cur='6.5';
Object.keys(MAP).forEach(function(band){
  var btn=document.createElement('button');
  btn.textContent=band; btn.setAttribute('data-b',band);
  btn.addEventListener('click',function(){cur=band;render(band);
    if(window.goatcounter&&goatcounter.count)goatcounter.count({path:'event/convert-'+band,event:true});});
  bandsBox.appendChild(btn);
});
function render(band){
  var m=MAP[band], d=T[ui];
  document.querySelectorAll('#bands button').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-b')===band);});
  $('#r-cefr').textContent=m.cefr; $('#r-ml').textContent=m.ml;
  $('#r-toefl').textContent=m.toefl; $('#r-det').textContent=m.det;
  $('#dtm-note').innerHTML=(m.cefr==='B1')?d.dtm75:d.dtmMax;
}
applyUI();
})();
