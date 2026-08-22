
(function(){
  'use strict';
  var FS='https://firestore.googleapis.com/v1/projects/pangeya-essay/databases/(default)/documents';
  var KEY='AIzaSyBnmbg7CyLki-M1E4rxPevJ741yTykliDA';
  var DRAFT='fs_article_draft';

  /* ---------- i18n ---------- */
  var T={
    uz:{
      back:'← news',
      kicker:'Ustozlar uchun ochiq minbar',
      h1:"Maqola yozing — minglab o'quvchi o'qisin",
      lead:'IELTS bo’yicha tajribangizni ulashing. Maqolangiz <b>flarestamina.com/news</b> sahifasida chiqadi — ismingiz, ijtimoiy tarmog’ingiz va o’quv markazingiz linki bilan. Ro’yxatdan o’tish shart emas.',
      s1:'yozasiz', s2:'"Yuklash"ni bosasiz', s3:"news'da chiqadi ✓",
      tipsH:'Yaxshi maqola formulasi:',
      tipsB:"aniq sarlavha · 3–6 qisqa abzats (abzatslar orasida bo'sh qator) · o'z tajribangizdan 1 ta misol · oxirida amaliy xulosa. Maqolangiz bir necha soat ichida o'z sahifasi va linkiga ega bo'ladi — uni o'quvchilaringizga ulashishingiz mumkin.",
      lblArtLang:'Maqola tili', hintArtLang:'— qaysi tilda yozasiz',
      lblTitle:'Maqola mavzusi', hintTitle:'— sarlavha',
      phTitle:"Masalan: Writing Task 2 da eng ko'p uchraydigan 5 xato",
      lblBody:'Maqola matni', hintBody:'— kamida 200 belgi, xohlagancha uzun',
      phBody:"Maqolangizni shu yerga yozing... Abzatslar uchun bo'sh qator qoldiring.",
      lblName:'Ism-familiya',
      phName:'Masalan: Nodir Karimov',
      lblCenter:"O'quv markazingiz", hintOpt:'— ixtiyoriy',
      phCenter:'Masalan: Everest Education, Toshkent',
      lblLink:'Telegram / Instagram / YouTube yoki markaz sayti', hintLink:'— ixtiyoriy, o’zingizni tanishtiring',
      submit:"Yuklash → news'da chiqadi",
      note:'Yuklash bilan siz maqola o’zingizniki ekanini va ochiq chop etilishiga rozilikni tasdiqlaysiz. Matn avtomatik saqlanib boradi — sahifa yopilsa ham yo’qolmaydi.',
      doneH:'Maqolangiz chiqdi!',
      doneP:'Rahmat, ustoz! Maqolangiz endi news sahifasining <b>Articles</b> bo’limida turibdi. Bir necha soat ichida u o’z sahifasi va linkiga ham ega bo’ladi — Google topadigan, ulashsa bo’ladigan.',
      doneView:"Maqolamni ko'rish →", doneMore:'+ yana maqola yozish',
      errTitle:'Maqola mavzusini yozing (kamida 5 belgi).',
      errBody:'Maqola matni juda qisqa — kamida 200 belgi yozing. Hozir: ',
      errName:'Ism-familiyangizni yozing.',
      errNet:"Xatolik yuz berdi — internetni tekshirib qayta urinib ko'ring. Matningiz saqlangan, yo'qolmaydi.",
      posting:'Yuklanmoqda...'
    },
    en:{
      back:'← news',
      kicker:'Open stage for teachers',
      h1:'Write an article — reach thousands of students',
      lead:'Share your IELTS experience. Your article appears on <b>flarestamina.com/news</b> — with your name, social link and learning-centre link. No sign-up needed.',
      s1:'you write', s2:'you tap "Publish"', s3:'it appears on news ✓',
      tipsH:'The good-article formula:',
      tipsB:'a clear title · 3–6 short paragraphs (blank line between them) · one example from your own teaching · a practical takeaway at the end. Within a few hours your article gets its own page and link — share it with your students.',
      lblArtLang:'Article language', hintArtLang:'— which language you write in',
      lblTitle:'Article title', hintTitle:'— headline',
      phTitle:'e.g. The 5 most common mistakes in Writing Task 2',
      lblBody:'Article text', hintBody:'— at least 200 characters, as long as you like',
      phBody:'Write your article here... Leave a blank line between paragraphs.',
      lblName:'Full name',
      phName:'e.g. Nodir Karimov',
      lblCenter:'Your learning centre', hintOpt:'— optional',
      phCenter:'e.g. Everest Education, Tashkent',
      lblLink:'Telegram / Instagram / YouTube or centre website', hintLink:'— optional, introduce yourself',
      submit:'Publish → appears on news',
      note:'By publishing you confirm the article is yours and agree to it being published publicly. Your text is auto-saved — it won’t be lost if the page closes.',
      doneH:'Your article is live!',
      doneP:'Thank you! Your article is now in the <b>Articles</b> tab on the news page. Within a few hours it also gets its own page and shareable link — indexed by Google.',
      doneView:'View my article →', doneMore:'+ write another article',
      errTitle:'Please write an article title (at least 5 characters).',
      errBody:'The article text is too short — write at least 200 characters. Now: ',
      errName:'Please write your name.',
      errNet:'Something went wrong — check your connection and try again. Your text is saved, it won’t be lost.',
      posting:'Publishing...'
    }
  };
  var ui=(window.FSPaper&&FSPaper.locale())||'en';

  var $=function(id){return document.getElementById(id)};
  function applyUI(){
    var d=T[ui];
    document.querySelectorAll('[data-k]').forEach(function(el){
      var k=el.getAttribute('data-k'); if(d[k]!=null) el.innerHTML=d[k];
    });
    document.querySelectorAll('[data-kp]').forEach(function(el){
      var k=el.getAttribute('data-kp'); if(d[k]!=null) el.setAttribute('placeholder',d[k]);
    });
    updCounter();
  }
  document.addEventListener('fs:lang',function(e){ui=e.detail.locale;applyUI();});

  /* ---------- article language selector ---------- */
  var artLang='uz';
  document.querySelectorAll('#artLang .opt').forEach(function(o){
    o.addEventListener('click',function(){
      document.querySelectorAll('#artLang .opt').forEach(function(x){x.classList.remove('on')});
      o.classList.add('on'); artLang=o.getAttribute('data-l');
    });
  });

  /* ---------- form ---------- */
  var form=$('artForm'),title=$('fTitle'),body=$('fBody'),name=$('fName'),
      center=$('fCenter'),link=$('fLink'),hp=$('fHp'),btn=$('btnPub'),
      err=$('errBox'),counter=$('counter');

  try{
    var dr=JSON.parse(localStorage.getItem(DRAFT)||'null');
    if(dr){title.value=dr.t||'';body.value=dr.b||'';name.value=dr.n||'';center.value=dr.c||'';link.value=dr.l||'';}
  }catch(e){}
  function saveDraft(){
    try{localStorage.setItem(DRAFT,JSON.stringify({t:title.value,b:body.value,n:name.value,c:center.value,l:link.value}));}catch(e){}
  }
  [title,body,name,center,link].forEach(function(el){el.addEventListener('input',saveDraft)});

  function updCounter(){
    var n=body.value.trim().length;
    counter.textContent=n+' / 200';
    counter.className='counter'+(n>=200?' ok':'');
  }
  body.addEventListener('input',updCounter);
  /* textarea grows with the text — teachers never scroll inside a tiny box */
  function autosize(){ body.style.height='auto'; body.style.height=Math.max(320, body.scrollHeight+4)+'px'; }
  body.addEventListener('input',autosize); setTimeout(autosize,50);

  function fail(msg){err.textContent=msg;err.style.display='block';window.scrollTo({top:err.offsetTop-90,behavior:'smooth'})}

  form.addEventListener('submit',function(e){
    e.preventDefault();
    err.style.display='none';
    var d=T[ui];
    if(hp.value){return}
    var t=title.value.trim(),b=body.value.trim(),n=name.value.trim();
    if(t.length<5){fail(d.errTitle);return}
    if(b.length<200){fail(d.errBody+b.length);return}
    if(n.length<3){fail(d.errName);return}
    var l=link.value.trim();
    if(l && !/^https?:\/\//i.test(l)){l='https://'+l}

    btn.disabled=true;btn.textContent=d.posting;
    var doc={fields:{
      title:{stringValue:t},
      body:{stringValue:b},
      author:{stringValue:n},
      center:{stringValue:center.value.trim()},
      link:{stringValue:l},
      lang:{stringValue:artLang},
      hidden:{booleanValue:false},
      date:{stringValue:new Date().toISOString()},
      type:{stringValue:'article'},
      ua:{stringValue:(navigator.userAgent||'').slice(0,120)}
    }};
    fetch(FS+'/articles?key='+KEY,{
      method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(doc)
    }).then(function(r){
      if(!r.ok)throw new Error('HTTP '+r.status);
      return r.json();
    }).then(function(){
      try{localStorage.removeItem(DRAFT)}catch(e){}
      form.style.display='none';
      $('heroBlock').style.display='none';
      $('doneBox').style.display='block';
      window.scrollTo(0,0);
      if(window.goatcounter&&goatcounter.count)goatcounter.count({path:'event/article-published',event:true});
    }).catch(function(){
      btn.disabled=false;btn.textContent=d.submit;
      fail(d.errNet);
    });
  });

  applyUI();
})();
