# PARAMETA 홈페이지 — 프로젝트 가이드

PARAMETA 코퍼레이트 사이트. 정적 HTML을 **빌드 스크립트로 생성**하고 GitHub Pages로 배포한다.

- **Repo**: `iconloop/parameta-home` (Public)
- **라이브**: `main` 브랜치 = GitHub Pages 배포본

---

## 빌드 워크플로 (가장 중요)

- **단일 소스**: `_build/build_subpages.py` — 모든 서브페이지 HTML을 생성한다.
- **공통 CSS 소스**: `parameta.html` — 여기의 CSS가 `EXTRA_CSS`로 각 페이지에 **인라인**된다.
- **전체 리빌드**: `python3 _build/build_subpages.py`
- **HTML은 생성물이다.** `portx.html`, `blog/*.html`, `press/*.html` 등을 직접 편집하지 말 것 — `build_subpages.py`(또는 `parameta.html`)를 고치고 **리빌드**한다.
- `build_subpages.py`의 **공통 CSS를 수정하면 전 페이지가 리빌드**되어 모든 HTML이 바뀐다. 특정 페이지만 바꾸려면 **페이지 전용 셀렉터**(예: `body.hero-dark.portx …`)를 써서 공통 CSS 오염을 피한다.

### 데이터 파이프라인 (뉴스룸 / 블로그 양산)
- `_build/extract_press.py` → `_build/data/press/*.json` → `press/*.html`
- `_build/extract_blog.py`  → `_build/data/blog/*.json`  → `blog/*.html`
- 본문 이미지: `assets/press/`, `assets/blog/`
- 대량 콘텐츠는 손으로 만들지 말고 **데이터를 돌며 템플릿으로 양산**한다.

---

## 디자인 시스템 (토큰)

새로 작성하는 CSS는 **시맨틱 토큰만** 사용한다. 생 값(raw px/rem, 생 웨이트)을 쓰지 않는다.

| 종류 | 토큰 |
|---|---|
| 본문 텍스트 | `--text-body`(18) · `--text-body-sm`(16) · `--text-cap`(14) |
| 스케일 | `--text-20` ~ `--text-72` |
| 색 | `--c-body`(ink 60%) · `--c-mut`(ink 40%) · `--accent`(#6100FF 보라) · `--ink`(#0E0C27 네이비, 히어로 배경색) |
| 웨이트 | `--w-title`(500) · `--w-strong`(600) · `--w-num`(700) |
| 행간 | `--lh-display`(.98) · `--lh-heading`(1.25) · `--lh-body`(1.6) |
| 간격 | `--space-*` (`--space-12` ~ `--space-160`, 값은 4의 배수 기반) |

> **정의 위치**: 원시 스케일(`--text-12`~`--text-96`, `--space-*`, `--leading-*`, `--para-black`/`--para-violet`)은 `parameta.html`에, 시맨틱 별칭(`--text-body`·`--text-body-sm`·`--text-cap`·`--c-body`·`--c-mut`·`--w-*`·`--lh-*`)은 `build_subpages.py`에 정의된다. `--lh-*`는 `--leading-*`의 별칭이다.

**원칙 3가지**
1. **그리드 준수** — 12칼럼 그리드에 맞춘다.
2. **토큰만 사용** — 색·크기·간격·웨이트·행간 모두 토큰.
3. **사이즈는 4의 배수 우선** (4배수 > 짝수 > 홀수). 홀수는 최후.

---

## 반응형

브레이크포인트: **PC 1024+ / 태블릿 / sm 640~767 / 모바일 ≤639**

- 태블릿·모바일 블록에서 `--text-*` / `--space-*`를 **한 단계씩 다운시프트**해 일관되게 축소한다.

---

## 브랜치 전략

| 브랜치 | 용도 |
|---|---|
| `main` | 라이브 배포 (GitHub Pages) — 직접 커밋하지 않음 |
| `feat-gnb` | 작업 브랜치. 라이브 올리기 전 여기서 작업 → `main` 머지 |
| `dev-mincircle` | 기획 관련 작업 (기획서 PR). **`main`에 흡수하지 않고** 따로 유지 |

- 작업 → `feat-gnb` → 검토 후 `main` 머지 → 라이브 반영.
- `dev` / `feat-about` 등 그 외 브랜치는 정리 대상 (사용 여부 확인 후 삭제).

---

## 주의사항

- **HTML 직접 편집 금지** — 항상 `build_subpages.py` / `parameta.html` 수정 후 리빌드.
- **`parameta.html`은 공통 CSS 소스**다. 빌드 산출물 복사(cp) 시 실수로 덮어쓰지 않도록 주의.
- **이미지는 압축 후 커밋** — 미압축 PNG(수 MB) 지양, WebP/AVIF 권장. `.git`·페이지 무게에 직접 영향.
- `.claude/`(launch.json, settings.local.json)는 **머신별 개인 설정**이라 `.gitignore` 대상 — 커밋하지 않는다.
