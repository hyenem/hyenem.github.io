#!/usr/bin/env python3
"""Generate Figma-importable SVG slides from compare-slides.html content."""
from xml.sax.saxutils import escape as esc

W, H = 1920, 1080

C = {
    'bg': '#ffffff', 'soft': '#f9fafb', 'elev': '#f3f4f6',
    'border': '#e5e7eb', 'border_strong': '#d1d5db',
    'text': '#111827', 'dim': '#4b5563', 'muted': '#6b7280',
    'accent': '#0d9488', 'accent_dim': '#14b8a6',
    'accent_soft': '#ccfbf1', 'accent_bg': '#f0fdfa',
    'warn': '#b45309', 'warn_soft': '#fef3c7', 'warn_border': '#fcd34d', 'warn_text': '#78350f',
    'danger': '#b91c1c', 'danger_soft': '#fee2e2', 'danger_border': '#fca5a5', 'danger_text': '#7f1d1d',
    'galaxy': '#1428a0', 'galaxy_soft': '#e0e7ff', 'galaxy_bg': '#eef2ff',
}

FONT = "Pretendard, 'Apple SD Gothic Neo', 'Malgun Gothic', system-ui, -apple-system, sans-serif"
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"


# ===== Helpers =====
def svg_open():
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">\n'

def svg_close():
    return '</svg>\n'

def bg():
    return f'  <rect width="{W}" height="{H}" fill="{C["bg"]}"/>\n'

def text(x, y, s, size=13, color='text', weight=400, italic=False, mono=False, anchor='start', spacing=None):
    fam = f' font-family="{MONO}"' if mono else ''
    fw = f' font-weight="{weight}"' if weight != 400 else ''
    fi = ' font-style="italic"' if italic else ''
    fc = C.get(color, color)
    a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
    sp = f' letter-spacing="{spacing}"' if spacing else ''
    return f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fc}"{fw}{fi}{fam}{a}{sp}>{esc(s)}</text>\n'

def rect(x, y, w, h, fill='bg', stroke=None, sw=1, rx=0):
    fc = C.get(fill, fill)
    out = f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fc}"'
    if stroke:
        sc = C.get(stroke, stroke)
        out += f' stroke="{sc}" stroke-width="{sw}"'
    return out + '/>\n'

def line(x1, y1, x2, y2, stroke='border', sw=1, dash=None):
    sc = C.get(stroke, stroke)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{sc}" stroke-width="{sw}"{d}/>\n'

def slide_header(num, title, tag, tag_color='accent'):
    """Top meta bar: 01/04, title, tag chip."""
    out = ''
    # num label
    out += text(50, 60, num, size=12, color='muted', mono=True, spacing='0.08em')
    # title
    out += text(140, 62, title, size=22, color='text', weight=700)
    # tag chip
    tag_bg = C.get(f'{tag_color}_soft', C['accent_soft'])
    tag_fg = C.get(tag_color, C['accent'])
    chip_w = 14 + len(tag) * 7
    chip_x = W - 50 - chip_w
    out += f'  <rect x="{chip_x}" y="46" width="{chip_w}" height="24" rx="4" fill="{tag_bg}"/>\n'
    out += f'  <text x="{chip_x + chip_w/2}" y="62" font-size="11" font-weight="700" fill="{tag_fg}" text-anchor="middle" font-family="{MONO}" letter-spacing="0.08em">{esc(tag.upper())}</text>\n'
    # separator
    out += line(50, 88, W - 50, 88, stroke='border')
    return out

def lead(lines, y_start=110):
    """Multi-line lead text below header."""
    out = ''
    y = y_start
    for ln in lines:
        out += text(50, y, ln, size=13.5, color='dim')
        y += 20
    return out


