#!/usr/bin/env python3
"""Generate Figma-importable SVG slide from vad-slide.html content."""
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
    'blue': '#1d4ed8', 'blue_soft': '#dbeafe', 'blue_bg': '#eff6ff', 'blue_border': '#93c5fd',
    'violet': '#6d28d9', 'violet_soft': '#ede9fe',
    'tldr_text': '#064e3b',
    # VAD generation palette
    'g1_bg': '#fde68a', 'g1_border': '#f59e0b', 'g1_text': '#78350f',
    'g2_bg': '#ddd6fe', 'g2_border': '#8b5cf6', 'g2_text': '#4c1d95',
    'g3_bg': '#bbf7d0', 'g3_border': '#22c55e', 'g3_text': '#14532d',
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
# VAD SLIDE
# ============================================================
def vad_slide():
    out = svg_open() + bg()
    out += slide_header(
        '01 / 01',
        'VAD — "지금 사람이 말하고 있는가"를 1/0으로 답하는 신호처리 게이트',
        'VAD · Speech Detection'
    )
    out += lead([
        'VAD(Voice Activity Detection)는 오디오 프레임마다 음성 / 무음을 판정하는 모듈이다. 에너지 임계(70년대) → 통계 모델(WebRTC GMM, 90~10년대) → DNN(Silero, 2014~)로 진화했고,',
        'BudsAI의 30초 링버퍼·DTX·서버 비용·배터리는 전부 이 1비트 판정에 매달려 있다.',
    ], y_start=112)

    # ===== Layout =====
    # Two columns: LEFT defs (430w) + RIGHT blocks
    LX = 50
    LY = 170
    LW = 430
    RX = LX + LW + 20  # 500
    RW = W - 50 - RX   # 1370

    # ============= LEFT: 3 definition cards =============
    # Card heights tuned to fill ~770 px vertical span
    defs = [
        # (title, key_chip, accent, body_lines, facts)
        (
            'VAD가 뭔가?', 'frame → 0/1', False,
            [
                '10~30 ms 단위 오디오 프레임에 대해 음성 확률',
                'p(speech | frame)를 뱉는 분류기. 임계값을 넘으면 1,',
                '아니면 0. ASR·코덱·통화·음성비서의 입구 게이트.',
            ],
            [
                '입력 단위: 10/20/30 ms 프레임 (160~480 샘플 @ 16 kHz)',
                '출력: 이진 라벨 또는 [0,1] 확률',
                '주 사용처: WebRTC, Opus DTX, G.729 Annex B / AMR,',
                '            항상켜진 음성비서',
                '지연 목표 5 ~ 30 ms — 대화에 끼어들 수 있을 만큼',
            ],
        ),
        (
            '왜 어려운가?', 'SNR 문제', True,
            [
                '무음 ≠ 0이다. 환풍기·도로·바람·키보드·다른 사람',
                '목소리가 항상 깔려있고, 그 위로 음성이 살짝 올라오는',
                '게 일반적. SNR이 낮을수록 단순 에너지로는 못 가른다.',
            ],
            [
                '핵심 트레이드오프: miss(말한 거 놓침) ↔',
                '            false alarm(잡음에 켜짐)',
                '잡음이 비정상(non-stationary)일수록 단순 임계 실패',
                '반향·다화자·음악 BGM은 더 어려움 → DNN이 압도',
                '온디바이스 제약: 메모리 KB 단위, 연산 mW 단위',
            ],
        ),
        (
            'BudsAI에서 왜 핵심인가', None, False,
            [],
            [
                '항상켜진 마이크에서 "내가 말한 순간만" 잘라 30s PCM',
                '            링버퍼에 보관',
                'VAD off → Opus DTX → 무음 구간 BT 전송 0 byte',
                '            (배터리·QoS)',
                'VAD on 게이트 → 서버 ASR로 흘려보내는 초 단축',
                '            = 비용 절감',
                '오탐 1번 = 잡음을 30s 통째로 업로드 = mTLS·LTE',
                '            비용·프라이버시 리스크',
                '그래서 펌웨어는 Silero v5 급(~2 MB, 1 ms/frame)을',
                '            NPU에 올린다',
            ],
        ),
    ]

    card_y = LY
    card_heights = [220, 260, 290]  # total 770
    card_gap = 14

    for i, (ctitle, ckey, accent, body, facts) in enumerate(defs):
        ch = card_heights[i]
        fill = 'accent_bg' if accent else 'soft'
        stroke = 'accent_dim' if accent else 'border'
        title_color = 'accent' if accent else 'text'

        out += rect(LX, card_y, LW, ch, fill=fill, stroke=stroke, sw=1, rx=8)
        # Title row
        out += text(LX + 14, card_y + 24, ctitle, size=14, color=title_color, weight=700)
        # Key chip
        if ckey:
            chip_w = 14 + len(ckey) * 6
            title_w = len(ctitle) * 10 + 8
            chip_x = LX + 14 + title_w
            out += rect(chip_x, card_y + 10, chip_w, 18, fill='bg', stroke='border', sw=1, rx=3)
            out += text(chip_x + chip_w / 2, card_y + 23, ckey, size=10, color='muted', mono=True, anchor='middle', spacing='0.04em')

        cy = card_y + 48
        # Body
        for ln in body:
            out += text(LX + 14, cy, ln, size=12, color='dim')
            cy += 17
        if body:
            cy += 6
        # Facts list with · marker
        for ln in facts:
            # Indented continuations start with spaces; check
            if ln.startswith('            '):
                out += text(LX + 26, cy, ln.strip(), size=11.5, color='text')
            else:
                out += text(LX + 22, cy, '·', size=13, color='accent', weight=900)
                out += text(LX + 32, cy, ln, size=11.5, color='text')
            cy += 17

        # Generation tags inside the "왜 어려운가" card
        if i == 1:
            gy = card_y + ch - 28
            # 3 small chips
            gens = [('1세대 에너지', 'g1'), ('2세대 통계', 'g2'), ('3세대 DNN', 'g3')]
            gx = LX + 14
            for label, key in gens:
                gw = 14 + len(label) * 7
                out += rect(gx, gy, gw, 20, fill=f'{key}_bg', stroke=f'{key}_border', sw=1, rx=4)
                out += text(gx + gw / 2, gy + 14, label, size=10, color=f'{key}_text', weight=700, anchor='middle', mono=True, spacing='0.04em')
                gx += gw + 6

        card_y += ch + card_gap

    # ============= RIGHT: 3 blocks =============
    # Block heights: gens ~320, pipe ~180, tricks ~210 + gaps ~16 each
    BY = LY
    block_gap = 14

    # ---------- Block 1: Generations table ----------
    gens_h = 320
    out += rect(RX, BY, RW, gens_h, fill='bg', stroke='border', sw=1, rx=8)
    # left accent stripe (3px)
    out += rect(RX, BY, 3, gens_h, fill='accent', rx=1)
    # Head
    out += text(RX + 16, BY + 24, '원리의 진화 — 세대별 판정 메커니즘', size=14, color='text', weight=700)
    out += text(RX + RW - 16, BY + 24, '1970s → 1990s → 2014~', size=11, color='muted', mono=True, anchor='end')
    out += line(RX + 12, BY + 36, RX + RW - 12, BY + 36, stroke='border', dash='4 3')

    # Table: 4 columns
    tbl_y = BY + 46
    tbl_x = RX + 12
    tbl_w = RW - 24
    col_w = [150, 380, 360, 426]  # 1316 total ≈ RW-24=1346, adjust
    # Actually RW=1370, tbl_w = 1346
    col_w = [150, 370, 360, 466]
    sum_w = sum(col_w)
    # Adjust last col
    col_w[3] = tbl_w - sum(col_w[:3])
    head_h = 28

    # Header row
    out += rect(tbl_x, tbl_y, tbl_w, head_h, fill='soft', stroke=None)
    out += line(tbl_x, tbl_y + head_h, tbl_x + tbl_w, tbl_y + head_h, stroke='border_strong')
    headers = ['세대 / 시기', '판정 신호', '수학 / 모델', '강점 · 약점']
    cx = tbl_x
    for i, h in enumerate(headers):
        out += text(cx + 10, tbl_y + 18, h.upper(), size=10, color='muted', weight=700, spacing='0.06em')
        cx += col_w[i]

    # Data rows
    rows = [
        ('g1', '1세대', 'Energy + ZCR', '1970s ~',
         'RMS 에너지가 임계 넘으면 음성. 보조로 ZCR(부호 바뀐 횟수)로 마찰음(s, f, h) 보강.',
         ['E = Σx[n]²', 'ZCR = Σ|sgn(x[n])−sgn(x[n−1])|', '적응 임계 θ = α·noise_floor'],
         '+ 곱셈 거의 없음, mW급',
         '− SNR < 10 dB이면 망함, 비정상 잡음에 흔들림'),
        ('g2', '2세대', 'Statistical / GMM', '1990s ~ 2010s',
         'FFT로 6 sub-band 에너지를 뽑고, 노이즈 vs 노이즈+음성 PDF 우도비 검정. G.729B, AMR, WebRTC VAD(GMM 4밴드).',
         ['Λ = log p(X|H1) − log p(X|H0)', 'p(X|H) = Σ wᵢ N(μᵢ, Σᵢ)', '노이즈 트래킹: MCRA / Min Stats'],
         '+ 잡음 추정 적응적, aggressiveness 0~3 튜닝',
         '− 정상 가우시안 가정, 반향·음악 BGM 약함'),
        ('g3', '3세대', 'DNN / RNN', '2014 ~',
         'log-mel(또는 raw waveform)을 작은 CNN+GRU에 통과. Silero VAD, Picovoice Cobra, NVIDIA MarbleNet.',
         ['p = σ(GRU(CNN(log-mel(x))))', '학습: LibriSpeech + AudioSet noise', '크기 ~2 MB, 추론 ~1 ms/frame'],
         '+ 저SNR·반향·다화자에서 압도적, AUC 0.99+',
         '− 학습 분포 밖 도메인엔 취약, NPU/SIMD 필요'),
    ]

    row_h = 78
    ry = tbl_y + head_h
    for (gkey, gen_name, gen_sub, era, signal, math_lines, pro, con) in rows:
        # Row separator
        if ry > tbl_y + head_h:
            out += line(tbl_x, ry, tbl_x + tbl_w, ry, stroke='border')
        # Label cell (colored)
        out += rect(tbl_x, ry, col_w[0], row_h, fill=f'{gkey}_bg', stroke=None)
        out += line(tbl_x, ry + row_h, tbl_x + col_w[0], ry + row_h, stroke=f'{gkey}_border', sw=1)
        out += text(tbl_x + 10, ry + 20, gen_name, size=12, color=f'{gkey}_text', weight=700, mono=True)
        out += text(tbl_x + 10, ry + 38, gen_sub, size=11, color=f'{gkey}_text', weight=700, mono=True)
        out += text(tbl_x + 10, ry + 58, era, size=9.5, color=f'{gkey}_text', spacing='0.04em')

        # Signal cell
        cx = tbl_x + col_w[0]
        sig_lines = wrap_text(signal, 36)
        cy = ry + 18
        for ln in sig_lines[:4]:
            out += text(cx + 10, cy, ln, size=11, color='text')
            cy += 15

        # Math cell (code-styled lines)
        cx += col_w[1]
        cy = ry + 18
        for ml in math_lines[:3]:
            # background box
            mw = len(ml) * 6.5 + 12
            mw = min(mw, col_w[2] - 14)
            out += rect(cx + 8, cy - 11, mw, 15, fill='soft', stroke='border', sw=0.5, rx=3)
            out += text(cx + 14, cy, ml, size=9.5, color='violet', mono=True)
            cy += 19

        # Pros/cons cell
        cx += col_w[2]
        out += text(cx + 10, ry + 22, pro, size=10.5, color='text')
        out += text(cx + 10, ry + 48, con, size=10.5, color='text')

        # Vertical separators
        sep_x = tbl_x
        for cw in col_w[:-1]:
            sep_x += cw
            out += line(sep_x, ry, sep_x, ry + row_h, stroke='border')

        ry += row_h

    # ---------- Block 2: Pipeline ----------
    BY2 = BY + gens_h + block_gap
    pipe_h = 200
    out += rect(RX, BY2, RW, pipe_h, fill='bg', stroke='border', sw=1, rx=8)
    out += rect(RX, BY2, 3, pipe_h, fill='blue', rx=1)
    out += text(RX + 16, BY2 + 24, '실제 한 프레임이 흘러가는 길 — 5단계', size=14, color='text', weight=700)
    out += text(RX + RW - 16, BY2 + 24, '20 ms frame @ 16 kHz, 320 samples', size=11, color='muted', mono=True, anchor='end')
    out += line(RX + 12, BY2 + 36, RX + RW - 12, BY2 + 36, stroke='border', dash='4 3')

    # 5 steps
    steps = [
        ('① 캡처', 'PCM 프레임', '마이크 ADC → 16-bit PCM', '320 샘플 (20 ms)', 'int16[320] @16kHz', False),
        ('② 전처리', 'DC컷·프리엠퍼시스', '고역 강조 y[n]=x[n]−0.97x[n−1],', '해닝 윈도우', 'HPF · window', False),
        ('③ 특징추출', 'FFT → log-mel / 밴드E', '512-pt FFT → 40 mel bin → log', '(또는 6 sub-band E)', 'log-mel[40]', False),
        ('④ 판정', 'GMM LRT / DNN 추론', '우도비 또는 CNN+GRU →', 'p ∈ [0, 1]', 'p(speech) = 0.87', True),
        ('⑤ 후처리', 'Hangover · 비대칭 임계', '임계 비교 + N프레임 hangover', '→ final 0/1', 'VAD = 1 (sticky)', False),
    ]
    step_y = BY2 + 50
    step_h = 130
    arrow_w = 16
    inner_w = RW - 24 - 4 * arrow_w
    step_w = inner_w / 5
    sx = RX + 12

    for i, (num, title, desc1, desc2, code, highlight) in enumerate(steps):
        fill = 'accent_bg' if highlight else 'soft'
        stroke = 'accent_dim' if highlight else 'border'
        out += rect(sx, step_y, step_w, step_h, fill=fill, stroke=stroke, sw=1, rx=6)
        if highlight:
            # glow effect via slightly larger outer stroke
            out += rect(sx - 2, step_y - 2, step_w + 4, step_h + 4, fill='none', stroke='accent_dim', sw=1, rx=8)
        # Number/label
        num_color = 'accent' if highlight else 'muted'
        out += text(sx + 10, step_y + 18, num, size=11, color=num_color, mono=True, weight=700, spacing='0.05em')
        # Title
        out += text(sx + 10, step_y + 40, title, size=12, color='text', weight=700)
        # Description
        out += text(sx + 10, step_y + 62, desc1, size=10.5, color='dim')
        out += text(sx + 10, step_y + 78, desc2, size=10.5, color='dim')
        # Code box
        cw = min(len(code) * 6.5 + 14, step_w - 20)
        out += rect(sx + 10, step_y + 92, cw, 18, fill='bg', stroke='border', sw=1, rx=3)
        out += text(sx + 17, step_y + 105, code, size=10, color='violet', mono=True)

        # Arrow to next
        if i < 4:
            ax = sx + step_w + 2
            ay = step_y + step_h / 2
            out += f'  <path d="M {ax} {ay - 6} L {ax + 12} {ay} L {ax} {ay + 6} Z" fill="{C["blue"]}"/>\n'

        sx += step_w + arrow_w

    # ---------- Block 3: Tricks + Metrics ----------
    BY3 = BY2 + pipe_h + block_gap
    tricks_h = 230
    out += rect(RX, BY3, RW, tricks_h, fill='bg', stroke='border', sw=1, rx=8)
    out += rect(RX, BY3, 3, tricks_h, fill='violet', rx=1)
    out += text(RX + 16, BY3 + 24, '성능을 짜내는 보조 메커니즘 · 평가 지표', size=14, color='text', weight=700)
    out += text(RX + RW - 16, BY3 + 24, 'prod tricks + how we measure', size=11, color='muted', mono=True, anchor='end')
    out += line(RX + 12, BY3 + 36, RX + RW - 12, BY3 + 36, stroke='border', dash='4 3')

    # 6 cards: 3 cols × 2 rows
    tricks = [
        ('Hangover', 'sticky', False,
         ['음성 끝나도 N=10~20 프레임 동안 "말하는 중"', '유지. 단어 사이 짧은 침묵(150~300 ms)에서', '끊겨 ASR이 잘리는 걸 막음.']),
        ('비대칭 임계', 'on/off', False,
         ['켤 땐 보수적 θ_on=0.7, 끌 땐 너그럽게', 'θ_off=0.3. 히스테리시스로 경계에서', '깜빡임(chatter) 방지.']),
        ('노이즈 트래킹', 'MCRA', False,
         ['무음 구간 통계로 노이즈 PSD를 계속', '업데이트(Minimum Statistics, MCRA).', '환경이 바뀌어도 따라감.']),
        ('음성 대역 가중', '300–3400', False,
         ['사람 목소리는 대부분 300 Hz ~ 3.4 kHz에', '몰림. 이 대역 sub-band E에 가중치 ↑,', '고주파 잡음은 ↓.']),
        ('지표 — DET / ROC', 'AUC', True,
         ['false alarm vs miss rate 곡선(DET).', '프레임 정확도, AUC, EER.', '응용 관점에선 ASR WER이 진짜 평가.']),
        ('지연 — Algorithmic', 'latency', True,
         ['프레임 + 룩어헤드 + hangover 결정까지.', '통화·비서는 ≤ 30 ms 필수,', '녹음·트랜스크립트는 100 ms도 허용.']),
    ]
    inner_x = RX + 12
    inner_w = RW - 24
    col_count = 3
    card_gap2 = 10
    tw = (inner_w - card_gap2 * (col_count - 1)) / col_count
    th = 86
    grid_y0 = BY3 + 50

    for i, (title, ic, is_metric, lines) in enumerate(tricks):
        col = i % col_count
        row = i // col_count
        tx = inner_x + col * (tw + card_gap2)
        ty = grid_y0 + row * (th + 8)
        fill = 'blue_bg' if is_metric else 'soft'
        stroke = 'blue_border' if is_metric else 'border'
        out += rect(tx, ty, tw, th, fill=fill, stroke=stroke, sw=1, rx=6)
        # Title
        out += text(tx + 10, ty + 20, title, size=12, color='text', weight=700)
        # Icon chip
        ic_w = 12 + len(ic) * 6.5
        ic_x = tx + tw - ic_w - 10
        ic_color = 'blue' if is_metric else 'violet'
        ic_border = 'blue_soft' if is_metric else 'violet_soft'
        out += rect(ic_x, ty + 8, ic_w, 16, fill='bg', stroke=ic_border, sw=1, rx=3)
        out += text(ic_x + ic_w / 2, ty + 19, ic, size=9.5, color=ic_color, weight=700, anchor='middle', mono=True, spacing='0.04em')

        # Body
        cy = ty + 40
        for ln in lines:
            out += text(tx + 10, cy, ln, size=10.5, color='dim')
            cy += 14

    # ============= Bottom TL;DR callout =============
    tldr_y = BY3 + tricks_h + 14
    tldr_h = H - tldr_y - 38  # leave room for footer
    if tldr_h < 88:
        tldr_h = 88
    out += rect(50, tldr_y, W - 100, tldr_h, fill='accent_bg', stroke='accent_dim', sw=1, rx=8)
    out += rect(50, tldr_y, 4, tldr_h, fill='accent', rx=2)
    out += text(70, tldr_y + 26, 'TL;DR', size=14, color='accent', weight=700, mono=True, spacing='0.06em')

    tldr_lines = [
        'VAD는 결국 "이 20 ms 프레임이 음성인가?"를 1비트로 답하는 분류기다. 에너지+ZCR(~70년대) → GMM 우도비(WebRTC, ~10년대) → DNN(Silero, 2014~)로 정확도는 올라가고 모델은',
        '더 작아졌다. BudsAI는 항상켜진 마이크의 게이트로 VAD를 깔아, 말한 순간만 30 s 링버퍼에 채우고 무음 구간엔 BT에 0 byte를 흘린다 — 오탐 1번이 그대로 LTE 비용·프라이버시·',
        '배터리 손실이라, 펌웨어가 작은 DNN VAD(Silero v5 ~2 MB)를 NPU에 올리는 건 옵션이 아니라 필수다.',
    ]
    cy = tldr_y + 50
    for ln in tldr_lines:
        out += text(78, cy, ln, size=12, color='tldr_text')
        cy += 18

    # ============= Footer note =============
    out += text(50, H - 14, 'BudsAI Design Doc · VAD one-pager', size=10, color='muted', mono=True, spacing='0.06em')
    out += text(W - 50, H - 14, 'APPENDIX · VAD ONE-PAGER', size=10, color='accent', mono=True, anchor='end', spacing='0.08em', weight=700)

    return out + svg_close()


# ============================================================
if __name__ == '__main__':
    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(out_dir, 'vad-slide.svg')
    content = vad_slide()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'wrote {path} ({len(content)} bytes)')
