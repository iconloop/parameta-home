#!/usr/bin/env python3
# ============================================================================
# PARAMETA 콘셉트 사이트 — 서브페이지 빌더 (양산용 단일 소스)
#
# 사용법:
#   python3 _build/build_subpages.py        # test/ 루트 기준 어디서든 절대경로로 동작
#
# 구조:
#   - 공통 크롬(CSS)은 parameta.html의 <style>에서 추출 → 메인 수정 시 자동 전파
#   - CHROME_HEADER / CHROME_FOOTER / JS  = 배너·GNB·푸터·오버레이·챗봇·모달 (단일 소스)
#   - EXTRA_CSS = 서브페이지 전용 스타일 (.phero, .sec, .cards-*, .light-card 등)
#   - PAGES[파일명] = dict(title, desc, eyebrow, h1_lines[], lead, crumb, content)
#
# 새 페이지 추가:
#   1) PAGES['새페이지.html'] = dict(...) 블록 추가 — content는 아래 헬퍼 조합
#      · eyebrow(라벨) / h2(제목) : 섹션 헤더
#      · rows([...])              : 서비스 행 리스트 (idx/meta 옵션)
#      · dark_card(...) + cards_wrap([...], cols) : 잉크 카드 그리드 (2/3열)
#      · faq([...])               : 롤모션 아코디언
#      · light-card / num-card    : 라이트 카드·숫자 카드 (직접 마크업)
#   2) 실행하면 test/에 HTML 생성. GNB/푸터에 링크 추가는 이 파일에서.
#
# 규칙: 색·폰트는 :root 토큰만 사용(--text-*, --ink 등), 폰트 짝수·최소14,
#       사이즈는 4의 배수, 새 섹션은 캡슐화(주석 마커).
# ============================================================================

#!/usr/bin/env python3
# Build Lumora-styled Parameta subpages from shared chrome + per-page content
import re, os

ROOT = '/Users/sang/Desktop/Claude/test'
main = open(os.path.join(ROOT, 'parameta.html'), encoding='utf-8').read()
CSS = re.search(r'<style>([\s\S]*?)</style>', main).group(1)

EXTRA_CSS = """
/* ============ SUBPAGE HERO ============ */
.phero{ position:relative; isolation:isolate; overflow:hidden; border-radius:0 0 var(--radius-card) var(--radius-card);
  background:linear-gradient(to bottom, var(--surface), var(--gray-200)) }
.phero-inner{ position:relative; z-index:10; display:flex; flex-direction:column; gap:1.75rem;
  padding:9rem 1.25rem 3.5rem }
.phero-h1{ max-width:22ch; font-size:var(--text-36); font-weight:600; line-height:1.05; letter-spacing:-.02em }
.phero-lead{ max-width:44rem; font-size:var(--text-16); line-height:1.7; color:rgba(var(--ink-rgb),.65) }
.phero-text{ display:flex; flex-direction:column; gap:1.75rem }
.phero-cta{ display:flex; flex-wrap:wrap; gap:1rem; margin-top:.5rem }
.phero-visual{ display:none }
.phero-status{ display:flex; align-items:center; justify-content:space-between; gap:.75rem;
  border-top:1px solid rgba(var(--ink-rgb),.1); padding:1.25rem; font-size:var(--text-14); font-weight:500;
  text-transform:uppercase; letter-spacing:.025em; color:rgba(var(--ink-rgb),.6); position:relative; z-index:10 }
.phero-wm{ pointer-events:none; position:absolute; right:-1rem; bottom:-2.5rem; z-index:1;
  user-select:none; font-weight:700; line-height:1; font-size:9rem; color:rgba(var(--white-rgb),.35);
  font-family:var(--font-display); letter-spacing:-.01em; white-space:nowrap }
@media (min-width:640px){ .phero-inner{ padding:10rem 2rem 4rem } .phero-h1{ font-size:var(--text-48) }
  .phero-status{ padding-left:2rem; padding-right:2rem } }
@media (min-width:768px){ .phero-h1{ font-size:var(--text-60) } }
/* ---- 다크 히어로(서브페이지) — body.hero-dark 지정 시 ---- */
body.hero-dark .phero{ background:var(--black); min-height:100vh }
body.hero-dark .phero-h1{ color:var(--white); max-width:18ch; font-size:var(--text-36); line-height:.98; font-weight:500 }
@media (min-width:640px){ body.hero-dark .phero-h1{ font-size:var(--text-48) } }
@media (min-width:768px){ body.hero-dark .phero-h1{ font-size:var(--text-60) } }
@media (min-width:1024px){ body.hero-dark .phero-h1{ font-size:var(--text-72) } }
body.hero-dark .phero-text .phero-lead{ color:rgba(var(--white-rgb),.7); font-size:var(--text-20) }
/* 히어로 CTA: 폰트 text-16 (높이는 base .pill.no-arrow 토큰 min-height:3rem = with-arrow와 동일) */
.phero-cta .pill .hspring{ font-size:var(--text-16) }
body.hero-dark .phero-cta .pill.outline .hspring{ border-color:rgba(var(--white-rgb),.3); color:var(--white) }
body.hero-dark .phero-cta .pill.outline .pill-badge{ background:var(--white); color:var(--ink) }
/* 다크 히어로: eyebrow(+블릿)·크럼브/스크롤(+디바이더)·워터마크 제거 */
body.hero-dark .phero-inner .eyebrow.dark{ display:none }
body.hero-dark .phero-status{ display:none }
body.hero-dark .phero-wm{ display:none }
/* 100vh · 12칼럼 그리드 스냅: 텍스트 1~6칸 / 비주얼 7~12칸 */
body.hero-dark .phero-inner{ min-height:100vh; display:grid; grid-template-columns:repeat(12,1fr);
  align-items:center; column-gap:var(--grid-gap); padding-top:6rem; padding-bottom:3rem }
body.hero-dark .phero-text{ grid-column:1 / 6; align-self:center; gap:1rem }
body.hero-dark .phero-cta{ margin-top:.5rem }  /* 리드↔버튼 살짝만 */
body.hero-dark .phero-visual{ grid-column:7 / 13; display:block; align-self:stretch; min-height:56vh;
  border-radius:var(--radius-card); border:1px solid rgba(var(--white-rgb),.12);
  background:radial-gradient(120% 90% at 70% 18%, rgba(var(--accent-rgb),.2), transparent 60%), rgba(var(--white-rgb),.03) }
@media (max-width:767px){
  body.hero-dark .phero, body.hero-dark .phero-inner{ min-height:auto }
  body.hero-dark .phero-inner{ grid-template-columns:1fr; padding-top:8rem; padding-bottom:3rem; row-gap:2rem }
  body.hero-dark .phero-text, body.hero-dark .phero-visual{ grid-column:auto }
  body.hero-dark .phero-visual{ min-height:40vh } }

/* ============ WHAT IS (좌 다이어그램 / 우 텍스트) ============ */
.whatis-grid{ display:grid; grid-template-columns:1fr; gap:2.5rem; align-items:center }
@media (min-width:900px){
  .whatis-grid{ grid-template-columns:repeat(12,1fr); column-gap:var(--grid-gap) }
  .whatis-grid .ps-flow{ grid-column:1 / 7 }
  .whatis-grid .whatis-text{ grid-column:8 / 13 } }
.whatis-text .phero-lead{ font-size:var(--text-18) }
.whatis-text .sec-h2{ margin-top:1rem; margin-bottom:2rem }
/* 라이트 카드 톤으로 감싸고 보라 코어만 포인트 */
.ps-flow{ display:flex; flex-direction:column; align-items:center; gap:0; border-radius:var(--radius-card);
  background-color:rgba(var(--ink-rgb),.06);
  background-image:radial-gradient(rgba(var(--ink-rgb),.06) 1px, transparent 1.5px);
  background-size:20px 20px; padding:5.5rem 2rem; text-align:center; --rvl-y:0px }
.ps-flow-band{ position:relative; width:82%; border-radius:var(--radius-card-sm); padding:1.75rem 1.5rem;
  background:var(--white); border:1px solid rgba(var(--ink-rgb),.22);
  box-shadow:0 8px 24px rgba(var(--ink-rgb),.06);
  opacity:0; transition:transform .35s cubic-bezier(.2,.8,.2,1), box-shadow .35s cubic-bezier(.2,.8,.2,1) }
.ps-flow-core{ width:92% }
.ps-flow .chip{ border-width:1px; border-color:rgba(var(--ink-rgb),.22) }
/* 연결부 노드: 흰 채움 + 연한 보라 링 (선이 카드에 닿는 지점) */
.ps-flow-band::before,.ps-flow-band::after{ content:''; position:absolute; left:50%; z-index:2;
  width:7px; height:7px; border-radius:50%; background:var(--purple-300);
  transform:translateX(-50%); display:none }
.ps-flow-band::before{ top:-3.5px }
.ps-flow-band::after{ bottom:-3.5px }
.ps-flow-band:nth-child(3)::before,.ps-flow-band:nth-child(3)::after{ display:block }
.ps-core-head{ display:flex; align-items:center; justify-content:flex-start; gap:1rem; text-align:left; margin-bottom:1rem }
.ps-flow-core .ps-core-head .core-sub{ margin:.125rem 0 0 }
.ps-flow-logo{ display:block; width:32px; height:32px; flex-shrink:0 }
/* 태그: 알약 대신 그레이 상자 안에 텍스트를 닷으로 연결 */
.ps-tags{ display:flex; width:100%; box-sizing:border-box; flex-wrap:wrap; justify-content:center; align-items:center;
  background:rgba(var(--ink-rgb),.05); border-radius:var(--radius-control); padding:.75rem 1.125rem }
.ps-tag{ display:inline-flex; align-items:center; font-size:var(--text-16); font-weight:500; color:rgba(var(--ink-rgb),.7) }
.ps-tag:not(:first-child)::before{ content:''; display:inline-block; width:4px; height:4px; border-radius:50%;
  background:rgba(var(--ink-rgb),.3); margin:0 .375rem }
/* 리빌: 밴드 위→아래 순차 등장 후 커넥터가 그어짐 */
/* ParaSta 코어가 먼저 등장 */
.ps-flow.is-in .ps-flow-band{ opacity:1; animation:psBandIn .6s cubic-bezier(.16,1,.3,1) backwards }
@keyframes psBandIn{ from{ opacity:0; transform:translateY(14px) } }
/* 외곽 카드: 선이 닿는 순간 상자가 생겨남(scale-in) */
.ps-flow.is-in .ps-flow-band:nth-child(1),
.ps-flow.is-in .ps-flow-band:nth-child(5){
  animation:psAppear .6s cubic-bezier(.2,.8,.2,1) .78s backwards }
@keyframes psAppear{ from{ opacity:0; transform:scale(.8) } }
.ps-flow.is-in .ps-flow-band:hover{ transform:scale(1.03); box-shadow:0 16px 40px rgba(var(--ink-rgb),.1) }
.ps-flow .chip-row{ justify-content:center }
.ps-flow-band .lbl{ font-size:var(--text-20); font-weight:600; text-transform:uppercase; letter-spacing:.025em;
  color:rgba(var(--ink-rgb),.8); margin-bottom:.875rem }
/* 외곽 카드 헤더: 아이콘 + 라벨 좌측정렬 (ParaSta 카드와 동일 결) */
.ps-band-head{ display:flex; align-items:center; gap:.5rem; text-align:left; margin-bottom:.625rem }
.ps-band-head .lbl{ margin-bottom:0 }
.ps-band-icon{ display:inline-flex; flex-shrink:0; width:26px; height:26px; align-items:center; justify-content:center;
  color:var(--purple-500) }
.ps-band-icon svg{ width:100%; height:100% }
.ps-flow-core .core-title{ font-size:var(--text-22); font-weight:600; letter-spacing:-.01em; color:var(--ink) }
.ps-flow-core .core-sub{ font-size:var(--text-16); color:rgba(var(--ink-rgb),.55); margin:.25rem 0 1rem }
.ps-flow-link{ width:0; height:2.5rem; margin:0 auto; border-left:2px dashed rgba(var(--purple-300-rgb),.85);
  transform:scaleY(0); transition:transform .45s cubic-bezier(.16,1,.3,1) }
/* 파라스타(가운데)에서 위·아래로 동시에 뻗어나감 */
.ps-flow-link:nth-child(2){ transform-origin:bottom }
.ps-flow-link:nth-child(4){ transform-origin:top }
.ps-flow.is-in .ps-flow-link{ transform:scaleY(1); transition-delay:300ms }
/* ============ SUBPAGE UTILITIES ============ */
.sec{ padding:5rem 1.25rem }
@media (min-width:640px){ .sec{ padding-left:2rem; padding-right:2rem } }
@media (min-width:1024px){ .sec{ padding-block:6rem } }
.sec-h2{ margin:1.25rem 0 3rem; max-width:24ch; font-size:var(--text-32); font-weight:600; letter-spacing:-.02em }
@media (min-width:640px){ .sec-h2{ font-size:var(--text-48) } }
.cards-3{ display:grid; grid-template-columns:1fr; gap:1.5rem }
@media (min-width:768px){ .cards-3{ grid-template-columns:repeat(2,1fr) } }
@media (min-width:1024px){ .cards-3{ grid-template-columns:repeat(3,1fr) } }
.cards-2{ display:grid; grid-template-columns:1fr; gap:1.5rem }
@media (min-width:768px){ .cards-2{ grid-template-columns:repeat(2,1fr) } }
.work-card.sm{ min-height:18rem }
.work-card.static{ cursor:default; transition:transform .35s cubic-bezier(.2,.8,.2,1) }
.work-card.static:hover{ transform:scale(1.03) }
/* grouped: 상단 이미지 영역(고정 높이) + 텍스트는 동일 y에서 시작 */
.work-card.grouped{ min-height:32rem; height:100%; display:flex; flex-direction:column }
/* grouped 카드가 든 그리드 셀만 flex로 (다른 카드 레이아웃 영향 없이 높이 정렬) */
.cards-3 > li:has(.work-card.grouped), .cards-2 > li:has(.work-card.grouped){ display:flex }
.work-card.grouped::before{ content:''; flex:none; height:16rem } /* 이미지 영역 */
.work-card.grouped .work-bottom{ position:static; inset:auto }
.work-card.grouped .work-meta{ margin-bottom:.875rem; color:var(--purple-300) }
.work-card.grouped .work-bottom p{ font-size:var(--text-16) }
.core-mods .work-bottom p{ font-size:var(--text-16) }
/* Core Modules: 좌측 타이틀 sticky + 우측 카드 세로 스크롤 */
.cm-grid{ display:grid; grid-template-columns:1fr; gap:2.5rem }
.cm-cards{ display:flex; flex-direction:column; gap:1.5rem }
@media (min-width:900px){
  .cm-grid{ grid-template-columns:repeat(12,1fr); column-gap:var(--grid-gap) }
  .cm-head{ grid-column:1 / 5 }
  /* 스티키 top = 50vh - 타이틀높이/2 (JS가 --cm-center 세팅)
     시작: 첫 카드와 같은 y(자연 위치) → 스크롤: 화면 중앙 고정 → 끝: 마지막 카드 하단에서 멈춤 */
  .cm-sticky{ position:sticky; top:var(--cm-center, 35vh) }
  .cm-cards{ grid-column:6 / 13 }
}
/* 이 섹션 카드는 호버 확대 없음(대형 카드라 랙 방지) */
.cm-cards .work-card.static{ transition:opacity .6s cubic-bezier(.4,0,.2,1) }
.cm-cards .work-card.static:hover{ transform:none }
/* 스크롤 하이라이트: 중앙에 온 카드만 진하게, 나머지는 연하게 */
.cm-cards .work-card{ opacity:.5; transition:opacity .6s cubic-bezier(.4,0,.2,1) }
.cm-cards .work-card.cm-active{ opacity:1 }
/* 그레이 배경 카드(화면 이미지가 들어갈 예정) — 다크 대신 라이트 그레이 */
.cm-cards .work-card{ background:color-mix(in srgb, var(--ink) 6%, var(--white)); color:var(--ink); height:auto }
.cm-cards .work-card.grouped .work-meta{ color:var(--purple-500); font-weight:600 }
.cm-cards .work-bottom h3{ color:var(--ink) }
.cm-cards .work-bottom p{ color:rgba(var(--ink-rgb),.6); max-width:none }
/* 태그: 진한 그레이 필 + 흰 글씨, 본문과 같은 사이즈, weight 500 */
.cm-cards .tag{ border:none; background:rgba(var(--ink-rgb),.45); color:var(--white);
  font-size:var(--text-16); font-weight:500; padding:.625rem 1.25rem }
/* 이미지 영역: 카드 폭 full-bleed(양옆·상단 여백 제거) + 도트 패턴 + 하단 그라데이션 마스크 */
.cm-cards .work-card.grouped::before{ height:16rem; margin:-1.5rem -1.5rem 1.5rem; border-radius:0;
  background-image:linear-gradient(to bottom, transparent 45%, color-mix(in srgb, var(--ink) 6%, var(--white))),
    radial-gradient(rgba(var(--ink-rgb),.06) 1px, transparent 1.5px);
  background-size:100% 100%, 20px 20px; background-position:0 0, 0 0 }
@media (min-width:640px){ .cm-cards .work-card.grouped::before{ margin:-2rem -2rem 1.5rem } }
/* Partners 2단 카드: 좌 금융권 / 우 퍼블릭·멀티체인 */
.pn-grid{ display:grid; grid-template-columns:1fr; gap:1.5rem; align-items:stretch }
@media (min-width:900px){ .pn-grid{ grid-template-columns:repeat(2,1fr); column-gap:var(--grid-gap) } }
.pn-card{ background:var(--ink); color:var(--white); border-radius:var(--radius-card); padding:2.5rem;
  box-shadow:0 0 0 1px rgba(var(--white-rgb),.05) }
.pn-head{ margin-bottom:1.5rem }
/* 키커: Advantages 다크카드 보라 키커와 동일 스타일 (타이틀 위) */
.pn-kick{ font-size:var(--text-14); letter-spacing:.025em; color:var(--purple-300); font-weight:600; margin-bottom:.75rem }
/* 타이틀은 다크카드(.work-bottom h3)와 동일 토큰 */
.pn-head h3{ font-size:var(--text-24); font-weight:500; letter-spacing:-.01em }
@media (min-width:640px){ .pn-head h3{ font-size:var(--text-30) } }
/* 사례: 디바이더 대신 인셋 박스(우리 그레이 인셋 언어의 다크 버전) */
.pn-list{ display:flex; flex-direction:column; gap:1rem }
.pn-list li{ background:rgba(var(--white-rgb),.05); border-radius:var(--radius-card-sm); padding:1.5rem }
.pn-list h4{ font-size:var(--text-18); font-weight:600; letter-spacing:-.01em }
.pn-list p{ margin-top:.5rem; font-size:var(--text-16); color:rgba(var(--white-rgb),.55); line-height:1.6 }
.pn-note{ margin-top:1.5rem; font-size:var(--text-16); color:var(--purple-300); line-height:1.6; text-align:center }
/* 인증 3종: 타이틀 없이 하단 배치 — 이미지 영역 + 라벨, 디바이더 없음 */
.cert-row{ display:grid; grid-template-columns:1fr; row-gap:3rem; padding:5rem 0 }
@media (min-width:768px){ .cert-row{ grid-template-columns:repeat(3,1fr); column-gap:var(--grid-gap) } }
.cert-item{ display:flex; flex-direction:column; align-items:center; gap:1.5rem }
.cert-img{ width:100%; max-width:14rem; aspect-ratio:16/10; border-radius:var(--radius-card-sm);
  background:color-mix(in srgb, var(--ink) 6%, var(--white)) }
.cert-txt{ text-align:center; font-size:var(--text-20); font-weight:600; letter-spacing:-.01em; color:var(--ink) }
@media (min-width:1024px){ .cert-txt{ font-size:var(--text-24) } }
/* Proven Core: 3개 스탯이라 데스크톱 3열 */
@media (min-width:1024px){ .stats-grid.pv-stats{ grid-template-columns:repeat(3,1fr) } }
/* Core Technology 행: 화살표(페이지 이동) 제거 + 제목 한 토큰 작게 */
.ct-rows .service-badge{ display:none }
.ct-rows .service-row h3{ font-size:var(--text-24) }
.ct-rows .service-desc{ font-size:var(--text-16); max-width:34rem; margin-right:5rem }
.ct-rows .service-idx{ transition:color .25s ease }
@media (hover:hover){ .ct-rows .service-row:hover .service-idx{ color:var(--purple-500); font-weight:600 } }
.work-quote{ margin-top:1.25rem; border-left:2px solid var(--purple-400); padding-left:1rem;
  font-size:var(--text-14); color:rgba(var(--white-rgb),.75); line-height:1.6 }
.work-quote cite{ display:block; margin-top:.5rem; font-style:normal; font-size:var(--text-14); color:rgba(var(--white-rgb),.45) }
.row-sm h3{ font-size:var(--text-18) !important }
@media (min-width:640px){ .row-sm h3{ font-size:var(--text-22) !important } }
.row-meta{ width:6.5rem; flex:none; font-size:var(--text-14); font-weight:500; text-transform:uppercase;
  letter-spacing:.05em; color:rgba(var(--ink-rgb),.4) }
.light-card{ border:1px solid var(--line); background:rgba(var(--surface-rgb),.5); border-radius:var(--radius-card-sm); padding:1.75rem }
.light-card h3{ font-size:var(--text-18); font-weight:600; letter-spacing:-.01em; margin-bottom:.625rem }
.light-card p{ font-size:var(--text-16); line-height:1.7; color:rgba(var(--ink-rgb),.6) }
.light-card .cap{ font-size:var(--text-14); font-weight:500; text-transform:uppercase; letter-spacing:.05em;
  color:var(--accent); margin-bottom:.75rem; display:block }
.addr-list{ display:flex; flex-direction:column; gap:1.25rem }
.addr-list .k{ font-size:var(--text-14); font-weight:500; text-transform:uppercase; letter-spacing:.05em; color:rgba(var(--ink-rgb),.45) }
.addr-list .v{ margin-top:.25rem; font-size:var(--text-16); line-height:1.6 }
.legal-body{ max-width:48rem }
.legal-body h3{ font-size:var(--text-18); font-weight:600; margin:2.5rem 0 .75rem }
.legal-body h3:first-child{ margin-top:0 }
.legal-body p{ font-size:var(--text-16); line-height:1.7; color:rgba(var(--ink-rgb),.6) }
.legal-note{ display:inline-flex; align-items:center; gap:.5rem; margin-top:.375rem;
  border:1px solid var(--line); border-radius:var(--radius-pill); padding:.25rem .875rem;
  font-size:var(--text-14); color:rgba(var(--ink-rgb),.45) }
.num-card .n{ font-size:var(--text-40); font-weight:600; letter-spacing:-.02em; line-height:1.1; margin-bottom:.5rem }
.num-card .n small{ font-size:var(--text-20); font-weight:500 }
.tag.on-light{ border-color:var(--line); color:var(--ink) }

/* ============ CONTENT-PORT ADDITIONS (우리 토큰 유지) ============ */
/* 비교표 */
/* Why ParaSta: 타이틀셋(4칼럼) 좌 / 표(8칼럼) 우 */
.why-grid{ display:flex; flex-direction:column; gap:2.5rem }
.why-table{ min-width:0 }
.why-head .sec-h2{ margin-top:1rem; margin-bottom:1.5rem }
.why-head .phero-lead{ font-size:var(--text-18) }
.mkv{ width:.8em; height:.8em; display:inline-block; vertical-align:-.1em }
.why-legend{ display:inline-flex; flex-wrap:wrap; gap:.75rem 1.25rem; margin-top:1.75rem;
  background:rgba(var(--ink-rgb),.05); border-radius:var(--radius-control); padding:.75rem 1.125rem;
  font-size:var(--text-14); color:rgba(var(--ink-rgb),.55) }
.why-legend .lg{ display:inline-flex; align-items:center; gap:.35rem }
.why-legend .mkv{ width:16px; height:16px }
.why-legend .mk{ display:inline-flex; margin-right:0 }
.why-legend .mk.on{ color:var(--accent) }
.why-legend .mk.mid{ color:rgba(var(--ink-rgb),.45) }
.why-legend .mk.off{ color:rgba(var(--ink-rgb),.3) }
.cmp-wrap{ overflow-x:auto; -webkit-overflow-scrolling:touch }
/* 데스크톱: 호버 확대가 스크롤바를 만들지 않도록 오버플로우 개방 */
@media (min-width:1024px){ .why-table .cmp-wrap{ overflow:visible } }
/* 표는 전체가 하나의 블록으로 리빌 (.cmp-wrap.rvl → 기본 .rvl 동작) */
.cmp-legend{ margin-bottom:1rem; font-size:var(--text-14); color:rgba(var(--ink-rgb),.5) }
table.cmp{ width:100%; min-width:46rem; border-collapse:separate; border-spacing:0; font-size:var(--text-16) }
table.cmp th, table.cmp td{ padding:1.25rem 1.125rem; text-align:left; vertical-align:top; border-bottom:1px solid var(--line) }
table.cmp thead th{ font-weight:600; font-size:var(--text-18); letter-spacing:.01em; padding-top:1.75rem;
  text-align:center; color:rgba(var(--ink-rgb),.55); border-bottom:1px solid var(--line) }
table.cmp thead th.hl{ color:var(--accent) }
table.cmp thead th.hl, table.cmp td.hl{ background:color-mix(in srgb, var(--purple-300) 22%, var(--white)) }
table.cmp thead th.hl, table.cmp td.hl{ border-bottom-color:rgba(var(--ink-rgb),.16) }
table.cmp thead th.hl{ border-top-left-radius:var(--radius-control); border-top-right-radius:var(--radius-control) }
table.cmp tbody tr:last-child td.hl{ border-bottom-left-radius:var(--radius-control); border-bottom-right-radius:var(--radius-control) }
table.cmp tbody tr:last-child td, table.cmp tbody tr:last-child th{ border-bottom:none; padding-bottom:1.75rem }
table.cmp tbody th{ font-weight:600; font-size:var(--text-18); color:rgba(var(--ink-rgb),.65); white-space:nowrap; padding-left:0; vertical-align:middle }
table.cmp td{ color:rgba(var(--ink-rgb),.7); line-height:1.5; text-align:center; vertical-align:middle }
table.cmp td .mk{ display:block; margin:0 auto .125rem }
table.cmp td .mkv{ width:22px; height:22px }
table.cmp td .mkv circle{ stroke-width:.8 }
.why-legend .mkv circle{ stroke-width:1.4 }
table.cmp td .cell-txt{ display:block; font-size:var(--text-14) }
table.cmp td.hl{ font-weight:500; color:var(--ink) }
/* ParaSta 열: 호버 시 열 전체가 버튼처럼 함께 살짝 커짐(그림자 없음) — JS가 hl-hover 동기화 */
table.cmp th.hl, table.cmp td.hl{ position:relative; transition:transform .4s cubic-bezier(.2,.8,.2,1) }
table.cmp th.hl.hl-hover, table.cmp td.hl.hl-hover{ transform:scale(1.03); z-index:1 }
table.cmp .mk{ font-weight:700; margin-right:.375rem }
table.cmp .mk.on{ color:var(--accent) }
table.cmp .mk.mid{ color:rgba(var(--ink-rgb),.45) }
table.cmp .mk.off{ color:rgba(var(--ink-rgb),.3) }
/* 간단 가로 바 */
.barc{ display:flex; flex-direction:column; gap:1rem; max-width:46rem }
.barc-title{ font-size:var(--text-16); font-weight:600; margin-bottom:.25rem }
.barc-row{ display:grid; grid-template-columns:7rem 1fr auto; align-items:center; gap:1rem }
.barc-l{ font-size:var(--text-14); color:rgba(var(--ink-rgb),.6) }
.barc-track{ height:.625rem; border-radius:var(--radius-pill); background:rgba(var(--ink-rgb),.07); overflow:hidden }
.barc-fill{ height:100%; border-radius:var(--radius-pill); background:linear-gradient(90deg,var(--purple-400),var(--purple-300)) }
.barc-row.hi .barc-fill{ background:linear-gradient(90deg,var(--purple-600),var(--accent)) }
.barc-v{ font-size:var(--text-16); font-weight:600; white-space:nowrap }
.barc-row.hi .barc-v{ color:var(--accent) }
.sec-note{ margin-top:1.25rem; font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); line-height:1.6; max-width:54rem }
/* 칩 · 라우트 */
.chip-row{ display:flex; flex-wrap:wrap; gap:.5rem }
.chip{ display:inline-flex; align-items:center; border:1px solid var(--line); border-radius:var(--radius-pill);
  padding:.5rem 1rem; font-size:var(--text-14); font-weight:500; color:rgba(var(--ink-rgb),.7) }
.routes{ display:flex; flex-wrap:wrap; gap:.625rem }
.route{ display:inline-flex; align-items:center; gap:.5rem; border:1px solid var(--line); border-radius:var(--radius-pill);
  padding:.625rem 1.25rem; font-size:var(--text-16); font-weight:500; color:rgba(var(--ink-rgb),.7);
  transition:border-color .2s, color .2s, background .2s }
@media (hover:hover){ .route:hover{ border-color:var(--accent); color:var(--accent) } }
.route.on{ background:var(--ink); color:var(--white); border-color:var(--ink) }
@media (max-width:480px){ .barc-row{ grid-template-columns:5.5rem 1fr auto; gap:.625rem } }
"""

