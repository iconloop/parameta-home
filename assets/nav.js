/* PARAMETA GNB — 단일 소스 (원본 parameta-home nav.js 패턴).
   배너 + 헤더 + 오버레이 메뉴 마크업을 모든 페이지의 <header id="header"> 자리에 주입.
   여기 한 번 고치면 전 페이지 즉시 반영. 스타일은 각 페이지 <style>(parameta.html에서 파생).
   담당: 마크업 주입 · 시계 · 스티키. (오버레이 열고닫기/모달은 페이지 모듈 JS 담당) */
(function(){
  var header = document.getElementById('header');
  if (!header) return;

  /* ---- 배너: 히어로에선 없음 — 스티키 스택에서만 등장 (#banner-fixed) ---- */
  var bannerFixed = document.getElementById('banner-fixed');
  if (!bannerFixed){
    bannerFixed = document.createElement('div');
    bannerFixed.id = 'banner-fixed';
    bannerFixed.setAttribute('aria-label', '공지');
    bannerFixed.innerHTML = '<a href="contact.html"><span class="b-strong">스테이블코인·STO 도입을 고민하고 계신가요?</span><span class="b-cta">Let\'s Talk →</span></a>';
    document.body.appendChild(bannerFixed);
  }

  /* ---- 헤더 (GNB) ---- */
  header.innerHTML = '\
  <div class="shell header-inner">\
    <a class="brand-btn" href="parameta.html" aria-label="PARAMETA home">\
      <span class="hspring" style="align-items:center;">\
        <img class="brand-logo" src="assets/brand/logo-horizontal-light.svg" alt="PARAMETA">\
      </span>\
    </a>\
    <nav class="nav-primary" aria-label="Primary">\
      <ul>\
        <li><a href="company.html"><span class="nav-lift" style="display:inline-flex">About</span></a></li>\
        <li class="has-drop"><a href="parasta.html" data-mega="products"><span class="nav-lift" style="display:inline-flex">Products</span></a></li>\
        <li class="has-drop"><a href="solution-finance.html" data-mega="solutions"><span class="nav-lift" style="display:inline-flex">Solutions</span></a></li>\
        <li class="has-drop"><a href="insights.html" data-mega="insights"><span class="nav-lift" style="display:inline-flex">Media</span></a></li>\
      </ul>\
    </nav>\
    <div class="header-right">\
      <div class="lang-wrap">\
        <button class="lang-btn" data-lang-toggle aria-label="언어 선택" aria-haspopup="true" aria-expanded="false">\
          <svg class="lang-globe" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.6 2.6 3.9 5.7 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.7-3.9-9S9.4 5.6 12 3z"/></svg>\
        </button>\
        <div class="lang-menu" role="menu">\
          <button class="lang-item is-active" data-lang="ko" role="menuitem">한국어</button>\
          <button class="lang-item" data-lang="en" role="menuitem">English</button>\
        </div>\
      </div>\
      <button class="menu-btn hs-scale" data-open-menu aria-label="메뉴 열기">\
        <span class="hspring">\
          <svg class="icn" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/></svg>\
          <span class="menu-word">Menu</span>\
        </span>\
      </button>\
    </div>\
  </div>';

  /* ---- 메가 드롭다운 (공유 박스 · 화면 중앙 · 리사이즈 모프) ---- */
  var mega = document.getElementById('mega');
  if (!mega){
    mega = document.createElement('div');
    mega.className = 'mega'; mega.id = 'mega'; mega.setAttribute('aria-hidden', 'true');
    mega.innerHTML = '\
    <div class="mega-inner">\
      <div class="mega-panel" data-for="solutions"><div class="nav-drop-panel duo">\
        <div class="nd-col">\
          <a href="solution-finance.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="12" r="5"/><path d="M14 7a5 5 0 0 1 0 10"/></svg></span><span class="nd-txt"><b>금융</b><span>금융기관용 디지털자산 인프라</span></span></a>\
          <a href="solution-settlement.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18"/></svg></span><span class="nd-txt"><b>결제·정산</b><span>정산 자동화·자금 통제</span></span></a>\
          <a href="solution-exchange.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h13l-3-3"/><path d="M20 16H7l3 3"/></svg></span><span class="nd-txt"><b>디지털자산 거래</b><span>자사 서비스 안 거래 기능</span></span></a>\
        </div>\
        <div class="nd-col">\
          <a href="solution-gov.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 21V8l7-4 7 4v13"/><path d="M9.5 21v-4h5v4"/></svg></span><span class="nd-txt"><b>공공</b><span>CSAP 인증 블록체인 SaaS</span></span></a>\
          <a href="solution-cert.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M9 15l2 2 4-4"/></svg></span><span class="nd-txt"><b>증명서</b><span>블록체인 기반 디지털 증명</span></span></a>\
          <a href="solution-data.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 4v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7z"/></svg></span><span class="nd-txt"><b>데이터주권</b><span>사용자 통제 데이터 인프라</span></span></a>\
        </div>\
      </div></div>\
      <div class="mega-panel" data-for="products"><div class="nav-drop-panel">\
        <a href="parasta.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 12l9 5 9-5"/><path d="M3 16.5l9 5 9-5"/></svg></span><span class="nd-txt"><b>ParaSta</b><span>디지털자산 금융 인프라</span></span></a>\
        <a href="portx.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h13l-3-3"/><path d="M20 16H7l3 3"/></svg></span><span class="nd-txt"><b>PortX</b><span>디지털자산 거래 솔루션</span></span></a>\
        <a href="myid.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-6 8-6s8 2 8 6"/></svg></span><span class="nd-txt"><b>MyID</b><span>분산신원(DID) 솔루션</span></span></a>\
        <a href="broof.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M9 15l2 2 4-4"/></svg></span><span class="nd-txt"><b>broof</b><span>블록체인 증명서 발급·검증</span></span></a>\
      </div></div>\
      <div class="mega-panel" data-for="insights"><div class="nav-drop-panel">\
        <a href="insights.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h13a2 2 0 0 1 2 2v11a2 2 0 0 0 2-2V8"/><rect x="4" y="5" width="13" height="14" rx="2"/><path d="M8 9h5M8 13h5M8 17h3"/></svg></span><span class="nd-txt"><b>Newsroom</b><span>파라메타 소식, 보도자료</span></span></a>\
        <a href="blog.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.8 2.8 0 0 1 4 4L8 20l-5 1 1-5z"/></svg></span><span class="nd-txt"><b>Blog</b><span>테크, 산업동향 이야기</span></span></a>\
        <a href="resources.html"><span class="nd-ico"><svg class="icn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M4 21h16"/></svg></span><span class="nd-txt"><b>Resources</b><span>로고, 용어정리, FAQ</span></span></a>\
      </div></div>\
    </div>';
    document.body.appendChild(mega);
  }
  var megaInner = mega.querySelector('.mega-inner');
  var megaPanels = mega.querySelectorAll('.mega-panel');
  var megaTriggers = header.querySelectorAll('[data-mega]');
  var megaCloseT, megaInit = false;
  function megaPlace(){
    var hi = header.querySelector('.header-inner') || header;
    mega.style.top = hi.getBoundingClientRect().bottom + 'px';
  }
  function megaSize(p){ if (p){ megaInner.style.width = p.offsetWidth + 'px'; megaInner.style.height = p.offsetHeight + 'px'; } }
  function megaOpen(key){
    clearTimeout(megaCloseT);
    megaPlace();
    var act = null;
    megaPanels.forEach(function(p){ var on = p.getAttribute('data-for') === key; p.classList.toggle('active', on); if (on) act = p; });
    if (!megaInit){ megaInner.style.transition = 'none'; megaSize(act); void megaInner.offsetWidth; megaInner.style.transition = ''; megaInit = true; }
    else megaSize(act);
    mega.classList.add('open'); mega.setAttribute('aria-hidden', 'false');
  }
  function megaClose(){ megaCloseT = setTimeout(function(){ mega.classList.remove('open'); mega.setAttribute('aria-hidden', 'true'); }, 140); }
  megaTriggers.forEach(function(t){
    var key = t.getAttribute('data-mega');
    t.addEventListener('pointerenter', function(){ megaOpen(key); });
    t.addEventListener('pointerleave', megaClose);
    t.addEventListener('focus', function(){ megaOpen(key); });
    /* 드롭다운 트리거는 클릭/탭해도 페이지 이동 막기 (hover/탭으로 열기만) */
    t.addEventListener('click', function(e){ e.preventDefault(); megaOpen(key); });
  });
  mega.addEventListener('pointerenter', function(){ clearTimeout(megaCloseT); });
  mega.addEventListener('pointerleave', megaClose);
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape'){ mega.classList.remove('open'); mega.setAttribute('aria-hidden', 'true'); } });
  window.addEventListener('scroll', function(){ if (mega.classList.contains('open')) megaPlace(); }, { passive: true });
  window.addEventListener('resize', function(){ if (mega.classList.contains('open')) megaPlace(); });

  /* ---- 오버레이 메뉴 (투뎁스) ---- */
  if (!document.getElementById('navmenu')){
    var nm = document.createElement('div');
    nm.id = 'navmenu';
    nm.setAttribute('aria-hidden', 'true');
    var ARR_R = '<svg class="nav-arrow" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M9 6l6 6-6 6"/></svg>';
    var ARR_L = '<svg class="nav-arrow" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M15 6l-6 6 6 6"/></svg>';
    nm.innerHTML = '\
    <div class="navmenu-top">\
      <button class="navmenu-close" data-close-menu><svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 4l16 16M20 4 4 20"/></svg><span class="cls-word">Close</span></button>\
    </div>\
    <div class="navmenu-body">\
      <nav class="navmenu-l1" aria-label="Overlay">\
        <ul>\
          <li><a class="navmenu-item" href="company.html">About</a></li>\
          <li><button class="navmenu-item" data-subpanel="products" aria-haspopup="true">Products' + ARR_R + '</button></li>\
          <li><button class="navmenu-item" data-subpanel="solutions" aria-haspopup="true">Solutions' + ARR_R + '</button></li>\
          <li><button class="navmenu-item" data-subpanel="insights" aria-haspopup="true">Media' + ARR_R + '</button></li>\
          <li><a class="navmenu-item" href="contact.html">Contact</a></li>\
        </ul>\
      </nav>\
      <nav class="navmenu-l2" data-panel="products" aria-label="Products">\
        <button class="navmenu-back" data-back>' + ARR_L + 'Products</button>\
        <ul>\
          <li><a href="parasta.html">ParaSta</a></li>\
          <li><a href="portx.html">PortX</a></li>\
          <li><a href="myid.html">MyID</a></li>\
          <li><a href="broof.html">broof</a></li>\
        </ul>\
      </nav>\
      <nav class="navmenu-l2" data-panel="solutions" aria-label="Solutions">\
        <button class="navmenu-back" data-back>' + ARR_L + 'Solutions</button>\
        <ul>\
          <li><a href="solution-finance.html">금융</a></li>\
          <li><a href="solution-gov.html">공공</a></li>\
          <li><a href="solution-cert.html">증명서</a></li>\
          <li><a href="solution-exchange.html">디지털자산 거래</a></li>\
          <li><a href="solution-data.html">데이터주권</a></li>\
          <li><a href="solution-settlement.html">결제·정산</a></li>\
        </ul>\
      </nav>\
      <nav class="navmenu-l2" data-panel="insights" aria-label="Media">\
        <button class="navmenu-back" data-back>' + ARR_L + 'Media</button>\
        <ul>\
          <li><a href="insights.html">Newsroom</a></li>\
          <li><a href="blog.html">Blog</a></li>\
          <li><a href="resources.html">Resources</a></li>\
        </ul>\
      </nav>\
    </div>';
    document.body.appendChild(nm);
    /* ---- 드릴다운: 항목 누르면 해당 패널 인, 뒤로가기로 아웃 ---- */
    nm.querySelectorAll('[data-subpanel]').forEach(function(b){
      b.addEventListener('click', function(){ nm.setAttribute('data-view', b.getAttribute('data-subpanel')); });
    });
    nm.querySelectorAll('[data-back]').forEach(function(b){
      b.addEventListener('click', function(){ nm.removeAttribute('data-view'); });
    });
  }

  /* ---- 시계 ---- */
  var MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  function fmtTime(d){
    var hh = d.getHours() % 12; if (hh === 0) hh = 12;
    var m = String(d.getMinutes()).padStart(2, '0');
    return hh + ':' + m + (d.getHours() >= 12 ? 'pm' : 'am');
  }
  var clockTime = document.getElementById('clockTime');
  var clockDate = document.getElementById('clockDate');
  var navmenuTime = document.getElementById('navmenuTime');
  function tickClock(){
    var d = new Date(), t = fmtTime(d);
    if (clockTime) clockTime.textContent = t;
    if (clockDate) clockDate.textContent = d.getDate() + ' ' + MONTHS[d.getMonth()] + ', ' + d.getFullYear();
    if (navmenuTime) navmenuTime.textContent = 'Local time — ' + t;
  }
  tickClock();
  setInterval(tickClock, 1000);

  /* ---- 언어 선택 드롭다운 (모양만 · 실제 번역은 아직 없음) ---- */
  var langWrap = document.querySelector('.lang-wrap');
  var langBtn = langWrap && langWrap.querySelector('[data-lang-toggle]');
  var langMenu = langWrap && langWrap.querySelector('.lang-menu');
  if (langBtn && langMenu){
    langBtn.addEventListener('click', function(e){
      e.stopPropagation();
      var open = langMenu.classList.toggle('open');
      langBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    langMenu.querySelectorAll('.lang-item').forEach(function(it){
      it.addEventListener('click', function(){
        langMenu.querySelectorAll('.lang-item').forEach(function(o){ o.classList.toggle('is-active', o === it); });
        document.documentElement.lang = it.dataset.lang;
        langMenu.classList.remove('open');
        langBtn.setAttribute('aria-expanded', 'false');
      });
    });
    document.addEventListener('click', function(e){
      if (!langWrap.contains(e.target)){ langMenu.classList.remove('open'); langBtn.setAttribute('aria-expanded', 'false'); }
    });
  }

  /* ---- 스티키: 상단에선 GNB만(배너 없음) → 히어로를 벗어나면 배너+GNB 슬라이드 인 ---- */
  var heroEl = document.querySelector('#home') || document.querySelector('.phero');
  var ctaEl = document.querySelector('#home .hero-cta'); /* 메인: CTA 버튼 지나면 등장 */
  function stickThreshold(){
    /* 태블릿·모바일(<1024): 히어로 전체 대신 약 1스크린만 내려가면 GNB 등장(트리거 앞당김) */
    if (window.innerWidth < 1024) return Math.round(window.innerHeight * 0.5);
    if (ctaEl) return ctaEl.getBoundingClientRect().bottom + (window.scrollY || 0);
    if (!heroEl) return 240;
    return heroEl.offsetTop + heroEl.offsetHeight * 0.5; /* PC 서브: 히어로 절반 지점 */
  }
  var brandImg = header.querySelector('.brand-logo');
  var darkHero = document.body.classList.contains('hero-dark');
  function updateHeaderStick(){
    var y = window.scrollY || 0;
    var stick = y > stickThreshold();
    header.classList.toggle('sticky', stick);
    bannerFixed.classList.toggle('show', stick);
    header.style.top = stick ? bannerFixed.offsetHeight + 'px' : '0px';
    if (mega) mega.classList.toggle('on-dark', darkHero && !stick);
    /* 다크 히어로: 스티키 전엔 화이트 로고, 스티키 후엔 컬러 로고 */
    if (darkHero && brandImg){
      brandImg.src = stick
        ? 'assets/brand/logo-horizontal-light.svg'
        : 'assets/brand/logo-horizontal-color-dark.svg';
    }
  }
  updateHeaderStick();
  window.addEventListener('scroll', updateHeaderStick, { passive: true });
  window.addEventListener('resize', updateHeaderStick);
})();
