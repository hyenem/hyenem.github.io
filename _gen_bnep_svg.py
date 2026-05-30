#!/usr/bin/env python3
"""Generate Figma-importable 1920x1080 SVG for bnep-slide.html (BNEP one-pager)."""
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
    # Packet layer colors (from bnep-slide.html .pkt .lyr.*)
    'payload_bg': '#fde68a', 'payload_bd': '#f59e0b', 'payload_tx': '#78350f',
    'tcp_bg': '#fecaca', 'tcp_bd': '#ef4444', 'tcp_tx': '#7f1d1d',
    'ip_bg': '#c7d2fe', 'ip_bd': '#6366f1', 'ip_tx': '#3730a3',
    'eth_bg': '#bbf7d0', 'eth_bd': '#22c55e', 'eth_tx': '#14532d',
    'bnep_bg': '#fbcfe8', 'bnep_bd': '#ec4899', 'bnep_tx': '#831843',
    'l2cap_bg': '#ddd6fe', 'l2cap_bd': '#8b5cf6', 'l2cap_tx': '#4c1d95',
    'hci_bg': '#e5e7eb', 'hci_bd': '#9ca3af', 'hci_tx': '#374151',
    'wifi_bg': '#cffafe', 'wifi_bd': '#06b6d4', 'wifi_tx': '#155e75',
    'lte_bg': '#fed7aa', 'lte_bd': '#f97316', 'lte_tx': '#7c2d12',
    'ghost_bg': '#ffffff', 'ghost_bd': '#e5e7eb', 'ghost_tx': '#6b7280',
    # Zone backgrounds
    'bnep_zone_bg': '#fff7ed', 'bnep_zone_bd': '#fb923c', 'bnep_zone_tx': '#c2410c',
    'kernel_zone_bg': '#f5f3ff', 'kernel_zone_bd': '#a78bfa',
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

def rect(x, y, w, h, fill='bg', stroke=None, sw=1, rx=0, dash=None):
    fc = C.get(fill, fill) if fill != 'none' else 'none'
    out = f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fc}"'
    if stroke:
        sc = C.get(stroke, stroke)
        out += f' stroke="{sc}" stroke-width="{sw}"'
        if dash:
            out += f' stroke-dasharray="{dash}"'
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


# ===== Packet layer block =====
def pkt_layer(x, y, w, h, kind, label):
    """Draw one packet layer row."""
    bg_k = f'{kind}_bg'
    bd_k = f'{kind}_bd'
    tx_k = f'{kind}_tx'
    out = ''
    if kind == 'ghost':
        out += f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{C[bg_k]}" stroke="{C[bd_k]}" stroke-width="1" stroke-dasharray="3 2"/>\n'
        out += f'  <text x="{x + w/2}" y="{y + h - 4}" font-size="10" fill="{C[tx_k]}" font-family="{MONO}" text-anchor="middle" text-decoration="line-through">{esc(label)}</text>\n'
    else:
        out += f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{C[bg_k]}" stroke="{C[bd_k]}" stroke-width="1"/>\n'
        out += f'  <text x="{x + w/2}" y="{y + h - 4}" font-size="10" fill="{C[tx_k]}" font-family="{MONO}" text-anchor="middle">{esc(label)}</text>\n'
    return out


def packet_stack(x, y, w, layers, note=None):
    """Draw stacked packet layers; layers = [(kind, label), ...]."""
    out = ''
    h = 15
    gap = 2
    cy = y
    for (kind, label) in layers:
        out += pkt_layer(x, cy, w, h, kind, label)
        cy += h + gap
    if note:
        for ln in note:
            out += text(x, cy + 11, ln, size=10, color='dim')
            cy += 14
    return out, cy


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