CHROME_HEADER = """
<a href="#main" class="skip">본문으로 건너뛰기</a>
<!-- GNB — 단일 소스: assets/nav.js가 배너·헤더·오버레이 메뉴 주입 -->
<header id="header" class="is-in" style="opacity:1; transform:none"></header>
"""

CHROME_FOOTER = """
<footer id="footer">
  <div class="shell footer-shell">
    <div class="footer-cta">
      <h2 class="footer-h2" id="footerH2" data-line-stagger="100">
        <span class="rvl-line"><span>Talk to</span></span>
        <span class="rvl-line"><span>our team.</span></span>
      </h2>
      <button class="pill light with-arrow arw-up hs-scale" data-modal>
        <span class="hspring">Contact Us<span class="pill-badge"><svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M7 17 17 7M8 7h9v9"/></svg></span></span>
      </button>
    </div>
    <div class="footer-cols">
      <div class="footer-col">
        <div class="footer-brand"><img class="brand-logo" src="assets/brand/logo-horizontal-color-dark.svg" alt="PARAMETA"></div>
        <p class="footer-tagline">서비스 환경에 맞는 디지털자산 인프라, 파라메타와 함께 시작해보세요.</p>
        <p class="footer-addr">서울특별시 서초구 강남대로 311 드림플러스 8F<br>02-2138-7026 · info@parametacorp.com</p>
      </div>
    </div>
    <div class="footer-legal">
      <span>ⓒ PARAMETA. 2026 · 대표 김종협 · 사업자등록번호 647-81-00375</span>
      <div class="footer-legal-links">
        <a class="alink-wrap" href="privacy.html"><span class="alink legal">개인정보 처리방침</span></a>
        <a class="alink-wrap" href="terms.html"><span class="alink legal">이용약관</span></a>
      </div>
    </div>
  </div>
  <div class="footer-wm"><img src="assets/brand/logo-horizontal-white.svg" alt=""></div>
</footer>

<div id="modal" role="dialog" aria-modal="true" aria-label="Contact Us" aria-hidden="true">
  <div class="modal-panel" id="modalPanel">
    <button class="modal-close" data-close-modal aria-label="닫기"><svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 4l16 16M20 4 4 20"/></svg></button>
    <div class="modal-form-wrap">
      <div class="modal-head">
        <span class="modal-eyebrow"><span class="dot"></span>Contact Us</span>
        <h2>프로젝트를 알려주세요.</h2>
      </div>
      <form class="modal-form" id="modalForm">
        <div class="modal-field">
          <label for="mfName">이름</label>
          <input id="mfName" type="text" required placeholder="이름을 입력해주세요" />
        </div>
        <div class="modal-field">
          <label for="mfEmail">이메일</label>
          <input id="mfEmail" type="email" required placeholder="you@company.com" />
        </div>
        <div class="modal-field">
          <label for="mfProject">문의 내용</label>
          <textarea id="mfProject" rows="4" required placeholder="구축하려는 서비스, 일정, 환경(SaaS/온프레미스)을 알려주세요."></textarea>
        </div>
        <div class="modal-bottom">
          <span class="modal-note">영업일 기준 1일 내 회신드립니다.</span>
          <button class="pill dark with-arrow arw-up hs-scale" type="submit">
            <span class="hspring"><span id="modalSubmitLabel">문의 보내기</span><span class="pill-badge"><svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M7 17 17 7M8 7h9v9"/></svg></span></span>
          </button>
        </div>
      </form>
    </div>
    <div class="modal-success">
      <div class="badge"><svg class="icn" viewBox="0 0 48 48" aria-hidden="true"><path fill="currentColor" d="M24 2c2.2 13.8 7.9 19.6 22 22-14.1 2.4-19.8 8.2-22 22-2.2-13.8-7.9-19.6-22-22 14.1-2.4 19.8-8.2 22-22Z"/></svg></div>
      <h2>문의가 접수되었습니다</h2>
      <p>확인 후 영업일 기준 1일 내에 회신드리겠습니다. 감사합니다.</p>
      <button class="pill dark no-arrow hs-scale" data-close-modal><span class="hspring">닫기</span></button>
    </div>
  </div>
</div>

<div id="dev-grid" aria-hidden="true"><div class="gi"><div class="col"></div><div class="col"></div><div class="col"></div><div class="col"></div><div class="col"></div><div class="col"></div><div class="col"></div><div class="col"></div><div class="col"></div><div class="col"></div><div class="col"></div><div class="col"></div></div></div>
<button id="dev-grid-toggle" type="button">GRID</button>
<!-- 챗봇 — 단일 소스: assets/chatbot.js가 FAB·드로어 주입 -->
"""

JS = """
<script type="importmap">
{ "imports": { "lenis": "https://unpkg.com/lenis@1.3.23/dist/lenis.mjs" } }
</script>
<script type="module">
import Lenis from 'lenis';

function applyAdaptiveGrid(){
  const FONT_BASE = 16, baseWidth = 1920, coef = 0.6666;
  const w = window.innerWidth;
  const widthReduction = ((baseWidth - w) / baseWidth) * 100;
  const size = FONT_BASE - (FONT_BASE * (widthReduction * coef)) / 100;
  if (size > FONT_BASE) document.documentElement.style.fontSize = size + 'px';
  else document.documentElement.style.removeProperty('font-size');
}
applyAdaptiveGrid();
addEventListener('resize', applyAdaptiveGrid);

const lenis = new Lenis({ smoothWheel: true });
function raf(t){ lenis.raf(t); requestAnimationFrame(raf); }
requestAnimationFrame(raf);

function stopScroll(){
  lenis.stop();
  const h = document.documentElement;
  h.style.position = 'relative'; h.style.overflow = 'hidden'; h.style.height = '100%';
}
function startScroll(){
  lenis.start();
  const h = document.documentElement;
  h.style.removeProperty('position'); h.style.removeProperty('overflow'); h.style.removeProperty('height');
}

/* reveals — no loader gate on subpages */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting){ e.target.classList.add('is-in'); revealObserver.unobserve(e.target); }
  });
}, { threshold: 0.15 });
document.querySelectorAll('.rvl, .rvl-op, .rvl-wm').forEach(el => revealObserver.observe(el));

function initLineReveal(el){
  const stagger = parseInt(el.dataset.lineStagger || '0', 10);
  el.querySelectorAll('.rvl-line').forEach((line, i) => {
    line.querySelector('span').style.transitionDelay = (i * stagger) + 'ms';
  });
}
const lineObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting){
      e.target.querySelectorAll('.rvl-line').forEach(l => l.classList.add('is-in'));
      lineObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.2 });
document.querySelectorAll('[data-line-reveal]').forEach(el => { initLineReveal(el); lineObserver.observe(el); });

/* ParaSta 비교표 강조열: 열 전체가 하나의 블록처럼 커지도록 */
const hlCells = document.querySelectorAll('.why-table table.cmp .hl');
function setHlOrigins(){
  if(!hlCells.length) return;
  let top = Infinity, bottom = -Infinity;
  hlCells.forEach(c => { const r = c.getBoundingClientRect(); top = Math.min(top, r.top); bottom = Math.max(bottom, r.bottom); });
  const centerY = (top + bottom) / 2;
  hlCells.forEach(c => { c.style.transformOrigin = 'center ' + (centerY - c.getBoundingClientRect().top) + 'px'; });
}
setHlOrigins();
addEventListener('resize', setHlOrigins);
addEventListener('load', setHlOrigins);
hlCells.forEach(c => {
  c.addEventListener('mouseenter', () => hlCells.forEach(x => x.classList.add('hl-hover')));
  c.addEventListener('mouseleave', () => hlCells.forEach(x => x.classList.remove('hl-hover')));
});

/* Core Modules 카드: 뷰포트 중앙에 가장 가까운 카드만 활성(진하게) */
const cmCards = [...document.querySelectorAll('.cm-cards .work-card')];
function updateCmActive(){
  if(!cmCards.length) return;
  const mid = window.innerHeight / 2;
  let best = null, bestD = Infinity;
  cmCards.forEach(c => { const r = c.getBoundingClientRect(); const d = Math.abs(r.top + r.height/2 - mid); if(d < bestD){ bestD = d; best = c; } });
  cmCards.forEach(c => c.classList.toggle('cm-active', c === best));
}
if(cmCards.length){
  let ticking = false;
  addEventListener('scroll', () => { if(!ticking){ ticking = true; requestAnimationFrame(() => { updateCmActive(); ticking = false; }); } }, { passive:true });
  addEventListener('resize', updateCmActive);
  updateCmActive();
}

/* Proven Core 숫자 카운트업 (메인 stats와 같은 결) */
const pvVals = [...document.querySelectorAll('.pv-val')];
if(pvVals.length){
  const pvObs = new IntersectionObserver((ents) => {
    ents.forEach(en => {
      if(!en.isIntersecting) return;
      pvObs.unobserve(en.target);
      const target = parseInt(en.target.dataset.val, 10);
      const t0 = performance.now(), dur = 1100;
      (function tick(now){
        const p = Math.min((now - t0) / dur, 1);
        const e = 1 - Math.pow(1 - p, 3); /* easeOutCubic */
        en.target.textContent = Math.round(target * e);
        if(p < 1) requestAnimationFrame(tick);
      })(t0);
    });
  }, { threshold: .6 });
  pvVals.forEach(el => pvObs.observe(el));
}

/* Core Modules 좌측 타이틀: 화면 중앙 고정점 계산(50vh - 높이/2) */
const cmSticky = document.querySelector('.cm-sticky');
function setCmCenter(){
  if(!cmSticky) return;
  cmSticky.style.setProperty('--cm-center', `calc(50vh - ${Math.round(cmSticky.offsetHeight/2)}px)`);
}
if(cmSticky){ setCmCenter(); addEventListener('resize', setCmCenter); }

/* page hero h1 reveals immediately */
const pheroH1 = document.querySelector('.phero-h1');
if (pheroH1){
  initLineReveal(pheroH1);
  requestAnimationFrame(() => requestAnimationFrame(() =>
    pheroH1.querySelectorAll('.rvl-line').forEach(l => l.classList.add('is-in'))));
}

/* nav menu (마크업은 nav.js 주입) */
const navmenu = document.getElementById('navmenu');
function openMenu(){
  navmenu.classList.add('open'); navmenu.setAttribute('aria-hidden', 'false');
  stopScroll(); document.addEventListener('keydown', onMenuKey);
}
function closeMenu(){
  navmenu.classList.remove('open'); navmenu.setAttribute('aria-hidden', 'true');
  startScroll(); document.removeEventListener('keydown', onMenuKey);
}
function onMenuKey(e){ if (e.key === 'Escape') closeMenu(); }

/* modal */
const modal = document.getElementById('modal');
const modalPanel = document.getElementById('modalPanel');
const modalForm = document.getElementById('modalForm');
const modalSubmitLabel = document.getElementById('modalSubmitLabel');
function openModal(){
  modal.classList.add('open'); modal.classList.remove('success');
  modal.setAttribute('aria-hidden', 'false');
  stopScroll(); document.addEventListener('keydown', onModalKey);
}
function closeModal(){
  modal.classList.remove('open'); modal.setAttribute('aria-hidden', 'true');
  startScroll(); document.removeEventListener('keydown', onModalKey);
  setTimeout(() => { modal.classList.remove('success'); modalForm.reset(); modalSubmitLabel.textContent = '문의 보내기'; }, 300);
}
function onModalKey(e){ if (e.key === 'Escape') closeModal(); }
modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
modalPanel.addEventListener('click', (e) => e.stopPropagation());
modalForm.addEventListener('submit', (e) => {
  e.preventDefault();
  modalSubmitLabel.textContent = '보내는 중…';
  setTimeout(() => { modal.classList.add('success'); }, 600);
});

/* faq accordion — 원본(reasons) 롤 모션 */
function faqSetH(item, open){
  const content = item.querySelector('.faq-content');
  const inner = item.querySelector('.faq-inner');
  const bottom = item.querySelector('.faq-t-bottom');
  if (!content || !inner || !bottom) return;
  const closed = bottom.offsetHeight;
  if (open){
    const mt = parseFloat(getComputedStyle(bottom).marginTop) || 0;
    content.style.maxHeight = Math.max(0, inner.scrollHeight - closed - mt) + 'px';
  } else {
    content.style.maxHeight = closed + 'px';
  }
}
function faqSpin(item){
  const b = item.querySelector('.faq-badge2');
  if (!b) return;
  const cur = (parseFloat(b.dataset.rot || '0')) + 360;
  b.dataset.rot = cur;
  b.style.transform = 'rotate(' + cur + 'deg)';
}
function faqToggle(li, list){
  const isOpen = li.classList.contains('open');
  list.querySelectorAll('.faq-item.open').forEach(o => {
    if (o === li) return;
    o.classList.remove('open');
    o.querySelector('.faq-row').setAttribute('aria-expanded', 'false');
    faqSetH(o, false);
    faqSpin(o);
  });
  li.classList.toggle('open', !isOpen);
  li.querySelector('.faq-row').setAttribute('aria-expanded', String(!isOpen));
  faqSetH(li, !isOpen);
  faqSpin(li);
}
document.querySelectorAll('.faq-item').forEach(li => {
  const row = li.querySelector('.faq-row');
  if (!row) return;
  const list = li.closest('ul');
  row.addEventListener('click', () => faqToggle(li, list));
  row.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' '){ e.preventDefault(); faqToggle(li, list); }
  });
  faqSetH(li, false);
});
addEventListener('resize', () => {
  document.querySelectorAll('.faq-item.open').forEach(o => faqSetH(o, true));
});

/* contact form stub */
const contactForm = document.getElementById('contactForm');
if (contactForm){
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    document.getElementById('cfSubmitLabel').textContent = '접수 완료';
    document.getElementById('cfNote').textContent = '문의가 접수되었습니다. 감사합니다.';
  });
}

/* dev grid toggle */
document.getElementById('dev-grid-toggle').addEventListener('click', () => {
  document.body.classList.toggle('show-grid');
});

</script>
"""

