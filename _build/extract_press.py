# -*- coding: utf-8 -*-
"""기획서(press/post-pr-NNN.html)에서 보도자료 콘텐츠를 추출해 _build/data/press/*.json 생성.
마크업은 버리고 내용(제목·날짜·요약·본문 블록·이미지 경로)만 가져온다. 1회성 마이그레이션 도구.
사용: python3 _build/extract_press.py <기획참고 폴더>
"""
import json, os, re, sys, glob, shutil

SRC = sys.argv[1] if len(sys.argv) > 1 else '/Users/sang/Desktop/Claude/parameta-pr2-기획참고'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_build', 'data', 'press')
ASSET_OUT = os.path.join(ROOT, 'assets', 'press')

idx = json.load(open(os.path.join(SRC, '_migrate', 'insights_index.json'), encoding='utf-8'))
press_idx = {p['slug']: p for p in idx['press']}

os.makedirs(OUT, exist_ok=True)
os.makedirs(ASSET_OUT, exist_ok=True)

TAG_RE = re.compile(r'<(p|figure|h3|ul)\b[^>]*>.*?</\1>', re.S)
STRIP = lambda x: re.sub(r'<[^>]+>', '', x).strip()

def blocks_of(article):
    out = []
    for m in TAG_RE.finditer(article):
        tag = m.group(1)
        html = m.group(0)
        if tag == 'p':
            if 'post-lead' in html:
                continue  # 제목 반복 — 템플릿이 자동 생성
            inner = re.sub(r'^<p[^>]*>|</p>$', '', html, flags=re.S).strip()
            if inner:
                out.append({'t': 'p', 'html': inner})
        elif tag == 'figure':
            im = re.search(r'src="([^"]+)"', html)
            if im:
                out.append({'t': 'img', 'src': im.group(1)})
        elif tag == 'h3':
            inner = re.sub(r'^<h3[^>]*>|</h3>$', '', html, flags=re.S).strip()
            out.append({'t': 'h3', 'html': STRIP(inner)})
        elif tag == 'ul':
            items = [STRIP(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', html, re.S)]
            out.append({'t': 'list', 'items': [x for x in items if x]})
    return out

def split_summary(blocks):
    """post-lead 이후 첫 이미지/본문 시작('['로 여는 문단) 전의 짧은 문단·리스트 = 요약.
    (일부 원문은 요약을 ul 리스트로 마크업 — 마크업 무관하게 내용만 요약으로 흡수)"""
    summary, rest = [], []
    in_summary = True
    for b in blocks:
        if in_summary and b['t'] == 'p':
            text = STRIP(b['html'])
            if text.startswith('[') or len(text) > 120:
                in_summary = False
                rest.append(b)
            else:
                summary.append(text)
        elif in_summary and b['t'] == 'list':
            summary.extend(b['items'])
        else:
            in_summary = False
            rest.append(b)
    return summary, rest

count = 0
for f in sorted(glob.glob(os.path.join(SRC, 'press', 'post-pr-*.html'))):
    slug = os.path.splitext(os.path.basename(f))[0]
    meta = press_idx.get(slug)
    if not meta:
        print('!! index에 없음:', slug); continue
    h = open(f, encoding='utf-8').read()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
    title = STRIP(m.group(1)) if m else meta['title']
    i = h.find('<article class="post-body"')
    j = h.find('</article>', i)
    blocks = blocks_of(h[i:j])
    summary, body = split_summary(blocks)

    # 이미지 복사 + 경로 재작성 (루트 기준 — press/ 하위에선 <base href="../">로 해석)
    hero_img = None
    for b in body:
        if b['t'] == 'img':
            rel = b['src'].lstrip('./')           # assets/img/posts/post-pr-239/fig-1.png
            src_path = os.path.join(SRC, rel.replace('assets/img/posts/', 'assets/img/posts/'))
            name = os.path.basename(rel)
            dst_dir = os.path.join(ASSET_OUT, slug)
            os.makedirs(dst_dir, exist_ok=True)
            if os.path.exists(src_path):
                shutil.copy2(src_path, os.path.join(dst_dir, name))
            else:
                print('!! 이미지 없음:', src_path)
            b['src'] = f'assets/press/{slug}/{name}'
            if hero_img is None:
                hero_img = b['src']

    data = dict(slug=slug, title=title, date=meta['date'], sort=meta['sort'],
                summary=summary, blocks=body, hero_img=hero_img)
    json.dump(data, open(os.path.join(OUT, slug + '.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    count += 1
print('extracted:', count)