# ===== Right-side pipeline step =====
def pipe_step(x, y, w, h, zone, who, verb_lines, layers, note_lines=None, arrow=None, arrow_color='accent'):
    """One step of the packet pipeline."""
    out = ''
    if zone == 'bnep':
        fill = 'bnep_zone_bg'
        bd = 'bnep_zone_bd'
        who_c = 'bnep_zone_tx'
        out += rect(x, y, w, h, fill=fill, stroke=bd, sw=1, rx=6)
        # subtle ring
        out += f'  <rect x="{x-2}" y="{y-2}" width="{w+4}" height="{h+4}" rx="8" fill="none" stroke="{C["bnep_zone_bd"]}" stroke-opacity="0.15" stroke-width="2"/>\n'
    elif zone == 'kernel':
        out += rect(x, y, w, h, fill='kernel_zone_bg', stroke='kernel_zone_bd', sw=1, rx=6)
        who_c = 'violet'
    else:
        out += rect(x, y, w, h, fill='soft', stroke='border', sw=1, rx=6)
        who_c = 'muted'

    # who line
    out += text(x + 10, y + 18, who, size=10, color=who_c, mono=True, spacing='0.04em', weight=700)
    # verb (allow up to 2 lines)
    cy = y + 36
    for ln in verb_lines[:2]:
        out += text(x + 10, cy, ln, size=11, color='text', weight=700)
        cy += 15

    # packet stack
    pk_y = cy + 4
    pk_x = x + 10
    pk_w = w - 20
    _stack, _ = packet_stack(pk_x, pk_y, pk_w, layers)
    out += _stack

    # notes below stack
    layers_h = len(layers) * 17
    nyy = pk_y + layers_h + 4
    if note_lines:
        for ln in note_lines:
            out += text(pk_x, nyy, ln, size=9.5, color='dim')
            nyy += 13

    # arrow on right
    if arrow == 'right':
        ac = C.get(arrow_color, C['accent'])
        ax = x + w + 4
        ay = y + h / 2
        out += f'  <text x="{ax}" y="{ay + 5}" font-size="18" fill="{ac}" font-weight="900" text-anchor="middle">▶</text>\n'
    elif arrow == 'left':
        ac = C.get(arrow_color, C['blue'])
        ax = x - 4
        ay = y + h / 2
        out += f'  <text x="{ax}" y="{ay + 5}" font-size="18" fill="{ac}" font-weight="900" text-anchor="middle">◀</text>\n'
    return out