ARW = '<svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M7 17 17 7M8 7h9v9"/></svg>'
MARK = '<svg class="icn" viewBox="0 0 48 48" aria-hidden="true"><path fill="currentColor" d="M24 2c2.2 13.8 7.9 19.6 22 22-14.1 2.4-19.8 8.2-22 22-2.2-13.8-7.9-19.6-22-22 14.1-2.4 19.8-8.2 22-22Z"/></svg>'

def dark_card(cap, title, desc, tags=None, quote=None, cite=None, sm=True, grouped=False):
    t = ''.join(f'<span class="tag">{x}</span>' for x in (tags or []))
    q = f'<blockquote class="work-quote">&ldquo;{quote}&rdquo;<cite>{cite}</cite></blockquote>' if quote else ''
    meta = f'<div class="work-meta"><span>{cap}</span></div>'
    if grouped:
        # 키커를 하단 텍스트 블록에 붙여 상단은 이미지 영역으로 비움
        return (f'<article class="work-card static{" sm" if sm else ""} grouped">'
                f'<div class="work-bottom">{meta}<h3>{title}</h3><p>{desc}</p>{q}'
                f'{f"<div class=work-tags>{t}</div>" if t else ""}</div></article>')
    return (f'<article class="work-card static{" sm" if sm else ""}">'
            f'{meta}'
            f'<div class="work-bottom"><h3>{title}</h3><p>{desc}</p>{q}'
            f'{f"<div class=work-tags>{t}</div>" if t else ""}</div></article>')

def rows(items, sm=False, meta=False):
    out = ['<ul>']
    for i, it in enumerate(items):
        idx = it.get('idx', f'{i+1:02d}')
        cell = (f'<span class="row-meta">{idx}</span>' if meta else f'<span class="service-idx">{idx}</span>')
        out.append(
            f'<li class="service-row-li rvl" style="--rvl-y:24px; --rvl-delay:{i*80}ms">'
            f'<div class="service-row{" row-sm" if sm else ""}">{cell}'
            f'<h3>{it["title"]}</h3>'
            f'<p class="service-desc">{it.get("desc","")}</p>'
            f'<span class="service-badge">{ARW}</span></div></li>')
    out.append('</ul>')
    return ''.join(out)

def faq(items):
    out = ['<ul>']
    for i, it in enumerate(items):
        idx = it.get("idx", f"{i+1:02d}")
        out.append(
            f'<li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:{i*60}ms">'
            f'<div class="faq-row" role="button" tabindex="0" aria-expanded="false">'
            f'<span class="faq-idx">{idx}</span>'
            f'<div class="faq-content"><div class="faq-inner">'
            f'<h3 class="faq-t faq-t-top">{it["q"]}</h3>'
            f'<div class="faq-ans">{it["a"]}</div>'
            f'<h3 class="faq-t faq-t-bottom">{it["q"]}</h3>'
            f'</div></div>'
            f'<span class="faq-badge2" aria-hidden="true"></span>'
            f'</div></li>')
    out.append('</ul>')
    return ''.join(out)

def eyebrow(label):
    return f'<div class="eyebrow dark rvl rvl-op"><span class="dot"></span>{label}</div>'

def h2(text, mx='24ch'):
    return f'<h2 class="sec-h2" data-line-reveal style="max-width:{mx}"><span class="rvl-line"><span>{text}</span></span></h2>'

def cards_wrap(cards, cols=3):
    lis = ''.join(f'<li class="rvl" style="--rvl-y:40px; --rvl-delay:{i*90}ms">{c}</li>' for i, c in enumerate(cards))
    return f'<ul class="cards-{cols}">{lis}</ul>'

def nums(items, cols=3):
    # items: dict(cap, n, sub) — n은 <small> 포함 가능
    lis = ''.join(
        f'<li class="rvl" style="--rvl-delay:{i*90}ms"><div class="light-card num-card">'
        f'<span class="cap">{it["cap"]}</span><div class="n">{it["n"]}</div><p>{it["sub"]}</p></div></li>'
        for i, it in enumerate(items))
    return f'<ul class="cards-{cols}">{lis}</ul>'

def mark_svg(level):
    # 지원(on)·일부지원(mid) = 채운 동그라미 + 흰 체크(색으로 구분), 미지원(off) = 빈 링
    if level == 'off':
        inner = '<circle cx="7" cy="7" r="6" fill="none" stroke="currentColor" stroke-width="1"/>'
    else:
        inner = ('<circle cx="7" cy="7" r="6.4" fill="currentColor"/>'
                 '<path d="M4.9 7.1 L6.4 8.5 L9.2 5.6" fill="none" stroke="#fff" '
                 'stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>')
    return f'<svg class="mkv" viewBox="0 0 14 14" aria-hidden="true">{inner}</svg>'

def cell(level, text):
    return f'<span class="mk {level}">{mark_svg(level)}</span><span class="cell-txt">{text}</span>'

def legend_marks():
    items = [('on','지원'), ('mid','일부 지원'), ('off','미지원')]
    lis = ''.join(f'<span class="lg"><span class="mk {lv}">{mark_svg(lv)}</span>{lb}</span>' for lv, lb in items)
    return f'<div class="why-legend rvl">{lis}</div>'

def compare_table(headers, body_rows, hl=1, legend=None):
    # headers: [행라벨열='', 열1, 열2 ...]  / hl: headers 인덱스(1-base) 하이라이트 열
    # body_rows: dict(label, cells=[열1, 열2 ...])  cells는 문자열(cell() 사용 가능)
    thead = '<tr>' + ''.join(
        (f'<th class="hl">{h}</th>' if i == hl else f'<th>{h}</th>') for i, h in enumerate(headers)
    ) + '</tr>'
    rows_html = ''
    for r in body_rows:
        tds = ''.join(
            f'<td class="hl">{c}</td>' if (j + 1) == hl else f'<td>{c}</td>'
            for j, c in enumerate(r['cells']))
        rows_html += f'<tr><th scope="row">{r["label"]}</th>{tds}</tr>'
    leg = f'<div class="cmp-legend">{legend}</div>' if legend else ''
    return (f'{leg}<div class="cmp-wrap rvl"><table class="cmp">'
            f'<thead>{thead}</thead><tbody>{rows_html}</tbody></table></div>')

def bar_chart(body_rows, title=None, note=None):
    # body_rows: dict(l 라벨, v 값, w 폭%, hi=선택)
    head = f'<p class="barc-title">{title}</p>' if title else ''
    body = ''.join(
        f'<div class="barc-row{" hi" if r.get("hi") else ""}">'
        f'<span class="barc-l">{r["l"]}</span>'
        f'<div class="barc-track"><div class="barc-fill" style="width:{r["w"]}%"></div></div>'
        f'<span class="barc-v">{r["v"]}</span></div>'
        for r in body_rows)
    nt = f'<p class="sec-note">{note}</p>' if note else ''
    return f'<div class="barc rvl">{head}{body}</div>{nt}'

def chips(items):
    return '<div class="chip-row rvl">' + ''.join(f'<span class="chip">{x}</span>' for x in items) + '</div>'

def routes(items, active):
    return '<div class="routes rvl">' + ''.join(
        f'<a class="route{" on" if href == active else ""}" href="{href}">{label}</a>'
        for label, href in items) + '</div>'

def note(text):
    return f'<p class="sec-note rvl">{text}</p>'

def lead_p(text):
    return f'<p class="phero-lead rvl" style="margin-bottom:2rem">{text}</p>'

# 6개 솔루션 크로스링크 (다른 분야 솔루션)
SOL_ROUTES = [
    ('금융', 'solution-finance.html'),
    ('공공', 'solution-gov.html'),
    ('증명서', 'solution-cert.html'),
    ('화이트라벨 거래소', 'solution-exchange.html'),
    ('데이터주권', 'solution-data.html'),
    ('결제·정산', 'solution-settlement.html'),
]

PAGES = {}

# ---------------- company.html ----------------
PAGES['company.html'] = dict(
    title='회사소개 | PARAMETA',
    desc='파라메타는 신뢰할 수 있는 블록체인 기술을 바탕으로, 금융·기업·공공 등 다양한 산업에서 활용되는 디지털 인프라와 서비스를 제공합니다.',
    eyebrow='About PARAMETA',
    h1_lines=['Web2의 안정성과', 'Web3의 가능성을', '모두 경험한 기업'],
    lead='파라메타는 공공, 금융, 민간 IT 시스템 운영 경험과 1세대 메인넷과 dApp 구축 경험을 바탕으로, 기업의 디지털자산 사업을 안정적으로 시작하고 확장할 수 있도록 지원합니다.',
    crumb='Company — 회사소개',
    content=f'''
<section><div class="shell sec">
  {eyebrow('Vision')}
  {h2('Web2 + Web3를 연결하는 WalletFi 생태계를 만들어갑니다')}
  {lead_p('파라메타는 금융권·공공·민간의 전통금융(Web2)부터 퍼블릭 블록체인 플랫폼과 DeFi(Web3)까지, 양쪽 영역의 전문 경험과 노하우를 두루 갖췄습니다. 두 힘을 하나로 모아, 지갑으로 모든 금융을 연결하는 지갑 기반 금융 생태계 WalletFi를 만들어갑니다.')}
  <div class="rvl" style="display:flex; flex-direction:column; gap:1.75rem">
    <div><div style="font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); margin-bottom:.75rem">두 세계를 연결</div>{chips(['전통금융 TradFi', '탈중앙화 금융 DeFi'])}</div>
    <div><div style="font-size:var(--text-14); color:var(--accent); font-weight:600; margin-bottom:.75rem">WalletFi — 스테이블코인 · 자산 토큰화 · 크로스보더 결제 인프라</div>{chips(['금융기관 · 핀테크', 'CEX / DEX 사용자'])}</div>
    <div><div style="font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); margin-bottom:.75rem">Wallet Infrastructure</div>{chips(['K-BTF', 'loopchain', 'PDS', 'BFS', 'DID'])}</div>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Track Record')}
  {h2('10년의 트랙레코드, 숫자로 증명한 신뢰')}
  {lead_p('2016년부터 쌓아온 실적이 파라메타의 기술을 증명합니다.')}
  {nums([
    dict(cap='Since 2016', n='10년차', sub='국내 1세대 Web3 인프라 기업'),
    dict(cap='Investment', n='250억 원', sub='누적 투자유치'),
    dict(cap='Revenue', n='750억 원+', sub='누적 매출 (2016~2025)'),
    dict(cap='Quality', n='GS 1등급', sub='loopchain SW품질 인증'),
  ], cols=2)}
  <div class="rvl" style="margin:2.5rem 0">
    <div style="font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); margin-bottom:1rem">함께 투자한 파트너 — 누적 250억 원</div>
    {chips(['기술보증기금','한국성장금융','코리아에셋투자증권','L&S벤처캐피탈','TS인베스트먼트','키움인베스트먼트','패스파인더에이치','케이클라비스','신한벤처투자'])}
  </div>
  <div class="rvl" style="margin-bottom:2.5rem">
    <div style="font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); margin-bottom:1rem">인증 · 수상</div>
    {chips(['GS인증 1등급 (loopchain)','기술보증기금 TI-1 등급','과기정통부 장관 표창','KISA 기술특례상장 컨설팅 A등급','금융위원회 혁신금융서비스 지정'])}
  </div>
  {cards_wrap([
    dark_card('First', '세계 최초 블록체인 공동인증 상용화', '증권사 26개사를 하나의 온체인 신원 체계로 묶은 공동인증을 세계 최초로 상용화했습니다.'),
    dark_card('First', '국내 최초 금융권 DID 실명인증 상용화', '신한은행과 함께 금융권 DID 실명인증을 국내 최초로 상용화했습니다.'),
    dark_card('First', '국내 최초 블록체인 서비스 CSAP 인증', 'MyID 2.0으로 블록체인 서비스 최초의 CSAP 클라우드 보안 인증을 획득했습니다.'),
    dark_card('First', '국내 최초 DID Method Registry 등재', '국내 최초로 DID Method Registry에 등재했습니다.'),
  ], cols=2)}
  <div class="rvl" style="margin-top:2.5rem">
    <div style="font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); margin-bottom:1rem">함께한 파트너 · Stablecoin Alliance 초대 의장사</div>
    {chips(['삼성','삼성증권','미래에셋','NH농협','NH투자증권','신한','IBK기업은행','KB'])}
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('History')}
  {h2('디지털자산 시장을 만들어온 파라메타의 10년')}
  {rows([
    dict(idx='2016', title='(주)더루프 설립', desc='국내 1세대 Web3 인프라 기업으로 출발했습니다.'),
    dict(idx='2018', title='1세대 퍼블릭 메인넷 ICON 출시', desc='라인 블록체인 합작법인 ‘언체인’을 설립했습니다(아이콘루프 시절).'),
    dict(idx='2019', title='loopchain GS인증 1등급 · broof 출시', desc='금융위 혁신금융서비스로 지정됐습니다.'),
    dict(idx='2020', title='제주안심코드 218만 명 · 신한은행 DID 실명인증', desc='DID 금융실명인증을 상용화했습니다.'),
    dict(idx='2023', title='PARAMETA 리브랜딩 (구 아이콘루프)', desc='시리즈 C 투자를 유치했습니다.'),
    dict(idx='2024', title='K-BTF 공공 블록체인 공동인프라 사업자 선정', desc='공공 블록체인 공동 인프라 사업자로 선정됐습니다.'),
    dict(idx='2025', title='MyID 2.0 블록체인 서비스 최초 CSAP 인증', desc='조달청 디지털마켓에 등록했습니다.'),
    dict(idx='2026', title='Stablecoin Alliance 초대 의장사', desc='ADB ABMF 국경 간 거래 표준모델을 발표했습니다.'),
  ], meta=True)}
</div></section>
<section><div class="shell about-grid">
  <div class="about-globe">
    <svg class="icn about-globe-bg" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9.25" stroke="currentColor" stroke-width="1.4"/><ellipse cx="12" cy="12" rx="4.2" ry="9.25" stroke="currentColor" stroke-width="1.4"/><path stroke="currentColor" stroke-width="1.4" stroke-linecap="round" d="M2.75 12h18.5"/></svg>
    <div class="eyebrow dark" style="position:relative"><span class="dot"></span>Company</div>
    <div class="about-globe-bottom rvl" style="--rvl-y:12px">
      <svg class="icn" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9.25" stroke="currentColor" stroke-width="1.4"/><ellipse cx="12" cy="12" rx="4.2" ry="9.25" stroke="currentColor" stroke-width="1.4"/><path stroke="currentColor" stroke-width="1.4" stroke-linecap="round" d="M2.75 12h18.5"/></svg>
      <span>오시는 길 — (주)파라메타</span>
    </div>
  </div>
  <div class="about-right">
    <div class="addr-list rvl">
      <div><div class="k">Address</div><div class="v">서울특별시 서초구 강남대로 311, 드림플러스 강남 8층</div></div>
      <div><div class="k">English</div><div class="v">8F, DreamPlus Gangnam, 311 Gangnam-daero, Seocho-gu, Seoul, Republic of Korea</div></div>
      <div><div class="k">Phone</div><div class="v">02-2138-7026</div></div>
      <div><div class="k">Email</div><div class="v">info@parametacorp.com</div></div>
    </div>
  </div>
</div></section>
''')

