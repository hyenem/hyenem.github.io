#!/usr/bin/env python3
"""Generate Figma-importable SVG slide from opus-slide.html content."""
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
    'blue': '#1d4ed8', 'blue_soft': '#dbeafe', 'blue_bg': '#eff6ff',
    'violet': '#6d28d9', 'violet_soft': '#ede9fe',
    # Engine palette (matches HTML)
    'silk_bg': '#fde68a', 'silk_border': '#f59e0b', 'silk_text': '#78350f',
    'celt_bg': '#ddd6fe', 'celt_border': '#8b5cf6', 'celt_text': '#4c1d95',
    'hybrid_bg': '#fbcfe8', 'hybrid_border': '#ec4899', 'hybrid_text': '#831843',
    'tldr_text': '#064e3b',
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
    """Top meta bar: NN/NN, title, tag chip."""
    out = ''
    out += text(50, 60, num, size=12, color='muted', mono=True, spacing='0.08em')
    out += text(140, 62, title, size=22, color='text', weight=700)
    tag_bg = C.get(f'{tag_color}_soft', C['accent_soft'])
    tag_fg = C.get(tag_color, C['accent'])
    chip_w = 14 + len(tag) * 7
    chip_x = W - 50 - chip_w
    out += f'  <rect x="{chip_x}" y="46" width="{chip_w}" height="24" rx="4" fill="{tag_bg}"/>\n'
    out += f'  <text x="{chip_x + chip_w/2}" y="62" font-size="11" font-weight="700" fill="{tag_fg}" text-anchor="middle" font-family="{MONO}" letter-spacing="0.08em">{esc(tag.upper())}</text>\n'
    out += line(50, 88, W - 50, 88, stroke='border')
    return out


def lead(lines, y_start=110):
    out = ''
    y = y_start
    for ln in lines:
        out += text(50, y, ln, size=13.5, color='dim')
        y += 20
    return out


def wrap_text(s, max_chars):
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
# Engine pill (small inline tag)
# ============================================================
def engine_pill(x, y, label, kind, size=11):
    """Render an SILK/CELT/HYBRID tag pill. (x, y) is top-left."""
    bg_c = C[f'{kind}_bg']
    border_c = C[f'{kind}_border']
    text_c = C[f'{kind}_text']
    pad_x = 8
    w = pad_x * 2 + len(label) * 7
    h = 20
    out = f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{bg_c}" stroke="{border_c}" stroke-width="1"/>\n'
    out += f'  <text x="{x + w/2}" y="{y + h - 6}" font-size="{size}" font-weight="700" fill="{text_c}" text-anchor="middle" font-family="{MONO}" letter-spacing="0.04em">{esc(label)}</text>\n'
    return out, w


# ============================================================
# Def card (left column)
# ============================================================
def def_card(x, y, w, h, title, key_label, paragraphs, facts, accent=False, engines=None):
    bg_c = 'accent_bg' if accent else 'soft'
    border_c = 'accent_dim' if accent else 'border'
    title_c = 'accent' if accent else 'text'

    out = rect(x, y, w, h, fill=bg_c, stroke=border_c, sw=1, rx=8)
    cy = y + 30
    # Title + key chip
    out += text(x + 16, cy, title, size=16, color=title_c, weight=700)
    if key_label:
        # right-aligned key chip
        chip_w = 12 + len(key_label) * 7
        chip_x = x + w - 16 - chip_w
        chip_y = cy - 16
        out += f'  <rect x="{chip_x}" y="{chip_y}" width="{chip_w}" height="20" rx="3" fill="#ffffff" stroke="{C["border"]}" stroke-width="1"/>\n'
        out += f'  <text x="{chip_x + chip_w/2}" y="{chip_y + 14}" font-size="10.5" fill="{C["muted"]}" text-anchor="middle" font-family="{MONO}" letter-spacing="0.04em">{esc(key_label)}</text>\n'
    cy += 18

    # Paragraphs
    for p_lines in paragraphs:
        for ln in p_lines:
            out += text(x + 16, cy, ln, size=12.5, color='dim')
            cy += 18
        cy += 4

    # Engine tag row (optional)
    if engines:
        ex = x + 16
        for kind, label in engines:
            pill_str, pw = engine_pill(ex, cy - 2, label, kind)
            out += pill_str
            ex += pw + 8
        cy += 26

    # Facts
    for fact_lines in facts:
        # bullet at first line
        out += text(x + 22, cy, '·', size=14, color='accent', weight=900)
        for i, ln in enumerate(fact_lines):
            tx = x + 32
            out += text(tx, cy, ln, size=12, color='text')
            cy += 17
        cy += 2

    return out