# ============================================================
# SLIDE — BNEP one-pager
# ============================================================
def slide_bnep():
    out = svg_open() + bg()
    out += slide_header('01 / 01', '버즈가 쏜 패킷이 인터넷에 닿기까지 — BNEP의 까기와 다시 싸기', 'BNEP · PAN')

    out += lead([
        'BNEP는 통역사가 아니라 택배 포장 전문가다. L3(IP) 위는 한 번도 안 보고, 이더넷 프레임만 골라 BT 위에 싣는다.',
        '라우팅·NAT은 OS 커널이 한다.',
    ], y_start=112)

    # ===== Left column: 3 def cards =====
    left_x = 50
    left_w = 430
    top_y = 165

    # Card 1: BT 테더링이란?
    c1_y = top_y
    c1_h = 240
    out += rect(left_x, c1_y, left_w, c1_h, fill='soft', stroke='border', sw=1, rx=8)
    out += text(left_x + 14, c1_y + 24, 'BT 테더링이란?', size=14, color='text', weight=700)
    # key chip on right
    chip_text = 'PAN profile'
    chip_w = 12 + len(chip_text) * 6
    chip_x = left_x + left_w - 14 - chip_w
    out += f'  <rect x="{chip_x}" y="{c1_y + 12}" width="{chip_w}" height="16" rx="3" fill="#ffffff" stroke="{C["border"]}" stroke-width="1"/>\n'
    out += text(chip_x + chip_w/2, c1_y + 24, chip_text, size=10, color='muted', mono=True, anchor='middle', spacing='0.04em')
    # body
    body1 = [
        '폰/PC가 자기가 가진 인터넷 회선(LTE·Wi-Fi·이더넷 등)을',
        'BT 링크를 타고 옆 디바이스에 빌려주는 것.',
        '표준 이름은 Bluetooth PAN이고,',
        '빌려주는 쪽이 NAP, 빌려쓰는 쪽이 PANU.',
    ]
    cy = c1_y + 50
    for ln in body1:
        out += text(left_x + 14, cy, ln, size=12, color='dim')
        cy += 17
    # facts list
    cy += 8
    facts1 = [
        ('· ', '버즈 = PANU (UUID 0x1115)'),
        ('· ', '호스트 = NAP (UUID 0x1116)'),
        ('· ', '2003년 BT 1.1부터 표준, OS 빌트인 — 앱 설치 0'),
    ]
    for sym, txt in facts1:
        out += text(left_x + 16, cy, sym, size=12, color='accent', weight=900)
        out += text(left_x + 28, cy, txt, size=11.5, color='text')
        cy += 19

    # Card 2 (accent): BNEP가 정확히 뭘 하나
    c2_y = c1_y + c1_h + 12
    c2_h = 320
    out += rect(left_x, c2_y, left_w, c2_h, fill='accent_bg', stroke='accent_dim', sw=1, rx=8)
    out += text(left_x + 14, c2_y + 24, 'BNEP가 정확히 뭘 하나?', size=14, color='accent', weight=700)
    chip_text = 'L2CAP PSM 0x000F'
    chip_w = 12 + len(chip_text) * 6
    chip_x = left_x + left_w - 14 - chip_w
    out += f'  <rect x="{chip_x}" y="{c2_y + 12}" width="{chip_w}" height="16" rx="3" fill="#ffffff" stroke="{C["border"]}" stroke-width="1"/>\n'
    out += text(chip_x + chip_w/2, c2_y + 24, chip_text, size=10, color='muted', mono=True, anchor='middle', spacing='0.04em')
    body2 = [
        '이더넷 프레임을 BT L2CAP 채널에 캡슐화하는',
        '한 줄짜리 프로토콜.',
        '"OS의 가짜 NIC ↔ BT 라디오" 사이를 잇는 통역 어댑터다.',
    ]
    cy = c2_y + 50
    for ln in body2:
        out += text(left_x + 14, cy, ln, size=12, color='dim')
        cy += 17
    cy += 8
    facts2 = [
        '입력: DST MAC · SRC MAC · EtherType · payload',
        '출력: BNEP type(1B) · EtherType(2B) · payload',
        '두 피어만 있을 땐 MAC 12B 통째로 생략 → Type 0x02 압축',
        '옵션: NetTypeFilter(IPv4/ARP만 통과) — 펌웨어 RAM 절약',
        'BNEP는 IP를 모른다. 이더넷 페이로드는 안 까봄.',
    ]
    for txt in facts2:
        out += text(left_x + 16, cy, '·', size=12, color='accent', weight=900)
        wrapped = wrap_text(txt, 42)
        for j, wl in enumerate(wrapped[:2]):
            out += text(left_x + 28, cy + j * 16, wl, size=11.5, color='text')
        cy += 16 * min(len(wrapped), 2) + 6

    # Card 3: 왜 이게 중요한가
    c3_y = c2_y + c2_h + 12
    c3_h = 210
    out += rect(left_x, c3_y, left_w, c3_h, fill='soft', stroke='border', sw=1, rx=8)
    out += text(left_x + 14, c3_y + 24, '왜 이게 중요한가', size=14, color='text', weight=700)
    body3 = [
        'OS 커널은 BNEP 위에 떠 있는 가짜 NIC(bnep0)를',
        '그냥 LAN 카드로 인식한다.',
        '그 위에서 평소 쓰던 라우팅·NAT·iptables·TCP/IP가',
        '그대로 돈다.',
        '',
        '버즈가 보낸 mTLS 핸드셰이크가',
        '손도 안 대고 인터넷으로 나가는 이유.',
    ]
    cy = c3_y + 50
    for ln in body3:
        if ln == '':
            cy += 6
            continue
        out += text(left_x + 14, cy, ln, size=12, color='dim')
        cy += 18

    # ===== Right column: packet flow =====
    right_x = 500
    right_w = W - 50 - right_x  # 1370
    flow_top_y = 165

    # ---- OUTBOUND section ----
    out_y = flow_top_y
    out_h = 360
    out += rect(right_x, out_y, right_w, out_h, fill='bg', stroke='border', sw=1, rx=8)
    # left accent stripe
    out += rect(right_x, out_y, 4, out_h, fill='accent', rx=2)
    # head
    out += text(right_x + 18, out_y + 24, 'OUTBOUND', size=14, color='text', weight=700)
    out += text(right_x + 122, out_y + 24, '▶', size=14, color='accent', weight=900)
    out += text(right_x + 146, out_y + 24, '버즈 → 호스트 → 인터넷', size=14, color='text', weight=700)
    out += text(right_x + right_w - 18, out_y + 24, 'Buds emits Opus / mTLS / etc.', size=11, color='muted', mono=True, anchor='end')
    out += line(right_x + 14, out_y + 38, right_x + right_w - 14, out_y + 38, stroke='border', dash='4 3')

    # 5 pipe steps for outbound
    step_y = out_y + 50
    step_h = out_h - 60
    inner_pad = 14
    avail_w = right_w - 2 * inner_pad - 4 * 18  # 4 gaps of 18 + arrows
    step_w = (right_w - 2 * inner_pad - 4 * 16) / 5
    gap_x = 16
    sx = right_x + inner_pad

    out_steps = [
        # (zone, who, verb_lines, layers, note_lines)
        (None, '① BUDS APP / LWIP',
         ['앱이 TCP write →', 'lwIP가 L4·L3·L2까지 싼다'],
         [('eth', 'Eth (dst=Host, src=Buds)'),
          ('ip', 'IP (src=192.168.44.2)'),
          ('tcp', 'TCP / TLS'),
          ('payload', 'Opus payload')],
         None),
        ('bnep', '② BUDS BNEP (TX)',
         ['MAC 12B를 떼고 Type 0x02로', '압축, L2CAP에 실음'],
         [('l2cap', 'L2CAP (PSM=0x000F)'),
          ('bnep', 'BNEP type=0x02'),
          ('ghost', '— MAC 12B drop —'),
          ('ip', 'IP'),
          ('tcp', 'TCP / TLS'),
          ('payload', 'Opus')],
         None),
        ('bnep', '③ HOST BNEP (RX)',
         ['BNEP 헤더 떼고 MAC 12B 복원', '→ 완전한 이더넷 프레임'],
         [('eth', 'Eth (복원됨)'),
          ('ip', 'IP src=192.168.44.2'),
          ('tcp', 'TCP / TLS'),
          ('payload', 'Opus')],
         ['→ 가짜 NIC bnep0로 RX']),
        ('kernel', '④ HOST KERNEL · NAT',
         ['netfilter MASQUERADE — src', 'IP/port를 호스트 WAN으로 재작성'],
         [('eth', 'Eth (다음 hop MAC)'),
          ('ip', 'IP src=호스트 WAN'),
          ('tcp', 'TCP (port rewrite)'),
          ('payload', 'Opus')],
         ['→ wlan0 / rmnet0으로 routing']),
        (None, '⑤ WAN PHY',
         ['Wi-Fi(802.11) 또는 LTE', '(PDCP/RLC/MAC)로 송출'],
         [('wifi', '802.11 /'),
          ('lte', 'LTE PDCP·RLC·MAC'),
          ('ip', 'IP src=WAN'),
          ('tcp', 'TCP / TLS'),
          ('payload', 'Opus → 인터넷')],
         None),
    ]

    cx = sx
    for i, (zone, who, verb, layers, notes) in enumerate(out_steps):
        out += pipe_step(cx, step_y, step_w, step_h, zone, who, verb, layers, notes,
                          arrow='right' if i < 4 else None, arrow_color='accent')
        cx += step_w + gap_x

    # ---- INBOUND section ----
    in_y = out_y + out_h + 18
    in_h = 360
    out += rect(right_x, in_y, right_w, in_h, fill='bg', stroke='border', sw=1, rx=8)
    out += rect(right_x, in_y, 4, in_h, fill='blue', rx=2)
    out += text(right_x + 18, in_y + 24, 'INBOUND', size=14, color='text', weight=700)
    out += text(right_x + 105, in_y + 24, '◀', size=14, color='blue', weight=900)
    out += text(right_x + 128, in_y + 24, '인터넷 → 호스트 → 버즈', size=14, color='text', weight=700)
    out += text(right_x + right_w - 18, in_y + 24, '서버 응답 / 푸시 등', size=11, color='muted', mono=True, anchor='end')
    out += line(right_x + 14, in_y + 38, right_x + right_w - 14, in_y + 38, stroke='border', dash='4 3')

    in_step_y = in_y + 50
    in_step_h = in_h - 60

    in_steps = [
        (None, '① WAN PHY',
         ['호스트 WAN IP로 도착,', '커널이 받음'],
         [('wifi', '802.11 /'),
          ('lte', 'LTE'),
          ('ip', 'IP dst=호스트 WAN'),
          ('tcp', 'TCP / TLS'),
          ('payload', 'server payload')],
         None),
        ('kernel', '② HOST KERNEL · 역 NAT',
         ['conntrack이 dst IP/port를', 'PANU(버즈)로 되돌림'],
         [('ip', 'IP dst=192.168.44.2'),
          ('tcp', 'TCP (원래 port)'),
          ('payload', 'server payload')],
         ['→ bnep0로 routing']),
        ('bnep', '③ HOST BNEP (TX)',
         ['이더넷 프레임 만들어 압축', '→ BNEP·L2CAP에 싣음'],
         [('l2cap', 'L2CAP (PSM=0x000F)'),
          ('bnep', 'BNEP type=0x02'),
          ('ghost', '— MAC 12B drop —'),
          ('ip', 'IP dst=Buds'),
          ('tcp', 'TCP / TLS'),
          ('payload', 'server payload')],
         None),
        ('bnep', '④ BUDS BNEP (RX)',
         ['L2CAP·BNEP 헤더 제거,', 'MAC 12B 복원, lwIP에 enqueue'],
         [('eth', 'Eth (복원됨)'),
          ('ip', 'IP dst=Buds'),
          ('tcp', 'TCP / TLS'),
          ('payload', 'server payload')],
         None),
        (None, '⑤ BUDS APP / LWIP',
         ['L3·L4 디캡 → 소켓 read로', '앱에 도달'],
         [('ghost', 'Eth'),
          ('ghost', 'IP'),
          ('ghost', 'TCP / TLS'),
          ('payload', 'server payload')],
         ['앱은 BT 위에 있다는', '사실을 모름']),
    ]

    cx = sx
    for i, (zone, who, verb, layers, notes) in enumerate(in_steps):
        out += pipe_step(cx, in_step_y, step_w, in_step_h, zone, who, verb, layers, notes,
                          arrow='right' if i < 4 else None, arrow_color='blue')
        cx += step_w + gap_x

    # ===== Bottom TL;DR callout =====
    tl_y = in_y + in_h + 18
    tl_h = 100
    out += rect(50, tl_y, W - 100, tl_h, fill='accent_bg', stroke='accent_dim', sw=1, rx=8)
    out += rect(50, tl_y, 4, tl_h, fill='accent', rx=2)
    out += text(70, tl_y + 26, 'TL;DR', size=14, color='accent', weight=700)
    tl_lines = [
        'BNEP는 L2(이더넷) 캡슐화만 한다. 헤더 떼고(MAC 12B drop) 다시 붙이는 게 전부. 라우팅·NAT·TCP는 호스트 OS 커널이 평소처럼 처리한다.',
        '그래서 버즈 코드는 "어디로 가는지" 신경 안 써도 되고, 호스트는 BT인지 LAN인지 구분 없이 같은 iptables 룰을 쓴다.',
        '이게 BudsAI가 앱 설치 0 · 호스트 무관 · 종단 mTLS를 동시에 가질 수 있는 이유다.',
    ]
    cy = tl_y + 48
    for ln in tl_lines:
        out += text(140, cy, ln, size=12.5, color='#064e3b')
        cy += 18

    # ===== Footer =====
    out += text(50, H - 22, 'BudsAI Design Doc · BNEP one-pager', size=10, color='muted', mono=True, spacing='0.04em')
    out += text(W - 50, H - 22, 'APPENDIX · BNEP ONE-PAGER', size=10, color='accent', mono=True, spacing='0.08em', anchor='end')

    return out + svg_close()


# ============================================================
if __name__ == '__main__':
    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))
    content = slide_bnep()
    path = os.path.join(out_dir, 'bnep-slide.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'wrote {path} ({len(content)} bytes)')