# ---------------- careers.html ----------------
PAGES['careers.html'] = dict(
    title='채용 | PARAMETA',
    desc='디지털자산의 미래를 함께 만들 분을 찾습니다.',
    eyebrow='Careers',
    h1_lines=['디지털자산의 미래를', '함께 만들 사람'],
    lead='파라메타는 새로운 시장에 표준을 세우고, 기술을 사업에 안착시키는 여정을 함께할 동료를 찾습니다.',
    crumb='Company — 채용',
    content=f'''
<section><div class="shell sec">
  {eyebrow('Who We Look For')}
  {h2('인재상')}
  {cards_wrap([
    dark_card('01', 'Builder Mindset', '0에서 1을 만드는 일을 즐기는 사람. 새로운 시장에 표준을 세우고, 기술을 사업에 안착시키는 과정에 흥미를 느끼는 사람을 찾습니다.'),
    dark_card('02', 'Domain × Depth', '블록체인·디지털자산·공공 인프라 중 한 영역에서 깊이를 추구하는 사람. 표면적 트렌드보다 본질을 끝까지 파고드는 전문성을 중요하게 생각합니다.'),
    dark_card('03', 'Long-term Trust', '9년 동안 운영해 온 인프라처럼, 책임감과 일관성으로 신뢰를 쌓아가는 사람. 단기 성과보다 오래가는 결과를 만드는 일에 가치를 두는 사람을 찾습니다.'),
  ], cols=3)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Open Positions')}
  {h2('채용 공고')}
  <div class="light-card rvl" style="max-width:44rem">
    <p>진행 중인 채용 공고는 사람인 · 잡코리아 · LinkedIn 등 외부 채용 플랫폼에서 확인하실 수 있습니다.<br><br>
    무관한 분야라도 합류 의사가 있다면 컨택을 통해 자유 지원해 주세요.</p>
    <div style="margin-top:1.5rem">
      <button class="pill dark with-arrow arw-up hs-scale" data-modal>
        <span class="hspring">자유 지원하기<span class="pill-badge">{ARW}</span></span>
      </button>
    </div>
  </div>
</div></section>
''')

# ---------------- insights.html ----------------
PAGES['insights.html'] = dict(
    title='Insights | PARAMETA',
    desc='사업·파트너십·인증·수상 소식과 디지털자산 시장 인사이트를 한곳에서 확인할 수 있습니다.',
    eyebrow='Insights',
    h1_lines=['디지털자산 시장을', '읽는 인사이트'],
    lead='사업·파트너십·인증·수상 소식과 보도자료, 그리고 시장을 읽는 블로그를 한곳에 모았습니다.',
    crumb='Insights — 보도자료 · 블로그',
    content=f'''
<section><div class="shell sec">
  {eyebrow('Press Release')}
  {h2('보도자료')}
  {rows([
    dict(idx='2026.02', title="파라메타, ADB 주관 채권 포럼서 '온체인 KYC' 기반 국경 간 거래 표준 모델 발표"),
    dict(idx='2026.02', title='파라메타, 스테이블코인·STO 무료 컨설팅으로 디지털자산 사업 기회 확대 지원'),
    dict(idx='2023.11', title='김종협 파라메타 대표, 2023 블록체인 진흥주간에서 과학기술정보통신부 장관 표창 수상'),
    dict(idx='2023.09', title="파라메타, 기술신용평가 최고 등급 'TI-1' 획득 — 최상위 수준의 기술력 인정"),
    dict(idx='2023.08', title='파라메타, 카스투게더·솔브릭코리아와 국내 최초 모빌리티·태양광 토큰증권 플랫폼 구축'),
    dict(idx='2023.07', title="파라메타, 플루토스파트너스와 국내 최초 '부동산 NPL 토큰증권 플랫폼' 구축 협력"),
  ], sm=True, meta=True)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Blog')}
  {h2('디지털자산 시장을 읽는 인사이트')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('MARKET', '스테이블코인 사업, 무엇부터 시작할까', '규제·발행·유통까지, 스테이블코인 사업을 시작하기 전 짚어야 할 핵심을 정리합니다.')}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('DID', '금융권 DID 도입 체크리스트', '은행·증권사가 분산신원 인증을 도입하기 전에 확인할 항목을 정리합니다.')}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:180ms">{dark_card('COMPLIANCE', '온체인 KYC, 규제와 사용성 사이', '규제 요건을 지키면서도 사용자 경험을 해치지 않는 KYC 설계를 다룹니다.')}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:270ms">{dark_card('TECH', 'loopchain은 왜 즉시 확정인가', '즉시 확정(Finality)이 왜 중요한지, 합의 방식과 함께 쉽게 풀어 봅니다.')}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Blockchain 101')}
  {h2('용어정리')}
  {faq([
    dict(q='DID (Decentralized Identifier, 분산아이디)', a='외부 인증기관 없이 사용자가 자신의 디지털 서명으로 신원을 직접 증명하는 분산형 신원 체계. 필요한 정보만 선택적으로 공개할 수 있고, W3C 표준을 따릅니다. 자기주권신원(SSI)을 구현하는 핵심 기술입니다.'),
    dict(q='SSI (Self-Sovereign Identity, 자기주권신원)', a='개인이 자신의 신원 정보를 스스로 소유·관리하는 신원 모델. 중앙 발급기관이 아닌 사용자가 인증·공개 범위·이력을 직접 제어합니다. DID 기술이 SSI를 가능하게 합니다.'),
    dict(q='Stable Coin (스테이블 코인)', a='법정통화나 자산에 가치를 연동(Peg)해 가격 변동성을 최소화한 디지털 자산. 결제·송금·정산처럼 안정적인 가치 이동이 필요한 환경에서 활용됩니다.'),
    dict(q='DeFi (Decentralized Finance, 탈중앙화 금융)', a='은행 등 중앙 기관 없이 블록체인 위에서 자동으로 거래되는 금융 메커니즘. 스마트 컨트랙트로 송금·예치·대출·환전을 처리하며, 누구나 참여할 수 있습니다.'),
    dict(q='NFT (Non-Fungible Token, 대체 불가능 토큰)', a='교환·복제가 불가능한 고유 식별자를 가진 블록체인 기반 토큰. 작품·콘텐츠·자산을 유일한 형태로 표현하며 스마트 컨트랙트로 발행·이전됩니다. FT(대체 가능 토큰)의 상대 개념.'),
    dict(q='BTP (Blockchain Transmission Protocol)', a='서로 다른 블록체인 간에 자산과 메시지를 안전하게 이동시키는 인터체인 프로토콜. 검증·중계·릴레이 메커니즘으로 체인 간 신뢰 가능한 통신을 제공합니다. 파라메타가 직접 개발했습니다.'),
    dict(q='loopchain (루프체인)', a='파라메타가 자체 개발한 엔터프라이즈 블록체인 엔진. PBFT 계열 LFT 합의 알고리즘으로 즉시 확정(Finality)과 운영 안정성을 제공합니다. 금융·공공 환경의 요구사항을 충족하도록 설계되었습니다.'),
    dict(q='SCORE (Smart Contract on Reliable Environment)', a='파라메타의 자체 코어 엔진 루프체인 위에서 동작하는 스마트 컨트랙트 실행 환경. Java·Python 등 익숙한 언어로 컨트랙트를 작성할 수 있게 합니다.'),
  ])}
</div></section>
''')

# ---------------- parasta.html ----------------
PAGES['parasta.html'] = dict(
    title='ParaSta · 디지털자산 금융 인프라 | PARAMETA',
    desc='ParaSta — 스테이블코인·디지털자산 사업을 위한 모듈형 인프라. 발행·오케스트레이션·지갑·온체인 KYC를 골라 조립하세요. Compliant-Ready · Zero-Ops.',
    eyebrow='Digital Asset Platform',
    h1_lines=['ParaSta'],
    lead='스테이블코인, 디지털자산 비즈니스를 위한 모듈형 인프라입니다.<br>필요한 기능을 선택해 구성하고, 발행부터 운영까지 하나로 연결합니다.',
    crumb='Products — ParaSta',
    body_class='hero-dark',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">View Demo</span></a>
      <a class="pill outline no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>''',
    content=f'''
<section><div class="shell sec">
  <div class="whatis-grid">
    <div class="ps-flow rvl">
      <div class="ps-flow-band">
        <div class="ps-band-head">
          <span class="ps-band-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.66 3.13 3 7 3s7-1.34 7-3"/><path d="M5 12v6c0 1.66 3.13 3 7 3s7-1.34 7-3v-6"/></svg></span>
          <div class="lbl">디지털 자산</div>
        </div>
        <div class="ps-tags"><span class="ps-tag">스테이블코인</span><span class="ps-tag">은행 예금토큰</span><span class="ps-tag">토큰증권</span></div>
      </div>
      <div class="ps-flow-link" aria-hidden="true"></div>
      <div class="ps-flow-band ps-flow-core">
        <div class="ps-core-head">
          <img class="ps-flow-logo" src="assets/brand/parasta-logo.svg" alt="ParaSta" width="40" height="40">
          <div class="ps-core-text">
            <div class="core-title">ParaSta</div>
            <div class="core-sub">발행부터 운영까지 ParaSta 하나로</div>
          </div>
        </div>
        <div class="ps-tags"><span class="ps-tag">토큰발행</span><span class="ps-tag">가상자산 지갑</span><span class="ps-tag">온체인 KYC</span><span class="ps-tag">오케스트레이션</span><span class="ps-tag">어드민</span></div>
      </div>
      <div class="ps-flow-link" aria-hidden="true"></div>
      <div class="ps-flow-band">
        <div class="ps-band-head">
          <span class="ps-band-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-5 9 5"/><path d="M4 9.5V18"/><path d="M20 9.5V18"/><path d="M8 9.5V18"/><path d="M12 9.5V18"/><path d="M16 9.5V18"/><path d="M2.5 18h19"/></svg></span>
          <div class="lbl">은행 및 결제망 연결</div>
        </div>
        <div class="ps-tags"><span class="ps-tag">은행 예금원장</span><span class="ps-tag">펌뱅킹</span><span class="ps-tag">결제 인프라</span><span class="ps-tag">은행간 정산망</span></div>
      </div>
    </div>
    <div class="whatis-text rvl" style="--rvl-delay:120ms">
      {eyebrow('What is ParaSta')}
      {h2('발행부터 운영까지 연결하는<br>디지털자산 인프라')}
      {lead_p('ParaSta는 스테이블코인, 예금토큰 등 다양한 디지털자산의 발행과 운영을 하나의 플랫폼에서 지원하고, 기존 은행, 결제망과 유기적으로 연결합니다. 신원 확인부터 지갑, 정산, 감사까지 디지털자산 운영 전반을 함께합니다.')}
    </div>
  </div>
</div></section>
<section><div class="shell sec">
  <div class="why-grid">
    <div class="why-head">
      {eyebrow('Why ParaSta')}
      {h2('디지털자산을 실제 금융 서비스로 연결하는 하나의 인프라')}
      {legend_marks()}
    </div>
    <div class="why-table">
      {compare_table(
        ['', 'ParaSta', '글로벌 인프라 SaaS', '국내 커스터디', '자체 구축 · SI'],
        [
          dict(label='국내 규제 대응', cells=[cell('on','AML, 트래블룰, 감사 로그 내장'), cell('off','도입사 직접 대응'), cell('mid','수탁·보관 중심'), cell('off','규제 검토부터 직접 대응')]),
          dict(label='신원관리', cells=[cell('on','발행 레이어에 KYC, DID 기능 내장'), cell('mid','외부 KYC 솔루션 연동'), cell('off','신원 인증 기능 제한적'), cell('off','KYC, DID 직접 개발')]),
          dict(label='구축 방식', cells=[cell('on','검증된 모듈을 SDK로 유연하게 구성'), cell('mid','정해진 기능 범위 내 구성'), cell('mid','커스터디 기능 중심'), cell('off','처음부터 직접 개발')]),
          dict(label='도입·운영', cells=[cell('on','키 관리, 가스비, 노드 운영 대행'), cell('on','글로벌 시장에 빠르게 도입'), cell('on','검증된 수탁 운영'), cell('off','개발, 운영 직접 관리')]),
          dict(label='글로벌 확장', cells=[cell('mid','국내 환경 최적화, 멀티체인 지원'), cell('on','글로벌 네트워크 보유'), cell('off','국내 시장 중심'), cell('mid','구축 범위에 따라 상이')]),
        ], hl=1)}
    </div>
  </div>
</div></section>
<section><div class="shell sec">
  {eyebrow('Advantages')}
  {h2('실제 금융 서비스로 이어지는<br>하나의 인프라')}
  {cards_wrap([
    dark_card('MODULAR', '모듈형 API', '발행 엔진부터 온체인 KYC, 멀티체인 브릿지까지, 필요한 코어 모듈을 선택해 유연하게 구성할 수 있습니다. 처음부터 새로 개발할 필요 없이, 실제 현장에서 검증된 기술을 빠르게 적용할 수 있습니다.', grouped=True),
    dark_card('COMPLIANT', '규제 대응이 준비된 인프라', 'AML, 트래블룰, 감사 로그를 인프라에 통합해 규제 대응 부담을 줄입니다. 금융권과 함께 검증한 규제 기술을 그대로 적용할 수 있습니다.', grouped=True),
    dark_card('ZERO-OPS', '운영까지 책임지는 인프라', '키 관리부터 가스비 대납, 인프라 운영까지, 발행 이후의 운영 전반을 ParaSta가 지원합니다. 기업은 서비스와 비즈니스 성장에만 집중할 수 있습니다.', grouped=True),
  ], cols=3)}
</div></section>
<section><div class="shell sec">
  <div class="cm-grid">
    <div class="cm-head">
      <div class="cm-sticky">
        <div class="cm-head-in rvl" style="--rvl-y:20px">
          <div class="eyebrow dark"><span class="dot"></span>Core Modules</div>
          <h2 class="sec-h2" style="max-width:24ch">필요한 기능만 선택해 구성하는<br>5가지 코어 모듈</h2>
        </div>
      </div>
    </div>
  <ul class="cm-cards core-mods">
    <li>{dark_card('Issuance', 'Mint with Compliance, Scale Across Chains', '기업 고유의 스테이블코인과 토큰화 자산을 발행하고 관리합니다. Multi-sig, PoR 기반 준비자산 증빙, Whitelist, Blacklist, 자금 동결 기능을 포함한 6-Layer 구조로 발행부터 사후 검증까지 전 과정을 통제합니다.', ['발행, 소각, 준비자산 운용','PoR 기반 준비자산 증빙','자산 수명주기 실시간 모니터링'], grouped=True)}</li>
    <li>{dark_card('Wallet', 'Enterprise Control, Frictionless UX', '계정 추상화, ERC-4337을 기반으로 가스비 부담 없는 사용자 경험을 제공합니다. 여러 체인을 하나의 인터페이스로 통합하고, Stealth Address로 프라이버시를 보호합니다. 온체인 KYC 모듈과 연동해 신원이 확인된 지갑만 거래할 수 있도록 통제합니다.', ['가스비 없는 사용자 경험','멀티체인 통합 인터페이스','Stealth Address 기반 프라이버시 보호'], grouped=True)}</li>
    <li>{dark_card('Orchestration', 'Bridge Worlds, Settle Instantly', '은행 계좌와 온체인 지갑을 하나의 API로 연결합니다. Fiat, Crypto 자동 전환부터 예약 정산, 조건부 정산, 이벤트 기반 시스템 연동까지, 거래 전 과정을 하나의 흐름으로 관리합니다.', ['Fiat ↔ Crypto 자동 전환','예약, 조건부 정산','실시간 AML 스크리닝'], grouped=True)}</li>
    <li>{dark_card('On-chain KYC', 'Verify Once, Use Everywhere', '공인기관의 KYC 결과를 검증 가능한 크레덴셜, VC와 VP 형태로 발급하고, 검증된 지갑 주소를 온체인 신원 레지스트리, KYW에 등록합니다. 토큰 컨트랙트는 이체 시점에 레지스트리를 조회해 자격을 갖춘 지갑만 거래하도록 통제하며, 개인정보는 온체인에 저장하지 않습니다.', ['DID 기반 VC, VP 발급','KYW 온체인 화이트리스트','ERC-3643, T-REX 기반 이체 검증'], grouped=True)}</li>
    <li>{dark_card('Unified Admin', 'See Everything, Control Everything', '발행, 지갑, 오케스트레이션, 온체인 KYC 등 4개 모듈을 하나의 통합 관제 환경에서 관리합니다. Mint, Burn 통제부터 MPC 기반 키 관리, 다단계 승인, 자금 흐름 모니터링까지 모든 운영 현황을 한 화면에서 확인할 수 있습니다.', ['Mint, Burn 라이프사이클 통제','MPC 기반 키 관리, 다단계 승인','통합 감사 리포팅'], grouped=True)}</li>
  </ul>
  </div>
</div></section>
<section><div class="shell sec">
  {eyebrow('Core Technology')}
  {h2('엔터프라이즈급 기술을 인프라에 내재화')}
  <div class="ct-rows">{rows([
    dict(title='계정 추상화 (AA)', desc='복잡한 지갑 기능을 Web2 서비스처럼 간편하게 제공합니다. 기관이 자사 서비스에 지갑을 도입할 때 사용자 진입장벽을 낮춥니다.'),
    dict(title='선택적 공개 (ZKP, Selective Disclosure)', desc='영지식증명을 기반으로 KYC를 수행하되, 개인정보 원문은 공유하지 않고 필요한 정보만 선택적으로 증명합니다.'),
    dict(title='스텔스 주소 (Stealth Address)', desc='거래마다 새로운 수신 주소를 생성해, 사용자와 거래 내역 간의 연결을 어렵게 하는 프라이버시 보호 기술입니다.'),
    dict(title='단일 인터페이스 멀티체인 (Multi-chain)', desc='체인별로 지갑, SDK, 연동 기능을 각각 개발할 필요 없이, 하나의 인터페이스에서 여러 체인의 자산과 거래를 통합 관리합니다. 새로운 체인이 필요할 때도 동일한 API로 확장할 수 있어 특정 체인에 종속되지 않습니다.'),
    dict(title='MPC 키 분할, 복구 (Key Share)', desc='개인키를 여러 개의 키셰어로 나누어 분산 보관하고, 정해진 임계값 이상의 키셰어가 모일 때만 서명하거나 복구합니다. 개인키를 한곳에 보관하지 않아 분실과 탈취 위험을 줄입니다.'),
  ])}</div>
</div></section>
<!-- Proven Core: 메인 Why Parameta 스타일 다크 스탯 패널 -->
<section><div class="shell stats-shell">
  <div class="stats-panel rvl" style="--rvl-y:40px; --rvl-s:.99">
    <div class="eyebrow light"><span class="dot"></span>Proven Core</div>
    <h2 class="stats-h2" data-line-reveal><span class="rvl-line"><span>금융, 공공, Web3 현장에서<br>검증된 코어 기술</span></span></h2>
    <ul class="stats-grid pv-stats">
      <li class="rvl" style="--rvl-y:20px"><div class="stat-num"><span class="pv-val" data-val="29">0</span>+</div><div class="stat-label">금융기관</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:90ms"><div class="stat-num"><span class="pv-val" data-val="8">0</span>+</div><div class="stat-label">공공기관</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:180ms"><div class="stat-num"><span class="pv-val" data-val="4">0</span>+</div><div class="stat-label">Web3 프로젝트</div></li>
    </ul>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Partners')}
  {h2('함께한 파트너')}
  <div class="rvl" style="margin:0 0 3rem">
    {chips(['신한은행','NH농협은행','NH투자증권','삼성증권','삼성','KB','IBK기업은행','한화'])}
  </div>
  <div class="pn-grid">
    <article class="pn-card rvl" style="--rvl-y:24px">
      <div class="pn-head">
        <p class="pn-kick">규제 산업에서 검증된 기술</p>
        <h3>금융권</h3>
      </div>
      <ul class="pn-list">
        <li><h4>신한은행</h4><p>금융권 DID 실명인증 상용화</p></li>
        <li><h4>NH농협은행</h4><p>올원뱅크 실명인증 적용</p></li>
        <li><h4>한국투자증권 외 25개 증권사</h4><p>증권업권을 하나의 온체인 신원 체계로 연결한 공동인증 서비스. 여러 금융기관의 신원과 인증을 연동한 경험으로, 스테이블코인 인프라에 필요한 규제 대응과 기관 간 연결 역량을 검증.</p></li>
      </ul>
    </article>
    <article class="pn-card rvl" style="--rvl-y:24px; --rvl-delay:90ms">
      <div class="pn-head">
        <p class="pn-kick">스테이블코인이 발행되고 유통되는 환경</p>
        <h3>퍼블릭, 멀티체인</h3>
      </div>
      <ul class="pn-list">
        <li><h4>자체 블록체인 코어 엔진 개발, 운영</h4><p>PBFT 합의와 인터체인 프로토콜을 자체 기술로 구현한 퍼블릭 메인넷. 다국가 밸리데이터 환경에서 축적한 구축, 운영 경험.</p></li>
        <li><h4>멀티체인 오케스트레이션, 크로스체인 연동</h4><p>CEX, DEX 통합 유동성, 스마트 오더 라우팅, 체인 간 자산 이동을 처리하는 WalletFi 오케스트레이션 솔루션, PortX와 SuperCycl의 직접 개발, 운영 경험.</p></li>
        <li><h4>규제 친화형 DeFi, 유동성 인프라 기술</h4><p>통합 유동성 집계와 규제 준수형 거래 실행 등, 제도권 환경에 맞춘 DeFi 인프라 기술.</p></li>
      </ul>
      <p class="pn-note">퍼블릭 체인에서 축적한 코어 엔진과 오케스트레이션 경험,<br>스테이블코인 발행 이후를 뒷받침하는 기반.</p>
    </article>
  </div>
  <div class="cert-row rvl" style="margin-top:5rem; --rvl-y:24px">
    <div class="cert-item"><div class="cert-img"></div><div class="cert-txt">기술보증기금 TI-1</div></div>
    <div class="cert-item"><div class="cert-img"></div><div class="cert-txt">CSAP 인증</div></div>
    <div class="cert-item"><div class="cert-img"></div><div class="cert-txt">혁신금융서비스 지정</div></div>
  </div>
</div></section>
''')

