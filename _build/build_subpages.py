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
.phero-status{ display:flex; align-items:center; justify-content:space-between; gap:.75rem;
  border-top:1px solid rgba(var(--ink-rgb),.1); padding:1.25rem; font-size:var(--text-14); font-weight:500;
  text-transform:uppercase; letter-spacing:.025em; color:rgba(var(--ink-rgb),.6); position:relative; z-index:10 }
.phero-wm{ pointer-events:none; position:absolute; right:-1rem; bottom:-2.5rem; z-index:1;
  user-select:none; font-weight:700; line-height:1; font-size:9rem; color:rgba(var(--white-rgb),.35);
  font-family:var(--font-display); letter-spacing:-.01em; white-space:nowrap }
@media (min-width:640px){ .phero-inner{ padding:10rem 2rem 4rem } .phero-h1{ font-size:var(--text-48) }
  .phero-status{ padding-left:2rem; padding-right:2rem } }
@media (min-width:768px){ .phero-h1{ font-size:var(--text-60) } }

/* ============ SUBPAGE UTILITIES ============ */
.sec{ padding:5rem 1.25rem }
@media (min-width:640px){ .sec{ padding-left:2rem; padding-right:2rem } }
@media (min-width:1024px){ .sec{ padding-block:6rem } }
.sec-h2{ margin:1.25rem 0 3rem; max-width:24ch; font-size:var(--text-30); font-weight:600; letter-spacing:-.02em }
@media (min-width:640px){ .sec-h2{ font-size:var(--text-40) } }
.cards-3{ display:grid; grid-template-columns:1fr; gap:1.5rem }
@media (min-width:768px){ .cards-3{ grid-template-columns:repeat(2,1fr) } }
@media (min-width:1024px){ .cards-3{ grid-template-columns:repeat(3,1fr) } }
.cards-2{ display:grid; grid-template-columns:1fr; gap:1.5rem }
@media (min-width:768px){ .cards-2{ grid-template-columns:repeat(2,1fr) } }
.work-card.sm{ min-height:18rem }
.work-card.static{ cursor:default }
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
      <div class="footer-col">
        <div class="footer-col-title">Company</div>
        <ul>
          <li><a class="alink-wrap" href="company.html"><span class="alink">회사소개</span></a></li>
          <li><a class="alink-wrap" href="careers.html"><span class="alink">채용</span></a></li>
          <li><a class="alink-wrap" href="insights.html"><span class="alink">인사이트</span></a></li>
          <li><a class="alink-wrap" href="contact.html"><span class="alink">컨택</span></a></li>
        </ul>
      </div>
      <div class="footer-col">
        <div class="footer-col-title">Solutions</div>
        <ul>
          <li><a class="alink-wrap" href="parasta.html"><span class="alink">ParaSta</span></a></li>
          <li><a class="alink-wrap" href="portx.html"><span class="alink">Port X</span></a></li>
          <li><a class="alink-wrap" href="myid.html"><span class="alink">MyID</span></a></li>
        </ul>
      </div>
      <div class="footer-col">
        <div class="footer-col-title">Products</div>
        <ul>
          <li><a class="alink-wrap" href="broof.html"><span class="alink">Broof</span></a></li>
          <li><a class="alink-wrap" href="kbtf.html"><span class="alink">KBTF</span></a></li>
          <li><a class="alink-wrap" href="parameta.html#faq"><span class="alink">FAQ</span></a></li>
        </ul>
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