# ============================================================
# SLIDE 01 — Market landscape (7 product cards + common flaw)
# ============================================================
def card(x, y, w, h, brand, name, tag, bullets, meta, is_you=False, brand_color=None):
    """Render a product card."""
    bg_color = 'accent_bg' if is_you else 'soft'
    border_color = 'accent_dim' if is_you else 'border'
    brand_c = brand_color or ('accent' if is_you else 'muted')
    name_c = 'accent' if is_you else 'text'

    out = rect(x, y, w, h, fill=bg_color, stroke=border_color, sw=1, rx=8)
    cy = y + 22
    out += text(x + 14, cy, brand.upper(), size=10, color=brand_c, mono=True, spacing='0.05em', weight=600)
    cy += 24
    out += text(x + 14, cy, name, size=15, color=name_c, weight=700)
    cy += 19
    out += text(x + 14, cy, tag, size=11, color='dim', italic=True)
    cy += 12
    out += line(x + 14, cy, x + w - 14, cy, stroke='border', dash='4 3')
    cy += 20

    # bullets
    for kind, txt in bullets:
        sym = '+' if kind == 'pro' else '−'
        sym_color = 'accent' if kind == 'pro' else 'danger'
        out += text(x + 16, cy, sym, size=12, color=sym_color, weight=700)
        out += text(x + 30, cy, txt, size=11, color='text')
        cy += 21

    # meta separator and meta
    meta_y = y + h - 14
    out += line(x + 14, meta_y - 14, x + w - 14, meta_y - 14, stroke='border', dash='4 3')
    out += text(x + 14, meta_y, meta, size=10, color='muted', mono=True)
    return out


def slide_01():
    out = svg_open() + bg()
    out += slide_header('01 / 04', '시장 대표 6종 + BudsAI — 강점/한계/스펙 한 장', 'Market')
    out += lead([
        '프리미엄 TWS · 자사 후속 · 음질 정통파 · ChatGPT 단축키 · 통역 특화 · 시각 컨텍스트 AI —',
        '7개 제품을 강점(+) / 한계(−) / 스펙 한 줄로 압축.',
    ], y_start=112)

    cards_data = [
        # (brand, name, tag, bullets, meta, is_you)
        ('Samsung · 본 제안', 'BudsAI', '직전 사운드 + 음성 질의 결합 AI 이어버드', [
            ('pro', '출력 PCM 30초 링버퍼 (~150KB) — 유일 차별점'),
            ('pro', '표준 BT PAN, 앱 0, 호스트 무관'),
            ('pro', '버즈 종단 mTLS (SE 인증서)'),
            ('con', '의도·세션 연속은 Gemini Live가 우위'),
            ('con', '신규 카테고리 — 학습 필요'),
        ], '~3s 응답 · Opus · Galaxy 시너지 풀 지원', True),

        ('Samsung · 자사 (2026-03 출시)', 'Galaxy Buds4 Pro', 'Bixby + Galaxy AI Interpreter 연장', [
            ('pro', '실시간 Interpreter(통역) 강력'),
            ('pro', 'Samsung Sound by AKG 튜닝'),
            ('pro', 'SSC 코덱 · One UI 통합'),
            ('con', 'ANC는 Bose/Sony 대비 중급(평가)'),
            ('con', 'Galaxy 폰 페어링 시에만 풀 기능'),
        ], '~2-3s 응답(추정) · Wearable 앱 필수', False),

        ('Apple', 'AirPods Pro 2', 'Siri + Apple Intelligence + Conv. Awareness', [
            ('pro', 'H2 칩 ANC · Hearing Aid · Adaptive'),
            ('pro', 'iPhone↔Mac 핸드오프 (실사용 미스 있음)'),
            ('pro', 'Live Translation (Apple Intelligence)'),
            ('con', 'iPhone 15 Pro+ 강제 · Mac 단독 불가'),
            ('con', '듣던 사운드 자체는 컨텍스트 미사용'),
        ], '~2-3s 응답(추정) · iCloud 계정 sync · AAC', False),

        ('Sony', 'WF-1000XM5', '음질·ANC 정통파', [
            ('pro', 'LDAC · 360 Reality Audio'),
            ('pro', 'ANC 클래스 최고 수준(Bose·Apple과 경합)'),
            ('pro', 'Speak-to-Chat (말하면 일시정지)'),
            ('con', 'AI 자체 기능 없음 — 폰 비서 패스스루'),
            ('con', '통역·번역·식별 모두 외부 의존'),
        ], '자체 AI 없음 · Headphones Connect · LDAC', False),

        ('Nothing', 'Nothing Ear (2024)', 'ChatGPT 직접 호출 (Nothing Phone 한정)', [
            ('pro', 'Pinch 제스처 → ChatGPT'),
            ('pro', 'LDAC · 45dB ANC · 합리적 가격'),
            ('pro', '투명 디자인 차별화'),
            ('con', '타사 폰에서 ChatGPT 단축키 사망'),
            ('con', '듣던 오디오는 컨텍스트 미사용'),
        ], '~3-5s 응답(추정) · Nothing X 앱 필수', False),

        ('Timekettle', 'WT2 Edge / M3', '실시간 양방향 통역 특화', [
            ('pro', '40+ 언어 동시 통역'),
            ('pro', '카드 기반 화자 분리 UX'),
            ('pro', 'M3는 30dB ANC + 음악·통화 패스스루'),
            ('con', 'AI 의도는 번역만 (음악ID/요약 X)'),
            ('con', '전용 앱 + 클라우드 STT/MT 필수'),
        ], '~2-4s 응답(추정) · M3 30dB ANC · WT2는 ANC X', False),

        ('Meta (참고)', 'Ray-Ban Meta', '스마트글래스 · "Hey Meta" + 카메라', [
            ('pro', '시각 컨텍스트 강함 (12MP 카메라)'),
            ('pro', 'Meta AI Live + Shazam v11 통합'),
            ('pro', '자체 폼팩터 · 오픈 이어 스피커'),
            ('con', '오디오 컨텍스트 약함 (환경 마이크만)'),
            ('con', 'Meta AI 앱 + 폰 종속'),
        ], '~2-3s 응답(추정) · 이어폰 아님 · 보완재', False),
    ]

    # Grid: 4 cols × 2 rows
    grid_x = 50
    grid_y = 170
    card_w = 440
    card_h = 290
    gap = 20

    for i, (brand, name, tag, bullets, meta, is_you) in enumerate(cards_data):
        col = i % 4
        row = i // 4
        x = grid_x + col * (card_w + gap)
        y = grid_y + row * (card_h + gap)
        out += card(x, y, card_w, card_h, brand, name, tag, bullets, meta, is_you=is_you)

    # Common flaw box at bottom
    cf_y = grid_y + 2 * card_h + gap + 14
    cf_h = 140
    out += rect(50, cf_y, W - 100, cf_h, fill='danger_soft', stroke='danger_border', sw=1, rx=8)
    out += rect(50, cf_y, 4, cf_h, fill='danger', rx=2)
    out += text(70, cf_y + 32, '공통 한계 (BudsAI 제외 6종 전체)', size=15, color='danger', weight=700)
    cy = cf_y + 62
    cf_lines = [
        '모두 "사용자가 질문하는 순간부터의 마이크 입력"만 AI에 보낸다.',
        '듣고 있던 출력 사운드 자체를 컨텍스트로 동봉하는 제품은 시장에 단 하나도 존재하지 않는다.',
        '"방금 그 노래/대사/단어"를 묻기 위해 사용자가 다시 마이크에 대고 캡처하거나 별도 앱(Shazam 등)을 켜야 한다.',
    ]
    for ln in cf_lines:
        out += text(70, cy, ln, size=13, color='danger_text')
        cy += 22

    return out + svg_close()