# ---------------- portx.html ----------------
PAGES['portx.html'] = dict(
    title='PortX · 화이트라벨 거래소 솔루션 | PARAMETA',
    desc='PortX — 직접 구축 없이 자체 디지털자산 거래 플랫폼을 소유하는 가장 빠른 길. 화이트라벨 하이브리드 거래소 솔루션. 애그리게이션 엔진·Smart Access·논커스터디.',
    eyebrow='Exchange Solution',
    h1_lines=['PortX'],
    lead='PortX는 디지털자산 거래 기능을 빠르게 도입할 수 있는 화이트라벨 거래소 솔루션입니다. 기술·보안·운영 부담은 낮추고, 사용자는 기존 서비스 안에서 그대로 거래할 수 있습니다.',
    crumb='Products — Port X',
    body_class='hero-dark',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">View Demo</span></a>
      <a class="pill outline no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>''',
    content=f'''
<section><div class="shell sec">
  {eyebrow('Supported Exchanges')}
  {h2('주요 글로벌·국내 거래소와 연동')}
  {lead_p('Binance, Bybit, OKX, Hyperliquid 등 메이저 거래소의 유동성을 하나로 연결합니다.')}
  {chips(['Binance','OKX','Bybit','Bitget','Gate.io','Hyperliquid','Bithumb','bitFlyer','bitbank'])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Why PortX')}
  {h2('거래소를 만들지 않고, 거래 서비스를 시작하는 방법')}
  {lead_p('거래소를 통째로 구축하지도, 데이터만 연결하지도 않습니다. 외부 유동성과 실제 거래 경험을 그대로 내 브랜드 안으로 가져옵니다.')}
  {compare_table(
    ['', 'PortX (하이브리드)', '턴키 거래소 솔루션', '단순 API 연결'],
    [
      dict(label='제공 방식', cells=['외부 유동성 + 실제 거래 UX를 내 브랜드로', '완성된 거래소 스택을 통째로', '계정·거래내역 데이터만 연결']),
      dict(label='유동성', cells=['외부 CEX·DEX 유동성 통합', '직접 확보·운영 부담', '거래 자체가 불가']),
      dict(label='출시 부담', cells=['구축 없이 거래 서비스 출시', '매칭엔진·백오피스까지 무겁게', '가볍지만 거래 서비스는 아님']),
      dict(label='보안', cells=['비수탁 — 민감정보 미보관', '커스터디 부담', '해당 없음']),
    ], hl=1)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Why Now')}
  {h2('거래는 이미 일어나고 있습니다')}
  {lead_p('문제는 그 거래가 어디에서 일어나느냐입니다. 지금이 그 흐름을 내 서비스 안으로 가져올 때입니다.')}
  {rows([
    dict(idx='연 58.5조$', title='중앙화 무기한 선물 거래량', desc='그만큼의 거래가 지금도 외부 거래소에서 일어납니다.'),
    dict(idx='외부 이탈', title='정보는 내 서비스, 거래는 밖에서', desc='수수료와 사용자 생애가치가 함께 빠져나갑니다.'),
    dict(idx='지금 시작', title='화이트라벨로 매출 전환', desc='구축 부담 없이 그 거래를 내 브랜드 안 실질 매출로 전환할 수 있습니다.'),
  ], meta=True)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Key Features')}
  {h2('거래 경험을 연결하는 핵심 기능')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('Feature 01', 'Aggregation Engine', '주요 글로벌 거래소의 호가와 유동성을 통합해, 깊은 유동성과 안정적인 체결 환경을 제공합니다.', ['호가 · 유동성 통합','단일 진입점'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('Feature 02', 'Smart Access', 'QR 코드로 외부 거래소 계정을 간편하게 연결해, 복잡한 API 키 입력 없이 거래 연동을 시작할 수 있습니다.', ['QR 계정 연결','API 키 불필요'])}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Use Cases')}
  {h2('디지털자산 비즈니스의 시작부터 운영까지')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('Case 01', 'Supercycl', 'CEX와 DEX 유동성을 하나로 연결하는 무기한 선물 거래 플랫폼. Aggregation Engine과 Smart Access로 여러 거래소의 유동성을 연동합니다.', ['선물 거래','유동성 연동'], quote='PortX 덕분에 자체 선물거래 서비스를 더 빠르게 시작할 수 있었습니다.', cite='Supercycl 헤드 개발자', sm=False)}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('Case 02', '코인 세금 서비스', '거래소와 연동해 거래 내역을 불러오고 예상 세금을 계산하는 세무 플랫폼. Smart Access로 계정 연결 과정을 간소화했습니다.', ['세무 플랫폼','거래 내역 연동'], quote='세금 계산에 필요한 거래 정보를 빠르게 가져올 수 있었습니다.', cite='코인 세금 서비스 CEO', sm=False)}</li>
  </ul>
</div></section>
''')

# ---------------- myid.html ----------------
PAGES['myid.html'] = dict(
    title='MyID · K-BTF 공공기관 블록체인 공동 인프라 | PARAMETA',
    desc='블록체인 서비스 최초로 CSAP 인증을 받은 공공기관 전용 DID·NFT 플랫폼입니다.',
    eyebrow='DID Identity',
    h1_lines=['공공기관을 위한', '블록체인 SaaS,', 'K-BTF'],
    lead='블록체인 서비스 최초로 CSAP 인증을 받은 공공기관 전용 DID·NFT 플랫폼입니다. 1년 이상 걸리던 자체 구축 과정을 약 1주일로 줄이고, 도입 비용도 최대 90%까지 절감합니다.',
    crumb='Solutions — MyID · K-BTF',
    content=f'''
<section><div class="shell sec">
  {eyebrow('Infrastructure')}
  {h2('공공기관을 위한 블록체인 공동 인프라')}
  {rows([
    dict(title='기관별 구축 부담 없이 — 공동 인프라', desc='각 기관이 따로 블록체인을 만들지 않아도 공동 인프라 위에서 서비스를 운영합니다.'),
    dict(title='SaaS 형태로 빠르게 도입', desc='복잡한 인프라 구축 과정 없이 필요한 기능을 서비스 형태로 이용합니다.'),
    dict(title='DID · NFT 기반 인증 지원', desc='도민증, 공무원증, 수료증, NFT 사원증 등 공공 인증 서비스를 발급·관리합니다.'),
    dict(title='CSAP 인증 기반 운영', desc='공공기관이 안심하고 도입할 수 있도록 클라우드 보안 인증 기준을 갖췄습니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('핵심 기술')}
  {h2('데이터 주권과 프라이버시를 지키는 독자 기술')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('Tech 01', 'W3C 표준 기반', 'W3C DID 1.0과 VC 2.0 표준 기반의 신원증명 환경. 신뢰수준 LoA를 단계별로 적용해 검증 강도를 설정합니다.', ['DID 1.0','VC 2.0','LoA'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('Tech 02', '필요한 정보만 증명', '선택적 공개, 범위 증명, 소속 증명, 발급자 비식별 지원. 개인정보 전체 공개 없이 필요한 사실만 증명합니다.', ['선택적 공개','범위 증명'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:180ms">{dark_card('Tech 03', '개인 데이터 저장소 (PDS)', '고정된 증명서(VC)를 넘어, 계속 바뀌는 내 데이터까지 본인이 직접 통제하며 안전하게 보관합니다.', ['PDS','데이터 주권'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:270ms">{dark_card('Tech 04', '블록체인 파일 시스템 (BFS)', '대용량 파일을 여러 노드에 다중 복제(멀티 피닝)해, 유실 없이 안전하게 보관하는 분산 저장 기술입니다.', ['BFS','멀티 피닝'])}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('References')}
  {h2('공공 현장에서 검증된 K-BTF')}
  {rows([
    dict(idx='서울', title='서울특별시 · 블록체인 표준 플랫폼', desc='서울시 블록체인 표준 플랫폼에 DID·인증 기반 기술을 공급합니다.'),
    dict(idx='부산', title='부산광역시 · 블록체인 배터리 여권', desc='전기차 배터리 생애주기 데이터를 DID·VC·PDS로 관리하고, EU DPP 규제 대응 기반을 구현합니다.'),
    dict(idx='경북', title='경상북도 · 블록체인 마이데이터', desc='도민 대상 공공 마이데이터 서비스에 블록체인·DID 신원인증을 적용합니다.'),
  ], meta=True)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('플랫폼 구성')}
  {h2('MyID 2.0을 이루는 두 가지 구성')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('01 / For Public Organizations', 'MyID 파트너센터', '공공기관이 원하는 형태의 모바일 인증서(DID)를 코드 한 줄 없이 만들고, 검증 항목만 골라 설정합니다. 발급부터 검증·관리까지 콘솔 하나에서 이뤄집니다.', ['발급 · 검증','통합 콘솔'], sm=False)}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('02 / For Citizens', '쯩 (zzeung) for 공공기관', '시민이 직접 지니는 디지털 지갑. 신분증·운전면허증·여권부터 NFT 사원증까지 보관하고, QR·블루투스·NFC·HTTP로 어디서든 제시·검증합니다.', ['디지털 지갑','QR · NFC'], sm=False)}</li>
  </ul>
</div></section>
''')

# ---------------- privacy.html / terms.html ----------------
def legal(sections):
    return '<section><div class="shell sec"><div class="legal-body rvl">' + ''.join(
        f'<h3>{t}</h3><p>내용 준비 중</p><span class="legal-note">법무 확인 필요</span>' for t in sections
    ) + '</div></div></section>'

PAGES['privacy.html'] = dict(
    title='개인정보처리방침 | PARAMETA',
    desc='PARAMETA 개인정보처리방침',
    eyebrow='Info',
    h1_lines=['개인정보처리방침'],
    lead='PARAMETA의 개인정보 수집·이용에 대한 방침입니다.',
    crumb='Info — 개인정보처리방침',
    content=legal(['1. 수집하는 개인정보 항목','2. 개인정보의 이용 목적','3. 보유 및 이용 기간','4. 제3자 제공','5. 이용자의 권리','6. 개인정보 보호책임자 및 문의처']))

PAGES['terms.html'] = dict(
    title='이용약관 | PARAMETA',
    desc='PARAMETA 이용약관',
    eyebrow='Info',
    h1_lines=['이용약관'],
    lead='PARAMETA 서비스 이용에 대한 약관입니다.',
    crumb='Info — 이용약관',
    content=legal(['제1조 (목적)','제2조 (정의)','제3조 (서비스의 제공)','제4조 (이용자의 의무)','제5조 (면책)']))


# ---------------- myid.html (DID 솔루션 — 실제 myid.html 콘텐츠) ----------------
PAGES['myid.html'] = dict(
    title='MyID · 자기주권 분산신원 | PARAMETA',
    desc='MyID — 기업·민간을 위한 자기주권형 분산신원(DID) 솔루션. W3C 표준 기반으로 발급·보관·검증을 하나로. 내가 나를 증명하는 법.',
    eyebrow='DID Solution',
    h1_lines=['MyID'],
    lead='기업과 기관이 신원 인증 서비스를 안전하게 구축할 수 있도록 지원하는 블록체인 기반 W3C 표준 DID 솔루션입니다. 내가 나를 증명하는 법, MyID.',
    crumb='Products — MyID',
    content=f"""
<section><div class="shell sec">
  <ul class="cards-2">
    <li class="rvl"><div class="light-card num-card"><span class="cap">Users</span><div class="n">약 370만</div><p>MyID · DID 누적 이용자 수</p></div></li>
    <li class="rvl" style="--rvl-delay:90ms"><div class="light-card num-card"><span class="cap">Verifications</span><div class="n">9,100만<small>+</small></div><p>제주안심코드 누적 인증 건수</p></div></li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Milestones')}
  {h2('국내외 최초 기록을 만들어온 DID')}
  {rows([
    dict(idx='국내 최초', title='DID Method Registry 등록'),
    dict(idx='국내 최초', title='DID 기반 혁신금융서비스 지정'),
    dict(idx='국내 최초', title='금융권 KYC DID 상용화'),
    dict(idx='세계 최초', title='블록체인 공동인증 — 증권사 26개사'),
  ], sm=True, meta=True)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Platform')}
  {h2('MyID는 블록체인 기반 DID 플랫폼입니다')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('Console', 'MyID 파트너센터', '코드 없이 DID·VC를 생성하고, 검증 항목을 구성할 수 있는 관리자 콘솔입니다. 발급·검증 이력과 인증 절차를 대시보드에서 통합 관리합니다.', ['DID·VC 생성','검증 항목 설정','이력 대시보드'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('Wallet', 'DID 지갑', '사용자가 자신의 DID와 VC를 직접 관리하는 신원 지갑입니다. Wallet SDK로 서비스 앱에 지갑 기능을 연동하고, 외부 발급 VC도 보관·이용할 수 있습니다.', ['Wallet SDK','외부 VC 보관','PDS 암호화'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:180ms">{dark_card('API', 'MyID API', 'DID 관리, VC 발급과 유효성 검증, VP 검증 등 신원 인증에 필요한 기능을 API로 제공합니다. 여러 블록체인과 연결된 통합 API로 외부 VC 연계도 지원합니다.', ['VC 발급','VC·VP 검증','외부 VC 연계'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:270ms">{dark_card('BaaS', '블록체인 BaaS', 'MyID 서비스에 필요한 퍼블릭·프라이빗 블록체인 환경을 서비스 형태로 제공합니다. loopchain core2 기반으로 안정적인 DID 서비스 운영을 지원합니다.', ['퍼블릭·프라이빗','loopchain core2'])}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Issue & Hold')}
  {h2('신원증명이 발급되고 검증되는 구조')}
  {rows([
    dict(idx='Issuer', title='발급기관', desc='신원증명(VC)을 발급하고, 취소·만료 상태를 관리합니다.'),
    dict(idx='Holder', title='사용자', desc='VC를 DID 지갑에 보관하고, 필요한 정보만 선택해 제출합니다.'),
    dict(idx='Verifier', title='검증기관', desc='제출된 VC의 발급자와 유효성을 확인합니다.'),
    dict(idx='Chain', title='블록체인 인프라', desc='VC 상태 정보를 기록해 위·변조 여부를 검증할 수 있게 합니다.'),
  ], meta=True)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Features')}
  {h2('MyID 주요 기능')}
  {rows([
    dict(title='DID · Key 관리', desc='플랫폼의 각 주체에게 DID를 발급하고, 키(Key)를 안전하게 관리합니다.'),
    dict(title='크레덴셜 발급 · 제출', desc='신원증명(VC)을 발급하고, 사용자가 필요한 정보만 골라 제출합니다.'),
    dict(title='크레덴셜 검증 · 폐기', desc='제출된 VC의 발급자·유효성을 검증하고, 취소·만료 상태를 관리합니다.'),
    dict(title='전자서명', desc='사용자·발급자·검증자 사이 모든 크레덴셜에 전자서명을 포함해 보안성을 높입니다.'),
    dict(title='저장 (PDS · Vault)', desc='크레덴셜을 별도 클라우드에 안전하게 저장해, 사용자가 본인 데이터를 직접 통제합니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Technology')}
  {h2('데이터 주권과 프라이버시를 지키는 핵심 기술')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('Tech 01', 'PDS — 개인 데이터 저장소', '한 번 발급되면 고정되는 증명서(VC)를 넘어, 계속 바뀌는 내 데이터까지 본인이 직접 통제하며 안전하게 보관합니다.', ['데이터 주권'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('Tech 02', 'Zero-Knowledge Proof — 영지식증명', '원본 정보를 드러내지 않고도 "성인이다", "특정 자격이 있다" 같은 사실만 증명합니다. 범위 증명·소속 증명을 지원합니다.', ['범위 증명','소속 증명'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:180ms">{dark_card('Tech 03', 'Selective Disclosure — 선택적 공개', '증명서 전체가 아니라 요구된 항목만 골라 제출합니다. 불필요한 개인정보는 아예 공개하지 않습니다.', ['최소 공개'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:270ms">{dark_card('Tech 04', 'Issuer Privacy — 발급자 비식별', '검증 과정에서 어느 기관이 발급했는지까지 감춰, 발급 이력이 불필요하게 노출되지 않도록 보호합니다.', ['프라이버시'])}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Lineup')}
  {h2('하나의 MyID, 세 가지 도입 형태')}
  {cards_wrap([
    dark_card('On-Premise', '구축형 MyID', 'MyID를 자사 인프라에 직접 구축해, 완전히 통제하고 자유롭게 커스터마이징하는 기업용 도입 방식입니다.', ['자사 인프라','커스터마이징']),
    dark_card('민간 SaaS', '쯩 (zzeung)', "구축 없이 구독형으로 바로 시작합니다. 시민용 디지털 지갑 앱 '쯩'으로 민간 서비스에 신원인증을 붙입니다.", ['구독형','디지털 지갑']),
    dark_card('공공 SaaS', 'MyID 2.0 (K-BTF)', '공공기관 전용 SaaS. 과기정통부·KISA 주관 K-BTF 공동 인프라 위에서 별도 구축 없이 도입합니다.', ['공공 전용','K-BTF']),
  ], cols=3)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('References')}
  {h2('금융·공공·기업이 검증한 적용 사례')}
  {rows([
    dict(idx='Finance', title='신한은행 · NH농협은행 금융실명인증', desc='기존 실명확인 3단계를 MyID 1단계로 통합해 비대면 실명인증을 간소화했습니다. NH농협은행은 올원뱅크 올원PASS 발급·재발급, 송금 이체한도 상향 등에 적용했습니다.'),
    dict(idx='Finance', title='SBI저축은행 블록체인 개인인증', desc='블록체인 기반 개인인증을 도입해 안전하고 간편한 본인확인 절차를 제공했습니다.'),
    dict(idx='Public', title='제주안심코드', desc='제주도청과 함께 개발한 전자출입명부 서비스로, QR 스캔만으로 출입 정보를 남깁니다. 설치 업장 6만 개, 앱 설치 218만 건, 누적 인증 9,100만 건을 기록했습니다.'),
    dict(idx='Public', title='질병관리청 백신접종증명', desc='질병관리청 시스템과 연동해 백신 접종 정보를 신원증명서(VC)로 발급하고, 제주안심코드 전자출입명부와 결합해 제출할 수 있게 했습니다.'),
    dict(idx='Public', title='강원도 나야나', desc='강원도 행정·경제·복지 통합 서비스에 DID 기반 신원인증을 적용했습니다.'),
    dict(idx='Public', title='경상북도 모이소', desc='행정안전부 우수 서비스로 선정된 도민 앱. 도민증 발급부터 복지급여 신청, 공공 마이데이터 연계, 관광 QR까지 하나로 제공했습니다.'),
    dict(idx='Public', title='모바일 운전면허인증', desc='ICT 규제 샌드박스 임시허가를 획득해 모바일 운전면허 인증 시범 서비스를 진행했습니다.'),
    dict(idx='Enterprise', title='포스코 체인지업그라운드', desc='출입통제부터 방문자 초대, 사무기기 이용, 공간 예약, 주차관리까지 DID 신원인증 하나로 처리했습니다. 포스코·포스텍·RIST 구성원은 소속 증명만으로 시설을 이용했습니다.'),
  ], meta=True)}
</div></section>
""")