def dark_card(cap, title, desc, tags=None, quote=None, cite=None, sm=True):
    t = ''.join(f'<span class="tag">{x}</span>' for x in (tags or []))
    q = f'<blockquote class="work-quote">&ldquo;{quote}&rdquo;<cite>{cite}</cite></blockquote>' if quote else ''
    return (f'<article class="work-card static{" sm" if sm else ""}">'
            f'<div class="work-meta"><span>{cap}</span></div>'
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
  {eyebrow('Track Record')}
  {h2('9년간 쌓아온 신뢰 — 한국 디지털 자산 인프라의 기준')}
  {rows([
    dict(title='9년간 쌓아온 Web3 인프라 경험', desc='2016년부터 국내 1세대 Web3 인프라 기업으로서, 한국 디지털 자산 시장의 기반을 만들어왔습니다.'),
    dict(title='공공 · 금융이 인정한 기술 신뢰성', desc='정부와 금융기관이 요구하는 보안과 품질 기준을 충족하며 기술 신뢰성을 검증받아왔습니다.'),
    dict(title='지자체와 함께 검증한 공공 인프라', desc='지자체 디지털 신원·블록체인 사업을 수행하며 신뢰 기반 인프라를 구축해왔습니다.'),
    dict(title='금융 · 기업과 함께 확장한 신뢰 인프라', desc='은행, 증권사, 대기업과의 협업으로 금융권 수준의 보안성과 안정성을 검증해왔습니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Impact')}
  {h2('디지털자산 시장의 새로운 길을 만들어온 기업')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('2018', '1세대 퍼블릭 블록체인 ICON 메인넷 출시', '자체 블록체인 엔진 루프체인(loopchain)을 기반으로 ICON 메인넷을 출시해, 국내 1세대 퍼블릭 블록체인 프로젝트로 자리잡았습니다.', ['loopchain','MainNet'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('2020', 'DID 기반 제주안심코드, 누적 수십만 이용자', "DID 모바일 신원 앱 '쯩(zzeung)'과 제주안심코드 시스템을 공동 구축해, 블록체인 신원 인증으로 출입을 인증한 국내 최초 사례를 만들었습니다.", ['DID','쯩(zzeung)'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:180ms">{dark_card('2024', '국내·글로벌 거래소 API 통합 인프라 PortX', '빗썸·업비트·코인원과 Binance·Coinbase·Kraken 등 글로벌 거래소를 단일 API로 연결하는 디지털자산 통합 인프라를 구축했습니다.', ['단일 API','거래소 통합'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:270ms">{dark_card('2025', '미래에셋과 파라스타로 통합 지갑 PoC', '미래에셋과 멀티체인 통합 지갑 PoC를 진행, DID 신원인증과 온체인 KYC를 결합한 증권사 지갑 인프라를 검증했습니다.', ['ParaSta','온체인 KYC'])}</li>
  </ul>
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
    title='ParaSta · Powering the future of Web3 finance | PARAMETA',
    desc='파라스타는 기업과 기관을 위한 디지털자산 금융 솔루션입니다. 발행·보관·정산·운영·규제 대응 기능을 하나의 플랫폼으로 제공합니다.',
    eyebrow='Digital Asset Platform',
    h1_lines=['Powering the future', 'of Web3 finance'],
    lead='파라스타는 기업과 기관을 위한 디지털자산 금융 솔루션입니다. 스테이블코인부터 예금토큰, 토큰증권(STO), 실물자산(RWA)까지 다양한 디지털자산의 발행·보관·정산·운영·규제 대응 기능을 하나의 플랫폼으로 제공합니다.',
    crumb='Solutions — ParaSta',
    content=f'''
<section><div class="shell sec">
  {eyebrow('Why ParaSta')}
  {h2('실제 금융 서비스로 이어지는 인프라')}
  {rows([
    dict(title='필요한 기능만 유연하게', desc='필요한 기능만 선택해 조합하고, 기존 시스템과 쉽게 연동되어 재구축 부담 없이 확장합니다.'),
    dict(title='규제 대응이 내재된 설계', desc='AML, 트래블룰, KYC, 감사 로그 등 규제 대응 기능을 기본 제공합니다.'),
    dict(title='운영 부담은 낮게', desc='키 관리, 노드 운영, 모니터링, 장애 대응까지 ParaSta가 맡습니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Core Modules')}
  {h2('필요한 기능만 골라 조합하는 4개의 코어 모듈')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('Module 01', 'Issuance', '스테이블코인과 토큰 자산의 발행·소각·준비금 운영을 지원합니다. 토큰 생애주기 모니터링과 멀티체인 동기화까지 자동화합니다.', ['발행 · 소각 · 준비금','실시간 모니터링'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('Module 02', 'Orchestration', '은행망과 블록체인을 단일 API로 연결합니다. 입출금, 환전, 정산 흐름을 자동 동기화하고 통합 로그로 추적할 수 있습니다.', ['Fiat ↔ Crypto 단일 API','정산 자동 동기화'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:180ms">{dark_card('Module 03', 'Wallet', '규제 환경에 맞는 엔터프라이즈 지갑을 제공합니다. 입출금부터 결제, 스테이킹, 송금까지 하나의 사용자 경험으로 확장할 수 있습니다.', ['가스비 없는 UX','결제 · 스테이킹'])}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:270ms">{dark_card('Module 04', 'Onchain-KYC', '한 번의 KYC로 여러 체인과 서비스에서 활용할 수 있습니다. AML·트래블룰 대응을 자동화해 컴플라이언스 부담을 줄입니다.', ['멀티체인 신원인증','AML · 트래블룰'])}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Features')}
  {h2('모듈을 뒷받침하는 기능')}
  {rows([
    dict(title='계정 추상화 (AA)', desc='가스비나 개인키를 의식하지 않는 Web2 수준의 사용성. 키를 잃어버려도 신원 인증으로 복구합니다.'),
    dict(title='영지식증명 (ZKP)', desc='민감한 개인정보 원문 없이, 검증에 필요한 사실만 선택적으로 증명합니다.'),
    dict(title='스텔스 주소', desc='거래마다 일회용 주소를 생성해 수신자의 실제 주소 노출을 줄입니다.'),
    dict(title='단일 인터페이스 멀티체인', desc='체인을 구분할 필요 없이 자산을 관리하고, 체인 간 이동·정산은 자동 처리됩니다.'),
    dict(title='키 분할 보관 · 복구', desc='개인키를 여러 조각으로 분산 보관·복구해 분실 위험과 진입장벽을 낮춥니다.'),
  ])}
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('Use Cases')}
  {h2('도입 목적에 맞춰 활용하는 ParaSta')}
  {cards_wrap([
    dark_card('증권사', 'STO·RWA 유통 인프라가 필요할 때', '발행과 지갑 모듈을 함께 제공해, 자산의 보관·이전·유통까지 하나의 흐름으로 구현할 수 있도록 돕습니다.', ['STO','RWA']),
    dark_card('은행', '예금토큰 파일럿을 빠르게 시작할 때', '필요한 운영 계층을 모듈형으로 제공해, 파일럿부터 실제 서비스 전환까지 빠르게 확장할 수 있도록 지원합니다.', ['예금토큰','감사 로그']),
    dark_card('결제 · 핀테크', '규제 대응과 사용자 경험을 함께 잡아야 할 때', '온체인 KYC와 지갑 모듈로 필요한 정보만 확인하고, 개인정보 노출은 줄이는 설계를 돕습니다.', ['온체인 KYC','UX']),
  ], cols=3)}
</div></section>
''')

# ---------------- portx.html ----------------
PAGES['portx.html'] = dict(
    title='PortX · Built for Real-World Adoption | PARAMETA',
    desc='PortX는 디지털자산 거래 기능을 빠르게 도입할 수 있는 화이트라벨 거래소 솔루션입니다.',
    eyebrow='Exchange Solution',
    h1_lines=['Built for', 'Real-World Adoption'],
    lead='PortX는 디지털자산 거래 기능을 빠르게 도입할 수 있는 화이트라벨 거래소 솔루션입니다. 기술·보안·운영 부담은 낮추고, 사용자는 기존 서비스 안에서 그대로 거래할 수 있습니다.',
    crumb='Solutions — Port X',
    content=f'''
<section><div class="shell sec">
  {eyebrow('Why PortX')}
  {h2('지금, 자체 거래소가 필요한 이유')}
  {rows([
    dict(title='커지는 거래 시장', desc='2024년 주요 중앙화 무기한 선물 거래량 58.5조 달러. 커지는 수요를 자체 서비스 기회로 연결합니다.'),
    dict(title='외부 이탈 최소화', desc='거래 기능을 직접 제공하면 사용자 흐름을 플랫폼 안에 더 오래 유지할 수 있습니다.'),
    dict(title='거래 기반 수익 모델', desc='거래 수수료와 높아진 사용자 생애가치로 트래픽을 매출로 전환합니다.'),
    dict(title='구축 부담 없는 출시', desc='매칭 엔진, 호가창, 보안 인프라를 직접 구축할 필요 없이 빠르게 출시합니다.'),
  ])}
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
    desc='기업과 기관이 신원 인증 서비스를 안전하게 구축할 수 있도록 지원하는 블록체인 기반 W3C 표준 DID 솔루션입니다.',
    eyebrow='DID Solution',
    h1_lines=['My Data, My Choice,', 'My ID'],
    lead='기업과 기관이 신원 인증 서비스를 안전하게 구축할 수 있도록 지원하는 블록체인 기반 W3C 표준 DID 솔루션입니다. 내가 나를 증명하는 법, MyID.',
    crumb='Solutions — MyID',
    content=f"""
<section><div class="shell sec">
  <ul class="cards-3">
    <li class="rvl"><div class="light-card num-card"><span class="cap">Users</span><div class="n">약 370만</div><p>MyID · DID 누적 이용자 수</p></div></li>
    <li class="rvl" style="--rvl-delay:90ms"><div class="light-card num-card"><span class="cap">Verifications</span><div class="n">9,100만<small>+</small></div><p>제주안심코드 누적 인증 건수</p></div></li>
    <li class="rvl" style="--rvl-delay:180ms"><div class="light-card num-card"><span class="cap">Alliance</span><div class="n">86개 기관</div><p>MyID Alliance 참여 기관</p></div></li>
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
  {h2('하나의 MyID, 두 가지 도입 형태')}
  <ul class="cards-2">
    <li class="rvl" style="--rvl-y:40px">{dark_card('On-Premise', '구축형 MyID', 'MyID를 자사 인프라에 직접 구축해, 완전히 통제하고 자유롭게 커스터마이징하는 기업용 도입 방식입니다.', ['자사 인프라','커스터마이징'], sm=False)}</li>
    <li class="rvl" style="--rvl-y:40px; --rvl-delay:90ms">{dark_card('민간 SaaS', '쯩 (zzeung)', "구축 없이 구독형으로 바로 시작합니다. 시민용 디지털 지갑 앱 '쯩'으로 민간 서비스에 신원인증을 붙입니다.", ['구독형','디지털 지갑'], sm=False)}</li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
  {eyebrow('References')}
  {h2('금융·공공·기업이 검증한 적용 사례')}
  {rows([
    dict(idx='Finance', title='신한은행 · NH농협은행 금융실명인증', desc='기존 실명확인 3단계를 MyID 1단계로 통합해 비대면 실명인증을 간소화했습니다.'),
    dict(idx='Finance', title='SBI저축은행 블록체인 개인인증', desc='블록체인 기반 개인인증으로 안전하고 간편한 본인확인 절차를 제공했습니다.'),
    dict(idx='Public', title='제주특별자치도 제주안심코드', desc="DID 모바일 신원 앱 '쯩'과 함께 누적 9,100만 건의 블록체인 신원 인증을 처리했습니다."),
  ], meta=True)}
</div></section>
""")

# ---------------- kbtf.html (K-BTF — 기존 myid20 콘텐츠) ----------------
PAGES['kbtf.html'] = dict(
    title='KBTF · 공공기관 블록체인 공동 인프라 | PARAMETA',
    desc='블록체인 서비스 최초로 CSAP 인증을 받은 공공기관 전용 DID·NFT 플랫폼입니다.',
    eyebrow='Products — KBTF',
    h1_lines=['공공기관을 위한', '블록체인 SaaS,', 'K-BTF'],
    lead='블록체인 서비스 최초로 CSAP 인증을 받은 공공기관 전용 DID·NFT 플랫폼입니다. 1년 이상 걸리던 자체 구축 과정을 약 1주일로 줄이고, 도입 비용도 최대 90%까지 절감합니다.',
    crumb='Products — KBTF',
    content=f"""
<section><div class="shell sec">
  <ul class="cards-3">
    <li class="rvl"><div class="light-card num-card"><span class="cap">Security</span><div class="n">최초</div><p>블록체인 서비스 CSAP 클라우드 보안 인증 (2025)</p></div></li>
    <li class="rvl" style="--rvl-delay:90ms"><div class="light-card num-card"><span class="cap">Cost</span><div class="n">84<small>%</small></div><p>자체 구축 대비 비용 절감 · 도입 약 1주일</p></div></li>
    <li class="rvl" style="--rvl-delay:180ms"><div class="light-card num-card"><span class="cap">Procurement</span><div class="n">유일</div><p>조달청 등록 블록체인 SaaS</p></div></li>
  </ul>
</div></section>
<section><div class="shell sec" style="padding-top:0">
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
""")

# ---------------- broof.html ----------------
_broof_orgs = ['서울특별시','POSTECH','한국생산성본부','사람인','인천','한경닷컴','한빛미디어','스터디파이','아트앤가이드','심플로우','해시넷','서울시민청']
_broof_chips = ''.join(f'<span class="tag on-light">{o}</span>' for o in _broof_orgs)
PAGES['broof.html'] = dict(
    title='Broof · 블록체인 증명서 발급 | PARAMETA',
    desc='블록체인 기반 디지털 증명서 발급·검증 서비스입니다. 발급은 웹에서 간편하게, 검증은 QR 하나로.',
    eyebrow='Products — Broof',
    h1_lines=['발급은 웹에서,', '검증은 QR 하나로'],
    lead='Broof는 블록체인 기반 디지털 증명서 발급·검증 서비스입니다. 별도 시스템 구축 없이 웹에서 증명서를 발급하고, QR 하나로 원본 여부와 위·변조 여부를 즉시 확인할 수 있습니다.',
    crumb='Products — Broof',
    content=f"""
<section><div class="shell sec">
  <ul class="cards-3">
    <li class="rvl"><div class="light-card num-card"><span class="cap">First</span><div class="n">최초</div><p>정부위원회 블록체인 기반 위촉장 발급</p></div></li>
    <li class="rvl" style="--rvl-delay:90ms"><div class="light-card num-card"><span class="cap">Issued</span><div class="n">38,000<small>+</small></div><p>연간 디지털 증명서 발급</p></div></li>
    <li class="rvl" style="--rvl-delay:180ms"><div class="light-card num-card"><span class="cap">Adopted</span><div class="n">다수 기관</div><p>대학 · 공공 · 기업 누적 도입</p></div></li>
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
<script src="assets/nav.js?v=4" defer></script>
<script src="assets/chatbot.js?v=2" defer></script>
<style>__CSS____EXTRA_CSS__</style>
</head>
<body>
__HEADER__
<main id="main">
  <section class="phero">
    <div class="phero-wm">PARAMETA</div>
    <div class="shell phero-inner">
      <div class="eyebrow dark rvl rvl-op"><span class="dot"></span>__EYEBROW__</div>
      <h1 class="phero-h1" data-line-stagger="120">__H1__</h1>
      <p class="phero-lead rvl" style="--rvl-delay:250ms">__LEAD__</p>
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
        .replace('__TITLE__', p['title'])
        .replace('__DESC__', p['desc'])
        .replace('__CSS__', CSS)
        .replace('__EXTRA_CSS__', EXTRA_CSS)
        .replace('__HEADER__', CHROME_HEADER)
        .replace('__EYEBROW__', p['eyebrow'])
        .replace('__H1__', h1)
        .replace('__LEAD__', p['lead'])
        .replace('__CRUMB__', p['crumb'])
        .replace('__CONTENT__', p['content'])
        .replace('__FOOTER__', CHROME_FOOTER)
        .replace('__JS__', JS))
    with open(os.path.join(ROOT, fname), 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'wrote {fname} ({len(out)} bytes)')
print('done')
