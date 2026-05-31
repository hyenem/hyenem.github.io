// arch-deck.html → Figma에서 완전 편집 가능한 네이티브 SVG (텍스트=<text>, 박스=<rect>)
// 실행: node _export_arch_svgs.js   (필요: npm i puppeteer-core, 시스템 Chrome)
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const HERE = __dirname;
const URL = 'file://' + path.join(HERE, 'arch-deck.html');

// ── 페이지 안에서 실행되는 직렬화기 ──────────────────────────────
function inPageSerialize() {
  const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
                    .replace(/"/g,'&quot;');
  const isMono = fam => /mono/i.test(fam);
  const famOut = fam => isMono(fam)
      ? "'JetBrains Mono', ui-monospace, monospace"
      : "Pretendard, 'Apple SD Gothic Neo', sans-serif";
  // rgba(...) → {fill, op}
  function col(c) {
    if (!c) return null;
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return {fill: c, op: 1};
    const p = m[1].split(',').map(s => parseFloat(s));
    const a = p.length > 3 ? p[3] : 1;
    if (a === 0) return null;
    return {fill: `rgb(${p[0]|0}, ${p[1]|0}, ${p[2]|0})`, op: a};
  }
  function gradColor(bgImg) { // 그라데이션 → 대표색 1개 근사
    const m = bgImg.match(/rgba?\([^)]+\)/);
    return m ? col(m[0]) : null;
  }

  function rectFor(el, b, OX, OY) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return '';
    if (b.width < 0.5 || b.height < 0.5) return '';
    const bg = col(cs.backgroundColor);
    let fill = bg;
    if (!fill && cs.backgroundImage && cs.backgroundImage !== 'none') fill = gradColor(cs.backgroundImage);
    const bw = parseFloat(cs.borderTopWidth) || 0;
    const bc = bw > 0 ? col(cs.borderTopColor) : null;
    if (!fill && !bc) return '';
    const x = (b.left - OX), y = (b.top - OY), w = b.width, h = b.height;
    let rx = parseFloat(cs.borderTopLeftRadius) || 0;
    if (/50%/.test(cs.borderTopLeftRadius)) rx = Math.min(w, h) / 2;
    let a = `x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}"`;
    if (rx) a += ` rx="${rx.toFixed(1)}"`;
    a += ` fill="${fill ? fill.fill : 'none'}"`;
    if (fill && fill.op < 1) a += ` fill-opacity="${fill.op.toFixed(2)}"`;
    if (bc) { a += ` stroke="${bc.fill}" stroke-width="${bw.toFixed(1)}"`; if (bc.op < 1) a += ` stroke-opacity="${bc.op.toFixed(2)}"`; }
    return `<rect ${a}/>`;
  }

  function textFor(node, el, OX, OY) {
    const cs = getComputedStyle(el);
    const fs = parseFloat(cs.fontSize);
    const fw = cs.fontWeight;
    const c = col(cs.color) || {fill:'#16263F', op:1};
    const fam = famOut(cs.fontFamily);
    const ls = cs.letterSpacing && cs.letterSpacing !== 'normal' ? parseFloat(cs.letterSpacing) : 0;
    const data = node.data;
    const range = document.createRange();
    const lines = [];
    let cur = null;
    for (let i = 0; i < data.length; i++) {
      range.setStart(node, i); range.setEnd(node, i + 1);
      const rs = range.getClientRects();
      if (!rs.length) { if (cur) cur.text += data[i]; continue; }
      const r = rs[rs.length - 1];
      if (r.width === 0 && r.height === 0) { if (cur) cur.text += data[i]; continue; }
      if (cur && Math.abs(r.top - cur.top) < 2) {
        cur.text += data[i]; cur.left = Math.min(cur.left, r.left);
        cur.top = Math.min(cur.top, r.top); cur.bottom = Math.max(cur.bottom, r.bottom);
      } else {
        if (cur) lines.push(cur);
        cur = {top: r.top, bottom: r.bottom, left: r.left, text: data[i]};
      }
    }
    if (cur) lines.push(cur);
    const out = [];
    for (const L of lines) {
      const t = L.text.replace(/\s+$/,'');           // 줄 끝 공백 제거
      const tl = t.replace(/^\s+/,'');                // 앞 공백 제거하되 x 보정
      if (!tl) continue;
      const lead = t.length - tl.length;
      const x = (L.left - OX) + lead * fs * 0.5;      // 앞 공백 대략 보정
      const lh = L.bottom - L.top;
      const y = (L.top - OY) + (lh - fs) / 2 + fs * 0.79;  // 베이스라인 근사
      let a = `x="${x.toFixed(1)}" y="${y.toFixed(1)}" font-size="${fs.toFixed(1)}"`
            + ` font-weight="${fw}" fill="${c.fill}" font-family="${fam}"`;
      if (ls) a += ` letter-spacing="${ls.toFixed(2)}"`;
      if (c.op < 1) a += ` fill-opacity="${c.op.toFixed(2)}"`;
      out.push(`<text ${a} xml:space="preserve">${esc(tl)}</text>`);
    }
    return out.join('\n');
  }

  function exportSlide(slide) {
    const b0 = slide.getBoundingClientRect();
    const OX = b0.left, OY = b0.top;
    const parts = [];
    parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">`);
    // 배경 + 모든 박스(rect) — DOM 순서대로(자식이 부모 위에 칠해짐)
    parts.push(rectFor(slide, b0, OX, OY));
    const all = slide.querySelectorAll('*');
    all.forEach(el => { const r = rectFor(el, el.getBoundingClientRect(), OX, OY); if (r) parts.push(r); });
    // 텍스트는 박스 위에
    const walk = el => {
      el.childNodes.forEach(n => {
        if (n.nodeType === 3 && n.textContent.trim()) {
          const t = textFor(n, el, OX, OY); if (t) parts.push(t);
        }
      });
    };
    walk(slide); all.forEach(walk);
    parts.push('</svg>');
    return parts.filter(Boolean).join('\n');
  }

  return [...document.querySelectorAll('.slide')].map(exportSlide);
}

(async () => {
  const browser = await puppeteer.launch({executablePath: CHROME, headless: 'new',
    args: ['--no-sandbox', '--font-render-hinting=none']});
  const page = await browser.newPage();
  await page.setViewport({width: 1920, height: 1200, deviceScaleFactor: 1});
  await page.goto(URL, {waitUntil: 'networkidle0', timeout: 60000});
  await page.evaluate(async () => { await document.fonts.ready; });
  await new Promise(r => setTimeout(r, 400));
  const svgs = await page.evaluate(inPageSerialize);
  svgs.forEach((svg, i) => {
    const fn = path.join(HERE, `arch-deck-${String(i + 1).padStart(2, '0')}.svg`);
    fs.writeFileSync(fn, svg, 'utf-8');
    console.log('wrote', path.basename(fn), (svg.length / 1024 | 0) + 'KB');
  });
  await browser.close();
  console.log('done:', svgs.length, 'editable SVGs');
})();
