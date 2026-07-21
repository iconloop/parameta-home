# -*- coding: utf-8 -*-
"""기획참고(blog/post-*.html)에서 블로그 아티클 콘텐츠를 추출해 _build/data/blog/*.json 생성.
마크업/스타일은 버리고 내용(제목·날짜·분류·요약·리드·본문 블록·이미지)만 가져온다.
extract_press.py 선례를 따르는 1회성 마이그레이션 도구.

블로그 특성 반영:
- 리드(post-lead)는 별도 필드(lead)로. 본문 블록은 p/figure(img)/h3/ul(list) 순서 그대로.
- 목차(On this page)는 빌드에서 h3를 자동 수집하므로 여기선 h3 텍스트만 보존.
- 꼬리 보일러플레이트(ParaSta CTA 홍보문·'참고:' 출처·'--' 구분선·중복 줄)는 제거 — 창작이 아니라 정리.
- 메타(제목·날짜·sort·cat·topics·desc)는 insights_index.json에서.

사용: python3 _build/extract_blog.py [기획참고폴더]
"""
import json, os, re, sys, glob, shutil

SRC = sys.argv[1] if len(sys.argv) > 1 else '/Users/sang/Desktop/Claude/parameta-pr2-기획참고'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_build', 'data', 'blog')
ASSET_OUT = os.path.join(ROOT, 'assets', 'blog')

idx = json.load(open(os.path.join(SRC, '_migrate', 'insights_index.json'), encoding='utf-8'))
BLOG_IDX = {b['slug']: b for b in idx['blog']}

os.makedirs(OUT, exist_ok=True)
os.makedirs(ASSET_OUT, exist_ok=True)

STRIP = lambda x: re.sub(r'<[^>]+>', '', x).strip()
TAG = re.compile(r'<(p|figure|h3|ul)\b[^>]*>.*?</\1>', re.S)


def copy_img(slug, rel):
    rel = rel.lstrip('./')                      # ../assets/img/posts/<slug>/fig-1.png → assets/img/posts/...
    src = os.path.join(SRC, rel)
    name = os.path.basename(rel)
    dst_dir = os.path.join(ASSET_OUT, slug)
    os.makedirs(dst_dir, exist_ok=True)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(dst_dir, name))
    else:
        print('  !! 이미지 없음:', src)
    return f'assets/blog/{slug}/{name}'


def parse(slug):
    """(lead, blocks, hero_img) 반환. 꼬리 보일러플레이트 컷 + 연속 중복 줄 제거."""
    h = open(os.path.join(SRC, 'blog', slug + '.html'), encoding='utf-8').read()
    i = h.find('<article class="post-body"')
    j = h.find('</article>', i)
    art = h[i:j] if i >= 0 else ''
    lead, blocks, hero = '', [], None
    prev_p = None
    for m in TAG.finditer(art):
        tag, html = m.group(1), m.group(0)
        if tag == 'p':
            if 'post-lead' in html:
                lead = STRIP(html)
                continue
            inner = re.sub(r'^<p[^>]*>|</p>$', '', html, flags=re.S).strip()
            if not inner:
                continue
            txt = STRIP(inner)
            if txt.strip() in ('--', '—', '––') or txt.startswith('참고:'):
                break                          # ParaSta CTA·출처 등 꼬리 보일러플레이트 이후 중단
            if txt == prev_p:                   # 연속 중복 줄 제거
                continue
            prev_p = txt
            blocks.append({'t': 'p', 'html': inner})
        elif tag == 'figure':
            im = re.search(r'src="([^"]+)"', html)
            if im:
                path = copy_img(slug, im.group(1))
                blocks.append({'t': 'img', 'src': path})
                if hero is None:
                    hero = path
                prev_p = None
        elif tag == 'h3':
            blocks.append({'t': 'h3', 'html': STRIP(html)})
            prev_p = None
        elif tag == 'ul':
            items = [STRIP(x) for x in re.findall(r'<li[^>]*>(.*?)</li>', html, re.S)]
            items = [x for x in items if x]
            if items:
                blocks.append({'t': 'list', 'items': items})
                prev_p = None
    return lead, blocks, hero


count, missing = 0, 0
for f in sorted(glob.glob(os.path.join(SRC, 'blog', 'post-*.html'))):
    slug = os.path.splitext(os.path.basename(f))[0]
    meta = BLOG_IDX.get(slug)
    if not meta:
        print('!! index에 없음:', slug)
        missing += 1
        continue
    lead, blocks, hero = parse(slug)
    chars = len(lead) + sum(len(b.get('html', '')) + sum(len(i) for i in b.get('items', [])) for b in blocks)
    read_min = max(1, round(chars / 500))       # 한글 대략 500자/분
    data = dict(slug=slug, title=meta['title'], date=meta['date'], sort=meta['sort'],
                cat=meta['cat'], topics=meta.get('topics', []), desc=meta['desc'],
                lead=lead, hero_img=hero, read_min=read_min, blocks=blocks)
    json.dump(data, open(os.path.join(OUT, slug + '.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    count += 1

print(f'extracted: {count}  (index 누락 {missing})')