# ---------------- kbtf.html (K-BTF — 기존 myid20 콘텐츠) ----------------
PAGES['kbtf.html'] = dict(
    title='KBTF · 공공기관 블록체인 공동 인프라 | PARAMETA',
    desc='MyID 2.0 — 블록체인 서비스 최초 CSAP 인증. 공공기관이 별도 구축 없이 도입 1주일·비용 90% 절감으로 DID·NFT·블록체인 서비스를 쓰는 공공 전용 SaaS. K-BTF 공동 인프라 기반.',
    eyebrow='Public Blockchain SaaS',
    h1_lines=['KBTF'],
    lead='블록체인 서비스 최초로 CSAP 인증을 받은 공공기관 전용 DID·NFT 플랫폼입니다. 자체 구축 1년·수억 원이 들던 블록체인 도입을 1주일·비용 90% 절감으로 끝냅니다.',
    crumb='Products — KBTF',
    content=f"""
<section><div class="shell sec">
  <ul class="cards-3">
    <li class="rvl"><div class="light-card num-card"><span class="cap">Security</span><div class="n">최초</div><p>블록체인 서비스 CSAP 클라우드 보안 인증 (2025)</p></div></li>
    <li class="rvl" style="--rvl-delay:90ms"><div class="light-card num-card"><span class="cap">Procurement</span><div class="n">유일</div><p>조달청 디지털마켓 등록 블록체인 SaaS</p></div></li>
    <li class="rvl" style="--rvl-delay:180ms"><div class="light-card num-card"><span class="cap">Speed · Cost</span><div class="n">1주 · 90%↓</div><p>자체 구축(1년·수억 원) 대비 도입 기간·비용</p></div></li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('MyID 2.0 · Public')}
  {h2('공공기관이 하나의 플랫폼에서 쓰는 블록체인 SaaS')}
  {lead_p('MyID 2.0은 공공기관이 하나의 플랫폼에서 블록체인 서비스를 이용할 수 있도록 제공하는 구독형 블록체인 서비스입니다. 과학기술정보통신부·KISA가 주관하는 K-BTF(Korea Blockchain Trust Framework)의 공식 서비스입니다.')}
  <div class="rvl" style="display:flex; flex-direction:column; gap:1.75rem">
    <div><div style="font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); margin-bottom:.75rem">공공 발행 — 정부·전국 지자체</div>{chips(['DID','증명서','NFT'])}</div>
    <div><div style="font-size:var(--text-14); color:var(--accent); font-weight:600; margin-bottom:.75rem">MyID 2.0 — 발급·보관·관리 (파라메타 운영)</div>{chips(['신분증','증명서','자격증','NFT'])}</div>
    <div><div style="font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); margin-bottom:.75rem">공공·민간 활용</div>{chips(['공공 서비스','은행 개설','항공','취업'])}</div>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Compare')}
  {h2('구축형 MyID vs 공동 인프라 MyID 2.0')}
  {compare_table(
    ['', 'MyID (구축형)', 'MyID 2.0 (공동 인프라)'],
    [
      dict(label='대상', cells=['민간 기업 (금융·기업)', '공공기관']),
      dict(label='도입 방식', cells=['자사 서비스에 맞춘 개별 구축·운영', '공동 인프라(K-BTF) 위 SaaS 이용']),
      dict(label='기간·비용', cells=['수개월 구축, 수억 원대 예산', '1주일 도입, 비용 90% 절감']),
      dict(label='강점', cells=['완전한 커스터마이징과 독립 운영', '별도 구축 없이 즉시, CSAP 인증 보안']),
    ], hl=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('플랫폼 구성')}
  {h2('MyID 2.0을 이루는 두 가지 구성')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('01 / For Public Organizations', 'MyID 파트너센터', '공공기관이 원하는 형태의 모바일 인증서(DID)를 코드 한 줄 없이 만들고, 검증 항목만 골라 설정합니다. 발급부터 검증·관리까지 콘솔 하나에서 이뤄집니다.', ['발급 · 검증','통합 콘솔'], sm=False)}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('02 / For Citizens', '쯩 (zzeung) for 공공기관', '시민이 직접 지니는 디지털 지갑. 신분증·운전면허증·여권부터 NFT 사원증까지 보관하고, QR·블루투스·NFC·HTTP로 어디서든 제시·검증합니다.', ['디지털 지갑','QR · NFC'], sm=False)}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Features')}
  {h2('파트너센터 하나로, 발급부터 관리까지')}
  {cards_wrap([
    dark_card('01', '인증서 생성 · 검증 정보 설정', '원하는 형태의 모바일 인증서(DID)를 코드 없이 만들고, 검증에 필요한 항목만 골라 설정합니다. 과하지 않게 꼭 필요한 정보만 모읍니다.'),
    dark_card('02', '인증서 발급 · 검증 이력', '발급·제출·검증 데이터를 실시간으로 모니터링하고, 건별 상세 내역까지 한 화면에서 확인합니다.'),
    dark_card('03', '인증서 통합 관리', '발급·취소·만료 상태와 인증서 전 과정을 하나의 콘솔에서 통합 관리합니다.'),
  ], cols=3)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('핵심 기술')}
  {h2('데이터 주권과 프라이버시를 지키는 독자 기술')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('PDS', '개인 데이터 저장소', '한 번 발급되면 고정되는 증명서(VC)를 넘어, 계속 바뀌는 내 데이터까지 본인이 직접 통제하며 안전하게 보관합니다.', ['데이터 주권'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('BFS', '블록체인 파일 시스템', '문서·이미지 같은 대용량 파일을 여러 노드에 다중 복제(멀티 피닝)해, 유실 없이 안전하게 보관하는 분산 저장 기술입니다.', ['멀티 피닝'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:180ms">{dark_card('ZKP', '영지식증명', '원본 정보를 드러내지 않고도 "성인이다", "특정 자격이 있다" 같은 사실만 증명합니다. 범위 증명·소속 증명을 지원합니다.', ['범위 증명','소속 증명'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:270ms">{dark_card('Selective Disclosure', '선택적 공개', '증명서 전체가 아니라 요구된 항목만 골라 제출합니다. 불필요한 개인정보는 아예 공개하지 않습니다.', ['최소 공개'])}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Applied Cases')}
  {h2('공공기관 현장에서 실증된 인프라')}
  {cards_wrap([
    dark_card('서울특별시', '블록체인 표준 플랫폼', '서울시 블록체인 표준 플랫폼에 DID·인증 기반 기술을 공급했습니다.'),
    dark_card('부산광역시', '블록체인 배터리 여권 플랫폼', '전기차 배터리 전 생애주기 데이터를 DID·VC·PDS로 관리. EU 디지털 제품 여권(DPP) 규제 대응 기반을 MyID 2.0 위에서 구현했습니다.'),
    dark_card('경상북도', '블록체인 마이데이터 플랫폼', '도민 대상 공공 마이데이터 서비스에 블록체인·DID 신원인증을 적용했습니다.'),
  ], cols=3)}
</div></section>
""")

# ---------------- broof.html ----------------
_broof_orgs = ['서울특별시','POSTECH','한국생산성본부','사람인','인천','한경닷컴','한빛미디어','스터디파이','아트앤가이드','심플로우','해시넷','서울시민청']
_broof_chips = ''.join(f'<span class="tag on-light">{o}</span>' for o in _broof_orgs)
PAGES['broof.html'] = dict(
    title='Broof · 블록체인 증명서 발급 | PARAMETA',
    desc='블록체인 기반 디지털 증명서 발급·검증 서비스입니다. 발급은 웹에서 간편하게, 검증은 QR 하나로.',
    eyebrow='Digital Credentials',
    h1_lines=['Broof'],
    lead='Broof는 블록체인 기반 디지털 증명서 발급·검증 서비스입니다. 별도 시스템 구축 없이 웹에서 증명서를 발급하고, QR 하나로 원본 여부와 위·변조 여부를 즉시 확인할 수 있습니다.',
    crumb='Products — Broof',
    body_class='hero-dark',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">View Demo</span></a>
      <a class="pill outline no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>''',
    content=f"""
<section><div class="shell sec">
  <ul class="cards-3">
    <li class="rvl"><div class="light-card num-card"><span class="cap">First</span><div class="n">정부위원회 첫</div><p>블록체인 기반 위촉장 발급 (국가AI전략위원회)</p></div></li>
    <li class="rvl" style="--rvl-delay:90ms"><div class="light-card num-card"><span class="cap">Issued</span><div class="n">90,000건<small>+</small></div><p>누적 블록체인 증명서 발급</p></div></li>
    <li class="rvl" style="--rvl-delay:180ms"><div class="light-card num-card"><span class="cap">Adopted</span><div class="n">20곳<small>+</small></div><p>누적 도입 기관 (대학 · 공공 · 기업)</p></div></li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Overview')}
  {h2('복잡한 구축 없이 증명서 발급부터 검증까지')}
  {rows([
    dict(title='위 · 변조 방지', desc='발급된 증명서의 원본 정보를 블록체인에 기록해 내용 변경 여부를 즉시 확인합니다.'),
    dict(title='QR 즉시 검증', desc='QR 스캔만으로 증명서의 진위와 원본 여부를 현장에서 바로 확인합니다.'),
    dict(title='간편 발급', desc='명단 업로드만으로 여러 건의 증명서를 한 번에 발급합니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Workflow')}
  {h2('올리고, 발급하고, 확인하면 끝')}
  {cards_wrap([
    dark_card('STEP 1', '템플릿 · 명단 등록', '증명서 양식을 선택하고, 수령자 명단을 업로드합니다.'),
    dark_card('STEP 2', '증명서 발급', '명단에 맞춰 증명서가 발급되고, 원본 정보가 블록체인에 기록됩니다.'),
    dark_card('STEP 3', '수령 · QR 검증', '수령자는 증명서를 받고, 제출처는 QR로 진위를 바로 확인합니다.'),
  ], cols=3)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Core Features')}
  {h2('발급 후 관리까지 한 번에')}
  {rows([
    dict(title='자동 알림', desc='증명서 발급과 동시에 카카오톡·이메일로 수령자에게 안내를 보냅니다.'),
    dict(title='발급 현황 관리', desc='발급·폐기·만료 상태를 한눈에 확인하고, 여러 담당자가 함께 관리합니다.'),
    dict(title='사용량 기반 과금', desc='정기 구독 없이 발급한 만큼만 이용해 부담 없이 시작합니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Applied Cases')}
  {h2('다양한 기관이 선택한 디지털 증명서')}
  {cards_wrap([
    dark_card('University', '포스텍 POSTECH', '블록체인 전문가과정 수료증을 정기적으로 발급합니다.', ['수료증']),
    dark_card('Enterprise', '미래에셋', '장학증서에 QR 검증 기능을 적용해 디지털로 전달합니다.', ['장학증서','QR 검증']),
    dark_card('Education', '교육 · 자격 기관', '수료증과 인증서 발급에 Broof를 활용하고 있습니다.', ['수료증','인증서']),
  ], cols=3)}
  <div class="rvl" style="margin-top:3rem">
    <div style="font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); margin-bottom:1rem">여러 기관이 이미 Broof를 활용하고 있습니다</div>
    <div style="display:flex; flex-wrap:wrap; gap:.5rem">{_broof_chips}</div>
  </div>
</div></section>
""")


# ---------------- contact.html ----------------
PAGES['contact.html'] = dict(
    title='문의 · 무료 컨설팅 | PARAMETA',
    desc='스테이블코인·STO 1:1 무료 컨설팅 신청. 파라메타 디지털자산 인프라 도입 문의.',
    eyebrow='Contact',
    h1_lines=['문의 · 무료 컨설팅'],
    lead='궁금하신 사항이 있으시면 문의하기를 이용해주세요. 담당자가 자세하게 안내해드리겠습니다.',
    crumb='Contact — 문의 · 무료 컨설팅',
    content=f"""
<section><div class="shell sec">
  <div class="cards-2" style="align-items:start">
    <div class="light-card rvl">
      <span class="cap">컨설팅 신청</span>
      <p style="margin-bottom:1.5rem">담당자가 영업일 기준 1~2일 내 회신드립니다. 모든 정보는 컨설팅 목적으로만 사용됩니다.</p>
      <form class="modal-form" id="contactForm">
        <div class="cards-2" style="gap:1rem">
          <div class="modal-field"><label for="cfName">이름</label><input id="cfName" type="text" required placeholder="이름"></div>
          <div class="modal-field"><label for="cfOrg">회사 / 기관</label><input id="cfOrg" type="text" required placeholder="회사 또는 기관명"></div>
          <div class="modal-field"><label for="cfEmail">이메일</label><input id="cfEmail" type="email" required placeholder="you@company.com"></div>
          <div class="modal-field"><label for="cfTel">연락처</label><input id="cfTel" type="tel" placeholder="010-0000-0000"></div>
        </div>
        <div class="modal-field"><label for="cfService">관심 서비스</label>
          <select id="cfService" required>
            <option>ParaSta — 디지털자산 인프라</option>
            <option>MyID 2.0 — 공공 분산신원</option>
            <option>PortX — 화이트라벨 거래소</option>
            <option>기타 / 잘 모르겠어요</option>
          </select>
        </div>
        <div class="modal-field"><label for="cfMsg">문의 내용</label>
          <textarea id="cfMsg" rows="5" required resize="none" placeholder="검토 중인 사업, 일정, 환경(SaaS/온프레미스)을 알려주세요."></textarea>
        </div>
        <label style="display:flex; align-items:center; gap:.5rem; font-size:var(--text-14); color:rgba(var(--ink-rgb),.6)">
          <input type="checkbox" required style="width:1rem; height:1rem"> 개인정보 수집·이용에 동의합니다
        </label>
        <div class="modal-bottom">
          <span class="modal-note" id="cfNote">영업일 기준 1~2일 내 회신드립니다.</span>
          <button class="pill dark with-arrow arw-up hs-scale" type="submit">
            <span class="hspring"><span id="cfSubmitLabel">상담 신청</span><span class="pill-badge">{ARW}</span></span>
          </button>
        </div>
      </form>
    </div>
    <div class="rvl" style="--rvl-delay:120ms">
      <div class="light-card" style="margin-bottom:1.5rem">
        <span class="cap">바로 문의하기</span>
        <p style="margin-bottom:1.25rem">폼 작성이 번거롭다면 메일·전화로 바로 연락주세요.</p>
        <div class="addr-list">
          <div><div class="k">Email</div><div class="v">info@parametacorp.com</div></div>
          <div><div class="k">Tel</div><div class="v">02-2138-7026</div></div>
          <div><div class="k">Hours</div><div class="v">평일 10:00 – 18:00</div></div>
        </div>
      </div>
      <div class="light-card">
        <span class="cap">오시는 길</span>
        <div class="addr-list">
          <div><div class="k">Address</div><div class="v">서울특별시 서초구 강남대로 311 드림플러스 강남 8F</div></div>
        </div>
      </div>
    </div>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Process')}
  {h2('컨설팅 진행 방식 — 부담 없이 3단계로')}
  {cards_wrap([
    dark_card('STEP 01', '신청 접수', '폼을 작성하시면 담당자가 영업일 기준 1~2일 내 회신드립니다.'),
    dark_card('STEP 02', '1:1 컨설팅', '온라인·오프라인 미팅으로 사업 단계·요구사항·예산을 함께 정리합니다.'),
    dark_card('STEP 03', '제안 및 검토', '최적의 솔루션 구성과 도입 로드맵을 제안서로 제공합니다.'),
  ], cols=3)}
</div></section>
""")

# ================= SOLUTION 6종 (신규) =================

