
(function(){
'use strict';
var T={
 uz:{kicker:"Bepul · 30 soniya · Chop etsa bo'ladi",
  h1:'Shaxsiy IELTS <span class="fl">o\'quv reja</span> generatori',
  lead:"Uchta savolga javob bering — haftama-hafta reja va halol baho oling: vaqtingiz yetadimi yoki imtihonni surish kerakmi.",
  q1:"1 · Hozirgi balingiz (mock natijasi)", q2:"2 · Maqsad band", q3:"3 · Imtihongacha necha hafta bor?", q4:"4 · Eng kuchsiz bo'limingiz",
  gen:"Rejani tuzish →", ctaT:"Reja mock testsiz ishlamaydi", ctaS:"100+ bepul IELTS mock — real formatda, bir zumda band ball",
  l1:"Grant muddatlari →", l2:"Ball konvertori →", l3:"Speaking mavzular →",
  vOkT:"✅ Real maqsad", vOk:"Bu masofa uchun vaqtingiz yetarli. Quyidagi rejaga har kuni 45–60 daqiqa bering — mock'laringiz {t} ga chiqqanda imtihonni band qiling.",
  vTightT:"⚠️ Tig'iz, lekin mumkin", vTight:"Qoida: 0.5 band ≈ 6–8 hafta kunlik mashq. Sizning masofangiz uchun vaqt tig'iz — reja har kuni bajarilsagina yetadi. Bitta ehtiyot varianti: {osr} dan xabardor bo'ling.",
  vHardT:"❌ Halol gap: vaqt yetmaydi", vHard:"{d} band ko'tarish uchun {need}+ hafta kerak, sizda {w} hafta bor. Ikki yo'l: imtihon sanasini suring, yoki maqsadni bosqichlab oling (avval {mid}). Baribir reja quyida — maksimal foyda uchun.",
  osr:"One Skill Retake (bitta bo'limni qayta topshirish)",
  ph1:"1-bosqich — Diagnostika va poydevor", ph2:"2-bosqich — Hajm", ph3:"3-bosqich — Imtihon rejimi",
  wk:"hafta", perday:"har kuni 45–60 daq",
  print:"🖨 Chop etish / PDF", share:"↗ Telegram'da ulashish", redo:"↺ Qayta tuzish",
  p1:["To'liq mock bilan boshlang — <a href='/ielts-hub/'>bepul, hub'da</a>: real boshlang'ich nuqtangizni biling.",
      "Har kuni faqat <b>{weak}</b> ustida ishlang: bitta section, keyin har xatoning SABABI tahlili.",
      "Xatolar daftari yuriting — 10 sessiondan keyin naqsh chiqadi.",
      "Haftada 2 marta: <a href='/speaking-topics/'>Speaking mavzular</a>dan 2 ta hikoya tayyorlang."],
  p2:["Kuniga bitta to'liq section (aralash) + kuchsiz bo'limga qo'shimcha 20 daq.",
      "Har hafta 1 ta <a href='/mock/'>to'liq mock</a> — real vaqtda, tanaffussiz.",
      "Writing: haftada 3 essay, bir xil turda — <a href='/writing/'>Writing lab</a>da tekshiring.",
      "Speaking: o'zingizni yozib oling va qayta eshiting — <a href='/speaking/'>Speaking lab</a>."],
  p3:["Har mock — imtihon simulyatsiyasi: telefonsiz, real taymer bilan.",
      "Faqat xato TURLARINGIZNI qaytaring: yangi material yo'q, mustahkamlash bor.",
      "Mock'lar barqaror maqsad+0.5 ko'rsatsa — tayyorsiz. <a href='/band-calculator/'>Band kalkulyator</a> bilan tekshiring.",
      "Oxirgi 3 kun: yengil takror, uyqu, va <a href='/news/computer-vs-paper-ielts-results/'>natija muddatlari</a>ni bilib qo'ying."]},
 en:{kicker:"Free · 30 seconds · Printable",
  h1:'Personal IELTS <span class="fl">study plan</span> generator',
  lead:"Answer three questions — get a week-by-week plan and an honest verdict: is your timeline enough, or should you move the exam?",
  q1:"1 · Current band (mock result)", q2:"2 · Target band", q3:"3 · Weeks until the exam", q4:"4 · Weakest skill",
  gen:"Build my plan →", ctaT:"A plan doesn't work without mocks", ctaS:"100+ free IELTS mocks — real format, instant band scores",
  l1:"Deadlines →", l2:"Score converter →", l3:"Speaking topics →",
  vOkT:"✅ Realistic goal", vOk:"Your timeline fits this distance. Give the plan 45–60 minutes daily — book the exam once your mocks hit {t}.",
  vTightT:"⚠️ Tight, but possible", vTight:"Rule of thumb: 0.5 band ≈ 6–8 weeks of daily work. Your window is tight — the plan only works if you do it every day. Keep {osr} in mind as a safety net.",
  vHardT:"❌ Honest verdict: not enough time", vHard:"Raising {d} band needs {need}+ weeks; you have {w}. Two options: move the exam date, or stage the goal (reach {mid} first). The plan below still maximises what you can gain.",
  osr:"One Skill Retake",
  ph1:"Phase 1 — Diagnose & foundation", ph2:"Phase 2 — Volume", ph3:"Phase 3 — Exam mode",
  wk:"weeks", perday:"45–60 min daily",
  print:"🖨 Print / PDF", share:"↗ Share on Telegram", redo:"↺ Rebuild",
  p1:["Start with one full mock — <a href='/ielts-hub/'>free, on the hub</a>: know your true baseline.",
      "Work only on <b>{weak}</b> daily: one section, then analyse WHY each miss happened.",
      "Keep a mistake journal — a pattern appears after ~10 sessions.",
      "Twice a week: prepare 2 flexible stories from <a href='/speaking-topics/'>Speaking topics</a>."],
  p2:["One full section daily (mixed skills) + 20 extra minutes on your weak skill.",
      "One <a href='/mock/'>full mock</a> every week — real timing, no breaks.",
      "Writing: 3 essays a week, same task type — check them in the <a href='/writing/'>Writing lab</a>.",
      "Speaking: record yourself and listen back — <a href='/speaking/'>Speaking lab</a>."],
  p3:["Every mock is a full dress rehearsal: no phone, real timers.",
      "Revisit only your mistake TYPES — no new material, just consolidation.",
      "When mocks sit steadily at target+0.5 — you're ready. Verify with the <a href='/band-calculator/'>band calculator</a>.",
      "Final 3 days: light review, sleep, and check <a href='/news/computer-vs-paper-ielts-results/'>result timelines</a>."]}
};
var ui=(window.FSPaper&&FSPaper.locale())||'en';
var $=function(s){return document.querySelector(s)};
var BANDS=['4.0','4.5','5.0','5.5','6.0','6.5','7.0','7.5'];
var TGT=['5.5','6.0','6.5','7.0','7.5','8.0'];
function pills(box,vals,def){
  box.innerHTML=vals.map(function(v){return '<button data-v="'+v+'"'+(v===def?' class="on"':'')+'>'+v+'</button>'}).join('');
}
pills($('#qCur'),BANDS,'5.5'); pills($('#qTgt'),TGT,'6.5');
document.querySelectorAll('.opts').forEach(function(g){
  g.addEventListener('click',function(e){
    var b=e.target.closest('button'); if(!b)return;
    g.querySelectorAll('button').forEach(function(x){x.classList.remove('on')});
    b.classList.add('on');
  });
});
function val(id){var b=document.querySelector(id+' button.on');return b?b.getAttribute('data-v'):null}
function applyUI(){
  var d=T[ui];
  document.querySelectorAll('[data-k]').forEach(function(el){var k=el.getAttribute('data-k');if(d[k]!=null)el.innerHTML=d[k]});
  if(!$('#result').hidden) build();
}
document.addEventListener('fs:lang',function(e){ui=e.detail.locale;applyUI();});
function build(){
  var d=T[ui];
  var cur=parseFloat(val('#qCur')), tgt=parseFloat(val('#qTgt'));
  var w=parseInt(val('#qWk'),10), weak=val('#qWeak');
  if(tgt<=cur) tgt=cur+0.5;
  var dist=Math.round((tgt-cur)*2)/2;
  var need=Math.round(dist*2*7);            // ~7 weeks per 0.5 band
  var cls,vt,vb;
  if(w>=need){cls='ok';vt=d.vOkT;vb=d.vOk.replace('{t}',(tgt+0.0).toFixed(1));}
  else if(w>=need*0.6){cls='tight';vt=d.vTightT;vb=d.vTight.replace('{osr}',"<a href='/news/ielts-one-skill-retake-uzbekistan/'>"+d.osr+"</a>");}
  else{cls='hard';vt=d.vHardT;vb=d.vHard.replace('{d}',dist.toFixed(1)).replace('{need}',need).replace('{w}',w).replace('{mid}',(cur+0.5).toFixed(1));}
  var w1=Math.max(1,Math.round(w*0.3)), w3=Math.max(1,Math.round(w*0.25)), w2=Math.max(1,w-w1-w3);
  var weakName={listening:'Listening',reading:'Reading',writing:'Writing',speaking:'Speaking'}[weak];
  function phase(title,weeks,items){
    return '<div class="phase"><div class="ph-meta">'+weeks+' '+d.wk+' · '+d.perday+'</div><h3>'+title+'</h3><ul>'+
      items.map(function(i){return '<li>'+i.replace('{weak}',weakName)+'</li>'}).join('')+'</ul></div>';
  }
  var h='<div class="verdict '+cls+'"><b>'+vt+'</b>'+vb+'</div>'+
    phase(d.ph1,w1,d.p1)+phase(d.ph2,w2,d.p2)+phase(d.ph3,w3,d.p3)+
    '<div class="pr-actions">'+
    '<button onclick="window.print()">'+d.print+'</button>'+
    '<a href="https://t.me/share/url?url='+encodeURIComponent('https://flarestamina.com/plan/')+'&text='+encodeURIComponent((ui==='uz'?'IELTS uchun shaxsiy o\'quv reja tuzdim — ':'I built my IELTS study plan — ')+cur.toFixed(1)+' → '+tgt.toFixed(1)+' ('+w+' '+d.wk+')')+'" target="_blank" rel="noopener">'+d.share+'</a>'+
    '<button onclick="document.getElementById(\'result\').hidden=true;window.scrollTo({top:0,behavior:\'smooth\'})">'+d.redo+'</button></div>';
  var r=$('#result'); r.innerHTML=h; r.hidden=false;
  r.scrollIntoView({behavior:'smooth',block:'start'});
  if(window.goatcounter&&goatcounter.count)goatcounter.count({path:'event/plan-built',event:true});
}
$('#go').addEventListener('click',build);
applyUI();
})();