# ============================================================
# Quality bars (right top)
# ============================================================
def qbar_row(x, y, label_top, label_mode, kind, fill_pct, fill_text, label_right_lines):
    """Single quality bar row.
    Layout (inside the right block area):
      label_col_w = 110
      track_x = x + 122
      track_w = total - 122 - 130 = ?
      label_right_x = x + total - 8
    """
    LBL_W = 110
    RIGHT_W = 150
    GAP = 12
    TOTAL_W = 1300  # caller-controlled; we'll be given the row width via x to x+row_w
    # We'll have callers pass row_w explicitly using qbar_row_w
    pass


def qbar_row_full(x, y, row_w, br_text, mode_text, kind, fill_pct, fill_text, right_lines):
    LBL_W = 110
    RIGHT_W = 156
    GAP = 12
    track_x = x + LBL_W + GAP
    track_w = row_w - LBL_W - RIGHT_W - 2 * GAP
    track_h = 28

    out = ''
    # left bitrate label
    out += text(x, y + 14, br_text, size=14, color='text', weight=700, mono=True)
    out += text(x, y + 30, mode_text, size=10, color='muted', mono=True, spacing='0.04em')

    # track (background)
    out += f'  <rect x="{track_x}" y="{y}" width="{track_w}" height="{track_h}" rx="4" fill="{C["soft"]}" stroke="{C["border"]}" stroke-width="1"/>\n'
    # fill
    fill_w = int(track_w * fill_pct / 100)
    bg_c = C[f'{kind}_bg']
    border_c = C[f'{kind}_border']
    text_c = C[f'{kind}_text']
    out += f'  <rect x="{track_x}" y="{y}" width="{fill_w}" height="{track_h}" rx="4" fill="{bg_c}"/>\n'
    # right edge subtle separator
    out += f'  <line x1="{track_x + fill_w}" y1="{y}" x2="{track_x + fill_w}" y2="{y + track_h}" stroke="rgba(0,0,0,0.08)" stroke-width="1"/>\n'
    # fill label
    out += f'  <text x="{track_x + 10}" y="{y + track_h - 9}" font-size="12" font-weight="700" fill="{text_c}" letter-spacing="0.02em" font-family="{FONT}">{esc(fill_text)}</text>\n'

    # right label (multi-line, right aligned)
    rx = x + row_w - 6
    ry = y + 14
    for ln in right_lines:
        out += text(rx, ry, ln, size=11, color='dim', anchor='end')
        ry += 14
    return out


