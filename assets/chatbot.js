/* PARAMETA 챗봇 — 단일 소스.
   FAB(타이프라이터) + 우측 푸시 드로어 + 데모 채팅 UI를 전 페이지에 주입.
   실서비스 연결: window.PARAMETA_CHATBOT_URL 지정 시 데모 UI 대신 iframe 임베드.
   스타일은 각 페이지 <style>(parameta.html에서 파생). */
(function(){
  'use strict';

  /* ---- FAB ---- */
  var fab = document.createElement('button');
  fab.className = 'fab-chat';
  fab.id = 'fabChat';
  fab.type = 'button';
  fab.setAttribute('aria-label', '파라메타에게 물어보기');
  fab.innerHTML = '<span id="fabLabel">무엇이든 물어보세요</span><span class="fab-caret" aria-hidden="true"></span>';
  document.body.appendChild(fab);

  /* ---- 드로어 ---- */
  var CHAT_URL = window.PARAMETA_CHATBOT_URL || '';
  var panel = document.createElement('div');
  panel.className = 'pc-panel';
  panel.id = 'pcPanel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', '파라메타 챗봇');
  panel.innerHTML = '\
  <div class="pc-head">\
    <span class="pc-title"><img src="assets/brand/logo-horizontal-light.svg" alt="PARAMETA"><span class="pc-status"><span class="pc-dot"></span>온라인</span></span>\
    <button class="pc-close" type="button" aria-label="닫기"><svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 4l16 16M20 4 4 20"/></svg></button>\
  </div>\
  <div class="pc-body" id="pcBody"></div>';
  document.body.appendChild(panel);

  var body = panel.querySelector('#pcBody');

  /* ---- 데모 채팅 UI (기본) / iframe (URL 지정 시) ---- */
  var CHIPS = [
    '토큰 발행은 어떻게 하나요?',
    '온체인 KYC가 뭔가요?',
    'K-BTF 도입 절차가 궁금해요',
    '비용은 어떻게 되나요?',
  ];
  var QA = [
    { k:['회사','파라메타','어떤'], a:'파라메타는 블록체인 기반 디지털자산 인프라를 만드는 Web3 기술 기업이에요. 금융·기업·공공에 필요한 지갑, 토큰 발행, 신원인증, 온체인 KYC, 상호운용 기술을 제공합니다.' },
    { k:['parasta','파라스타','토큰','발행','스테이블','예금'], a:'토큰 발행은 ParaSta로 시작하시면 돼요. 스테이블코인·예금토큰·STO·RWA의 발행부터 지갑, 정산, 규제 대응까지 하나의 플랫폼으로 제공하고, SaaS와 온프레미스 모두 지원합니다.' },
    { k:['portx','포트엑스','거래소','화이트라벨'], a:'PortX는 화이트라벨 거래소 솔루션이에요. 매칭 엔진·호가창·보안 인프라를 직접 구축할 필요 없이, 자체 브랜드 거래 서비스를 빠르게 출시할 수 있습니다.' },
    { k:['myid','did','신원','인증'], a:'MyID는 W3C 표준 기반 DID(분산신원) 솔루션이에요. 약 370만 명이 사용 중이고, 금융실명인증·공공 신원증명 등에 적용돼 있습니다.' },
    { k:['kbtf','공공','조달'], a:'K-BTF는 블록체인 서비스 최초로 CSAP 인증을 받은 공공기관 전용 SaaS예요. 자체 구축 대비 도입 기간 약 1주일, 비용 최대 90% 절감이 가능합니다. 절차는 1:1 컨설팅에서 안내드려요.' },
    { k:['broof','증명서','수료증'], a:'Broof는 블록체인 증명서 발급·검증 서비스예요. 명단 업로드로 한 번에 발급하고, QR 하나로 위·변조 여부를 즉시 확인할 수 있습니다.' },
    { k:['kyc','aml','트래블'], a:'온체인 KYC는 한 번의 KYC로 여러 체인과 서비스에서 활용하는 신원인증이에요. AML·트래블룰 대응을 자동화해 컴플라이언스 부담을 줄여줍니다.' },
    { k:['비용','가격','견적','기간','poc','얼마'], a:'규모와 환경(SaaS/온프레미스)에 따라 달라서, 1:1 무료 컨설팅에서 정확히 안내드리고 있어요. 상단 배너나 Contact 페이지에서 신청해주세요!' },
    { k:['saas','온프레미스','구축'], a:'둘 다 지원해요. 파일럿은 SaaS로 빠르게 시작하고, 본격 운영 시 온프레미스로 전환하는 것도 가능합니다.' },
  ];
  var FALLBACK = '여기까지는 데모 챗봇이라 간단한 안내만 드릴 수 있어요. 자세한 내용은 1:1 무료 컨설팅으로 문의해주시면 담당자가 정확히 답변드립니다!';

  var msgs, input;
  function buildDemoUI(){
    body.innerHTML = '\
    <div class="pc-msgs" id="pcMsgs">\
      <div class="pc-msg bot">안녕하세요, 파라메타입니다 👋<br>디지털자산 인프라, 무엇이든 물어보세요.</div>\
      <div class="pc-chips">' + CHIPS.map(function(q){ return '<button type="button" class="pc-chip">' + q + '</button>'; }).join('') + '</div>\
    </div>\
    <form class="pc-input" id="pcForm">\
      <input type="text" id="pcText" placeholder="무엇이든 물어보세요" autocomplete="off" />\
      <button class="pc-send" type="submit" aria-label="보내기"><svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 19V5M6 11l6-6 6 6"/></svg></button>\
    </form>';
    msgs = body.querySelector('#pcMsgs');
    input = body.querySelector('#pcText');
    body.querySelector('#pcForm').addEventListener('submit', function(e){
      e.preventDefault();
      var q = input.value.trim();
      if (!q) return;
      input.value = '';
      send(q);
    });
    msgs.addEventListener('click', function(e){
      var chip = e.target.closest('.pc-chip');
      if (chip) send(chip.textContent);
    });
  }
  function addMsg(cls, html){
    var el = document.createElement('div');
    el.className = 'pc-msg ' + cls;
    el.innerHTML = html;
    msgs.appendChild(el);
    msgs.scrollTop = msgs.scrollHeight;
    return el;
  }
  function reply(q){
    var low = q.toLowerCase();
    for (var i = 0; i < QA.length; i++){
      for (var j = 0; j < QA[i].k.length; j++){
        if (low.indexOf(QA[i].k[j]) !== -1) return QA[i].a;
      }
    }
    return FALLBACK;
  }
  function send(q){
    var chips = msgs.querySelector('.pc-chips');
    if (chips) chips.remove();
    addMsg('user', q.replace(/</g, '&lt;'));
    var typing = addMsg('bot typing', '<span></span><span></span><span></span>');
    setTimeout(function(){
      typing.classList.remove('typing');
      typing.textContent = reply(q);
      msgs.scrollTop = msgs.scrollHeight;
    }, 700 + Math.random() * 500);
  }

  var built = false;
  function buildBody(){
    if (built) return;
    built = true;
    if (CHAT_URL){
      body.innerHTML = '<iframe class="pc-frame" title="파라메타 챗봇" src="' + CHAT_URL + '"></iframe>';
    } else {
      buildDemoUI();
    }
  }

  /* ---- 열기/닫기 (푸시 드로어) ---- */
  function chatOpen(){
    buildBody();
    panel.classList.add('open');
    document.documentElement.classList.add('chat-open');
    if (input) setTimeout(function(){ input.focus(); }, 480);
  }
  function chatClose(){
    panel.classList.remove('open');
    document.documentElement.classList.remove('chat-open');
  }
  function chatToggle(){ panel.classList.contains('open') ? chatClose() : chatOpen(); }
  fab.addEventListener('click', chatToggle);
  panel.querySelector('.pc-close').addEventListener('click', chatClose);
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape') chatClose(); });
  window.ParametaChat = { open: chatOpen, close: chatClose, toggle: chatToggle };

  /* ---- FAB 타이프라이터 ---- */
  var FAB_LINES = [
    '무엇이든 물어보세요',
    '토큰 발행은 어떻게 하는 거지?',
    '스테이블코인 사업, 무엇부터 시작하지?',
    'DID 신원인증 도입 비용이 궁금해요',
    '화이트라벨 거래소도 만들 수 있나요?',
    '온체인 KYC가 뭔가요?',
    'K-BTF는 어떻게 도입하나요?',
    'SaaS와 온프레미스, 뭐가 맞을까요?',
    'PoC는 보통 얼마나 걸리나요?',
  ];
  var fabLabel = document.getElementById('fabLabel');
  if (fabLabel && !window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    var fLine = 0, fChar = fabLabel.textContent.length, fDel = false;
    var fabType = function(){
      if (document.hidden || panel.classList.contains('open')){ setTimeout(fabType, 900); return; }
      var line = FAB_LINES[fLine % FAB_LINES.length];
      if (!fDel){
        fChar++;
        fabLabel.textContent = line.slice(0, fChar);
        if (fChar >= line.length){ fDel = true; setTimeout(fabType, 2300); return; }
        setTimeout(fabType, 65 + Math.random() * 55);
      } else {
        fChar--;
        fabLabel.textContent = line.slice(0, fChar);
        if (fChar <= 0){ fDel = false; fLine++; setTimeout(fabType, 450); return; }
        setTimeout(fabType, 26);
      }
    };
    setTimeout(function(){ fDel = true; fabType(); }, 2600);
  }
})();