# ============================================================
# SLIDE 02 — Matrix (10 axes × 7 products)
# ============================================================
def slide_02():
    out = svg_open() + bg()
    out += slide_header('02 / 04', '10개 축 × 7개 제품 비교 매트릭스', 'Matrix')
    out += lead([
        'LLM 시대에 누구나 가능한 "의도 라우팅 자유도", "세션 연속 대화" 같은 축은 차별점이 아니므로 제외.',
        '진짜로 BudsAI만 ●인 축은 4개 — 컨텍스트·호스트 무관·앱 0·E2E 보안. (검증 출처: compare.html#refs)',
    ], y_start=112)

    # Matrix
    cols = ['비교 축', 'BudsAI', 'Buds4 Pro', 'AirPods Pro 2', 'Sony XM5', 'Nothing Ear', 'Timekettle', 'Ray-Ban Meta']
    rows = [
        ('듣던 사운드를 AI 컨텍스트', ['● 30s 링버퍼', '—', '—', '—', '—', '—', '△ 시각만']),
        ('호스트 무관 (노트북·TV·차량)', ['● BT PAN 표준', '— Galaxy 필수', '— iPhone 종속', '△ 음악만', '— Nothing Phone', '—', '—']),
        ('앱 설치 불필요 (Zero-Install)', ['● OS 빌트인 BT', '—', '—', '—', '—', '—', '—']),
        ('버즈 종단 E2E (mTLS)', ['● SE 인증서', '△', '△ iCloud', '—', '—', '— 앱 종단', '—']),
        ('호스트 페이로드 접근 차단', ['● Dumb Pipe', '—', '— iPhone 처리', '—', '—', '—', '—']),
        ('실시간 통역', ['● 8 의도 중', '● Interpreter', '△ Live Trans', '—', '—', '● 40+ 언어', '●']),
        ('음악 식별 (Shazam류)', ['● 동일 입력', '△ Bixby(폰)', '● Siri+Shazam', '—', '—', '—', '● Shazam v11']),
        ('고음질 코덱', ['● A2DP 독립', '● SSC', '● AAC', '● LDAC', '● LDAC', '—', '△']),
        ('ANC', ['△ HW 의존', '●', '●', '● 최고', '●', '△ M3 30dB', '— 오픈형']),
        ('종단간 응답 지연', ['~3s', '~2-3s', '~2-3s', 'N/A', '~3-5s', '~2-4s', '~2-3s']),
    ]

    tx0 = 50
    ty0 = 180
    col_widths = [240] + [217] * 7  # total 240 + 7*217 = 1759. usable=1820, leftover small
    # Adjust to fit: 1820 = 240 + 7*x → x=225.7
    col_widths = [240] + [226] * 7  # total = 240 + 1582 = 1822, close
    total_w = sum(col_widths)
    row_h = 56
    head_h = 44

    # Header row
    cx = tx0
    out += rect(tx0, ty0, total_w, head_h, fill='elev', stroke='border', sw=1)
    for i, col in enumerate(cols):
        is_self = (i == 1)
        if is_self:
            out += rect(cx, ty0, col_widths[i], head_h, fill='accent_soft')
        # vertical separator at right edge (except last)
        if i < len(cols):
            out += line(cx + col_widths[i], ty0, cx + col_widths[i], ty0 + head_h, stroke='border')
        # text
        if i == 0:
            out += text(cx + 12, ty0 + 28, col, size=12, color='text', weight=700)
        else:
            out += text(cx + col_widths[i]/2, ty0 + 28, col, size=11, color='accent' if is_self else 'text', weight=700, anchor='middle')
        cx += col_widths[i]

    # Data rows
    ry = ty0 + head_h
    for ri, (label, vals) in enumerate(rows):
        out += rect(tx0, ry, total_w, row_h, fill='bg', stroke='border', sw=1)
        # Label cell bg
        out += rect(tx0, ry, col_widths[0], row_h, fill='soft')
        out += text(tx0 + 12, ry + 32, label, size=12, color='text', weight=600)
        # Self col bg
        cx = tx0 + col_widths[0]
        out += rect(cx, ry, col_widths[1], row_h, fill='accent_bg')

        cx = tx0
        for i, col_w in enumerate(col_widths):
            if i > 0:
                v = vals[i - 1]
                # parse v: starts with ●, △, —, or just text
                parts = v.split(' ', 1)
                sym = parts[0]
                note = parts[1] if len(parts) > 1 else ''
                # color by sym
                if sym == '●':
                    sym_color = 'accent'
                    sym_w = 700
                    sym_size = 16
                elif sym == '△':
                    sym_color = 'warn'
                    sym_w = 700
                    sym_size = 14
                elif sym == '—':
                    sym_color = 'muted'
                    sym_w = 400
                    sym_size = 14
                else:
                    # response time like "~3s"
                    sym_color = 'accent' if 'N/A' not in v else 'muted'
                    sym_w = 700
                    sym_size = 13
                    sym = v
                    note = ''

                # center sym
                out += text(cx + col_w/2, ry + 26, sym, size=sym_size, color=sym_color, weight=sym_w, anchor='middle')
                if note:
                    out += text(cx + col_w/2, ry + 44, note, size=10, color='muted', anchor='middle')
                # vertical separator right
                if i < len(col_widths):
                    out += line(cx + col_w, ry, cx + col_w, ry + row_h, stroke='border')
            cx += col_w
        ry += row_h

    # Outer border
    table_h = head_h + len(rows) * row_h
    out += rect(tx0, ty0, total_w, table_h, fill='none', stroke='border', sw=1)

    # Legend
    leg_y = ty0 + table_h + 16
    out += text(50, leg_y, '● 지원/강점', size=12, color='accent', weight=700)
    out += text(180, leg_y, '△ 부분/제한적', size=12, color='warn', weight=700)
    out += text(320, leg_y, '— 미지원', size=12, color='muted')
    out += text(W - 50, leg_y, '※ ANC/코덱 BudsAI는 Buds Pro 차세대 HW 기준 · 응답 지연은 음성 호출 → TTS 시작 추정', size=11, color='muted', anchor='end')

    return out + svg_close()