# ============================================================
# MAIN SLIDE — Opus one-pager
# ============================================================
def slide_opus():
    out = svg_open() + bg()
    out += slide_header('01 / 01', 'Opus — 한 코덱으로 음성과 음악을 다 잡는 IETF 표준', 'Codec · RFC 6716')
    out += lead([
        'Opus는 SILK(음성용 LPC) + CELT(음악용 MDCT)를 한 비트스트림 안에서 자동 전환·하이브리드로 묶은 IETF 표준 코덱이다.',
        '6 ~ 510 kbps, 8 ~ 48 kHz, 2.5 ~ 60 ms 프레임을 한 디코더가 다 받는다.',
    ], y_start=112)

    # ===== Layout =====
    # Left col: 3 definition cards stacked, width 430
    # Right col: quality block + size block stacked
    LEFT_X = 50
    LEFT_W = 430
    RIGHT_X = LEFT_X + LEFT_W + 24
    RIGHT_W = W - RIGHT_X - 50  # ~1366
    TOP_Y = 170
    BOTTOM_RESERVE = 110  # TL;DR area
    AREA_BOTTOM = H - BOTTOM_RESERVE - 20  # 950
    AREA_H = AREA_BOTTOM - TOP_Y  # ~780

    # ===== LEFT: 3 def cards =====
    gap = 14
    # Heights: card1=270, card2=330, card3=180 → 780 (with 2 gaps of 14 = 808 — adjust)
    h1 = 256
    h2 = 326
    h3 = 184
    # total = 256+14+326+14+184 = 794 ≈ AREA_H
    y = TOP_Y

    # Card 1: Opus가 뭔가?
    out += def_card(
        LEFT_X, y, LEFT_W, h1,
        title='Opus가 뭔가?',
        key_label='RFC 6716 · 2012',
        paragraphs=[[
            'IETF가 표준화한 로열티 프리 오디오 코덱.',
            'Skype의 SILK와 Xiph의 CELT를 합쳐, VoIP부터',
            '음악 스트리밍·라이브 방송까지 한 코덱으로 커버.',
        ]],
        facts=[
            ['비트레이트 6 ~ 510 kbps (VBR 기본, CBR 가능)'],
            ['샘플레이트 8 / 12 / 16 / 24 / 48 kHz'],
            ['프레임 2.5 / 5 / 10 / 20 / 40 / 60 ms'],
            ['모노 / 스테레오 / 멀티채널'],
            ['WebRTC · Discord · YouTube Live · Zoom'],
        ],
        accent=False,
    )
    y += h1 + gap

    # Card 2: 압축 원리 (accent)
    out += def_card(
        LEFT_X, y, LEFT_W, h2,
        title='압축 원리',
        key_label='hybrid engine',
        paragraphs=[[
            'Opus는 콘텐츠·비트레이트에 따라 두 엔진을',
            '프레임 단위로 전환. 경계에서는 두 엔진을',
            '동시에 돌리는 하이브리드 모드 사용.',
        ]],
        engines=[('silk', 'SILK'), ('celt', 'CELT'), ('hybrid', 'HYBRID')],
        facts=[
            ['SILK: 음성용. LPC 선형 예측 → 저비트레이트', '에서도 자연스러운 음성. NB/MB/WB 모드.'],
            ['CELT: 음악·저지연용. MDCT 변환 코딩 →', '음악·과도음에 강함. SWB/FB 모드.'],
            ['Hybrid: 저주파 SILK, 고주파 CELT —', '12 ~ 40 kbps 음성에서 자동.'],
            ['DTX(무음 송신 정지), 인밴드 FEC,', 'PLC(패킷 손실 은닉) 내장.'],
        ],
        accent=True,
    )
    y += h2 + gap

    # Card 3: 왜 BudsAI에 맞나
    out += def_card(
        LEFT_X, y, LEFT_W, h3,
        title='왜 BudsAI에 맞나',
        key_label=None,
        paragraphs=[],
        facts=[
            ['한 코덱이 음성·음악을 다 잡음 — "방금 듣던 곡"'],
            ['12 kbps WB 30초 음성 ≈ 45 KB, BT PAN+mTLS에 가뜬'],
            ['지연 5 ms 모드까지 — 링버퍼 회전 부담 無'],
            ['표준이라 서버 측 libopus 디코딩 검증·무료'],
            ['모든 모던 OS·브라우저에 디코더 내장'],
        ],
        accent=False,
    )

    # ===== RIGHT: quality block + size block =====
    # Quality block ~390 high, Size block ~390 high
    q_h = 360
    s_h = AREA_H - q_h - gap

    # ----- Quality block -----
    qx = RIGHT_X
    qy = TOP_Y
    qw = RIGHT_W
    # outer card with left accent border
    out += rect(qx, qy, qw, q_h, fill='bg', stroke='border', sw=1, rx=8)
    out += rect(qx, qy, 4, q_h, fill='accent', rx=2)
    # head
    out += text(qx + 18, qy + 26, '퀄리티 — 비트레이트별 체감 (MUSHRA 계열 평가 종합)', size=15, color='text', weight=700)
    out += text(qx + qw - 14, qy + 26, 'listening tests / xiph.org', size=11, color='muted', mono=True, anchor='end')
    out += line(qx + 18, qy + 40, qx + qw - 14, qy + 40, stroke='border', dash='4 3')

    # Rows
    bars = [
        ('6 kbps',   'NB · 음성',         'silk',   32,  '알아들음',         ['전화선보다 소폭 거침']),
        ('12 kbps',  'WB · 음성',         'hybrid', 62,  '자연스러움',       ['PSTN(64 kbps) 훨씬 상회']),
        ('16 kbps',  'WB · 음성',         'hybrid', 74,  'VoIP 권장',        ['WebRTC 기본값']),
        ('24 kbps',  'WB · 음성',         'hybrid', 86,  '사실상 투명',      ['음성 기준 원음 구분 난']),
        ('64 kbps',  'FB · 음악 mono',    'celt',   78,  'AAC 96 kbps 동급', ['스트리밍 준수']),
        ('96 kbps',  'FB · 음악 stereo',  'celt',   90,  '거의 투명',        ['동영상 오디오 트랙']),
        ('128 kbps', 'FB · 음악 stereo',  'celt',   97,  '투명 (ABX 불가)',  ['CD급 무손실 체감']),
    ]
    bar_y = qy + 56
    bar_gap = 6
    bar_h = 28
    inner_x = qx + 18
    inner_w = qw - 36
    for br, mode, kind, pct, ftxt, rlines in bars:
        out += qbar_row_full(inner_x, bar_y, inner_w, br, mode, kind, pct, ftxt, rlines)
        bar_y += bar_h + bar_gap

    # qscale (range labels)
    sc_y = bar_y + 4
    out += text(inner_x + 122, sc_y, '0 kbps', size=10.5, color='muted', mono=True)
    out += text(inner_x + 122 + (inner_w - 122 - 156) / 2, sc_y, '품질 →', size=10.5, color='muted', mono=True, anchor='middle')
    out += text(inner_x + inner_w - 156, sc_y, '투명(원음 구분 불가)', size=10.5, color='muted', mono=True, anchor='end')

    # Legend
    leg_y = qy + q_h - 16
    out += line(qx + 18, leg_y - 14, qx + qw - 14, leg_y - 14, stroke='border', dash='4 3')
    # legend swatches
    lx = qx + 22
    def swatch(x, y, kind):
        return f'  <rect x="{x}" y="{y - 9}" width="11" height="11" rx="2" fill="{C[f"{kind}_bg"]}" stroke="{C[f"{kind}_border"]}" stroke-width="1"/>\n'
    out += swatch(lx, leg_y, 'silk')
    out += text(lx + 16, leg_y, 'SILK (음성 LPC)', size=11.5, color='dim')
    lx2 = lx + 180
    out += swatch(lx2, leg_y, 'hybrid')
    out += text(lx2 + 16, leg_y, 'Hybrid (SILK+CELT)', size=11.5, color='dim')
    lx3 = lx2 + 200
    out += swatch(lx3, leg_y, 'celt')
    out += text(lx3 + 16, leg_y, 'CELT (음악 MDCT)', size=11.5, color='dim')

    # ----- Size block -----
    sx = RIGHT_X
    sy = TOP_Y + q_h + gap
    sw = RIGHT_W
    out += rect(sx, sy, sw, s_h, fill='bg', stroke='border', sw=1, rx=8)
    out += rect(sx, sy, 4, s_h, fill='blue', rx=2)
    out += text(sx + 18, sy + 26, '공간 ↔ 시간 — 같은 1 MB에 얼마나 담기나', size=15, color='text', weight=700)
    out += text(sx + sw - 14, sy + 26, 'bitrate × 60 / 8 = KB/min', size=11, color='muted', mono=True, anchor='end')
    out += line(sx + 18, sy + 40, sx + sw - 14, sy + 40, stroke='border', dash='4 3')

    # Table
    table_x = sx + 18
    table_w = sw - 36
    # Columns: 비트레이트 / 용도 / KB/분 / 1MB로 저장 / 30초
    col_w = [200, 0, 140, 170, 130]  # 용도 = remainder
    col_w[1] = table_w - sum(col_w)
    th_y = sy + 56
    th_h = 32
    out += rect(table_x, th_y, table_w, th_h, fill='soft', stroke='border_strong', sw=1)
    headers = ['비트레이트', '용도', 'KB / 분', '1 MB로 저장', '30초']
    aligns = ['start', 'start', 'end', 'end', 'end']
    cx = table_x
    for i, hd in enumerate(headers):
        if aligns[i] == 'end':
            out += text(cx + col_w[i] - 12, th_y + 21, hd.upper(), size=10.5, color='muted', weight=700, spacing='0.06em', anchor='end')
        else:
            out += text(cx + 12, th_y + 21, hd.upper(), size=10.5, color='muted', weight=700, spacing='0.06em')
        if i < len(headers) - 1:
            pass  # no vertical separator in this style
        cx += col_w[i]

    # Rows
    table_rows = [
        # (br, pill_kind, pill_label, use_text, kb_min, mb_time, sec30, is_buds)
        ('6 kbps',   'silk',   'SILK', 'NB 음성 (협대역, DTX on)',      '45 KB',  '22 분',  '23 KB',  False),
        ('12 kbps',  'hybrid', 'HYB',  'WB 음성, 일상 통화 수준',       '90 KB',  '11 분',  '45 KB',  True),
        ('16 kbps',  'hybrid', 'HYB',  'WB 음성, WebRTC 권장',          '120 KB', '8.5 분', '60 KB',  False),
        ('24 kbps',  'hybrid', 'HYB',  'WB 음성, 사실상 투명',          '180 KB', '5.5 분', '90 KB',  False),
        ('64 kbps',  'celt',   'CELT', 'FB 음악 mono, AAC 96k 동급',    '480 KB', '2.1 분', '240 KB', False),
        ('128 kbps', 'celt',   'CELT', 'FB 음악 stereo, 거의 투명',     '960 KB', '~65 초', '480 KB', False),
    ]
    row_h = 38
    ry = th_y + th_h
    for br, kind, plabel, use_text, kbmin, mbtime, sec30, is_buds in table_rows:
        if is_buds:
            out += rect(table_x, ry, table_w, row_h, fill='accent_bg', stroke='accent_dim', sw=1)
        else:
            out += rect(table_x, ry, table_w, row_h, fill='bg', stroke='border', sw=1)
        cx = table_x
        # col 0: bitrate + pill
        out += text(cx + 12, ry + 24, br, size=12.5, color='text', weight=700, mono=True)
        pill_str, pw = engine_pill(cx + 12 + len(br) * 7.5 + 6, ry + 11, plabel, kind, size=10)
        out += pill_str
        cx += col_w[0]
        # col 1: use
        out += text(cx + 6, ry + 24, use_text, size=12, color='dim')
        # BUDS tag at end of use cell
        if is_buds:
            tag_label = 'BUDS'
            tag_w = 50
            tag_x = cx + col_w[1] - tag_w - 6
            tag_y = ry + 11
            out += f'  <rect x="{tag_x}" y="{tag_y}" width="{tag_w}" height="18" rx="3" fill="{C["accent"]}"/>\n'
            out += f'  <text x="{tag_x + tag_w/2}" y="{tag_y + 13}" font-size="10" font-weight="700" fill="#ffffff" text-anchor="middle" font-family="{MONO}" letter-spacing="0.06em">{esc(tag_label)}</text>\n'
        cx += col_w[1]
        # col 2: KB/min (right)
        out += text(cx + col_w[2] - 12, ry + 24, kbmin, size=12, color='text', mono=True, anchor='end')
        cx += col_w[2]
        # col 3: 1MB time (right, accent)
        out += text(cx + col_w[3] - 12, ry + 24, mbtime, size=12.5, color='accent', weight=700, mono=True, anchor='end')
        cx += col_w[3]
        # col 4: 30초 (right)
        out += text(cx + col_w[4] - 12, ry + 24, sec30, size=12, color='text', mono=True, anchor='end')
        ry += row_h

    # Formula box at bottom of size block
    fm_y = ry + 12
    fm_h = 30
    out += rect(table_x, fm_y, table_w, fm_h, fill='soft', stroke='border', sw=1, rx=4)
    out += text(table_x + 12, fm_y + 20, '환산 공식: ', size=11.5, color='muted', mono=True)
    out += text(table_x + 12 + 78, fm_y + 20, 'bitrate(kbps) × 60 / 8 = KB/min', size=11.5, color='violet', mono=True)
    out += text(table_x + 12 + 78 + 240, fm_y + 20, ' · 패킷·컨테이너 오버헤드는 ±5% 수준이라 표에서는 무시.', size=11.5, color='muted', mono=True)

    # ===== TL;DR callout =====
    td_y = AREA_BOTTOM + 14
    td_h = 92
    out += rect(50, td_y, W - 100, td_h, fill='accent_bg', stroke='accent_dim', sw=1, rx=8)
    out += rect(50, td_y, 4, td_h, fill='accent', rx=2)
    out += text(70, td_y + 26, 'TL;DR', size=14, color='accent', weight=700)
    td_lines = [
        'Opus는 SILK(음성) + CELT(음악)를 한 코덱에 묶어 6 ~ 510 kbps를 자유롭게 오간다.',
        'BudsAI의 30초 음성 링버퍼는 12 kbps WB 기준 약 45 KB로 충분하고, 같은 30초를 "방금 듣던 음악"(64 kbps mono)으로 보내도 240 KB — BT PAN 위 mTLS에 부담 없는 크기.',
        '한 디코더가 음성·음악·라이브를 다 받기 때문에, 서버는 입력 종류를 의식할 필요가 없다.',
    ]
    cy = td_y + 48
    for ln in td_lines:
        out += text(70, cy, ln, size=12.5, color='tldr_text')
        cy += 18

    # ===== Footer memo =====
    out += text(W - 50, H - 22, 'BudsAI Design Doc · Opus one-pager', size=11, color='muted', mono=True, anchor='end', spacing='0.04em')

    return out + svg_close()


# ============================================================
if __name__ == '__main__':
    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out_dir, 'opus-slide.svg')
    content = slide_opus()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'wrote {path} ({len(content)} bytes)')