# ---------------- solution-finance.html ----------------
PAGES['solution-finance.html'] = dict(
    title='금융 디지털자산 솔루션 | PARAMETA',
    desc='규제 환경에 맞춘 엔터프라이즈 디지털자산 금융 플랫폼. 발행·지갑·오케스트레이션·온체인 KYC·통합관제를 하나로. 스테이블코인·예금토큰·RWA·토큰증권까지 단계적 확장.',
    eyebrow='Solutions — 금융',
    h1_lines=['규제 환경에 맞춘', '엔터프라이즈 디지털자산', '금융 플랫폼'],
    lead='발행·지갑·오케스트레이션·온체인 KYC·통합관제를 하나로 연결합니다. 스테이블코인·예금토큰·RWA·토큰증권까지 단계적으로 확장합니다.',
    crumb='Solutions — 금융',
    body_class='hero-dark',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">View Demo</span></a>
      <a class="pill outline no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>''',
    content=f"""
<section><div class="shell sec">
  {eyebrow('Product')}
  {h2('이 솔루션을 구성하는 제품')}
  {chips(['ParaSta'])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Why Now')}
  {h2('디지털자산의 금융화는 이미 시작됐습니다 — 문제는 발행 이후입니다')}
  {lead_p('글로벌 대형 자산운용·결제사는 이미 RWA와 스테이블코인으로 진입했고, 국내에서도 토큰증권 제도화가 논의되고 있습니다. 핵심 문제는 토큰을 발행하는 것보다 유통·보유·상환 전 구간에서 발생하는 규제와 운영 리스크입니다. 투자자 적격성·자금세탁방지(KYC)를 계속 확인하고, 배당·이자·상환을 약속대로 집행하며, 자산이 여러 지갑으로 옮겨 다니는 과정을 실시간으로 통제·감사하는 일이 사업의 성패를 좌우합니다.')}
  {bar_chart([
    dict(l='2024년', v='34조원', w=9),
    dict(l='2025년', v='119조원', w=32),
    dict(l='2030년', v='367조원', w=100, hi=True),
  ], title='국내 토큰증권(STO) 시가총액 전망', note='전망치. 출처: 하나금융경영연구소·삼일PwC(BCG 기준 인용). 현행 자본시장법 기준 30~60조원 등 더 보수적 전망도 있어 ‘전망’으로 표기합니다.')}
  <div style="height:2.5rem"></div>
  {bar_chart([
    dict(l='2025년 1월', v='$2,050억', w=68),
    dict(l='2025년 말', v='$3,000억+', w=100, hi=True),
  ], title='글로벌 스테이블코인 발행잔액', note='출처: DeFiLlama 등 시장 집계(실적 집계). 2025년 약 49% 증가. 이미 온체인에서 대규모로 유통 중인 실측치입니다.')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Problem')}
  {h2('금융기관이 마주하는 문제')}
  {cards_wrap([
    dark_card('문제', '발행보다 어려운 운영', 'KYC, 상환, 유통 통제, 사후검증이 발행보다 어렵습니다.'),
    dark_card('문제', '계좌와 온체인의 분절', '은행 계좌와 온체인 지갑이 따로 놀아 정산이 복잡합니다.'),
    dark_card('문제', '규제 대응 부담', 'AML·트래블룰을 서비스마다 다시 설계해야 합니다.'),
    dark_card('문제', '범용 SaaS의 한계', '글로벌 지갑 SaaS는 국내 규제·운영 설계를 대신하지 않습니다.'),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Features')}
  {h2('주요 기능')}
  {lead_p('발행부터 상환·사후검증까지 6-Layer 통제 구조로 연결합니다.')}
  {cards_wrap([
    dark_card('01', 'Issuance 발행', '규제 준수형 발행·상환·유통통제.'),
    dark_card('02', 'Wallet 지갑', '신원 기반 자산 통제, 멀티체인 단일 인터페이스.'),
    dark_card('03', 'Orchestration 관제', '계좌↔온체인 통합, 조건부 정산, 실시간 스크리닝.'),
    dark_card('04', 'On-chain KYC', '공인 KYC를 VC/VP로 변환, 멀티체인 신원 허브.'),
    dark_card('05', 'Unified Admin', '통합 관제탑, 키 거버넌스, 통합 감사 리포팅.'),
    dark_card('RWA · STO', 'ParaSta 연동', '토큰증권·실물자산 발행 이후 운영까지 API로 연결.'),
  ], cols=3)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('How to Adopt')}
  {h2('이렇게 도입합니다')}
  {lead_p('한 번에 구축하지 않고 단계로 나눕니다.')}
  {cards_wrap([
    dark_card('4주', 'PoC', '개념 검증'),
    dark_card('12주', 'Pilot', '파일럿 운영'),
    dark_card('4~6개월', '상용', '상용 전환'),
  ], cols=3)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('By the Numbers')}
  {h2('숫자로 보는 ParaSta')}
  {nums([
    dict(cap='Modules', n='4개 모듈', sub='발행·지갑·오케스트레이션·온체인 KYC (+ 통합 관제탑)'),
    dict(cap='Control', n='6-Layer', sub='발행·상환·통제 구조'),
    dict(cap='Package', n='4주 · 12주', sub='PoC · Pilot 패키지'),
    dict(cap='Throughput', n='최대 100,000', sub='TPS (벤치마크·제한 환경)'),
  ])}
  {note('파라메타 트랙레코드(회사 배경) · 금융위 혁신금융서비스 지정 · 기술보증기금 TI-1 · CSAP · ChainID 증권사 공동인증. ParaSta 자체 실적이 아닌 회사 트랙레코드로 표기합니다.')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Use Cases')}
  {h2('적용 사례')}
  {cards_wrap([
    dark_card('참여', 'NH투자증권 — STO 비전그룹', '<b>과제</b> · 토큰증권을 발행 이후 운영·관리까지 고려한 인프라가 필요<br><br><b>해결</b> · 토큰증권 발행·운영 논의에 기술 파트너로 참여', sm=False),
    dark_card('MOU', '쿠콘 · 인피닛블록', '<b>과제</b> · 스테이블코인 발행·정산·결제를 API로 연계할 허브가 필요<br><br><b>해결</b> · 발행·정산·결제·API 연계 협력 MOU 체결', sm=False),
    dark_card('발표', 'ADB ABMF — 온체인 KYC 발표', '<b>과제</b> · 국경 간 투자에서 지갑·사용자 신원의 적격성 확인이 필요<br><br><b>해결</b> · 지갑 인증·온체인 KYC·KYW 접근을 국제 협의체에서 발표', sm=False),
  ], cols=3)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('FAQ')}
  {h2('자주 묻는 질문')}
  {faq([
    dict(q='스테이블코인과 예금토큰은 무엇이 다른가요', a='둘 다 가치가 고정된 디지털 화폐지만 발행 주체와 담보 구조가 다릅니다. 제도·발행 요건은 국내 법제화 상황에 따라 달라집니다.'),
    dict(q='STO·RWA는 무엇인가요', a='실물·금융 자산을 토큰으로 발행해 거래·관리하는 방식입니다. 발행뿐 아니라 이후 운영·통제까지 인프라가 필요합니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Solutions')}
  {h2('다른 분야 솔루션')}
  {routes(SOL_ROUTES, 'solution-finance.html')}
</div></section>
""")

# ---------------- solution-gov.html ----------------
PAGES['solution-gov.html'] = dict(
    title='공공 블록체인 솔루션 | PARAMETA',
    desc='공공기관용 CSAP 인증 블록체인 SaaS. DID·지갑·개인데이터저장소(PDS)·분산저장(BFS)을 직접 구축 없이 구독형으로. 신청 4단계, 최대 1주일 내 적용.',
    eyebrow='Solutions — 공공',
    h1_lines=['공공기관용 CSAP 인증', '블록체인 SaaS'],
    lead='DID·지갑·개인데이터저장소(PDS)·분산저장(BFS) 기반 서비스를 직접 구축하지 않고 구독형으로 도입합니다. 신청 4단계, 최대 1주일 내 적용.',
    crumb='Solutions — 공공',
    body_class='hero-dark',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">View Demo</span></a>
      <a class="pill outline no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>''',
    content=f"""
<section><div class="shell sec">
  {eyebrow('Product')}
  {h2('이 솔루션을 구성하는 제품')}
  {chips(['KBTF (MyID 2.0)'])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Why Now')}
  {h2('공공 블록체인은 기관마다 새로 자체구축해야 했습니다')}
  {lead_p('공공기관이 SaaS형 서비스를 도입하려면 CSAP 같은 엄격한 보안인증을 통과한 제품이어야 합니다. 그런데 블록체인 분야에는 CSAP 인증을 받은 SaaS가 사실상 없어, 기관마다 예산 산정부터 자체 구축까지 최소 1년, 초기 구축비 수억원을 들여 직접 만들어야 했습니다. 그사이 정부의 블록체인 공공서비스 투자는 늘어 2024년 지원사업은 총 200억원·14개 규모로 확대됐고, 블록체인 활용 수요가 가장 큰 분야도 정부·공공입니다.')}
  {bar_chart([
    dict(l='정부/공공', v='47.9%', w=80, hi=True),
    dict(l='출판·방송통신', v='36.5%', w=61),
    dict(l='은행·보험·증권', v='24.0%', w=40),
    dict(l='전문·과학·기술', v='20.8%', w=35),
    dict(l='교통·물류·운수', v='14.6%', w=24),
  ], title='블록체인 활용 분야 (공급기업 기준, 복수응답)', note='출처: KISA 2024년도 블록체인 산업 실태조사 결과보고서(국가승인통계 제127017호), 복수응답. 정부 지원사업 규모는 과기정통부·KISA 2024.')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Problem')}
  {h2('공공기관이 반복해서 겪는 문제')}
  {cards_wrap([
    dark_card('문제', '중복 인프라 투자', '기관마다 같은 블록체인·DID를 따로 구축·유지보수합니다.'),
    dark_card('문제', '분절된 앱 경험', '기관·서비스마다 앱과 인증이 흩어져 사용자 경험이 끊깁니다.'),
    dark_card('문제', '개인정보 보관 부담', '신원 데이터를 직접 보관하며 반복 인증 부담을 안습니다.'),
    dark_card('문제', '조달·보안인증 문턱', 'CSAP 없는 서비스는 공공 조달 검토를 통과하기 어렵습니다.'),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Features')}
  {h2('직접 구축 없이 도입합니다')}
  {cards_wrap([
    dark_card('01', '직접 구축 없이 도입', '예산·기간·보안·운영 부담 없이 구독형으로 시작합니다.'),
    dark_card('02', '블록체인 서비스 최초 CSAP', '클라우드 보안인증을 획득하고 조달에 등록돼 있습니다.'),
    dark_card('03', '최대 1주일 내 적용', '신청 4단계를 거쳐 최대 일주일 안에 서비스를 적용합니다.'),
    dark_card('04', '반복 구축 축소', '기관마다 흩어진 앱·인프라를 공통 인프라로 통합합니다.'),
  ], cols=2)}
  <div class="rvl" style="margin-top:2rem">
    <div style="font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); margin-bottom:1rem">기본 제공 기능</div>
    {chips(['신원 DID / VC / VP', '지갑', '개인데이터저장소 PDS', '분산저장 BFS'])}
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('How to Adopt')}
  {h2('같은 서비스를 여는 데 걸리는 시간')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('최소 1년+', '기존 개별 구축', '예산 산정 → 업체 선정 → 견적 → 계약 → 구축', sm=False)}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('1주일', 'MyID 2.0 공동인프라', '가입 승인 → 결제수단 등록 → 회원가입·설정', sm=False)}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('By the Numbers')}
  {h2('숫자로 보는 MyID 2.0')}
  {nums([
    dict(cap='Security', n='최초', sub='블록체인 서비스 CSAP 인증'),
    dict(cap='Cost', n='90%↓', sub='자체 구축 대비 비용 절감(모델)'),
    dict(cap='Included', n='20,000건', sub='월 포함 건수'),
    dict(cap='Speed', n='1주일', sub='도입 소요'),
  ], cols=2)}
  {note('구축형 대비 절감률은 단순 산식(모델) 기준입니다.')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Use Cases')}
  {h2('적용 사례')}
  {cards_wrap([
    dark_card('시범·적용', '부산시 — 배터리 여권 플랫폼', '<b>과제</b> · 배터리 제조·운행·정비·사용후 데이터가 흩어져 있고, EU DPP 규정에 맞춰 신뢰할 수 있게 연결·검증해야 함<br><br><b>해결</b> · K-BTF 기반 DID·데이터 인프라로 각 단계 데이터를 연결하고 발급·검증 흐름을 표준화', sm=False),
    dark_card('시범·적용', 'KOMSA — 선박검사 전자증서 검증', '<b>과제</b> · 선박검사 전자증서는 연 약 56만 회 반복 검증되는 고빈도 공적 문서로 검증 처리 부담이 큼<br><br><b>해결</b> · K-BTF SaaS에 MyID 2.0의 DID/VC 발급·검증과 PDS를 결합해 검증체계 구축(연 약 51,066시간 절감 목표)', sm=False),
    dark_card('운영 · 행안부 수상', '경상북도 — 도민증 모이소', '<b>과제</b> · 도민 대상 행정서비스에서 반복 신원확인과 비대면 신청 처리가 필요<br><br><b>해결</b> · DID 기반 도민증으로 발급·인증을 제공', sm=False),
    dark_card('역대 최대 규모', '제주도 — 제주안심코드', '<b>과제</b> · 대규모 방문 인증을 빠르게 처리하면서 개인정보 노출을 줄여야 함<br><br><b>해결</b> · QR 기반 인증으로 6만 업장·218만 이용자·누적 9,100만 건 인증을 운영', sm=False),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('FAQ')}
  {h2('자주 묻는 질문')}
  {faq([
    dict(q='CSAP 인증은 무엇이고 왜 중요한가요', a='클라우드 서비스의 보안을 평가하는 국내 인증입니다. 공공기관이 민간 SaaS를 도입할 때 요구되는 기준이라, 인증이 없으면 조달 검토를 통과하기 어렵습니다.'),
    dict(q='구축형과 공공 SaaS는 무엇이 다른가요', a='구축형은 기관이 인프라를 직접 만들어 소유·운영합니다. 공공 SaaS는 이미 만들어진 인프라를 구독형으로 이용해 별도 구축 없이 시작합니다.'),
    dict(q='공공 서비스에 DID가 왜 필요한가요', a='반복 신원확인과 개인정보 보관 부담을 줄입니다. 사용자는 필요한 정보만 선택해 제출하고, 기관은 데이터를 직접 쌓지 않습니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Solutions')}
  {h2('다른 분야 솔루션')}
  {routes(SOL_ROUTES, 'solution-gov.html')}
</div></section>
""")

# ---------------- solution-cert.html ----------------
PAGES['solution-cert.html'] = dict(
    title='디지털 증명 솔루션 | PARAMETA',
    desc='발급부터 공유, 제출처 검증까지 끝나는 블록체인 디지털 증명 인프라. 위촉장·수료증·MOU·디지털 배지를 발급·공유·검증합니다.',
    eyebrow='Solutions — 증명서',
    h1_lines=['발급부터 공유, 제출처', '검증까지 끝나는', '디지털 증명 인프라'],
    lead='위촉장·수료증·MOU·디지털 배지 등 다양한 증명을 발급·공유·검증할 수 있는 블록체인 기반 디지털 증명 서비스입니다.',
    crumb='Solutions — 증명서',
    body_class='hero-dark',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">View Demo</span></a>
      <a class="pill outline no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>''',
    content=f"""
<section><div class="shell sec">
  {eyebrow('Product')}
  {h2('이 솔루션을 구성하는 제품')}
  {chips(['Broof'])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Why Now')}
  {h2('증명서는 발급보다 발급 이후가 더 부담입니다')}
  {lead_p('PDF나 이미지 증명서는 제출처가 원본 여부를 확인하기 어렵고, 발급기관은 발급 이후에도 검증 문의·재발급·서버·보안 운영을 계속 안습니다. 증명 하나를 위해 검증 시스템을 따로 만들어 유지하는 구조입니다.')}
  {bar_chart([
    dict(l='종이 증서', v='약 5,000원', w=100),
    dict(l='Broof 디지털', v='1,100원', w=22, hi=True),
  ], title='증명서 건당 비용 비교 (당사 추산 · 모델)', note='당사 추산 예시(모델). 종이 증서 1건당 발급·우편·재발급·검증 인건비를 합산한 보수적 가정. 연 10,000건 가정 시 종이 약 5,000만원 → Broof 약 1,100만원.')}
  <div style="height:2rem"></div>
  {nums([
    dict(cap='발급 가능', n='481종', sub='전자증명서 발급 가능 (’26.5)'),
    dict(cap='정부24', n='2천만', sub='정부24 회원'),
    dict(cap='연계', n='59개', sub='연계 공공·민간 앱'),
  ])}
  {note('출처: 행정안전부 정부 전자문서지갑(dpaper.kr, ’26.5). 증명서 디지털화가 이미 광범위하게 자리 잡았습니다. Broof는 위촉장·배지 등 기관 자체 증명 영역을 다룹니다.')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Problem')}
  {h2('발급기관이 반복해서 겪는 문제')}
  {cards_wrap([
    dark_card('문제', '발급 이후 운영 지속', '검증 문의·재발급·서버·보안 운영이 발급 후에도 계속됩니다.'),
    dark_card('문제', '위변조 확인 어려움', 'PDF·이미지 증명서는 제출처가 원본 여부를 확인하기 어렵습니다.'),
    dark_card('문제', '검증 시스템 구축 부담', '증명마다 검증 시스템을 따로 만들어 유지해야 합니다.'),
    dark_card('문제', '종이 발급·배부 비용', '인쇄·배부·인건비가 건마다 쌓입니다.'),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Features')}
  {h2('주요 기능')}
  {chips(['위촉장', '수료증', 'MOU', '디지털 배지'])}
  <div style="height:1.5rem"></div>
  {rows([
    dict(title='발급–열람–공유–검증을 하나의 서비스로', desc='증명 발급부터 제출·검증까지 한 흐름으로 제공합니다.'),
    dict(title='QR·bf-ID로 즉시 진위 확인', desc='제출처가 원본 진위를 바로 확인합니다.'),
    dict(title='별도 검증 시스템 없이 장기 검증', desc='기관이 검증 시스템을 따로 구축·운영하지 않아도 됩니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('By the Numbers')}
  {h2('숫자로 보는 Broof')}
  {nums([
    dict(cap='Since', n='2019년~', sub='운영 중인 블록체인 증명 서비스'),
    dict(cap='Issued', n='90,000건+', sub='누적 블록체인 증명 발급'),
    dict(cap='Adopted', n='20곳+', sub='누적 도입 기관'),
    dict(cap='First', n='정부 위원회 첫', sub='블록체인 위촉장 사례'),
  ])}
  {note('누적 발급·도입 기관 수는 Broof 제품 기준. 종이 대비 절감률은 단순 산식(모델) 기준입니다.')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Use Cases')}
  {h2('적용 사례')}
  {cards_wrap([
    dark_card('정부 위원회 첫', '국가AI전략위원회 — 위촉증', '<b>과제</b> · 위원 위촉을 종이 없이 신뢰할 수 있는 형태로 발급·검증해야 함<br><br><b>해결</b> · 180여명에게 블록체인 기반 위촉증을 발급', sm=False),
    dark_card('운영', '대학·연구기관 — 수료증·학습 증명', '<b>과제</b> · 수료·이수 증명을 제출처가 진위 확인할 수 있어야 함<br><br><b>해결</b> · QR·bf-ID 기반 발급·검증으로 원본 무결성을 제공', sm=False),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('FAQ')}
  {h2('자주 묻는 질문')}
  {faq([
    dict(q='QR·bf-ID 검증은 어떻게 동작하나요', a='발급된 증명에 연결된 QR 또는 bf-ID로 제출처가 원본 여부를 즉시 확인합니다. 발급기관에 따로 문의하지 않아도 됩니다.'),
    dict(q='발급기관은 검증 시스템을 따로 만들어야 하나요', a='아니요. Broof가 발급·공유·검증 흐름을 제공하므로 기관이 별도 검증 시스템을 구축·운영하지 않습니다.'),
    dict(q='어떤 증명을 발급할 수 있나요', a='위촉장, 수료증, MOU, 디지털 배지 등 다양한 증명을 발급할 수 있습니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Solutions')}
  {h2('다른 분야 솔루션')}
  {routes(SOL_ROUTES, 'solution-cert.html')}
</div></section>
""")

