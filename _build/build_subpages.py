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
#      · card(title, desc, kicker=, tags=, tone='dark'|'gray', media=True) + card_grid([...], cols)
#        : 카드 공통 토큰 (dark_card/cards_wrap은 하위호환 alias)
#      · faq([...])               : 롤모션 아코디언
#      · light-card / num-card    : 라이트 카드·숫자 카드 (직접 마크업)
#   2) 실행하면 test/에 HTML 생성. GNB/푸터에 링크 추가는 이 파일에서.
#
# 규칙: 색·폰트는 :root 토큰만 사용(--text-*, --ink 등), 폰트 짝수·최소14,
#       사이즈는 4의 배수, 새 섹션은 캡슐화(주석 마커).
# ============================================================================

#!/usr/bin/env python3
# Build PARAMETA subpages from shared chrome + per-page content
import re, os, json, glob

ROOT = '/Users/sang/Desktop/Claude/test'
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')  # 보도자료 등 콘텐츠 데이터
main = open(os.path.join(ROOT, 'parameta.html'), encoding='utf-8').read()
CSS = re.search(r'<style>([\s\S]*?)</style>', main).group(1)

EXTRA_CSS = """
/* 서브페이지 전용: 641~1024 루트 유동화 — 640에서 14px → 1024에서 16px 선형 보간.
   rem 기반 토큰(폰트·간격·라운드)이 전부 비례 스케일. 메인(parameta.html)은 고정 16px 유지 */
@media (min-width:641px) and (max-width:1024px){ html{ font-size:calc(10.667px + 0.52083vw) } }
/* 태블릿(768~1023)에서만: 서브페이지 타입 토큰을 한 단계씩 아래 값으로 다운시프트(예: 14→12값, 36→32값). 기존 토큰 그리드 그대로. 여백 토큰·메인·타 해상도 무관 */
@media (min-width:768px) and (max-width:1023px){ :root{
  --text-14:0.75rem; --text-16:0.875rem; --text-18:1rem; --text-20:1.125rem;
  --text-22:1.25rem; --text-24:1.375rem; --text-26:1.5rem; --text-28:1.625rem;
  --text-30:1.75rem; --text-32:1.875rem; --text-36:2rem; --text-40:2.25rem;
  --text-48:2.5rem; --text-56:3rem; --text-60:3.5rem; --text-72:3.75rem;
  --text-76:4.5rem; --text-80:4.75rem; --text-96:5rem;
  --space-12:.5rem; --space-16:.75rem; --space-20:1rem; --space-24:1.25rem; --space-32:1.5rem;
  --space-40:2rem; --space-48:2.5rem; --space-64:3rem; --space-80:4rem;
  --space-120:5rem; --space-144:7.5rem; --space-160:9rem;   /* 스페이싱 전체 한 단계 다운 (8은 4배수 유지 위해 제외) */
} }
/* sm(≤767)에서도: 타입+스페이싱 토큰 한 단계 다운시프트(태블릿과 동일 문법). 메인 무관 */
@media (max-width:767px){ :root{
  --text-14:0.75rem; --text-16:0.875rem; --text-18:1rem; --text-20:1.125rem;
  --text-22:1.25rem; --text-24:1.375rem; --text-26:1.5rem; --text-28:1.625rem;
  --text-30:1.75rem; --text-32:1.875rem; --text-36:2rem; --text-40:2.25rem;
  --text-48:2.5rem; --text-56:3rem; --text-60:3.5rem; --text-72:3.75rem;
  --text-76:4.5rem; --text-80:4.75rem; --text-96:5rem;
  --space-12:.5rem; --space-16:.75rem; --space-20:1rem; --space-24:1.25rem; --space-32:1.5rem;
  --space-40:2rem; --space-48:2.5rem; --space-64:3rem; --space-80:4rem;
  --space-120:5rem; --space-144:7.5rem; --space-160:9rem;   /* 스페이싱 전체 한 단계 다운 (8은 4배수 유지 위해 제외) */
} }
/* 챗봇 전체(FAB+패널): 메인과 동일 렌더 보장.
   - 641~1023: 서브만 루트가 유동이라 px 고정(메인 루트 16px 환산값)
   - ≤640: 루트는 메인과 동일하므로 다운시프트된 텍스트 토큰만 원복(rem)
   - 1024+: 루트 규칙이 메인과 동일해 자동 일치 */
@media (min-width:641px) and (max-width:1023px){
  .fab-chat{ min-height:48px; min-width:48px; padding:0 20px; font-size:14px; right:24px; bottom:24px }
  .fab-ai{ width:16px; height:16px; margin-right:8px }
  .fab-chat .icn{ font-size:16px }
  .pc-panel{ width:416px }
  html.chat-open{ padding-right:416px }
  html.chat-open #header{ right:416px }
  html.chat-open #banner-fixed{ right:416px }
  .pc-head{ flex-basis:64px; padding:0 16px 0 24px; font-size:14px }
  .pc-head .pc-title{ gap:12px }
  .pc-head img{ height:16px }
  .pc-dot{ width:8px; height:8px }
  .pc-close{ width:36px; height:36px }
  .pc-msgs{ padding:20px; gap:12px }
  .pc-msg{ padding:12px 16px; font-size:14px; border-radius:14px }
  .pc-msg.bot{ border-top-left-radius:4px }
  .pc-msg.user{ border-bottom-right-radius:4px }
  .pc-msg.typing{ padding:14px 16px; gap:4px }
  .pc-msg.typing span{ width:6px; height:6px }
  .pc-chips{ gap:8px; margin-top:4px }
  .pc-chip{ padding:8px 14px; font-size:14px }
  .pc-input{ padding:16px 20px; gap:8px }
  .pc-input input{ padding:10px 18px; font-size:14px }
  .pc-send{ width:40px; height:40px }
  .pc-send .icn{ font-size:16px }
}
@media (max-width:640px){
  /* 다운시프트된 텍스트 토큰만 메인 값으로 원복 — 루트·일반 rem은 메인과 동일해 그대로 */
  .fab-chat{ font-size:.875rem }
  .fab-chat .icn{ font-size:1rem }
  .pc-head{ font-size:.875rem }
  .pc-msg{ font-size:.875rem }
  .pc-chip{ font-size:.875rem }
  .pc-input input{ font-size:.875rem }
  .pc-send .icn{ font-size:1rem }
}
/* ══ 시맨틱 토큰 — 새 작업은 무조건 이 층만 사용 (원시 토큰 직접 사용 지양) ══ */
:root{
  /* 폰트 사이즈 */
  --text-body:var(--text-18);          /* 본문 */
  --text-body-sm:var(--text-16);       /* 작은 본문(카드 서브) */
  --text-cap:var(--text-14);           /* 캡션·메타 서브 (최소) */
  /* 폰트 컬러 */
  --c-body:rgba(var(--ink-rgb),.6);    /* 본문 */
  --c-mut:rgba(var(--ink-rgb),.4);     /* 뮤트(라벨·연도·월) */
  /* 웨이트 */
  --w-title:500; --w-strong:600; --w-num:700;
  /* 라인하이트 (기존 leading 토큰 참조) */
  --lh-display:var(--leading-display,.98); --lh-heading:var(--leading-heading,1.25); --lh-body:var(--leading-body,1.6);
  /* 여백 */
  --pad-panel-y:var(--space-48); --pad-panel-x:clamp(1.5rem,4vw,3rem);   /* 그레이 패널 공통 */
  --gap-unit:var(--space-24);          /* 컴포넌트 내부 기준 간격 */
}
.body-t{ font-size:var(--text-body); line-height:var(--lh-body) }
/* 공통 서브타이틀(.sub-t): 섹션 내 소제목 — Alliance(.ally-num)와 동일 스타일.
   마크업: <span class="sub-t" data-line-reveal><span class="rvl-line"><span>텍스트</span></span></span> → 스크롤 인 시 줄 마스크 리빌 */
.sub-t{ display:block; font-size:var(--text-26); font-weight:700; color:var(--ink); line-height:var(--leading-heading) }   /* 서브타이틀 22→26, 행간 1.25 */
/* 공통 메타 라벨(.meta-t): 섹션 내 소소한 구분 라벨 (마퀴 라벨 등).
   ※ 기존 유사 스타일(rc-label 옛 정의 등)은 타 페이지 사용 중 — 전 페이지 이관 완료 후 제거 예정 */
.meta-t{ display:block; font-size:var(--text-16); font-weight:600; letter-spacing:.06em;
  color:var(--c-body); text-transform:uppercase }
/* 모바일 전용 줄바꿈: <br class="br-m"> — ≤639에서만 개행 */
.br-m{ display:none }
@media (max-width:639px){ .br-m{ display:inline } }
/* ============ SUBPAGE HERO ============ */
.phero{ position:relative; isolation:isolate; overflow:hidden; border-radius:0 0 var(--radius-card) var(--radius-card);
  background:linear-gradient(to bottom, var(--surface), var(--gray-200)) }
.phero-inner{ position:relative; z-index:10; display:flex; flex-direction:column; gap:1.75rem;
  padding:9rem 1.25rem 3.5rem }
.phero-h1{ max-width:22ch; font-size:var(--text-36); font-weight:600; line-height:var(--leading-display); letter-spacing:-.02em }
.phero-lead{ max-width:44rem; font-size:var(--text-16); line-height:var(--leading-body); color:rgba(var(--ink-rgb),.65) }
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
body.hero-dark .phero{ background:var(--ink); min-height:100vh }  /* 푸터와 동일한 잉크 토큰 */
body.hero-dark .phero-h1{ color:var(--white); max-width:18ch; font-size:var(--text-36); line-height:var(--leading-display); font-weight:500 }
@media (min-width:640px){ body.hero-dark .phero-h1{ font-size:var(--text-48) } }
@media (min-width:768px){ body.hero-dark .phero-h1{ font-size:var(--text-60) } }
@media (min-width:1024px){ body.hero-dark .phero-h1{ font-size:var(--text-72) } }
/* ---- 솔루션형 히어로 토큰: 타이틀 한 사이즈 다운 (36/48/60/72 → 32/40/48/60) ---- */
body.hero-dark.hero-sol .phero-h1{ font-size:var(--text-32); max-width:24ch }
@media (min-width:640px){ body.hero-dark.hero-sol .phero-h1{ font-size:var(--text-40) } }
@media (min-width:768px){ body.hero-dark.hero-sol .phero-h1{ font-size:var(--text-48) } }
@media (min-width:1024px){ body.hero-dark.hero-sol .phero-h1{ font-size:var(--text-60) } }
body.hero-dark.hero-sol .phero-h1 .rvl-line + .rvl-line{ margin-top:.2em }  /* 문장형 다중 줄: 줄 블록 사이만 벌림 (행간 .98 유지) */
body.hero-dark .phero-text .phero-lead{ color:rgba(var(--white-rgb),.7); font-size:var(--text-20) }
/* 히어로 CTA: 폰트 text-16 (높이는 base .pill.no-arrow 토큰 min-height:3rem = with-arrow와 동일) */
.phero-cta .pill .hspring{ font-size:var(--text-16) }
/* 히어로 CTA 스왑(공통): 새 Talk to Sales(cta-talk)는 기본 숨김 → PortX만 노출, 기존(cta-legacy)은 PortX에서 숨김. 나머지 페이지는 부활 전까지 기존 유지 */
.phero-cta .cta-talk{ display:none }
body.portx .phero-cta .cta-talk, body.parasta .phero-cta .cta-talk, body.broof .phero-cta .cta-talk{ display:inline-block }
body.portx .phero-cta .cta-legacy, body.parasta .phero-cta .cta-legacy{ display:none }
/* 새 버튼 사이징을 메인 히어로 Let's Talk와 동일하게 */
.phero-cta .cta-talk .hspring{ gap:.875rem }
.phero-cta .cta-talk .pill-badge{ width:2.5rem; height:2.5rem; font-size:var(--text-18) }
/* light 버튼(View Demo) 호버: 텍스트 purple-500 */
.phero-cta .pill.light .hspring{ transition:color .25s ease, transform .3s cubic-bezier(.2,.8,.2,1) }
@media (hover:hover){ .phero-cta .pill.light:hover .hspring{ color:var(--purple-500) } }
body.hero-dark .phero-cta .pill.outline .hspring{ border-color:rgba(var(--white-rgb),.3); color:var(--white);
  transition:background .25s ease, color .25s ease, border-color .25s ease, transform .3s cubic-bezier(.2,.8,.2,1) }
body.hero-dark .phero-cta .pill.outline .pill-badge{ background:var(--white); color:var(--ink) }
/* outline 버튼 호버: 보라 채움 (uc-arrow와 동일 언어) */
@media (hover:hover){ body.hero-dark .phero-cta .pill.outline:hover .hspring{ background:var(--accent); border-color:transparent; color:var(--white) } }
/* 관련 제품 바로가기: 리드 아래 좌측, 디바이더 + 캡션 타이틀 + 제품 플래그 (아이브로우 없음) */
.phero-rel{ display:flex; flex-direction:column; align-items:flex-start; gap:.75rem;
  margin-top:var(--space-64);  /* 리드↔디바이더: 컬럼 gap 1rem + 64 = 5rem (기존 2rem의 2.5배) */
  border-top:1px solid var(--line); padding-top:1.25rem }
.phero-rel-t{ font-size:var(--text-18); font-weight:600; line-height:var(--leading-body); color:var(--accent) }
.phero-rel-flag{ display:inline-flex; align-items:center; border:1px solid var(--line); border-radius:var(--radius-pill);
  padding:.625rem 1.25rem; font-size:var(--text-18); font-weight:600; color:rgba(var(--ink-rgb),.7); text-decoration:none;
  transition:background .25s ease, color .25s ease, border-color .25s ease, transform .35s cubic-bezier(.2,.8,.2,1) }
body.hero-dark .phero-rel{ border-top-color:rgba(var(--white-rgb),.16) }
body.hero-dark .phero-rel-t{ color:var(--purple-300) }  /* 다크 배경 가독용 밝은 보라 (lang-item active와 동일 관례) */
body.hero-dark .phero-rel-flag{ border-color:rgba(var(--white-rgb),.3); color:var(--white) }
@media (hover:hover){
  .phero-rel-flag:hover{ transform:scale(1.04) }  /* hs-scale과 동일 스프링 */
  body.hero-dark .phero-rel-flag:hover{ background:var(--white); border-color:transparent; color:var(--ink) }
}
/* 첫 섹션 상단 여백 확장: 모바일 7.5rem / 데스크톱 10rem */
.sec.sec-top-lg{ padding-top:var(--space-120) }
@media (min-width:1024px){ .sec.sec-top-lg{ padding-top:var(--space-160) } }
/* 섹션 본문 다중 문단: 문단 사이 1rem (마지막 문단만 하단 3rem 유지) */
.sec-lead:has(+ .sec-lead){ margin-bottom:var(--space-16) }
/* 섹션 스태거: 아이브로우 → 타이틀 → 본문(문단 일괄) → 차트 좌/우 (히어로와 동일 .rvl 딜레이 체계) */
.sec-stagger .eyebrow{ --rvl-delay:0ms }
.sec-stagger .sec-h2 .rvl-line span{ transition-delay:120ms !important }  /* 라인리빌 JS 인라인(0ms) 상회용 */
.sec-stagger .sec-lead{ --rvl-delay:260ms }  /* 문단들은 한 덩어리로 동시 등장 */
.sec-stagger .colc-duo .colc:first-child{ --rvl-delay:420ms }
.sec-stagger .colc-duo .colc:last-child{ --rvl-delay:560ms }
/* 다크 히어로: eyebrow(+블릿)·크럼브/스크롤(+디바이더)·워터마크 제거 */
body.hero-dark .phero-inner .eyebrow.dark{ display:none }
body.hero-dark .phero-status{ display:none }
body.hero-dark .phero-wm{ display:none }
/* 100vh · 12칼럼 그리드 스냅: 텍스트 1~6칸 / 비주얼 7~12칸 */
body.hero-dark .phero-inner{ min-height:100vh; display:grid; grid-template-columns:repeat(12,1fr);
  align-items:center; column-gap:var(--grid-gap); padding-top:6rem; padding-bottom:3rem }
body.hero-dark .phero-text{ grid-column:1 / 6; align-self:center; gap:1rem }
body.hero-dark .phero-cta{ margin-top:var(--space-16) }  /* 리드↔버튼 간격 (8→16) */
body.hero-dark .phero-visual{ grid-column:7 / 13; display:block; align-self:stretch; min-height:56vh;
  width:calc(100% + (100% - 5 * var(--grid-gap)) / 12 + var(--grid-gap) / 2);
  margin-left:calc(-1 * ((100% - 5 * var(--grid-gap)) / 12 + var(--grid-gap) / 2));  /* 왼쪽으로 반칸만 확장 */
  position:relative; overflow:hidden;
  border-radius:var(--radius-card); border:1px solid rgba(var(--white-rgb),.12);
  background:radial-gradient(120% 90% at 70% 18%, rgba(var(--accent-rgb),.2), transparent 60%), rgba(var(--white-rgb),.03) }
/* 이미지가 들어간 비주얼: 아웃라인·그라 제거, 영역만 + cover */
body.hero-dark .phero-visual:has(img){ border:none; background:none }
body.hero-dark .phero-visual img{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block }
/* 투명 배경 목업류: 크롭 없이 통짜로 보여주기 */
body.hero-dark .phero-visual img.fit-contain{ object-fit:contain }
@media (max-width:1023px){
  body.hero-dark .phero, body.hero-dark .phero-inner{ min-height:auto }
  body.hero-dark .phero-inner{ grid-template-columns:1fr; padding-top:6.25rem; padding-bottom:3rem; row-gap:2rem }
  body.hero-dark .phero-text, body.hero-dark .phero-visual{ grid-column:auto }
  body.hero-dark .phero-visual{ min-height:40vh; width:auto; margin-left:0 } }  /* 모바일 포함 기본 (원래대로) */
/* 태블릿 전용(640~1023): 이미지 우측 걸침 크롭 + full-bleed. 모바일(≤639)은 위 기본 유지 */
@media (min-width:640px) and (max-width:1023px){
  body.hero-dark .phero-visual{ min-height:52vh; margin-inline:-2rem; margin-bottom:-3rem; border-top-left-radius:0; border-top-right-radius:0 }
  body.hero-dark .phero-visual img.fit-contain{ inset:auto; right:-20px; bottom:-50%; width:auto; height:156%; max-width:none; object-fit:contain } }
/* ---- 콘텐츠형 히어로(hero-center): 이미지 영역 없음 + 텍스트 중앙정렬 ---- */
body.hero-center .phero-inner{ grid-template-columns:1fr; place-items:center; text-align:center }
body.hero-center .phero-visual{ display:none }
body.hero-center .phero-text{ grid-column:1 / -1; align-items:center; max-width:44rem; margin:0 auto }
body.hero-center .phero-h1{ max-width:none }
body.hero-center .phero-text .phero-lead{ max-width:40rem }
body.hero-center .phero-cta{ justify-content:center }
/* ============ 라이트 히어로 공통(hero-light) — company·contact·insights 공유 ============ */
/* 화이트 배경 + orb 캔버스 + 중앙정렬 텍스트 + 여백/타이포 토큰 (A: 공통) */
body.hero-light .phero{ background:var(--white); position:relative; overflow:hidden }
/* orb 배경 캔버스: hero-light에서만 표시 (ev-matrix는 전면 제거) */
.ev-matrix{ display:none }
body:not(.hero-light) .orb-bg{ display:none }
body.hero-light .orb-bg{ position:absolute; inset:0; z-index:0; width:100%; height:100%; display:block; pointer-events:none }
body.hero-light .phero-inner{ position:relative; z-index:1; display:flex; flex-direction:column; align-items:center;
  text-align:center; gap:2.75rem; min-height:0; padding:13rem 2rem 6rem }
body.hero-light .phero-status{ display:none }   /* 크럼·Scroll·디바이더 제거 */
body.hero-light .phero-visual{ display:none }   /* 이미지 영역 제거 */
body.hero-light .phero-text{ align-items:center; align-self:center; max-width:44rem; margin:0 auto; gap:.75rem }
/* h1 한 토큰 크게 */
body.hero-light .phero-h1{ font-size:var(--text-40) }
@media (min-width:640px){ body.hero-light .phero-h1{ font-size:var(--text-60) } }
@media (min-width:640px) and (max-width:767px){ body.hero-light .phero-h1{ font-size:var(--text-56) } }
@media (min-width:768px){ body.hero-light .phero-h1{ font-size:var(--text-72) } }
/* 리드 본문 사이즈 (16 → 18, 데스크톱 20) */
body.hero-light .phero-text .phero-lead{ font-size:var(--text-18) }
@media (min-width:768px){ body.hero-light .phero-text .phero-lead{ font-size:var(--text-20) } }

/* 히어로 플로팅 이미지 — 히어로 하단 중앙, 아래 박스가 하단 절반을 덮음 (페이지별 hero_figure) */
body:not(.hero-light) .phero-figure{ display:none }
/* bottom:0(=다크 카드 상단) + translateY(44%) → 반 걸침에서 살짝 위로 */
body.hero-light .phero-figure{ position:absolute; left:50%; bottom:0; transform:translate(-50%, 44%);
  width:clamp(22rem, 38vw, 40rem); z-index:1; pointer-events:none; display:block }
@media (min-width:768px) and (max-width:1024px){
  body.hero-light .phero-figure{ width:clamp(26rem, 42vw, 40rem) }  /* 루트 유동화로 줄어든 만큼 보정 */
}
@media (max-width:767px){
  body.hero-light .phero-inner{ padding-top:7.5rem }   /* 타이틀 위로 당김 */
  body.hero-light .phero-figure{ width:24rem; transform:translate(-50%, 8%); z-index:2 }  /* 큐브 위치는 고정 */
}
/* 브러시 리빌: base(심플) + detail(복합, 스크롤 크로스페이드) + 캔버스(브러시 리빌) */
body.hero-light .phero-figure .pf-base{ display:block; width:100%; height:auto; transition:opacity .45s ease }
body.hero-light .phero-figure .pf-detail{ position:absolute; inset:0; width:100%; height:auto; opacity:0; transition:opacity .45s ease; will-change:opacity }
body.hero-light .phero-figure .pf-canvas{ position:absolute; inset:0; width:100%; height:100%; pointer-events:none }

/* ============ About(company) 전용(B) — 라이트 히어로 위에 Vision 편입 ============ */
body.company .phero-inner{ padding-bottom:28rem }   /* 아래 Vision 편입 + 그래픽 공간 (두 배로) */
body.company .hero-vision{ position:relative; z-index:1; margin:0 auto; padding-bottom:6rem; padding-inline:var(--shell-pad) }
/* 태블릿: 히어로 하단 여백 확보해 큐브가 본문 글자와 안 겹치게 */
@media (min-width:768px) and (max-width:1023px){
  body.company .phero-inner{ padding-bottom:260px }
}
/* 모바일: Vision(남색 박스) 자체를 위로 — 큐브는 그대로 두고 남색 영역이 올라와 큐브 하단에 겹침. base 28rem 뒤에 둬야 이김 */
@media (max-width:767px){
  body.company .phero-inner{ padding-bottom:24rem; min-height:calc(100lvh + 3rem) }  /* 첫 화면은 히어로만 — 남색은 폴드 아래에서 시작 */
  body.company .hero-vision{ margin-top:-3rem }
}
body.company .tr-flush .sec{ padding-top:0 }  /* Track Record: 위쪽 패딩 제거 (Vision 패널에 붙임) */
/* Industry Firsts 최초 실적: 도식 패널 안 불릿 리스트 + 디바이더 (얼라이언스 노드 아래 합체, 소제목으로 묶음 구분) */
body.company .firsts .firsts-list-wrap{ margin-top:var(--space-48) }
body.company .firsts .firsts-list-wrap .ally-num{ font-size:var(--text-22) }  /* 기본 28에서 3토큰 다운 */
body.company .firsts .firsts-list{ margin-top:var(--space-16) }
body.company .firsts .firsts-list li{ display:flex; align-items:center; gap:1rem;
  padding-block:var(--space-24); font-size:var(--text-22); font-weight:500; color:var(--ink);
  line-height:var(--leading-heading) }
body.company .firsts .firsts-list{ display:grid; grid-template-columns:1fr 1fr; column-gap:var(--grid-gap) }  /* 2×2 배열 */
body.company .firsts .firsts-list li:nth-child(n+3){ border-top:1px solid rgba(var(--ink-rgb),.1) }  /* 둘째 줄에만 디바이더 */
@media (max-width:767px){
  body.company .firsts .firsts-list{ grid-template-columns:1fr }
  body.company .firsts .firsts-list li + li{ border-top:1px solid rgba(var(--ink-rgb),.1) }
}
body.company .firsts .firsts-list li::before{ content:''; flex:none; width:.375rem; height:.375rem;
  border-radius:50%; background:var(--purple-500) }
/* Industry Firsts 도식화: 의장사 허브 + 스템, 카드는 노드 점 붙은 항목으로 */
/* firsts 패널: ParaSta ps-flow처럼 그레이 배경(닷 패턴)으로 감쌈 */
body.company .firsts .firsts-panel{ background-color:rgba(var(--ink-rgb),.04); border-radius:var(--radius-card);
  padding:3.5rem clamp(1.5rem,4vw,3rem);
  background-image:radial-gradient(rgba(var(--ink-rgb),.06) 1px, transparent 1.5px); background-size:20px 20px }
body.company .firsts .firsts-hub{ display:flex; flex-direction:column; align-items:center; margin-bottom:0 }
body.company .firsts .firsts-stem{ width:0; height:2.25rem; border-left:2px dashed var(--gray-300) }  /* ParaSta ps-flow-link 점선 스타일 (그레이) */
/* ⊓ 분기 커넥터: 중앙 스템 → 수평 바 → 좌우 두 열로 하강 (ㄷ 90° 회전) */
body.company .firsts .firsts-branch{ position:relative; height:2rem; margin:0 }
body.company .firsts .firsts-branch::before{ content:''; position:absolute; top:0; left:25%; right:25%;
  border-top:2px dashed var(--gray-300) }
body.company .firsts .firsts-branch .fb-l, body.company .firsts .firsts-branch .fb-r{ content:''; position:absolute; top:0; height:100%;
  border-left:2px dashed var(--gray-300) }
body.company .firsts .firsts-branch .fb-l{ left:25% }
body.company .firsts .firsts-branch .fb-r{ left:75% }
/* 의장사 허브: WalletFi 코어 원 스타일(화이트 원 + gray-400 보더), 작게 + 로고 치환 */
body.company .firsts .chair-badge{ flex-direction:column; align-items:center; justify-content:center; gap:.625rem;
  width:12.5rem; height:12.5rem; padding:1.25rem; border-radius:50%; background:var(--white); border:1px solid rgba(var(--ink-rgb),.14); text-align:center;
  box-shadow:0 8px 24px rgba(var(--ink-rgb),.06); transition:transform .35s cubic-bezier(.2,.8,.2,1), box-shadow .35s }
@media (hover:hover){ body.company .firsts .chair-badge:hover{ transform:scale(1.03); box-shadow:0 16px 40px rgba(var(--ink-rgb),.1) } }
body.company .firsts .chair-badge .pm-mark{ display:block; width:4.95rem; height:4rem; overflow:hidden; flex:none }
body.company .firsts .chair-badge .pm-mark img{ height:4rem; width:auto; max-width:none; display:block }  /* 가로 로고(300×40)에서 좌측 컬러 심볼(0~48.4u)만 크롭 — 흰색 워드마크는 흰 원 위에서 안 보임 */
body.company .firsts .chair-badge i{ font-size:var(--text-20); font-style:normal; font-weight:500; color:var(--ink) }  /* 본문 검정(잉크)과 동일 토큰 + 한 토큰 업 */
/* firsts 카드: ParaSta ps-flow 밴드 스타일 — 화이트 + 소프트 보더 + 그림자 */
body.company .firsts .work-card{ min-height:0; border-radius:var(--radius-card-sm); padding:1.75rem 2rem;
  background:var(--white); border:1px solid rgba(var(--ink-rgb),.14);
  transition:transform .35s cubic-bezier(.2,.8,.2,1) }   /* 쉐도우 없음 — firsts 전용 처리 */
@media (hover:hover){ body.company .firsts .work-card:hover{ transform:scale(1.03) } }
body.company .firsts .work-card .work-bottom{ position:static; inset:auto }  /* 이미지 카드용 하단 고정 해제 → 일반 패딩 */
/* 얼라이언스 노드: 좌측 아이콘 영역 (로고 플레이스홀더 원) */
body.company .firsts .work-card{ display:flex; align-items:center; gap:var(--space-20) }
body.company .firsts .work-card::before{ content:''; flex:none; width:4.5rem; height:4.5rem; border-radius:50%; background:rgba(var(--ink-rgb),.08) }
body.company .firsts .work-card .work-bottom p{ margin-top:.25rem; font-size:var(--text-16) }  /* 타이틀-서브카피 간격 축소(.5rem→.25rem) + 한 토큰 업(14→16) */
body.company .firsts .work-card .work-bottom h3{ font-size:var(--text-22) }
body.company .firsts .work-card p:empty{ display:none }
/* Track Record 카드: work-card media 토큰 — 상단 아이콘 이미지 영역 + 하단 텍스트(숫자는 h3) */
@media (min-width:768px) and (max-width:1023px){ body.company .tr-flush .cards-3{ grid-template-columns:repeat(3,1fr) } }   /* 태블릿도 3열 */
body.company .tr-flush .work-card.grouped{ min-height:0; padding:0; overflow:hidden;
  background:color-mix(in srgb, var(--ink) 6%, var(--white)); border-radius:var(--radius-card) }
body.company .tr-flush .work-card.grouped::before{ flex:none; width:100%; aspect-ratio:5/4; height:auto; margin:0; border-radius:0;
  background-color:transparent; background-image:none;
  /* 레이어(위→아래): 아이콘 SVG → 하단 페이드(텍스트 영역 배경색으로 자연 연결) — 이미지를 안 가림 */
  background-repeat:no-repeat, no-repeat;
  background-position:center, 0 0;
  background-size:cover, 100% 100% }
body.company .tr-flush .work-bottom{ padding:var(--space-32); margin-top:-2rem; position:relative; z-index:1 }   /* 텍스트가 이미지 영역 하단에 살짝 걸침 */
body.company .tr-flush .work-meta{ color:var(--purple-500); font-weight:600; margin-bottom:var(--space-12) }   /* 라벨 3개 보라색, 아래 간격 16→12 */
body.company .tr-flush .work-card h3{ font-size:var(--text-40); font-weight:700; letter-spacing:-.01em; color:var(--ink) }   /* 수치 한 토큰 업(36→40) */
body.company .tr-flush .work-bottom p{ margin-top:0; font-size:var(--text-18); color:rgba(var(--ink-rgb),.6) }   /* 수치(h3)↔설명(p) 사이 간격 제거 */
/* 카드별 라인 아이콘 (스트로크 1.4 · 잉크 톤) — 깃발/코인 스택/추세 차트 */
body.company .tr-flush .cards-3 li:nth-child(1) .work-card.grouped::before{ background-image:url("assets/about/tr-1.svg"),
  linear-gradient(to bottom, rgba(var(--white-rgb),0) 55%, color-mix(in srgb, var(--ink) 6%, var(--white)) 96%) }
body.company .tr-flush .cards-3 li:nth-child(2) .work-card.grouped::before{ background-image:url("assets/about/tr-2.svg"),
  linear-gradient(to bottom, rgba(var(--white-rgb),0) 55%, color-mix(in srgb, var(--ink) 6%, var(--white)) 96%) }
body.company .tr-flush .cards-3 li:nth-child(3) .work-card.grouped::before{ background-image:url("assets/about/tr-3.svg"),
  linear-gradient(to bottom, rgba(var(--white-rgb),0) 55%, color-mix(in srgb, var(--ink) 6%, var(--white)) 96%) }
@media (hover:hover){ body.company .tr-flush .work-card.static:hover{ transform:scale(1.03) } }
/* ≤767: 이미지 제거, 3개를 한 박스 안 3칸(스탯 바)으로 */
@media (max-width:767px){
  body.company .tr-flush .cards-3{ grid-template-columns:repeat(3,1fr); gap:0;
    background-color:rgba(var(--ink-rgb),.04); border-radius:var(--radius-card-sm); padding:clamp(var(--space-24), 5.5vw, var(--space-40)) 0;   /* 위아래 여유: 화면 폭 가변 */
    background-image:radial-gradient(rgba(var(--ink-rgb),.06) 1px, transparent 1.5px); background-size:20px 20px }  /* firsts 패널과 동일한 그레이+닷 */
  body.company .tr-flush .cards-3 > li + li{ position:relative }
  body.company .tr-flush .cards-3 > li + li::before{ content:''; position:absolute; left:0; top:50%;
    transform:translateY(-50%); width:1px; height:56%; background:rgba(var(--ink-rgb),.08) }  /* 칸 사이 디바이더: 세로 중앙 56%만 */
  body.company .tr-flush .work-card.grouped{ background:transparent; border-radius:0; overflow:visible }
  body.company .tr-flush .work-card.grouped::before{ display:none }   /* 이미지 영역 제거 */
  body.company .tr-flush .work-bottom{ margin-top:0; padding:0 var(--space-16); text-align:center }
  body.company .tr-flush .work-meta{ margin-bottom:var(--space-8); justify-content:center; font-size:clamp(var(--text-14), 2.5vw, var(--text-16)) }  /* Since 2016 센터 + 가변 */
  body.company .tr-flush .work-card h3{ font-size:clamp(var(--text-24), 4.2vw, var(--text-36)) }   /* 640~767: 화면 폭 가변(vw), 토큰으로 상하한 */
  body.company .tr-flush .work-bottom p{ font-size:clamp(var(--text-14), 2.2vw, var(--text-16)) }   /* 설명: 화면 폭 가변 */
}
@media (max-width:639px){
  body.company .tr-flush .cards-3{ grid-template-columns:1fr; padding:var(--space-16) var(--space-24) }   /* 가로 3칸 → 세로 리스트, 좌우 패딩 추가 */
  body.company .tr-flush .cards-3 > li{ padding-block:var(--space-20) }
  body.company .tr-flush .work-bottom{ text-align:left; padding:0 }   /* 리스트: 좌측정렬, 좌우 패딩 제거(박스 패딩만) */
  body.company .tr-flush .work-meta{ justify-content:flex-start; font-size:clamp(var(--text-16), 2.5vw, var(--text-18)) }
  body.company .tr-flush .work-bottom p{ font-size:clamp(var(--text-18), 2.2vw, var(--text-20)) }   /* 설명 한 토큰 업 */
  body.company .tr-flush .cards-3 > li + li::before{ top:0; left:0; transform:none; width:100%; height:1px }   /* 디바이더 풀폭 */
  body.company .tr-flush .cards-3 .work-card h3{ font-size:clamp(var(--text-26), 4.2vw, var(--text-30)); white-space:nowrap }   /* 수치 한 토큰 업 */
}   /* base 뒤에 있어야 이김 (특이도 동일) */
/* Recognition 카드: 상단에 실제 인증 로고 들어갈 아이콘 영역 (플레이스홀더 원) — 오프셋은 공통 카드 패딩(1.5rem, ≥640px 2rem)과 동기화 */
body.company .recog .work-card::before{ content:''; position:absolute; top:1.5rem; left:1.5rem;
  width:5rem; height:5rem; border-radius:50%; background:rgba(var(--ink-rgb),.08) }
@media (min-width:640px){ body.company .recog .work-card::before{ top:2rem; left:2rem } }
body.company .recog .work-card .work-bottom h3{ font-size:var(--text-26) }  /* 22 → 24 → 26 두 토큰 업 (사용자 확정) */
body.company .recog .work-card .work-bottom p{ font-size:var(--text-16) }  /* 서브카피 한 토큰 업 (기본 text-14) */
/* History 드롭다운: 체크박스 토글 아코디언 — 대표내용은 label, 세부는 타임라인 레일 위 연보라 미니 노드 */
body.company .ht-acc{ padding:0 }
body.company .ht-acc label{ cursor:pointer; display:flex; align-items:center; justify-content:space-between;
  gap:1rem; padding:1.3rem 1.6rem }
body.company .ht-acc .ht-chev{ flex:none; width:.625rem; height:.625rem; margin-top:-.25rem;
  border-right:2px solid rgba(var(--ink-rgb),.45); border-bottom:2px solid rgba(var(--ink-rgb),.45);
  transform:rotate(45deg); transition:transform .45s cubic-bezier(.16,1,.3,1) }
body.company .ht-acc input:checked ~ label .ht-chev{ transform:rotate(225deg); margin-top:.25rem }
/* 부드러운 펼침·접힘: grid-rows 0fr↔1fr 트랜지션. 좌측으로 확장한 클립 박스가 레일 노드까지 포함 */
body.company .ht-subwrap{ display:grid; grid-template-rows:0fr; transition:grid-template-rows .5s cubic-bezier(.16,1,.3,1);
  margin-left:-10.725rem }  /* 연도 칼럼 5.5 + 갭 1.75 + 카드 패딩 1.6 + 레일까지 1.875 */
body.company .ht-acc input:checked ~ .ht-subwrap{ grid-template-rows:1fr }
body.company .ht-sub{ list-style:none; margin:0; overflow:hidden; min-height:0; padding-left:12.325rem;  /* 마진 상쇄 + 카드 좌패딩 1.6 */
  display:flex; flex-direction:column; gap:.625rem; opacity:0; transform:translateY(-4px);
  transition:opacity .4s ease .05s, transform .5s cubic-bezier(.16,1,.3,1) }
body.company .ht-acc input:checked ~ .ht-subwrap .ht-sub{ opacity:1; transform:none }
body.company .ht-sub li{ position:relative; padding:0 1.6rem 0 0; font-size:var(--text-16); line-height:var(--leading-body);
  color:rgba(var(--ink-rgb),.62) }
body.company .ht-sub li:last-child{ padding-bottom:1.3rem }
body.company .ht-sub li::before{ content:''; position:absolute; left:-10.725rem; top:.5em; width:7px; height:7px; border-radius:50%;
  margin-left:1px; background:var(--purple-300) }  /* 레일 위: 메인 노드(11px 보라)보다 작고 연한 연보라, 레일 센터 정렬 실측 보정 */
@media (max-width:639px){  /* 모바일: 연도 상단 배치라 레일까지 거리 축소 */
  body.company .ht-subwrap{ margin-left:-3.475rem }
  body.company .ht-sub{ padding-left:5.075rem }
  body.company .ht-sub li::before{ left:-3.14rem }
}
/* 펼침 시 연도·노드는 대표행 첫 줄 중심(라벨 패딩 1.3 + 행간 절반 .9 = 2.2rem)에 고정 */
body.company .ht-item{ align-items:start }
body.company .ht-yr{ line-height:1; padding-top:calc(2.2rem - .875rem) }  /* 연도 중심 = 2.2rem (text-28 절반 보정) */
body.company .ht-node{ top:calc(2.2rem + 1.25rem); transform:translateY(-50%) }  /* +아이템 상단 패딩 1.25 (absolute는 패딩 미반영) */
body.company .phero-text .eyebrow, body.contact .phero-text .eyebrow{ display:none }   /* 히어로 아이브로우 제거 (About·Contact) */
/* Contact 전용: 그래픽 없는 히어로 → 여백 축소로 문의 섹션을 위로, 카드는 솔루션 톤(불투명 그레이·테두리 없음) */
body.contact .phero-inner{ padding-top:9rem; padding-bottom:var(--space-32); align-items:flex-start; text-align:left }
body.contact .phero-text{ align-items:flex-start; align-self:flex-start; margin-inline:0 }
body.contact .phero + section .sec{ padding-top:var(--space-32) }
body.contact .light-card{ background:var(--white); border:1px solid rgba(var(--ink-rgb),.12);
  box-shadow:0 8px 24px rgba(var(--ink-rgb),.06); padding:var(--space-32);
  transition:transform .35s cubic-bezier(.2,.8,.2,1), box-shadow .35s ease }   /* ParaSta wfd-band 톤: 흰색+스트로크+쉐도우 */
@media (hover:hover){ body.contact .light-card:hover{ transform:scale(1.02); box-shadow:0 16px 40px rgba(var(--ink-rgb),.1) } }
/* 상담 신청 버튼: 메인 히어로 CTA와 동일 크기 (text-16 + 배지 2.5rem) */
body.contact .modal-bottom .pill .hspring{ font-size:var(--text-16); gap:.875rem; padding:.5rem .5rem .5rem 1.75rem }
body.contact .modal-bottom .pill-badge{ width:2.5rem; height:2.5rem; font-size:var(--text-18) }
body.contact .work-bottom p{ font-size:var(--text-18) }   /* Process 카드 본문 키움 */
/* 개인정보 수집·이용 안내 (제출 시 동의 간주) */
body.contact .privacy-guide{ display:flex; flex-direction:column; gap:.3rem; font-size:var(--text-16); color:rgba(var(--ink-rgb),.5) }
body.contact .privacy-guide strong{ font-size:var(--text-18); font-weight:600; color:rgba(var(--ink-rgb),.5); margin-bottom:.15rem }
body.contact .pg-item{ position:relative; padding-left:.85rem }
body.contact .pg-item::before{ content:'·'; position:absolute; left:.1rem; color:rgba(var(--ink-rgb),.4) }
body.contact .work-meta{ color:var(--purple-300) }   /* STEP 01 라벨 보라 (다크카드 톤) */
/* 문의 폼·연락처 텍스트 2토큰씩 키움 */
body.contact .light-card .cap{ font-size:var(--text-22); font-weight:600; margin-bottom:.25rem }
body.contact .light-card p{ font-size:var(--text-20) }
body.contact .modal-field label{ font-size:var(--text-16) }
body.contact .modal-field input, body.contact .modal-field select, body.contact .modal-field textarea{ font-size:var(--text-20); padding:1.25rem }
/* 관심 서비스 드롭다운: 기본 화살표 제거 + 커스텀 chevron, 오른쪽 여백 확보 */
body.contact .modal-field select{ appearance:none; -webkit-appearance:none; padding-right:2.75rem;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16' fill='none' stroke='%230E0C27' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 6l4 4 4-4'/%3E%3C/svg%3E");
  background-repeat:no-repeat; background-position:right 1.1rem center; background-size:1rem }
body.contact .modal-form{ gap:var(--space-24) }                 /* 필드 행 간격 벌림 (관심 서비스·문의 내용) */
body.contact .addr-list .k{ font-size:var(--text-16) }
body.contact .addr-list .v{ font-size:var(--text-20) }
/* 폼 섹션: 좌(폼) 8컬럼 · 우(연락처) 4컬럼 — 12컬럼 그리드 */
.contact-split{ display:grid; grid-template-columns:repeat(var(--grid-cols),1fr); gap:var(--grid-gap) }
.contact-split > :first-child{ grid-column:1 / 9 }
.contact-split > :last-child{ grid-column:9 / 13 }
@media (max-width:767px){ .contact-split{ display:flex; flex-direction:column } }
/* Vision WalletFi 도식 — ParaSta 회색·점 스타일 · 풀 12칼럼 그리드(페이지 그리드 스냅) */
.wfd{ margin:3rem 0 0; display:grid; grid-template-columns:repeat(12,minmax(0,1fr));
  column-gap:var(--grid-gap); row-gap:var(--grid-gap); align-items:stretch;
  padding:3rem 2.5rem; border-radius:var(--radius-card);
  background-color:rgba(var(--ink-rgb),.06);
  background-image:radial-gradient(rgba(var(--ink-rgb),.06) 1px, transparent 1.5px); background-size:20px 20px }
.wfd-side{ grid-column:span 4 }
.wfd-core{ grid-column:span 4; position:relative; border-color:var(--border-violet) }
.wfd-infra{ grid-column:1 / -1 }
.wfd-band{ background:var(--white); border:1px solid rgba(var(--ink-rgb),.12); border-radius:var(--radius-card-sm);
  box-shadow:0 8px 24px rgba(var(--ink-rgb),.06); padding:1.75rem 1.5rem; text-align:center;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.75rem }
.wfd-t{ font-size:var(--text-18); font-weight:600; color:var(--ink) }
.wfd-t em{ font-style:normal; color:var(--purple-500); font-weight:500; margin-left:.25rem }
.wfd-d{ font-size:var(--text-14); line-height:var(--leading-body,1.6); color:rgba(var(--ink-rgb),.6) }
.wfd-d b{ display:block; color:var(--ink); font-weight:600; font-size:var(--text-16); margin-bottom:.125rem }
.wfd-core .wfd-t{ color:var(--purple-500); font-size:var(--text-24) }
.wfd-s{ font-size:var(--text-14); color:rgba(var(--ink-rgb),.62); max-width:22rem }
/* 수렴 화살표: 코어 좌우 그리드 갭 중앙에 겹침 */
.wfd-core::before, .wfd-core::after{ position:absolute; top:50%; transform:translate(-50%,-50%);
  font-size:var(--text-22); line-height:1; color:var(--purple-500) }
.wfd-core::before{ content:'→'; left:calc(var(--grid-gap) / -2) }
.wfd-core::after{ content:'←'; left:calc(100% + var(--grid-gap) / 2) }
.wfd-infra{ background:linear-gradient(135deg,var(--purple-500),var(--purple-400)); border-radius:var(--radius-card-sm); padding:1.5rem 1.375rem; text-align:center }
.wfd-infra-t{ font-size:var(--text-16); font-weight:700; letter-spacing:.04em; color:var(--white); margin:0 0 .875rem }
.wfd-chips{ display:flex; flex-wrap:wrap; justify-content:center; gap:.625rem }
.wfd-chips span{ font-size:var(--text-14); font-weight:600; color:var(--white); background:rgba(var(--white-rgb),.16);
  border:1px solid rgba(var(--white-rgb),.28); border-radius:var(--radius-pill,999px); padding:.5rem 1rem }
@media (max-width:767px){ .wfd{ padding:2rem 1.25rem } .wfd-side, .wfd-core{ grid-column:1 / -1 }
  .wfd-core::before, .wfd-core::after{ display:none } }
/* Vision: Proven Core식 다크 박스로 가둠(타이틀 포함) — 위 히어로는 라이트 */
body.company .vision-panel{ border-radius:var(--radius-card); background:var(--ink); color:var(--white);
  padding:3rem 1.75rem; text-align:left }
@media (min-width:640px){ body.company .vision-panel{ padding:3.5rem 3rem } }
@media (min-width:1024px){ body.company .vision-panel{ padding:4.5rem 4.5rem } }
/* 헤더 텍스트 라이트 반전 */
body.company .vision-panel .sh-center{ margin:0 auto }
body.company .vision-panel .eyebrow{ color:rgba(var(--white-rgb),.9) }
body.company .vision-panel .eyebrow::before, body.company .vision-panel .eyebrow::after{ color:rgba(var(--white-rgb),.4) }  /* 다크 카드: [ ] 브라켓도 라이트 톤 */
body.company .vision-panel .sec-h2{ color:var(--white); font-size:var(--text-30); font-weight:500; letter-spacing:-.01em }   /* Proven Core(stats-h2)와 동일 폰트 */
@media (min-width:768px){ body.company .vision-panel .sec-h2{ font-size:var(--text-36) } }
body.company .vision-panel .phero-lead{ color:rgba(var(--white-rgb),.68); font-size:var(--text-20) }
@media (max-width:1023px){ body.company .vision-panel .phero-lead{ font-size:var(--text-18) } }
/* wfd 다이어그램 다크 톤 */
body.company .vision-panel .wfd{ background-color:transparent; padding:0; margin-top:5.5rem;
  background-image:radial-gradient(rgba(var(--white-rgb),.04) 1px, transparent 1.5px); background-size:20px 20px }
body.company .vision-panel .wfd-band{ background:var(--purple-400); box-shadow:none; position:relative; z-index:1;
  box-sizing:border-box; border:1px solid rgba(var(--white-rgb),.35) }  /* 좌우 원: 밝은 퍼플 + 반투명 흰 아웃라인 */
body.company .vision-panel .wfd-t{ color:var(--white); font-size:var(--text-20) }  /* 좌우 타이틀: 코어보다 한 단계 작게 */
body.company .vision-panel .wfd-t em{ color:var(--white) }
body.company .vision-panel .wfd-d{ color:rgba(var(--white-rgb),.62) }
body.company .vision-panel .wfd-d b{ color:var(--white) }
body.company .vision-panel .wfd-s{ color:rgba(var(--white-rgb),.64) }
body.company .vision-panel .wfd-side .wfd-d{ font-size:var(--text-16) }   /* 사이드 서브텍스트(금융기관·핀테크 등) 14→16 */
body.company .vision-panel .wfd-core{ background:var(--white); border:1px solid var(--gray-400) }  /* WalletFi = 흰색 원, 보더는 purple-300과 비슷한 명도의 모노(gray-400) */
body.company .vision-panel .wfd-core .wfd-t{ color:var(--purple-500); font-size:var(--text-24) }  /* 흰 원 위 글자 반전 */
body.company .vision-panel .wfd-core .wfd-s{ color:rgba(var(--ink-rgb),.6) }
/* TradFi·WalletFi·DeFi 셋 다 원 */
body.company .vision-panel .wfd{ align-items:center }
body.company .vision-panel .wfd-band{ aspect-ratio:1; border-radius:50%; padding:1.5rem;
  justify-content:center; width:min(100%, 17rem); justify-self:center; margin-inline:auto }  /* 원 크기 19rem→17rem */
/* 코어: 스케일 안 되는 래퍼(그리드 아이템, 커넥터 보유) + 안쪽 흰 원(호버 시 이것만 확대) */
body.company .vision-panel .wfd-core-wrap{ grid-column:span 4; justify-self:center; position:relative;
  width:min(100%, 19rem); aspect-ratio:1 }   /* 코어(WalletFi)만 사이드(17rem)보다 크게 */
body.company .vision-panel .wfd-core{ width:100% }  /* 래퍼를 꽉 채움 */
body.company .vision-panel .wfd-core .wfd-s{ max-width:13rem; font-size:var(--text-16); line-height:1.5 }   /* 사이드 서브와 동일 토큰 16 + 행간 살짝 확장 */
body.company .vision-panel .wfd-d{ max-width:13rem; font-size:var(--text-18) }  /* 좌우 서브카피도 코어와 동일 */
/* 노드 점: 흰 원(코어) 양옆 모서리에 붙음 → 원과 함께 스케일 */
body.company .vision-panel .wfd-core::before, body.company .vision-panel .wfd-core::after{
  content:''; display:block; position:absolute; top:50%; z-index:2; border:0; font-size:0;
  width:9px; height:9px; border-radius:50%; background:var(--gray-400) }
body.company .vision-panel .wfd-core::before{ left:0; right:auto; transform:translate(calc(-50% - 1px),-50%) }
body.company .vision-panel .wfd-core::after{ left:auto; right:0; transform:translate(calc(50% + 1px),-50%) }
/* 점선: 별개 — 스케일 안 되는 래퍼 pseudo, 원 모서리에서 살짝 떨어져 갭에만 */
body.company .vision-panel .wfd-core-wrap::before, body.company .vision-panel .wfd-core-wrap::after{
  content:''; position:absolute; top:50%; transform:translateY(-50%) scaleX(0); height:0; z-index:-1;
  width:calc(var(--grid-gap) + 6.75rem + 5rem);  /* 갭 + 양쪽 원 안으로 넉넉히 오버슛(z-index:-1이라 원 뒤로 숨음) */
  border-top:2px dashed var(--gray-400);  /* PortX/ParaSta와 동일한 dashed 보더 스타일 */
  transition:transform .45s cubic-bezier(.16,1,.3,1) }  /* 코어 뒤 좌우로 솩 확장 */
body.company .vision-panel .wfd-core-wrap::before{ left:auto; right:100%; transform-origin:right center }
body.company .vision-panel .wfd-core-wrap::after{ left:100%; transform-origin:left center }
/* Wallet Infrastructure: 라인 박스 */
body.company .vision-panel .wfd-infra{ background:transparent; border:1px solid var(--gray-600); padding-block:1.75rem; margin-top:1rem;
  /* 좌우 원 바깥 가장자리에 맞춤: 4칼럼 셀폭 − 19rem 원폭의 절반이 인셋 */
  margin-inline:calc(((100% - 11 * var(--grid-gap)) / 3 + 3 * var(--grid-gap) - 19rem) / 2) }
/* 태블릿(768~1023): 원이 19rem보다 작아져 위 calc가 음수가 되므로, 밴드를 원 라인 안쪽으로 보정 */
@media (min-width:768px) and (max-width:1023px){ body.company .vision-panel .wfd-infra{ margin-inline:1rem }
  body.company .vision-panel .wfd{ margin-top:2.5rem }   /* 본문↔다이어그램 간격 축소 */
  body.company .vision-panel .wfd-band{ width:min(100%, 13rem) }   /* 사이드 원 축소 */
  body.company .vision-panel .wfd-core-wrap{ width:min(100%, 14.5rem) }   /* 코어 원 축소(사이드보다 살짝 크게) */
  body.company .vision-panel .wfd-core{ width:100% }   /* 코어 밴드는 wrap(14.5rem) 꽉 채움 — 위 13rem 규칙 무효화 */
  body.company .vision-panel .wfd-core .wfd-t{ font-size:var(--text-22) }   /* WalletFi 타이틀 한 단계 축소 */
  body.company .vision-panel .wfd-side .wfd-t{ font-size:var(--text-18) }   /* 양옆 타이틀(TradFi/DeFi) 한 단계 축소 */
  body.company .vision-panel .wfd-infra-t{ font-size:var(--text-16) }   /* Wallet Infrastructure 한 단계 축소 */
  body.company .vision-panel .wfd-band{ gap:.5rem }   /* 원 안 타이틀↔서브텍스트 간격 살짝 축소 */
}
@media (max-width:767px){ body.company .vision-panel .wfd-infra{ margin-inline:0 }   /* 모바일: calc 음수 방지(오버플로우) */
  /* 동그라미 3개: 세로 스택 대신 한 줄 유지 + 원·폰트 축소 */
  body.company .vision-panel .wfd{ margin-top:2rem }
  body.company .vision-panel .wfd-side{ grid-column:span 4 }
  body.company .vision-panel .wfd-core-wrap{ grid-column:span 4; width:min(100%, 12rem) }
  body.company .vision-panel .wfd-band{ width:min(100%, 11rem); padding:1rem; gap:.25rem }
  body.company .vision-panel .wfd-core{ width:100% }
  body.company .vision-panel .wfd-core .wfd-t{ font-size:var(--text-20) }
  body.company .vision-panel .wfd-core .wfd-s{ font-size:var(--text-14) }
  body.company .vision-panel .wfd-side .wfd-t{ font-size:var(--text-16) }
  body.company .vision-panel .wfd-side .wfd-d{ font-size:var(--text-14) }
  /* 점선: 축소된 원 기준으로 오버슛 줄임 — 사이드 원 밖으로 못 나가게 */
  body.company .vision-panel .wfd-core-wrap::before, body.company .vision-panel .wfd-core-wrap::after{
    width:calc(var(--grid-gap) + 3rem) }
}
/* 모바일(≤640): 원 3개 세로 스택 + 서브텍스트 유지 + 커넥터(점·점선) 세로 전환 */
@media (max-width:640px){
  body.company .vision-panel .wfd-core .wfd-t{ font-size:var(--text-20) }  /* WalletFi: 세로 스택에서 원이 커져 20으로 복귀 */
  body.company .vision-panel .wfd-side .wfd-t{ font-size:var(--text-18) }  /* 사이드 타이틀(전통금융/탈중앙화 금융) 살짝 업 */
  body.company .vision-panel .wfd-side, body.company .vision-panel .wfd-core-wrap{ grid-column:1 / -1 }
  /* 세로 스택은 폭 여유 있으니 원 살짝 키움 (서브텍스트 수용) — 사이드만! (.wfd-band로 잡으면 코어까지 축소돼 래퍼와 어긋남) */
  body.company .vision-panel .wfd-band.wfd-side{ width:min(100%, 13rem) }
  body.company .vision-panel .wfd-core-wrap{ width:min(100%, 14rem) }
  body.company .vision-panel .wfd-core{ width:100% }  /* 코어는 래퍼(14rem) 꽉 채움 — 점·점선 앵커 일치 */
  /* 노드 점: 코어 원 상하 모서리로 이동 */
  body.company .vision-panel .wfd-core::before{ left:50%; top:0; transform:translate(-50%, calc(-50% - 1px)) }
  body.company .vision-panel .wfd-core::after{ left:50%; right:auto; top:auto; bottom:0; transform:translate(-50%, calc(50% + 1px)) }
  /* 점선: 코어 위아래로 뻗는 세로 대시 (리빌은 scaleY로) */
  body.company .vision-panel .wfd-core-wrap::before, body.company .vision-panel .wfd-core-wrap::after{
    left:50%; width:0; height:calc(var(--grid-gap) + 4rem); border-top:0;
    border-left:2px dashed var(--gray-400) }
  body.company .vision-panel .wfd-core-wrap::before{ right:auto; top:auto; bottom:100%;
    transform:translate(-50%,0) scaleY(0); transform-origin:bottom center }
  body.company .vision-panel .wfd-core-wrap::after{ left:50%; top:100%;
    transform:translate(-50%,0) scaleY(0); transform-origin:top center }
}
/* 인프라 타이틀: 사이즈 키우고 웨이트 낮게 */
body.company .vision-panel .wfd-infra-t{ font-size:var(--text-18); font-weight:500; letter-spacing:normal; color:var(--gray-400); margin-bottom:.625rem }   /* 20→18 (한 토큰↓) */
/* ── Vision 다이어그램 순차 리빌: 코어 먼저 → 점선 좌우 확장 → 양옆 원 딱딱 ── */
body.company .vision-panel .wfd-core, body.company .vision-panel .wfd-side{ opacity:0 }
body.company .vision-panel .wfd.is-in .wfd-core{ opacity:1; animation:wfdPop .5s cubic-bezier(.16,1,.3,1) backwards }
body.company .vision-panel .wfd.is-in .wfd-core-wrap::before, body.company .vision-panel .wfd.is-in .wfd-core-wrap::after{ transform:translateY(-50%) scaleX(1); transition-delay:.3s }
@media (max-width:640px){  /* 모바일 세로 점선: 리빌 완료 상태도 세로 트랜스폼으로 (위 가로용 규칙 대체 — 반드시 뒤에) */
  body.company .vision-panel .wfd.is-in .wfd-core-wrap::before,
  body.company .vision-panel .wfd.is-in .wfd-core-wrap::after{ transform:translate(-50%,0) scaleY(1) }
}
body.company .vision-panel .wfd.is-in .wfd-side{ opacity:1; animation:wfdPop .5s cubic-bezier(.16,1,.3,1) backwards }
body.company .vision-panel .wfd.is-in .wfd-side{ animation-delay:.55s }  /* 좌우 동시 등장 */
@keyframes wfdPop{ from{ opacity:0; transform:scale(.82) } }
/* 인프라 카드 전체 호버 스케일 (칩 개별 호버 아님) */
body.company .vision-panel .wfd-infra{ transition:transform .35s cubic-bezier(.2,.8,.2,1) }
@media (hover:hover){ body.company .vision-panel .wfd-infra:hover{ transform:scale(1.03) } }
/* 항목: 알약 대신 · 구분 텍스트 (서브카피와 동일 톤) */
body.company .vision-panel .wfd-chips{ display:block; font-size:var(--text-20); font-weight:500; color:var(--white) }   /* 인프라 텍스트 20 · 웨이트 500 */
@media (max-width:640px){ body.company .vision-panel .wfd-chips{ font-size:var(--text-18) } }   /* 모바일: 칩 살짝 다운(20→18) — 위 20 규칙 뒤라 이김 */
/* 호버 리빌: 원만 scale — 커넥터는 wfd-core-wrap 소속이라 함께 안 커짐 */
body.company .vision-panel .wfd-band{ transition:transform .35s cubic-bezier(.2,.8,.2,1), background-color .35s }
@media (hover:hover){ body.company .vision-panel .wfd-band:hover{ transform:scale(1.05) } }

/* ============ WHAT IS (좌 다이어그램 / 우 텍스트) ============ */
.whatis-grid{ display:grid; grid-template-columns:1fr; gap:2.5rem; align-items:center }
@media (max-width:639px){ .whatis-grid{ gap:0 } }
@media (min-width:900px){
  .whatis-grid{ grid-template-columns:repeat(12,1fr); column-gap:var(--grid-gap) }
  .whatis-grid .ps-flow{ grid-column:1 / 7 }
  .whatis-grid .whatis-text{ grid-column:8 / 13 } }
@media (max-width:899px){ .whatis-grid .ps-flow{ order:1 } }
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
/* PortX 도식: 코어 내부 기능 2분할 미니 카드 */
.px-duo{ display:grid; grid-template-columns:1fr 1fr; gap:.75rem; margin-top:1rem }
.px-mini{ background:rgba(var(--ink-rgb),.05); border-radius:var(--radius-control); padding:1rem; text-align:left }
.px-mini .mi-head{ display:flex; align-items:center; gap:.5rem; font-size:var(--text-14); font-weight:600; color:var(--ink); margin-bottom:.375rem }
.px-mini .mi-head svg{ width:1.125rem; height:1.125rem; flex:none; color:var(--purple-500) }
.px-mini p{ font-size:var(--text-14); color:rgba(var(--ink-rgb),.55); line-height:1.4 !important; word-break:keep-all }  /* 행간 토큰 예외(사용자 승인): 다이어그램 미니카드만 타이트하게 */
.px-mini p.pm-break{ word-break:break-all }  /* 이 카드 문단만: 줄을 꽉 채워 끊기(사용자 지정, 여기만) */
@media (max-width:480px){ .px-duo{ grid-template-columns:1fr } }
/* ============ SUBPAGE UTILITIES ============ */
.sec{ padding:5rem 1.25rem }
@media (min-width:640px){ .sec{ padding-left:2rem; padding-right:2rem } }
@media (min-width:1024px){ .sec{ padding-block:6rem } }
.sec.uc-tail{ padding-bottom:var(--space-120) }   /* 마지막 Use Cases 섹션: 푸터 전 여백 확대 */
/* 섹션 서브카피·바디카피 = text-20 (2026-07-13 통일), 컨테이너 풀폭 */
.sec .phero-lead{ font-size:var(--text-20); max-width:none }
/* 타이틀 변형: 서브카피 있는 버전은 하단 0.25rem, 없는 버전은 기본 2rem */
.sec-h2.has-lead{ margin-bottom:.375rem }
.sec-h2.has-body{ margin-bottom:2rem }
.sec-h2.has-body + .phero-lead{ font-size:var(--text-20) }  /* 바디카피는 text-20 */
/* 섹션 헤더 중앙정렬 변형 (sec_head layout='center') */
.sh-center{ text-align:center }
.sh-center .sec-h2{ margin-left:auto; margin-right:auto }
.sec-lead{ margin-bottom:3rem }
.sh-center .phero-lead{ margin-left:auto; margin-right:auto; font-size:var(--text-20) }
.sh-center .sec-lead{ margin-bottom:3rem }
.sec-h2{ margin:1.25rem 0 3rem; max-width:24ch; font-size:var(--text-32); font-weight:600; letter-spacing:-.02em; line-height:var(--leading-heading) }
@media (min-width:640px){ .sec-h2{ font-size:var(--text-40) } }   /* 태블릿: 데스크톱보다 한 단계 작게 */
/* 태블릿·모바일(≤1023): 섹션 리드(및 리드 없는 타이틀) 아래 간격 축소 3rem→2rem — 전 서브페이지 공통 */
@media (max-width:1023px){
  .sec-lead, .sh-center .sec-lead{ margin-bottom:clamp(var(--space-16), 4.5vw, var(--space-32)) }   /* 화면 폭 가변 (4.5vw 사용자 확정) */
  .sec-h2:not(.has-lead){ margin-bottom:clamp(var(--space-16), 2.5vw, var(--space-32)) }
}
@media (min-width:1024px){ .sec-h2{ font-size:var(--text-48) } }
/* 태블릿 이하: 서브카피·바디카피 한 톤 작게 (text-20 → text-18) */
@media (max-width:1023px){ .sec .phero-lead, .sec-h2.has-body + .phero-lead, .sh-center .phero-lead{ font-size:var(--text-18) } }
/* 섹션 헤더 좌우형(sec_head layout='split'): 좌 아이브로우+타이틀 / 우 서브카피, 900↓ 스택 */
.sec-head-split{ margin-bottom:3rem }
.sec-head-split .sec-h2{ margin-bottom:0 }
.sec-head-split .shr .phero-lead{ font-size:var(--text-18); max-width:34rem; margin-top:1rem }
@media (min-width:900px){
  .sec-head-split{ display:grid; grid-template-columns:repeat(12,1fr); column-gap:var(--grid-gap); align-items:end }
  .sec-head-split .shl{ grid-column:1 / 7 }
  .sec-head-split .shr{ grid-column:8 / 13 }
  .sec-head-split .shr .phero-lead{ margin-top:0; margin-bottom:.375rem } }
.cards-3{ display:grid; grid-template-columns:1fr; gap:1.5rem }
@media (min-width:768px){ .cards-3{ grid-template-columns:repeat(2,1fr) } }
@media (min-width:1024px){ .cards-3{ grid-template-columns:repeat(3,1fr) } }
.cards-2{ display:grid; grid-template-columns:1fr; gap:1.5rem }
@media (min-width:768px){ .cards-2{ grid-template-columns:repeat(2,1fr) } }
.cards-4{ display:grid; grid-template-columns:repeat(2,1fr); gap:1rem }
@media (min-width:1024px){ .cards-4{ grid-template-columns:repeat(4,1fr) } }
/* 그레이 라벨 카드 (Coverage 등) — 짧은 유형 라벨용 */
.label-card{ background:color-mix(in srgb, var(--ink) 6%, var(--white)); border-radius:var(--radius-card-sm);
  padding:1.75rem; min-height:8rem; display:flex; align-items:flex-end;
  font-size:var(--text-18); font-weight:600; letter-spacing:-.01em; color:var(--ink); word-break:keep-all }
.work-card.sm{ min-height:18rem }
/* 카드 톤 변형: tone='gray' — 코어모듈式 라이트 그레이 (스코프 무관 어디서든) */
.work-card.t-gray{ background:color-mix(in srgb, var(--ink) 6%, var(--white)); color:var(--ink) }
.work-card.t-gray .work-meta{ color:var(--purple-500); font-weight:600 }
.work-card.t-gray .work-bottom h3{ color:var(--ink) }
.work-card.t-gray .work-bottom p{ color:rgba(var(--ink-rgb),.6) }
.work-card.t-gray .tag{ border:none; background:rgba(var(--ink-rgb),.45); color:var(--white); font-weight:500 }
.work-card.static{ cursor:default; transition:transform .35s cubic-bezier(.2,.8,.2,1) }
.work-card.static:hover{ transform:scale(1.03) }
/* grouped: 상단 이미지 영역(고정 높이) + 텍스트는 동일 y에서 시작 */
.work-card.grouped{ min-height:32rem; height:100%; display:flex; flex-direction:column }
/* grouped 카드가 든 그리드 셀만 flex로 (다른 카드 레이아웃 영향 없이 높이 정렬) */
.cards-3 > li:has(.work-card.grouped), .cards-2 > li:has(.work-card.grouped){ display:flex }
.cards-3 > li > .work-card.grouped, .cards-2 > li > .work-card.grouped,
.cards-3 > li > .card-link, .cards-2 > li > .card-link{ flex:1 1 auto; min-width:0 }
.card-link > .work-card.grouped{ flex:1 1 auto; min-width:0 }  /* 링크 래핑 카드: li>a>article 구조 대응 */
.work-card.grouped::before{ content:''; flex:none; height:16rem } /* 이미지 영역 */
/* 상세페이지 다크카드 이미지 영역 (임시: 공통 1장, 추후 개별 교체) — full-bleed(좌우·위 여백 없음) + 텍스트와 간격 */
.cards-3 .work-card.grouped::before, .cards-2 .work-card.grouped::before{
  margin:-1.5rem -1.5rem 1.5rem; border-radius:0;
  background:url('assets/parasta/body-test.avif') center/cover no-repeat }
@media (min-width:640px){
  .cards-3 .work-card.grouped::before, .cards-2 .work-card.grouped::before{ margin:-2rem -2rem 1.75rem } }
/* 개별 이미지 지정 카드(card media=경로) — 공용 placeholder 대신 해당 이미지 */
.cards-3 .work-card.grouped[style*="--media"]::before, .cards-2 .work-card.grouped[style*="--media"]::before{ background:var(--media) center/cover no-repeat }
/* PortX Key Features — 타이틀 위 간격 확보 */
.kf-media .work-card.grouped .work-bottom{ padding-top:var(--space-16) }
.kf-media .work-card.grouped::before{ height:20rem; opacity:.9 }   /* 이미지 영역 높이(기본 16rem→20rem) + 투명도 90% */
/* 호버 크로스페이드: 호버 이미지 레이어(::after)를 이미지 영역에 겹쳐 opacity 교차 */
.kf-media .work-card.grouped[style*="--media-hover"]::after{
  content:''; position:absolute; top:0; left:0; right:0; height:20rem;
  background:var(--media-hover) center/cover no-repeat; opacity:0; pointer-events:none;
  transition:opacity .4s ease; z-index:1 }
@media (hover:hover){ .kf-media .work-card.grouped[style*="--media-hover"]:hover::after{ opacity:.9 } }
/* 짧은 콘텐츠 카드도 과하지 않게: grouped 최소높이는 콘텐츠 기준 */
.cards-3 .work-card.grouped, .cards-2 .work-card.grouped{ min-height:0 }
/* 세로형 이미지 카드 변형: 이미지 영역을 카드의 약 2/3로 (기본 16rem → 24rem) */
.media-tall .work-card.grouped::before{ height:24rem }
@media (max-width:639px){ .media-tall .work-card.grouped::before{ height:14rem } }
.work-card.grouped .work-bottom{ position:static; inset:auto }
.work-card.grouped .work-meta{ margin-bottom:.875rem; color:var(--purple-300) }
.work-card.grouped .work-bottom p{ font-size:var(--text-16) }
.work-card.grouped .tag{ font-size:var(--text-16); font-weight:500; padding:.625rem 1.25rem; color:var(--purple-300);
  border:none; background:rgba(var(--purple-300-rgb),.12) }  /* 연보라 필 + 연보라 텍스트 */
.cm-cards .work-card.grouped .tag, .work-card.t-gray .tag{
  background:rgba(var(--ink-rgb),.45); color:var(--white) }  /* 그레이 카드 = 진한 잉크 필 + 흰 텍스트 (두 벌 체계) */
.core-mods .work-bottom p{ font-size:var(--text-16) }
/* ---- 모바일(≤639) 가독성 보정: 간격·R값·폰트 축소 ---- */
@media (max-width:639px){
  .sec{ padding-block:4rem }
  .sec-h2{ margin-bottom:2rem }
  body.hero-dark .phero-text .phero-lead{ font-size:var(--text-18) }
  body.hero-dark .phero-visual{ border-radius:var(--radius-card-sm) }
  /* 카드 그리드 모바일 1열: 카드 컴팩트 (cards-2·3·코어모듈 공통 — 카드 간격 1rem 통일) */
  .cards-3:has(.work-card.grouped), .cards-2:has(.work-card.grouped), .cm-grid .cm-cards{ gap:1rem }
  .cards-3 .work-card.grouped, .cards-2 .work-card.grouped{ min-height:auto; border-radius:var(--radius-card-sm) }
  .cards-3 .work-card.grouped::before, .cards-2 .work-card.grouped::before{ height:10rem }
  .cards-3 .work-card.grouped .work-bottom h3, .cards-2 .work-card.grouped .work-bottom h3{ font-size:var(--text-20) }
  /* Core Modules 카드: 이미지 영역·타이틀·태그 축소 */
  .cm-cards .work-card.grouped::before{ height:10rem; margin:-1.25rem -1.25rem 1.25rem }
  .cm-cards .work-card.grouped{ padding:1.25rem; border-radius:var(--radius-card-sm) }
  .cm-cards .work-bottom h3{ font-size:var(--text-20) }
  .cm-cards .tag{ font-size:var(--text-14); padding:.5rem .875rem }
}
/* Core Modules: 좌측 타이틀 sticky + 우측 카드 세로 스크롤 */
.cm-grid{ display:grid; grid-template-columns:1fr; gap:2.5rem }
@media (max-width:639px){ .cm-grid{ gap:0 } }
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
/* cm-sm 변형(broof Core Features): 이미지 영역·카드 최소높이 축소(텍스트 짧아 아래 빈공간 방지) */
.cm-cards.cm-sm .work-card.grouped::before{ height:16rem }
.cm-cards.cm-sm .work-card.grouped{ min-height:0 }
/* Core Modules(ParaSta) 이미지 영역: 앱 화면 중앙 정렬 — 그라 마스크 없이 이미지 그대로(페이드는 이미지 자체에서 처리) */
.cm-cards.core-mods .work-card.grouped::before{
  background-image:url('assets/body-app.avif'),
    radial-gradient(rgba(var(--ink-rgb),.06) 1px, transparent 1.5px);
  background-size:contain, 20px 20px;
  background-position:center, 0 0;
  background-repeat:no-repeat, repeat }
/* 로고 카드 그리드 (Trusted By) — 한 줄 4개 */
.logo-grid{ list-style:none; margin:2.5rem 0 0; padding:0; display:grid;
  grid-template-columns:repeat(12,minmax(0,1fr)); column-gap:var(--grid-gap); row-gap:var(--grid-gap) }
.logo-grid > li{ grid-column:span 3 }
@media (max-width:1023px){ .logo-grid > li{ grid-column:span 6 } }   /* 태블릿 2열 */
@media (max-width:479px){ .logo-grid > li{ grid-column:span 12 } }   /* 소형 모바일 1열 */
.logo-card{ display:flex; flex-direction:column; align-items:flex-start; min-height:6.5rem; height:100%; padding:1.5rem;
  border:1px solid rgba(var(--white-rgb),.1); border-radius:var(--radius-card-sm);
  background:var(--ink); font-size:var(--text-18); font-weight:500; color:rgba(var(--white-rgb),.85);
  transition:transform .35s cubic-bezier(.2,.8,.2,1), background .35s ease, color .35s ease, border-color .35s ease }
.logo-card .logo-ico{ display:block; width:3.5rem; height:3.5rem; margin-bottom:2rem;
  border-radius:var(--radius-card-sm); background:rgba(var(--white-rgb),.08); transition:background .35s ease }
.logo-card .logo-ico img{ width:100%; height:100%; object-fit:contain; display:block }
@media (hover:hover){
  .logo-card:hover{ background:var(--brand); border-color:transparent; color:var(--white); transform:scale(1.03) }
  .logo-card:hover .logo-ico{ background:rgba(255,255,255,.35) } }
@media (max-width:1023px){ .logo-grid > li{ grid-column:span 4 } }
@media (max-width:639px){ .logo-grid > li{ grid-column:span 6 } }
/* Partners 2단 카드: 좌 금융권 / 우 퍼블릭·멀티체인 */
.pn-grid{ display:grid; grid-template-columns:1fr; gap:1.5rem; align-items:stretch }
@media (min-width:900px){ .pn-grid{ grid-template-columns:repeat(2,1fr); column-gap:var(--grid-gap) } }
.pn-card{ background:var(--ink); color:var(--white); border-radius:var(--radius-card); padding:2.5rem;
  box-shadow:0 0 0 1px rgba(var(--white-rgb),.05); transition:transform .35s cubic-bezier(.2,.8,.2,1) }
@media (hover:hover){ .pn-card:hover{ transform:scale(1.03) } }  /* 다크카드 공통 호버 */
/* 모바일: 좌우는 컴팩트, 위아래는 여유 있게 */
@media (max-width:639px){
  .pn-card{ padding:2.5rem 1.5rem; border-radius:var(--radius-card-sm) }
  .pn-list li{ padding:1.25rem } }
.pn-head{ margin-bottom:1.5rem }
/* 키커: Advantages 다크카드 보라 키커와 동일 스타일 (타이틀 위) */
.pn-kick{ font-size:var(--text-14); letter-spacing:.025em; color:var(--purple-300); font-weight:600; margin-bottom:.875rem }
/* Use Cases 캐러셀: 다크카드 1장 + 좌우 화살표 (레퍼 px-uc 구조 이식) */
.uc-carousel{ display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); column-gap:var(--grid-gap); align-items:center }
.uc-prev{ grid-column:1; justify-self:start }
.uc-slides{ grid-column:3 / 11 }
.uc-next{ grid-column:12; justify-self:end }
/* PC: 화살표 = 그리드 1칸 폭 (minmax(0,1fr) 트랙이라 밀림 없음) */
@media (min-width:1024px){ .uc-carousel .uc-arrow{ width:100%; justify-self:stretch } }

.uc-arrow{ width:3.5rem; aspect-ratio:1/1; height:auto; border-radius:var(--radius-pill); border:1px solid var(--line);
  display:grid; place-items:center; color:rgba(var(--ink-rgb),.6); background:var(--white);
  transition:background .25s ease, color .25s ease, transform .25s }  /* 1칸 폭 원형 */
.uc-arrow svg{ width:1.75rem; height:1.75rem }
@media (hover:hover){ .uc-arrow:hover{ background:var(--accent); border-color:transparent; color:var(--white); transform:scale(1.06) } }
/* 슬라이드를 그리드 1칸에 겹쳐 쌓아 컨테이너 높이 = 가장 긴 슬라이드 (전환 시 높이 안 튐) */
.uc-slides{ display:grid }
.uc-slide{ grid-area:1 / 1; position:relative; opacity:0; visibility:hidden; transition:opacity .4s ease, transform .35s cubic-bezier(.2,.8,.2,1);
  background:color-mix(in srgb, var(--ink) 6%, var(--white)); color:var(--ink); border-radius:var(--radius-card); padding:3rem;
  display:flex; flex-direction:column }
.uc-slide.is-active{ opacity:1; visibility:visible;
  will-change:transform; backface-visibility:hidden }  /* GPU 레이어 고정: 스케일 종료 시 텍스트 재래스터 스냅(덜컹) 방지 */
@media (hover:hover){ .uc-slide.is-active:hover{ transform:scale(1.02) } }  /* 호버 시 카드 확대 */
.uc-thumb{ width:5rem; height:5rem; border-radius:var(--radius-card-sm); background:rgba(var(--ink-rgb),.07); margin-bottom:1.5rem }
/* uc-tall 변형(broof): 이미지↔텍스트 간격 확대로 카드 키움 */
.uc-carousel.uc-tall .uc-thumb{ margin-bottom:4rem }
/* uc-lg 변형(금융): 본문 한 단계 업 + 라벨 플래그 행 구조 */
.uc-carousel.uc-lg .uc-slide > p{ font-size:var(--text-20) }
.uc-carousel.uc-lg .uc-slide h3{ margin-bottom:1rem }  /* 타이틀↔플래그 행 간격 */
.uc-rows{ display:flex; flex-direction:column; gap:.6rem }  /* 상단 정렬 + 컨테이너는 최장 슬라이드에 고정 */
.uc-row{ display:flex; align-items:center; gap:.75rem; font-size:var(--text-20);
  color:rgba(var(--ink-rgb),.6); line-height:var(--leading-body); word-break:keep-all }
.uc-flag{ flex:none; display:inline-flex; align-items:center; padding:.375rem .875rem;
  background:rgba(var(--ink-rgb),.07); border-radius:var(--radius-pill);
  font-size:var(--text-16); font-weight:600; color:rgba(var(--ink-rgb),.45) }  /* 그레이 필 + 연그레이 텍스트 */
.uc-title{ display:flex; align-items:center; gap:.75rem; flex-wrap:wrap; margin-bottom:.75rem }   /* 타이틀 + 플래그 한 행 */
.uc-num{ position:absolute; right:3rem; bottom:2.25rem; font-size:var(--text-14); font-weight:600; letter-spacing:.04em; color:rgba(var(--ink-rgb),.3); font-variant-numeric:tabular-nums }   /* 카드 우하단 넘버링 */
.uc-num b{ color:var(--ink); font-weight:700 }   /* 현재 번호 진한색 */
@media (max-width:639px){ .uc-row{ flex-direction:column; align-items:flex-start; gap:.375rem } }
.uc-thumb video, .uc-thumb img{ width:100%; height:100%; object-fit:cover; display:block; border-radius:inherit }
.uc-slide h3{ font-size:var(--text-24); font-weight:500; letter-spacing:-.01em; margin-bottom:0; color:var(--ink) }
@media (min-width:640px){ .uc-slide h3{ font-size:var(--text-30) } }
.uc-slide > p{ font-size:var(--text-18); color:rgba(var(--ink-rgb),.6); line-height:var(--leading-body); word-break:keep-all }
.uc-testimonial{ margin-top:2.5rem; padding-top:2rem; border-top:1px solid rgba(var(--ink-rgb),.12);
  display:flex; align-items:center; gap:1rem }
.uc-avatar{ width:3rem; height:3rem; border-radius:var(--radius-pill); background:rgba(var(--ink-rgb),.1); flex:none; overflow:hidden }
.uc-avatar video, .uc-avatar img{ width:100%; height:100%; object-fit:cover; display:block }
.uc-quote{ font-size:var(--text-20); font-weight:500; color:rgba(var(--ink-rgb),.85) }
.uc-name{ margin-top:.25rem; font-size:var(--text-16); font-weight:600; color:var(--purple-500) }
/* Use Cases 탭바(parasta) — 캐러셀 위 카테고리 전환 */
.uc-tabbar{ display:flex; justify-content:center; gap:.5rem; margin-bottom:var(--space-24) }
.uc-tabbtn{ padding:.625rem 1.25rem; border-radius:var(--radius-pill); border:1px solid var(--line); background:var(--white); color:rgba(var(--ink-rgb),.55); font-size:var(--text-16); font-weight:500; cursor:pointer; transition:background .25s ease, color .25s ease, border-color .25s ease }
@media (hover:hover){ .uc-tabbtn:hover{ color:var(--ink) } }
.uc-tabbtn.is-active{ background:var(--ink); border-color:transparent; color:var(--white) }
.uc-tabpanel{ display:none }
.uc-tabpanel.is-active{ display:block }
/* ParaSta Use Cases 카드 크게 (탭 캐러셀 전용) — 높이만 키움, 폭은 기본(3/11) */
.uc-tabpanel .uc-slide{ min-height:26rem; padding:3.5rem }
.uc-tabsub{ text-align:center; font-size:var(--text-16); color:rgba(var(--ink-rgb),.5); margin-bottom:var(--space-32) }
.uc-tabnote{ text-align:center; font-size:var(--text-16); color:rgba(var(--ink-rgb),.6); line-height:var(--leading-body); margin-top:var(--space-32) }
/* Broof Applied Cases — 좌측 인증서 풀영역 + 우측 글·후기(PortX 포멧) */
.bc-cases .uc-slide{ display:grid; grid-template-columns:minmax(0,42%) 1fr; gap:0; align-items:stretch; padding:0; overflow:hidden }   /* 패딩 0 → 인증서 full-bleed, overflow로 카드 라운드에 맞춰 클립 */
.bc-cert{ background:color-mix(in srgb, var(--ink) 12%, var(--white)); display:grid; place-items:center; min-height:30rem }
.bc-cert img{ width:100%; height:100%; object-fit:cover; display:block }
.bc-body{ display:flex; flex-direction:column; justify-content:flex-start; padding:var(--space-48) }   /* 텍스트만 패딩 */
.bc-cases .bc-body h3{ margin-bottom:var(--space-12) }
.bc-cases .bc-body > p{ font-size:var(--text-18); color:rgba(var(--ink-rgb),.6); line-height:var(--leading-body); word-break:keep-all }
.bc-cases .uc-testimonial{ margin-top:auto }   /* 후기를 하단 고정 → 슬라이드마다 위치 동일 */
/* 좌우 폭 0.5칸 더 차지 — 24분할 그리드(데스크톱). 화살표는 공통(width:100% stretch) 유지 */
@media (min-width:1024px){
  .bc-cases.uc-carousel{ grid-template-columns:repeat(24, minmax(0,1fr)) }
  .bc-cases .uc-prev{ grid-column:1 / 3 }
  .bc-cases .uc-slides{ grid-column:4 / 22 }
  .bc-cases .uc-next{ grid-column:23 / 25 }
}
@media (max-width:767px){ .bc-cases .uc-slide{ grid-template-columns:1fr; gap:0 } .bc-cert{ min-height:16rem } }
/* 탭(640~1023): 카드 패딩을 위 grouped 카드(2rem)와 통일 — 하단은 유지 */
@media (min-width:640px) and (max-width:1023px){ .uc-slide{ padding:2rem 2rem 3rem } }
.uc-dots{ display:none }
@media (max-width:639px){
  .uc-carousel{ display:flex; flex-wrap:wrap; justify-content:center; gap:1.25rem 1rem }
  .uc-slide{ padding:1.5rem 1.5rem 1.875rem; border-radius:var(--radius-card-sm) }  /* 하단 30px */
  .uc-slides{ flex:0 0 100%; order:0; touch-action:pan-y }
  .uc-prev, .uc-next{ display:none }
  .uc-dots{ display:flex; order:1; gap:.5rem; justify-content:center; flex-basis:100% }
  .uc-dot{ width:.5rem; height:.5rem; border-radius:var(--radius-pill); background:rgba(var(--ink-rgb),.18);
    transition:background .25s, transform .25s }
  .uc-dot.is-active{ background:var(--accent); transform:scale(1.25) }
  /* 모바일 카드 폰트: 다른 카드 규격과 통일 (타이틀 20 / 본문 16) */
  .uc-slide h3{ font-size:var(--text-20) }
  .uc-slide > p{ font-size:var(--text-16) }
  .uc-quote{ font-size:var(--text-16) }
  .uc-name{ font-size:var(--text-14) }
  .uc-thumb{ width:4rem; height:4rem; margin-bottom:1.25rem }
  .uc-slide h3{ margin-bottom:.5rem }
  .uc-testimonial{ margin-top:1.75rem; padding-top:1.5rem; gap:.75rem }
  .uc-avatar{ width:2.5rem; height:2.5rem } }
/* 컴팩트 아이콘 카드 (icon_card) — 아이콘·타이틀·설명 */
.ico-card{ background:var(--ink); color:var(--white); border-radius:var(--radius-card-sm);
  padding:2rem; height:100%; box-shadow:0 0 0 1px rgba(var(--white-rgb),.05);
  transition:transform .35s cubic-bezier(.2,.8,.2,1) }
@media (hover:hover){ .ico-card:hover{ transform:scale(1.03) } }
.ico-card .ic{ display:block; width:1.75rem; height:1.75rem; margin-bottom:3.5rem; color:var(--white) }
.ico-card .ic svg{ width:100%; height:100% }
.ico-card h3{ font-size:var(--text-20); font-weight:500; letter-spacing:-.01em; margin-bottom:.75rem; line-height:var(--leading-heading) }
.ico-card p{ font-size:var(--text-16); color:rgba(var(--white-rgb),.55); line-height:var(--leading-body); word-break:keep-all }
.cards-2 > li:has(.ico-card), .cards-3 > li:has(.ico-card){ display:flex }
.cards-2 > li > .ico-card, .cards-3 > li > .ico-card{ flex:1 1 auto; min-width:0 }
@media (max-width:639px){ .ico-card{ padding:1.5rem } .ico-card .ic{ margin-bottom:2.5rem } }
.ex-card{ padding:1.5rem; transition:transform .35s cubic-bezier(.2,.8,.2,1), background .35s ease, color .35s ease }
@media (hover:hover){
  .ex-card[style*="--brand"]:hover{ background:var(--brand); color:var(--brand-txt) }
  .ex-card[style*="--brand"]:hover .ex-ico{ background:rgba(255,255,255,.4) } }
.ex-card .ex-ico{ display:block; width:3.5rem; height:3.5rem; margin-bottom:2rem; background:rgba(var(--white-rgb),.08) }
/* 거래소 로고 카드 — 논호버: 남색+연보라 로고(mask)+흰 이름 / 호버: 흰 라인카드+총천연색 로고(img)+회색 이름, 살짝 커짐 */
.ex-card:has(.ex-ico.ex-logo){ border:1px solid transparent }   /* 호버 전환용 투명 보더 */
.ex-card .ex-ico.ex-logo{ position:relative; background:transparent; padding:0 }
.ex-card .ex-ico.ex-logo::before{ content:''; position:absolute; inset:0; background:var(--purple-300);
  -webkit-mask:var(--logo) center/contain no-repeat; mask:var(--logo) center/contain no-repeat; transition:opacity .35s ease }
.ex-card .ex-ico.ex-logo img{ position:relative; width:100%; height:100%; display:block; opacity:0; transition:opacity .35s ease }
@media (hover:hover){
  .ex-card:has(.ex-ico.ex-logo):hover{ background:var(--white); border-color:var(--line); color:var(--ink); transform:scale(1.03) }
  .ex-card:has(.ex-ico.ex-logo):hover h3{ color:rgba(var(--ink-rgb),.4); font-weight:500 }
  .ex-card:has(.ex-ico.ex-logo):hover .ex-ico.ex-logo{ background:transparent }   /* 옛 936 룰의 호버 흰 원 제거 */
  .ex-card:has(.ex-ico.ex-logo):hover .ex-ico.ex-logo::before{ opacity:0 }
  .ex-card:has(.ex-ico.ex-logo):hover .ex-ico.ex-logo img{ opacity:1 } }
.ex-card h3{ margin-bottom:0 }
.ex-card .ex-num{ display:block; font-size:var(--text-14); font-weight:500; color:rgba(var(--white-rgb),.5); margin-bottom:.5rem }  /* 기능 카드 번호 */
.ex-card h3 + p{ margin-top:.75rem; font-size:var(--text-18) }  /* 서브카피 달릴 때만 간격 + 한 단계 업 */

/* DID 신뢰 도식 (Platform): VISION식 다크 패널 + 원 3개 + 점선·닷 커넥터 + MyID 블록체인 인프라 바 */
.did-hub{ margin-top:var(--space-32); margin-bottom:var(--space-48); background:var(--ink); border-radius:var(--radius-card); padding:3rem 1.5rem; color:var(--white) }
@media (min-width:640px){ .did-hub{ padding:3.5rem 3rem } }
@media (min-width:1024px){ .did-hub{ padding:4.5rem 4.5rem } }
/* did-hub 헤더(sec_head) 타이포·간격 = About VISION 패널과 동일 */
.did-hub .eyebrow{ color:rgba(var(--white-rgb),.9) }
.did-hub .eyebrow::before, .did-hub .eyebrow::after{ color:rgba(var(--white-rgb),.4) }
.did-hub .sec-h2{ color:var(--white); font-size:var(--text-30); font-weight:500; letter-spacing:-.01em }
@media (min-width:768px){ .did-hub .sec-h2{ font-size:var(--text-36) } }
.did-hub .phero-lead, .did-hub .sec-lead{ color:rgba(var(--white-rgb),.68); font-size:var(--text-20) }
@media (max-width:1023px){ .did-hub .phero-lead, .did-hub .sec-lead{ font-size:var(--text-18) } }
.did-ring{ display:flex; align-items:center; justify-content:center; margin-top:5.5rem }
.did-node{ flex:0 0 auto; width:min(30%, 15rem); aspect-ratio:1; border-radius:50%; background:var(--purple-400);
  display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:var(--space-24); gap:.4rem }
.did-node .did-role{ font-size:var(--text-14); font-weight:600; letter-spacing:.05em; text-transform:uppercase; color:rgba(var(--white-rgb),.85) }
.did-node b{ font-size:var(--text-20); font-weight:600; color:var(--white) }
.did-node .did-sub{ font-size:var(--text-14); color:rgba(var(--white-rgb),.72); line-height:var(--leading-body); max-width:11rem }
.did-node.is-core{ width:min(34%, 17rem); background:var(--white) }
.did-node.is-core .did-role{ color:var(--purple-500) }
.did-node.is-core b{ color:var(--purple-500); font-size:var(--text-24) }
.did-node.is-core .did-sub{ color:rgba(var(--ink-rgb),.6) }
.did-link{ flex:1 1 0; align-self:center; position:relative; height:2.25rem; display:flex; align-items:center; justify-content:center }
.did-link::before{ content:''; position:absolute; left:0; right:0; top:50%; border-top:1.5px dashed rgba(var(--white-rgb),.28) }
.did-link::after{ content:''; position:absolute; left:50%; top:50%; width:.5rem; height:.5rem; border-radius:50%; background:rgba(var(--white-rgb),.5); transform:translate(-50%,-50%) }
.did-link span{ position:absolute; bottom:calc(50% + .5rem); font-size:var(--text-14); color:rgba(var(--white-rgb),.65); white-space:nowrap }
.did-infra{ margin-top:var(--space-40); border:1px solid rgba(var(--white-rgb),.15); border-radius:var(--radius-card-sm); padding:var(--space-24); text-align:center }
.did-infra-t{ font-size:var(--text-16); font-weight:700; letter-spacing:.04em; color:var(--purple-300); margin-bottom:.5rem }
.did-infra p{ font-size:var(--text-14); color:rgba(var(--white-rgb),.7); line-height:var(--leading-body) }
@media (max-width:767px){
  .did-hub{ padding:var(--space-32) var(--space-24) }
  .did-ring{ flex-direction:column }
  .did-node, .did-node.is-core{ width:min(100%, 13rem) }
  .did-link{ flex:none; width:auto; height:2.5rem }
  .did-link::before{ left:50%; right:auto; top:0; bottom:0; border-top:none; border-left:1.5px dashed rgba(var(--white-rgb),.28) }
  .did-link span{ bottom:auto; left:calc(50% + .75rem); white-space:nowrap } }
/* ex-card 그레이 변형: 라이트 그레이 채움 + 잉크 텍스트 (호버 스케일만 유지) */
.ex-card.ex-gray{ background:color-mix(in srgb, var(--ink) 6%, var(--white)); color:var(--ink); box-shadow:none }
.ex-card.ex-gray h3{ color:var(--ink) }
.ex-card.ex-gray p{ color:rgba(var(--ink-rgb),.6) }
.ex-card.ex-gray .ex-ico{ background:rgba(var(--ink-rgb),.06) }
/* 거래소 카드: 컴팩트라 모바일도 2열, 태블릿 3열 */
.cards-3:has(.ex-card){ grid-template-columns:repeat(2,minmax(0,1fr)); gap:1rem }
@media (min-width:640px){ .cards-3:has(.ex-card){ grid-template-columns:repeat(3,minmax(0,1fr)); gap:1.5rem } }
@media (max-width:479px){ .cards-3:has(.ex-card){ grid-template-columns:1fr } }
@media (max-width:639px){ .ex-card .ex-ico{ margin-bottom:2rem } }
/* 원형 아이콘 + 라벨 행 (거래소·통화 등) */
.ex-rows{ display:flex; flex-direction:column; gap:3rem }  /* 행 간 = 아이템 간과 동일 토큰 */
.ex-row{ display:flex; flex-wrap:wrap; justify-content:center; gap:3rem; align-items:center }
.ex-item{ display:flex; align-items:center; gap:.75rem }
.ex-ico{ width:2.75rem; height:2.75rem; border-radius:var(--radius-pill); overflow:hidden; flex:none;
  background:color-mix(in srgb, var(--ink) 6%, var(--white)) }
.ex-ico img{ width:100%; height:100%; object-fit:cover; display:block }
.ex-name{ font-size:var(--text-16); font-weight:500; color:var(--ink) }
@media (max-width:639px){ .ex-rows{ gap:1.75rem } .ex-row{ gap:1.75rem } .ex-ico{ width:2.25rem; height:2.25rem } }
/* 파트너 로고 마퀴 */
.pt-marquee{ overflow:hidden; margin:0 0 3.5rem;
  -webkit-mask-image:linear-gradient(to right, transparent, #000 10%, #000 90%, transparent);
  mask-image:linear-gradient(to right, transparent, #000 10%, #000 90%, transparent) }
.pt-track{ display:flex; width:max-content; animation:ptScroll 32s linear infinite }
.pt-set{ display:flex; align-items:center; gap:0; padding-right:0 }
.pt-set img{ height:7.5rem; width:auto; flex:none }  /* ≈120px, 로고 여백만으로 간격 (svg 원본 컬러) */
body.parasta .pt-set img{ height:5rem }   /* parasta 마퀴 로고 축소(120→80px) */
@keyframes ptScroll{ to{ transform:translateX(-50%) } }
@media (max-width:639px){ .pt-set img{ height:5.5rem } }
/* 인증·수상 마퀴: 로고(위) + 텍스트(아래) 아이템 순환 */
.cert-track{ animation-duration:34s }
.cert-item{ display:flex; flex-direction:column; align-items:center; gap:.375rem; flex:none; padding:0 2.5rem; text-align:center }
.cert-logo{ width:3.75rem; height:3.75rem; border-radius:var(--radius-pill); background:rgba(var(--ink-rgb),.06); flex:none }
.cert-label{ font-size:var(--text-18); font-weight:500; color:rgba(var(--ink-rgb),.7); white-space:nowrap }
@media (max-width:639px){ .cert-item{ padding:0 1.5rem } .cert-logo{ width:3rem; height:3rem } }
/* How to Adopt 비교: 두 경로를 위아래로 쌓고 각 경로는 가로 타임라인 — 트랙 길이로 단계·시간 대비 */
.adopt-compare{ display:flex; flex-direction:column; gap:var(--space-64) }
.ac-row{ display:grid; grid-template-columns:repeat(var(--grid-cols),1fr); gap:var(--grid-gap); align-items:center }
@media (max-width:639px){ .ac-row{ display:flex; flex-direction:column; align-items:flex-start; gap:1.25rem } }
.ac-meta{ grid-column:1 / 4 }
.ac-meta h3{ font-size:var(--text-24); font-weight:500; letter-spacing:-.01em; line-height:var(--leading-heading) }
.ac-time{ margin-top:.5rem; display:inline-flex; align-items:center; padding:.375rem .875rem; border-radius:var(--radius-pill);
  background:rgba(var(--ink-rgb),.07); font-size:var(--text-16); font-weight:600; color:rgba(var(--ink-rgb),.45) }
.ac-row.ac-hi .ac-time{ background:color-mix(in srgb, var(--accent) 12%, var(--white)); color:var(--accent) }
.ac-track{ grid-column:4 / 13; position:relative; display:flex; justify-content:flex-start; width:100%; align-items:flex-start }
.ac-track::before{ content:''; position:absolute; left:10%; top:6px; height:2px; background:var(--gray-100) }
.ac-track.slow::before{ right:10% }   /* 첫 노드(10%) ~ 5번째 노드(90%) */
.ac-track.fast::before{ right:50% }   /* 첫 노드(10%) ~ 3번째 노드(50%) — 시작 x는 slow와 동일 */
.ac-row.ac-hi .ac-track::before{ background:color-mix(in srgb, var(--accent) 28%, var(--white)) }
.ac-step{ position:relative; flex:0 0 20%; display:flex; flex-direction:column; align-items:center; text-align:center; z-index:1 }
.ac-dot{ width:13px; height:13px; border-radius:var(--radius-pill); background:var(--gray-300); border:2px solid var(--white);
  transition:transform .25s cubic-bezier(.2,.8,.2,1), box-shadow .25s ease }
.ac-row.ac-hi .ac-dot{ background:var(--accent) }
.ac-lbl{ margin-top:.75rem; font-size:var(--text-16); line-height:1.35; color:rgba(var(--ink-rgb),.7); transition:color .25s ease }
@media (hover:hover){
  .ac-step:hover .ac-dot{ transform:scale(1.5); box-shadow:0 0 0 6px rgba(var(--ink-rgb),.05) }
  .ac-row.ac-hi .ac-step:hover .ac-dot{ box-shadow:0 0 0 6px color-mix(in srgb, var(--accent) 12%, transparent) }
  .ac-step:hover .ac-lbl{ color:var(--ink) }
}
/* 의장사 알약 */
.chair-badge{ display:inline-flex; align-items:center; gap:.875rem; padding:.75rem 1.5rem;
  border:1px solid rgba(var(--purple-300-rgb),.5); border-radius:var(--radius-pill);
  font-size:var(--text-16); font-weight:600; color:var(--ink) }
.chair-badge .chair-div{ width:1px; height:1rem; background:rgba(var(--ink-rgb),.2); flex:none }
/* 얼라이언스 마퀴: 타이틀(좌) + 로고 마퀴(우) */
.ally-marquee-wrap{ display:block; margin-top:3.5rem }   /* 시안 D: 라벨 위 / 마퀴 아래 세로 배치 (옛 2열 그리드 폐기) */
.ally-num{ display:block; font-size:var(--text-28); font-weight:700; color:var(--ink); line-height:1 }
.ally-cap{ display:block; font-size:var(--text-16); color:rgba(var(--ink-rgb),.55); margin-top:.375rem }
.ally-logos, .ally-marquee-wrap .pt-marquee{ margin:0 }
.ally-logos .pt-track{ animation-duration:42s }   /* 인증수상 마퀴와 동일 속도 */
.ally-logos:hover .pt-track{ animation-play-state:paused }   /* 호버 시 정지 */
/* 시안 D 마퀴 문법: 좌우 페이드 */
.ally-logos{ padding-block:var(--space-24);
  -webkit-mask-image:linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
  mask-image:linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent) }
.ally-logos .pt-set{ gap:0; padding-right:0 }
.ally-logos .pt-set img{ height:5.25rem }
@media (max-width:639px){ .ally-logos .pt-set img{ height:3.5rem } }
/* History 타임라인 (C안): 좌측 레일 + 노드 + 큰 연도 + 그레이 카드 */
.ht-list{ list-style:none; margin:0; padding:0 0 0 2rem; position:relative }
.ht-list::before{ content:''; position:absolute; left:5px; top:.5rem; bottom:.5rem; width:2px; background:var(--gray-100) }
.ht-item{ position:relative; display:grid; grid-template-columns:5.5rem 1fr; gap:1.75rem; align-items:center; padding:1.25rem 0 }
.ht-node{ position:absolute; left:-2rem; top:50%; transform:translateY(-50%); width:11px; height:11px; border-radius:50%;
  background:var(--purple-500); margin-left:.5px }  /* 레일(5~7px, 2px선) 중심 정렬: -2rem+5.5px+.5px = 레일 센터 */
.ht-yr{ font-size:var(--text-28); font-weight:700; letter-spacing:-.02em; color:var(--ink) }
.ht-card{ background:color-mix(in srgb, var(--ink) 6%, var(--white)); border-radius:var(--radius-card-sm); padding:1.3rem 1.6rem }
.ht-card p{ font-size:var(--text-18); line-height:var(--leading-body); color:rgba(var(--ink-rgb),.78); margin:0 }
@media (max-width:639px){ .ht-item{ grid-template-columns:1fr; gap:.5rem } }
/* 타이틀은 다크카드(.work-bottom h3)와 동일 토큰 */
.pn-head h3{ font-size:var(--text-24); font-weight:500; letter-spacing:-.01em }
@media (min-width:640px){ .pn-head h3{ font-size:var(--text-30) } }
/* 사례: 디바이더 대신 인셋 박스(우리 그레이 인셋 언어의 다크 버전) */
.pn-list{ display:flex; flex-direction:column; gap:1rem }
.pn-list li{ background:rgba(var(--white-rgb),.05); border-radius:var(--radius-card-sm); padding:1.5rem }
.pn-list h4{ font-size:var(--text-18); font-weight:600; letter-spacing:-.01em }
.pn-list p{ margin-top:.5rem; font-size:var(--text-16); color:rgba(var(--white-rgb),.55); line-height:var(--leading-body) }
.pn-note{ margin-top:1.5rem; font-size:var(--text-16); color:var(--purple-300); line-height:var(--leading-body); text-align:center }
/* 인증 3종: 타이틀 없이 하단 배치 — 이미지 영역 + 라벨, 디바이더 없음 */
.cert-row{ display:grid; grid-template-columns:repeat(3,1fr); column-gap:1rem; padding:5rem 0 }
@media (min-width:768px){ .cert-row{ column-gap:var(--grid-gap) } }
.cert-item{ display:flex; flex-direction:column; align-items:center; gap:1.5rem }
.cert-img{ width:100%; max-width:14rem; aspect-ratio:16/10; border-radius:var(--radius-card-sm);
  background:color-mix(in srgb, var(--ink) 6%, var(--white)) }
.cert-txt{ text-align:center; font-size:var(--text-14); font-weight:600; letter-spacing:-.01em; color:var(--ink) }
@media (min-width:768px){ .cert-txt{ font-size:var(--text-20) } }
@media (min-width:1024px){ .cert-txt{ font-size:var(--text-24) } }
/* Proven Core: 3개 스탯이라 데스크톱 3열 */
@media (min-width:1024px){ .stats-grid.pv-stats{ grid-template-columns:repeat(3,1fr) } }
/* 스탯 패널 보조: 숫자 앞뒤 작은 접두어/접미어(최대·TPS 등) · 다크 패널용 노트 */
.stat-num .sn-pre{ font-size:var(--text-24); font-weight:500; margin-right:.375rem }
.stat-num .sn-suf{ font-size:var(--text-24); font-weight:500 }
/* 문장형 스탯: 전체 동일 사이즈, 기본 스탯보다 토큰 2단계 다운 (48→36 / 60→40 / 72→48) */
.stat-num.sn-sm{ font-size:var(--text-36) }
@media (min-width:640px){ .stat-num.sn-sm{ font-size:var(--text-40) } }
@media (min-width:768px){ .stat-num.sn-sm{ font-size:var(--text-48) } }
/* 스탯 2x2 배치 (기본 4열 대신) — 숫자는 기본에서 토큰 1단계 다운 (48→40 / 60→48 / 72→60) */
@media (min-width:1024px){ .stats-grid.sg-2x2{ grid-template-columns:repeat(2,1fr) } }
.stats-grid.sg-2x2{ margin-top:var(--space-64); margin-bottom:var(--space-32) }  /* 타이틀↔그리드 여백 업(3.5→4rem) + 하단 마진 */
.sg-2x2 .stat-num{ font-size:var(--text-36); font-weight:700 }  /* 기본(600)보다 한 단계 볼드, 사이즈는 한 토큰 다운 */
@media (min-width:640px){ .sg-2x2 .stat-num{ font-size:var(--text-40) } }
@media (min-width:768px){ .sg-2x2 .stat-num{ font-size:var(--text-48) } }
.stats-panel .sec-note{ margin-top:3rem; color:rgba(var(--white-rgb),.45) }
.stats-panel .sec-note + .sec-note{ margin-top:1rem }
.stats-panel .sec-note strong{ font-weight:600; color:rgba(var(--white-rgb),.7) }
/* 라이트 텍스트 스탯: 모바일 1열 세로 스택, 768부터 3열 유지 */
@media (max-width:767px){ .stats-grid.pv-stats.on-light{ grid-template-columns:1fr; row-gap:2.5rem } }
@media (min-width:768px){ .stats-grid.pv-stats.on-light{ grid-template-columns:repeat(3,1fr) } }
/* 라이트 배경 스탯 (박스 없이 풀폭) */
.pv-stats.on-light{ margin-top:0 }
.pv-stats.on-light{ text-align:center; padding:5rem 0 }
.pv-stats.on-light li{ display:flex; flex-direction:column; align-items:center; gap:0 }
.pv-stats.on-light .stat-num{ color:var(--ink); font-size:var(--text-36) }
/* 768~1023: 3열 열폭 좁음(768서 208px) → 최장 문자열 한 줄 보장 위해 text-28 */
@media (min-width:768px) and (max-width:1023px){ .pv-stats.on-light .stat-num{ font-size:var(--text-28) } }
@media (min-width:1024px){ .pv-stats.on-light .stat-num{ font-size:var(--text-48) } }
.pv-stats.on-light .stat-num .pv-hl{ color:var(--purple-500) }
.pv-stats.on-light .stat-label{ color:rgba(var(--ink-rgb),.55) }
@media (min-width:1024px){ .pv-stats.on-light .stat-label{ font-size:var(--text-20) } }
.pv-stats.on-light .stat-kicker{ font-size:var(--text-14); font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:rgba(var(--ink-rgb),.4); margin-bottom:.75rem }   /* 스탯 상단 킥커(Users·Verifications) */
@media (min-width:768px){ .stats-grid.pv-stats.on-light.pv-2{ grid-template-columns:repeat(2,1fr) } }   /* 2개 스탯은 2열 */
/* Core Technology 행: 화살표(페이지 이동) 제거 + 제목 한 토큰 작게 */
.ct-rows .service-badge{ display:none }
.ct-rows .service-row h3{ font-size:var(--text-26) }
.ct-rows .service-desc{ display:block; font-size:var(--text-body); max-width:34rem; margin-right:5rem }
/* <1024: 행 리스트 본문을 타이틀 아래로 (사라지지 않게) — 전 서브페이지 공통 */
@media (max-width:1023px){
  .sec .service-row{ position:relative; padding-right:4.5rem; flex-wrap:wrap; row-gap:.5rem }
  .sec .service-badge{ position:absolute; right:1.25rem; top:50%; transform:translateY(-50%) }
  .sec .service-desc{ display:block; flex-basis:100%; max-width:none; margin:0 0 0 2.75rem }
  .sec .row-meta ~ .service-desc{ margin-left:0 } }
@media (min-width:640px) and (max-width:1023px){
  .sec .service-desc{ margin-left:4rem }
  .sec .row-meta ~ .service-desc{ margin-left:7.5rem } }
/* 모바일: meta(날짜) 행은 날짜 위·타이틀 아래 스택 */
@media (max-width:639px){
  .sec .service-row .row-meta{ flex-basis:100%; width:auto; margin-bottom:.125rem }
  .sec .row-sm h3{ font-size:var(--text-20) } }
.ct-rows .service-idx{ transition:color .25s ease }
.rows-meta-wide .service-idx{ width:4.5rem; white-space:nowrap }  /* 기간형 인덱스(4~6개월 등) 줄바꿈 방지 */
.service-row h3 .t-acc{ color:var(--accent); font-style:normal }  /* 행 타이틀 내 기간 강조 (보라) */
@media (hover:hover){ .ct-rows .service-row:hover .service-idx{ color:var(--purple-500); font-weight:600 } }
.work-quote{ margin-top:1.25rem; border-left:2px solid var(--purple-400); padding-left:1rem;
  font-size:var(--text-14); color:rgba(var(--white-rgb),.75); line-height:var(--leading-body) }
.work-quote cite{ display:block; margin-top:.5rem; font-style:normal; font-size:var(--text-14); color:rgba(var(--white-rgb),.45) }
.row-sm h3{ font-size:var(--text-18) !important }
@media (min-width:640px){ .row-sm h3{ font-size:var(--text-22) !important } }
.row-meta{ width:6.5rem; flex:none; font-size:var(--text-14); font-weight:500; text-transform:uppercase;
  letter-spacing:.05em; color:rgba(var(--ink-rgb),.4) }
/* ico-card / ex-card (PortX Supported Exchanges 스타일 이식) — 다크 카드 + 로고 원, 호버 시 브랜드컬러 */
.ico-card{ background:var(--ink); color:var(--white); border-radius:var(--radius-card-sm); padding:1.75rem;
  transition:transform .35s cubic-bezier(.2,.8,.2,1) }
@media (hover:hover){ .ico-card:hover{ transform:scale(1.03) } }
.ico-card h3{ font-size:var(--text-20); font-weight:500; letter-spacing:-.01em; margin-bottom:.75rem; line-height:var(--leading-heading) }
.cards-2 > li:has(.ico-card), .cards-3 > li:has(.ico-card){ display:flex }
.cards-2 > li > .ico-card, .cards-3 > li > .ico-card{ flex:1 1 auto; min-width:0 }
@media (max-width:639px){ .ico-card{ padding:1.5rem } }
.ex-card{ padding:1.5rem; transition:transform .35s cubic-bezier(.2,.8,.2,1), background .35s ease, color .35s ease }
@media (hover:hover){ .ex-card[style*="--brand"]:hover{ background:var(--brand); color:var(--brand-txt) }
  .ex-card[style*="--brand"]:hover .ex-ico{ background:rgba(255,255,255,.4) } }
.ex-card .ex-ico{ display:block; width:3.5rem; height:3.5rem; border-radius:var(--radius-pill); margin-bottom:2rem;
  background:rgba(var(--white-rgb),.08); transition:background .35s ease }
.ex-card h3{ margin-bottom:0 }
.cards-3:has(.ex-card){ grid-template-columns:repeat(2,minmax(0,1fr)); gap:1rem }
@media (min-width:640px){ .cards-3:has(.ex-card){ grid-template-columns:repeat(3,minmax(0,1fr)); gap:1.5rem } }
@media (max-width:479px){ .cards-3:has(.ex-card){ grid-template-columns:1fr } }
.light-card{ border:1px solid var(--line); background:rgba(var(--surface-rgb),.5); border-radius:var(--radius-card-sm); padding:1.75rem }
.light-card h3{ font-size:var(--text-18); font-weight:600; letter-spacing:-.01em; margin-bottom:.625rem; line-height:var(--leading-heading) }
.light-card p{ font-size:var(--text-16); line-height:var(--leading-body); color:rgba(var(--ink-rgb),.6) }
.light-card .cap{ font-size:var(--text-14); font-weight:500; text-transform:uppercase; letter-spacing:.05em;
  color:var(--accent); margin-bottom:.75rem; display:block }
body.company .about-grid{ padding-bottom:var(--space-32) }   /* 지도와의 간격 축소 */
.addr-list{ display:flex; flex-direction:column; gap:var(--gap-unit) }
@media (min-width:1024px){
  .about-grid{ grid-template-columns:repeat(var(--grid-cols),minmax(0,1fr)); gap:var(--grid-gap) }
  .about-globe{ grid-column:1 / 6 }
  .about-right{ grid-column:6 / 13 }   /* 어드레스: 6번 칼럼부터 */
}
.addr-list .k{ font-size:var(--text-16); font-weight:500; text-transform:uppercase; letter-spacing:.05em; color:rgba(var(--ink-rgb),.45) }   /* 14→16 */
.addr-list .v{ margin-top:.25rem; font-size:var(--text-body); line-height:var(--leading-body) }   /* 본문 토큰 */
.legal-body{ max-width:48rem }
.legal-body h3{ font-size:var(--text-18); font-weight:600; margin:2.5rem 0 .75rem }
.legal-body h3:first-child{ margin-top:0 }
.legal-body p{ font-size:var(--text-16); line-height:var(--leading-body); color:rgba(var(--ink-rgb),.6) }
.legal-note{ display:inline-flex; align-items:center; gap:.5rem; margin-top:.375rem;
  border:1px solid var(--line); border-radius:var(--radius-pill); padding:.25rem .875rem;
  font-size:var(--text-14); color:rgba(var(--ink-rgb),.45) }
.num-card .n{ font-size:var(--text-40); font-weight:600; letter-spacing:-.02em; line-height:1.1; margin-bottom:.5rem }
.num-card .n small{ font-size:var(--text-20); font-weight:500 }
/* With/Without 좌우 비교 (Problem 문제→해결, PR#1 기획) — 좌: 라이트(지금·문제) / 우: 다크(도입 후·해결) */
.ww{ display:grid; grid-template-columns:1fr 1fr; gap:var(--grid-gap); align-items:stretch }
@media (max-width:767px){ .ww{ grid-template-columns:1fr } }
.ww-col{ border-radius:var(--radius-card); padding:var(--space-32) }
@media (min-width:1024px){ .ww-col{ padding:var(--space-40) } }
.ww-now{ background:color-mix(in srgb, var(--ink) 6%, var(--white)) }
.ww-after{ background:var(--ink); color:var(--white); box-shadow:0 0 0 1px rgba(var(--white-rgb),.05) }
.ww-col .ww-cap{ display:block; font-size:var(--text-14); font-weight:500; text-transform:uppercase; letter-spacing:.05em; margin-bottom:var(--space-12) }
.ww-now .ww-cap{ color:rgba(var(--ink-rgb),.45) }
.ww-after .ww-cap{ color:var(--purple-300) }
.ww-col .ww-t{ font-size:var(--text-24); font-weight:500; letter-spacing:-.01em; margin-bottom:var(--space-24); line-height:var(--leading-heading) }
.ww-after .ww-t{ color:var(--white) }
.ww-col ul{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column }
.ww-col li{ display:flex; gap:var(--space-12); padding-block:var(--space-16); align-items:flex-start }
.ww-now li + li{ border-top:1px solid var(--line) }
.ww-after li + li{ border-top:1px solid rgba(var(--white-rgb),.1) }
.ww-mk{ flex:none; font-weight:700; font-size:var(--text-16); line-height:var(--leading-heading); margin-top:.125rem }
.ww-now .ww-mk{ color:rgba(var(--ink-rgb),.3) }
.ww-after .ww-mk{ color:var(--purple-300) }
.ww-col li b{ display:block; font-size:var(--text-18); font-weight:600; letter-spacing:-.01em; margin-bottom:.375rem; line-height:var(--leading-heading) }
.ww-col li p{ font-size:var(--text-16); line-height:var(--leading-body); margin:0 }
.ww-now li p{ color:rgba(var(--ink-rgb),.6) }
.ww-after li p{ color:rgba(var(--white-rgb),.62) }
/* 증명서 Why Now 2컬럼: 좌 스탯박스(한 박스·3줄) / 우 (콘텐츠 대기) — cert 전용, 타 페이지 영향 없음 */
.cert-wn-duo{ display:grid; grid-template-columns:7fr 5fr; gap:var(--grid-gap); align-items:stretch }
@media (max-width:767px){ .cert-wn-duo{ grid-template-columns:1fr; row-gap:var(--space-48) } }
/* 좌측 차트: 우측 박스 높이에 맞춰 흰 패널까지 같이 늘림 + 노트를 하단 고정해 우측 출처와 y 정렬 (cert 전용) */
.cert-wn-duo > .colc{ height:100% }
.cert-wn-duo > .colc .colc-panel{ flex:1; display:flex; flex-direction:column; padding-bottom:var(--space-32) }
.cert-wn-duo > .colc .colc-panel .colc-plot{ margin-top:var(--space-24) }
.cert-wn-duo > .colc .colc-panel .sec-note{ margin-top:auto }
/* data Why Now 차트: 바 높이 살짝 축소(→ 우측 박스도 같이 줄어듦) + 바를 위로 + 주석 간격 확보 (data 전용) */
.wn-data > .colc{ --colc-h:9.5rem }
.wn-data > .colc .colc-panel .colc-plot{ margin-top:0 }
.wn-data > .colc .colc-panel .colc-labels{ margin-bottom:var(--space-40) }
.cert-statbox{ background:color-mix(in srgb, var(--ink) 6%, var(--white)); border:none; border-radius:var(--radius-card-sm);
  padding:var(--space-32); display:flex; flex-direction:column; justify-content:space-between; gap:var(--space-24) }
.cert-stats{ display:flex; flex-direction:column }
.cert-stat{ display:flex; flex-direction:column; gap:.35rem; padding:var(--space-24) 0 }
.cert-stat:first-child{ padding-top:0 }
.cert-stat:last-child{ padding-bottom:0 }
.cert-stat + .cert-stat{ border-top:1px solid var(--line) }
.cert-stat .csn{ font-size:var(--text-36); font-weight:600; letter-spacing:-.02em; line-height:1.05; color:var(--ink) }
.cert-stat .csn small{ font-size:inherit; font-weight:inherit; color:inherit; margin-left:.05em }
.cert-stat p{ font-size:var(--text-16); line-height:var(--leading-body); color:rgba(var(--ink-rgb),.6) }
.cert-src{ padding-top:var(--space-24); border-top:1px solid var(--line);
  font-size:var(--text-18); font-weight:400; line-height:var(--leading-body); color:var(--muted) }
/* 스탯박스 4지표 2x2 배치 (data 등에서 사용) */
.cert-stats.is-2x2{ display:grid; grid-template-columns:1fr 1fr; column-gap:var(--space-40) }
.cert-stats.is-2x2 .cert-stat{ border-top:none; padding:var(--space-24) 0 }
.cert-stats.is-2x2 .cert-stat:nth-child(-n+2){ padding-top:0 }
.cert-stats.is-2x2 .cert-stat:nth-child(n+3){ border-top:1px solid var(--line); padding-top:var(--space-40); padding-bottom:0 }
@media (max-width:479px){ .cert-stats.is-2x2{ grid-template-columns:1fr } }
/* 2x2 스탯박스: 하단정렬(출처=좌측 차트 출처와 같은 지점) + 그리드↔출처 gap을 키워 그리드를 위로 → 위쪽 여백 축소 */
.statbox-2x2{ justify-content:flex-end; gap:var(--space-32) }
.statbox-2x2 .cert-src{ border-top:none }
/* 발급 가능 증명: 12칼럼 그리드 정렬 — 아이템 3~12칸(10칸), 4칸 균등폭 + 균등 갭 (cert 전용, About 컴포넌트 유지) */
.cert-cred{ grid-template-columns:repeat(12,1fr); align-items:center }
.cert-cred > .ally-head{ grid-column:1 / span 2 }
.cert-cred > .pt-marquee{ grid-column:3 / span 10; overflow:visible; margin:0 }
.cert-cred .pt-track{ display:grid; grid-template-columns:repeat(4,1fr); gap:var(--grid-gap); width:100%; animation:none }
.cert-cred .cert-item{ padding:0 }
.cert-cred .cert-label{ white-space:normal; text-align:center }
@media (max-width:639px){
  .cert-cred{ grid-template-columns:1fr }
  .cert-cred > .ally-head, .cert-cred > .pt-marquee{ grid-column:auto }
  .cert-cred .pt-track{ grid-template-columns:repeat(2,1fr) }
}
/* 회색 채움 변형 (About Track Record 톤) — company 밖에서도 사용 */
.num-solid .num-card{ background:color-mix(in srgb, var(--ink) 6%, var(--white)); border:none }
.tag.on-light{ border-color:var(--line); color:var(--ink) }

/* ============ CONTENT-PORT ADDITIONS (우리 토큰 유지) ============ */
/* 비교표 */
/* Why ParaSta: 타이틀셋(4칼럼) 좌 / 표(8칼럼) 우 */
.why-grid{ display:flex; flex-direction:column; gap:2.5rem }
.why-table{ min-width:0 }
/* 섹션 직속 표(portx·myid): 셀 상하 패딩 확대 — 행이 여유 있게 */
.sec > .why-table table.cmp th, .sec > .why-table table.cmp td{ padding-top:1.75rem; padding-bottom:1.75rem }
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
table.cmp td{ color:rgba(var(--ink-rgb),.7); line-height:var(--leading-body); text-align:center; vertical-align:middle }
table.cmp td .mk{ display:block; margin:0 auto .125rem }
table.cmp td .mkv{ width:22px; height:22px }
table.cmp td .mkv circle{ stroke-width:.8 }
.why-legend .mkv circle{ stroke-width:1.4 }
table.cmp td .cell-txt{ display:block; font-size:var(--text-14) }
table.cmp td.hl{ font-weight:500; color:var(--ink) }
/* ParaSta 열: 호버 시 열 전체가 버튼처럼 함께 살짝 커짐(그림자 없음) — JS가 hl-hover 동기화 */
table.cmp th.hl, table.cmp td.hl{ position:relative; transition:transform .4s cubic-bezier(.2,.8,.2,1) }
table.cmp th.hl.hl-hover, table.cmp td.hl.hl-hover{ transform:scale(1.03); z-index:1 }
/* 가로만 확대: 세로 scale 시 셀 경계 틈·디바이더 실종 문제 원천 차단 */
/* 비교표 헤더 플래그 배지 */
.cmp-flag{ display:inline-block; margin-left:.5rem; padding:.25rem .625rem; border-radius:var(--radius-pill);
  background:rgba(var(--accent-rgb),.1); color:var(--accent); font-size:var(--text-14); font-weight:600; vertical-align:middle }
.cmp-flag.cmp-flag-gray{ background:rgba(var(--ink-rgb),.08); color:var(--c-body) }   /* 그레이 플래그 변형 */
.cmpt-btn .cmp-flag{ margin-left:.375rem; padding:.125rem .5rem }
.cmpt-btn.active .cmp-flag{ background:rgba(255,255,255,.22); color:var(--white) }
table.cmp .mk{ font-weight:700; margin-right:.375rem }
table.cmp .mk.on{ color:var(--accent) }
table.cmp .mk.mid{ color:rgba(var(--ink-rgb),.45) }
table.cmp .mk.off{ color:rgba(var(--ink-rgb),.3) }
/* ---- 비교표 모바일 탭(<768): 열 하나씩만 표시 ---- */
.cmp-tabs{ display:none }
@media (max-width:767px){
  .cmp-tabs{ display:grid; grid-template-columns:minmax(0,1fr) }
  .cmp-tabs ~ .cmp-wrap{ display:none }
  .cmpt-barwrap{ grid-row:1; grid-column:1; position:relative; margin-bottom:1rem }
  .cmpt-bar{ display:flex; gap:.5rem; overflow-x:auto; -webkit-overflow-scrolling:touch;
    padding-bottom:.5rem; scrollbar-width:none }
  .cmpt-bar::-webkit-scrollbar{ display:none }
  /* 좌우 화살표: 흰색 그라 마스크로 뒤를 가리고 그 위에 표시 */
  .cmpt-nav{ position:absolute; top:0; bottom:.5rem; width:3.5rem; z-index:2; display:flex; align-items:center;
    color:rgba(var(--ink-rgb),.55); opacity:0; pointer-events:none; transition:opacity .25s }
  .cmpt-nav.show{ opacity:1; pointer-events:auto }
  .cmpt-nav svg{ width:1rem; height:1rem; flex:none }
  .cmpt-nav.prev{ left:0; justify-content:flex-start;
    background:linear-gradient(to right, var(--white) 45%, transparent) }
  .cmpt-nav.next{ right:0; justify-content:flex-end;
    background:linear-gradient(to left, var(--white) 45%, transparent) }
  .cmpt-btn{ flex:none; padding:.625rem 1rem; border-radius:var(--radius-pill);
    border:1px solid var(--line); font-size:var(--text-14); font-weight:500;
    color:rgba(var(--ink-rgb),.55); background:var(--white); transition:all .25s }
  .cmpt-btn.active{ border-color:transparent; background:var(--ink); color:var(--white) }
  .cmpt-btn.is-hl.active{ background:var(--accent) }
  /* 패널은 같은 그리드 셀에 겹쳐 쌓아 높이 통일(가장 긴 패널 기준) */
  .cmpt-panel{ grid-row:2; grid-column:1; visibility:hidden;
    border-radius:var(--radius-card-sm); border:1px solid var(--line); padding:.25rem 1.25rem }
  .cmpt-panel.active{ visibility:visible }
  .cmpt-panel.is-hl{ border-color:transparent; background:color-mix(in srgb, var(--purple-300) 22%, var(--white)) }
  .cmpt-row{ display:flex; align-items:center; justify-content:space-between; gap:1rem;
    padding:1rem 0; border-bottom:1px solid var(--line) }
  .cmpt-panel.is-hl .cmpt-row{ border-bottom-color:rgba(var(--ink-rgb),.12) }
  .cmpt-row:last-child{ border-bottom:none }
  .cmpt-label{ flex:none; font-size:var(--text-14); font-weight:600; color:rgba(var(--ink-rgb),.65) }
  .cmpt-cell{ display:flex; align-items:center; gap:.5rem; text-align:right; font-size:var(--text-14);
    color:rgba(var(--ink-rgb),.7); line-height:var(--leading-body) }
  .cmpt-panel.is-hl .cmpt-cell{ color:var(--ink); font-weight:500 }
  .cmpt-cell .mk{ display:inline-flex; order:2; flex:none }
  .cmpt-cell .mkv{ width:18px; height:18px }
  .cmpt-cell .cell-txt{ order:1 }
  .cmpt-cell .mk.on{ color:var(--accent) }
  .cmpt-cell .mk.mid{ color:rgba(var(--ink-rgb),.45) }
  .cmpt-cell .mk.off{ color:rgba(var(--ink-rgb),.3) }
}
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
.sec-note{ margin-top:1.25rem; font-size:var(--text-14); color:rgba(var(--ink-rgb),.45); line-height:var(--leading-body); max-width:54rem }
/* 세로 막대 차트 (barc 세로 변형) — 값은 막대 위, 라벨은 베이스라인 아래 */
.colc{ --colc-h:11rem; display:flex; flex-direction:column;
  border:2px solid color-mix(in srgb, var(--ink) 6%, var(--white)); border-radius:var(--radius-card-sm); padding:var(--space-16) 0 0;
  background:color-mix(in srgb, var(--ink) 6%, var(--white)) }  /* 밴드 색 = num-solid 카드색. 상단 타이틀 밴드만 남기고 흰 패널이 꽉 채움 (위 16 = 아래 마진과 동일 → 밴드 중앙) */
.colc .barc-title{ padding:0 var(--space-32) }
.colc-panel{ background:var(--white); padding:var(--space-48) var(--space-32) var(--space-24);
  border-radius:var(--radius-control) var(--radius-control) calc(var(--radius-card-sm) - 1px) calc(var(--radius-card-sm) - 1px) }  /* 하단은 바깥 R-보더만큼 맞물림. 상단 여유 48 */
.colc-duo{ display:grid; grid-template-columns:1fr 1fr; gap:var(--grid-gap); align-items:start }
@media (max-width:767px){ .colc-duo{ grid-template-columns:1fr; row-gap:var(--space-48) } }
.colc .barc-title{ margin-bottom:var(--space-16); font-size:var(--text-18) }  /* 세로 차트 타이틀 한 단계 업 */
.colc-plot{ display:grid; align-items:end; gap:var(--grid-gap); border-bottom:1px solid var(--line) }
.colc-stack{ display:flex; flex-direction:column; align-items:center; justify-content:flex-end; gap:.625rem;
  transform-origin:bottom center; transition:transform .35s cubic-bezier(.2,.8,.2,1) }  /* 호버 스프링 (hs-scale과 동일) */
@media (hover:hover){
  .colc-stack:hover{ transform:scale(1.04) }
  .colc-stack:hover .colc-bar::after{ opacity:1 }  /* 시머는 오버레이 페이드인 — 배경 교체 없어 번쩍임 없음 */
}
/* 호버 시머 오버레이: 막대 3배 광 시트 1장이 아래→위 대각으로 반복 스윕 — 타일링 없어 이음매(네모) 없음 */
.colc-bar::after{ content:''; position:absolute; inset:-100%; opacity:0; transition:opacity .5s ease;
  background:linear-gradient(135deg, rgba(var(--white-rgb),0) 32%, rgba(var(--white-rgb),.18) 50%, rgba(var(--white-rgb),0) 68%);
  animation:colcShimmer 2.2s linear infinite }
/* 아래(+40%)에서 위(-40%) 한 방향 진행. 시작·끝 모두 광이 막대 밖이라 루프 리셋이 안 보임 */
@keyframes colcShimmer{ 0%{ transform:translate(40%,40%) } 100%{ transform:translate(-40%,-40%) } }
.colc-bar{ position:relative; overflow:hidden; width:100%; max-width:4rem; border-radius:var(--radius-control) var(--radius-control) 0 0;
  background:var(--gray-200) }  /* 둥근 사각형 막대(상단만 R). 비강조는 그레이, 강조(hi)만 보라 */
.colc-stack.hi .colc-bar{ background:linear-gradient(180deg,var(--accent),var(--purple-600)) }
.colc-v{ font-size:var(--text-18); font-weight:600; white-space:nowrap }
.colc-stack.hi .colc-v{ color:var(--accent) }
.colc .sec-note{ font-size:var(--text-18); color:var(--muted); margin-top:var(--space-32); font-weight:400 }  /* 차트 출처 노트: 본문 레귤러, 라벨과의 간격 32 */
.colc .sec-note strong{ font-weight:600 }  /* 출처(첫 줄)만 볼드 */
.colc-labels{ display:grid; gap:var(--grid-gap); margin-top:.625rem }
.colc-l{ font-size:var(--text-18); font-weight:600; color:rgba(var(--ink-rgb),.6); text-align:center }  /* 축 라벨: 노트와 동일 사이즈 + 볼드, 명도는 한 톤 밝게 */
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

/* ============ 데모 오버레이 (#demo) — 좌 목업 / 우 코드·스텝 ============ */
#demo{ position:fixed; inset:0; z-index:120; display:flex; align-items:center; justify-content:center; padding:2rem;
  background:rgba(var(--ink-rgb),.55); backdrop-filter:blur(8px); opacity:0; pointer-events:none; transition:opacity .35s ease }
#demo.open{ opacity:1; pointer-events:auto }
.demo-panel{ position:relative; width:100%; max-width:64rem; max-height:90vh; overflow:hidden;
  display:grid; grid-template-columns:1fr 1fr; background:var(--white); border-radius:var(--radius-card);
  box-shadow:0 40px 120px rgba(var(--ink-rgb),.45); transform:translateY(16px) scale(.99); transition:transform .4s cubic-bezier(.2,.8,.2,1) }
#demo.open .demo-panel{ transform:none }
.demo-close{ position:absolute; top:1rem; right:1rem; z-index:2; width:2.5rem; height:2.5rem; border-radius:var(--radius-pill);
  display:grid; place-items:center; background:rgba(var(--ink-rgb),.06); color:var(--ink); transition:background .2s }
.demo-close .icn{ width:1.125rem; height:1.125rem }
@media (hover:hover){ .demo-close:hover{ background:rgba(var(--ink-rgb),.12) } }
/* 좌: 목업 영역 (그레이 + 도트) */
.demo-visual{ background:color-mix(in srgb, var(--ink) 5%, var(--white)); padding:2.5rem; display:grid; place-items:center;
  background-image:radial-gradient(rgba(var(--ink-rgb),.06) 1px, transparent 1.5px); background-size:20px 20px }
.demo-mock{ width:100%; max-width:19rem; aspect-ratio:9/16; border-radius:var(--radius-card);
  background:var(--white); box-shadow:0 20px 50px rgba(var(--ink-rgb),.14); overflow:hidden }
.demo-mock img, .demo-mock video{ width:100%; height:100%; object-fit:cover; display:block }
/* 우: 정보 영역 */
.demo-info{ padding:3rem 2.75rem; display:flex; flex-direction:column; overflow-y:auto }
.demo-step-eb{ font-family:'Departure Mono',monospace; font-size:var(--text-14); letter-spacing:.06em; color:var(--purple-500); margin-bottom:1rem }
.demo-step-t{ font-size:var(--text-24); font-weight:600; letter-spacing:-.01em; color:var(--ink); margin-bottom:.75rem; line-height:var(--leading-heading) }
.demo-step-d{ font-size:var(--text-16); line-height:var(--leading-body); color:rgba(var(--ink-rgb),.6); word-break:keep-all }
.demo-tabs{ display:flex; gap:.5rem; margin:1.75rem 0 1rem }
.demo-tab{ padding:.5rem 1rem; border-radius:var(--radius-pill); font-size:var(--text-14); font-weight:500;
  color:rgba(var(--ink-rgb),.55); background:rgba(var(--ink-rgb),.05); transition:all .2s }
.demo-tab.active{ background:var(--ink); color:var(--white) }
.demo-code{ flex:1; min-height:12rem; border-radius:var(--radius-card-sm); background:var(--ink); color:rgba(var(--white-rgb),.9);
  padding:1.5rem; font-family:'Departure Mono',monospace; font-size:var(--text-14); line-height:var(--leading-body); overflow:auto; white-space:pre; word-break:normal }
.demo-code .k{ color:var(--purple-300) } .demo-code .s{ color:#7fd0a8 } .demo-code .c{ color:rgba(var(--white-rgb),.4) }
.demo-foot{ display:flex; align-items:center; justify-content:space-between; margin-top:1.5rem }
.demo-dots{ display:flex; gap:.5rem }
.demo-dot{ width:.5rem; height:.5rem; border-radius:var(--radius-pill); background:rgba(var(--ink-rgb),.18); transition:all .25s }
.demo-dot.is-active{ background:var(--accent); transform:scale(1.25) }
.demo-arrows{ display:flex; gap:.5rem }
.demo-arrow{ width:2.75rem; height:2.75rem; border-radius:var(--radius-pill); border:1px solid var(--line);
  display:grid; place-items:center; color:rgba(var(--ink-rgb),.6); background:var(--white); transition:all .25s }
.demo-arrow svg{ width:1.125rem; height:1.125rem }
.demo-arrow:disabled{ opacity:.35; cursor:default }
@media (hover:hover){ .demo-arrow:not(:disabled):hover{ background:var(--accent); border-color:transparent; color:var(--white) } }
@media (max-width:767px){
  #demo{ padding:0 }
  .demo-panel{ grid-template-columns:1fr; max-height:100vh; height:100vh; border-radius:0; overflow-y:auto }
  .demo-visual{ padding:2rem } .demo-mock{ max-width:14rem }
  .demo-info{ padding:2rem 1.5rem } }

/* ============ INSIGHTS — 블로그 탭 필터 + 카드 링크 ============ */
.blog-tabs{ display:flex; flex-wrap:wrap; gap:.625rem; margin-bottom:2rem }
.blog-tab{ padding:.75rem 1.5rem; border:1px solid var(--line); border-radius:var(--radius-pill);
  background:transparent; font-size:var(--text-body); font-weight:var(--w-title); line-height:1; color:var(--c-body);
  cursor:pointer; transition:background .2s ease, color .2s ease, border-color .2s ease }
@media (hover:hover){ .blog-tab:hover{ color:var(--ink); border-color:rgba(var(--ink-rgb),.4) } }
.blog-tab.is-on{ background:var(--ink); color:var(--white); border-color:var(--ink) }
.card-link{ display:flex; text-decoration:none; color:inherit }
.blog-item.hidden, .press-item.hidden{ display:none }
/* 페이지네이션 (보도자료·블로그 공용) — 공통 토큰: --pager-* 로 단일 조정 */
.pager{ --pager-btn:3rem;      /* 버튼 지름 48px */
  --pager-ico:1.5rem;          /* 화살표 아이콘 24px */
  --pager-gap:.5rem;
  display:flex; justify-content:center; align-items:center; gap:var(--pager-gap); margin-top:var(--space-48) }
.pager button{ width:var(--pager-btn); height:var(--pager-btn); padding:0; border:none; background:transparent;  /* 고정 원 — 호버·셀렉티드 동일 */
  border-radius:var(--radius-pill); font-size:var(--text-18); font-weight:500; line-height:1;
  color:rgba(var(--ink-rgb),.55); cursor:pointer;
  display:inline-flex; align-items:center; justify-content:center;
  transition:color .2s ease, background .2s ease, opacity .2s ease }
@media (hover:hover){ .pager button:hover:not(:disabled):not(.is-on){ color:var(--ink); background:rgba(var(--surface-rgb),1) } }
.pager button.is-on{ background:var(--ink); color:var(--white); font-weight:600 }
.pager button:disabled{ opacity:.3; cursor:default }
.pager button svg{ width:var(--pager-ico); height:var(--pager-ico); display:block }
.pager-dots{ min-width:1.5rem; text-align:center; font-size:var(--text-18); color:rgba(var(--ink-rgb),.4); user-select:none }

/* ============ POST — 블로그 아티클 상세 ============ */
.post-meta{ display:flex; align-items:center; gap:1.5rem; flex-wrap:wrap; padding:1.5rem 0;
  border-top:1px solid rgba(var(--ink-rgb),.1); border-bottom:1px solid rgba(var(--ink-rgb),.1) }
.post-cat{ font-size:var(--text-cap); font-weight:var(--w-strong); letter-spacing:.025em; text-transform:uppercase;
  color:var(--accent); background:rgba(var(--accent-rgb),.08); border-radius:var(--radius-pill); padding:.375rem .875rem }
.post-date, .post-read{ font-size:var(--text-cap); color:var(--c-mut) }
.post-read{ margin-left:auto }
.post-grid{ display:grid; grid-template-columns:1fr; gap:2.5rem }
@media (min-width:1024px){
  .post-grid{ grid-template-columns:repeat(12,1fr); column-gap:var(--grid-gap) }
  .post-body{ grid-column:2 / 9 }
  .post-side{ grid-column:10 / 12; position:sticky; top:12rem; align-self:start } }
.post-body>*+*{ margin-top:1.25rem }
.post-body .post-lead{ font-size:var(--text-30); font-weight:var(--w-num); letter-spacing:-.01em;
  line-height:var(--lh-heading); color:var(--accent); margin-bottom:1.5rem }   /* 프레스 pd-title 스타일 이식(굵은 보라) */
.post-body h3{ font-size:var(--text-24); font-weight:var(--w-strong); line-height:var(--lh-heading); letter-spacing:-.01em;
  margin:3.5rem 0 1.25rem; scroll-margin-top:10rem }
.post-body > h3:first-child{ margin-top:0 }   /* h3가 리터럴 첫 요소일 때만 갭 제거(리드·도입문단 있으면 3.5rem 유지) */
.post-body h3::before{ content:''; display:block; width:2rem; height:2px; background:var(--gray-300); margin-bottom:1.5rem }
.post-body p{ font-size:var(--text-20); line-height:var(--lh-body); color:var(--c-body) }   /* 프레스 본문과 동일(20) */
.post-body p b{ color:var(--ink); font-weight:var(--w-strong) }
.post-body ul{ list-style:none; display:flex; flex-direction:column; gap:.75rem; padding-left:1.25rem }
.post-body ul li{ position:relative; font-size:var(--text-20); line-height:var(--lh-body); color:var(--c-body) }   /* 본문 문단(20)과 폰트 통일 */
.post-body ul li::before{ content:''; position:absolute; left:-1.25rem; top:.62em; width:.375rem; height:.375rem;
  border-radius:50%; background:currentColor }   /* 불릿 = 폰트와 같은 색 */
.post-fig{ margin:2.5rem 0 }
.post-fig img{ width:100%; height:auto; display:block; border-radius:var(--radius-card-sm) }
.post-side ul{ list-style:none; margin-top:1rem; display:flex; flex-direction:column; gap:.25rem;
  border-left:1px solid rgba(var(--ink-rgb),.12) }   /* 섹션 이동 레일 */
.post-side a{ display:block; padding:.625rem 0 .625rem 1rem; margin-left:-1px; border-left:2px solid transparent;
  font-size:var(--text-body); line-height:var(--lh-body); color:var(--c-mut); text-decoration:none;
  transition:color .2s ease, border-color .2s ease }
@media (hover:hover){ .post-side a:hover{ color:var(--ink) } }
.post-side a.is-active{ color:var(--ink); border-color:var(--ink); font-weight:var(--w-title) }   /* 현재 보고 있는 섹션 — 히어로 배경과 같은 네이비(--ink), 보라 X */
@media (max-width:1023px){ .post-side{ border-top:1px solid rgba(var(--ink-rgb),.1); padding-top:2rem } }
/* 목차 없는 아티클(h3<2): 히어로와 좌측 정렬(2칸부터) */
@media (min-width:1024px){ .post-grid.solo .post-body{ grid-column:2 / 11 } }
@media (min-width:1024px){ .post-grid .post-actions{ grid-column:2 / 9 } .post-grid.solo .post-actions{ grid-column:2 / 11 } }   /* 액션바: 본문 컬럼 정렬 */
/* 블로그 상세 히어로 제목 — 장문 대응(좌측 정렬), 솔루션 히어로급 스케일 (높이·정렬은 body.press 공용) */
body.blog .phero-h1{ font-size:var(--text-32); max-width:28ch }   /* 프레스 상세와 동일 스케일 */
@media (min-width:640px){ body.blog .phero-h1{ font-size:var(--text-40) } }
@media (min-width:768px){ body.blog .phero-h1{ font-size:var(--text-48) } }
@media (min-width:1024px){ body.blog .phero-h1{ font-size:var(--text-60) } }
/* 히어로 메타 — 카테고리·날짜·읽는시간(좌) 그룹 */
.pdm-info{ display:flex; align-items:center; gap:1rem; flex-wrap:wrap }
.pdm-read{ font-size:var(--text-body-sm); color:rgba(var(--white-rgb),.5) }
body.blog .pd-hero-meta .post-cat{ background:rgba(var(--white-rgb),.14); color:var(--white) }   /* 다크 히어로 위 카테고리 칩 */

/* ══ 검수 시안: ① Recognition 칩 통합(Track Record 하단) ② Industry Firsts 1st 앵커 재구성 ══ */
/* ① 인증·수상 칩 — 독립 섹션 대신 Track Record 숫자 카드 아래 한 줄 증거 밴드 */
.recog-chips{ margin-top:clamp(var(--space-24), 4.2vw, var(--space-64)) }   /* 위 간격: 화면 폭 가변 (1440≈60, 상한 64) */
@media (max-width:767px){ .recog-chips{ margin-top:clamp(var(--space-24), 4.7vw, var(--space-40)) } }   /* 모바일: 가변 (375≈23, 640≈30) */
.recog-chips .rc-label{ margin-bottom:clamp(var(--space-12), 3.125vw, var(--space-40)) }   /* 타이틀↔로고: 화면 폭 가변 (640≈20px, 상한 40) */
/* 인증·수상 무한 스와이프 — [로고 위 / 수상명 아래] 셀, 기존 ptScroll 재사용 */
.aw-marquee{ overflow:hidden;
  mask-image:linear-gradient(to right, transparent, #000 8%, #000 92%, transparent);
  -webkit-mask-image:linear-gradient(to right, transparent, #000 8%, #000 92%, transparent) }
.aw-marquee .pt-track{ display:flex; width:max-content; animation:ptScroll 42s linear infinite; grid-template-columns:none; gap:0 }
.aw-marquee:hover .pt-track{ animation-play-state:paused }

.aw-set{ display:flex; align-items:flex-start; gap:0; padding-right:0 }
.aw-item{ display:flex; flex-direction:column; align-items:center; gap:1rem;
  width:12.5rem; margin:0 1rem; text-align:center }   /* 아이템 사이 간격 (24→32px) */
.aw-logo{ position:relative; width:4.75rem; height:4.75rem;
  display:flex; align-items:center; justify-content:center }  /* 박스 제거 — 로고 SVG가 자체 완결형 */
.aw-logo img{ max-width:100%; max-height:100%; width:auto; height:auto; object-fit:contain }  /* 68%→100% */
@media (max-width:639px){ .aw-logo{ width:3.5rem; height:3.5rem } }   /* 모바일: 로고 축소 (4.75→3.5rem) — base 뒤 */
.aw-logo img:not([style*="none"]) + i{ display:none } /* 로고 파일 있으면 약칭 숨김 */
.aw-logo i{ font-style:normal; font-family:'Departure Mono',monospace; font-size:var(--text-14);
  font-weight:400; color:var(--gray-400); letter-spacing:.02em }
.aw-item figcaption{ display:flex; flex-direction:column; gap:.3rem }
.aw-item b{ font-size:var(--text-body); font-weight:var(--w-title); color:var(--ink); line-height:var(--lh-heading); word-break:keep-all }   /* 14→16→18 */
.aw-item figcaption span{ font-size:var(--text-body-sm); color:var(--c-body) }   /* 12→14→16 */
@media (max-width:640px){ .aw-item{ width:10rem; margin:0 .875rem } }

/* ② Industry Firsts — 집계(1st)를 크게, 개별 항목은 작게 */
.firsts-hero{ display:grid; grid-template-columns:1.2fr 2.8fr; align-items:center; gap:clamp(2.5rem,6vw,5.5rem);   /* 1st 영역 확장 (auto→30%) */
  background-color:rgba(var(--ink-rgb),.04); border-radius:var(--radius-card);
  padding:var(--pad-panel-y) var(--pad-panel-x);   /* 그레이 패널 공통 토큰 */
  background-image:radial-gradient(rgba(var(--ink-rgb),.06) 1px, transparent 1.5px); background-size:20px 20px }
.fh-big{ display:flex; flex-direction:column; align-items:center; gap:.75rem }
.fh-num{ font-weight:700; line-height:.85; color:var(--ink); letter-spacing:-.04em; font-size:clamp(6rem,11vw,9.5rem) }
.fh-num .st{ font-size:.38em; font-weight:700; color:var(--ink); vertical-align:baseline; letter-spacing:0; margin-left:.04em }   /* st를 1 하단(베이스라인)에 정렬 */
.fh-cap{ font-size:var(--text-18); font-weight:500; color:var(--muted); white-space:nowrap }   /* 2토큰 업(14→18) + 웨이트 500 */
.fh-list li{ display:flex; align-items:center; gap:.9rem; padding-block:1rem;
  font-size:var(--text-20); font-weight:var(--w-title); color:var(--ink); line-height:var(--lh-heading) }   /* 두 토큰 업(16→20) */
.fh-list li + li{ border-top:1px solid rgba(var(--ink-rgb),.09) }
.fh-chip{ flex:none; font-size:var(--text-16); font-weight:500; letter-spacing:.02em;   /* 두 토큰 업(12→16), 웨이트 500 */
  padding:.5rem 1rem; border-radius:999px; background:rgba(97,0,255,.09); color:var(--purple-600) }   /* 알약 확대 (.3/.7→.5/1rem) */
.fh-chip.world{ background:var(--purple-500); color:#fff }
.fh-chip.lead{ background:rgba(var(--ink-rgb),.07); color:var(--ink) }
.fh-list li.fh-ally{ margin-top:.5rem; padding-top:1.5rem }
.fh-sub{ margin-left:auto; padding-left:1rem; font-size:var(--text-body); font-weight:400; color:var(--c-body); white-space:nowrap }   /* 두 토큰 업(14→18) */
@media (max-width:767px){
  .firsts-hero{ grid-template-columns:1fr; gap:1.75rem; padding:2rem 1.25rem }
  .fh-num{ font-size:3.75rem }
  .fh-list li{ display:grid; grid-template-columns:auto 1fr; column-gap:.9rem; row-gap:0; align-items:center }
  .fh-sub{ grid-column:2; margin-left:0; padding-left:0; justify-self:start }
}
.ht-era{ list-style:none; display:flex; align-items:center; gap:.6rem; padding:2.25rem 0 .75rem }
.ht-era:first-child{ padding-top:0 }
.ht-era .dot{ width:.45rem; height:.45rem; border-radius:50%; background:var(--accent); flex:none }
.ht-era-label{ font-size:var(--text-13, .8125rem); font-weight:600; letter-spacing:.1em; text-transform:uppercase; color:var(--subtle); white-space:nowrap }
@media (max-width:767px){ .ht-era-label{ white-space:normal } }  /* 긴 라벨이 뷰포트 밖으로 밀려 가로 스크롤 만드는 것 방지 */
.ht-sub li .m{ color:var(--muted); margin-right:.6rem; font-variant-numeric:tabular-nums; white-space:nowrap }
/* ══ History B-lite v2: 고정 사이드(스크롤 시 페이드 전환) + 연속 리스트, 디바이더 없음 ══ */
@media (min-width:900px){ .ht2 .cm-head{ grid-column:1 / 6 } .ht2 .ht2-body{ grid-column:6 / 13 } }   /* 타이틀 칼럼 4→5개 */
.ht2-fade{ display:grid; margin-top:var(--space-8) }
.ht2-layer .sec-h2{ margin:var(--space-8) 0 0 }
.ht2-layer{ grid-area:1 / 1; opacity:0; transition:opacity .45s cubic-bezier(.4,0,.2,1); pointer-events:none }
.ht2-layer.on{ opacity:1 }
.ht2-group{ background:rgba(var(--ink-rgb),.04); border-radius:var(--radius-card);
  padding:var(--pad-panel-y) var(--pad-panel-x) }   /* 그레이 패널 공통 토큰 */
.ht2-group + .ht2-group{ margin-top:var(--space-32) }
@media (min-width:900px){
  .ht2-group{ opacity:.45; transition:opacity .6s cubic-bezier(.4,0,.2,1) }
  .ht2-group.ht2-on{ opacity:1 }
}
.ht2-era-head{ display:none }
.ht2-era-head .ht2-t{ font-size:var(--text-26); font-weight:var(--w-num); line-height:var(--lh-heading); margin:0 }   /* 마진 제거 (웨이트 700 유지) */
.ht2-faq{ list-style:none; margin:0; padding:0 }
.ht2 .faq-row{ padding:var(--space-24) 0 }   /* 기본(모바일·태블릿): 기존 스타일 */
.ht2 .faq-item.open .faq-row{ padding:var(--space-24) 0 }
.ht2 .faq-t{ display:flex; align-items:baseline }
.ht2 .ht2-yr{ flex:none; font-weight:var(--w-title); color:var(--c-mut); margin-right:var(--space-16); font-variant-numeric:tabular-nums }   /* 연도: 별도 박스 */
.ht2 .ht2-tt{ flex:1; min-width:0 }   /* 줄바꿈은 텍스트 시작점 기준 */
.ht2 .faq-t-bottom .ht2-tt{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap }   /* 닫힘 타이틀 말줄임 (flex 구조로 이관) */
/* History 전용: 공통 FAQ 롤업 모션 제거 — 타이틀 제자리 고정, 월 리스트만 아래로 펼침 */
.ht2 .faq-content{ max-height:none !important; overflow:visible }   /* JS 인라인 maxHeight·클립 무력화 */
.ht2 .faq-inner, .ht2 .faq-item.open .faq-inner{ transform:none }   /* translateY 롤업 제거 */
.ht2 .faq-t-top{ display:none }   /* 열림·닫힘 타이틀 동일 → 중복 제거, bottom 하나만 정적 사용 */
.ht2 .faq-t-bottom{ margin-top:0; max-height:none; opacity:1 !important; transform:none !important }
.ht2 .faq-item.open .faq-t-bottom .ht2-tt{ white-space:normal; overflow:visible; text-overflow:clip }   /* 열리면 전체 표시(줄바꿈) */
.ht2 .faq-content{ contain:inline-size }   /* nowrap 타이틀의 min-content 전파 차단 (모바일 가로 오버플로우 방지) */
.ht2 .faq-item.open .ht2-yr{ color:var(--purple-500) }   /* 열리면 연도 보라 */
@media (hover:hover){ .ht2 .faq-row:hover{ background:transparent } }   /* 호버 배경 제거 */
.ht2 .faq-t{ font-size:var(--text-20); font-weight:var(--w-title) }
.ht2 .faq-ans{ display:none }   /* 본문은 faq-content 밖(ht2-subwrap)에서 풀폭으로 */
.ht2-subwrap{ display:grid; grid-template-rows:0fr; transition:grid-template-rows .45s cubic-bezier(.45,0,.55,1) }
.ht2-subwrap .ht2-subin{ overflow:hidden }   /* 패딩 금지 — 0fr 접힘 누수 원인 */
/* PC 전용: 타이틀 행 패딩 제거 + 월 리스트에 여유 (패딩은 클립 안쪽 rows에) */
@media (min-width:900px){   /* cm-grid 2열 시작(900)과 경계 일치 — 963 등 이 구간 동일 규칙 */
  .ht2 .faq-row, .ht2 .faq-item.open .faq-row{ padding:0 }
  .ht2 .faq-li{ padding-block:var(--space-24) }   /* 간격은 행 안이 아니라 디바이더 사이(li 껍데기)에 */
  .ht2 .ht2-faq > .faq-li:first-child{ padding-top:0 }   /* 맨 위 행 위 패딩 삭제 */
  .ht2 .ht2-faq > .faq-li:last-child{ padding-bottom:0 }   /* 맨 아래 행 아래 패딩 삭제 */
  .ht2 .ht2-rows{ padding-block:var(--space-16) }
  .ht2 .faq-t, .ht2 .ht2-yr{ font-weight:var(--w-strong) }   /* PC 카드 타이틀(연도+문장) 웨이트 업 500→600 */
}
.ht2 .faq-item.open .ht2-subwrap{ grid-template-rows:1fr }
.ht2-rows{ list-style:none; margin:0; padding:0 }
.ht2-rows li .m, .ht2-rows li > span:last-child{ transform-origin:left center; transition:transform .3s cubic-bezier(.2,.8,.2,1) }
@media (hover:hover){   /* 호버는 줄 단위, 확대는 각자 제자리에서 */
  .ht2-rows li:hover .m{ transform:scale(1.015) }
  .ht2-rows li:hover > span:last-child{ transform:scale(1.015) }
}
.ht2-rows li:first-child{ padding-top:0 }   /* 첫 행 위 간격 제거 */
.ht2-rows li{ display:flex; gap:var(--space-16);   /* 디바이더 없이 패딩으로만 그룹핑, 갭은 연도와 동일 16 */
  padding:var(--space-12) 0; font-size:var(--text-body); font-weight:400; color:var(--c-body); line-height:var(--lh-body) }   /* 본문 웨이트 400 */
.ht2-rows li .m{ flex:none; min-width:3rem; color:var(--c-mut); font-weight:400 }   /* 월 그레이·볼드 */
@media (max-width:899px){
  .ht2 .cm-head{ display:none }
  .ht2-era-head{ display:block; margin-bottom:0; padding:0 }   /* 위 간격 제거 (카드 패딩이 담당) */
}
/* Alliance 소절 카드 위 여백 */
/* 시안 D: 좌 문장(.sub-t) / 우 미니 필 2개, 86+는 마퀴 라벨 */
.firsts-eco .eco-head{ display:flex; justify-content:space-between; align-items:center; gap:var(--space-40) }
.firsts-eco .eco-pills{ display:flex; gap:var(--space-12); flex-wrap:wrap; justify-content:flex-end }
.firsts-eco .eco-pill{ transition:transform .35s cubic-bezier(.2,.8,.2,1);
  font-size:var(--text-18); border:1px solid rgba(var(--ink-rgb),.12); border-radius:var(--radius-pill);
  padding:.875rem 1.25rem; white-space:nowrap; color:var(--ink) }
.firsts-eco .eco-pill b{ font-weight:600; transition:color .25s }
.firsts-eco .eco-pill i{ font-style:normal; color:var(--c-body); margin-left:.375rem }
@media (max-width:767px){
  .firsts-eco .eco-head{ flex-direction:column; align-items:flex-start; gap:var(--space-20) }
  .firsts-eco .eco-pills{ justify-content:flex-start }
}
body.company .firsts-eco .ally-head{ text-align:left }
@media (hover:hover){ .firsts-eco .eco-pill:hover{ transform:scale(1.05) } .firsts-eco .eco-pill:hover b{ color:var(--purple-500) } }   /* 얼라이언스 문장 좌측 정렬 (스탯 로우 확정 후 변경) */
.firsts-eco{ margin-top:clamp(var(--space-24), 4.2vw, var(--space-64)) }   /* 인증수상(recog-chips)과 동일 가변 커브 */
@media (max-width:767px){ .firsts-eco{ margin-top:clamp(var(--space-24), 4.7vw, var(--space-40)) } }

/* ============ MEDIA 공통(newsroom·blog·resources) — 첫 섹션을 히어로에 붙임 (contact 방식) ============ */
body.media .phero + section .sec{ padding-top:var(--space-32) }
body.media .phero-inner{ padding-bottom:3rem }  /* 히어로 하단 6rem → 3rem (media 스코프만) */

/* ============ NEWSROOM — 보도자료 리스트 ============ */
/* ============ 공통 컨트롤 — 필 인풋·드롭다운 (페이저처럼 --ctl-* 토큰으로 단일 조정) ============ */
.select-pill, .input-pill{ --ctl-h:2.75rem;   /* 컨트롤 높이 44px */
  --ctl-pad:1.25rem;                           /* 좌우 패딩 20px */
  --ctl-ico:1.25rem;                           /* 아이콘 20px (페이저 화살표와 동일) */
  --ctl-fs:var(--text-18);                     /* 컨트롤 텍스트 */
  height:var(--ctl-h); border:1px solid rgba(var(--ink-rgb),.15); border-radius:var(--radius-pill);
  background-color:transparent; font-size:var(--ctl-fs); color:var(--ink) }
.select-pill{ padding:0 calc(var(--ctl-pad) + 1rem) 0 var(--ctl-pad); font-weight:var(--w-title); cursor:pointer; appearance:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23111' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat:no-repeat; background-position:right .875rem center; background-size:var(--ctl-ico) }
.input-pill{ display:flex; align-items:center; gap:.5rem; padding:0 var(--ctl-pad) }
.input-pill svg{ width:var(--ctl-ico); height:var(--ctl-ico); color:rgba(var(--ink-rgb),.45); flex:none }
.input-pill input{ border:none; background:transparent; outline:none; min-width:0;
  font-size:var(--ctl-fs); color:var(--ink) }
.input-pill input::placeholder{ color:var(--c-mut) }
@media (hover:hover){ .select-pill:hover, .input-pill:hover{ border-color:var(--c-mut) } }
.select-pill:focus-visible, .input-pill:focus-within{ border-color:var(--ink) }
/* 커스텀 드롭다운 — 트리거는 select-pill 그대로, 패널은 카드 문법 */
.drop{ position:relative }
.drop-btn{ display:inline-flex; align-items:center; text-align:left }
.drop.open .drop-btn{ border-color:var(--ink) }
.drop-menu{ position:absolute; top:calc(100% + 1rem); left:0; min-width:16rem; max-height:22rem; z-index:30;
  overflow-y:auto; list-style:none; padding:1rem .75rem; background:var(--white); border:none;
  border-radius:1rem; box-shadow:0 8px 40px rgba(var(--ink-rgb),.14);
  opacity:0; visibility:hidden; transform:translateY(-4px);
  transition:opacity .2s ease, transform .2s ease, visibility .2s }
.drop.open .drop-menu{ opacity:1; visibility:visible; transform:none }
.drop-menu li{ padding:.875rem 1.25rem; border-radius:.5rem; font-size:var(--text-20); font-weight:var(--w-title);
  color:rgba(var(--ink-rgb),.45); white-space:nowrap; cursor:pointer;
  transition:background .2s ease, color .2s ease }
@media (hover:hover){ .drop-menu li:hover{ background:rgba(var(--surface-rgb),1); color:var(--ink) } }
.drop-menu li.is-on{ color:var(--ink); font-weight:var(--w-strong) }
/* 패널 스크롤바 — 레퍼처럼 얇은 회색 썸 */
.drop-menu::-webkit-scrollbar{ width:.375rem }
.drop-menu::-webkit-scrollbar-thumb{ background:rgba(var(--ink-rgb),.25); border-radius:var(--radius-pill) }
.drop-menu::-webkit-scrollbar-track{ background:transparent }

/* 뉴스룸 컨트롤 — 네이버 뉴스룸형: 텍스트 드롭다운 + 라운드 검색박스 */
.news-controls{ display:flex; align-items:center; gap:2rem; flex-wrap:wrap;
  padding-bottom:1.25rem; border-bottom:1px solid rgba(var(--ink-rgb),.14);
  position:relative; z-index:40 }  /* rvl transform 스태킹 위로 — 드롭 패널이 리스트에 안 뚫리게 */
/* 드롭 트리거: 필 대신 텍스트형 — 기본(전체)은 그레이, 선택·열림은 잉크 */
.news-controls .drop-btn{ height:auto; padding:0; border:none; background-image:none;
  font-size:var(--text-20); font-weight:var(--w-strong); color:var(--c-mut);
  transition:color .2s ease }
.news-controls .drop-btn::after{ content:''; width:1.125rem; height:1.125rem; margin-left:.375rem; background:currentColor;
  -webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E") center/contain no-repeat;
  mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E") center/contain no-repeat }
@media (hover:hover){ .news-controls .drop-btn:hover{ color:var(--ink) } }
.news-controls .drop.open .drop-btn,
.news-controls .drop:not([data-value="all"]) .drop-btn{ color:var(--ink) }
/* 검색박스: 레퍼(네이버)형 — 보더 없는 그레이 필 + 우측 화이트 라운드 사각 돋보기 (컬러·R값 토큰) */
.news-search{ margin-left:auto; display:flex; align-items:center; gap:.5rem;
  height:3.5rem; padding:0 .25rem 0 1rem; border:none;
  border-radius:var(--radius-control); background:color-mix(in srgb, var(--ink) 6%, var(--white)) }
.news-search input{ flex:1; width:16rem; min-width:0; border:none; outline:none; background:transparent;
  font-size:var(--text-20); font-weight:var(--w-title); color:var(--ink) }
.news-search input::placeholder{ color:var(--subtle) }
.news-search input::-webkit-search-cancel-button{ display:none }
.ns-clear{ width:1.5rem; height:1.5rem; flex:none; border:none; padding:0; cursor:pointer;
  margin-right:.25rem;  /* 돋보기와 살짝 간격 */
  border-radius:var(--radius-pill); background:var(--gray-300); color:var(--white);
  display:grid; place-items:center; transition:background .2s ease }
.ns-clear[hidden]{ visibility:hidden }  /* 자리는 유지 — 나타날 때 인풋 폭이 안 변하게 */
@media (hover:hover){ .ns-clear:hover{ background:var(--gray-400) } }
.ns-clear svg{ width:.75rem; height:.75rem }
.ns-btn{ width:3rem; height:3rem; flex:none; border:none; padding:0;
  background:var(--white); border-radius:calc(var(--radius-control) - .25rem); color:rgba(var(--ink-rgb),.72); cursor:pointer;
  display:grid; place-items:center; transition:transform .2s ease }  /* 박스 R(control) - 인셋 4px = 동심원 정렬 */
@media (hover:hover){ .ns-btn:hover{ transform:scale(1.05) } }
.ns-btn svg{ width:1.5rem; height:1.5rem }
/* ============ PRESS DETAIL — 보도자료 상세 공통 (네이버 뉴스룸 상세 포맷) ============ */
/* 히어로: 다크 배경 + 좌측 정렬 타이틀·날짜 + 우측 공유 버튼 */
body.press .phero{ min-height:0 }  /* 100vh 해제 — 레퍼처럼 밴드형 히어로 */
body.press .phero{ min-height:60vh; display:flex; flex-direction:column; justify-content:flex-end; padding-bottom:var(--space-40) }   /* 하단 기준 앵커 */  /* 화면 3/5 */
body.press .phero-inner{ position:relative; z-index:1; width:100%;
  grid-template-columns:repeat(12,1fr); column-gap:var(--grid-gap);
  min-height:0; padding:11rem var(--shell-pad) 0 }  /* 상단 GNB 보정, 하단은 메타 줄이 담당 */
@media (min-width:640px){ body.press .phero-inner{ padding-inline:2rem } }  /* 섹션·오버레이 패딩과 동기화 */
/* 히어로 메타 줄 — 날짜(좌)·공유(우) 한 줄, 콘텐츠 그리드 정렬 */
.pd-hero-meta{ position:relative; z-index:1; width:100%; max-width:var(--container-shell);
  margin:4rem auto 0; padding-inline:var(--shell-pad);
  display:grid; grid-template-columns:repeat(12,1fr); column-gap:var(--grid-gap) }
@media (min-width:640px){ .pd-hero-meta{ padding-inline:2rem } }
.pdm-cell{ grid-column:1 / -1; display:flex; justify-content:space-between; align-items:center }
@media (min-width:1024px){ .pdm-cell{ grid-column:2 / 12 } }
.pdm-date{ font-size:var(--text-20); color:rgba(var(--white-rgb),.6) }
body.press .phero-visual{ display:none }
body.press .phero-text{ align-items:flex-start; text-align:left;
  grid-column:1 / -1; max-width:none; margin:0 }
@media (min-width:1024px){ body.press .phero-text{ grid-column:2 / 12 } }  /* 본문과 동일: 2~11칸 */
body.press .phero-h1{ max-width:none; font-size:var(--text-32);
  line-height:var(--lh-heading) }  /* 긴 뉴스 제목 — display(.98) 대신 heading(1.25) 토큰 */
@media (min-width:640px){ body.press .phero-h1{ font-size:var(--text-40) } }
@media (min-width:768px){ body.press .phero-h1{ font-size:var(--text-48) } }
@media (min-width:1024px){ body.press .phero-h1{ font-size:var(--text-60) } }
body.press .phero-text .phero-lead{ color:rgba(var(--white-rgb),.6) }
/* 공유 버튼 — 아이콘만: 평소 죽은 흰색, 호버 시 흰색 + 확대 */
.pd-share{ width:44px; height:44px; flex:none; padding:0; cursor:pointer; border:none; background:transparent;
  color:rgba(var(--white-rgb),.55);
  display:grid; place-items:center; will-change:transform;
  transition:color .22s ease, transform .4s cubic-bezier(.2,.8,.2,1) }
@media (hover:hover){ .pd-share:hover{ color:var(--white); transform:scale(1.15) } }
.pd-share svg{ width:1.75rem; height:1.75rem }
@media (max-width:767px){ .pd-share{ width:36px; height:36px } .pd-share svg{ width:1.25rem; height:1.25rem } }   /* 모바일: 공유 버튼 축소 */
/* 공유 모달 — 기존 modal-panel 문법 준용 */
#pd-share-modal{ position:fixed; inset:0; z-index:120; display:flex; align-items:center; justify-content:center;
  opacity:0; pointer-events:none; transition:opacity .25s ease }
#pd-share-modal.open{ opacity:1; pointer-events:auto }
.psm-backdrop{ position:absolute; inset:0; background:rgba(var(--ink-rgb),.5) }
.psm-panel{ position:relative; width:calc(100% - 2.5rem); max-width:26rem; background:var(--white);
  border-radius:var(--radius-card); padding:2rem; transform:translateY(12px); transition:transform .25s ease }
#pd-share-modal.open .psm-panel{ transform:none }
.psm-panel h2{ text-align:center; font-size:var(--text-22); font-weight:var(--w-strong); margin-bottom:1.75rem }
.psm-close{ position:absolute; right:1rem; top:1rem; width:2.25rem; height:2.25rem; border:none; background:transparent;
  color:rgba(var(--ink-rgb),.55); cursor:pointer; display:grid; place-items:center; border-radius:var(--radius-pill) }
@media (hover:hover){ .psm-close:hover{ background:var(--surface); color:var(--ink) } }
.psm-close svg{ width:1.125rem; height:1.125rem }
.psm-grid{ list-style:none; display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:1.75rem }
.psm-item{ display:flex; flex-direction:column; align-items:center; gap:.625rem; text-decoration:none;
  font-size:var(--text-16); font-weight:var(--w-title); color:rgba(var(--ink-rgb),.7) }
.psm-ico{ width:3.5rem; height:3.5rem; border-radius:var(--radius-control); display:grid; place-items:center;
  color:var(--white); border:none;
  transition:transform .2s ease }
@media (hover:hover){ .psm-item:hover .psm-ico{ transform:scale(1.06) } }
.psm-ico svg{ width:1.5rem; height:1.5rem }
.psm-x{ background:var(--ink) }
.psm-fb{ background:#1877F2 }
.psm-fb svg{ width:1.75rem; height:1.75rem }
.psm-line{ background:#06C755 }
.psm-line svg{ width:1.75rem; height:1.75rem }
.psm-mail{ background:color-mix(in srgb, var(--ink) 6%, var(--white)); color:var(--ink) }
.psm-url{ display:flex; gap:.5rem }
.psm-url input{ flex:1; min-width:0; height:2.75rem; padding:0 1rem; border:1px solid rgba(var(--ink-rgb),.15);
  border-radius:var(--radius-control); font-size:var(--text-16); color:var(--accent); background:var(--white) }
.psm-copy{ flex:none; height:2.75rem; padding:0 1rem; border:1px solid rgba(var(--ink-rgb),.15);
  border-radius:var(--radius-control); background:color-mix(in srgb, var(--ink) 6%, var(--white));
  font-size:var(--text-16); font-weight:var(--w-strong); color:var(--ink); cursor:pointer; transition:background .2s ease }
@media (hover:hover){ .psm-copy:hover{ background:var(--gray-100) } }
/* 본문: 중앙 단일 칼럼 — 제목 반복(브랜드 컬러) + 양쪽 정렬 문단 */
.pd-grid{ display:grid; grid-template-columns:repeat(12,1fr); column-gap:var(--grid-gap) }
.pd-grid > *{ grid-column:1 / -1 }
@media (min-width:1024px){ .pd-grid > *{ grid-column:2 / 12 } }  /* 본문 10칸 중앙 */
.pd-body{ min-width:0 }
.pd-title{ font-size:var(--text-30); font-weight:var(--w-num); letter-spacing:-.01em; line-height:var(--lh-heading);
  color:var(--accent); margin-bottom:1.5rem; word-break:keep-all }
.pd-sum{ list-style:none; display:flex; flex-direction:column; gap:.5rem; margin-bottom:2.5rem;
  font-size:var(--text-20); font-weight:var(--w-title); color:var(--ink); line-height:var(--lh-body); word-break:keep-all }
.pd-fig{ margin:0 0 2.5rem }
.pd-fig img{ display:block; width:100%; height:auto; border-radius:var(--radius-card-sm);
  border:1px solid var(--line) }
/* 본문 소제목·리스트 블록 — 시맨틱 토큰층 준수(--lh-*·--w-*), 리스트는 본문 문단과 동일 크기 */
.pd-h3{ font-size:var(--text-24); font-weight:var(--w-strong); line-height:var(--lh-heading); letter-spacing:-.01em;
  margin:3rem 0 1.25rem; color:var(--ink) }
.pd-body ul.pd-list{ list-style:none; margin:0 0 1.5rem; padding:0; display:flex; flex-direction:column; gap:.5rem;
  font-size:var(--text-20); font-weight:var(--w-title); color:var(--ink); line-height:var(--lh-body); word-break:keep-all }
.pd-fig figcaption{ margin-top:.75rem; font-size:var(--text-16); color:var(--muted);
  text-align:center; line-height:var(--lh-body); word-break:keep-all }
.pd-body > p{ font-size:var(--text-20); line-height:var(--lh-body); color:rgba(var(--ink-rgb),.75);  /* 장문 기사 본문 — 본문 토큰보다 한 단계 큰 20 (해상도별 다운시프트 동일 적용) */
  margin-bottom:1.5rem; word-break:keep-all; text-align:justify }
.pd-end{ color:var(--muted) }
/* 액션 바: 텍스트 복사·이미지 다운로드(좌) + 목록보기(우, 다크) */
.pd-actions{ margin-top:3rem; display:flex; align-items:center; gap:.75rem; flex-wrap:wrap;
  padding-top:var(--space-48); border-top:1px solid var(--line) }  /* 디바이더↔버튼 간격 */
/* 액션 버튼 = 공통 pill 시스템 (hs-scale 호버 포함) — 공통 컨트롤 토큰(--ctl-*) 재사용 */
.pd-actions{ --ctl-h:3.25rem; --ctl-pad:1.25rem; --ctl-fs:var(--text-18); --ctl-ico:1.25rem }
.pd-actions .pill.no-arrow .hspring{ min-height:var(--ctl-h); font-size:var(--ctl-fs); padding-inline:var(--ctl-pad);
  gap:.5rem }  /* 공통 pill(.pill.no-arrow .hspring)보다 구체적으로 — 토큰이 이기게. gap은 아이콘↔텍스트 간격 */
.pd-actions .pill.outline .hspring{ color:var(--gray-700) }  /* 아웃라인 버튼 텍스트·아이콘 — 진한 그레이 토큰 */
.pd-actions svg{ width:var(--ctl-ico); height:var(--ctl-ico) }
.pd-actions .pill:disabled{ opacity:.4; cursor:default }
.pd-actions .pill:disabled .hspring{ transform:none }
.pd-list{ margin-left:auto }

/* 검색 결과 없음 — 아이콘 + 안내 문구 */
.news-empty{ display:flex; flex-direction:column; align-items:center; gap:1.25rem;
  padding:5rem 0; border-bottom:1px solid rgba(var(--ink-rgb),.1) }
.news-empty[hidden]{ display:none }
.ne-ico{ width:5rem; height:5rem; border-radius:var(--radius-pill);
  background:color-mix(in srgb, var(--ink) 6%, var(--white)); color:var(--subtle);
  display:grid; place-items:center }
.ne-ico svg{ width:2.25rem; height:2.25rem }
.news-empty p{ font-size:var(--text-22); font-weight:var(--w-title); color:var(--muted) }
/* 리스트 — 날짜 | 제목 | 썸네일 영역 (타이포·호버는 FAQ 행과 동일, 클릭 시 상세 이동) */
.news-list{ list-style:none }
.news-row{ border-bottom:1px solid var(--line) }
.nr-link{ display:grid; grid-template-columns:7rem 1fr 15rem; align-items:center; gap:var(--grid-gap);  /* 날짜 칼럼 +1rem — 제목과 간격 */
  padding:1.5rem 0; border-radius:var(--radius-card-sm); text-decoration:none; color:inherit;
  background:rgba(var(--surface-rgb),0); transition:background .45s cubic-bezier(.45,0,.55,1) }
/* 행 호버: 배경 필 대신 제목 색 전환 */
@media (hover:hover){ .nr-link:hover .nr-title{ color:var(--accent) } }
.nr-date{ font-size:var(--text-16); font-weight:var(--w-title); color:var(--c-mut);
  line-height:2.25rem; font-variant-numeric:tabular-nums }
.nr-title{ font-size:var(--text-20); font-weight:var(--w-title); letter-spacing:-.01em; line-height:2.25rem;
  transition:color .2s ease;
  color:var(--ink); word-break:keep-all }
@media (min-width:640px){ .nr-title{ font-size:var(--text-24) } }
.nr-thumb{ width:100%; aspect-ratio:3/2; border-radius:var(--radius-card-sm);
  background-color:color-mix(in srgb, var(--ink) 6%, var(--white));
  background-size:cover; background-position:center; background-repeat:no-repeat }
@media (max-width:767px){
  .nr-link{ grid-template-columns:1fr; gap:.75rem; padding:1.25rem 0 }
  .nr-date{ line-height:1 }
  .nr-title{ font-size:var(--text-18); line-height:var(--lh-heading) }
  .nr-thumb{ max-width:20rem }
  .news-search{ margin-left:0; flex:1 } }

/* ============ BLOG — 좌측 카테고리 레일 + 3열 카드 피드 ============ */
.blog-layout{ display:grid; grid-template-columns:1fr; gap:2rem }
@media (min-width:1024px){
  .blog-layout{ grid-template-columns:repeat(12,1fr); column-gap:var(--grid-gap) }
  .blog-rail{ grid-column:1 / 3; flex-direction:column; align-items:flex-start;
    position:sticky; top:7.5rem; align-self:start }
  .blog-main{ grid-column:3 / 13 } }
.blog-rail{ display:flex; flex-wrap:wrap; gap:.5rem }
.blog-grid{ list-style:none; display:grid; grid-template-columns:1fr; gap:2.5rem 1.5rem }
@media (min-width:640px){ .blog-grid{ grid-template-columns:repeat(2,1fr) } }
@media (min-width:1024px){ .blog-grid{ grid-template-columns:repeat(3,1fr) } }
.bf-card{ display:flex; flex-direction:column; align-items:flex-start; text-decoration:none; color:inherit }
.bf-thumb{ width:100%; aspect-ratio:4/3; border-radius:var(--radius-card-sm); margin-bottom:1.25rem;
  background:color-mix(in srgb, var(--ink) 6%, var(--white)) center/cover no-repeat;
  transition:transform .35s cubic-bezier(.2,.8,.2,1) }
@media (hover:hover){ .bf-card:hover .bf-thumb{ transform:translateY(-4px) } }
.bf-thumb-empty{ display:grid; place-items:center; background:var(--ink) }
.bf-thumb-empty .bf-mark{ width:12%; max-width:2.5rem; height:auto }
.bf-title{ font-size:var(--text-22); font-weight:var(--w-strong); letter-spacing:-.01em; line-height:var(--lh-heading);
  color:var(--ink); word-break:keep-all;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden }
.bf-desc{ margin-top:.5rem; font-size:var(--text-body); line-height:var(--lh-body); color:var(--c-body);
  display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden }
.bf-tag{ margin-top:1rem; font-size:var(--text-body-sm); font-weight:var(--w-title); line-height:1; padding:.625rem 1.25rem;
  border-radius:var(--radius-pill); color:var(--c-body);
  background:color-mix(in srgb, var(--ink) 6%, var(--white)) }   /* 연한 그레이 필(테두리 없음), 사이즈·패딩·웨이트500 파라스타 플래그 준용 */

/* ============ RESOURCES — 로고 다운로드 (기존 t-gray grouped 카드 문법, 인쇄용·웹용 좌우) ============ */
.res-logo{ display:grid; grid-template-columns:1fr; gap:1rem }
@media (min-width:768px){ .res-logo{ grid-template-columns:repeat(2,1fr); gap:var(--grid-gap) } }
.res-logo .work-card.grouped{ min-height:0 }
/* 라인 카드: 그레이 몸통 제거, 테두리만 — 이미지 영역(로고 자리)은 잉크 6% 플레이스홀더 유지 */
.res-logo .work-card.rl-card{ background:transparent; border:1px solid var(--line) }
.res-logo .work-card.grouped::before{ margin:-1.5rem -1.5rem 1.5rem; border-radius:0;
  background:color-mix(in srgb, var(--ink) 6%, var(--white)) }
@media (min-width:640px){ .res-logo .work-card.grouped::before{ margin:-2rem -2rem 1.75rem } }
.rl-actions{ display:flex; flex-wrap:wrap; gap:.5rem; margin-top:1.25rem }
.rl-btn{ min-height:3rem; padding:0 1.75rem; border:1px solid var(--line); border-radius:var(--radius-pill);
  background:transparent; font-size:var(--text-14); font-weight:var(--w-title); color:var(--ink); cursor:pointer;
  transition:background .2s ease, color .2s ease, border-color .2s ease }
@media (hover:hover){ .rl-btn:not(:disabled):hover{ background:var(--ink); color:var(--white); border-color:var(--ink) } }
.rl-btn:disabled{ opacity:.4; cursor:default }
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
        <span class="rvl-line"><span>디지털자산 사업</span></span>
        <span class="rvl-line"><span>파라메타와 시작하세요</span></span>
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

<!-- 데모 오버레이 (View Demo → data-demo) — 좌 목업 / 우 코드·설명 / 스텝 네비 -->
<div id="demo" role="dialog" aria-modal="true" aria-label="Product demo" aria-hidden="true">
  <div class="demo-panel" id="demoPanel">
    <button class="demo-close" data-close-demo aria-label="닫기"><svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 4l16 16M20 4 4 20"/></svg></button>
    <div class="demo-visual"><div class="demo-mock" id="demoMock"></div></div>
    <div class="demo-info">
      <div class="demo-step-eb" id="demoStepEb">STEP 01</div>
      <h3 class="demo-step-t" id="demoStepT"></h3>
      <p class="demo-step-d" id="demoStepD"></p>
      <div class="demo-tabs">
        <button class="demo-tab active" data-demo-tab="code">Code</button>
        <button class="demo-tab" data-demo-tab="table">Table</button>
      </div>
      <div class="demo-code" id="demoCode"></div>
      <div class="demo-foot">
        <div class="demo-dots" id="demoDots"></div>
        <div class="demo-arrows">
          <button class="demo-arrow" id="demoPrev" aria-label="이전"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5L8 12l7 7"/></svg></button>
          <button class="demo-arrow" id="demoNext" aria-label="다음"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></button>
        </div>
      </div>
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
document.querySelectorAll('.rvl, .rvl-op, .rvl-wm, .vision-panel .wfd').forEach(el => revealObserver.observe(el));

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
/* Press 상세: 히어로 제목을 렌더 줄 단위로 분해 — 자연 줄바꿈도 줄별 스태거 리빌 */
(function(){
  const h1 = document.querySelector('body.press .phero-h1');
  if(!h1) return;
  const lines = h1.querySelectorAll('.rvl-line');
  if(lines.length !== 1) return;
  const src = lines[0].querySelector('span');
  const text = src.textContent;
  src.innerHTML = text.split(' ').map(w => '<i class="pdw">' + w + '</i>').join(' ');
  const words = [...src.querySelectorAll('.pdw')];
  const rows = [];
  let top = null;
  words.forEach(w => {
    if(w.offsetTop !== top){ rows.push([]); top = w.offsetTop; }
    rows[rows.length - 1].push(w.textContent);
  });
  if(rows.length < 2){ src.textContent = text; return; }
  h1.innerHTML = rows.map(r => '<span class="rvl-line"><span>' + r.join(' ') + '</span></span>').join('');
})();
document.querySelectorAll('[data-line-reveal], [data-line-stagger]').forEach(el => { initLineReveal(el); lineObserver.observe(el); });

/* Track Record 숫자 카운트업 (0→목표, 접두·접미 텍스트 보존) — company 전용 */
(function(){
  const nums = document.querySelectorAll('.tr-flush .num-card .n');
  if (!nums.length) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ease = t => 1 - Math.pow(1 - t, 3);
  const items = [...nums].map(el => {
    const full = el.textContent;
    const m = full.match(/[\d,]+/);
    if (!m) return null;
    const target = parseInt(m[0].replace(/,/g, ''), 10);
    if (target < 10) return null;               // 'GS 1등급' 등 소수치는 정적 유지
    return { el, full, target, from: Math.max(0, target - 10), start: m.index, len: m[0].length, comma: m[0].includes(',') };  // 목표 −10부터 촤라락 (250은 240부터)
  }).filter(Boolean);
  if (!items.length) return;
  const fmt = (n, c) => c ? n.toLocaleString('en-US') : String(n);
  function run(it){
    if (reduce) return;                          // 모션 최소화 설정이면 최종값 유지
    const pre = it.full.slice(0, it.start), suf = it.full.slice(it.start + it.len);
    const dur = 1100; let s = null;
    function step(ts){
      if (s === null) s = ts;
      const p = Math.min(1, (ts - s) / dur);
      it.el.textContent = pre + fmt(Math.round(it.from + ease(p) * (it.target - it.from)), it.comma) + suf;
      if (p < 1) requestAnimationFrame(step); else it.el.textContent = it.full;
    }
    requestAnimationFrame(step);
  }
  const obs = new IntersectionObserver((ents) => {
    ents.forEach(e => { if (e.isIntersecting){ run(items.find(i => i.el === e.target)); obs.unobserve(e.target); } });
  }, { threshold: 0.6 });
  items.forEach(i => obs.observe(i.el));
})();

/* ParaSta 비교표 강조열: 열 전체가 하나의 블록처럼 커지도록 */
const hlCells = document.querySelectorAll('table.cmp .hl');
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
      const target = parseFloat(en.target.dataset.val);
      const from = parseFloat(en.target.dataset.from) || 0;
      const dec = parseInt(en.target.dataset.decimals, 10) || 0;  /* 소수 자릿수 (없으면 0=정수, 기존과 동일) */
      const t0 = performance.now(), dur = 1100;
      (function tick(now){
        const p = Math.min((now - t0) / dur, 1);
        const e = 1 - Math.pow(1 - p, 3); /* easeOutCubic */
        en.target.textContent = (from + (target - from) * e).toLocaleString('en-US', {minimumFractionDigits: dec, maximumFractionDigits: dec});
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

/* Vision 헤더(아이브로우·타이틀·리드)는 스크롤 관찰자(revealObserver·lineObserver)가 처리 —
   패널이 화면에 들어올 때 리빌. 아이브로우 → 타이틀 → 리드 순서 스태거 부여 */
(function(){
  const hvPanel = document.querySelector('.hero-vision .vision-panel');
  if (!hvPanel) return;
  const hvEb = hvPanel.querySelector(':scope > .eyebrow');
  const hvLead = hvPanel.querySelector(':scope > .phero-lead');
  if (hvEb) hvEb.style.setProperty('--rvl-delay', '0ms');
  if (hvLead) hvLead.style.setProperty('--rvl-delay', '220ms');
})();

/* About 히어로 orb 배경 (company 전용) — orb-background.html 이식, .phero 크기에 맞춤 */
(function(){
  const cv = document.querySelector('body.hero-light .orb-bg');
  if(!cv) return;
  const ctx = cv.getContext('2d', { alpha:false });
  if(!ctx) return;
  const phero = cv.closest('.phero');
  const BACKGROUND='#ffffff', MUTED='#eceef5', VIOLET='#ded8fa';
  const CELL_SIZE=26, NOISE_SCALE=9, TIME_SPEED=0.085, MAX_RADIUS=2, CENTER_DENSITY=0.22, MAX_DPR=1.5, TAU=Math.PI*2;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let width=1, height=1, dpr=1, frame=0, startedAt=performance.now();
  const clamp=(v,a,b)=>Math.min(b,Math.max(a,v)); const smooth=v=>v*v*(3-2*v); const lerp=(a,b,t)=>a+(b-a)*t;
  function hash3(x,y,z){ let v=Math.imul(x,374761393)+Math.imul(y,668265263)+Math.imul(z,1442695041); v=Math.imul(v^(v>>>13),1274126177); return ((v^(v>>>16))>>>0)/4294967295; }
  function noise3(x,y,z){ const x0=Math.floor(x),y0=Math.floor(y),z0=Math.floor(z); const tx=smooth(x-x0),ty=smooth(y-y0),tz=smooth(z-z0);
    const n000=hash3(x0,y0,z0),n100=hash3(x0+1,y0,z0),n010=hash3(x0,y0+1,z0),n110=hash3(x0+1,y0+1,z0),n001=hash3(x0,y0,z0+1),n101=hash3(x0+1,y0,z0+1),n011=hash3(x0,y0+1,z0+1),n111=hash3(x0+1,y0+1,z0+1);
    const lo=lerp(lerp(n000,n100,tx),lerp(n010,n110,tx),ty), up=lerp(lerp(n001,n101,tx),lerp(n011,n111,tx),ty); return lerp(lo,up,tz); }
  function edgeVis(x,y){ const h=Math.abs(x/width-0.5)*2, v=Math.abs(y/height-0.5)*2; const d=Math.max(h,v); return 0.38+smooth(clamp((d-0.18)/0.7,0,1))*0.62; }
  function densityFor(x,y){ const h=Math.abs(x/width-0.5)*2, v=Math.abs(y/height-0.5)*2; const d=Math.max(h,v); return CENTER_DENSITY+smooth(clamp((d-0.16)/0.68,0,1))*(1-CENTER_DENSITY); }
  function radiusFor(val){ if(val<0.43||val>=0.9) return 0; const life=(val-0.43)/0.47; return MAX_RADIUS*smooth(Math.sin(life*Math.PI)); }
  function alphaFor(r,vis){ return clamp((r/MAX_RADIUS)*vis,0,0.58); }
  function drawOrb(x,y,r,val,vis){ if(r<0.45||vis<0.035) return; ctx.globalAlpha=alphaFor(r,vis); ctx.fillStyle=val>=0.65?VIOLET:MUTED; ctx.beginPath(); ctx.arc(x,y,r,0,TAU); ctx.fill(); }
  function render(now){ const elapsed=reduced.matches?24:(now-startedAt)/1000; const z=elapsed*TIME_SPEED+4.7;
    ctx.setTransform(dpr,0,0,dpr,0,0); ctx.globalAlpha=1; ctx.fillStyle=BACKGROUND; ctx.fillRect(0,0,width,height);
    const cols=Math.ceil(width/CELL_SIZE)+1, rows=Math.ceil(height/CELL_SIZE)+1;
    for(let r=0;r<rows;r++){ for(let c=0;c<cols;c++){ const x=c*CELL_SIZE+CELL_SIZE/2, y=r*CELL_SIZE+CELL_SIZE/2;
      const val=noise3(c/Math.max(1,cols)*NOISE_SCALE, r/Math.max(1,rows)*NOISE_SCALE, z); const vis=edgeVis(x,y);
      if(hash3(c,r,17)>densityFor(x,y)) continue; drawOrb(x,y,radiusFor(val),val,vis); } }
    ctx.globalAlpha=1; if(!reduced.matches && !document.hidden) frame=requestAnimationFrame(render); }
  function resize(){ const rc=phero.getBoundingClientRect(); width=Math.max(1,Math.round(rc.width)); height=Math.max(1,Math.round(rc.height));
    dpr=Math.min(MAX_DPR,Math.max(1,devicePixelRatio||1)); cv.width=Math.round(width*dpr); cv.height=Math.round(height*dpr);
    ctx.imageSmoothingEnabled=true; cancelAnimationFrame(frame); render(performance.now()); }
  if('ResizeObserver' in window){ let to; new ResizeObserver(()=>{ clearTimeout(to); to=setTimeout(resize,120); }).observe(phero); } else addEventListener('resize', resize, {passive:true});
  reduced.addEventListener?.('change', ()=>{ cancelAnimationFrame(frame); render(performance.now()); });
  document.addEventListener('visibilitychange', ()=>{ cancelAnimationFrame(frame); if(!document.hidden) render(performance.now()); });
  resize();
})();

/* About 히어로 큐브: 메인식 브러시 리빌 — base=심플(1.png) 위를 마우스로 긁으면 복합(2.png) 드러났다 사라짐 */
(function(){
  const fig = document.querySelector('.phero-figure-liquid');
  if(!fig) return;
  const canvas = fig.querySelector('.pf-canvas'), baseImg = fig.querySelector('.pf-base');
  if(!canvas || !baseImg) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if(reduced.matches) return;   // 정적 base만
  const ctx = canvas.getContext('2d');
  const brushRadius = 90, decay = 0.02;
  const dpr = Math.min(devicePixelRatio||1, 2);
  let revealSrc=null, revealReady=false, revealW=0, revealH=0;
  const ri = new Image(); ri.src='assets/about/cube-detail.png';
  ri.onload=()=>{ revealSrc=ri; revealW=ri.naturalWidth; revealH=ri.naturalHeight; revealReady=true; buildCover(); };
  let radius=brushRadius*dpr, diam=Math.ceil(radius*2), cw=0, ch=0;
  const cover=document.createElement('canvas'), brush=document.createElement('canvas'), brushCtx=brush.getContext('2d');
  brush.width=diam; brush.height=diam;
  function buildCover(){ if(cw===0||!revealReady) return; cover.width=cw; cover.height=ch; const c=cover.getContext('2d'); c.clearRect(0,0,cw,ch); const s=Math.max(cw/revealW,ch/revealH), dw=revealW*s, dh=revealH*s; c.drawImage(revealSrc,(cw-dw)/2,(ch-dh)/2,dw,dh); }
  function resize(){ const r=fig.getBoundingClientRect(); if(!r.width) return; cw=Math.max(1,Math.round(r.width*dpr)); ch=Math.max(1,Math.round(r.height*dpr)); canvas.width=cw; canvas.height=ch; canvas.style.width=r.width+'px'; canvas.style.height=r.height+'px'; buildCover(); }
  if('ResizeObserver' in window){ new ResizeObserver(resize).observe(fig); } else addEventListener('resize',resize,{passive:true});
  resize();
  const points=[]; let lastPt=null;
  addEventListener('pointermove',(e)=>{ const r=canvas.getBoundingClientRect(); const x=(e.clientX-r.left)*dpr, y=(e.clientY-r.top)*dpr;
    if(x<-radius||y<-radius||x>cw+radius||y>ch+radius){ lastPt=null; return; }
    if(lastPt){ const dx=x-lastPt.x, dy=y-lastPt.y, dist=Math.hypot(dx,dy), step=Math.max(radius*0.3,1), n=Math.min(Math.ceil(dist/step),60);
      for(let i=1;i<=n;i++) points.push({x:lastPt.x+dx*i/n, y:lastPt.y+dy*i/n}); }
    else points.push({x,y});
    lastPt={x,y}; }, {passive:true});
  function stamp(x,y){ const c=diam/2; brushCtx.clearRect(0,0,diam,diam); brushCtx.globalCompositeOperation='source-over';
    const g=brushCtx.createRadialGradient(c,c,0,c,c,radius); g.addColorStop(0,'rgba(255,255,255,1)'); g.addColorStop(.55,'rgba(255,255,255,.82)'); g.addColorStop(1,'rgba(255,255,255,0)');
    brushCtx.fillStyle=g; brushCtx.fillRect(0,0,diam,diam);
    brushCtx.globalCompositeOperation='source-in'; brushCtx.drawImage(cover,x-c,y-c,diam,diam,0,0,diam,diam);
    ctx.globalCompositeOperation='source-over'; ctx.drawImage(brush,x-c,y-c); }
  let idle=0;
  function tick(){ const drawing=points.length>0; if(drawing) idle=0; else idle++;
    if(!drawing&&idle>120){ ctx.clearRect(0,0,cw,ch); if(!document.hidden) requestAnimationFrame(tick); return; }
    const fade=drawing?decay:Math.min(decay+idle*0.004,0.5);
    ctx.globalCompositeOperation='destination-out'; ctx.fillStyle='rgba(0,0,0,'+fade+')'; ctx.fillRect(0,0,cw,ch);
    if(drawing&&revealReady){ for(const p of points) stamp(p.x,p.y); } points.length=0;
    if(!document.hidden) requestAnimationFrame(tick); }
  requestAnimationFrame(tick);
})();

/* About 히어로 큐브: 스크롤 살짝만 해도 심플→복합(detail) 전체 전환 (transition으로 슥) */
(function(){
  const fig = document.querySelector('.phero-figure-liquid');
  const detail = fig && fig.querySelector('.pf-detail');
  const base = fig && fig.querySelector('.pf-base');
  if(!detail || !base) return;
  let ticking=false;
  function update(){ ticking=false; const on = scrollY > 40;
    detail.style.opacity = on ? '1' : '0';
    base.style.opacity = on ? '0' : '1';   /* 스크롤 시 뒤 심플 큐브 숨김 (완전 교체) */
  }
  addEventListener('scroll', ()=>{ if(!ticking){ ticking=true; requestAnimationFrame(update); } }, {passive:true});
  update();
})();

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

/* ---------- 데모 오버레이 ---------- */
const demo = document.getElementById('demo');
const demoPanel = document.getElementById('demoPanel');
// 페이지가 window.DEMO_STEPS를 지정하지 않으면 기본 샘플(placeholder) 사용
// code는 라인 배열 (백슬래시·따옴표 이스케이프 회피 — join으로 개행)
const DEMO_STEPS = window.DEMO_STEPS || [
  { title:'발급 요청', desc:'API 한 번으로 스테이블코인을 발행합니다. 필요한 규제 파라미터가 요청에 함께 전달됩니다.',
    code:['<span class="c">// 발행 요청</span>', 'POST /v1/issue', '  asset: <span class="s">KRWx</span>', '  amount: <span class="s">100000</span>'] },
  { title:'온체인 기록', desc:'발행 내역과 준비자산 증빙(PoR)이 온체인에 기록되어, 누구나 검증할 수 있습니다.',
    code:['<span class="c">// 트랜잭션 확정</span>', '<span class="k">status</span>: <span class="s">confirmed</span>', '<span class="k">txHash</span>: <span class="s">0x9f...c2</span>'] },
  { title:'운영 관제', desc:'발행 이후의 유통·상환·모니터링을 통합 어드민 한 곳에서 관리합니다.',
    code:['<span class="c">// 실시간 모니터링</span>', 'GET /v1/reserves', '<span class="k">ratio</span>: <span class="s">102.4%</span>'] },
];
let demoIdx = 0;
function demoRender(){
  const s = DEMO_STEPS[demoIdx];
  document.getElementById('demoStepEb').textContent = 'STEP ' + String(demoIdx + 1).padStart(2, '0');
  document.getElementById('demoStepT').textContent = s.title;
  document.getElementById('demoStepD').textContent = s.desc;
  document.getElementById('demoCode').innerHTML = Array.isArray(s.code) ? s.code.join('\\n') : s.code;
  document.getElementById('demoMock').innerHTML = s.mock || '';
  document.getElementById('demoPrev').disabled = demoIdx === 0;
  document.getElementById('demoNext').disabled = demoIdx === DEMO_STEPS.length - 1;
  document.querySelectorAll('#demoDots .demo-dot').forEach((d, n) => d.classList.toggle('is-active', n === demoIdx));
}
(function initDemoDots(){
  const dots = document.getElementById('demoDots');
  if (!dots) return;
  DEMO_STEPS.forEach((_, i) => {
    const b = document.createElement('button');
    b.className = 'demo-dot' + (i === 0 ? ' is-active' : ''); b.type = 'button';
    b.setAttribute('aria-label', (i + 1) + '단계');
    b.addEventListener('click', () => { demoIdx = i; demoRender(); });
    dots.appendChild(b);
  });
})();
function openDemo(){ demoIdx = 0; demoRender(); demo.classList.add('open'); demo.setAttribute('aria-hidden', 'false'); stopScroll(); document.addEventListener('keydown', onDemoKey); }
function closeDemo(){ demo.classList.remove('open'); demo.setAttribute('aria-hidden', 'true'); startScroll(); document.removeEventListener('keydown', onDemoKey); }
function onDemoKey(e){ if (e.key === 'Escape') closeDemo(); }
demo.addEventListener('click', (e) => { if (e.target === demo) closeDemo(); });
document.getElementById('demoPrev').addEventListener('click', () => { if (demoIdx > 0){ demoIdx--; demoRender(); } });
document.getElementById('demoNext').addEventListener('click', () => { if (demoIdx < DEMO_STEPS.length - 1){ demoIdx++; demoRender(); } });
document.querySelectorAll('.demo-tab').forEach(t => t.addEventListener('click', () => {
  document.querySelectorAll('.demo-tab').forEach(x => x.classList.toggle('active', x === t));
}));

/* 비교표 모바일 탭 전환 */
document.querySelectorAll('.cmp-tabs').forEach(wrap => {
  wrap.addEventListener('click', (e) => {
    const btn = e.target.closest('.cmpt-btn');
    if (!btn) return;
    const idx = btn.dataset.cmpt;
    wrap.querySelectorAll('.cmpt-btn').forEach(b => {
      const on = b === btn;
      b.classList.toggle('active', on);
      b.setAttribute('aria-selected', String(on));
    });
    wrap.querySelectorAll('.cmpt-panel').forEach(p =>
      p.classList.toggle('active', p.dataset.cmptPanel === idx));
    btn.scrollIntoView({ behavior:'smooth', block:'nearest', inline:'center' });
  });
});
/* 탭바 좌우 화살표: 스크롤 위치에 따라 표시 */
document.querySelectorAll('.cmpt-barwrap').forEach(bw => {
  const bar = bw.querySelector('.cmpt-bar');
  const prev = bw.querySelector('.cmpt-nav.prev');
  const next = bw.querySelector('.cmpt-nav.next');
  const upd = () => {
    prev.classList.toggle('show', bar.scrollLeft > 4);
    next.classList.toggle('show', bar.scrollLeft < bar.scrollWidth - bar.clientWidth - 4);
  };
  bar.addEventListener('scroll', upd, { passive:true });
  window.addEventListener('resize', upd);
  upd();
  prev.addEventListener('click', () => bar.scrollBy({ left:-180, behavior:'smooth' }));
  next.addEventListener('click', () => bar.scrollBy({ left:180, behavior:'smooth' }));
});

/* Use Cases 캐러셀 (portx·parasta 등) — 인스턴스별 스코프로 한 페이지 여러 개 지원 */
document.querySelectorAll('.uc-carousel').forEach(uc => {
  const slides = uc.querySelectorAll('.uc-slide');
  if (!slides.length) return;
  let idx = 0;
  const dots = uc.querySelector('.uc-dots');
  const sync = i => dots?.querySelectorAll('.uc-dot').forEach((d, n) => d.classList.toggle('is-active', n === i));
  const show = i => { slides.forEach((s, n) => s.classList.toggle('is-active', n === i)); idx = i; sync(i); };
  uc.querySelector('.uc-prev')?.addEventListener('click', () => show((idx - 1 + slides.length) % slides.length));
  uc.querySelector('.uc-next')?.addEventListener('click', () => show((idx + 1) % slides.length));
  // 닷 인디케이터 (모바일 전용 노출)
  if (dots){
    slides.forEach((_, i) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'uc-dot' + (i === 0 ? ' is-active' : '');
      b.setAttribute('aria-label', (i + 1) + '번째 사례');
      b.addEventListener('click', () => show(i));
      dots.appendChild(b);
    });
  }
  // 모바일 스와이프(플리킹)
  const wrap = uc.querySelector('.uc-slides');
  let x = null;
  wrap?.addEventListener('touchstart', e => { x = e.touches[0].clientX; }, { passive:true });
  wrap?.addEventListener('touchend', e => {
    if (x === null) return;
    const dx = e.changedTouches[0].clientX - x; x = null;
    if (Math.abs(dx) < 40) return;
    show(dx < 0 ? (idx + 1) % slides.length : (idx - 1 + slides.length) % slides.length);
  }, { passive:true });
  // 슬라이드 안 <video>를 카드 호버 시 재생
  slides.forEach(sl => {
    const vids = sl.querySelectorAll('video');
    if (!vids.length) return;
    sl.addEventListener('mouseenter', () => vids.forEach(v => v.play()));
    sl.addEventListener('mouseleave', () => vids.forEach(v => { v.pause(); v.currentTime = 0; }));
  });
});
/* Use Cases 탭 (parasta) — 탭바 버튼으로 패널(캐러셀) 전환 */
document.querySelectorAll('.uc-tabbar').forEach(bar => {
  const btns = [...bar.querySelectorAll('.uc-tabbtn')];
  const scope = bar.closest('.sec') || document;
  const panels = [...scope.querySelectorAll('.uc-tabpanel')];
  btns.forEach((b, i) => b.addEventListener('click', () => {
    btns.forEach((x, n) => x.classList.toggle('is-active', n === i));
    panels.forEach((p, n) => p.classList.toggle('is-active', n === i));
  }));
});

/* global click routing — 메인(parameta.html)과 동일 */
document.addEventListener('click', (e) => {
  const demoBtn = e.target.closest('[data-demo]');
  if (demoBtn){ e.preventDefault(); openDemo(); return; }
  const closeDemoBtn = e.target.closest('[data-close-demo]');
  if (closeDemoBtn){ closeDemo(); return; }
  const modalBtn = e.target.closest('[data-modal]');
  if (modalBtn){
    if (modalBtn.hasAttribute('data-close-menu')) closeMenu();
    openModal();
    return;
  }
  const openMenuBtn = e.target.closest('[data-open-menu]');
  if (openMenuBtn){ openMenu(); return; }
  const closeMenuBtn = e.target.closest('[data-close-menu]:not([data-modal])');
  if (closeMenuBtn){ closeMenu(); return; }
  const closeModalBtn = e.target.closest('[data-close-modal]');
  if (closeModalBtn){ closeModal(); return; }
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
  const list = li.closest('.ht2-body') || li.closest('ul');   /* 히스토리: 시대 3그룹 통합 스코프 */
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

/* Insights: 페이지네이션 공통 (최소 5페이지 표시, 빈 페이지는 disabled — 레퍼런스 동작) */
const PAGER_ARR = {
  prev:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="15 6 9 12 15 18"/></svg>',
  next:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 6 15 12 9 18"/></svg>'
};
/* 페이지 최상단으로 부드럽게 — 네이티브 behavior:'smooth'가 안 먹는 환경(프리뷰 등) 대비 rAF 수동 애니메이션 */
function pagerScrollTop(){
  const start = window.scrollY; if(start <= 0) return;
  const t0 = performance.now(), dur = 620;
  const step = now => {
    const p = Math.min(1, (now - t0) / dur);
    const e = p < 0.5 ? 4*p*p*p : 1 - Math.pow(-2*p + 2, 3) / 2;   /* easeInOutCubic — 시작·끝 부드럽게 */
    window.scrollTo(0, Math.round(start * (1 - e)));
    if(p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
function paintPager(pager, sec, cur, real, go){
  pager.innerHTML = '';
  const mk = (label, page, on, dis) => {
    const b = document.createElement('button'); b.type = 'button';
    if(label === 'prev' || label === 'next'){ b.innerHTML = PAGER_ARR[label]; b.setAttribute('aria-label', label === 'prev' ? '이전' : '다음'); }
    else b.textContent = label;
    if(on) b.classList.add('is-on');
    if(dis) b.disabled = true;
    b.addEventListener('click', () => { go(page); pagerScrollTop(); });   /* 페이지 최상단으로 스르륵 */
    pager.appendChild(b);
  };
  const dots = () => { const sp = document.createElement('span'); sp.className = 'pager-dots'; sp.textContent = '\u2026'; pager.appendChild(sp); };
  mk('prev', cur-1, false, cur <= 1);
  /* 중간 윈도 5개 + 첫·끝 페이지 고정, 사이 간격은 … (총 6~7개). 예: 6 → 1 … 4 5 6 7 8 … 12 */
  if(real <= 7){
    for(let n = 1; n <= real; n++) mk(String(n), n, n === cur, false);
  } else {
    const start = Math.min(Math.max(1, cur - 2), real - 4);   // 윈도 5개, 가장자리 클램프
    const end = start + 4;
    if(start > 1){ mk('1', 1, cur === 1, false); if(start > 2) dots(); }   // 앞쪽 첫 페이지 + 간격
    for(let n = start; n <= end; n++) mk(String(n), n, n === cur, false);
    if(end < real){ if(end < real - 1) dots(); mk(String(real), real, cur === real, false); }   // 뒤쪽 간격 + 끝 페이지
  }
  mk('next', cur+1, false, cur >= real);
}
/* Insights: 블로그 탭 필터 + 페이지네이션 */
const blogSec = document.querySelector('[data-blog]');
if(blogSec){
  const tabs = [...blogSec.querySelectorAll('.blog-tab')];
  const posts = [...blogSec.querySelectorAll('.blog-item')];
  const pager = blogSec.querySelector('.pager');
  const PER = 9; let filter = 'all', cur = 1;  // 3열 × 3행
  const elig = () => posts.filter(p => filter === 'all' || p.dataset.cat === filter);
  // 카드 타이틀 2줄 초과 시 가운데 생략(단어 경계, 앞·뒤 유지) — CSS로 불가해 측정 후 처리
  function clampMiddle(el){
    const full = el.dataset.full || (el.dataset.full = el.textContent.trim());
    el.textContent = full;
    const lh = parseFloat(getComputedStyle(el).lineHeight) || 28;
    const max = lh * 2 + 2;
    if(el.scrollHeight <= max) return;
    const w = full.split(/\s+/);
    for(let keep = w.length - 1; keep >= 2; keep--){
      const head = Math.ceil(keep / 2), tail = keep - head;
      el.textContent = w.slice(0, head).join(' ') + ' … ' + w.slice(w.length - tail).join(' ');
      if(el.scrollHeight <= max) return;
    }
  }
  const clampVisible = () => posts.filter(p => !p.classList.contains('hidden'))
    .forEach(p => { const t = p.querySelector('.bf-title'); if(t) clampMiddle(t); });
  function paint(){
    const e = elig();
    const real = Math.max(1, Math.ceil(e.length / PER));
    if(cur > real) cur = real;
    posts.forEach(p => p.classList.add('hidden'));
    e.slice((cur-1)*PER, cur*PER).forEach(p => p.classList.remove('hidden'));
    if(pager) paintPager(pager, blogSec, cur, real, page => { cur = page; paint(); });
    requestAnimationFrame(() => requestAnimationFrame(clampVisible));   // 레이아웃 확정 후 측정
  }
  tabs.forEach(t => {
    const f = t.dataset.filter;
    if(f !== 'all' && !posts.some(p => p.dataset.cat === f)) t.disabled = true;
    t.addEventListener('click', () => {
      tabs.forEach(o => o.classList.toggle('is-on', o === t));
      filter = f; cur = 1; paint();
    });
  });
  paint();
  if(document.fonts && document.fonts.ready) document.fonts.ready.then(clampVisible);   // 웹폰트 스왑 후 재측정
  addEventListener('load', clampVisible);
  let rz; addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(clampVisible, 150); });
}
/* 공통 커스텀 드롭다운 (.drop) — 시스템 셀렉트 대체. 선택 시 data-value 갱신 + change 이벤트 */
const drops = [...document.querySelectorAll('.drop')];
if(drops.length){
  drops.forEach(drop => {
    const btn = drop.querySelector('.drop-btn');
    const label = drop.querySelector('.drop-label');
    const opts = [...drop.querySelectorAll('.drop-menu li')];
    btn.addEventListener('click', e => {
      e.stopPropagation();
      const willOpen = !drop.classList.contains('open');
      drops.forEach(d => { d.classList.remove('open'); d.querySelector('.drop-btn').setAttribute('aria-expanded', 'false'); });
      drop.classList.toggle('open', willOpen);
      btn.setAttribute('aria-expanded', String(willOpen));
    });
    opts.forEach(o => o.addEventListener('click', () => {
      opts.forEach(x => x.classList.toggle('is-on', x === o));
      drop.dataset.value = o.dataset.value;
      label.textContent = o.textContent;
      drop.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
      drop.dispatchEvent(new CustomEvent('change'));
    }));
  });
  const closeAll = () => drops.forEach(d => { d.classList.remove('open'); d.querySelector('.drop-btn').setAttribute('aria-expanded', 'false'); });
  document.addEventListener('click', e => { if(!e.target.closest('.drop')) closeAll(); });
  document.addEventListener('keydown', e => { if(e.key === 'Escape') closeAll(); });
}
/* Insights(Newsroom): 보도자료 리스트 — 연도·검색 필터 + 페이지네이션(10개씩) */
const pressSec = document.querySelector('[data-press]');
if(pressSec){
  const items = [...pressSec.querySelectorAll('.press-item')];
  const pager = pressSec.querySelector('.pager');
  const selY = pressSec.querySelector('.news-sel-year');
  const selM = pressSec.querySelector('.news-sel-month');
  const inp = pressSec.querySelector('.news-search input');
  const clearBtn = pressSec.querySelector('.ns-clear');
  const searchBtn = pressSec.querySelector('.ns-btn');
  const emptyEl = pressSec.querySelector('.news-empty');
  const PER = 10; let year = 'all', month = 'all', kw = '', cur = 1;
  const elig = () => items.filter(r =>
    (year === 'all' || r.dataset.year === year) &&
    (month === 'all' || r.dataset.month === month) &&
    (!kw || r.querySelector('.nr-title').textContent.toLowerCase().includes(kw)));
  function paintP(){
    const e = elig();
    const real = Math.max(1, Math.ceil(e.length / PER));
    if(cur > real) cur = real;
    items.forEach(r => r.classList.add('hidden'));
    e.slice((cur-1)*PER, cur*PER).forEach(r => r.classList.remove('hidden'));
    if(emptyEl) emptyEl.hidden = e.length > 0;
    if(pager){
      pager.style.display = e.length ? '' : 'none';
      paintPager(pager, pressSec, cur, real, page => { cur = page; paintP(); });
    }
  }
  function applyKw(){
    kw = inp.value.trim().toLowerCase(); cur = 1;
    paintP();
  }
  if(selY) selY.addEventListener('change', () => { year = selY.dataset.value; cur = 1; paintP(); });
  if(selM) selM.addEventListener('change', () => { month = selM.dataset.value; cur = 1; paintP(); });
  if(inp){
    /* 입력 중엔 필터하지 않음 — X 버튼 표시만 갱신, 검색은 Enter·돋보기에서 실행 */
    inp.addEventListener('input', () => {
      if(clearBtn) clearBtn.hidden = !inp.value;
      if(!inp.value && kw){ kw = ''; cur = 1; paintP(); }  /* 전부 지우면 필터 해제 */
    });
    inp.addEventListener('keydown', e => { if(e.key === 'Enter') applyKw(); });
  }
  if(searchBtn) searchBtn.addEventListener('click', applyKw);
  if(clearBtn) clearBtn.addEventListener('click', () => {
    inp.value = ''; clearBtn.hidden = true; kw = ''; cur = 1; paintP(); inp.focus();
  });
  paintP();
}
/* Press 상세: 본문 텍스트 복사 (clipboard API + execCommand 폴백) */
const pdCopy = document.querySelector('[data-copy]');
if(pdCopy){
  const copyText = async txt => {
    try { await navigator.clipboard.writeText(txt); return true; }
    catch(e){
      const ta = document.createElement('textarea');
      ta.value = txt; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      const ok = document.execCommand('copy'); ta.remove(); return ok;
    }
  };
  pdCopy.addEventListener('click', async () => {
    const bodyEl = document.querySelector('.pd-body, .post-body');
    if(!bodyEl) return;
    const ok = await copyText(bodyEl.innerText);
    const label = pdCopy.querySelector('.pd-copy-label');
    if(!label) return;
    const orig = label.textContent;
    label.textContent = ok ? '복사되었습니다' : '복사 실패';
    setTimeout(() => { label.textContent = orig; }, 1500);
  });
}
/* Press 상세: 전체 이미지 다운로드 — 본문 전체를 세로 긴 캡처 PNG 한 장으로 저장 (html2canvas 지연 로드) */
const pdDl = document.querySelector('[data-dl-images]');
if(pdDl){
  let busy = false;
  pdDl.addEventListener('click', async () => {
    if(busy) return;
    const bodyEl = document.querySelector('.pd-body, .post-body');
    if(bodyEl == null) return;
    busy = true;
    const label = pdDl.querySelector('.hspring');
    const orig = label.childNodes[0].nodeValue;
    label.childNodes[0].nodeValue = '저장 중... ';
    try{
      if(!window.htmlToImage){
        await new Promise((res, rej) => {
          const sc = document.createElement('script');
          sc.src = 'https://unpkg.com/html-to-image@1.11.13/dist/html-to-image.js';
          sc.onload = res; sc.onerror = rej;
          document.head.appendChild(sc);
        });
      }
      const blob = await htmlToImage.toBlob(bodyEl, {
        backgroundColor: '#ffffff', pixelRatio: 2,
        style: { padding: '3rem 2rem' }
      });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = (document.title.split(' | ')[0] || 'press') + '.png';
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(a.href);
    }catch(e){}
    label.childNodes[0].nodeValue = orig;
    busy = false;
  });
}
/* Press 상세: 공유하기 모달 — SNS 링크 + URL 복사 */
const pdShare = document.querySelector('.pd-share');
const psModal = document.getElementById('pd-share-modal');
if(pdShare && psModal){
  const urlInput = psModal.querySelector('.psm-url input');
  const copyBtn = psModal.querySelector('.psm-copy');
  const links = {
    x:    u => 'https://twitter.com/intent/tweet?url=' + u + '&text=' + encodeURIComponent(document.title),
    fb:   u => 'https://www.facebook.com/sharer/sharer.php?u=' + u,
    line: u => 'https://social-plugins.line.me/lineit/share?url=' + u,
    mail: u => 'mailto:?subject=' + encodeURIComponent(document.title) + '&body=' + u,
  };
  const openM = () => {
    const u = encodeURIComponent(location.href);
    psModal.querySelectorAll('[data-share]').forEach(a => { a.href = links[a.dataset.share](u); });
    urlInput.value = location.href;
    psModal.classList.add('open'); psModal.setAttribute('aria-hidden', 'false');
  };
  const closeM = () => { psModal.classList.remove('open'); psModal.setAttribute('aria-hidden', 'true'); };
  pdShare.addEventListener('click', openM);
  psModal.querySelectorAll('[data-psm-close]').forEach(el => el.addEventListener('click', closeM));
  document.addEventListener('keydown', e => { if(e.key === 'Escape') closeM(); });
  if(copyBtn) copyBtn.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(urlInput.value); }
    catch(e){ urlInput.select(); document.execCommand('copy'); }
    const orig = copyBtn.textContent;
    copyBtn.textContent = '복사됨';
    setTimeout(() => { copyBtn.textContent = orig; }, 1500);
  });
}

/* 블로그 상세: On this page 스크롤스파이 — 스크롤 위치 기준 현재 섹션 하이라이트 */
const postSide = document.querySelector('.post-side');
if(postSide){
  const links = [...postSide.querySelectorAll('a')];
  const map = new Map();
  links.forEach(a => { const id = (a.getAttribute('href') || '').split('#')[1]; const t = id && document.getElementById(id); if(t) map.set(a, t); });
  const sections = [...map.values()];
  const setActive = t => links.forEach(l => l.classList.toggle('is-active', map.get(l) === t));
  function pick(){
    const line = innerHeight * 0.4;   // 뷰포트 40% 지점 — 섹션이 화면 상단부에 들어오면 미리 활성(스크롤보다 앞서 전환)
    let cur = sections[0];
    for(const s of sections){ if(s.getBoundingClientRect().top <= line) cur = s; else break; }
    setActive(cur);
  }
  if(sections.length){
    pick();
    addEventListener('scroll', pick, { passive: true });
    addEventListener('resize', pick);
    lenis.on('scroll', pick);   // Lenis 스무스 스크롤(휠) 대응
    // 목차 클릭 → 헤더 오프셋 두고 부드럽게 이동 (페이저와 동일한 rAF 방식 — 프리뷰/Lenis 공존)
    const HEAD = 124;   // GNB + CTA 밴드 여유
    const smoothTo = (y) => {
      const s = window.scrollY, d = y - s, t0 = performance.now(), dur = 640;
      const step = now => {
        const p = Math.min(1, (now - t0) / dur);
        const e = p < 0.5 ? 4*p*p*p : 1 - Math.pow(-2*p + 2, 3) / 2;
        window.scrollTo(0, Math.round(s + d * e));
        if(p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    links.forEach(a => a.addEventListener('click', e => {
      const t = map.get(a);
      if(!t) return;
      e.preventDefault();
      smoothTo(Math.max(0, t.getBoundingClientRect().top + window.scrollY - HEAD));
      history.replaceState(null, '', a.getAttribute('href'));
      setActive(t);
    }));
  }
}

/* dev grid toggle */
document.getElementById('dev-grid-toggle').addEventListener('click', () => {
  document.body.classList.toggle('show-grid');
});

/* About 히어로: evervault풍 암호화 문자 매트릭스 (company 전용) */
(function(){
  const cv = document.querySelector('body.company .ev-matrix');
  if(!cv) return;
  const ctx = cv.getContext('2d');
  const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/<>{}[]#'.split('');
  const CELL = 20;          // 셀 한 변(css px)
  const FONT = 12;          // 글자 크기(css px)
  const INK = '14,12,39';   // --ink-rgb
  const MAXA = 0.16;        // 최대 투명도
  const reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
  let dpr = 1, cols = 0, rows = 0, chars = [], op = [], tgt = [], raf = 0, last = 0;
  const rnd = a => a[(Math.random()*a.length)|0];

  function build(){
    const r = cv.getBoundingClientRect();
    if(!r.width || !r.height) return false;
    dpr = Math.min(devicePixelRatio||1, 2);
    cv.width = Math.round(r.width*dpr); cv.height = Math.round(r.height*dpr);
    cols = Math.ceil(r.width/CELL); rows = Math.ceil(r.height/CELL);
    const n = cols*rows;
    chars = new Array(n); op = new Float32Array(n); tgt = new Float32Array(n);
    for(let i=0;i<n;i++){ chars[i]=rnd(GLYPHS); const v=Math.random()*MAXA*0.5; op[i]=v; tgt[i]=v; }
    ctx.setTransform(dpr,0,0,dpr,0,0);
    ctx.font = FONT+'px ui-monospace, SFMono-Regular, Menlo, monospace';
    ctx.textBaseline = 'top';
    return true;
  }
  function draw(){
    const w = cv.width/dpr, h = cv.height/dpr;
    ctx.clearRect(0,0,w,h);
    for(let y=0;y<rows;y++){ for(let x=0;x<cols;x++){
      const i = y*cols+x, a = op[i];
      if(a < 0.008) continue;
      ctx.fillStyle = 'rgba('+INK+','+a.toFixed(3)+')';
      ctx.fillText(chars[i], x*CELL+3, y*CELL+3);
    }}
  }
  function step(t){
    raf = requestAnimationFrame(step);
    if(t-last < 55) return;      // ~18fps 스로틀
    last = t;
    const n = cols*rows;
    const churn = Math.max(6, (n*0.02)|0);   // 프레임당 셔머/스크램블 셀 수
    for(let k=0;k<churn;k++){
      const i = (Math.random()*n)|0;
      tgt[i] = Math.random()*MAXA;
      if(Math.random()<0.5) chars[i] = rnd(GLYPHS);
    }
    for(let i=0;i<n;i++) op[i] += (tgt[i]-op[i])*0.12;   // 목표치로 이징
    draw();
  }
  function start(){ if(!build()) return; if(reduce){ draw(); return; } cancelAnimationFrame(raf); last=0; raf=requestAnimationFrame(step); }

  if('ResizeObserver' in window){
    let to; new ResizeObserver(()=>{ clearTimeout(to); to=setTimeout(start,150); }).observe(cv);
  } else addEventListener('resize', ()=>{ clearTimeout(window.__evto); window.__evto=setTimeout(start,150); });
  start();
})();

</script>
"""

ARW = '<svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M7 17 17 7M8 7h9v9"/></svg>'
MARK = '<svg class="icn" viewBox="0 0 48 48" aria-hidden="true"><path fill="currentColor" d="M24 2c2.2 13.8 7.9 19.6 22 22-14.1 2.4-19.8 8.2-22 22-2.2-13.8-7.9-19.6-22-22 14.1-2.4 19.8-8.2 22-22Z"/></svg>'

def card(title, desc='', kicker='', tags=None, tone='dark', media=False, quote=None, cite=None, sm=True, media_hover=None):
    """카드 공통 토큰 — 색·간격·타이포는 CSS 단일 소스, 조합만 선언.
    tone : 'dark'(잉크) | 'gray'(라이트 그레이 — 코어모듈式, 어디서든 사용 가능)
    media: True → 상단 이미지 영역(full-bleed) + 키커·텍스트 하단 블록
    media_hover: 경로 → 호버 시 이미지 영역 배경을 이 이미지로 스왑(--media-hover)
    kicker/tags/quote+cite : 옵션 요소
    """
    cls = 'work-card static' + (' sm' if sm else '') + (' grouped' if media else '') + (' t-gray' if tone == 'gray' else '')
    if isinstance(media, str):
        _mv = f"--media:url('{media}')" + (f"; --media-hover:url('{media_hover}')" if media_hover else '')
        mstyle = f' style="{_mv}"'
    else:
        mstyle = ''
    t = ''.join(f'<span class="tag">{x}</span>' for x in (tags or []))
    q = f'<blockquote class="work-quote">&ldquo;{quote}&rdquo;<cite>{cite}</cite></blockquote>' if quote else ''
    meta = f'<div class="work-meta"><span>{kicker}</span></div>' if kicker else ''
    if media:
        # 키커를 하단 텍스트 블록에 붙여 상단은 이미지 영역으로 비움
        return (f'<article class="{cls}"{mstyle}>'
                f'<div class="work-bottom">{meta}<h3>{title}</h3><p>{desc}</p>{q}'
                f'{f"<div class=work-tags>{t}</div>" if t else ""}</div></article>')
    return (f'<article class="{cls}">'
            f'{meta}'
            f'<div class="work-bottom"><h3>{title}</h3><p>{desc}</p>{q}'
            f'{f"<div class=work-tags>{t}</div>" if t else ""}</div></article>')

def dark_card(cap, title, desc, tags=None, quote=None, cite=None, sm=True, grouped=False):
    # (구 API) card()로 위임 — 새 코드는 card() 직접 사용
    return card(title, desc, kicker=cap, tags=tags, quote=quote, cite=cite, sm=sm, media=grouped)

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

def h2(text, mx='24ch', cls=''):
    return f'<h2 class="sec-h2{cls}" data-line-reveal style="max-width:{mx}"><span class="rvl-line"><span>{text}</span></span></h2>'

def card_grid(cards, cols=3):
    lis = ''.join(f'<li class="rvl" style="--rvl-y:40px; --rvl-delay:{i*90}ms">{c}</li>' for i, c in enumerate(cards))
    return f'<ul class="cards-{cols}">{lis}</ul>'
cards_wrap = card_grid  # 구 이름 하위호환

def nums(items, cols=3):
    # items: dict(cap, n, sub) — n은 <small> 포함 가능
    lis = ''.join(
        f'<li class="rvl" style="--rvl-delay:{i*90}ms"><div class="light-card num-card">'
        f'<span class="cap">{it["cap"]}</span><div class="n">{it["n"]}</div><p>{it["sub"]}</p></div></li>'
        for i, it in enumerate(items))
    return f'<ul class="cards-{cols}">{lis}</ul>'

def ww_compare(now_title, after_title, items, now_cap='지금', after_cap='도입 후'):
    """With/Without 좌우 비교 (Problem 문제→해결). items: (문제 제목, 문제 설명, 해결 제목, 해결 설명)"""
    nows = ''.join(f'<li><span class="ww-mk">✕</span><div><b>{pt}</b><p>{pd}</p></div></li>'
                   for pt, pd, _, _ in items)
    afters = ''.join(f'<li><span class="ww-mk">✓</span><div><b>{st}</b><p>{sd}</p></div></li>'
                     for _, _, st, sd in items)
    return (f'<div class="ww rvl" style="--rvl-y:40px">'
            f'<div class="ww-col ww-now"><span class="ww-cap">{now_cap}</span><div class="ww-t">{now_title}</div><ul>{nows}</ul></div>'
            f'<div class="ww-col ww-after"><span class="ww-cap">{after_cap}</span><div class="ww-t">{after_title}</div><ul>{afters}</ul></div>'
            f'</div>')

def ex_cards(items, cols=3):
    # items: (name, brand_hex, txt) — PortX Supported Exchanges와 동일한 ico-card ex-card, 호버 시 브랜드컬러
    lis = ''.join(
        f'<li class="rvl" style="--rvl-y:40px; --rvl-delay:{i*90}ms">'
        f'<article class="ico-card ex-card" style="--brand:{b}; --brand-txt:var(--{t})">'
        f'<span class="ex-ico"></span><h3>{n}</h3></article></li>'
        for i, (n, b, t) in enumerate(items))
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

def icon_card(icon_svg, title, desc):
    # 컴팩트 아이콘 카드: 아이콘 상단 + 타이틀 + 짧은 설명 (Privy 스타일, 다크)
    return (f'<article class="ico-card">'
            f'<span class="ic" aria-hidden="true">{icon_svg}</span>'
            f'<h3>{title}</h3><p>{desc}</p></article>')

def usecase_carousel(items, label='사례 선택'):
    # Use Cases 캐러셀 포맷(portx) 재사용 — 슬라이드: 썸네일 + 카테고리 플래그 + 타이틀 + 본문. items:[dict(cat,title,desc)]
    ap = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5L8 12l7 7"/></svg>'
    an = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg>'
    total = len(items)
    slides = []
    for i, it in enumerate(items):
        flag = f'<span class="uc-flag">{it["cat"]}</span>' if it.get('cat') else ''
        active = ' is-active' if i == 0 else ''
        num = f'<span class="uc-num"><b>{i + 1:02d}</b> / {total:02d}</span>'
        slides.append(f'<article class="uc-slide{active}"><div class="uc-thumb" aria-hidden="true"></div><div class="uc-title"><h3>{it["title"]}</h3>{flag}</div><p>{it["desc"]}</p>{num}</article>')
    return ('<div class="uc-carousel">'
            f'<button class="uc-arrow uc-prev rvl rvl-op" type="button" aria-label="이전 사례">{ap}</button>'
            f'<div class="uc-slides rvl" style="--rvl-y:40px">{"".join(slides)}</div>'
            f'<div class="uc-dots" aria-label="{label}"></div>'
            f'<button class="uc-arrow uc-next rvl rvl-op" type="button" aria-label="다음 사례">{an}</button>'
            '</div>')

def exchange_card(name, logo=None, brand=None, dark_text=False, desc=None, num=None, gray=False, logo_dark=False):
    # 거래소 카드: 원형 로고 자리 + 이름. brand=호버 시 카드가 그 브랜드 컬러로 (dark_text=밝은 브랜드용)
    # desc=타이틀 아래 서브카피, num=타이틀 위 번호 (기능 카드 겸용), gray=라이트 그레이 채움 변형
    # logo_dark=어두운 심볼(기본 상태에서 반대색=흰색으로 반전, 다크 카드에서 보이게)
    cls_ico = 'ex-ico' + (' ex-logo' if logo else '') + (' ex-logo-inv' if (logo and logo_dark) else '')
    ico = f'<span class="{cls_ico}"{f" style={chr(34)}--logo:url({chr(39)}{logo}{chr(39)}){chr(34)}" if logo else ""}>{f"<img src={chr(34)}{logo}{chr(34)} alt={chr(34)}{chr(34)} loading={chr(34)}lazy{chr(34)}>" if logo else ""}</span>'
    style = f' style="--brand:{brand}; --brand-txt:{"var(--ink)" if dark_text else "var(--white)"}"' if (brand and not gray) else ''
    cls = 'ico-card ex-card' + (' ex-gray' if gray else '')
    n = f'<span class="ex-num">{num}</span>' if num else ''
    d = f'<p>{desc}</p>' if desc else ''
    return f'<article class="{cls}"{style}>{ico}{n}<h3>{name}</h3>{d}</article>'

def icon_row(*rows):
    # 원형 아이콘 + 라벨 행 (센터 정렬, 간격 단일 토큰) — icon_row([행1]), icon_row([행1],[행2])
    # 아이템: 'Binance'(플레이스홀더 원) 또는 ('assets/…png','Binance')(로고)
    row_html=[]
    for items in rows:
        lis=[]
        for it in items:
            if isinstance(it, tuple):
                ico = f'<span class="ex-ico"><img src="{it[0]}" alt=""></span>'; name = it[1]
            else:
                ico = '<span class="ex-ico"></span>'; name = it
            lis.append(f'<span class="ex-item">{ico}<span class="ex-name">{name}</span></span>')
        row_html.append(f'<div class="ex-row">{"".join(lis)}</div>')
    return f'<div class="ex-rows rvl">{"".join(row_html)}</div>'

def partner_logos(logos=None):
    # 함께한 파트너 로고 세트 (assets/partners/) — 마퀴 트랙에 2회 반복 삽입
    logos = logos or [('logo-shinhan', '신한은행'), ('logo-nh', 'NH농협은행'), ('logo-nh-securities', 'NH투자증권'),
                      ('logo-samsung-securities', '삼성증권'), ('logo-samsung', '삼성'), ('logo-kb', 'KB'),
                      ('logo-ibk', 'IBK기업은행'), ('logo-hanwha', '한화')]
    imgs = ''.join(f'<img src="assets/partners/{f}.svg" alt="{name}" loading="lazy">' for f, name in logos)
    return f'<div class="pt-set" aria-hidden="false">{imgs}</div>'

def cert_marquee(items):
    # 인증·수상: 로고(위) + 텍스트(아래) 아이템을 마퀴로 순환 (2회 반복해 무한 루프)
    def one(label):
        return f'<div class="cert-item"><span class="cert-logo" aria-hidden="true"></span><span class="cert-label">{label}</span></div>'
    row = ''.join(one(x) for x in items)
    return (f'<div class="rvl cert-marquee pt-marquee" aria-label="인증 · 수상">'
            f'<div class="pt-track cert-track">{row}{row}</div></div>')

def hist_timeline(items):
    # History C안: 세로 좌측 레일 + 노드 + 큰 연도 + 그레이 내용 카드
    # 항목: (연도, 대표내용) 또는 (연도, 대표내용, [세부...]) — 세부가 있으면 <details> 드롭다운
    lis = []
    for i, it in enumerate(items):
        y, t, subs = (it[0], it[1], it[2] if len(it) > 2 else None)
        if subs:
            sub_lis = ''.join(f'<li>{s}</li>' for s in subs)
            body = (f'<div class="ht-card ht-acc">'
                    f'<input type="checkbox" id="ht-acc-{i}" hidden>'
                    f'<label for="ht-acc-{i}"><p>{t}</p><span class="ht-chev" aria-hidden="true"></span></label>'
                    f'<div class="ht-subwrap"><ul class="ht-sub">{sub_lis}</ul></div></div>')
        else:
            body = f'<div class="ht-card"><p>{t}</p></div>'
        lis.append(f'<li class="ht-item rvl" style="--rvl-y:24px; --rvl-delay:{i*70}ms">'
                   f'<span class="ht-node"></span><div class="ht-yr">{y}</div>{body}</li>')
    return f'<ul class="ht-list">{"".join(lis)}</ul>'

# company 파트너 로고 세트 (미래에셋 포함)
COMPANY_LOGOS = [('logo-samsung', '삼성'), ('logo-samsung-securities', '삼성증권'), ('logo-mirae', '미래에셋'),
                 ('logo-nh', 'NH농협'), ('logo-nh-securities', 'NH투자증권'), ('logo-shinhan', '신한'),
                 ('logo-ibk', 'IBK기업은행'), ('logo-kb', 'KB')]

def legend_marks():
    items = [('on','지원'), ('mid','일부 지원'), ('off','미지원')]
    lis = ''.join(f'<span class="lg"><span class="mk {lv}">{mark_svg(lv)}</span>{lb}</span>' for lv, lb in items)
    return f'<div class="why-legend rvl">{lis}</div>'

def compare_table(headers, body_rows, hl=1, legend=None, tabs=False):
    # headers: [행라벨열='', 열1, 열2 ...]  / hl: headers 인덱스(1-base) 하이라이트 열
    # body_rows: dict(label, cells=[열1, 열2 ...])  cells는 문자열(cell() 사용 가능)
    # tabs=True: 모바일(<768)에서 표 대신 열 단위 탭 UI 병행 출력
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
    tabs_html = ''
    if tabs:
        cols = headers[1:]
        first = hl - 1 if 0 < hl <= len(cols) else 0  # 기본 선택 = 하이라이트 열
        btns = ''.join(
            f'<button class="cmpt-btn{" active" if i == first else ""}{" is-hl" if (i + 1) == hl else ""}" '
            f'data-cmpt="{i}" role="tab" aria-selected="{"true" if i == first else "false"}">{h}</button>'
            for i, h in enumerate(cols))
        panels = ''
        for i, h in enumerate(cols):
            rows = ''.join(
                f'<div class="cmpt-row"><div class="cmpt-label">{r["label"]}</div>'
                f'<div class="cmpt-cell">{r["cells"][i]}</div></div>'
                for r in body_rows)
            panels += (f'<div class="cmpt-panel{" active" if i == first else ""}'
                       f'{" is-hl" if (i + 1) == hl else ""}" data-cmpt-panel="{i}">{rows}</div>')
        chev_l = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M10 3 5 8l5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        chev_r = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        tabs_html = (f'<div class="cmp-tabs rvl">'
                     f'<div class="cmpt-barwrap">'
                     f'<button class="cmpt-nav prev" aria-label="이전 탭">{chev_l}</button>'
                     f'<div class="cmpt-bar" role="tablist">{btns}</div>'
                     f'<button class="cmpt-nav next" aria-label="다음 탭">{chev_r}</button>'
                     f'</div>{panels}</div>')
    return (f'{leg}{tabs_html}<div class="cmp-wrap rvl"><table class="cmp">'
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

def col_chart(cols, title=None, note=None):
    # cols: dict(l 라벨, v 값, w 높이%, hi=선택) — bar_chart의 세로 변형
    head = f'<p class="barc-title">{title}</p>' if title else ''
    n = len(cols)
    stacks = ''.join(
        f'<div class="colc-stack{" hi" if c.get("hi") else ""}">'
        f'<span class="colc-v">{c["v"]}</span>'
        f'<div class="colc-bar" style="height:calc({c["w"]}*var(--colc-h)/100)"></div></div>'
        for c in cols)
    labels = ''.join(f'<span class="colc-l">{c["l"]}</span>' for c in cols)
    nt = f'<p class="sec-note">{note}</p>' if note else ''
    return (f'<div class="colc rvl">{head}'
            f'<div class="colc-panel">'
            f'<div class="colc-plot" style="grid-template-columns:repeat({n},1fr)">{stacks}</div>'
            f'<div class="colc-labels" style="grid-template-columns:repeat({n},1fr)">{labels}</div>'
            f'{nt}'
            f'</div></div>')

def chips(items):
    return '<div class="chip-row rvl">' + ''.join(f'<span class="chip">{x}</span>' for x in items) + '</div>'

def adopt_compare(rows):
    # How to Adopt 비교: [(name, term, [steps], hi)] 를 위아래 가로 타임라인으로. hi=빠른 경로(짧은 트랙+보라)
    out = []
    for name, term, steps, hi in rows:
        nodes = ''.join(f'<div class="ac-step"><span class="ac-dot"></span><span class="ac-lbl">{s}</span></div>' for s in steps)
        out.append(f'<div class="ac-row{" ac-hi" if hi else ""}">'
                   f'<div class="ac-meta"><h3>{name}</h3><span class="ac-time">{term}</span></div>'
                   f'<div class="ac-track {"fast" if hi else "slow"}">{nodes}</div></div>')
    return f'<div class="adopt-compare rvl">{"".join(out)}</div>'

def routes(items, active):
    return '<div class="routes rvl">' + ''.join(
        f'<a class="route{" on" if href == active else ""}" href="{href}">{label}</a>'
        for label, href in items) + '</div>'

def note(text):
    return f'<p class="sec-note rvl">{text}</p>'

def lead_p(text, mx=None):
    style = f' style="max-width:{mx}"' if mx else ''
    return f'<p class="phero-lead sec-lead rvl"{style}>{text}</p>'

# 12칼럼 그리드에서 n칸까지 폭 (그리드 변수 기반 정확 스냅)
def grid_cols_w(n):
    return f'calc((100% - 11 * var(--grid-gap)) / 12 * {n} + {n-1} * var(--grid-gap))'

def sec_head(label, title, lead=None, layout='stack', mx='24ch', body=False, lead_mx=None):
    """섹션 헤더 공통 토큰 (타이포는 parasta-section-type-set 기준).
    유형:
      · sec_head('Eyebrow', '타이틀')                          — 아이브로우 + 타이틀 (하단 3rem)
      · sec_head('Eyebrow', '타이틀', '서브카피')               — 서브카피: 타이틀에 붙음 (0.25rem)
      · sec_head('Eyebrow', '타이틀', '본문', body=True)        — 바디카피: 문단 간격 유지 (2rem)
      · sec_head('Eyebrow', '타이틀', '서브카피', layout='split') — 좌 타이틀셋 / 우 서브 (900↓ 스택)
    """
    if layout == 'center':  # 중앙정렬 변형
        inner = eyebrow(label) + h2(title, mx, cls=(' has-lead' if lead else ''))
        if lead: inner += lead_p(lead)
        return f'<div class="sh-center">{inner}</div>'
    if layout == 'split' and lead:
        return (f'<div class="sec-head-split">'
                f'<div class="shl">{eyebrow(label)}{h2(title, mx)}</div>'
                f'<div class="shr"><p class="phero-lead rvl">{lead}</p></div></div>')
    if lead and not body:  # 서브카피: 타이틀 하단 0.25rem (has-lead 변형)
        return eyebrow(label) + h2(title, mx, cls=' has-lead') + lead_p(lead, lead_mx)
    if lead:               # 바디카피: 타이틀 하단 2rem (has-body 변형)
        return eyebrow(label) + h2(title, mx, cls=' has-body') + lead_p(lead, lead_mx)
    return eyebrow(label) + h2(title, mx)

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
    eyebrow='Company',
    h1_lines=['About PARAMETA'],
    lead='Web2의 경험과 이해에 Web3 기술을 더해<br>지갑 중심의 WalletFi 생태계를 만듭니다.',
    crumb='Company — 회사소개',
    body_class='company',  # 라이트 화이트 히어로 + evervault풍 문자 매트릭스 (확정)
    hero_visual='',
    hero_figure='''<div class="phero-figure phero-figure-liquid" aria-hidden="true">
      <img class="pf-base" src="assets/about/cube-simple.png" alt="" width="480" height="480">
      <img class="pf-detail" src="assets/about/cube-detail.png" alt="" width="480" height="480">
      <canvas class="pf-canvas"></canvas>
    </div>''',
    # 히어로 배경(라이트+패턴)을 안 짤리게 통으로 — Vision을 히어로 안으로 편입, 다크 박스는 카드로 얹음
    hero_extra=f'''<div class="shell hero-vision">
  <div class="vision-panel rvl" style="--rvl-y:40px; --rvl-s:.99">
  {sec_head('Vision', 'Web2와 Web3를 잇는 WalletFi 생태계', '파라메타는 금융, 공공, 민간 서비스에 블록체인을 전개해 온 경험으로 규제와 시장 환경을 깊이 이해하고, 그 위에 퍼블릭 블록체인과 DeFi 기반의 Web3 기술을 더합니다. 이를 바탕으로 자산 보관과 거래, 다양한 금융 서비스를 하나의 디지털 지갑에서 이용하는 WalletFi 생태계를 만들어갑니다.', mx='none', lead_mx='38rem')}
  <div class="wfd rvl" style="--rvl-y:24px">
    <div class="wfd-band wfd-side">
      <div class="wfd-t">전통금융 <em>TradFi</em></div>
      <div class="wfd-d">금융기관 · 핀테크 등</div>
    </div>
    <div class="wfd-core-wrap">
      <div class="wfd-band wfd-core">
        <div class="wfd-t">WalletFi</div>
        <div class="wfd-s">스테이블코인<br>자산 토큰화<br>크로스보더 결제</div>
      </div>
    </div>
    <div class="wfd-band wfd-side">
      <div class="wfd-t">탈중앙화 금융 <em>DeFi</em></div>
      <div class="wfd-d">CEX · DEX 사용자 등</div>
    </div>
    <div class="wfd-infra">
      <div class="wfd-infra-t">Wallet Infrastructure</div>
      <div class="wfd-chips">K-BTF · loopchain · PDS · BFS · DID</div>
    </div>
  </div>
  </div>
</div>''',
    content='''
<section class="tr-flush"><div class="shell sec">
  <div class="eyebrow dark rvl rvl-op"><span class="dot"></span>Track Record</div><h2 class="sec-h2 has-lead" data-line-reveal style="max-width:24ch"><span class="rvl-line"><span>10년의 트랙레코드,<br class="br-m"> 숫자로 증명한 신뢰</span></span></h2><p class="phero-lead sec-lead rvl">2016년부터 쌓아온 실적이 파라메타의 기술을 증명합니다.</p>
  <ul class="cards-3"><li class="rvl" style="--rvl-delay:0ms"><article class="work-card static grouped t-gray"><div class="work-bottom"><div class="work-meta"><span>Since 2016</span></div><h3 data-count-from="0">10 Years</h3><p>국내 1세대 Web3 인프라 기업</p></div></article></li><li class="rvl" style="--rvl-delay:90ms"><article class="work-card static grouped t-gray"><div class="work-bottom"><div class="work-meta"><span>Investment</span></div><h3 data-count-from="240">250억 원</h3><p>누적 투자유치</p></div></article></li><li class="rvl" style="--rvl-delay:180ms"><article class="work-card static grouped t-gray"><div class="work-bottom"><div class="work-meta"><span>Revenue</span></div><h3 data-count-from="740">750억 원+</h3><p>누적 매출 (2016~2025)</p></div></article></li></ul>
  <script>/* Track Record 수치 카운트업: 스크롤 인 시 data-count-from → 원래 숫자로 (접미어 유지) */
  (function(){
    var els = document.querySelectorAll('.tr-flush h3[data-count-from]');
    if (!els.length || !('IntersectionObserver' in window)) return;
    function run(el){
      var m = el.textContent.match(/^([\\d,]+)([\\s\\S]*)$/); if (!m) return;
      var to = parseInt(m[1].replace(/,/g,''), 10), suffix = m[2];
      var from = parseInt(el.getAttribute('data-count-from'), 10) || 0;
      var t0 = null, DUR = 1100;
      function tick(ts){
        if (t0 === null) t0 = ts;
        var p = Math.min((ts - t0) / DUR, 1);
        var e = 1 - Math.pow(1 - p, 3);   /* ease-out cubic */
        el.textContent = Math.round(from + (to - from) * e) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(en){ if (en.isIntersecting){ run(en.target); io.unobserve(en.target); } });
    }, { threshold: .5 });
    els.forEach(function(el){ io.observe(el); });
  })();
  </script>
  <div class="recog-chips rvl">
    <span class="rc-label sub-t" data-line-reveal><span class="rvl-line"><span>인증 수상</span></span></span>
    <div class="aw-marquee rvl" style="--rvl-y:40px; --rvl-delay:150ms" aria-label="인증 수상 목록">
      <div class="pt-track">
        <div class="aw-set">
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-gs.svg" alt="" onerror="this.style.display='none'"><i>GS</i></span><figcaption><b>GS인증 1등급</b><span>loopchain SW품질</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-tcb.svg" alt="" onerror="this.style.display='none'"><i>TI-1</i></span><figcaption><b>기술평가 TI-1</b><span>최고 등급</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-csap.svg" alt="" onerror="this.style.display='none'"><i>CSAP</i></span><figcaption><b>CSAP 인증</b><span>블록체인 최초</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-msit.svg" alt="" onerror="this.style.display='none'"><i>MSIT</i></span><figcaption><b>과기정통부 장관 표창</b><span>과학기술정보통신부 2018</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-kisa.svg" alt="" onerror="this.style.display='none'"><i>KISA</i></span><figcaption><b>기술특례상장 A등급</b><span>KISA 2년 연속</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-fsc.svg" alt="" onerror="this.style.display='none'"><i>FSC</i></span><figcaption><b>혁신금융서비스 지정</b><span>금융위원회 2019</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-swaward.svg" alt="" onerror="this.style.display='none'"><i>SW</i></span><figcaption><b>SW품질대상 최우수상</b><span>과기정통부 2019</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-jeju.svg" alt="" onerror="this.style.display='none'"><i>JEJU</i></span><figcaption><b>제주특별자치도 표창</b><span>제주안심코드 2021</span></figcaption></figure>
        </div>
        <div class="aw-set" aria-hidden="true">
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-gs.svg" alt="" onerror="this.style.display='none'"><i>GS</i></span><figcaption><b>GS인증 1등급</b><span>loopchain SW품질</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-tcb.svg" alt="" onerror="this.style.display='none'"><i>TI-1</i></span><figcaption><b>기술평가 TI-1</b><span>최고 등급</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-csap.svg" alt="" onerror="this.style.display='none'"><i>CSAP</i></span><figcaption><b>CSAP 인증</b><span>블록체인 최초</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-msit.svg" alt="" onerror="this.style.display='none'"><i>MSIT</i></span><figcaption><b>과기정통부 장관 표창</b><span>과학기술정보통신부 2018</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-kisa.svg" alt="" onerror="this.style.display='none'"><i>KISA</i></span><figcaption><b>기술특례상장 A등급</b><span>KISA 2년 연속</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-fsc.svg" alt="" onerror="this.style.display='none'"><i>FSC</i></span><figcaption><b>혁신금융서비스 지정</b><span>금융위원회 2019</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-swaward.svg" alt="" onerror="this.style.display='none'"><i>SW</i></span><figcaption><b>SW품질대상 최우수상</b><span>과기정통부 2019</span></figcaption></figure>
          <figure class="aw-item"><span class="aw-logo"><img src="assets/awards/logo-jeju.svg" alt="" onerror="this.style.display='none'"><i>JEJU</i></span><figcaption><b>제주특별자치도 표창</b><span>제주안심코드 2021</span></figcaption></figure>
        </div>
      </div>
    </div>
  </div>
</div></section>

<section class="firsts"><div class="shell sec">
  <div class="eyebrow dark rvl rvl-op"><span class="dot"></span>Industry Firsts</div><h2 class="sec-h2 has-lead" data-line-reveal style="max-width:24ch"><span class="rvl-line"><span>블록체인 산업의 첫 기록</span></span></h2><p class="phero-lead sec-lead rvl">파라메타는 산업이 처음 가는 길을 먼저 열어왔습니다.</p>
  <div class="firsts-hero rvl">
    <div class="fh-big" aria-hidden="true"><span class="fh-num">1<span class="st">st</span></span><span class="fh-cap">세계·국내 최초 4건</span></div>
    <ul class="fh-list">
      <li><span class="fh-chip world">세계 최초</span>블록체인 공동인증 상용화<span class="fh-sub">증권사 26개사 · 2017</span></li>
      <li><span class="fh-chip">국내 최초</span>금융권 DID 실명인증 상용화<span class="fh-sub">2020</span></li>
      <li><span class="fh-chip">국내 최초</span>블록체인 서비스 CSAP 인증<span class="fh-sub">MyID 2.0 · 2025</span></li>
      <li><span class="fh-chip">국내 최초</span>W3C DID Method Registry 등재</li>
    </ul>
  </div>
  
  
  
  <div class="rvl firsts-eco">
    <div class="eco-head">
      <div class="ally-head"><span class="sub-t">주요 얼라이언스 파트너와 함께<br>블록체인 생태계를 만들어갑니다</span></div>
      <div class="eco-pills">
        <span class="eco-pill"><b>Stablecoin Alliance</b><i>초대 의장사</i></span>
        <span class="eco-pill"><b>MyID Alliance</b><i>의장사</i></span>
      </div>
    </div>
  </div>
  <div class="rvl ally-marquee-wrap" style="margin-top:var(--space-32); --rvl-y:40px">
    <div class="meta-t">PARTNERS 86+</div>
    <div class="pt-marquee ally-logos" aria-label="파트너 로고"><div class="pt-track"><div class="pt-set" aria-hidden="false"><img src="assets/partners/logo-shinhan.svg" alt="신한" loading="lazy"><img src="assets/partners/logo-samsung-securities.svg" alt="삼성증권" loading="lazy"><img src="assets/partners/logo-nh-securities.svg" alt="NH투자증권" loading="lazy"><img src="assets/partners/logo-mirae.svg" alt="미래에셋" loading="lazy"><img src="assets/partners/logo-samsung.svg" alt="삼성" loading="lazy"><img src="assets/partners/logo-nh.svg" alt="NH농협" loading="lazy"><img src="assets/partners/logo-ibk.svg" alt="IBK기업은행" loading="lazy"><img src="assets/partners/logo-kb.svg" alt="KB" loading="lazy"><img src="assets/partners/logo-hanwha.svg" alt="한화" loading="lazy"><img src="assets/partners/logo-hyundai.svg" alt="현대" loading="lazy"></div><div class="pt-set" aria-hidden="true"><img src="assets/partners/logo-shinhan.svg" alt="신한" loading="lazy"><img src="assets/partners/logo-samsung-securities.svg" alt="삼성증권" loading="lazy"><img src="assets/partners/logo-nh-securities.svg" alt="NH투자증권" loading="lazy"><img src="assets/partners/logo-mirae.svg" alt="미래에셋" loading="lazy"><img src="assets/partners/logo-samsung.svg" alt="삼성" loading="lazy"><img src="assets/partners/logo-nh.svg" alt="NH농협" loading="lazy"><img src="assets/partners/logo-ibk.svg" alt="IBK기업은행" loading="lazy"><img src="assets/partners/logo-kb.svg" alt="KB" loading="lazy"><img src="assets/partners/logo-hanwha.svg" alt="한화" loading="lazy"><img src="assets/partners/logo-hyundai.svg" alt="현대" loading="lazy"></div></div></div>
  </div>
</div></section>


<section><div class="shell sec">
  <div class="ht2">
<div class="cm-grid">
  <div class="cm-head">
    <div class="cm-sticky">
      <div class="cm-head-in rvl" style="--rvl-y:20px">
        <div class="eyebrow dark"><span class="dot"></span>History</div>
        <div class="ht2-fade">
          <div class="ht2-layer on"><h2 class="sec-h2" style="max-width:24ch">2023 — 2026<br>디지털자산 인프라 확장</h2></div>
          <div class="ht2-layer"><h2 class="sec-h2" style="max-width:24ch">2019 — 2022<br>DID 상용화와 공공 확산</h2></div>
          <div class="ht2-layer"><h2 class="sec-h2" style="max-width:24ch">2016 — 2018<br>기술 기반 구축</h2></div>
        </div>
      </div>
    </div>
  </div>
  <div class="ht2-body">
    <div class="ht2-group rvl" style="--rvl-y:24px" data-rng="2023 — 2026" data-title="디지털자산 인프라 확장">
      <div class="ht2-era-head"><h3 class="ht2-t">2023 — 2026<br>디지털자산 인프라 확장</h3></div>

    <ul class="ht2-faq"><li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:0ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2026</b><span class="ht2-tt">APAC 확장, ADB 채권 포럼 국경 간 거래 표준모델 발표 등 시장 확대</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2026</b><span class="ht2-tt">APAC 확장, ADB 채권 포럼 국경 간 거래 표준모델 발표 등 시장 확대</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">06월</span><span>인도네시아 HARA와 전략적 업무협약 체결, APAC 사업 확장 본격화</span></li>
      <li><span class="m">02월</span><span>'스테이블코인·STO 무료 컨설팅' 실시, 디지털자산 사업 기회 확대 지원</span></li>
      <li><span class="m">02월</span><span>ADB 주관 채권 포럼(ABMF)에서 온체인 KYC 기반 국경 간 거래 표준 모델 발표</span></li>
      <li><span class="m">01월</span><span>리스크엑스(RiskX)와 스테이블코인 기반 글로벌 디지털 자산·금융 사업 협력</span></li>
    </ul></div></div></li>
    <li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:60ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2025</b><span class="ht2-tt">Stablecoin Alliance 초대 의장사 선임</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2025</b><span class="ht2-tt">Stablecoin Alliance 초대 의장사 선임</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">12월</span><span>Stablecoin Alliance 출범, 초대 의장사 선임</span></li>
      <li><span class="m">12월</span><span>코스포·네이버클라우드·네이버 아라비아 3자 MOU, broof로 블록체인에 영구 기록</span></li>
      <li><span class="m">11월</span><span>국가AI전략위원회 위촉증, 블록체인 증명서 broof로 발급</span></li>
      <li><span class="m">10월</span><span>조달청 디지털서비스몰 등록으로 공공기관 도입 경로 확보</span></li>
      <li><span class="m">10월</span><span>쿠콘·인피닛블록과 스테이블코인 인프라 확장 MoU 체결</span></li>
      <li><span class="m">09월</span><span>하나테크와 글로벌 스테이블코인 결제지원 MoU 체결</span></li>
      <li><span class="m">08월</span><span>국내 최초 유럽 DPP 대응 '블록체인 기반 배터리 여권 플랫폼' 구축 수주</span></li>
      <li><span class="m">05월</span><span>DID 플랫폼 'MyID 2.0', 블록체인 서비스 최초 CSAP 인증 획득</span></li>
    </ul></div></div></li>
    <li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:120ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2024</b><span class="ht2-tt">K-BTF 공공 블록체인 공동인프라 사업자 선정</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2024</b><span class="ht2-tt">K-BTF 공공 블록체인 공동인프라 사업자 선정</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">11월</span><span>Web3Auth와 블록체인 신원인증 글로벌 확대 MoU 체결</span></li>
      <li><span class="m">06월</span><span>국내 최초·유일 CSAP 기반 공공용 블록체인 서비스(K-BTF) 사업자 선정</span></li>
      <li><span class="m">03월</span><span>90억 원 규모 추가 투자 유치, 누적 투자금 250억 원 달성</span></li>
    </ul></div></div></li>
    <li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:180ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2023</b><span class="ht2-tt">PARAMETA 리브랜딩, 디지털자산 인프라 기업 전환</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2023</b><span class="ht2-tt">PARAMETA 리브랜딩, 디지털자산 인프라 기업 전환</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">12월</span><span>핑거랩스·블로코엑스와이지와 웹3 생태계 확장 MOU 체결</span></li>
      <li><span class="m">11월</span><span>2023 블록체인 진흥주간 과학기술정보통신부 장관 표창 수상 (김종협 대표)</span></li>
      <li><span class="m">11월</span><span>신한EZ손해보험·피엠그로우와 전기차 배터리 잔존 수명 인증 생태계 구축 파트너십 체결</span></li>
      <li><span class="m">10월</span><span>비트블루와 IP·콘텐츠 토큰증권 플랫폼 구축 MOU 체결</span></li>
      <li><span class="m">09월</span><span>기술신용평가 최고 등급 TI-1 획득</span></li>
      <li><span class="m">09월</span><span>글로벌 노드 프로바이더 Alchemy·QuickNode와 국내 최초 Web3 인프라 파트너십 체결</span></li>
      <li><span class="m">09월</span><span>loopchain 성능 측정 및 향상 방안 리포트 공개</span></li>
      <li><span class="m">08월</span><span>솔브릭코리아와 국내 최초 '태양광 발전소 토큰증권 플랫폼' 구축 MOU 체결</span></li>
      <li><span class="m">08월</span><span>카스투게더와 국내 최초 '모빌리티 토큰증권 플랫폼' 구축 MOU 체결</span></li>
      <li><span class="m">08월</span><span>페블러스와 블록체인 기반 AI 모델 유통 생태계 구축 MOU 체결</span></li>
      <li><span class="m">07월</span><span>플루토스파트너스와 국내 최초 '부동산 NPL 토큰증권 플랫폼' 구축 MOU 체결</span></li>
      <li><span class="m">07월</span><span>DID 기반 경북형 공공마이데이터 플랫폼 '모이소 경상북도' 고도화(2단계) 사업 수주</span></li>
      <li><span class="m">06월</span><span>독일 '인터배터리 유럽 2023'에서 전기차 배터리 잔존 수명 인증 서비스 공개</span></li>
      <li><span class="m">05월</span><span>2023 블록체인 민간분야 집중사업 '전기차 배터리 잔존 수명 인증 서비스' 수주</span></li>
      <li><span class="m">03월</span><span>NH투자증권 토큰증권 협의체 'STO 비전그룹' 기술 기업 참여</span></li>
      <li><span class="m">03월</span><span>유하와 STO 활용 '콘텐츠 조각투자 플랫폼' 구축 협업</span></li>
      <li><span class="m">03월</span><span>그리너리와 '탄소배출권 조각투자 플랫폼' 구축 전략적 파트너십 체결</span></li>
      <li><span class="m">03월</span><span>스피젠-파이프라인과 모빌리티 조각투자·멤버십 NFT 플랫폼 구축 협력</span></li>
      <li><span class="m">02월</span><span>㈜파라메타로 사명 변경</span></li>
      <li><span class="m">02월</span><span>'파라메타 서비스(Parameta Service)' 출시</span></li>
      <li><span class="m">02월</span><span>코스닥 기술특례상장 모의 기술성 평가 A등급 획득</span></li>
      <li><span class="m">02월</span><span>경북형 공공마이데이터 플랫폼 '모이소 경상북도'에 블록체인 DID 기술 적용</span></li>
      <li><span class="m">02월</span><span>시지온과 웹3 데이터 프로토콜 '퍼미(Perme)' 구축 전략적 파트너십 체결</span></li>
      <li><span class="m">02월</span><span>피에스엑스와 토큰증권 플랫폼 공동 개발 전략적 파트너십 체결</span></li>
      <li><span class="m">01월</span><span>인텔렉추얼브릿지와 지식재산권 NFT 플랫폼 사업 구축 MOU 체결</span></li>
    </ul></div></div></li></ul>
  
    </div>
    <div class="ht2-group rvl" style="--rvl-y:24px" data-rng="2019 — 2022" data-title="DID 상용화와 공공 확산">
      <div class="ht2-era-head"><h3 class="ht2-t">2019 — 2022<br>DID 상용화와 공공 확산</h3></div>

    <ul class="ht2-faq"><li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:0ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2022</b><span class="ht2-tt">블록체인 프레임워크 'Parameta Framework' 공개</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2022</b><span class="ht2-tt">블록체인 프레임워크 'Parameta Framework' 공개</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">12월</span><span>마이아이디, 금융위원회 혁신금융서비스 규제개선 요청 통과</span></li>
      <li><span class="m">08월</span><span>1세대 마이데이터 사업자 '깃플'과 블록체인 기반 마이데이터 사업 협약 체결</span></li>
      <li><span class="m">07월</span><span>'경상북도 디지털 신원인증 마이데이터 플랫폼' 구축 사업 수주</span></li>
      <li><span class="m">06월</span><span>자체 블록체인 프레임워크 '파라메타 프레임워크(Parameta Framework)' 공개</span></li>
      <li><span class="m">06월</span><span>broof로 제26회 제주국제관광마라톤축제 블록체인 완주증 발급</span></li>
      <li><span class="m">04월</span><span>국내 최초 블록체인 기반 통합 서비스 플랫폼 강원도 '나야나'에 DID 기술 적용</span></li>
      <li><span class="m">01월</span><span>아이콘재단·투바이트와 인터체인 NFT 플랫폼 '하바(HAVAH)' 구축 전략적 파트너십 체결</span></li>
    </ul></div></div></li>
    <li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:60ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2021</b><span class="ht2-tt">NH농협은행 DID 실명인증 출시, 금융·기업·공공으로 적용 확산</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2021</b><span class="ht2-tt">NH농협은행 DID 실명인증 출시, 금융·기업·공공으로 적용 확산</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">12월</span><span>제주안심코드, 제주특별자치도 표창패 수여</span></li>
      <li><span class="m">12월</span><span>신한카드와 블록체인·DID 사업 전략적 제휴</span></li>
      <li><span class="m">12월</span><span>포스코그룹 거점 오피스에 블록체인 DID 기반 출입인증 시스템 적용</span></li>
      <li><span class="m">12월</span><span>코로나19 예방접종 서비스 출시</span></li>
      <li><span class="m">12월</span><span>제주특별자치도관광협회·제주산학융합원과 MOU 체결</span></li>
      <li><span class="m">11월</span><span>제주형 공유물류 플랫폼 '모당' 구축 사업 참여</span></li>
      <li><span class="m">11월</span><span>아이콘루프 컨소시엄, 스마트팜 빅데이터 플랫폼 출시</span></li>
      <li><span class="m">10월</span><span>블록체인 기반 선박검사관리플랫폼 서비스 출시</span></li>
      <li><span class="m">08월</span><span>NH농협은행 DID 금융실명인증 서비스 출시</span></li>
      <li><span class="m">06월</span><span>포항 체인지업 그라운드에 블록체인 DID 기반 통합 신원인증 시스템 구축</span></li>
      <li><span class="m">01월</span><span>블록체인 기반 '모바일 운전면허증 서비스' ICT 규제 샌드박스 임시허가</span></li>
    </ul></div></div></li>
    <li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:120ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2020</b><span class="ht2-tt">신한은행 국내 최초 금융권 DID 실명인증 상용화</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2020</b><span class="ht2-tt">신한은행 국내 최초 금융권 DID 실명인증 상용화</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">12월</span><span>제주형 관광방역 시스템 '제주안심코드' 공식 출시 (이후 누적 이용자 218만 명)</span></li>
      <li><span class="m">12월</span><span>서울블록체인지원센터와 블록체인 연동형(DID) 방문객 관리 시스템 공동개발 협약</span></li>
      <li><span class="m">12월</span><span>강원도 정부혁신 분야 공로 표창장 수상</span></li>
      <li><span class="m">12월</span><span>기술혁신형 중소기업(INNO-BIZ) 인증 획득</span></li>
      <li><span class="m">10월</span><span>고신대복음병원과 스마트 헬스케어 구축 MOU 체결</span></li>
      <li><span class="m">09월</span><span>사람인HR과 국내 최초 채용 서비스 전반에 블록체인 기술 적용</span></li>
      <li><span class="m">09월</span><span>이니텍과 DID 기반 차세대 사설인증 사업 추진 MOU 체결</span></li>
      <li><span class="m">09월</span><span>포항시·포스코·포스텍 등과 포항 데이터 생태계 구축 MOU 체결</span></li>
      <li><span class="m">08월</span><span>신한은행과 국내 최초 금융권 DID 실명인증 상용화</span></li>
      <li><span class="m">08월</span><span>제주도와 블록체인 DID 신원인증 관광방역 MOU 체결</span></li>
      <li><span class="m">07월</span><span>브릿지 라운드 투자 유치, 누적 투자금 160억 원 달성</span></li>
      <li><span class="m">05월</span><span>IITP 분산 디지털 신원 관리·보안 기술 연구개발 참여</span></li>
      <li><span class="m">05월</span><span>블록체인 기반 강원도형 만성질환 통합 관리 플랫폼 시범사업 주관 사업자 선정</span></li>
      <li><span class="m">04월</span><span>고성능 합의 알고리즘 'LFT2' 공개</span></li>
      <li><span class="m">02월</span><span>포스텍과 국내 최초 전체 졸업생 대상 블록체인 학위기 발급</span></li>
      <li><span class="m">01월</span><span>사람인HR과 블록체인 기반 인사 채용 생태계 구축 MOU 체결</span></li>
    </ul></div></div></li>
    <li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:180ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2019</b><span class="ht2-tt">분산ID 'MyID' 혁신금융서비스 지정</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2019</b><span class="ht2-tt">분산ID 'MyID' 혁신금융서비스 지정</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">11월</span><span>'마이아이디 얼라이언스(MyID Alliance)' 출범, 의장사 선임</span></li>
      <li><span class="m">11월</span><span>대한민국 SW제품 품질대상 최우수상 수상</span></li>
      <li><span class="m">10월</span><span>100억 원 규모 시리즈 A 투자 유치</span></li>
      <li><span class="m">08월</span><span>loopchain V1.0 GS인증 1등급 획득</span></li>
      <li><span class="m">08월</span><span>한국생산성본부와 업무협약 체결</span></li>
      <li><span class="m">08월</span><span>미술품 공동구매 플랫폼 아트앤가이드에 블록체인 증명서 발급 서비스 적용</span></li>
      <li><span class="m">07월</span><span>블록체인 신원인증 서비스 '디패스(DPASS)' 출시</span></li>
      <li><span class="m">06월</span><span>분산ID 서비스 'MyID', 금융위원회 혁신금융서비스 금융규제 샌드박스 지정</span></li>
      <li><span class="m">05월</span><span>블록체인 증명서 발급 서비스 '브루프(broof)' 출시</span></li>
      <li><span class="m">04월</span><span>UN 산하 국제전기통신연합(ITU)과 업무협약 체결</span></li>
      <li><span class="m">04월</span><span>SBI저축은행 블록체인 개인인증 서비스 출시</span></li>
      <li><span class="m">02월</span><span>AWS 파트너 네트워크(APN) 어드밴스드 기술 파트너 선정</span></li>
    </ul></div></div></li></ul>
  
    </div>
    <div class="ht2-group rvl" style="--rvl-y:24px" data-rng="2016 — 2018" data-title="기술 기반 구축">
      <div class="ht2-era-head"><h3 class="ht2-t">2016 — 2018<br>기술 기반 구축</h3></div>

    <ul class="ht2-faq"><li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:0ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2018</b><span class="ht2-tt">라인과 블록체인 합작법인 설립</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2018</b><span class="ht2-tt">라인과 블록체인 합작법인 설립</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">11월</span><span>블록체인 발전 기여 공로, 과학기술정보통신부 장관 표창 수상</span></li>
      <li><span class="m">11월</span><span>AWS 마켓플레이스에 'ICON Development Network' 론칭</span></li>
      <li><span class="m">09월</span><span>서울시 블록체인 기반 단위업무 정보전략계획(ISP) 수립 사업자 선정</span></li>
      <li><span class="m">08월</span><span>선관위 차세대 선거시스템 구축 계획 블록체인 부문 컨설팅 사업자 선정</span></li>
      <li><span class="m">08월</span><span>'소상공인 전용 디지털광장' 플랫폼에 블록체인 기술 적용</span></li>
      <li><span class="m">08월</span><span>㈜아이콘루프로 사명 변경</span></li>
      <li><span class="m">06월</span><span>관세청 수입 통관 절차에 loopchain 기술 적용</span></li>
      <li><span class="m">05월</span><span>라인과 블록체인 합작법인 설립, 링크체인 메인넷 개발</span></li>
      <li><span class="m">05월</span><span>'CHAIN ID'-삼성패스 연계 운영 업무 협약 체결</span></li>
      <li><span class="m">03월</span><span>기업부설연구소 설립 인정</span></li>
      <li><span class="m">01월</span><span>1세대 퍼블릭 메인넷 ICON 출시에 기술 파트너로 참여, 코어 엔진 loopchain 제공</span></li>
    </ul></div></div></li>
    <li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:60ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2017</b><span class="ht2-tt">세계 최초 블록체인 공동인증 'CHAIN ID' 상용화</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2017</b><span class="ht2-tt">세계 최초 블록체인 공동인증 'CHAIN ID' 상용화</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">12월</span><span>U-Coin·위비코인 파일럿 서비스 출시</span></li>
      <li><span class="m">11월</span><span>교보생명과 블록체인 기반 보험금 자동청구 서비스 출시</span></li>
      <li><span class="m">11월</span><span>금융투자업권 개인정보노출자 사고정보 시스템 출시</span></li>
      <li><span class="m">10월</span><span>금융투자업권 공동인증 서비스 'CHAIN ID' 출시, 증권사 26개사 참여</span></li>
      <li><span class="m">09월</span><span>국가전략 프로젝트 'P-HIS 컨소시엄' 기술 파트너 참여</span></li>
    </ul></div></div></li>
    <li class="faq-li faq-item rvl" style="--rvl-y:24px; --rvl-delay:120ms"><div class="faq-row" role="button" tabindex="0" aria-expanded="false"><div class="faq-content"><div class="faq-inner"><h3 class="faq-t faq-t-top"><b class="ht2-yr">2016</b><span class="ht2-tt">(주)더루프 설립, 국내 1세대 Web3 인프라 기업 출발</span></h3><div class="faq-ans"></div><h3 class="faq-t faq-t-bottom"><b class="ht2-yr">2016</b><span class="ht2-tt">(주)더루프 설립, 국내 1세대 Web3 인프라 기업 출발</span></h3></div></div><span class="faq-badge2" aria-hidden="true"></span></div><div class="ht2-subwrap"><div class="ht2-subin"><ul class="ht2-rows">
      <li><span class="m">12월</span><span>'금융투자업권 블록체인 컨소시엄' 출범</span></li>
      <li><span class="m">08월</span><span>서강대학교 내 블록체인 기반 디지털화폐 PoC 완료</span></li>
      <li><span class="m">06월</span><span>서울시 S-coin 시범사업 추진</span></li>
      <li><span class="m">05월</span><span>(주)더루프 설립</span></li>
      <li><span class="m">05월</span><span>서강대학교와 블록체인 공동사업화 업무협약 체결</span></li>
    </ul></div></div></li></ul>
  
    </div>
  </div>
</div>
</div><script>/* History: 스크롤 시 좌측 시대 페이드 전환 (아코디언은 공통 FAQ JS) */
(function(){
  var layers=document.querySelectorAll('.ht2-layer');
  var groups=document.querySelectorAll('.ht2-group');
  if(!layers.length || !('IntersectionObserver' in window)) return;
  var curIdx=-1;
  function setEra(g){
    var idx=[].indexOf.call(groups, g);
    layers.forEach(function(l,i){ l.classList.toggle('on', i===idx); });
    groups.forEach(function(x){ x.classList.toggle('ht2-on', x===g); });
    if(idx!==curIdx){
      curIdx=idx;
      var first=g.querySelector('.faq-item');
      if(first && !first.classList.contains('open')){
        var row=first.querySelector('.faq-row'); if(row) row.click();   /* 공유 FAQ 핸들러 재사용 */
      }
    }
  }
  if(groups[0]){ groups[0].classList.add('ht2-on'); window.addEventListener('load', function(){ setEra(groups[0]); }); }   /* 모든 스크립트 바인딩 후 초기 오픈 */
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting) setEra(e.target); });
  }, { rootMargin:'-40% 0px -55% 0px' });
  groups.forEach(function(g){ io.observe(g); });
})();
</script></section>
<section><div class="shell about-grid">
  <div class="about-globe">
    <svg class="icn about-globe-bg" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9.25" stroke="currentColor" stroke-width="1.4"/><ellipse cx="12" cy="12" rx="4.2" ry="9.25" stroke="currentColor" stroke-width="1.4"/><path stroke="currentColor" stroke-width="1.4" stroke-linecap="round" d="M2.75 12h18.5"/></svg>
    <div class="eyebrow dark" style="position:relative"><span class="dot"></span>Company</div>
  </div>
  <div class="about-right">
    <div class="addr-list rvl">
      <div><div class="k">Address</div><div class="v">서울특별시 서초구 강남대로 311, 드림플러스 강남 8층</div></div>
      <div><div class="k">English</div><div class="v">8F, DreamPlus Gangnam, 311 Gangnam-daero, Seocho-gu, Seoul, Republic of Korea</div></div>
      <div><div class="k">Phone</div><div class="v">02-2138-7026</div></div>
    </div>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  <div class="rvl" style="border-radius:var(--radius-card-sm); overflow:hidden; height:360px">
    <div id="daumRoughmapContainer1784644327077" class="root_daum_roughmap root_daum_roughmap_landing"></div>
  </div>
  <script charset="UTF-8" class="daum_roughmap_loader_script" src="https://ssl.daumcdn.net/dmaps/map_js_init/roughmapLoader.js"></script>
  <script charset="UTF-8">
  /* 카카오맵 지도퍼가기 — 컨테이너 폭으로 동적 렌더 + 리사이즈 재렌더 (퍼가기 기본 폭 640 고정 문제 대응) */
  var st=document.createElement('style');
  st.textContent='.root_daum_roughmap .cont{display:none !important} .root_daum_roughmap .wrap_controllers{display:none !important} .root_daum_roughmap{border:0 !important}';
  document.head.appendChild(st);
  (function(){
    var el = document.getElementById('daumRoughmapContainer1784644327077');
    if (!el) return;
    function render(){
      el.innerHTML = '';
      /* 래퍼보다 사방 4px 크게 렌더 + 중앙 정렬 → 위젯 자체 테두리 클립 */
      el.style.margin = '-4px';
      new daum.roughmap.Lander({
        "timestamp" : "1784644327077",
        "key" : "r8ubh64gunj",
        "mapWidth" : String((el.parentElement.clientWidth || 640) + 8),
        "mapHeight" : "368"
      }).render();
    }
    render();
    var t; addEventListener('resize', function(){ clearTimeout(t); t = setTimeout(render, 300); });
  })();
  </script>
</div></section>
''')

# ---------------- insights.html (Newsroom) ----------------
# 보도자료 데이터 — _build/data/press/*.json (extract_press.py 산출, 120편) 로드
# 피처드(최신 3)·리스트·상세 양산이 모두 이 데이터를 공유
PRESS_DATA = []
for _f in sorted(glob.glob(os.path.join(DATA_DIR, 'press', '*.json'))):
    with open(_f, encoding='utf-8') as _fh:
        PRESS_DATA.append(json.load(_fh))
PRESS_DATA.sort(key=lambda d: -d['sort'])
PRESS_ITEMS = [dict(date=d['date'], title=d['title'], href=f"press/{d['slug']}.html", img=d.get('hero_img')) for d in PRESS_DATA]

def drop(cls, options, aria):
    """커스텀 드롭다운 (시스템 셀렉트 대체) — options: [(value, label)], 첫 항목이 기본값."""
    v0, l0 = options[0]
    on = ' class="is-on"'
    lis = ''.join(
        f'<li role="option" data-value="{v}"{on if i == 0 else ""}>{l}</li>'
        for i, (v, l) in enumerate(options))
    return (f'<div class="drop {cls}" data-value="{v0}">'
            f'<button class="select-pill drop-btn" type="button" aria-haspopup="listbox" aria-expanded="false" aria-label="{aria}">'
            f'<span class="drop-label">{l0}</span></button>'
            f'<ul class="drop-menu" role="listbox" data-lenis-prevent>{lis}</ul></div>')

def press_list(items):
    """보도자료 리스트 — 날짜 | 제목 | 썸네일 영역(placeholder)."""
    years = sorted({it['date'][:4] for it in items}, reverse=True)
    y_opts = [('all', '전체 연도')] + [(y, y) for y in years]
    m_opts = [('all', '전체 월')] + [(f'{m:02d}', f'{m}월') for m in range(1, 13)]
    rows = ''.join(
        f'<li class="news-row press-item rvl" data-year="{it["date"][:4]}" data-month="{it["date"][5:7]}" style="--rvl-y:24px; --rvl-delay:{(i % 5) * 60}ms">'
        f'<a class="nr-link" href="{it["href"]}">'
        f'<span class="nr-date">{it["date"]}</span>'
        f'<h3 class="nr-title">{it["title"]}</h3>'
        + (f'<span class="nr-thumb" aria-hidden="true" style="background-image:url(\'{it["img"]}\')"></span>' if it.get('img') else '<span class="nr-thumb" aria-hidden="true"></span>')
        + '</a></li>'
        for i, it in enumerate(items))
    return (f'<div class="news-controls rvl">'
            f'{drop("news-sel-year", y_opts, "연도 필터")}'
            f'{drop("news-sel-month", m_opts, "월 필터")}'
            f'<div class="news-search">'
            f'<input type="search" placeholder="보도자료 검색" aria-label="보도자료 검색">'
            f'<button class="ns-clear" type="button" aria-label="검색어 지우기" hidden><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><line x1="7" y1="7" x2="17" y2="17"/><line x1="17" y1="7" x2="7" y2="17"/></svg></button>'
            f'<button class="ns-btn" type="button" aria-label="검색"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></button>'
            f'</div></div>'
            f'<ul class="news-list">{rows}</ul>'
            f'<div class="news-empty" hidden>'
            f'<span class="ne-ico" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/><line x1="8" y1="11" x2="8" y2="11"/><line x1="11" y1="11" x2="11" y2="11"/><line x1="14" y1="11" x2="14" y2="11"/></svg></span>'
            f'<p>검색 결과가 없습니다.</p></div>')

PAGES['insights.html'] = dict(
    title='Newsroom | PARAMETA',
    desc='파라메타의 사업, 파트너십, 인증, 수상 소식을 한곳에서 확인할 수 있습니다.',
    eyebrow='',
    h1_lines=['Newsroom'],
    lead='',
    crumb='Newsroom — 보도자료',
    body_class='media',
    content=f'''
<section data-press><div class="shell sec">
  {sec_head('Press Release', '보도자료')}
  {press_list(PRESS_ITEMS)}
  <div class="pager" role="navigation" aria-label="보도자료 페이지"></div>
</div></section>
''')

# ---------------- 보도자료 상세 공통 템플릿 (네이버 뉴스룸 상세 포맷) ----------------
def press_detail(fname, h1_lines, date, summary, blocks):
    """보도자료 상세 페이지 등록 — 네이버 상세 포맷:
    히어로(딤+이미지, 좌측 정렬, 날짜, 공유 버튼) / 본문(제목 반복, 요약 불릿, 블록 시퀀스, (끝)) / 액션 바.
    summary: 요약 문장 리스트(없으면 생략) / blocks: [{'t':'p'|'img'|'h3'|'list', ...}] 원문 순서 그대로"""
    title_flat = ' '.join(h1_lines)
    sums = f"<ul class=\"pd-sum\">{''.join(f'<li>{x}</li>' for x in summary)}</ul>" if summary else ''
    parts = []
    for bl in blocks:
        t = bl['t']
        if t == 'p':
            parts.append(f"<p>{bl['html']}</p>")
        elif t == 'img':
            parts.append(f'<figure class="pd-fig"><img src="{bl["src"]}" alt="" loading="lazy"></figure>')
        elif t == 'h3':
            parts.append(f"<h3 class=\"pd-h3\">{bl['html']}</h3>")
        elif t == 'list':
            lis = ''.join(f'<li>{x}</li>' for x in bl.get('items', []))
            parts.append(f'<ul class="pd-list">{lis}</ul>')
    body = ''.join(parts)
    PAGES[fname] = dict(
        title=f'{title_flat} | PARAMETA',
        desc=f'{title_flat} — 파라메타 보도자료.',
        eyebrow='',
        h1_lines=h1_lines,
        lead='',
        crumb='Newsroom — Press',
        body_class='hero-dark press',
        hero_cta='',
        hero_extra=(
            f'<div class="pd-hero-meta"><div class="pdm-cell"><span class="pdm-date">{date}</span>'
            '<button class="pd-share" type="button" aria-label="공유하기">'
            '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle vector-effect="non-scaling-stroke" cx="18" cy="5" r="3"/><circle vector-effect="non-scaling-stroke" cx="6" cy="12" r="3"/><circle vector-effect="non-scaling-stroke" cx="18" cy="19" r="3"/><line vector-effect="non-scaling-stroke" x1="8.6" y1="13.5" x2="15.4" y2="17.5"/><line vector-effect="non-scaling-stroke" x1="15.4" y1="6.5" x2="8.6" y2="10.5"/></svg>'
            '</button></div></div>'),
        content=f'''
<section><div class="shell sec pd-grid">
  <article class="pd-body">
    <h2 class="pd-title">{title_flat}</h2>
    {sums}
    {body}
    <p class="pd-end">(끝)</p>
  </article>
  <div class="pd-actions rvl">
    <button class="pill outline no-arrow hs-scale" type="button" data-copy><span class="hspring"><span class="pd-copy-label">텍스트 복사</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></span></button>
    <button class="pill outline no-arrow hs-scale" type="button" data-dl-images><span class="hspring">전체 이미지 다운로드<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></span></button>
    <a class="pill dark no-arrow hs-scale pd-list" href="insights.html"><span class="hspring">목록보기</span></a>
  </div>
</div></section>
<div id="pd-share-modal" role="dialog" aria-modal="true" aria-label="공유하기" aria-hidden="true">
  <div class="psm-backdrop" data-psm-close></div>
  <div class="psm-panel">
    <button class="psm-close" type="button" data-psm-close aria-label="닫기"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg></button>
    <h2>공유하기</h2>
    <ul class="psm-grid">
      <li><a class="psm-item" data-share="x" href="#" target="_blank" rel="noopener"><span class="psm-ico psm-x"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231 5.451-6.231zm-1.161 17.52h1.833L7.084 4.126H5.117l11.966 15.644z"/></svg></span>X</a></li>
      <li><a class="psm-item" data-share="fb" href="#" target="_blank" rel="noopener"><span class="psm-ico psm-fb"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.397 20.997v-8.196h2.765l.411-3.209h-3.176V7.548c0-.926.258-1.56 1.587-1.56h1.684V3.127c-.291-.039-1.29-.126-2.453-.126-2.429 0-4.09 1.483-4.09 4.205v2.386H7.353v3.209h2.772v8.196h3.272z"/></svg></span>페이스북</a></li>
      <li><a class="psm-item" data-share="line" href="#" target="_blank" rel="noopener"><span class="psm-ico psm-line"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/></svg></span>라인</a></li>
      <li><a class="psm-item" data-share="mail" href="#"><span class="psm-ico psm-mail"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><polyline points="3 7 12 13 21 7"/></svg></span>메일</a></li>
    </ul>
    <div class="psm-url">
      <input type="text" readonly aria-label="페이지 주소">
      <button class="psm-copy" type="button">URL 복사</button>
    </div>
  </div>
</div>
''')

# 보도자료 120편 양산 — _build/data/press/*.json → press/post-pr-NNN.html
for _d in PRESS_DATA:
    press_detail(
        f"press/{_d['slug']}.html",
        h1_lines=[_d['title']],
        date=_d['date'],
        summary=_d['summary'],
        blocks=_d['blocks'],
    )

# ---------------- blog.html ----------------
# 블로그 아티클 데이터 — _build/data/blog/*.json (2단계 정식 추출 예정, 1단계는 대표 12편)
BLOG_CATS = [('insight', '인사이트'), ('news', '뉴스'), ('people', '피플')]
BLOG_DATA = []
for _f in sorted(glob.glob(os.path.join(DATA_DIR, 'blog', '*.json'))):
    with open(_f, encoding='utf-8') as _fh:
        BLOG_DATA.append(json.load(_fh))
BLOG_DATA.sort(key=lambda d: -d['sort'])

def blog_feed(items, cats):
    """블로그 피드 — 좌측 카테고리 레일(cat) + 우측 3열 카드(썸네일, 제목, 설명, 카테고리 태그)."""
    label = dict(cats)
    tabs = ('<button class="blog-tab is-on" type="button" role="tab" data-filter="all">All</button>'
            + ''.join(f'<button class="blog-tab" type="button" role="tab" data-filter="{k}">{v}</button>' for k, v in cats))
    cards = []
    for i, it in enumerate(items):
        if it.get('hero_img'):
            thumb = f'<span class="bf-thumb" aria-hidden="true" style="background-image:url({it["hero_img"]})"></span>'
        else:  # 이미지 없는 아티클 — 남색 카드 + 흰색 심볼 디폴트 썸네일
            thumb = ('<span class="bf-thumb bf-thumb-empty" aria-hidden="true">'
                     '<img class="bf-mark" src="assets/brand/logo-symbol-white.svg" alt=""></span>')
        cards.append(
            f'<li class="blog-item rvl" data-cat="{it["cat"]}" style="--rvl-y:24px; --rvl-delay:{(i % 3) * 60}ms">'
            f'<a class="bf-card" href="blog/{it["slug"]}.html">'
            f'{thumb}'
            f'<h3 class="bf-title">{it["title"]}</h3>'
            f'<p class="bf-desc">{it["desc"]}</p>'
            f'<span class="bf-tag">{label.get(it["cat"], it["cat"])}</span></a></li>')
    cards = ''.join(cards)
    return ('<div class="blog-layout">'
            f'<div class="blog-rail" role="tablist" aria-label="블로그 카테고리">{tabs}</div>'
            f'<div class="blog-main"><ul class="blog-grid">{cards}</ul>'
            '<div class="pager" role="navigation" aria-label="블로그 페이지"></div></div></div>')

PAGES['blog.html'] = dict(
    title='Blog | PARAMETA',
    desc='디지털자산 시장을 읽는 인사이트를 확인할 수 있습니다.',
    eyebrow='',
    h1_lines=['Blog'],
    lead='',
    crumb='Blog — 디지털자산 인사이트',
    body_class='media',
    content=f'''
<section data-blog><div class="shell sec">
  {sec_head('Articles', '디지털자산 시장을 읽는 인사이트')}
  {blog_feed(BLOG_DATA, BLOG_CATS)}
</div></section>
''')

# ---------------- resources.html (자료실) ----------------
PAGES['resources.html'] = dict(
    title='Resources | PARAMETA',
    desc='파라메타 로고 등 브랜드 자료를 한곳에서 확인할 수 있습니다.',
    eyebrow='',
    h1_lines=['Resources'],
    lead='',
    crumb='Resources — 자료실',
    body_class='media',
    content=f'''
<section><div class="shell sec">
  {sec_head('Logo', '로고 다운로드')}
  <div class="res-logo rvl" style="--rvl-y:24px">
    <article class="work-card static grouped t-gray rl-card">
      <div class="work-bottom"><h3>인쇄·출판용</h3>
        <div class="rl-actions">
          <button class="rl-btn" type="button" disabled>PNG 다운로드</button>
          <button class="rl-btn" type="button" disabled>AI 다운로드</button>
        </div>
      </div>
    </article>
    <article class="work-card static grouped t-gray rl-card">
      <div class="work-bottom"><h3>웹·화면용</h3>
        <div class="rl-actions">
          <button class="rl-btn" type="button" disabled>PNG 다운로드</button>
          <button class="rl-btn" type="button" disabled>AI 다운로드</button>
        </div>
      </div>
    </article>
  </div>
</div></section>
''')

# ---------------- 블로그 아티클 상세 (post_blog) ----------------
SHARE_BTN = ('<button class="pd-share" type="button" aria-label="공유하기">'
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle vector-effect="non-scaling-stroke" cx="18" cy="5" r="3"/><circle vector-effect="non-scaling-stroke" cx="6" cy="12" r="3"/><circle vector-effect="non-scaling-stroke" cx="18" cy="19" r="3"/><line vector-effect="non-scaling-stroke" x1="8.6" y1="13.5" x2="15.4" y2="17.5"/><line vector-effect="non-scaling-stroke" x1="15.4" y1="6.5" x2="8.6" y2="10.5"/></svg></button>')
SHARE_MODAL = '''<div id="pd-share-modal" role="dialog" aria-modal="true" aria-label="공유하기" aria-hidden="true">
  <div class="psm-backdrop" data-psm-close></div>
  <div class="psm-panel">
    <button class="psm-close" type="button" data-psm-close aria-label="닫기"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg></button>
    <h2>공유하기</h2>
    <ul class="psm-grid">
      <li><a class="psm-item" data-share="x" href="#" target="_blank" rel="noopener"><span class="psm-ico psm-x"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231 5.451-6.231zm-1.161 17.52h1.833L7.084 4.126H5.117l11.966 15.644z"/></svg></span>X</a></li>
      <li><a class="psm-item" data-share="fb" href="#" target="_blank" rel="noopener"><span class="psm-ico psm-fb"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.397 20.997v-8.196h2.765l.411-3.209h-3.176V7.548c0-.926.258-1.56 1.587-1.56h1.684V3.127c-.291-.039-1.29-.126-2.453-.126-2.429 0-4.09 1.483-4.09 4.205v2.386H7.353v3.209h2.772v8.196h3.272z"/></svg></span>페이스북</a></li>
      <li><a class="psm-item" data-share="line" href="#" target="_blank" rel="noopener"><span class="psm-ico psm-line"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19.365 9.863c.349 0 .63.285.63.631 0 .345-.281.63-.63.63H17.61v1.125h1.755c.349 0 .63.283.63.63 0 .344-.281.629-.63.629h-2.386c-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63h2.386c.346 0 .627.285.627.63 0 .349-.281.63-.63.63H17.61v1.125h1.755zm-3.855 3.016c0 .27-.174.51-.432.596-.064.021-.133.031-.199.031-.211 0-.391-.09-.51-.25l-2.443-3.317v2.94c0 .344-.279.629-.631.629-.346 0-.626-.285-.626-.629V8.108c0-.27.173-.51.43-.595.06-.023.136-.033.194-.033.195 0 .375.104.495.254l2.462 3.33V8.108c0-.345.282-.63.63-.63.345 0 .63.285.63.63v4.771zm-5.741 0c0 .344-.282.629-.631.629-.345 0-.627-.285-.627-.629V8.108c0-.345.282-.63.63-.63.346 0 .628.285.628.63v4.771zm-2.466.629H4.917c-.345 0-.63-.285-.63-.629V8.108c0-.345.285-.63.63-.63.348 0 .63.285.63.63v4.141h1.756c.348 0 .629.283.629.63 0 .344-.282.629-.629.629M24 10.314C24 4.943 18.615.572 12 .572S0 4.943 0 10.314c0 4.811 4.27 8.842 10.035 9.608.391.082.923.258 1.058.59.12.301.079.766.038 1.08l-.164 1.02c-.045.301-.24 1.186 1.049.645 1.291-.539 6.916-4.078 9.436-6.975C23.176 14.393 24 12.458 24 10.314"/></svg></span>라인</a></li>
      <li><a class="psm-item" data-share="mail" href="#"><span class="psm-ico psm-mail"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><polyline points="3 7 12 13 21 7"/></svg></span>메일</a></li>
    </ul>
    <div class="psm-url">
      <input type="text" readonly aria-label="페이지 주소">
      <button class="psm-copy" type="button">URL 복사</button>
    </div>
  </div>
</div>'''

_KV_RE = re.compile(r'^[^:：.<\n]{1,24}[:：]\s')   # "라벨: 값" (짧은 라벨 + 콜론)
def _group_kv_runs(blocks):
    """연속된 '라벨: 값' 문단(2줄 이상)을 블릿 리스트로 묶는다 — 이런 key-value 나열은 자동으로 블릿 처리."""
    out, run = [], []
    def flush():
        if len(run) >= 2: out.append({'t': 'list', 'items': run[:]})
        else: out.extend({'t': 'p', 'html': x} for x in run)
        run.clear()
    for b in blocks:
        if b['t'] == 'p' and _KV_RE.match(b.get('html', '')):
            run.append(b['html'])
        else:
            flush(); out.append(b)
    flush()
    return out

def post_blog(data):
    """블로그 아티클 상세 — 뉴스룸(프레스) 히어로 포맷 이식: 딤 히어로(좌측 정렬) +
    메타줄(카테고리·날짜·읽는시간 좌 / 공유 버튼 우) + 본문 블록/On this page 목차(h3 2개 이상)."""
    cat_label = dict(BLOG_CATS).get(data['cat'], data['cat'])
    # ── On this page 목차: 본문 h3를 순서대로 자동 수집 → post-sN 앵커 부여 → 사이드 목차 생성.
    #    저자가 목차를 따로 작성할 필요 없음. 본문에 h3만 있으면 양산 시 전 아티클에 자동 반영되고,
    #    h3가 2개 미만이면 목차를 숨기고 본문을 넓게(solo) 쓴다. (스크롤스파이·부드러운 이동은 JS에서 처리)
    parts, toc = [], []
    if data.get('lead'):
        parts.append(f'<p class="post-lead">{data["lead"]}</p>')
    hn = 0
    for bl in _group_kv_runs(data['blocks']):
        t = bl['t']
        if t == 'p':
            parts.append(f'<p>{bl["html"]}</p>')
        elif t == 'img':
            parts.append(f'<figure class="post-fig"><img src="{bl["src"]}" alt="" loading="lazy"></figure>')
        elif t == 'h3':
            hn += 1
            hid = f'post-s{hn}'
            parts.append(f'<h3 id="{hid}">{bl["html"]}</h3>')
            toc.append((hid, bl['html']))
        elif t == 'list':
            lis = ''.join(f'<li>{x}</li>' for x in bl.get('items', []))
            parts.append(f'<ul>{lis}</ul>')
    body = '\n      '.join(parts)
    if len(toc) >= 2:
        toc_html = ''.join(f'<li><a href="#{i}">{tx}</a></li>' for i, tx in toc)
        side = f'<aside class="post-side">{eyebrow("On this page")}<ul>{toc_html}</ul></aside>'
        grid_cls = 'post-grid'
    else:
        side = ''
        grid_cls = 'post-grid solo'
    PAGES[f"blog/{data['slug']}.html"] = dict(
        title=f"{data['title']} | PARAMETA",
        desc=data['desc'],
        eyebrow='',
        h1_lines=[data['title']],
        lead='',
        crumb='Blog — Article',
        body_class='hero-dark press blog',
        hero_cta='',
        hero_extra=(
            '<div class="pd-hero-meta"><div class="pdm-cell">'
            f'<div class="pdm-info"><span class="pdm-date">{data["date"]}</span>'
            f'<span class="post-cat">{cat_label}</span></div>'
            f'{SHARE_BTN}</div></div>'),
        content=f'''
<section><div class="shell sec">
  <div class="{grid_cls}">
    <article class="post-body">
      {body}
    </article>
    {side}
    <div class="pd-actions post-actions rvl">
      <button class="pill outline no-arrow hs-scale" type="button" data-copy><span class="hspring"><span class="pd-copy-label">텍스트 복사</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></span></button>
      <button class="pill outline no-arrow hs-scale" type="button" data-dl-images><span class="hspring">전체 이미지 다운로드<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></span></button>
      <a class="pill dark no-arrow hs-scale pd-list" href="blog.html"><span class="hspring">목록보기</span></a>
    </div>
  </div>
</div></section>
{SHARE_MODAL}
''')

# 블로그 상세 — 블록이 있는(추출 완료) 아티클만 페이지 생성. 1단계는 샘플 1편, 2단계에서 전체 양산.
for _d in BLOG_DATA:
    if _d.get('blocks'):
        post_blog(_d)

# ---------------- parasta.html ----------------
PAGES['parasta.html'] = dict(
    title='ParaSta · 디지털자산 금융 인프라 | PARAMETA',
    desc='ParaSta — 스테이블코인·디지털자산 사업을 위한 모듈형 인프라. 발행·오케스트레이션·지갑·온체인 KYC를 골라 조립하세요. Compliant-Ready · Zero-Ops.',
    eyebrow='Digital Asset Platform',
    body_class='hero-dark parasta',   # parasta 식별 클래스(히어로 CTA 새 버튼 노출)
    h1_lines=['ParaSta'],
    lead='스테이블코인, 디지털자산 비즈니스를 위한 모듈형 인프라입니다.<br>필요한 기능을 선택해 구성하고, 발행부터 운영까지 하나로 연결합니다.',
    crumb='Products — ParaSta',
    hero_visual='<img class="fit-contain" src="assets/parasta/hero-test.avif" alt="" loading="eager" fetchpriority="high">',
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
      {sec_head('What is ParaSta', '발행부터 운영까지 연결하는<br>디지털자산 인프라', 'ParaSta는 스테이블코인, 예금토큰 등 다양한 디지털자산의 발행과 운영을 하나의 플랫폼에서 지원하고, 기존 은행, 결제망과 바로 연결합니다. 신원 확인부터 지갑, 정산, 감사까지 디지털자산 운영 전반을 지원합니다.', body=True)}
    </div>
  </div>
</div></section>
<section><div class="shell sec">
  <div class="why-grid">
    <div class="why-head">
      {sec_head('Why ParaSta', '디지털자산을 실제 금융 서비스로 연결하는 하나의 인프라')}
      {legend_marks()}
    </div>
    <div class="why-table">
      {compare_table(
        ['', 'ParaSta', '해외 커스터디·지갑 SaaS', '국내 커스터디', '자체 구축 · SI'],
        [
          dict(label='국내 규제 대응', cells=[cell('on','AML, 트래블룰, 감사 로그 내장'), cell('off','도입사 직접 대응'), cell('mid','수탁·보관 중심'), cell('off','규제 검토부터 직접 대응')]),
          dict(label='신원관리', cells=[cell('on','발행 레이어에 KYC, DID 기능 내장'), cell('mid','외부 KYC 솔루션 연동'), cell('off','신원 인증 기능 제한적'), cell('off','KYC, DID 직접 개발')]),
          dict(label='구축 방식', cells=[cell('on','검증된 모듈을 SDK로 유연하게 구성'), cell('mid','정해진 기능 범위 내 구성'), cell('mid','커스터디 기능 중심'), cell('off','처음부터 직접 개발')]),
          dict(label='도입·운영', cells=[cell('on','키 관리, 가스비, 노드 운영 대행'), cell('on','글로벌 시장에 빠르게 도입'), cell('on','검증된 수탁 운영'), cell('off','개발, 운영 직접 관리')]),
        ], hl=1, tabs=True)}
    </div>
  </div>
</div></section>
<section><div class="shell sec">
  {sec_head('Advantages', '필요한 것만 골라 도입하고,<br>운영은 맡기는 인프라')}
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
    <li>{dark_card('Issuance', 'Mint with Compliance, Scale Across Chains', '기업 고유의 스테이블코인과 토큰화 자산을 발행하고 관리합니다. 다중 서명, 준비자산 증빙(PoR), 화이트리스트, 블랙리스트, 자금 동결을 포함한 6단계 통제 구조로 발행부터 사후 검증까지 전 과정을 통제합니다.', ['발행, 소각, 준비자산 운용','PoR 기반 준비자산 증빙','자산 수명주기 실시간 모니터링'], grouped=True)}</li>
    <li>{dark_card('Wallet', 'Enterprise Control, Frictionless UX', '계정 추상화(ERC-4337)를 기반으로 가스비 부담 없는 사용자 경험을 제공합니다. 여러 체인을 하나의 인터페이스로 통합하고, 일회용 수신 주소(Stealth Address)로 프라이버시를 보호합니다. 온체인 KYC 모듈과 연동해 신원이 확인된 지갑만 거래할 수 있도록 통제합니다.', ['가스비 없는 사용자 경험','멀티체인 통합 인터페이스','Stealth Address 기반 프라이버시 보호'], grouped=True)}</li>
    <li>{dark_card('Orchestration', 'Bridge Worlds, Settle Instantly', '은행 계좌와 온체인 지갑을 하나의 API로 연결합니다. 법정화폐↔가상자산 자동 전환부터 예약 정산, 조건부 정산, 이벤트 기반 시스템 연동까지, 거래 전 과정을 하나의 흐름으로 관리합니다.', ['법정화폐↔가상자산 자동 전환','예약, 조건부 정산','실시간 AML 스크리닝'], grouped=True)}</li>
    <li>{dark_card('On-chain KYC', 'Verify Once, Use Everywhere', '공인기관의 KYC 결과를 검증 가능한 크레덴셜(VC, VP) 형태로 발급하고, 검증된 지갑 주소를 온체인 신원 레지스트리(KYW)에 등록합니다. 토큰 컨트랙트는 이체 시점에 레지스트리를 조회해 자격을 갖춘 지갑만 거래하도록 통제하며, 개인정보는 온체인에 저장하지 않습니다.', ['DID 기반 VC, VP 발급','KYW 온체인 화이트리스트','표준 규격(ERC-3643) 기반 이체 검증'], grouped=True)}</li>
    <li>{dark_card('Unified Admin', 'See Everything, Control Everything', '발행, 지갑, 오케스트레이션, 온체인 KYC 등 4개 모듈을 하나의 통합 관제 환경에서 관리합니다. Mint, Burn 통제부터 MPC 기반 키 관리, 다단계 승인, 자금 흐름 모니터링까지 모든 운영 현황을 한 화면에서 확인할 수 있습니다.', ['발행, 소각 전 과정 통제','MPC 기반 키 관리, 다단계 승인','통합 감사 리포팅'], grouped=True)}</li>
  </ul>
  </div>
</div></section>
<section><div class="shell sec">
  {sec_head('Core Technology', '엔터프라이즈가 디지털자산을 다루는 데 필요한 기술이 인프라에 담겨 있습니다')}
  <div class="ct-rows">{rows([
    dict(title='계정 추상화 (AA)', desc='지갑 설치, 시드 문구 보관, 가스비 결제 같은 절차 없이 기존 앱과 동일한 사용 경험을 제공합니다. 가스비는 기업이 대신 부담하는 구조로, 사용자 진입 장벽을 낮춥니다.'),
    dict(title='선택적 공개 (ZKP, Selective Disclosure)', desc="검증에 필요한 사실만 골라 증명합니다. 생년월일 전체 대신 '성인 여부'만, 주소 전체 대신 '거주 국가'만 확인하는 식입니다. 개인정보 원문을 수집, 보관하지 않아 기업의 유출 리스크와 관리 부담을 줄입니다."),
    dict(title='스텔스 주소 (Stealth Address)', desc='블록체인은 주소만 알면 누구나 거래 내역을 볼 수 있는 공개 장부입니다. 거래마다 새로운 수신 주소를 생성해, 고객의 자산 규모와 거래 흐름이 외부에 추적, 노출되지 않도록 보호합니다.'),
    dict(title='단일 인터페이스 멀티체인 (Multi-chain)', desc='메인체인이 바뀌거나 추가돼도 시스템을 다시 구축할 필요가 없습니다. 한 번의 연동으로 여러 체인의 자산과 거래를 통합 관리하고, 새로운 체인도 같은 방식으로 확장합니다.'),
    dict(title='MPC 키 분할, 복구 (Key Share)', desc='개인키를 하나로 보관하지 않고 여러 개의 키 셰어로 나눠 분산 보관합니다. 일부가 유출돼도 자산을 옮길 수 없고, 일부를 분실해도 나머지 키 셰어로 복구할 수 있습니다.'),
  ])}</div>
</div></section>
<!-- 파트너 로고 마퀴: 섹션 밖 풀블리드 밴드 -->
<section><div class="pt-marquee rvl" aria-label="함께한 파트너 로고" style="margin:0"><div class="pt-track">{partner_logos()}{partner_logos()}</div></div></section>
<section><div class="shell sec uc-tail">
  {sec_head('Partners', '함께한 파트너', layout='center')}
  <div class="uc-tabbar" role="tablist">
    <button class="uc-tabbtn is-active" type="button">금융권</button>
    <button class="uc-tabbtn" type="button">퍼블릭, 멀티체인</button>
  </div>
  <div class="uc-tabpanel is-active">
    {usecase_carousel([
      dict(title='신한은행', desc='금융권 DID 실명인증 상용화'),
      dict(title='NH농협은행', desc='올원뱅크 실명인증 적용'),
      dict(title='한국투자증권 외 25개 증권사', desc='증권업권을 하나의 온체인 신원 체계로 연결한 공동인증 서비스. 여러 금융기관의 신원과 인증을 연동한 경험으로, 스테이블코인 인프라에 필요한 규제 대응과 기관 간 연결 역량을 검증했습니다.'),
    ], label='금융권 사례')}
  </div>
  <div class="uc-tabpanel">
    {usecase_carousel([
      dict(title='자체 블록체인 코어 엔진 개발, 운영', desc='PBFT 합의와 인터체인 프로토콜을 자체 기술로 구현한 퍼블릭 메인넷. 다국가 밸리데이터 환경에서 축적한 구축, 운영 경험.'),
      dict(title='멀티체인 오케스트레이션, 크로스체인 연동', desc='거래소 간 유동성 통합, 자동 주문 배분, 체인 간 자산 이동을 처리하는 WalletFi 솔루션 PortX, SuperCycl을 직접 개발, 운영한 경험.'),
      dict(title='규제 친화형 DeFi, 유동성 인프라 기술', desc='통합 유동성 집계와 규제 준수형 거래 실행 등, 제도권 환경에 맞춘 DeFi 인프라 기술.'),
    ], label='퍼블릭·멀티체인 사례')}
  </div>
</div></section>
''')

# ---------------- portx.html ----------------
PAGES['portx.html'] = dict(
    title='PortX · 화이트라벨 거래소 솔루션 | PARAMETA',
    desc='PortX — 직접 구축 없이 자체 디지털자산 거래 플랫폼을 소유하는 가장 빠른 길. 화이트라벨 하이브리드 거래소 솔루션. 애그리게이션 엔진·Smart Access·논커스터디.',
    eyebrow='Exchange Solution',
    body_class='hero-dark portx',   # portx 식별 클래스(히어로 CTA 버튼 스왑용)
    h1_lines=['PortX'],
    lead='PortX는 여러 거래소(CEX, DEX)를 API로 연동해, 자사 브랜드의 디지털자산 거래 서비스를 만들 수 있게 하는 화이트라벨 솔루션입니다. 필요한 기능만 모듈로 골라 도입하고, 거래부터 운영까지 하나로 연결합니다.',
    crumb='Products — Port X',
    hero_visual='<img class="fit-contain" src="assets/portx/portx-hero.png" alt="" loading="eager" fetchpriority="high">',
    content=f'''
<section><div class="shell sec">
  <div class="whatis-grid">
    <div class="ps-flow rvl">
      <div class="ps-flow-band">
        <div class="ps-band-head">
          <span class="ps-band-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8"/><ellipse cx="12" cy="12" rx="3.5" ry="8"/><path d="M4 12h16"/></svg></span>
          <div class="lbl">글로벌 거래소</div>
        </div>
        <div class="ps-tags"><span class="ps-tag">Binance</span><span class="ps-tag">OKX</span><span class="ps-tag">Bybit</span><span class="ps-tag">Hyperliquid</span></div>
      </div>
      <div class="ps-flow-link" aria-hidden="true"></div>
      <div class="ps-flow-band ps-flow-core">
        <div class="ps-core-head">
          <img class="ps-flow-logo" src="assets/portx/portx.svg" alt="PortX" width="40" height="40" style="width:28px;height:28px;margin-top:-4px">
          <div class="ps-core-text">
            <div class="core-title">PortX</div>
            <div class="core-sub">외부 유동성과 거래 경험을 하나로</div>
          </div>
        </div>
        <div class="px-duo">
          <div class="px-mini">
            <div class="mi-head"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 12l9 5 9-5"/><path d="M3 16.5l9 5 9-5"/></svg>Aggregation Engine</div>
            <p class="pm-break">글로벌 CEX, DEX를 연동해, 여러 거래소의 유동성을 자사 서비스에 연결</p>
          </div>
          <div class="px-mini">
            <div class="mi-head"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="3.5" width="6.5" height="6.5" rx="1"/><rect x="14" y="3.5" width="6.5" height="6.5" rx="1"/><rect x="3.5" y="14" width="6.5" height="6.5" rx="1"/><path d="M14 14h3v3h-3z"/><path d="M20.5 14v2M14 20.5h2M18.5 18.5h2v2"/></svg>Smart Access</div>
            <p>외부 거래소 계정을 간편하게 연결해 거래 데이터와 기능을 연동</p>
          </div>
        </div>
      </div>
      <div class="ps-flow-link" aria-hidden="true"></div>
      <div class="ps-flow-band">
        <div class="ps-band-head">
          <span class="ps-band-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5.5" y="3" width="13" height="18" rx="2.5"/><path d="M10 17.5h4"/></svg></span>
          <div class="lbl">적용 서비스</div>
        </div>
        <div class="ps-tags"><span class="ps-tag">화이트라벨 거래</span><span class="ps-tag">간편 계정 연동</span><span class="ps-tag">거래 내역 조회</span></div>
      </div>
    </div>
    <div class="whatis-text rvl" style="--rvl-delay:120ms">
      {sec_head('What is PortX', '외부 유동성과 거래 경험을 연결하는<br>디지털자산 거래 인프라', 'PortX는 여러 글로벌 거래소를 API로 연동해, 자사 서비스 안에 디지털자산 거래 기능을 더하는 거래소 허브 솔루션입니다. 이미 있는 거래소들의 유동성과 거래 기능을 자사 브랜드로 연결하고, 전문 거래 화면부터 계정 연동까지 필요한 모듈만 골라 도입할 수 있습니다.', body=True)}
    </div>
  </div>
</div></section>
<section><div class="shell sec">
  {sec_head('Supported Exchanges', '주요 글로벌, 국내 거래소 유동성 연결', 'Binance, Bybit, OKX, Hyperliquid 등 주요 거래소를 연동해,<br>여러 거래소의 유동성을 한 화면에서 이용할 수 있습니다.', layout='center')}
  {card_grid([
    exchange_card('Binance', logo='assets/exchanges/binance.svg', brand='#F0B90B', dark_text=True),
    exchange_card('OKX', logo='assets/exchanges/okx.svg', brand='#000000', logo_dark=True),
    exchange_card('Bybit', logo='assets/exchanges/bybit.svg', brand='#F7A600', dark_text=True),
    exchange_card('Bitget', logo='assets/exchanges/bitget.svg', brand='#00F0FF', dark_text=True),
    exchange_card('Gate.io', logo='assets/exchanges/gate.svg', brand='#2354E6'),
    exchange_card('Hyperliquid', logo='assets/exchanges/hyperliquid.svg', brand='#97FCE4', dark_text=True),
    exchange_card('Bithumb', logo='assets/exchanges/bithumb.svg', brand='#F37321'),
    exchange_card('bitFlyer', logo='assets/exchanges/bitflyer.svg', brand='#00A0E9'),
    exchange_card('bitbank', logo='assets/exchanges/bitbank.svg', brand='#00C29E', dark_text=True),
  ], cols=3)}
</div></section>
<section><div class="shell sec">
  {sec_head('Why PortX', '거래소 구축 없이 시작하는 디지털자산 거래 서비스', '서비스에 거래 기능을 더하는 방법은 세 가지입니다. 거래소를 직접 만들거나, 거래 데이터만 연동하거나,<br>PortX처럼 외부 거래소를 연동해 거래까지 제공하는 방식입니다.')}
  <div class="why-table">{compare_table(
    ['', 'PortX<span class="cmp-flag">거래소 허브</span>', '거래소 직접 구축', '데이터 연동만<span class="cmp-flag cmp-flag-gray">조회형 API</span>'],
    [
      dict(label='무엇을 만드나', cells=['자사 브랜드 거래 서비스', '거래소 전체를 새로 구축', '계정, 거래내역 조회 기능']),
      dict(label='유동성', cells=['연동한 거래소들의 유동성 이용', '직접 확보하고 유지해야 함', '없음 (거래 불가)']),
      dict(label='거래 기능', cells=['주문, 거래 화면 기본 제공', '주문 체결(매칭엔진)부터 직접 개발', '미제공 (조회만 가능)']),
      dict(label='구축 부담', cells=['연동만으로 시작', '매칭엔진, 백오피스 등 전체 스택', '연동은 간편']),
      dict(label='자산, 보안 책임', cells=['비수탁 (민감정보 미보관)', '커스터디 운영, 보안 책임 전부 부담', '해당 없음']),
    ], hl=1, tabs=True)}</div>
</div></section>
<section><div class="shell sec">
  {sec_head('Why Now', '이미 일어나는 거래를, 내 서비스 안으로', '사용자는 정보를 내 서비스에서 찾고, 거래는 외부에서 실행합니다.<br>이제 그 거래 흐름과 수익 기회를 자사 서비스 안으로 가져올 차례입니다.')}
  <div class="ct-rows">{rows([
    dict(title='연 58.5조 달러의 시장', desc='중앙화 무기한 선물 시장에서 발생하는 거래 규모. 지금도 막대한 거래가 외부 거래소에서 이루어지고 있습니다.'),
    dict(title='거래는 여전히 외부에서', desc='정보 탐색은 내 서비스에서, 실제 거래는 외부 거래소에서. 수수료와 사용자 관계가 함께 빠져나갑니다.'),
    dict(title='그 흐름을 자사 매출로', desc='복잡한 거래소 구축 없이 화이트라벨로 빠르게 시작하고, 외부로 향하던 거래를 자사 브랜드 안의 실질 매출로 전환합니다.'),
  ])}</div>
</div></section>
<section><div class="shell sec">
  {sec_head('Key Features', '거래 경험을 연결하는 핵심 기능')}
  <div class="kf-media">{card_grid([
    card('Aggregation Engine', '주요 글로벌 거래소의 호가와 유동성을 한 화면에서 보고, 연동된 거래소를 통해 바로 주문합니다.', tags=['멀티 거래소 유동성 연결','단일 진입점 주문 연결'], media='assets/portx/feature-01.png', media_hover='assets/portx/feature-01-hover.png'),
    card('Smart Access', 'QR 코드로 외부 거래소 계정을 간편하게 연결해, API 키 입력 없이 빠르게 연동합니다.', tags=['QR 계정 연결','API 키 없는 연동'], media='assets/portx/feature-02.png', media_hover='assets/portx/feature-02-hover.png'),
    card('전문 거래 화면', '트레이더용 대시보드와 고급 차트(TradingView), 거래 UI/UX를 기본 제공합니다.', tags=['전문 대시보드','TradingView 차트'], media='assets/portx/feature-03.png', media_hover='assets/portx/feature-03-hover.png'),
    card('통합 성과관리', '여러 거래소의 성과를 한 대시보드에서 보고, 손익(PnL)을 정밀하게 분석합니다.', tags=['통합 대시보드','PnL 분석'], media='assets/portx/feature-04.png', media_hover='assets/portx/feature-04-hover.png'),
  ], cols=2)}</div>
</div></section>
<section><div class="shell sec uc-tail">
  {sec_head('Use Cases', '디지털자산 비즈니스의<br>시작부터 운영까지', layout='center')}
  <div class="uc-carousel">
    <button class="uc-arrow uc-prev rvl rvl-op" type="button" aria-label="이전 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5L8 12l7 7"/></svg></button>
    <div class="uc-slides rvl" style="--rvl-y:40px">
      <article class="uc-slide is-active">
        <div class="uc-thumb"><img src="assets/portx/uc-supercycl.png" alt="Supercycl"></div>
        <h3>Supercycl</h3>
        <p>Supercycl은 CEX와 DEX 유동성을 하나로 연결하는 디지털자산 무기한 선물 거래 플랫폼입니다.<br>Supercycl은 PortX의 Aggregation Engine과 Smart Access를 도입해 여러 거래소를 연동하고, 사용자가 하나의 환경에서 선물거래를 하도록 서비스를 운영합니다.</p>
        <div class="uc-testimonial">
          <div class="uc-avatar"><img src="assets/portx/uc-supercycl-pp.png" alt=""></div>
          <div class="uc-qbody">
            <p class="uc-quote">&ldquo;PortX 덕분에 자체 선물거래 서비스를 더 빠르게 시작할 수 있었습니다.&rdquo;</p>
            <p class="uc-name">Supercycl 헤드 개발자</p>
          </div>
        </div>
      </article>
      <article class="uc-slide">
        <div class="uc-thumb"><img src="assets/portx/uc-tass.png" alt="코인 세금 서비스"></div>
        <h3>코인 세금 서비스</h3>
        <p>거래소와 연동해 거래 내역을 불러오고, 예상 세금을 미리 계산해주는 디지털자산 세무 플랫폼입니다.<br>PortX의 Smart Access 모듈을 활용해 외부 거래소 계정 연결을 간소화하고, 세금 계산에 필요한 거래 정보를 서비스 안에서 활용합니다.</p>
        <div class="uc-testimonial">
          <div class="uc-avatar"><img src="assets/portx/uc-tass-pp.png" alt=""></div>
          <div class="uc-qbody">
            <p class="uc-quote">&ldquo;세금 계산에 필요한 거래 정보를 빠르게 가져올 수 있었습니다.&rdquo;</p>
            <p class="uc-name">코인 세금 서비스 CEO</p>
          </div>
        </div>
      </article>
    </div>
    <div class="uc-dots" aria-label="사례 선택"></div>
    <button class="uc-arrow uc-next rvl rvl-op" type="button" aria-label="다음 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></button>
  </div>
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
    hero_cta='',
    content=legal(['1. 수집하는 개인정보 항목','2. 개인정보의 이용 목적','3. 보유 및 이용 기간','4. 제3자 제공','5. 이용자의 권리','6. 개인정보 보호책임자 및 문의처']))

PAGES['terms.html'] = dict(
    title='이용약관 | PARAMETA',
    desc='PARAMETA 이용약관',
    eyebrow='Info',
    h1_lines=['이용약관'],
    lead='PARAMETA 서비스 이용에 대한 약관입니다.',
    crumb='Info — 이용약관',
    hero_cta='',
    content=legal(['제1조 (목적)','제2조 (정의)','제3조 (서비스의 제공)','제4조 (이용자의 의무)','제5조 (면책)']))


# ---------------- myid.html (DID 솔루션 — PR#1 기획 반영) ----------------
MYID_TRUST_LOGOS = [('logo-shinhan', '신한은행'), ('logo-nh', 'NH농협은행'), ('logo-nh-securities', 'NH투자증권'),
                    ('logo-samsung-securities', '삼성증권'), ('logo-samsung', '삼성'), ('logo-kb', 'KB'),
                    ('logo-ibk', 'IBK기업은행'), ('logo-hanwha', '한화'), ('logo-hyundai', '현대'), ('logo-mirae', '미래에셋증권')]

PAGES['myid.html'] = dict(
    title='MyID · 자기주권 분산신원 | PARAMETA',
    desc='MyID — 블록체인 기술로 신뢰는 그대로 유지하면서, 신원확인 단계를 줄이고 개인정보는 사용자가 직접 관리합니다. 구축형부터 공공 SaaS까지.',
    eyebrow='MY DATA · MY CHOICE · MY ID',
    h1_lines=['MyID'],
    lead='블록체인 기술로 신뢰는 그대로 유지하면서, 신원확인 단계를 줄이고 개인정보는 사용자가 직접 관리합니다. 수많은 적용 사례와 검증된 보안성을 바탕으로 구축형부터 공공 SaaS까지 제공합니다.',
    crumb='Products — MyID',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>''',
    hero_visual='<img class="fit-contain" src="assets/myid/hero-test.avif" alt="" loading="eager" fetchpriority="high">',
    content=f"""
<section><div class="shell sec">
  <ul class="stats-grid pv-stats on-light pv-2">
    <li class="rvl" style="--rvl-y:20px"><div class="stat-num">약 <span class="pv-hl"><span class="pv-val" data-val="370" data-from="360">360</span>만</span></div><div class="stat-label">MyID, DID 누적 이용자 수</div></li>
    <li class="rvl" style="--rvl-y:20px; --rvl-delay:90ms"><div class="stat-num">인증 <span class="pv-hl"><span class="pv-val" data-val="9100" data-from="9090">9,090</span>만+</span></div><div class="stat-label">제주안심코드 누적 인증 건수</div></li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {sec_head('Milestones', '국내외 최초 기록을 만들어온 DID')}
  <div class="firsts-hero rvl">
    <div class="fh-big" aria-hidden="true"><span class="fh-num">5<span class="st">건</span></span><span class="fh-cap">국내외 DID 최초</span></div>
    <ul class="fh-list">
      <li><span class="fh-chip world">세계 최초</span>블록체인 공동인증, 증권사 26개사</li>
      <li><span class="fh-chip">블록체인 최초</span>블록체인 서비스 최초 CSAP 인증</li>
      <li><span class="fh-chip">국내 최초</span>금융권 KYC DID 상용화</li>
      <li><span class="fh-chip">국내 최초</span>DID 기반 혁신금융서비스 지정</li>
      <li><span class="fh-chip">국내 최초</span>DID Method Registry 등록</li>
    </ul>
  </div>
</div></section>
<section id="lineup"><div class="shell sec" style="padding-top:0">
  {sec_head('Lineup', 'MyID vs MyID 2.0', '같은 DID 플랫폼을 대상에 맞게 두 갈래로 제공합니다. 민간은 MyID, 공공기관은 K-BTF 공동 인프라 기반 MyID 2.0으로 도입합니다.')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('민간 · 기업 · 금융', 'MyID', '기업·금융·민간 서비스가 자체 신원인증을 구축합니다. 도입 방식은 구축형과 서비스형 두 가지 중에서 선택합니다.', ['구축형 (On-Premise)','서비스형 (SaaS)'], grouped=True)}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('공공기관 전용', 'MyID 2.0 (K-BTF)', '공공기관은 CSAP 보안인증을 받은 서비스만 이용할 수 있습니다. MyID 2.0은 블록체인 서비스 최초 CSAP 인증 SaaS로, 과기정통부·KISA 주관 K-BTF 공동 인프라 위에서 별도 구축 없이 도입합니다.', ['공동 인프라 구독형 SaaS','CSAP 인증'], grouped=True)}</li>
  </ul>
  <div class="why-table" style="margin-top:var(--space-40)">{compare_table(['', 'MyID', 'MyID 2.0 (K-BTF)'], [
    dict(label='대상', cells=['기업 · 금융 · 민간 서비스', '공공기관 · 지자체']),
    dict(label='도입 방식', cells=['구축형(On-Premise) · 서비스형(SaaS)', 'K-BTF 공동 인프라 구독형 SaaS']),
    dict(label='인증', cells=['W3C 표준 DID · 금융권 KYC 상용화', '블록체인 서비스 최초 CSAP 인증 — 공공기관 도입 요건 충족']),
    dict(label='도입 기간', cells=['규모·방식에 따라 협의', '최대 1주일']),
    dict(label='예상 비용', cells=['도입 방식·규모별 협의', '월 200만원~ + 건당 과금']),
    dict(label='', cells=['<a href="contact.html">도입·요금 상담 신청</a>', '<a href="https://zzeung.kr/" target="_blank" rel="noopener">K-BTF 홈페이지 →</a>']),
  ], hl=2, tabs=True)}</div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  <div class="did-hub rvl" style="--rvl-y:24px">
    {sec_head('Platform', '개인정보는 쌓지 않고, 신원은 사용자가 통제합니다', 'MyID는 블록체인 기반 DID 플랫폼입니다. 신원증명(VC)을 사용자 지갑에 보관하고 필요한 정보만 선택 제출하며, W3C 표준 기반으로 발급·검증·연동을 제공합니다. 아래 4가지 구성으로 서비스에 바로 붙일 수 있습니다.')}
    <div class="did-ring">
      <div class="did-node">
        <span class="did-role">Issuer</span>
        <b>신원인증기관</b>
        <span class="did-sub">VC 발급</span>
      </div>
      <div class="did-link"><span>VC 발급</span></div>
      <div class="did-node is-core">
        <span class="did-role">Holder</span>
        <b>사용자 · DID 지갑</b>
        <span class="did-sub">지갑에 보관, 필요한 정보만 제출</span>
      </div>
      <div class="did-link"><span>선택 제출</span></div>
      <div class="did-node">
        <span class="did-role">Verifier</span>
        <b>서비스제공자</b>
        <span class="did-sub">검증</span>
      </div>
    </div>
    <div class="did-infra">
      <div class="did-infra-t">MyID 블록체인</div>
      <p>세 주체 모두 MyID 위에서 DID 등록, 블록체인으로 무결성 검증</p>
    </div>
  </div>
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{card('MyID 파트너센터', '코드 없이 DID·VC를 생성하고, 검증 항목을 구성할 수 있는 관리자 콘솔입니다. 발급·검증 이력과 인증 절차를 대시보드에서 통합 관리합니다.', kicker='Console', tags=['DID·VC 생성','검증 항목 설정','이력 대시보드'], tone='gray')}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{card('DID 지갑', '사용자가 자신의 DID와 VC를 직접 관리하는 신원 지갑입니다. Wallet SDK로 서비스 앱에 지갑 기능을 연동하고, 외부 발급 VC도 보관·이용할 수 있습니다.', kicker='Wallet', tags=['Wallet SDK','외부 VC 보관','PDS 암호화'], tone='gray')}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:180ms">{card('MyID API', 'DID 관리, VC 발급과 유효성 검증, VP 검증 등 신원 인증에 필요한 기능을 API로 제공합니다. 여러 블록체인과 연결된 통합 API로 외부 VC 연계도 지원합니다.', kicker='API', tags=['VC 발급','VC·VP 검증','외부 VC 연계'], tone='gray')}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:270ms">{card('블록체인 BaaS', 'MyID 서비스에 필요한 퍼블릭·프라이빗 블록체인 환경을 서비스 형태로 제공합니다. loopchain core2 기반으로 안정적인 DID 서비스 운영을 지원합니다.', kicker='BaaS', tags=['퍼블릭·프라이빗','loopchain core2'], tone='gray')}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {sec_head('Technology', '데이터 주권과 프라이버시를 지키는 핵심 기술')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('Tech 01', 'PDS + BFS — 개인 데이터 저장소 · 분산 파일 저장', '계속 바뀌는 내 데이터는 개인 데이터 저장소(PDS)에 본인 통제로 보관하고, 문서·이미지 같은 대용량 파일은 여러 노드에 다중 복제하는 블록체인 파일 시스템(BFS)에 유실 없이 저장합니다.', ['데이터 주권','멀티 피닝'], grouped=True)}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('Tech 02', 'Zero-Knowledge Proof — 영지식증명', '원본 정보를 드러내지 않고도 "성인이다", "특정 자격이 있다" 같은 사실만 증명합니다. 범위 증명·소속 증명을 지원합니다.', ['범위 증명','소속 증명'], grouped=True)}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:180ms">{dark_card('Tech 03', 'Selective Disclosure — 선택적 공개', '증명서 전체가 아니라 요구된 항목만 골라 제출합니다. 불필요한 개인정보는 아예 공개하지 않습니다.', ['최소 공개'], grouped=True)}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:270ms">{dark_card('Tech 04', 'Issuer Privacy — 발급자 비식별', '검증 과정에서 어느 기관이 발급했는지까지 감춰, 발급 이력이 불필요하게 노출되지 않도록 보호합니다.', ['프라이버시'], grouped=True)}</li>
  </ul>
</div></section>
<section><div class="shell sec">
  <div class="pt-marquee rvl" aria-label="함께한 파트너 로고">
    <div class="pt-track">{partner_logos(MYID_TRUST_LOGOS)}{partner_logos(MYID_TRUST_LOGOS)}</div>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {sec_head('References', '금융·공공·기업이 검증한 적용 사례', layout='center')}
  {usecase_carousel([
    dict(cat='Finance', title='신한은행, NH농협은행 금융실명인증', desc='기존 실명확인 3단계를 MyID 1단계로 통합해 비대면 실명인증을 간소화했습니다. NH농협은행은 올원뱅크 올원PASS 발급, 재발급, 송금 이체한도 상향 등에 적용했습니다.'),
    dict(cat='Public', title='제주안심코드', desc='제주도청과 함께 개발한 전자출입명부 서비스로, QR 스캔만으로 출입 정보를 남길 수 있게 했습니다. 설치 업장 6만 개, 앱 설치 218만 건, 누적 인증 9,100만 건을 기록했습니다.'),
    dict(cat='Public', title='질병관리청 백신접종증명', desc='질병관리청 시스템과 연동해 백신 접종 정보를 신원증명서(VC)로 발급하고, 제주안심코드 전자출입명부와 결합해 제출할 수 있게 했습니다.'),
    dict(cat='Public', title='강원도 나야나', desc='강원도 행정, 경제, 복지 통합 서비스에 DID 기반 신원인증을 적용했습니다.'),
    dict(cat='Public, Healthcare', title='강원도 만성질환 통합관리 플랫폼', desc='과기정통부, KISA 2020 블록체인 공공선도 시범사업(의료 부문)으로, DID 기반 사용자 인증과 건강정보 자기주권 관리 체계를 구축했습니다. 심뇌혈관 만성질환자의 건강정보를 안전하게 관리하고 AI 분석, IoMT 측정 데이터를 모바일로 제공합니다.'),
    dict(cat='Public', title='경상북도 모이소', desc='행정안전부 우수 서비스로 선정된 도민 앱입니다. 경북도청과 함께 도민증 발급부터 복지급여 신청, 공공 마이데이터 연계, 관광 QR까지 하나로 제공했습니다.'),
    dict(cat='Public', title='부산시 배터리여권 플랫폼 (DPP)', desc='전기차 배터리의 제조, 운행, 정비, 재활용 데이터를 DID, VC, PDS로 연결해, EU 배터리 규제(DPP)에 맞춰 출처, 이력, 무결성을 증명하는 데이터 플랫폼입니다.'),
    dict(cat='Public', title='KCA 블록체인 선박검사 관리 플랫폼', desc='KISA 블록체인 시범사업으로, 중앙전파관리소, KCA, KOMSA, 수협에 흩어진 무선국 허가, 선박검사 증서를 블록체인으로 연계, 조회하고 검사 증서를 NFT로 발행합니다. 서류 위변조와 분실 위험을 낮춰 해양안전 데이터의 신뢰성을 높입니다.'),
    dict(cat='Public', title='KOMSA 선박 전자증서 검증', desc='연 약 56만 회 반복 검증되는 선박검사 전자증서에 DID, VC 발급, 검증과 PDS를 결합해, 위변조 확인 부담을 줄이는 검증체계를 구축했습니다.'),
    dict(cat='Enterprise', title='WattEver 배터리 잔존수명 인증서', desc='중고, 재사용 배터리 거래에서 잔존수명 인증 데이터를 PDS 기반으로 저장, 검증해, 위변조 없이 신뢰할 수 있게 합니다.'),
    dict(cat='Enterprise', title='포스코 체인지업그라운드', desc='출입통제부터 방문자 초대, 사무기기 이용, 공간 예약, 주차관리까지 DID 신원인증 하나로 처리했습니다. 포스코, 포스텍, RIST 구성원은 소속 증명만으로 시설을 이용했습니다.'),
  ])}
</div></section>
""")

# ---------------- broof.html ----------------
_broof_orgs = ['서울특별시','POSTECH','한국생산성본부','사람인','인천','한경닷컴','한빛미디어','스터디파이','아트앤가이드','호서대','해시넷','서울시민청']
_broof_chips = ''.join(f'<span class="tag on-light">{o}</span>' for o in _broof_orgs)
# 기관별 근사 브랜드 컬러(실제 브랜드값은 추후 교체). 호버 시 카드 배경으로 사용.
_broof_brand = {
    '서울특별시':'#1f4e9c', 'POSTECH':'#86192b', '한국생산성본부':'#0b4da2', '사람인':'#0e5ee6',
    '인천':'#00a3a5', '한경닷컴':'#e60012', '한빛미디어':'#d81f26', '스터디파이':'#5b47e0',
    '아트앤가이드':'#b8863b', '호서대':'#2bb6a4', '해시넷':'#2f6df6', '서울시민청':'#e5673b',
}
_broof_logo_cards = ''.join(
    f'<li class="rvl" style="--rvl-y:20px; --rvl-delay:{i*40}ms">'
    f'<article class="logo-card" style="--brand:{_broof_brand.get(o, "var(--purple-500)")}"><span class="logo-ico"></span>{o}</article></li>'
    for i, o in enumerate(_broof_orgs))
PAGES['broof.html'] = dict(
    title='Broof · 블록체인 증명서 발급 | PARAMETA',
    desc='Broof — 블록체인 기반 증명서 발급·검증 서비스. 위·변조를 방지하는 디지털 증명서를 발급하고, 누구나 즉시 진위를 확인합니다.',
    eyebrow='Digital Credentials',
    body_class='hero-dark broof',   # broof 식별 클래스(히어로 새 버튼)
    h1_lines=['Broof'],
    lead='별도 시스템 구축 없이 증명서를 간편하게 발급하고, QR 코드 하나로 진위를 즉시 검증합니다. 블록체인으로 증명서의 위조와 분실 위험까지 낮춥니다.',
    crumb='Products — Broof',
    hero_visual='<img class="fit-contain" src="assets/broof/hero-test.avif" alt="" loading="eager" fetchpriority="high">',
    hero_cta='''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light with-arrow arw-right hs-scale cta-talk" href="contact.html"><span class="hspring">Go to Broof<span class="pill-badge"><svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M13 6l6 6-6 6"/></svg></span></span></a>
    </div>''',
    content=f"""
<section><div class="shell sec" style="padding-bottom:0">
  <ul class="stats-grid pv-stats on-light">
    <li class="rvl" style="--rvl-y:20px"><div class="stat-num">정부 위원회 <span class="pv-hl">최초</span></div><div class="stat-label">블록체인 위촉장 발급</div></li>
    <li class="rvl" style="--rvl-y:20px; --rvl-delay:90ms"><div class="stat-num">누적 <span class="pv-hl"><span class="pv-val" data-val="90000" data-from="89991">89,991</span>건+</span></div><div class="stat-label">증명서 발급</div></li>
    <li class="rvl" style="--rvl-y:20px; --rvl-delay:180ms"><div class="stat-num">누적 <span class="pv-hl"><span class="pv-val" data-val="20" data-from="11">11</span>개 기관+</span></div><div class="stat-label">대학, 공공기관, 기업 도입</div></li>
  </ul>
</div></section>
<section><div class="shell sec">
  {sec_head('Overview', '시스템 구축 없이 완성하는 디지털 증명서', '별도 시스템 구축 없이 웹에서 증명서를 발급하고, QR 코드 하나로 원본을 즉시 확인합니다. 졸업증명서, 수료증, 위촉장, 자격증 등 다양한 형태로 활용할 수 있습니다.', lead_mx=grid_cols_w(7))}
  {card_grid([
    card('위·변조 방지', '발급 즉시 블록체인에 기록해, 내용이 변경되면 원본과의 불일치를 확인할 수 있습니다.', kicker='TAMPER-PROOF', media=True),
    card('즉시 검증', 'QR 코드 하나로 원본 여부와 위·변조 여부를 바로 확인합니다.', kicker='VERIFY', media=True),
    card('간편 발급', '명단만 등록하면 수백 건의 증명서도 한 번에 발급할 수 있습니다.', kicker='ISSUE', media=True),
  ], cols=3)}
</div></section>
<section><div class="shell sec">
  {sec_head('Workflow', '올리고, 발급하고, 확인하면 끝', '증명서 양식과 명단만 등록하면, 발급부터 QR 검증까지 간단하게 이어집니다.')}
  <div class="ct-rows">{rows([
    dict(title='템플릿, 명단 등록', desc='발급기관이 증명서 템플릿을 만들고, 수령자 정보를 담은 명단을 CSV로 일괄 등록합니다. 여러 명의 증명서도 한 번에 준비할 수 있습니다.'),
    dict(title='발급, 블록체인 기록', desc='등록된 명단을 바탕으로 증명서가 자동 발급되고, 원본 정보와 해시값이 블록체인에 기록됩니다. 이후 내용이 변경되면 원본과의 차이를 확인할 수 있습니다.'),
    dict(title='수령, 즉시 검증', desc='수령자는 카카오톡이나 이메일로 증명서를 받고, 제출처는 별도 프로그램 없이 QR 코드나 링크로 진위 여부를 즉시 확인합니다.'),
  ])}</div>
</div></section>
<section><div class="shell sec">
  <div class="cm-grid">
    <div class="cm-head">
      <div class="cm-sticky">
        <div class="cm-head-in rvl" style="--rvl-y:20px">
          <div class="eyebrow dark"><span class="dot"></span>Core Features</div>
          <h2 class="sec-h2" style="max-width:24ch">알림부터 현황 관리,<br>과금까지 한 번에</h2>
        </div>
      </div>
    </div>
  <ul class="cm-cards core-mods cm-sm">
    <li>{dark_card('NOTIFY', '자동 알림', '증명서가 발급되면 수령자에게 카카오톡과 이메일로 안내가 자동 발송됩니다. 담당자가 개별적으로 연락하지 않아도 발급 사실과 확인 방법을 빠르게 전달할 수 있습니다.', grouped=True)}</li>
    <li>{dark_card('DASHBOARD', '발급 현황 대시보드', '발급된 증명서의 발급, 폐기, 만료 상태를 대시보드에서 한눈에 확인할 수 있습니다. 여러 담당자가 함께 발급 내역을 확인하고 체계적으로 관리할 수 있습니다.', grouped=True)}</li>
    <li>{dark_card('USAGE', '사용량 기반 과금', '정기구독료 없이 실제로 증명서를 발급한 만큼만 비용이 부과됩니다. 발급량이 많지 않은 기관도 초기 부담 없이 필요한 시점부터 유연하게 이용할 수 있습니다.', grouped=True)}</li>
  </ul>
  </div>
</div></section>
<section><div class="shell sec">
  {sec_head('Trusted By', '공공기관, 대학, 기업이 선택한 Broof', '공공기관·대학부터 기업까지, 다양한 현장에서 Broof로 증명서를 발급하고 진위를 검증합니다.')}
  <ul class="logo-grid">{_broof_logo_cards}</ul>
</div></section>
<section><div class="shell sec" style="padding-top:9rem">
  {sec_head('Applied Cases', '대학, 공공기관, 기업이<br>선택한 디지털 증명서', layout='center')}
  <div class="uc-carousel bc-cases">
    <button class="uc-arrow uc-prev rvl rvl-op" type="button" aria-label="이전 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5L8 12l7 7"/></svg></button>
    <div class="uc-slides rvl" style="--rvl-y:40px">
      <article class="uc-slide is-active">
        <div class="bc-cert" aria-hidden="true"></div>
        <div class="bc-body">
          <h3>POSTECH</h3>
          <p>블록체인 전문가과정 수료증을 Broof로 정기 발급합니다. 수료자는 QR 코드 하나로 어디서나 수료 사실을 증명하고, 대학은 재발급·진위 확인 업무 부담을 덜었습니다.</p>
          <div class="uc-testimonial">
            <div class="uc-avatar" aria-hidden="true"></div>
            <div class="uc-qbody">
              <p class="uc-quote">&ldquo;코로나19로 졸업식 대신 카카오톡으로 디지털 졸업장을 전달했어요.&rdquo;</p>
              <p class="uc-name">POSTECH 담당자</p>
            </div>
          </div>
        </div>
      </article>
      <article class="uc-slide">
        <div class="bc-cert" aria-hidden="true"></div>
        <div class="bc-body">
          <h3>아트앤가이드</h3>
          <p>미술품 공동구매의 소유권을 블록체인 증명서로 발급합니다. 구매자는 QR 코드로 소유권을 즉시 확인하고, 소유 이력의 신뢰를 높였습니다.</p>
          <div class="uc-testimonial">
            <div class="uc-avatar" aria-hidden="true"></div>
            <div class="uc-qbody">
              <p class="uc-quote">&ldquo;블록체인으로 작품 소유권을 등록하니 소유권의 신뢰도가 높아졌어요.&rdquo;</p>
              <p class="uc-name">아트앤가이드 담당자</p>
            </div>
          </div>
        </div>
      </article>
      <article class="uc-slide">
        <div class="bc-cert" aria-hidden="true"></div>
        <div class="bc-body">
          <h3>패스트캠퍼스</h3>
          <p>온라인 강의 수료증을 Broof로 발급합니다. 수료자는 QR 코드 하나로 수료 사실을 증명하고, 기관은 발급, 재발급 업무 부담을 덜었습니다.</p>
          <div class="uc-testimonial">
            <div class="uc-avatar" aria-hidden="true"></div>
            <div class="uc-qbody">
              <p class="uc-quote">&ldquo;broof 이용으로 증명서 발급에 들던 시간이 매우 줄어들었어요.&rdquo;</p>
              <p class="uc-name">패스트캠퍼스 담당자</p>
            </div>
          </div>
        </div>
      </article>
    </div>
    <div class="uc-dots" aria-label="사례 선택"></div>
    <button class="uc-arrow uc-next rvl rvl-op" type="button" aria-label="다음 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></button>
  </div>
</div></section>
""")

# ---------------- contact.html ----------------
PAGES['contact.html'] = dict(
    title='문의 · 무료 컨설팅 | PARAMETA',
    desc='스테이블코인·STO 1:1 무료 컨설팅 신청. 파라메타 디지털자산 인프라 도입 문의.',
    eyebrow='Contact',
    body_class='contact',
    h1_lines=['Contact'],
    lead='궁금하신 사항이 있으시면 문의하기를 이용해주세요.<br>담당자가 자세하게 안내해드리겠습니다.',
    crumb='Contact — 문의 · 무료 컨설팅',
    hero_cta='',
    content=f"""
<section><div class="shell sec">
  <div class="contact-split" style="align-items:start">
    <div class="light-card rvl">
      <span class="cap">컨설팅 신청</span>
      <p style="margin-bottom:1.5rem">담당자가 영업일 기준 1~2일 내 회신드립니다. 모든 정보는 컨설팅 목적으로만 사용됩니다.</p>
      <form class="modal-form" id="contactForm">
        <div class="cards-2" style="column-gap:1rem; row-gap:var(--space-24)">
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
        <div class="privacy-guide">
          <strong>개인정보 수집·이용에 대한 안내</strong>
          <span class="pg-item">수집 목적 : 회원 문의사항 처리</span>
          <span class="pg-item">수집 항목 : 성, 이름, 이메일, 전화번호, 법인명</span>
          <span class="pg-item">보유 및 이용기간 : 3년 보관 후 즉시 파기</span>
        </div>
        <div class="modal-bottom" style="justify-content:flex-start">
          <button class="pill dark with-arrow arw-up hs-scale" type="submit">
            <span class="hspring"><span id="cfSubmitLabel">상담 신청</span><span class="pill-badge">{ARW}</span></span>
          </button>
        </div>
      </form>
    </div>
    <div class="rvl" style="--rvl-delay:120ms">
      <div class="light-card" style="margin-bottom:1.5rem">
        <span class="cap">바로 문의하기</span>
        <p style="margin-bottom:1.25rem">폼 작성이 번거롭다면 연락주세요.</p>
        <div class="addr-list">
          <div><div class="k">Email</div><div class="v">info@parametacorp.com</div></div>
          <div><div class="k">Tel</div><div class="v">02-2138-7026</div></div>
          <div><div class="k">Hours</div><div class="v">평일 9:00 – 20:00</div></div>
        </div>
      </div>
    </div>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {sec_head('Process', '컨설팅은 3단계로 진행됩니다')}
  {cards_wrap([
    dark_card('STEP 01', '상담 신청', '폼을 작성해 주시면 담당자가 영업일 기준 1~2일 이내에 회신드립니다.'),
    dark_card('STEP 02', '1:1 컨설팅', '온라인 또는 오프라인 미팅을 통해 사업 단계, 요구사항, 예산을 함께 정리합니다.'),
    dark_card('STEP 03', '제안 및 검토', '요구사항에 맞는 솔루션 구성과 단계별 도입 로드맵을 제안서로 제공합니다.'),
  ], cols=3)}
</div></section>
""")

# ================= SOLUTION 6종 (신규) =================

# ---------------- solution-finance.html ----------------
PAGES['solution-finance.html'] = dict(
    title='금융 디지털자산 솔루션 | PARAMETA',
    desc='규제 환경에 맞춘 엔터프라이즈 디지털자산 금융 플랫폼. 발행·지갑·오케스트레이션·온체인 KYC·통합관제를 하나로. 스테이블코인·예금토큰·RWA·토큰증권까지 단계적 확장.',
    eyebrow='Solutions — 금융',
    h1_lines=['규제 대응부터 정산, 상환까지,', '금융기관의 디지털자산 인프라'],
    lead='발행, 지갑, 계좌·지갑 연동, 온체인 KYC, 통합 관리를 하나로 연결합니다. 스테이블코인부터 예금토큰, RWA, 토큰증권까지 규제와 사업 환경에 맞춰 단계적으로 확장할 수 있습니다.',
    crumb='Solutions — 금융',
    hero_cta='''<div class="phero-rel rvl" style="--rvl-delay:600ms">
      <p class="phero-rel-t">관련 제품 살펴보기</p>
      <a class="phero-rel-flag" href="parasta.html">ParaSta</a>
    </div>''',
    hero_visual='<img src="assets/solutions/hero-test-1.webp" alt="" loading="eager" fetchpriority="high">',
    content=f"""
<section><div class="shell sec sec-top-lg sec-stagger">
  {sec_head('Why Now', '발행보다 중요한 것은 발행 이후입니다', '글로벌 대형 자산운용사와 결제사는 이미 RWA와 스테이블코인 시장에 진입했고, 국내에서도 토큰증권 제도화가 논의되고 있습니다. 토큰은 발행보다 유통·보유·상환 과정의 규제와 운영 리스크 관리가 더 어렵습니다.')}
  {lead_p('투자자 적격성과 고객확인(KYC)·자금세탁방지(AML) 요건을 계속 검증해야 합니다. 배당·이자 지급과 상환을 정확히 집행하고, 지갑 간 자산 이동을 실시간으로 통제·감사해야 합니다.')}
  <div class="colc-duo">
  {col_chart([
    dict(l='2024년', v='34조원', w=9),
    dict(l='2025년', v='119조원', w=32),
    dict(l='2030년', v='367조원', w=100, hi=True),
  ], title='국내 토큰증권(STO) 시장 규모 전망', note='<strong>출처: 하나금융경영연구소·삼일PwC(BCG 전망 인용)</strong><br>현행 자본시장법 기준 30~60조원의 보수적 전망도 있습니다. 위 수치는 전망치입니다.')}
  {col_chart([
    dict(l='2025년 1월', v='$2,050억', w=68),
    dict(l='2025년 말', v='$3,000억+', w=100, hi=True),
  ], title='글로벌 스테이블코인 발행 잔액 추이', note='<strong>출처: DeFiLlama 등 시장 데이터 집계</strong><br>2025년 발행 잔액은 전년 대비 약 49% 증가. 온체인에서 유통 중인 자산 기준 실측치입니다.')}
  </div>
</div></section>
<section><div class="shell sec">
  {sec_head('Problem', '디지털자산 사업의 과제, 이렇게 해결합니다')}
  {ww_compare('발행 이후의 운영을 각자 감당해야 합니다', '발행부터 운영까지 하나로 연결합니다', [
    ('발행보다 복잡한 운영', '디지털자산은 발행 이후 KYC, 상환, 유통 통제, 사후 검증까지 지속적인 운영이 필요합니다.',
     '발행부터 운영까지 한 곳에서', '발행, KYC, 상환, 유통 통제를 하나로 연결해 관리합니다.'),
    ('계좌 따로, 온체인 지갑 따로', '은행 계좌와 온체인 지갑이 분리되어 있어 자산 관리와 정산이 복잡합니다.',
     '계좌와 지갑을 연결', '은행 계좌와 온체인 지갑을 이어, 자산 관리와 정산을 한 흐름으로 처리합니다.'),
    ('규제 대응 부담', '서비스마다 자금세탁방지(AML)와 트래블룰 준수 체계를 별도로 설계해야 합니다.',
     '규제 대응을 기본 제공', 'AML, 트래블룰 대응을 기본으로 갖춰, 서비스마다 따로 설계하지 않아도 됩니다.'),
    ('범용 SaaS의 한계', '글로벌 지갑 SaaS만으로는 국내 규제와 금융기관의 운영 요건에 대응하기 어렵습니다.',
     '국내 규제에 맞춘 설계', '국내 규제와 금융기관 운영 요건에 맞춰 설계했습니다.'),
  ], after_cap='ParaSta 도입 후')}
</div></section>
<section><div class="shell sec">
  {sec_head('Features', '발행부터 상환·사후 검증까지 연결하는<br>6-Layer 통제 구조', '디지털자산의 발행·유통·상환·사후 검증 전 과정을 6개의 통제 계층으로 연결해 안정적으로 관리합니다.')}
  {cards_wrap([
    exchange_card('Issuance · 발행', brand='var(--purple-500)', desc='규제를 준수하며 디지털자산의 발행·상환·유통을 통제합니다.'),
    exchange_card('Wallet · 지갑', brand='var(--purple-500)', desc='사용자 신원을 기반으로 자산을 통제하고, 여러 블록체인 지갑을 하나의 인터페이스에서 관리합니다.'),
    exchange_card('Orchestration · 오케스트레이션', brand='var(--purple-500)', desc='은행 계좌와 온체인 지갑을 연결해 조건부 정산과 실시간 거래 점검을 처리합니다.'),
    exchange_card('On-chain KYC · 온체인 신원 인증', brand='var(--purple-500)', desc='검증된 KYC 정보를 위·변조 확인이 가능한 디지털 증명(VC·VP)으로 변환해, 여러 블록체인에서 활용합니다.'),
    exchange_card('Unified Admin · 통합 관리', brand='var(--purple-500)', desc='전체 운영 현황과 키 권한을 통합 관리하고, 감사에 필요한 리포트를 제공합니다.'),
    exchange_card('Parameta S · RWA·STO 연동', brand='var(--purple-500)', desc='API를 통해 토큰증권과 실물자산의 발행부터 이후 운영까지 연결합니다.'),
  ], cols=3)}
</div></section>
<section><div class="shell sec">
  {sec_head('How to Adopt', '단계적으로 도입할 수 있습니다', '필요한 기능부터 시작해 운영 환경과 사업 단계에 맞춰 확장합니다.')}
  <div class="ct-rows">{rows([
    dict(title='<em class="t-acc">4주</em> : PoC · 개념 검증', desc='도입 범위를 정하고 발행·지갑·온체인 KYC 등 핵심 기능의 적용 가능성을 검증합니다.'),
    dict(title='<em class="t-acc">12주</em> : Pilot · 파일럿 운영', desc='제한된 환경에서 계좌·지갑 연동과 정산·거래 통제 등 주요 운영 절차를 검증합니다.'),
    dict(title='<em class="t-acc">4~6개월</em> : 상용 전환', desc='검증된 기능을 기존 시스템과 연동하고, 보안·관제·감사 체계를 갖춰 상용 서비스로 전환합니다.'),
  ])}</div>
</div></section>
<!-- By the Numbers: Proven Core식 다크 스탯 패널 -->
<section><div class="shell stats-shell">
  <div class="stats-panel rvl" style="--rvl-y:40px; --rvl-s:.99">
    <div class="eyebrow light"><span class="dot"></span>By the Numbers</div>
    <h2 class="stats-h2" data-line-reveal style="max-width:none"><span class="rvl-line"><span>디지털자산 금융을 위한<br>핵심 기술과 운영 체계</span></span></h2>
    <ul class="stats-grid sg-2x2">
      <li class="rvl" style="--rvl-y:20px"><div class="stat-num"><span class="pv-val" data-val="4">0</span>개 핵심 모듈</div><div class="stat-label">발행, 지갑, 계좌·지갑 연동, 온체인 KYC</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:90ms"><div class="stat-num"><span class="pv-val" data-val="6">0</span> Layer</div><div class="stat-label">발행부터 상환까지 이어지는 구조</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:180ms"><div class="stat-num"><span class="pv-val" data-val="2">0</span>단계 도입</div><div class="stat-label">4주 PoC와 12주 Pilot을 거쳐 단계적으로 도입</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:270ms"><div class="stat-num"><span class="pv-val" data-val="100000">0</span> TPS</div><div class="stat-label">제한된 테스트 환경에서 측정한 loopchain 최대 처리 성능</div></li>
    </ul>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {sec_head('Credentials', '금융·공공 분야에서 검증된 기술력', '기술보증기금 TI-1, CSAP 인증, 혁신금융서비스 지정을 받았습니다.')}
  <div class="cert-row rvl" style="--rvl-y:24px; padding:var(--space-32) 0 0">
    <div class="cert-item"><div class="cert-img"></div><div class="cert-txt">기술보증기금 TI-1</div></div>
    <div class="cert-item"><div class="cert-img"></div><div class="cert-txt">CSAP 인증</div></div>
    <div class="cert-item"><div class="cert-img"></div><div class="cert-txt">혁신금융서비스 지정</div></div>
  </div>
</div></section>
<section><div class="shell sec">
  {sec_head('FAQ', '자주 묻는 질문')}
  {faq([
    dict(q='스테이블코인과 예금토큰은 무엇이 다른가요?', a='스테이블코인은 법정화폐 등 특정 자산의 가치에 연동되도록 설계된 디지털자산입니다. 예금토큰은 은행 예금을 블록체인상에서 사용할 수 있도록 토큰화한 것으로, 발행 주체와 담보 구조, 적용 규제가 다릅니다.'),
    dict(q='STO와 RWA는 무엇인가요?', a='STO는 주식·채권 등 증권의 권리를 토큰으로 발행하는 방식이며, RWA는 부동산·채권·원자재 등 실물 및 금융자산을 블록체인과 연결하는 개념입니다. 두 방식 모두 발행 이후 유통·정산·상환을 관리할 수 있는 운영 인프라가 필요합니다.'),
  ])}
</div></section>
<section><div class="shell sec">
  {sec_head('Use Cases', '디지털자산 금융 적용 사례', layout='center')}
  <div class="uc-carousel uc-tall uc-lg">
    <button class="uc-arrow uc-prev rvl rvl-op" type="button" aria-label="이전 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5L8 12l7 7"/></svg></button>
    <div class="uc-slides rvl" style="--rvl-y:40px">
      <article class="uc-slide is-active">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>NH투자증권 · STO 비전그룹 참여</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">활용 영역</span><span>토큰증권 발행 이후의 운영·관리 인프라</span></div><div class="uc-row"><span class="uc-flag">주요 내용</span><span>토큰증권 발행·운영 체계 논의에 기술 파트너로 참여</span></div></div>
      </article>
      <article class="uc-slide">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>쿠콘 · 인피닛블록 MOU</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">활용 영역</span><span>스테이블코인 발행·정산·결제 및 API 연계</span></div><div class="uc-row"><span class="uc-flag">주요 내용</span><span>스테이블코인 기반 금융 서비스 연계를 위한 업무협약 체결</span></div></div>
      </article>
      <article class="uc-slide">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>ADB ABMF · 온체인 KYC 발표</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">활용 영역</span><span>국경 간 투자자의 지갑·사용자 신원 및 적격성 확인</span></div><div class="uc-row"><span class="uc-flag">주요 내용</span><span>지갑 인증과 온체인 KYC, 지갑 검증(KYW) 적용 방안을 국제 협의체에서 발표</span></div></div>
      </article>
    </div>
    <button class="uc-arrow uc-next rvl rvl-op" type="button" aria-label="다음 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></button>
  </div>
</div></section>
""")

# ---------------- solution-gov.html ----------------
PAGES['solution-gov.html'] = dict(
    title='공공 블록체인 솔루션 | PARAMETA',
    desc='1년 걸리던 공공 블록체인을 1주일 만에 도입. 블록체인 서비스 최초 CSAP 인증 SaaS로 DID, 지갑, 개인데이터저장소(PDS), 분산저장(BFS)을 직접 구축 없이 구독형으로. 신청 4단계, 최대 1주일 내 적용.',
    eyebrow='Solutions — 공공',
    h1_lines=['1년 걸리던 공공 블록체인,', '1주일 만에 도입합니다'],
    lead='<b>블록체인 서비스 최초 CSAP 인증 SaaS</b><br>DID·지갑·개인데이터저장소(PDS)·분산저장(BFS) 기반 서비스를 직접 구축하지 않고 구독형으로 도입합니다. 신청 4단계, 최대 1주일 내 적용.',
    crumb='Solutions — 공공',
    hero_cta='''<div class="phero-rel rvl" style="--rvl-delay:600ms">
      <p class="phero-rel-t">관련 제품 살펴보기</p>
      <a class="phero-rel-flag" href="myid.html#lineup">MyID 2.0</a>
    </div>''',
    hero_visual='<img src="assets/solutions/hero-test-2.webp" alt="" loading="eager" fetchpriority="high">',
    content=f"""
<section><div class="shell sec sec-top-lg sec-stagger">
  {sec_head('Why Now', '공공 블록체인은 기관마다<br>새로 구축해야 했습니다', '공공기관이 SaaS형 서비스를 도입하려면 CSAP 같은 엄격한 보안인증을 통과한 제품이어야 합니다. 블록체인 분야에는 CSAP 인증을 받은 SaaS가 사실상 없었습니다. 기관마다 최소 1년, 초기 구축비 수억원을 들여 직접 만들어야 했습니다.<br>그사이 정부는 2024년 블록체인 지원사업을 총 200억원·14개 규모로 늘렸습니다. 블록체인 활용 수요가 가장 큰 분야 역시 정부·공공입니다.')}
  {col_chart([
    dict(l='정부·공공', v='47.9%', w=100, hi=True),
    dict(l='출판·방송', v='36.5%', w=76),
    dict(l='금융', v='24.0%', w=50),
    dict(l='전문·과학', v='20.8%', w=43),
    dict(l='교통·물류', v='14.6%', w=30),
  ], title='블록체인 활용 분야 (공급기업 기준)', note='<strong>출처: KISA 2024년도 블록체인 산업 실태조사 결과보고서(국가승인통계 제127017호)</strong><br>복수응답 기준.')}
</div></section>
<section><div class="shell sec">
  {sec_head('Problem', '공공기관의 반복 문제, 이렇게 해결합니다')}
  {ww_compare('기관마다 새로 구축해야 합니다', '직접 구축 없이 도입합니다', [
    ('중복 인프라 투자', '기관마다 같은 블록체인, DID를 따로 구축하고 유지보수합니다.',
     '공동 인프라로 한 번에', '기관마다 따로 짓지 않고, 공동 인프라를 구독형으로 함께 씁니다.'),
    ('분절된 앱 경험', '기관, 서비스마다 앱과 인증이 흩어져 사용자 경험이 끊깁니다.',
     '하나의 인증으로 연결', '흩어진 앱, 인증을 하나로 이어, 사용자 경험이 끊기지 않습니다.'),
    ('개인정보 보관 부담', '신원 데이터를 직접 보관해야 하고, 반복 인증 부담도 큽니다.',
     '직접 보관하지 않음', '신원 데이터를 직접 쌓아두지 않아, 반복 인증 부담이 줄어듭니다.'),
    ('조달, 보안인증 문턱', 'CSAP 없는 서비스는 공공 조달 검토를 통과하기 어렵습니다.',
     '보안인증 갖추고 조달 등록', '클라우드 보안인증(CSAP)을 갖추고 조달에 등록돼 있어, 보안과 조달 요건을 바로 충족합니다.'),
  ], after_cap='MyID 2.0 도입 후')}
</div></section>
<section><div class="shell sec">
  {sec_head('Features', '직접 구축 없이 도입합니다', 'CSAP 인증을 받은 공동 인프라를 구독형으로 도입해, 예산·기간·운영 부담을 덜고 시작합니다.')}
  {cards_wrap([
    exchange_card('서비스형(SaaS) 도입', gray=True, desc='수억 원대 초기 개발비와 긴 구축 기간 없이, 구독형으로 즉시 시작합니다.'),
    exchange_card('블록체인 서비스 최초 CSAP', gray=True, desc='클라우드 보안인증을 획득하고 조달에 등록돼 있습니다.'),
    exchange_card('최대 1주일 내 적용', gray=True, desc='신청 4단계를 거쳐 최대 1주일 안에 서비스를 적용합니다.'),
    exchange_card('반복 구축 축소', gray=True, desc='기관마다 흩어진 앱·인프라를 공통 인프라로 통합합니다.'),
  ], cols=4)}
</div></section>
<section><div class="shell sec">
  {sec_head('Platform', '기본 제공 기능', '사용자는 필요한 정보만 선택 공개(Selective Disclosure)로 제출합니다. 개인 데이터는 사용자 단말과 분산 환경에 저장해 기관의 보관 부담을 줄입니다. 발급·보유·검증이 하나의 흐름으로 이어집니다.')}
  {cards_wrap([
    exchange_card('신원 DID / VC / VP', gray=True),
    exchange_card('지갑', gray=True),
    exchange_card('개인데이터저장소 PDS', gray=True),
    exchange_card('분산저장 BFS', gray=True),
  ], cols=4)}
</div></section>
<section><div class="shell sec">
  {sec_head('How to Adopt', '서비스 도입 시간 비교')}
  {adopt_compare([
    ('기존 개별 구축', '최소 1년+', ['예산 산정', '업체 선정', '견적', '계약', '구축'], False),
    ('MyID 2.0 공동 인프라', '1주일', ['가입 승인', '결제수단 등록', '회원가입·설정'], True),
  ])}
</div></section>
<!-- By the Numbers: 다크 스탯 패널 -->
<section><div class="shell stats-shell">
  <div class="stats-panel rvl" style="--rvl-y:40px; --rvl-s:.99">
    <div class="eyebrow light"><span class="dot"></span>By the Numbers</div>
    <h2 class="stats-h2" data-line-reveal style="max-width:none"><span class="rvl-line"><span>공공 서비스를 위한<br>검증된 블록체인 인프라</span></span></h2>
    <ul class="stats-grid sg-2x2">
      <li class="rvl" style="--rvl-y:20px"><div class="stat-num">최초</div><div class="stat-label">블록체인 서비스 CSAP 인증</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:90ms"><div class="stat-num"><span class="pv-val" data-val="90">0</span>%↓</div><div class="stat-label">자체 구축 대비 비용 절감 (모델 기준)</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:180ms"><div class="stat-num"><span class="pv-val" data-val="20000">0</span>건</div><div class="stat-label">월 기본 포함 건수</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:270ms"><div class="stat-num"><span class="pv-val" data-val="52">0</span>배</div><div class="stat-label">기존 개별 구축 대비 도입 속도 (1년+ → 1주일)</div></li>
    </ul>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {sec_head('FAQ', '자주 묻는 질문')}
  {faq([
    dict(q='CSAP 인증은 무엇이고 왜 중요한가요?', a='클라우드 서비스의 보안을 평가하는 국내 인증입니다. 공공기관이 민간 SaaS를 도입할 때 요구되는 기준이라, 인증이 없으면 조달 검토를 통과하기 어렵습니다.'),
    dict(q='구축형과 공공 SaaS는 무엇이 다른가요?', a='구축형은 기관이 인프라를 직접 만들어 소유·운영합니다. 공공 SaaS는 이미 만들어진 인프라를 구독형으로 이용해 별도 구축 없이 시작합니다.'),
    dict(q='공공 서비스에 DID가 왜 필요한가요?', a='반복 신원확인과 개인정보 보관 부담을 줄입니다. 사용자는 필요한 정보만 선택해 제출하고, 기관은 데이터를 직접 쌓지 않습니다.'),
  ])}
</div></section>
<section><div class="shell sec">
  {sec_head('Use Cases', '공공 블록체인 적용 사례', layout='center')}
  <div class="uc-carousel uc-tall uc-lg">
    <button class="uc-arrow uc-prev rvl rvl-op" type="button" aria-label="이전 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5L8 12l7 7"/></svg></button>
    <div class="uc-slides rvl" style="--rvl-y:40px">
      <article class="uc-slide is-active">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>부산시 · 배터리 여권 플랫폼</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">과제</span><span>배터리 제조·운행·정비·사용후 데이터가 흩어져 있고, EU DPP 규정에 맞춰 신뢰할 수 있게 연결·검증해야 합니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>K-BTF(Korea Blockchain Trust Framework) 기반으로 배터리 데이터를 단계별로 연결하고, 증명 발급·검증 절차를 하나의 방식으로 정리했습니다.</span></div></div>
      </article>
      <article class="uc-slide">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>KOMSA · 선박검사 전자증서 검증</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">과제</span><span>선박검사 전자증서는 연 약 56만 회 반복 검증되는 고빈도 공적 문서로 검증 처리 부담이 큽니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>K-BTF SaaS에 MyID 2.0의 DID/VC 발급·검증과 PDS를 결합해 검증체계를 구축했습니다 (연 약 51,066시간 절감 목표).</span></div></div>
      </article>
      <article class="uc-slide">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>경상북도 · 도민증 모이소</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">과제</span><span>도민 대상 행정서비스에서 반복 신원확인과 비대면 신청 처리가 필요합니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>DID 기반 도민증으로 발급·인증을 제공했습니다 (행정안전부 수상).</span></div></div>
      </article>
      <article class="uc-slide">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>제주도 · 제주안심코드</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">과제</span><span>대규모 방문 인증을 빠르게 처리하면서 개인정보 노출을 줄여야 합니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>QR 기반 인증으로 6만 업장·218만 이용자, 누적 9,100만 건을 처리했습니다.</span></div></div>
      </article>
    </div>
    <button class="uc-arrow uc-next rvl rvl-op" type="button" aria-label="다음 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></button>
  </div>
</div></section>
""")

# ---------------- solution-cert.html ----------------
PAGES['solution-cert.html'] = dict(
    title='디지털 증명 솔루션 | PARAMETA',
    desc='발급부터 공유, 제출처 검증까지 끝내는 블록체인 증명 솔루션. 표준 SaaS 증명은 broof형과 DID·VC 기반 자격증명 MyID형, 두 가지 형태로 제공합니다.',
    eyebrow='Solutions — 증명서',
    h1_lines=['발급만 하세요.', '검증, 재발급은 솔루션이 처리합니다'],
    lead='위촉장, 수료증, MOU, 디지털 배지, 자격·신원 증명을 두 가지 형태로 발급하고 검증하는 블록체인 기반 증명 솔루션입니다. broof형은 웹에서 바로 발급하고, MyID형은 DID·VC 기반으로 기관에 맞춰 설계합니다.',
    crumb='Solutions — 증명서',
    hero_cta='''<div class="phero-rel rvl" style="--rvl-delay:600ms">
      <p class="phero-rel-t">관련 제품 살펴보기</p>
      <a class="phero-rel-flag" href="broof.html">broof</a>
      <a class="phero-rel-flag" href="myid.html">MyID</a>
    </div>''',
    hero_visual='<img src="assets/solutions/hero-test-1.webp" alt="" loading="eager" fetchpriority="high">',
    content=f"""
<section><div class="shell sec sec-top-lg sec-stagger">
  {sec_head('Why Now', '증명서는 발급보다 발급 이후가 더 부담입니다', 'PDF나 이미지 증명서는 제출처가 원본 여부를 확인하기 어렵고, 발급기관은 발급 이후에도 검증 문의, 재발급, 서버, 보안 운영을 계속 감당해야 합니다. 증명 하나를 위해 검증 시스템을 따로 만들어 유지하는 구조입니다.<br>증명서 디지털화는 이미 흐름이 됐습니다. 정부 전자문서지갑에는 481종의 전자증명서가 올라가 있고, 정부24 회원 약 2천만 명, 연계 앱 59개가 있습니다.')}
  <div class="cert-wn-duo">
    {col_chart([
      dict(l='종이 증서', v='약 5,000원', w=100),
      dict(l='broof 디지털', v='1,100원', w=22, hi=True),
    ], title='증명서 건당 비용 비교 (당사 추산)', note='종이 증서 1건당 발급·우편·재발급·검증 인건비를 합산한 보수적 가정입니다. 연 10,000건 기준 종이 약 5,000만원, broof 약 1,100만원입니다.')}
    <div class="cert-statbox rvl">
      <div class="cert-stats">
        <div class="cert-stat"><div class="csn"><span class="pv-val" data-val="481">0</span>종</div><p>전자증명서 발급 가능 (’26.5)</p></div>
        <div class="cert-stat"><div class="csn"><span class="pv-val" data-val="2">0</span>천만</div><p>정부24 회원</p></div>
        <div class="cert-stat"><div class="csn"><span class="pv-val" data-val="59">0</span>개</div><p>연계 공공·민간 앱</p></div>
      </div>
      <p class="cert-src">출처: 행정안전부 정부 전자문서지갑(dpaper.kr, ’26.5).</p>
    </div>
  </div>
</div></section>
<section><div class="shell sec">
  {sec_head('Problem &amp; Solution', '발급기관 문제와 해결 방식', '발급기관이 반복해서 겪는 네 가지 문제를 두 가지 형태로 해결합니다. 웹에서 바로 발급하는 broof형과, DID, VC 기반으로 기관에 맞춰 설계하는 MyID형입니다.')}
  {ww_compare('발급 이후가 더 부담입니다', '발급 이후는 솔루션이 처리합니다', [
    ('발급 이후 운영 지속', '검증 문의, 재발급, 서버, 보안 운영이 발급 후에도 계속됩니다.',
     '발급 이후 운영을 솔루션이 처리', '발급만 하세요. 검증 문의, 재발급, 서버, 보안 운영을 솔루션이 전부 처리합니다.'),
    ('위변조 확인 어려움', 'PDF, 이미지 증명서는 제출처가 원본 여부를 확인하기 어렵습니다.',
     '제출처가 원본을 직접 확인', 'QR코드, 검증 링크(broof형)나 검증 가능한 디지털 자격증명(VC, MyID형)으로 제출처가 원본이 맞는지 바로 확인합니다.'),
    ('검증 시스템 구축 부담', '증명마다 검증 시스템을 따로 만들어 유지해야 합니다.',
     '검증 시스템을 직접 만들지 않음', 'broof형은 웹 서비스로, MyID형은 신원, 자격증명 인프라 연결로 별도 구축과 운영 부담을 줄입니다.'),
    ('종이 발급, 배부 비용', '인쇄, 배부, 인건비가 건마다 쌓입니다.',
     '웹 발급으로 종이 비용 제거', '인쇄, 배부, 인건비가 드는 종이 발급을 웹 발급으로 대체합니다.'),
  ])}
</div></section>
<section><div class="shell sec">
  {sec_head('Compare', '필요에 맞는 형태를 고르세요', '정해진 양식으로 빠르게 발급하면 되는 경우엔 broof형, DID·VC 기반으로 검증 이후 서비스 연동까지 필요하면 MyID형이 맞습니다.')}
  {compare_table(['', 'broof형 — 웹 발급 서비스', 'MyID형 — 신원 기반 자격증명'], [
    dict(label='구조', cells=['웹에서 바로 발급하는 서비스(SaaS)', 'DID 기반 자격증명 인프라']),
    dict(label='증명 형태', cells=['웹 증명서 (QR코드·검증 링크로 확인)', '검증 가능한 디지털 자격증명(VC)']),
    dict(label='맞춤 설계', cells=['정해진 양식 기반, 빠른 도입', '기관 요구에 맞춰 설계']),
    dict(label='검증 후 활용', cells=['제출처가 원본이 맞는지 확인', '검증 결과를 바탕으로 다음 서비스, 절차까지 연결']),
    dict(label='도입 방식', cells=['가입해 바로 발급', '프로젝트로 구축, 연동']),
    dict(label='대표 용도', cells=['위촉장, 수료증, MOU, 디지털 배지', '금융 실명확인, 신원·자격 증명, 서비스 연동']),
    dict(label='실적', cells=['2019년 출시, 정부 위원회 첫 블록체인 위촉장', '누적 이용자 약 370만, 제주안심코드 인증 9,100만 건, 금융권 DID 최초 상용화']),
  ], hl=0, tabs=True)}
</div></section>
<!-- By the Numbers: 다크 스탯 패널 -->
<section><div class="shell stats-shell">
  <div class="stats-panel rvl" style="--rvl-y:40px; --rvl-s:.99">
    <div class="eyebrow light"><span class="dot"></span>By the Numbers</div>
    <h2 class="stats-h2" data-line-reveal style="max-width:none"><span class="rvl-line"><span>현장에서 검증된<br>블록체인 증명 인프라</span></span></h2>
    <ul class="stats-grid sg-2x2">
      <li class="rvl" style="--rvl-y:20px"><div class="stat-num">2019년~</div><div class="stat-label">운영 중인 블록체인 증명 서비스</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:90ms"><div class="stat-num"><span class="pv-val" data-val="90000">0</span>건+</div><div class="stat-label">누적 블록체인 증명 발급</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:180ms"><div class="stat-num"><span class="pv-val" data-val="370">0</span>만+</div><div class="stat-label">MyID/DID 누적 이용자</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:270ms"><div class="stat-num"><span class="pv-val" data-val="9100">0</span>만 건</div><div class="stat-label">제주안심코드 누적 인증</div></li>
    </ul>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {sec_head('FAQ', '자주 묻는 질문')}
  {faq([
    dict(q='QR코드·검증 링크로 어떻게 확인하나요?', a='증명에 붙은 QR코드나 검증 링크로, 제출처가 발급기관에 묻지 않고 원본 여부를 바로 확인합니다.'),
    dict(q='발급기관은 검증 시스템을 따로 만들어야 하나요?', a='아니요. broof형은 웹 서비스로, MyID형은 인프라 연결로 발급·검증까지 처리합니다. 기관이 검증 시스템을 따로 만들 필요가 없습니다.'),
    dict(q='어떤 증명을 발급할 수 있나요?', a='broof형으로는 위촉장, 수료증, MOU, 디지털 배지를, MyID형으로는 금융 실명확인, 재직, 자격 같은 신원·자격 증명을 발급합니다.'),
    dict(q='broof형과 MyID형은 어떻게 다른가요?', a='broof형은 웹에서 위촉장, 수료증 같은 증명서를 바로 발급합니다. MyID형은 DID·VC 기반으로 기관에 맞춰 설계하고, 검증 이후 서비스 연동까지 확장합니다. 빠른 표준 발급은 broof형, 신원·자격 증명과 맞춤 설계는 MyID형입니다.'),
    dict(q='MyID형은 검증 후 무엇을 할 수 있나요?', a='검증기관이 자격증명(VC)을 신뢰하면, 그 결과로 특정 서비스나 절차를 여는 등 검증 이후 활용까지 연결할 수 있습니다.'),
  ])}
</div></section>
<section><div class="shell sec">
  {sec_head('Use Cases', '디지털 증명 적용 사례', layout='center')}
  <div class="uc-carousel uc-tall uc-lg">
    <button class="uc-arrow uc-prev rvl rvl-op" type="button" aria-label="이전 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5L8 12l7 7"/></svg></button>
    <div class="uc-slides rvl" style="--rvl-y:40px">
      <article class="uc-slide is-active">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>국가AI전략위원회 · 위촉증</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">형태</span><span>broof형</span></div><div class="uc-row"><span class="uc-flag">과제</span><span>위촉장을 종이로 발급하면 제출처가 진짜인지 확인하기 어렵고, 재발급과 보관 부담이 남습니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>블록체인 기반 위촉증으로 발급해, 받는 사람이 직접 보관, 공유하고 제출처는 QR코드로 원본을 확인하도록 했습니다.</span></div><div class="uc-row"><span class="uc-flag">결과</span><span>180여 명에게 발급한 정부 위원회 첫 블록체인 위촉장 사례입니다.</span></div></div>
      </article>
      <article class="uc-slide">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>대학·연구기관 · 수료증·학습 증명</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">형태</span><span>broof형</span></div><div class="uc-row"><span class="uc-flag">과제</span><span>제출받은 수료·이수 증명이 진짜인지 확인하려면 발급기관에 다시 문의해야 했습니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>발급한 증명에 QR코드와 검증 링크를 붙였습니다. 제출처는 문의 없이 원본과 위·변조 여부를 바로 확인합니다.</span></div><div class="uc-row"><span class="uc-flag">결과</span><span>발급기관이 검증 문의에 일일이 대응하지 않아도 됩니다.</span></div></div>
      </article>
      <article class="uc-slide">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>금융권 실명확인</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">형태</span><span>MyID형</span></div><div class="uc-row"><span class="uc-flag">과제</span><span>금융 서비스마다 실명확인을 처음부터 다시 해서, 사용자는 같은 서류를 반복 제출하고 기관은 개인정보를 반복 보관했습니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>한 번 확인한 신원을 사용자가 직접 관리하는 신원(DID)으로 보관하고, 다른 서비스에서는 필요한 정보만 골라 제출합니다.</span></div><div class="uc-row"><span class="uc-flag">결과</span><span>국내 최초로 금융권 DID 실명확인을 상용화했습니다.</span></div></div>
      </article>
      <article class="uc-slide">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>공공 대규모 인증 (제주안심코드)</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">형태</span><span>MyID형</span></div><div class="uc-row"><span class="uc-flag">과제</span><span>감염병 확산기의 대규모 방문 인증을, 개인정보 부담을 최소화하면서 빠르게 처리해야 했습니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>개인정보를 최소한만 남기는 방식으로 방문 인증을 제공했습니다.</span></div><div class="uc-row"><span class="uc-flag">결과</span><span>인증 9,100만 건을 처리했습니다.</span></div></div>
      </article>
    </div>
    <button class="uc-arrow uc-next rvl rvl-op" type="button" aria-label="다음 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></button>
  </div>
</div></section>
""")

# ---------------- solution-exchange.html ----------------
PAGES['solution-exchange.html'] = dict(
    title='디지털자산 거래 솔루션 | PARAMETA',
    desc='직접 거래소를 만들지 않아도 자사 서비스 안에 거래 기능을 넣습니다. 외부 거래소 유동성과 거래 화면을 브랜드 안에 연결하는 디지털자산 거래 솔루션.',
    eyebrow='Solutions — 디지털자산 거래',
    h1_lines=['거래소 구축 없이,', '자사 서비스에서 바로 거래를 시작합니다'],
    lead='PortX는 여러 거래소의 유동성과 거래 화면을 자사 서비스에 그대로 연결하는 솔루션입니다. 매칭엔진, 유동성, 지갑, 보안을 직접 만들지 않아도, 자사 브랜드를 단 디지털자산 거래 서비스를 빠르게 시작할 수 있습니다.',
    crumb='Solutions — 디지털자산 거래',
    hero_cta='''<div class="phero-rel rvl" style="--rvl-delay:600ms">
      <p class="phero-rel-t">관련 제품 살펴보기</p>
      <a class="phero-rel-flag" href="portx.html">PortX</a>
    </div>''',
    hero_visual='<img src="assets/solutions/hero-test-2.webp" alt="" loading="eager" fetchpriority="high">',
    content=f"""
<section><div class="shell sec sec-top-lg sec-stagger">
  {sec_head('Why Now', '사용자는 거래를 위해<br>외부 거래소로 빠져나갑니다', '국내 가상자산 이용자는 2023년 말 645만 명에서 2024년 말 970만 명으로 빠르게 늘었습니다. 이용자를 이미 확보한 서비스라도 자체 거래 기능이 없으면, 사용자는 거래를 하려고 외부 거래소로 빠져나갑니다.<br>그만큼 수수료와 사용자 관계를 외부에 내주게 됩니다. 그렇다고 직접 거래소를 만들자니 유동성·API·지갑·보안 부담이 큽니다.')}
  <div class="num-solid" style="margin-bottom:var(--space-40)">{nums([
    dict(cap='유출', n='약 20조원', sub='국내에서 해외로 빠져나간 가상자산 (’22 하반기)'),
    dict(cap='출금', n='30.6조원', sub='국내 거래소 총 외부 출금액 (같은 기간)'),
  ], cols=2)}</div>
  {col_chart([
    dict(l='2024년 말', v='970만명', w=100, hi=True),
    dict(l='2024년 6월', v='778만명', w=80),
    dict(l='2023년 말', v='645만명', w=66),
  ], title='국내 가상자산 거래가능 이용자 수', note='출처: 금융정보분석원(FIU) 가상자산사업자 실태조사. 신고 사업자 기준 거래가능 이용자 수.')}
</div></section>
<section><div class="shell sec">
  {sec_head('Problem', '거래소 사업의 고민, 이렇게 해결합니다')}
  {ww_compare('사용자가 외부 거래소로 빠져나갑니다', '자사 서비스 안에서 바로 거래를 시작합니다', [
    ('사용자 외부 이탈', '거래하려는 사용자가 외부 거래소로 빠져 수수료와 관계를 잃습니다.',
     '자사 서비스 안에서 거래', '외부 거래소의 시세와 유동성을 서비스 안에 연결해, 사용자가 자사 서비스 안에서 계속 거래하고 활동합니다.'),
    ('직접 구축 부담', '거래소 자체 구축 시 유동성, API, 지갑, 보안을 전부 직접 감당해야 합니다.',
     '개발 대신 연결', '매칭엔진, 유동성, 지갑, 보안을 직접 개발할 것 없이, 검증된 API 연결로 바로 시작합니다.'),
    ('연결 과정 이탈', 'API 키 발급과 입력 과정에서 사용자가 이탈합니다.',
     'QR 한 번으로 연결', 'API 키 입력 없이 QR 한 번으로 거래소를 연결합니다.'),
    ('체인, 거래소 파편화', '여러 체인과 거래소를 각각 연동하고 유지해야 합니다.',
     '여러 곳을 한 번에 연결', '여러 체인과 거래소를 하나로 연결해 따로 관리할 필요가 없습니다.'),
  ], after_cap='PortX 도입 후')}
</div></section>
<section><div class="shell sec">
  {sec_head('Features', '거래 경험을 서비스 안으로', '외부 거래소의 유동성과 거래 기능을 자사 브랜드 안에 연결합니다. 전체 도입이 아니라, 필요한 기능만 모듈로 골라 도입할 수 있습니다.')}
  {cards_wrap([
    exchange_card('거래소 연동', gray=True, desc='외부 중앙화·탈중앙화 거래소(CEX·DEX)의 유동성을 자사 서비스에 연결합니다.'),
    exchange_card('Smart Access · QR', gray=True, desc='API 키 입력 없이 QR 한 번으로 거래소를 연결합니다.'),
    exchange_card('Pro-Level Interface · 전문 거래 화면', gray=True, desc='트레이더용 대시보드와 TradingView를 기본 제공합니다. 여러 거래소 포트폴리오를 한눈에 관리합니다.'),
    exchange_card('Performance Analytics · 성과 분석', gray=True, desc='여러 거래소의 성과를 한 대시보드에서 보고, 손익(PnL)을 정밀하게 분석합니다.'),
    exchange_card('Non-Custodial Security · 비수탁 보안', gray=True, desc='서버에 민감 정보를 저장하지 않는 비수탁 방식입니다.'),
  ], cols=3)}
</div></section>
<!-- By the Numbers: 다크 스탯 패널 -->
<section><div class="shell stats-shell">
  <div class="stats-panel rvl" style="--rvl-y:40px; --rvl-s:.99">
    <div class="eyebrow light"><span class="dot"></span>By the Numbers</div>
    <h2 class="stats-h2" data-line-reveal style="max-width:none"><span class="rvl-line"><span>거래소 구축 없이 시작하는<br>화이트라벨 거래 인프라</span></span></h2>
    <ul class="stats-grid sg-2x2">
      <li class="rvl" style="--rvl-y:20px"><div class="stat-num"><span class="pv-val" data-val="9">0</span>+개 거래소</div><div class="stat-label">CEX + DEX 거래소 지원, 지속 확대 중</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:90ms"><div class="stat-num">QR 1회</div><div class="stat-label">API 키 없이 수 초 만에 연결</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:180ms"><div class="stat-num">78~94%</div><div class="stat-label">직접 연동 대비 기간 단축 (모델 기준)</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:270ms"><div class="stat-num">비수탁</div><div class="stat-label">자산 보관을 최소화한 구조</div></li>
    </ul>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {sec_head('FAQ', '자주 묻는 질문')}
  {faq([
    dict(q='화이트라벨 방식이 무엇인가요?', a='거래에 필요한 기능(시세 연동, 주문, 지갑, 보안)은 파라메타가 미리 만들어 두고, 고객사는 자사 로고와 디자인만 입혀 출시하는 방식입니다. 거래소를 새로 만들지 않고도 자사 브랜드의 거래 서비스를 가질 수 있습니다.'),
    dict(q='직접 거래소를 만드는 것과 무엇이 다른가요?', a='유동성, API, 지갑, 보안을 반복 개발하지 않고, 표준 거래 인프라로 빠르게 시작합니다.'),
    dict(q='자산은 어디에 보관되나요?', a='서버에 민감 정보를 저장하지 않는 비수탁(Non-Custodial) 방식이라, 자산 통제권이 고객과 사용자에게 있습니다.'),
    dict(q='PortX 전체를 도입해야 하나요?', a='아니요. 거래소 연동, QR 연결(Smart Access), 전문 거래 화면, 성과 분석을 필요한 것만 모듈로 골라 도입할 수 있습니다.'),
  ])}
</div></section>
<section><div class="shell sec">
  {sec_head('Use Cases', '화이트라벨 거래 적용 사례', layout='center')}
  <div class="uc-carousel uc-tall uc-lg">
    <button class="uc-arrow uc-prev rvl rvl-op" type="button" aria-label="이전 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5L8 12l7 7"/></svg></button>
    <div class="uc-slides rvl" style="--rvl-y:40px">
      <article class="uc-slide is-active">
        <div class="uc-thumb"><img src="assets/portx/uc-supercycl.png" alt="Supercycl"></div>
        <h3>Supercycl</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">과제</span><span>자사 서비스 안에 거래 기능을 빠르게 붙여 시장 반응을 확인해야 합니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>거래소 연동, QR 연결(Smart Access), 전문 거래 화면, 손익(PnL) 분석을 붙여 짧은 기간에 자사 브랜드 거래 서비스를 열고 초기 사용자를 확보했습니다.</span></div></div>
      </article>
      <article class="uc-slide">
        <div class="uc-thumb"><img src="assets/portx/uc-tass.png" alt="TaaS"></div>
        <h3>TaaS · 디지털자산 세금정산</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">과제</span><span>여러 거래소에 흩어진 거래 내역을 모아 예상 세금을 계산해야 합니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>PortX Smart Access로 외부 거래소 계정 연결을 간소화해, 세금 계산에 필요한 거래 정보를 서비스 안에서 바로 활용했습니다.</span></div></div>
      </article>
    </div>
    <button class="uc-arrow uc-next rvl rvl-op" type="button" aria-label="다음 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></button>
  </div>
</div></section>
""")

# ---------------- solution-data.html ----------------
PAGES['solution-data.html'] = dict(
    title='데이터주권 솔루션 | PARAMETA',
    desc='개인정보를 직접 쌓지 않고 사용자가 통제하게 만드는 데이터 인프라. PDS·BFS·선택적 공개로 서비스가 개인정보를 떠안지 않게 하는 DID 기반 신원·데이터 솔루션.',
    eyebrow='Solutions — 데이터주권',
    h1_lines=['개인정보는 쌓지 않고', '통제권은 사용자에게'],
    lead='개인정보를 다루는 서비스는 수집, 보관, 동의 관리와 유출 대응 부담이 큽니다. MyID는 사용자가 데이터를 직접 통제하고, 필요한 곳에 필요한 만큼만 제출하는 DID 기반 신원·데이터 인프라입니다. 사용자 저장소와 선택적 공개 기술로 개인정보 보관 부담을 줄입니다.',
    crumb='Solutions — 데이터주권',
    hero_cta='''<div class="phero-rel rvl" style="--rvl-delay:600ms">
      <p class="phero-rel-t">관련 제품 살펴보기</p>
      <a class="phero-rel-flag" href="myid.html">MyID</a>
    </div>''',
    hero_visual='<img src="assets/solutions/hero-test-1.webp" alt="" loading="eager" fetchpriority="high">',
    content=f"""
<section><div class="shell sec sec-top-lg sec-stagger">
  {sec_head('Why Now', '데이터는 사용자 중심으로 움직이기 시작했습니다', '마이데이터에서 시작된 ‘사용자가 자기 데이터를 옮기고 통제하는’ 흐름이 의료·통신 등 전 분야로 퍼지고 있습니다.<br>동시에 개인정보를 많이 쌓아둘수록 유출·규제·동의 관리 부담이 커집니다.')}
  <div class="cert-wn-duo wn-data">
    {col_chart([
      dict(l='2023년', v='0.8억', w=48),
      dict(l='2024년', v='1.2억', w=73),
      dict(l='2025.5', v='1.65억', w=100, hi=True),
    ], title='마이데이터 서비스 이용 (누적)', note='<strong>출처: 금융위원회 보도자료(2025.6, 마이데이터 2.0)</strong>')}
    <div class="cert-statbox statbox-2x2 rvl">
      <div class="cert-stats is-2x2">
        <div class="cert-stat"><div class="csn">약 <span class="pv-val" data-val="1.65" data-decimals="2">0.00</span>억</div><p>마이데이터 서비스 이용 (’25.5)</p></div>
        <div class="cert-stat"><div class="csn"><span class="pv-val" data-val="3.5" data-decimals="1">0.0</span>개</div><p>1인당 이용 서비스 수</p></div>
        <div class="cert-stat"><div class="csn">1조 <span class="pv-val" data-val="1430">0</span>억 건</div><p>마이데이터 누적 정보 전송 (’25.5)</p></div>
        <div class="cert-stat"><div class="csn"><span class="pv-val" data-val="30.7" data-decimals="1">0.0</span>조원</div><p>국내 데이터산업 시장 (2024)</p></div>
      </div>
      <p class="cert-src">출처: 금융위(마이데이터, ’25.6)·과기정통부 K-DATA 데이터산업현황조사(2024). 서비스 이용 수 기준이라 순수 개인 수와는 다르며, 전 분야 마이데이터는 개인정보보호위원회가 추진합니다.</p>
    </div>
  </div>
</div></section>
<section><div class="shell sec">
  {sec_head('Problem', '개인정보를 다루는 부담, 이렇게 해결합니다')}
  {ww_compare('개인정보를 직접 떠안아야 합니다', '개인정보를 떠안지 않는 구조로 바꿉니다', [
    ('보관 리스크', '개인정보를 직접 쌓아둘수록 유출 사고와 과징금, 신뢰 하락 부담이 커집니다.',
     '개인정보 유출 리스크 원천 차단', '개인정보를 기업 서버가 아닌 사용자 저장소(PDS)에 보관하여, 유출 사고와 과징금 부담을 근본적으로 해소합니다.'),
    ('반복 수집과 동의 관리', '서비스마다 같은 정보를 다시 받고 동의를 관리하는 비용이 쌓입니다.',
     '한 번 발급해 다시 사용', '한 번 검증한 정보를 여러 서비스에서 다시 사용해, 매번 새로 받지 않아도 됩니다.'),
    ('사용자 통제 요구', '전송요구권 등 사용자가 자기 데이터를 옮기거나 지워 달라는 요구에 대응해야 합니다.',
     '필요한 것만 골라 제출', '사용자가 필요한 항목만 골라 제출하고, 옮기거나 지워 달라는 요구도 바로 처리합니다.'),
    ('위·변조 검증', '받은 데이터가 진짜인지, 바뀌지 않았는지 확인해야 합니다.',
     '진짜인지 바로 확인', '데이터가 원본 그대로인지 블록체인으로 바로 확인합니다.'),
  ])}
</div></section>
<section><div class="shell sec">
  {sec_head('Features', '개인정보를 떠안지 않는 구조', '데이터를 사용자 통제 아래 두고, 서비스는 필요한 사실만 검증합니다.')}
  {cards_wrap([
    exchange_card('PDS · 개인데이터저장소', gray=True, desc='데이터를 사용자 통제 아래 두고, 기관 보관 부담을 줄입니다.'),
    exchange_card('BFS · 분산 저장', gray=True, desc='대용량 데이터를 여러 곳에 나눠 저장해, 위·변조 없이 언제든 꺼내 쓸 수 있습니다.'),
    exchange_card('선택 공개 (ZK)', gray=True, desc="생년월일 대신 '성인 여부'만 증명하는 식으로, 필요한 사실만 밝히고 나머지는 감춥니다."),
    exchange_card('MyID 지갑·API', gray=True, desc='별도 인증 앱 없이 API 연결만으로 신원·데이터를 발급·보관·제출·검증합니다.'),
  ], cols=2)}
</div></section>
<!-- By the Numbers: 다크 스탯 패널 -->
<section><div class="shell stats-shell">
  <div class="stats-panel rvl" style="--rvl-y:40px; --rvl-s:.99">
    <div class="eyebrow light"><span class="dot"></span>By the Numbers</div>
    <h2 class="stats-h2" data-line-reveal style="max-width:none"><span class="rvl-line"><span>국책 R&D로 검증된<br>분산 저장 인프라</span></span></h2>
    <ul class="stats-grid sg-2x2">
      <li class="rvl" style="--rvl-y:20px"><div class="stat-num">2021~2025</div><div class="stat-label">국책 R&D 기반 BFS (IITP·ETRI 공동)</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:90ms"><div class="stat-num"><span class="pv-val" data-val="218">0</span>만 명</div><div class="stat-label">제주안심코드 누적 이용자</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:180ms"><div class="stat-num"><span class="pv-val" data-val="9100">0</span>만 건</div><div class="stat-label">제주안심코드 누적 인증</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:270ms"><div class="stat-num">위·변조 탐지</div><div class="stat-label">검증 기록은 블록체인에, 원본은 분산 노드에</div></li>
    </ul>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {sec_head('FAQ', '자주 묻는 질문')}
  {faq([
    dict(q='PDS는 무엇인가요?', a='개인데이터저장소로, 데이터를 기관이 아니라 사용자 통제 아래 두는 저장 방식입니다.'),
    dict(q='BFS는 무엇인가요?', a='데이터를 여러 곳에 나눠 저장해, 위·변조 없이 언제든 꺼내 쓸 수 있게 하는 분산저장 기술입니다.'),
    dict(q='데이터 무결성은 어떻게 보장하나요?', a='파일 원본은 분산 노드에, 해시는 블록체인에 남깁니다. 하나라도 바뀌면 즉시 드러나는 구조입니다.'),
  ])}
</div></section>
<section><div class="shell sec">
  {sec_head('Use Cases', '데이터주권 적용 사례', layout='center')}
  <div class="uc-carousel uc-tall uc-lg">
    <button class="uc-arrow uc-prev rvl rvl-op" type="button" aria-label="이전 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5L8 12l7 7"/></svg></button>
    <div class="uc-slides rvl" style="--rvl-y:40px">
      <article class="uc-slide is-active">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>부산시 · 배터리여권 플랫폼 (DPP)</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">과제</span><span>전기차 배터리의 제조·운행·정비·중고거래·재활용 데이터가 흩어져 있고, EU 배터리 규제(DPP)에 맞춰 출처·이력·무결성을 증명해야 합니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>신원 증명(DID·VC)과 사용자 저장소(PDS)를 결합해, 배터리의 생산부터 재활용까지 전 과정 데이터를 위·변조 없이 기록·관리했습니다. MyID 2.0을 처음 적용한 공공 인프라 사례입니다.</span></div></div>
      </article>
    </div>
    <button class="uc-arrow uc-next rvl rvl-op" type="button" aria-label="다음 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></button>
  </div>
</div></section>
""")

# ---------------- solution-settlement.html ----------------
PAGES['solution-settlement.html'] = dict(
    title='결제·정산 솔루션 | PARAMETA',
    desc='결제·정산을 자동화하고 자금 흐름을 통제합니다. 은행망과 블록체인을 잇는 미들웨어 ParaSta. 기존 결제망 병행 (Dual-Rail), 폐쇄형 정산토큰에서 스테이블코인으로 2단계 전환.',
    eyebrow='Solutions — 결제·정산',
    h1_lines=['기존 결제망 그대로,', '정산, 대사는 온체인으로 자동화합니다'],
    lead='ParaSta는 은행망과 블록체인을 연결해 환전, 송금, 정산을 단일 API로 처리합니다. 기존 결제망은 유지하면서 정산, 대사, 통제 기능을 더합니다. 폐쇄형 정산토큰에서 시작해 스테이블코인까지 규제와 사업 환경에 맞춰 확장할 수 있습니다.',
    crumb='Solutions — 결제·정산',
    hero_cta='''<div class="phero-rel rvl" style="--rvl-delay:600ms">
      <p class="phero-rel-t">관련 제품 살펴보기</p>
      <a class="phero-rel-flag" href="parasta.html">ParaSta</a>
    </div>''',
    hero_visual='<img src="assets/solutions/hero-test-2.webp" alt="" loading="eager" fetchpriority="high">',
    content=f"""
<section><div class="shell sec sec-top-lg sec-stagger">
  {sec_head('Why Now', '디지털 정산이 커질수록,<br>투명성과 통제가 중요해집니다', '국내 간편지급 서비스의 일평균 이용액은 약 9,600억 원 수준입니다. 정산 규모가 커질수록 자동 대사와 자금 흐름의 투명성, 오류·부정 거래 통제가 중요해집니다. 2024년 17.6조 원 규모의 지역사랑상품권을 비롯한 공공·민간 정산도 같은 과제를 안고 있습니다.')}
  <div class="num-solid" style="margin-bottom:var(--space-40)">{nums([
    dict(cap='2024', n='약 9,594억원', sub='간편지급 일평균 이용액'),
    dict(cap='2024', n='약 9,120억원', sub='간편송금 일평균 이용액'),
  ], cols=2)}</div>
  {col_chart([
    dict(l='지류', v='1.3조원', w=11),
    dict(l='모바일', v='4.3조원', w=36),
    dict(l='카드형', v='12.0조원', w=100, hi=True),
  ], title='공공 정산 사례 — 지역사랑상품권 발행액 (2024년)', note='출처: 국회예산정책처(2025) 지역사랑상품권 발행·관리체계 평가. 2024년 총 발행 17.6조 원.')}
</div></section>
<section><div class="shell sec">
  {sec_head('Problem', '결제·정산의 반복 문제, 이렇게 해결합니다')}
  {ww_compare('정산마다 수작업 대사가 반복됩니다', '정산, 대사를 온체인으로 자동화합니다', [
    ('정산 데이터 불일치', '거래 원장과 결제사 데이터가 어긋나 수작업 대사가 필요합니다.',
     '수작업 없이 자동 대사', '확인만 하세요. 거래와 결제 데이터를 온체인 기록 기준으로 자동 대사합니다.'),
    ('환불, 취소 재정산', '환불, 취소, 차지백이 생기면 정산을 다시 맞춰야 합니다.',
     '바뀌어도 자동으로 다시 정산', '환불, 취소가 생겨도 정산을 실시간으로 다시 맞춥니다.'),
    ('다자 분배와 정산', '여러 파트너가 얽힌 분배와 정산은 대사와 통제가 복잡합니다.',
     '규칙대로 자동 분배', '여러 파트너의 몫을 정해진 규칙대로 자동 분배하고 정산합니다.'),
    ('권한, 감사 부담', '누가 무엇을 언제 바꿨는지 추적하고 감사에 대응해야 합니다.',
     '모든 변경을 자동 기록', '누가 언제 무엇을 바꿨는지 모두 기록돼, 감사 대응이 간단해집니다.'),
  ])}
</div></section>
<section><div class="shell sec">
  {sec_head('Features', '정산·대사·통제를 한 레이어로', '기존 결제 레일 위에 정산·통제 레이어만 얹어, 도입 부담을 낮추고 자금 흐름을 자동화합니다.')}
  {cards_wrap([
    exchange_card('환전·송금·정산 자동화', gray=True, desc='은행망과 블록체인을 잇는 단일 API로 환전·송금·정산 다단계를 자동 처리합니다.'),
    exchange_card('실시간 정산·자동 대사', gray=True, desc='승인·취소·환불을 실시간 반영하고, 수수료·정산 내역을 자동으로 맞춥니다.'),
    exchange_card('기존 결제망 병행 (Dual-Rail)', gray=True, desc='기존 결제 레일을 유지하면서 토큰 정산 레일을 병행해, 도입 부담을 낮춥니다.'),
    exchange_card('2단계 전환', gray=True, desc='규제 변수가 적은 폐쇄형 정산토큰으로 시작해, 필요할 때 스테이블코인으로 확장합니다.'),
    exchange_card('온체인 KYC · 통합 관리', gray=True, desc='지갑·사용자 적격성 확인과 자금 흐름 모니터링·감사 리포팅을 함께 제공합니다.'),
  ], cols=3)}
</div></section>
<!-- By the Numbers: 다크 스탯 패널 -->
<section><div class="shell stats-shell">
  <div class="stats-panel rvl" style="--rvl-y:40px; --rvl-s:.99">
    <div class="eyebrow light"><span class="dot"></span>By the Numbers</div>
    <h2 class="stats-h2" data-line-reveal style="max-width:none"><span class="rvl-line"><span>자금 흐름을 통제하는<br>정산 인프라</span></span></h2>
    <ul class="stats-grid sg-2x2">
      <li class="rvl" style="--rvl-y:20px"><div class="stat-num"><span class="pv-val" data-val="4">0</span>개 모듈</div><div class="stat-label">ParaSta 코어 + 통합 관제탑</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:90ms"><div class="stat-num"><span class="pv-val" data-val="2">0</span>단계 전환</div><div class="stat-label">폐쇄형 정산토큰에서 스테이블코인으로</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:180ms"><div class="stat-num">온체인 KYC</div><div class="stat-label">지갑·사용자 적격성 확인</div></li>
      <li class="rvl" style="--rvl-y:20px; --rvl-delay:270ms"><div class="stat-num"><span class="pv-val" data-val="100000">0</span> TPS</div><div class="stat-label">제한된 테스트 환경에서 측정한 최대 처리 성능</div></li>
    </ul>
  </div>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {sec_head('FAQ', '자주 묻는 질문')}
  {faq([
    dict(q='정산토큰과 스테이블코인은 무엇이 다른가요?', a='폐쇄형 정산토큰은 정해진 참여자 안에서만 쓰는 정산 수단이고, 스테이블코인은 더 넓은 유통을 전제합니다. 같은 인프라에서 단계적으로 전환하는 설계가 가능합니다.'),
    dict(q='지역화폐에도 적용할 수 있나요?', a='발행·정산·통제 구조를 지역화폐 정산에 적용하는 설계가 가능합니다. 실제 적용은 제도·발주 조건에 따릅니다.'),
  ])}
</div></section>
<section><div class="shell sec">
  {sec_head('Coverage', '이런 정산 영역에 적용됩니다')}
  {cards_wrap([
    exchange_card('가맹점 결제 정산', brand='var(--purple-500)'),
    exchange_card('커머스 에스크로 정산', brand='var(--purple-500)'),
    exchange_card('크로스보더 송금·정산', brand='var(--purple-500)'),
    exchange_card('지역화폐·지역상품권', brand='var(--purple-500)'),
  ], cols=4)}
</div></section>
<section><div class="shell sec">
  {sec_head('Use Cases', '결제·정산 적용 사례', layout='center')}
  <div class="uc-carousel uc-tall uc-lg">
    <button class="uc-arrow uc-prev rvl rvl-op" type="button" aria-label="이전 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5L8 12l7 7"/></svg></button>
    <div class="uc-slides rvl" style="--rvl-y:40px">
      <article class="uc-slide is-active">
        <div class="uc-thumb" aria-hidden="true"></div>
        <h3>쿠콘 · 인피닛블록 MOU</h3>
        <div class="uc-rows"><div class="uc-row"><span class="uc-flag">과제</span><span>여러 기관의 발행·정산·결제 시스템을 하나의 API 허브로 연결해야 합니다.</span></div><div class="uc-row"><span class="uc-flag">해결</span><span>스테이블코인 기반 발행·정산·결제·API 연계를 위한 업무협약을 체결했습니다.</span></div></div>
      </article>
    </div>
    <button class="uc-arrow uc-next rvl rvl-op" type="button" aria-label="다음 사례"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></button>
  </div>
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
<script src="assets/nav.js?v=33" defer></script>
<script src="assets/chatbot.js?v=4" defer></script>
<style>__CSS____EXTRA_CSS__</style>
</head>
<body class="__BODYCLASS__">
__HEADER__
<main id="main">
  <section class="phero">
    <canvas class="ev-matrix" aria-hidden="true"></canvas>
    <canvas class="orb-bg" aria-hidden="true"></canvas>
    <div class="phero-wm">PARAMETA</div>
    <div class="shell phero-inner">
      <div class="phero-text">
        __EYEBROW__
        <h1 class="phero-h1" data-line-stagger="120">__H1__</h1>
        <p class="phero-lead rvl" style="--rvl-delay:250ms">__LEAD__</p>
        __HERO_CTA__
      </div>
      <div class="phero-visual" aria-hidden="true">__HERO_VISUAL__</div>
      __HERO_FIGURE__
    </div>
    __HERO_EXTRA__
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

# ---- 공통 히어로 토큰: 3벌 ----
#  ① 제품형(product)  : 다크 + 이미지 비주얼 + View Demo/Talk to Sales   (parasta·portx·myid·broof)
#  ② 솔루션형(solution): 다크 + 이미지 비주얼 + Talk to Sales            (solution-* 6종)
#  ③ 콘텐츠형(content) : 다크 + 이미지 없음 + 텍스트 중앙정렬 + Contact Us (company·insights·careers·contact·privacy·terms)
# 페이지는 body_class / hero_cta / hero_visual 키로 오버라이드 (''로 비활성)
DEFAULT_BODY_CLASS = 'hero-dark'
HERO_CTA_PRODUCT = '''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light with-arrow arw-right hs-scale cta-talk" href="contact.html"><span class="hspring">Talk to Sales<span class="pill-badge"><svg class="icn" viewBox="0 0 24 24" fill="none"><path stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M13 6l6 6-6 6"/></svg></span></span></a>
      <a class="pill light no-arrow hs-scale cta-legacy" data-demo href="contact.html"><span class="hspring">View Demo</span></a>
      <a class="pill outline no-arrow hs-scale cta-legacy" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>'''
HERO_CTA_SOLUTION = '''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">Talk to Sales</span></a>
    </div>'''
HERO_CTA_CONTACT = '''<div class="phero-cta rvl" style="--rvl-delay:340ms">
      <a class="pill light no-arrow hs-scale" href="contact.html"><span class="hspring">Contact Us</span></a>
    </div>'''
DEFAULT_HERO_CTA = HERO_CTA_PRODUCT

# 콘텐츠형(hero-center + Contact Us) 페이지 — 이미지 비주얼 없음
CONTENT_PAGES = set()
# CTA 없는 콘텐츠형(회사/인사이트/문의/약관 등) — 중앙정렬만, CTA 없음
CONTENT_NOCTA = {'company.html', 'insights.html', 'blog.html', 'resources.html', 'contact.html', 'privacy.html', 'terms.html'}
# 라이트 히어로(hero-light) — 화이트+orb+중앙정렬. company는 Vision 편입까지 추가(body_class='company')
HERO_LIGHT = {'company.html', 'contact.html', 'insights.html', 'blog.html', 'resources.html'}
def resolve_hero(fname, p):
    """페이지별 히어로 body_class·CTA를 토큰으로 해석 (명시적 키가 있으면 우선)."""
    if fname in HERO_LIGHT:
        # 라이트 히어로: hero-dark/hero-center 대신 hero-light. company만 'company' 병용
        body = ('hero-light ' + p.get('body_class', '')).strip()
        cta = p.get('hero_cta')
        if cta is None:
            cta = '' if fname in CONTENT_NOCTA else HERO_CTA_CONTACT
        return body, cta
    body = p.get('body_class', DEFAULT_BODY_CLASS)
    if fname in CONTENT_PAGES or fname in CONTENT_NOCTA:
        body = (body + ' hero-center').strip()
    if fname.startswith('solution-'):
        body = (body + ' hero-sol').strip()  # 솔루션형 히어로 토큰(타이틀 한 사이즈 다운)
    cta = p.get('hero_cta')
    if cta is None:
        if fname.startswith('solution-'):
            cta = ''  # 솔루션은 CTA 없음
        elif fname in CONTENT_NOCTA:
            cta = ''
        elif fname in CONTENT_PAGES:
            cta = HERO_CTA_CONTACT
        else:
            cta = HERO_CTA_PRODUCT
    return body, cta

for fname, p in PAGES.items():
    h1 = ''.join(f'<span class="rvl-line"><span>{l}</span></span>' for l in p['h1_lines'])
    _body, _cta = resolve_hero(fname, p)
    # eyebrow 비면 div 자체를 생략 (dot·괄호 잔재 방지)
    _eyebrow = (f'<div class="eyebrow dark rvl rvl-op"><span class="dot"></span>{p["eyebrow"]}</div>'
                if p['eyebrow'] else '')
    out = (SHELL
        .replace('__BODYCLASS__', _body)
        .replace('__TITLE__', p['title'])
        .replace('__DESC__', p['desc'])
        .replace('__CSS__', CSS)
        .replace('__EXTRA_CSS__', EXTRA_CSS)
        .replace('__HEADER__', CHROME_HEADER)
        .replace('__EYEBROW__', _eyebrow)
        .replace('__H1__', h1)
        .replace('__LEAD__', p['lead'])
        .replace('__CRUMB__', p['crumb'])
        .replace('__HERO_CTA__', _cta)
        .replace('__HERO_VISUAL__', p.get('hero_visual', ''))
        .replace('__HERO_FIGURE__', p.get('hero_figure', ''))
        .replace('__HERO_EXTRA__', p.get('hero_extra', ''))
        .replace('__CONTENT__', p['content'])
        .replace('__FOOTER__', CHROME_FOOTER)
        .replace('__JS__', JS))
    if '/' in fname:
        # 하위 폴더 페이지: <base>로 상대경로(에셋·nav 링크·챗봇 로딩)를 루트 기준으로 해석
        depth = fname.count('/')
        out = out.replace('<head>', f'<head><base href="{"../" * depth}">', 1)
        # base 영향으로 깨지는 문서 내 앵커(#main·목차 #post-sN 등)는 자기 경로로 고정
        out = re.sub(r'href="#', f'href="{fname}#', out)
    outpath = os.path.join(ROOT, fname)
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'wrote {fname} ({len(out)} bytes)')
print('done')