# ============================================================
# SLIDE 03 — Differentiators (4 rows + honest box)
# ============================================================
def slide_03():
    out = svg_open() + bg()
    out += slide_header('03 / 04', '진짜 단독 차별점 4개 + 솔직히 동등하거나 약한 부분', 'Differentiators')
    out += lead([
        'LLM 시대엔 "의도 라우팅"·"세션 연속 대화"는 누구나 한다. 정직하게 BudsAI만 단독으로 가지는 본질적 차별점 4개(기술 3 + 생태계 1)만 남기고,',
        '동등하거나 약한 부분은 따로 인정한다.',
    ], y_start=112)

    # Table
    headers = ['#', '차별 축 (What)', '어떻게 (How)', '구현 증거 (Evidence)', '타사가 왜 못 하나 (Why none)']
    col_widths = [40, 260, 560, 320, 640]  # total 1820
    total_w = sum(col_widths)

    rows = [
        ('01', '"이미 들은 사운드"가 컨텍스트',
         '버즈가 출력 PCM 마지막 30초를 Opus로 압축해 링버퍼에 항상 보관. 질문 발생 시 자동 동봉. 사용자가 "방금 그거"라고만 해도 시스템이 이미 무엇을 들었는지 알고 있음.',
         '30s · ~150KB · Opus 16kbps · Track A 패킷',
         '모든 경쟁사는 사용자 발화 시점부터의 마이크 입력만 캡처. "방금 그 노래"를 다시 캡처하거나 Shazam 같은 앱을 별도 호출해야 함. 이 한 가지가 BudsAI의 진짜 해자.', None),
        ('02', '호스트 무관 · 앱 설치 0',
         '표준 BT PAN(BNEP) 프로파일만 사용. OS 빌트인 "Bluetooth 테더링" 토글 한 번이면 노트북·MP3·TV·차량·eSIM 동글에서 동일 동작. 자사 폰 없어도 모든 핵심 기능 그대로.',
         'BNEP · IETF RFC 3220 · OS 빌트인',
         'AirPods=iPhone, Buds4 Pro=Galaxy, Nothing=Nothing Phone에 강하게 종속 — 기술 문제가 아니라 락인 비즈니스 모델. 시장 6종 중 아무도 의도적으로 풀지 않음.', None),
        ('03', '버즈 종단 mTLS · Dumb Pipe',
         '디바이스 인증서를 버즈의 Secure Element에 보관. 버즈가 직접 서버와 mTLS 핸드셰이크. 호스트는 IP 패킷만 라우팅하므로 평문 페이로드를 못 봄.',
         'SE + X.509 · TLS 1.3 · Knox Vault 호환',
         '타사는 모두 폰이 평문 페이로드 처리 → 분실 폰·공유 노트북·렌터카 사용 시 음성 노출 위험. 호스트 무관(#02)을 추구하지 않으면 mTLS 종단을 버즈에 둘 동기 자체가 없음.', None),
        ('04', 'Galaxy 생태계 자동 통합',
         '버즈 응답을 Galaxy 컴패니언 앱이 받아 Spotify·Samsung Notes·Calendar·Internet·Watch·Tab·Auto·DeX·SmartThings로 자동 라우팅. Bixby Routines가 위치·시간 기반으로 BudsAI 모드 자체를 자동 트리거.',
         '컴패니언 앱 · Bixby Routines · SmartThings · One UI Auto · DeX · Knox Vault',
         '자사 OS·앱·차량·웨어러블·태블릿·DeX·SE 보안 모듈을 모두 가진 회사는 삼성과 애플뿐. 그런데 애플은 호스트 무관 아키텍처(#02)를 만들 동기 자체가 없음. 두 조건을 동시에 만족하는 회사는 사실상 삼성 하나.', 'galaxy'),
    ]

    tx0 = 50
    ty0 = 175
    head_h = 38

    # Header
    out += rect(tx0, ty0, total_w, head_h, fill='elev', stroke='border', sw=1)
    cx = tx0
    for i, h in enumerate(headers):
        if i > 0:
            out += line(cx, ty0, cx, ty0 + head_h, stroke='border')
        align = 'middle' if i == 0 else 'start'
        x_text = cx + col_widths[i] / 2 if i == 0 else cx + 12
        out += text(x_text, ty0 + 24, h.upper(), size=11, color='text', weight=700, spacing='0.03em', anchor=align)
        cx += col_widths[i]

    # Rows
    ry = ty0 + head_h
    row_h = 130
    for (n, what, how, evidence, none, accent_tag) in rows:
        out += rect(tx0, ry, total_w, row_h, fill='bg', stroke='border', sw=1)
        cx = tx0
        # num
        out += text(cx + col_widths[0]/2, ry + 32, n, size=14, color='accent', weight=700, mono=True, anchor='middle')
        cx += col_widths[0]
        out += line(cx, ry, cx, ry + row_h, stroke='border')
        # what
        out += text(cx + 12, ry + 26, what, size=13, color='text', weight=700)
        if accent_tag == 'galaxy':
            # 생태계 chip
            chip_y = ry + 38
            out += rect(cx + 12, chip_y, 50, 18, fill='galaxy_soft', rx=3)
            out += text(cx + 37, chip_y + 13, '생태계', size=10, color='galaxy', weight=700, anchor='middle')
        cx += col_widths[1]
        out += line(cx, ry, cx, ry + row_h, stroke='border')
        # how
        wrap_lines = wrap_text(how, 56)
        cy = ry + 24
        for ln in wrap_lines[:5]:
            out += text(cx + 12, cy, ln, size=11.5, color='text')
            cy += 18
        cx += col_widths[2]
        out += line(cx, ry, cx, ry + row_h, stroke='border')
        # evidence (mono, on soft bg)
        out += rect(cx, ry, col_widths[3], row_h, fill='soft')
        out += line(cx, ry, cx, ry + row_h, stroke='border')
        ev_lines = wrap_text(evidence, 32)
        cy = ry + 28
        for ln in ev_lines[:4]:
            out += text(cx + 12, cy, ln, size=11.5, color='dim', mono=True)
            cy += 20
        cx += col_widths[3]
        out += line(cx, ry, cx, ry + row_h, stroke='border')
        # none (danger color)
        none_lines = wrap_text(none, 62)
        cy = ry + 24
        for ln in none_lines[:5]:
            out += text(cx + 12, cy, ln, size=11.5, color='danger')
            cy += 18
        ry += row_h

    # Honest box at bottom
    hb_y = ry + 16
    hb_h = 200
    out += rect(tx0, hb_y, total_w, hb_h, fill='warn_soft', stroke='warn_border', sw=1, rx=8)
    out += rect(tx0, hb_y, 4, hb_h, fill='warn', rx=2)
    out += text(tx0 + 20, hb_y + 28, '솔직 인정 — 차별점이 아닌 영역', size=13, color='warn', weight=700)
    honest_items = [
        ('의도 자유도', 'Gemini Live·Apple Intelligence·ChatGPT 모두 자연어로 임의 의도 처리 가능. BudsAI의 "8개 의도 분류기"는 결국 같은 LLM 시대 패턴이며 단독 우위가 아니다.'),
        ('세션 연속 대화', 'Gemini Live·Apple Intelligence가 이미 인터럽티블 후속 대화를 더 자연스럽게 처리한다. BudsAI의 PrevSessionID는 "직전 사운드 트랙"을 같이 끌고 간다는 점에서만 의미.'),
        ('실시간 통역', 'Buds4 Pro Interpreter·Timekettle·Pixel Buds Pro 2의 Gemini가 동등 또는 더 강함. BudsAI는 8개 의도 중 하나로 처리할 뿐.'),
        ('ANC · 음질', 'Sony XM5·AirPods Pro 2가 최고. BudsAI는 차세대 Buds Pro HW에 의존.'),
    ]
    cy = hb_y + 60
    for label, body in honest_items:
        out += text(tx0 + 20, cy, f'• {label} — {body}', size=12, color='warn_text')
        cy += 28

    return out + svg_close()