# ---------------- solution-exchange.html ----------------
PAGES['solution-exchange.html'] = dict(
    title='화이트라벨 거래소 솔루션 | PARAMETA',
    desc='직접 거래소를 만들지 않아도 우리 서비스 안에 거래 기능을 넣습니다. 외부 거래소 유동성과 거래 화면을 브랜드 안으로 가져오는 화이트라벨 하이브리드 거래소 솔루션.',
    eyebrow='Solutions — 화이트라벨 거래소',
    h1_lines=['거래소를 만들지 않아도,', '서비스 안에 거래 기능을 넣습니다'],
    lead='PortX는 여러 거래소의 유동성과 거래 화면을 우리 서비스 안으로 그대로 가져오는 솔루션입니다. 매칭엔진·유동성·지갑·보안을 직접 만들지 않아도, 우리 브랜드를 단 디지털자산 거래 서비스를 빠르게 시작할 수 있습니다.',
    crumb='Solutions — 화이트라벨 거래소',
    body_class='hero-dark',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">View Demo</span></a>
      <a class="pill outline no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>''',
    content=f"""
<section><div class="shell sec">
  {eyebrow('Product')}
  {h2('이 솔루션을 구성하는 제품')}
  {chips(['PortX'])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Why Now')}
  {h2('사용자는 거래를 위해 외부 거래소로 빠져나갑니다')}
  {lead_p('국내 가상자산 이용자는 2023년 말 645만 명에서 2024년 말 970만 명으로 빠르게 늘었습니다. 이용자를 이미 확보한 서비스라도 자체 거래 기능이 없으면, 사용자는 거래를 하려고 외부 거래소로 빠져나갑니다. 그만큼 수수료와 사용자 관계를 외부에 내주게 됩니다. 그렇다고 직접 거래소를 만들자니 유동성·API·지갑·보안 부담이 큽니다.')}
  {bar_chart([
    dict(l='2023년 말', v='645만명', w=66),
    dict(l='2024년 6월', v='778만명', w=80),
    dict(l='2024년 말', v='970만명', w=100, hi=True),
  ], title='국내 가상자산 거래가능 이용자 수', note='출처: 금융정보분석원(FIU) 가상자산사업자 실태조사. 신고 사업자 기준 거래가능 이용자.')}
  <div style="height:2rem"></div>
  {nums([
    dict(cap='유출', n='약 20조원', sub='국내에서 해외로 빠져나간 가상자산 (’22 하반기)'),
    dict(cap='출금', n='30.6조원', sub='국내 거래소 총 외부 출금액 (같은 기간)'),
  ], cols=2)}
  {note('출처: 금융정보분석원(FIU) 가상자산사업자 실태조사(’22 하반기). 자금이 국내 서비스 밖으로 빠져나간다는 근거(실적).')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Problem')}
  {h2('사업자가 마주하는 문제')}
  {cards_wrap([
    dark_card('문제', '사용자 외부 이탈', '거래하려는 사용자가 외부 거래소로 빠져 수수료·관계를 잃습니다.'),
    dark_card('문제', '직접 구축 부담', '거래소를 만들려면 유동성·API·지갑·보안·리스크가 부담입니다.'),
    dark_card('문제', '온보딩 마찰', 'API key 발급·입력 과정에서 사용자가 이탈합니다.'),
    dark_card('문제', '체인·거래소 파편화', '여러 체인·거래소를 각각 연동·유지해야 합니다.'),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Features')}
  {h2('주요 기능')}
  {cards_wrap([
    dark_card('01', '거래소 연동', '외부 CEX/DEX 유동성을 고객 서비스로 연결합니다.'),
    dark_card('02', 'Smart Access · QR', 'API key 입력 없이 QR 한 번으로 거래소를 연결합니다.'),
    dark_card('03', '전문 거래 화면·성과 분석', '전문 거래 UX와 PnL·성과 분석을 제공합니다.'),
    dark_card('04', '비수탁 보안 · BTP', '비수탁 흐름과 체인 간 연결(BTP)로 확장합니다.'),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('By the Numbers')}
  {h2('숫자로 보는 PortX')}
  {nums([
    dict(cap='Exchanges', n='9개 거래소', sub='연동 노출 가능'),
    dict(cap='Access', n='QR 1회', sub='API key 없이 수 초 연결'),
    dict(cap='Speed', n='78~94%', sub='직접 연동 대비 기간 단축(모델)'),
    dict(cap='Security', n='비수탁', sub='자산 보관 최소화 구조'),
  ])}
  {note('78~94%는 9개 거래소 직접 연동 대비 기간 단축 모델. BTP(인터체인)는 상호운용 기반 기술입니다.')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Use Cases')}
  {h2('적용 사례')}
  {cards_wrap([
    dark_card('적용', 'Supercycl — Pre-OBT', '<b>과제</b> · 자사 서비스 안에서 거래 경험을 빠르게 검증해야 함<br><br><b>해결</b> · PortX 기반 거래 연동으로 Pre-OBT 조기 사용자 확보', sm=False),
    dark_card('적용', 'TaaS — 디지털자산 세금정산', '<b>과제</b> · 여러 거래소에 흩어진 거래 내역을 모아 예상 세금을 계산해야 함<br><br><b>해결</b> · PortX Smart Access로 외부 거래소 계정 연결을 간소화해, 세금 계산에 필요한 거래 정보를 서비스 안에서 바로 활용', sm=False),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('FAQ')}
  {h2('자주 묻는 질문')}
  {faq([
    dict(q='화이트라벨 하이브리드 거래소가 무엇인가요', a='거래소를 직접 만들지 않고, 외부 거래소의 유동성과 거래 화면을 고객 브랜드 안에 붙이는 방식입니다.'),
    dict(q='직접 거래소를 만드는 것과 무엇이 다른가요', a='유동성·API·지갑·보안을 반복 개발하지 않고, 표준 거래 인프라로 빠르게 시작합니다.'),
    dict(q='BTP는 무엇인가요', a='서로 다른 블록체인 사이의 메시지·자산 이동을 지원하는 인터체인 기술입니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Solutions')}
  {h2('다른 분야 솔루션')}
  {routes(SOL_ROUTES, 'solution-exchange.html')}
</div></section>
""")

# ---------------- solution-data.html ----------------
PAGES['solution-data.html'] = dict(
    title='데이터주권 솔루션 | PARAMETA',
    desc='개인정보를 직접 쌓지 않고 사용자가 통제하게 만드는 데이터 인프라. PDS·BFS·선택적 공개로 서비스가 개인정보를 떠안지 않게 하는 DID 기반 신원·데이터 솔루션.',
    eyebrow='Solutions — 데이터주권',
    h1_lines=['개인정보를 직접 쌓지 않고,', '사용자가 통제하게 만드는', '데이터 인프라'],
    lead='개인정보를 다루는 서비스일수록 수집·보관·동의 관리·유출 대응 부담이 큽니다. MyID는 사용자가 자기 데이터를 직접 통제해 필요한 곳에 필요한 만큼만 제출하도록 설계된 DID 기반 신원·데이터 인프라입니다. PDS·BFS·선택적 공개로 서비스가 개인정보를 떠안지 않게 합니다.',
    crumb='Solutions — 데이터주권',
    body_class='hero-dark',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">View Demo</span></a>
      <a class="pill outline no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>''',
    content=f"""
<section><div class="shell sec">
  {eyebrow('Product')}
  {h2('이 솔루션을 구성하는 제품')}
  {chips(['MyID'])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Why Now')}
  {h2('데이터는 사용자 중심으로 움직이기 시작했습니다')}
  {lead_p("마이데이터에서 시작된 ‘사용자가 자기 데이터를 옮기고 통제하는’ 흐름이 의료·통신 등 전 분야로 퍼지고 있습니다. 동시에 개인정보를 많이 쌓아둘수록 유출·규제·동의 관리 부담이 커집니다. 데이터를 떠안는 대신 사용자가 통제하게 하는 구조가 점점 유리해지고 있습니다.")}
  {nums([
    dict(cap='이용', n='약 1.65억', sub='마이데이터 서비스 이용 (’25.5)'),
    dict(cap='1인당', n='3.5개', sub='14세 이상 국민 1인당 이용 서비스 수'),
    dict(cap='전송', n='1조 1,430억 건', sub='마이데이터 누적 정보 전송 (’25.5)'),
    dict(cap='시장', n='30.7조원', sub='국내 데이터산업 시장 (2024)'),
  ])}
  {note('출처: 금융위원회 보도자료(’25.6, 마이데이터 2.0)·K-DATA 2024 데이터산업 현황조사(실적). 데이터가 실제로 대량 이동하고 있어 안전한 보관·검증 수요가 함께 커집니다.')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Problem')}
  {h2('개인정보를 다루는 서비스가 마주하는 문제')}
  {cards_wrap([
    dark_card('문제', '보관 리스크', '개인정보를 직접 쌓아둘수록 유출 사고와 과징금·신뢰 하락 부담이 커집니다.'),
    dark_card('문제', '반복 수집·동의 관리', '서비스마다 같은 정보를 다시 받고 동의를 관리하는 비용이 쌓입니다.'),
    dark_card('문제', '사용자 통제 요구', '전송요구권 등 사용자가 자기 데이터를 옮기고 지우라는 요구에 대응해야 합니다.'),
    dark_card('문제', '위·변조 검증', '받은 데이터가 진짜인지, 바뀌지 않았는지 확인해야 합니다.'),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Features')}
  {h2('주요 기능')}
  {cards_wrap([
    dark_card('PDS', '개인데이터저장소', '데이터를 사용자 통제 아래 두고, 기관 보관 부담을 줄입니다.'),
    dark_card('BFS', '분산 저장', '대용량 데이터를 분산 저장해 무결성과 가용성을 확보합니다.'),
    dark_card('ZK', '선택 공개 (Selective Disclosure)', '생년월일 대신 성인 여부만처럼, 필요한 사실만 증명하고 나머지는 감춥니다.'),
    dark_card('API', 'MyID 지갑·API', '별도 인증 앱 없이 API 연결만으로 서비스 안에서 신원·데이터를 발급·보관·제출·검증합니다.'),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('By the Numbers')}
  {h2('숫자로 보는 Core Storage')}
  {nums([
    dict(cap='R&D', n='2021~2025', sub='국책 R&D 기반 BFS (IITP·ETRI 공동)'),
    dict(cap='Users', n='218만 명', sub='제주안심코드 누적 이용자'),
    dict(cap='Auth', n='9,100만 건', sub='제주안심코드 누적 인증'),
    dict(cap='Integrity', n='위변조 불가', sub='해시는 온체인, 원본은 분산 노드'),
  ])}
  {note('BFS 기반 기술은 IITP 국책 R&D 과제(2021-0-00136, ETRI 공동)로 개발됐고, 제주 스마트시티에서 교통·어류질병·드론 해양환경 모니터링으로 실증됐습니다(R&D 실증).')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Use Cases')}
  {h2('적용 사례')}
  {cards_wrap([
    dark_card('공개 · DID·VC·PDS', '부산시 배터리여권 플랫폼 (DPP)', '<b>과제</b> · 전기차 배터리의 제조·운행·정비·중고거래·재활용 데이터가 흩어져 있고, EU 배터리 규제(DPP)에 맞춰 출처·이력·무결성을 증명해야 함<br><br><b>해결</b> · DID·VC·PDS를 결합해 참여자 신원과 데이터 주권을 보장하는 데이터 스페이스로 배터리 생애 데이터를 기록·관리(MyID 2.0이 최초 적용된 공공 인프라 사례)', sm=False),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('FAQ')}
  {h2('자주 묻는 질문')}
  {faq([
    dict(q='PDS는 무엇인가요', a='개인데이터저장소로, 데이터를 기관이 아니라 사용자 통제 아래 두는 저장 방식입니다.'),
    dict(q='BFS는 무엇인가요', a='데이터를 여러 곳에 분산 저장해 무결성과 가용성을 확보하는 분산저장 기술입니다.'),
    dict(q='데이터 무결성은 어떻게 보장하나요', a='파일 원본은 분산 노드에, 해시는 블록체인에 남깁니다. 하나라도 바뀌면 즉시 드러나는 구조입니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Solutions')}
  {h2('다른 분야 솔루션')}
  {routes(SOL_ROUTES, 'solution-data.html')}
</div></section>
""")

# ---------------- solution-settlement.html ----------------
PAGES['solution-settlement.html'] = dict(
    title='결제·정산 솔루션 | PARAMETA',
    desc='결제·정산을 자동화하고 자금 흐름을 통제합니다. 은행망과 블록체인을 잇는 미들웨어 ParaSta. Dual-Rail 도입, 폐쇄형 정산토큰에서 스테이블코인으로 2단계 전환.',
    eyebrow='Solutions — 결제·정산',
    h1_lines=['결제·정산을 자동화하고,', '자금 흐름을 통제합니다'],
    lead='ParaSta는 은행망과 블록체인을 잇는 미들웨어로, 환전·송금·정산의 여러 단계를 단일 API로 처리합니다. 기존 결제 레일은 그대로 두고 정산·대사·통제 레이어만 얹어(Dual-Rail), 규제 부담이 적은 폐쇄형 정산토큰으로 시작해 필요할 때 스테이블코인으로 확장합니다.',
    crumb='Solutions — 결제·정산',
    body_class='hero-dark',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">View Demo</span></a>
      <a class="pill outline no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>''',
    content=f"""
<section><div class="shell sec">
  {eyebrow('Product')}
  {h2('이 솔루션을 구성하는 제품')}
  {chips(['ParaSta'])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Why Now')}
  {h2('정산은 이미 디지털로 움직입니다 — 다음은 투명성과 통제입니다')}
  {lead_p('국내 디지털 정산은 이미 하루 약 1조 원 규모로 움직입니다(간편지급 기준). 규모가 커질수록 어려운 건 발행이 아니라 정산의 투명성, 자동 대사, 오류·부정 통제입니다. 지역사랑상품권(2024년 17.6조 원)처럼 공공·민간의 대규모 정산도 같은 과제를 안고 있습니다.')}
  {nums([
    dict(cap='간편지급', n='약 9,594억원', sub='간편지급 일평균 이용액 (2024)'),
    dict(cap='간편송금', n='약 9,120억원', sub='간편송금 일평균 이용액 (2024)'),
  ], cols=2)}
  {note('출처: 한국은행 「2024년중 전자지급서비스 이용현황」(2025.3). 이미 하루 약 1조 원 규모로 디지털 정산이 이뤄집니다(실적).')}
  <div style="height:2rem"></div>
  {bar_chart([
    dict(l='카드형', v='12.0조원', w=100, hi=True),
    dict(l='모바일', v='4.3조원', w=36),
    dict(l='지류', v='1.3조원', w=11),
  ], title='적용 영역 예시 — 지역사랑상품권 발행액 (2024년)', note='출처: 국회예산정책처(2025) 지역사랑상품권 발행·관리체계 평가. 2024년 총 발행 17.6조 원. 지역화폐는 이 정산 인프라가 적용되는 여러 영역 중 하나입니다.')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Problem')}
  {h2('결제·정산에서 반복되는 문제')}
  {cards_wrap([
    dark_card('문제', '정산 데이터 불일치', '거래 원장과 결제사 데이터가 어긋나 수작업 대사가 필요합니다.'),
    dark_card('문제', '환불·취소 재정산', '환불·취소·차지백이 생기면 정산을 다시 맞춰야 합니다.'),
    dark_card('문제', '다자 분배·정산', '여러 파트너가 얽힌 분배·정산은 대사와 통제가 복잡합니다.'),
    dark_card('문제', '권한·감사 부담', '누가 무엇을 언제 바꿨는지 추적하고 감사에 대응해야 합니다.'),
  ], cols=2)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Features')}
  {h2('주요 기능')}
  {cards_wrap([
    dark_card('01', '환전·송금·정산 자동화', '은행망과 블록체인을 잇는 단일 API로 환전·송금·정산 다단계를 자동 처리합니다.'),
    dark_card('02', '이벤트 기반 정산·자동 대사', '승인·취소·환불을 실시간 반영하고, 수수료·정산 내역을 자동으로 맞춥니다.'),
    dark_card('03', 'Dual-Rail 도입', '기존 결제 레일은 그대로 두고 정산·통제 레이어만 얹어 도입 부담을 낮춥니다.'),
    dark_card('04', '2단계 전환', '규제 변수가 적은 폐쇄형 정산토큰으로 시작해, 필요할 때 스테이블코인으로 확장합니다.'),
    dark_card('05', '온체인 KYC · 통합 관제', '지갑·사용자 적격성 확인과 자금 흐름 모니터링·감사 리포팅을 함께 제공합니다.'),
  ], cols=3)}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('By the Numbers')}
  {h2('숫자로 보는 정산 인프라')}
  {nums([
    dict(cap='Modules', n='4개 모듈', sub='ParaSta 코어 + 통합 관제탑'),
    dict(cap='Transition', n='2단계', sub='폐쇄형 정산토큰 → 스테이블코인'),
    dict(cap='KYC', n='온체인 KYC', sub='지갑·사용자 적격성'),
    dict(cap='Throughput', n='최대 100,000', sub='TPS (벤치마크·제한 환경)'),
  ])}
  {note('예금토큰·스테이블코인 제도는 법제화 상황에 따라 달라집니다.')}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Use Cases')}
  {h2('적용 사례')}
  {cards_wrap([
    dark_card('MOU', '쿠콘 · 인피닛블록', '<b>과제</b> · 발행·정산·결제를 API로 연계할 허브가 필요<br><br><b>해결</b> · 발행·정산·결제·API 연계 협력 MOU 체결', sm=False),
  ], cols=2)}
  <div class="rvl" style="margin-top:2rem">
    <div style="font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); margin-bottom:1rem">적용 영역 (유형)</div>
    {chips(['가맹점 결제 정산', '커머스 에스크로 정산', '크로스보더 송금·정산', '지역화폐·지역상품권'])}
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('FAQ')}
  {h2('자주 묻는 질문')}
  {faq([
    dict(q='정산토큰과 스테이블코인은 무엇이 다른가요', a='폐쇄형 정산토큰은 특정 폐쇄 환경의 정산 수단이고, 스테이블코인은 더 넓은 유통을 전제합니다. 같은 인프라에서 단계적으로 전환하는 설계가 가능합니다.'),
    dict(q='지역화폐에도 적용할 수 있나요', a='발행·정산·통제 구조를 지역화폐 정산에 적용하는 설계가 가능합니다. 실제 적용은 제도·발주 조건에 따릅니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Solutions')}
  {h2('다른 분야 솔루션')}
  {routes(SOL_ROUTES, 'solution-settlement.html')}
</div></section>
""")

# ---------------- assemble ----------------
SHELL = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>__TITLE__</title>
<meta name="description" content="__DESC__" />
<meta name="theme-color" content="#0E0C27" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<script src="assets/nav.js?v=14" defer></script>
<script src="assets/chatbot.js?v=3" defer></script>
<style>__CSS____EXTRA_CSS__</style>
</head>
<body class="__BODYCLASS__">
__HEADER__
<main id="main">
  <section class="phero">
    <div class="phero-wm">PARAMETA</div>
    <div class="shell phero-inner">
      <div class="phero-text">
        <div class="eyebrow dark rvl rvl-op"><span class="dot"></span>__EYEBROW__</div>
        <h1 class="phero-h1" data-line-stagger="120">__H1__</h1>
        <p class="phero-lead rvl" style="--rvl-delay:250ms">__LEAD__</p>
        __HERO_CTA__
      </div>
      <div class="phero-visual" aria-hidden="true"></div>
    </div>
    <div class="shell phero-status">
      <span>__CRUMB__</span>
      <span style="display:inline-flex; gap:.5rem">Scroll <span aria-hidden="true">↓</span></span>
    </div>
  </section>
__CONTENT__
</main>
__FOOTER__
__JS__
</body>
</html>
"""

for fname, p in PAGES.items():
    h1 = ''.join(f'<span class="rvl-line"><span>{l}</span></span>' for l in p['h1_lines'])
    out = (SHELL
        .replace('__BODYCLASS__', p.get('body_class', ''))
        .replace('__TITLE__', p['title'])
        .replace('__DESC__', p['desc'])
        .replace('__CSS__', CSS)
        .replace('__EXTRA_CSS__', EXTRA_CSS)
        .replace('__HEADER__', CHROME_HEADER)
        .replace('__EYEBROW__', p['eyebrow'])
        .replace('__H1__', h1)
        .replace('__LEAD__', p['lead'])
        .replace('__CRUMB__', p['crumb'])
        .replace('__HERO_CTA__', p.get('hero_cta', ''))
        .replace('__CONTENT__', p['content'])
        .replace('__FOOTER__', CHROME_FOOTER)
        .replace('__JS__', JS))
    with open(os.path.join(ROOT, fname), 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'wrote {fname} ({len(out)} bytes)')
print('done')
