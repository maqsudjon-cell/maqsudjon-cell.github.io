
(function(){
'use strict';
/* Deadlines data. status: c=confirmed, e=expected, w=watch(no date). kind: deadline|opens */
var D=[
 {n:"Chevening 2027/28",date:"2026-10-06",st:"c",kind:"deadline",post:"/news/chevening-2027/",off:"https://www.chevening.org"},
 {n:"IELTS Speaking topics rotation",date:"2026-09-01",st:"e",kind:"opens",post:"/speaking-topics/",off:"https://ielts.org"},
 {n:"GKS 2027 (Korea) — embassy track",date:"2026-09-15",st:"e",kind:"opens",post:"/news/gks-2027/",off:"https://www.studyinkorea.go.kr/en/main.do"},
 {n:"DAAD EPOS 2027 (Germany) — first deadlines",date:"2026-08-31",st:"e",kind:"deadline",post:"/news/daad-2027-germany/",off:"https://www.daad.de/en/"},
 {n:"Erasmus Mundus 2027 — portals open",date:"2026-10-15",st:"e",kind:"opens",post:"/news/erasmus-mundus-2027/",off:"https://erasmus-plus.ec.europa.eu"},
 {n:"Stipendium Hungaricum 2027/28",date:"2026-11-15",st:"e",kind:"opens",post:"/news/stipendium-hungaricum-2027/",off:"https://stipendiumhungaricum.hu"},
 {n:"CSC China 2027",date:"2026-12-01",st:"e",kind:"opens",post:"/news/csc-china-2027/",off:"https://www.campuschina.org"},
 {n:"Türkiye Bursları 2027",date:"2027-01-10",st:"e",kind:"opens",post:"/news/turkiye-burslari-2027/",off:"https://www.turkiyeburslari.gov.tr"},
 {n:"El-Yurt Umidi — keyingi tanlov",date:null,st:"w",kind:"watch",post:"/news/el-yurt-umidi-2026/",off:"https://eyuf.uz"}
];
var T={
 uz:{kicker:"Jonli hisoblagich · Har kuni yangilanadi",
     h1:'Grant muddatlari <span class="fl">2026–2027</span>',
     lead:"Barcha yirik stipendiyalar bitta sahifada — necha kun qolgani jonli hisoblanadi. Har karta bizning tayyorgarlik maqolamizga olib boradi. Saqlab qo'ying va haftada bir qarang.",
     note:'✅ tasdiqlangan = rasmiy e\'lon qilingan sana · ⏳ kutilmoqda = o\'tgan yillardagi jadval asosida taxmin · 👁 kuzatuvda = sana hali yo\'q. Sanalar o\'zgarishi mumkin — har doim rasmiy sahifani tekshiring. Yangi e\'lonlar <a href="https://t.me/flarestamina" rel="noopener">t.me/flarestamina</a> kanalida.',
     ctaT:"Deadline'gacha band ko'tarish kerakmi?", ctaS:"100+ bepul IELTS mock test — real formatda, bir zumda natija",
     lnk1:"Ball konvertori →", lnk2:"Yangiliklar →",
     day:"kun", today:"BUGUN!", passed:"o'tdi",
     stc:"✅ tasdiqlangan", ste:"⏳ kutilmoqda", stw:"👁 kuzatuvda",
     deadline:"deadline", opens:"ochiladi", watch:"e'lon kutilmoqda",
     guide:"tayyorgarlik →", official:"rasmiy sayt ↗"},
 en:{kicker:"Live countdown · Updates daily",
     h1:'Scholarship deadlines <span class="fl">2026–2027</span>',
     lead:"Every major scholarship on one page — with live day counters. Each card links to our preparation guide. Bookmark it and check weekly.",
     note:'✅ confirmed = officially announced date · ⏳ expected = estimate based on previous cycles · 👁 watch = no date yet. Dates can change — always verify on the official page. New announcements land on <a href="https://t.me/flarestamina" rel="noopener">t.me/flarestamina</a>.',
     ctaT:"Need a higher band before the deadline?", ctaS:"100+ free IELTS mocks — real format, instant scores",
     lnk1:"Score converter →", lnk2:"News →",
     day:"days", today:"TODAY!", passed:"passed",
     stc:"✅ confirmed", ste:"⏳ expected", stw:"👁 watch",
     deadline:"deadline", opens:"opens", watch:"awaiting announcement",
     guide:"prep guide →", official:"official site ↗"}
};
var ui=(window.FSPaper&&FSPaper.locale())||'en';
function esc(s){return String(s).replace(/</g,'&lt;')}
function daysTo(d){
  var now=new Date(); now=Date.UTC(now.getFullYear(),now.getMonth(),now.getDate());
  var p=d.split('-'); var t=Date.UTC(+p[0],+p[1]-1,+p[2]);
  return Math.round((t-now)/86400000);
}
function render(){
  var d=T[ui];
  document.querySelectorAll('[data-k]').forEach(function(el){var k=el.getAttribute('data-k'); if(d[k]!=null) el.innerHTML=d[k];});
  var items=D.slice().sort(function(a,b){
    if(!a.date) return 1; if(!b.date) return -1;
    return a.date.localeCompare(b.date);
  });
  var h='';
  items.forEach(function(x){
    var days=x.date?daysTo(x.date):null;
    var urgent=days!==null&&days>=0&&days<=45;
    var cnt = x.date===null ? '<div class="n">—</div><div class="u">'+d.stw.replace(/^..\s*/,'')+'</div>'
      : days<0 ? '<div class="n" style="color:var(--dim)">·</div><div class="u">'+d.passed+'</div>'
      : days===0 ? '<div class="n">0</div><div class="u">'+d.today+'</div>'
      : '<div class="n">'+days+'</div><div class="u">'+d.day+'</div>';
    var st=x.st==='c'?'<span class="st c">'+d.stc+'</span>':x.st==='e'?'<span class="st e">'+d.ste+'</span>':'<span class="st w">'+d.stw+'</span>';
    var kind=x.kind==='watch'?d.watch:d[x.kind];
    var dateTxt=x.date? x.date : '';
    h+='<div class="dl'+(urgent?' urgent':'')+'">'+
       '<div class="count">'+cnt+'</div>'+
       '<div class="inf"><h2>'+esc(x.n)+'</h2>'+
       '<div class="meta">'+st+'<span class="kind">'+kind+(dateTxt?' · '+dateTxt:'')+'</span>'+
       '<a href="'+x.post+'">'+d.guide+'</a>'+
       '<a href="'+x.off+'" target="_blank" rel="noopener nofollow">'+d.official+'</a></div></div></div>';
  });
  document.getElementById('list').innerHTML=h;
}
document.addEventListener('fs:lang',function(e){ui=e.detail.locale;render();});
render();
})();