def wrap_text(s, max_chars):
    """Naive char-based wrap for Korean text."""
    lines = []
    cur = ''
    for word in s.replace('\n', ' ').split(' '):
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += ' ' + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ============================================================
# SLIDE 04 — Galaxy synergy (banner + scenarios + 6 cards + positioning)
# ============================================================
def slide_04():
    out = svg_open() + bg()
    out += slide_header('04 / 04', 'Galaxy + BudsAI 시너지 — One UI 통합이 만드는 절대적 우위', 'Galaxy Synergy', tag_color='galaxy')
    out += lead([
        'BudsAI는 타사 호스트에서도 동작하지만, Galaxy 환경에서는 다른 차원이 된다.',
        '버즈 응답이 Galaxy 폰 앱·워치·태블릿·차량·DeX로 자동 라우팅되며, Bixby Routines가 위치·시간 기반으로 BudsAI 자체를 자동 트리거. 이게 Galaxy 구매 동인의 핵심.',
    ], y_start=112)

    # Galaxy banner
    bn_y = 165
    bn_h = 80
    out += rect(50, bn_y, W - 100, bn_h, fill='galaxy_bg', stroke='galaxy_soft', sw=1, rx=8)
    out += rect(50, bn_y, 4, bn_h, fill='galaxy', rx=2)
    out += text(70, bn_y + 26, '핵심 원리', size=13, color='galaxy', weight=700)
    bn_lines = [
        'Galaxy 컴패니언 앱이 BudsAI 서버 응답을 받아 폰의 적절한 앱(Spotify·Samsung Notes·Calendar·Internet)으로 액션을 자동 라우팅.',
        '자사 앱·OS·차량·웨어러블 생태계를 모두 가진 회사는 삼성과 애플뿐이고, 애플은 호스트 무관 아키텍처를 만들 동기가 없음 → 사실상 Galaxy + BudsAI 조합에서만 가능.',
    ]
    cy = bn_y + 46
    for ln in bn_lines:
        out += text(70, cy, ln, size=12, color='text')
        cy += 18

    # Scenario table (5 rows)
    st_y = bn_y + bn_h + 18
    st_cols = ['일상 시나리오', 'BudsAI 단독 (타사 호스트)', '+ Galaxy 폰 페어링 시']
    st_widths = [240, 700, 880]
    total_w = sum(st_widths)

    scenarios = [
        ('카페에서 음악 식별',
         '"아이유의 Love wins all입니다" TTS만. 더 듣고 싶으면 사용자가 음악 앱 직접 열어야.',
         'TTS + Spotify/YouTube Music이 곡을 자동 재생 큐 추가, 좋아요 자동, 잠금화면 앨범아트, Galaxy Watch 알림.'),
        ('영어 단어 뜻',
         '"전형적인이란 뜻" TTS만. 단어장 정리는 사용자 몫.',
         'Samsung Notes의 영단어장에 자동 저장 (날짜·예문 포함), Galaxy AI Note Assist가 주간 복습 카드 생성.'),
        ('회의 통화 "부장님 뭐라셨지"',
         '직전 30초 요약을 TTS로. 기록은 사용자가 폰 꺼내 옮겨 적어야.',
         'Samsung Notes 자동 받아쓰기 + Galaxy AI가 액션 아이템 추출 → Calendar 일정 자동 등록, Watch 리마인더.'),
        ('운전 중 라디오 곡 식별',
         'TTS만. 차량 디스플레이는 그대로 라디오.',
         'One UI Auto가 차량 디스플레이에 곡명·아티스트 표시, "좋아요" 음성으로 플레이리스트 자동 저장.'),
        ('미드 대사 번역',
         '번역 TTS 응답.',
         'Galaxy Tab/DeX 외부 모니터에 직전 30초 자막+번역 동시 표시, Multi-Control로 후속 질문, SmartThings로 TV 미러링.'),
    ]

    head_h = 36
    row_h = 56

    # Header
    out += rect(50, st_y, total_w, head_h, fill='elev', stroke='border', sw=1)
    cx = 50
    for i, c in enumerate(st_cols):
        if i > 0:
            out += line(cx, st_y, cx, st_y + head_h, stroke='border')
        is_galaxy = (i == 2)
        if is_galaxy:
            out += rect(cx, st_y, st_widths[i], head_h, fill='galaxy_soft')
        out += text(cx + 12, st_y + 23, c.upper(), size=11, color='galaxy' if is_galaxy else 'text', weight=700, spacing='0.04em')
        cx += st_widths[i]

    # Rows
    ry = st_y + head_h
    for (trig, alone, galaxy) in scenarios:
        out += rect(50, ry, total_w, row_h, fill='bg', stroke='border', sw=1)
        # trigger cell bg
        out += rect(50, ry, st_widths[0], row_h, fill='soft')
        out += text(62, ry + 32, trig, size=12, color='text', weight=700)
        cx = 50 + st_widths[0]
        out += line(cx, ry, cx, ry + row_h, stroke='border')
        # alone
        alone_lines = wrap_text(alone, 70)
        cy = ry + 22
        for ln in alone_lines[:3]:
            out += text(cx + 12, cy, ln, size=11, color='dim')
            cy += 16
        cx += st_widths[1]
        out += line(cx, ry, cx, ry + row_h, stroke='border')
        # galaxy
        out += rect(cx, ry, st_widths[2], row_h, fill='galaxy_bg')
        out += line(cx, ry, cx, ry + row_h, stroke='border')
        galaxy_lines = wrap_text(galaxy, 78)
        cy = ry + 22
        for ln in galaxy_lines[:3]:
            out += text(cx + 12, cy, ln, size=11, color='text')
            cy += 16
        ry += row_h

    # 6 Galaxy feature cards
    fc_y = ry + 18
    fc_w = (W - 100 - 5 * 12) / 6  # 6 cards with 12 gap, ≈297
    fc_h = 120
    features = [
        ('F1 · ROUTINES', 'Bixby Routines 자동 트리거', '위치(회의실·카페·차량)·시간 기반으로 BudsAI 트리거 감도를 자동 조정.', '위치 → 모드 자동 전환'),
        ('F2 · AUTO-ROUTE', '앱 자동 라우팅', '의도별 결과를 Spotify·Notes·Calendar에 자동 저장 + 후속 액션 실행.', '컴패니언 앱 디스패치'),
        ('F3 · SMARTTHINGS', '다중 디바이스 동기화', 'Watch에 결과 알림, Tab에서 후속 작업, 거실 TV 미러링, 차량에 컨텍스트.', 'Watch · Tab · TV · Auto'),
        ('F4 · ONE UI AUTO', '차량 디스플레이 통합', '운전 중 음악 식별·번역·길찾기 응답이 차량 디스플레이에 자동 시각화.', '운전 중 안전한 시각 응답'),
        ('F5 · DEX', 'DeX 외부 모니터 확장', '회의·강의 보조 모드에서 직전 30초 파형 + 응답을 외부 모니터에 시각화.', '회의·강의 보조 화면'),
        ('F6 · KNOX VAULT', 'Knox Vault 보안 강화', '버즈 SE 인증서를 Galaxy의 Knox Vault에 백업·동기화. 엔터프라이즈 등급.', 'SE + Knox 이중 보호'),
    ]
    for i, (ic, title, body, ex) in enumerate(features):
        fx = 50 + i * (fc_w + 12)
        out += rect(fx, fc_y, fc_w, fc_h, fill='bg', stroke='border', sw=1, rx=6)
        out += rect(fx, fc_y, 3, fc_h, fill='galaxy', rx=1)
        out += text(fx + 12, fc_y + 18, ic, size=10, color='galaxy', weight=700, mono=True, spacing='0.06em')
        out += text(fx + 12, fc_y + 38, title, size=12, color='text', weight=700)
        bd_lines = wrap_text(body, 26)
        cy = fc_y + 58
        for ln in bd_lines[:3]:
            out += text(fx + 12, cy, ln, size=10.5, color='dim')
            cy += 14
        # bottom dashed sep + ex
        out += line(fx + 12, fc_y + fc_h - 24, fx + fc_w - 12, fc_y + fc_h - 24, stroke='border', dash='3 3')
        out += text(fx + 12, fc_y + fc_h - 8, ex, size=10, color='galaxy', mono=True)

    # Final positioning box
    fp_y = fc_y + fc_h + 14
    fp_h = 100
    out += rect(50, fp_y, W - 100, fp_h, fill='galaxy_bg', stroke='galaxy_soft', sw=1, rx=8)
    out += rect(50, fp_y, 4, fp_h, fill='galaxy', rx=2)
    out += text(70, fp_y + 28, '한 줄 포지셔닝', size=13, color='galaxy', weight=700)
    fp_lines = [
        'BudsAI의 진짜 단독 차별점은 4개다. 기술 3개(직전 사운드 컨텍스트 · 호스트 무관 · E2E 보안)는 어떤 OEM이 따라할 수 있을지 몰라도,',
        '4번째인 Galaxy 자사 생태계 자동 통합은 호스트 무관(#02)을 풀 의지가 있고 자사 앱·차량·웨어러블·DeX·SE 보안을 모두 가진 회사가 삼성 하나뿐이기 때문에 구조적으로 복제 불가능.',
        '이 4번째가 BudsAI의 진짜 사업적 해자.',
    ]
    cy = fp_y + 50
    for ln in fp_lines:
        out += text(70, cy, ln, size=12, color='text')
        cy += 18

    return out + svg_close()


# ============================================================
if __name__ == '__main__':
    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))
    files = [
        ('compare-slide-01.svg', slide_01()),
        ('compare-slide-02.svg', slide_02()),
        ('compare-slide-03.svg', slide_03()),
        ('compare-slide-04.svg', slide_04()),
    ]
    for name, content in files:
        path = os.path.join(out_dir, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'wrote {path} ({len(content)} bytes)')
