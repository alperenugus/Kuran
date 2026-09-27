# -*- coding: utf-8 -*-
"""Render Kuran.pdf: one PDF page per Diyanet mushaf page (605 pages; the footer
shows the number printed in the mushaf, 1-604 — the opening spread is unnumbered), each
holding exactly the ayahs Diyanet prints on that page, set in Diyanet's
"Shaikh Hamdullah Mushaf" font (KuranKerimFontHamdullah.ttf, downloaded from
Diyanet at build time — it is not redistributed here).

    python3 scripts/make_pdf.py        # needs Google Chrome

Line breaks inside a page are made by the typesetter, not copied from the print
(Diyanet publishes no line data); the text size is fitted per page so every page
fills its frame the way a printed mushaf page does (~15 lines).
"""
import html, json, os, subprocess, tempfile, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_URL = "https://webdosya.diyanet.gov.tr/kuran/kuranikerim/dosyalar/font/KuranKerimFontHamdullah.ttf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
BESMELE = "بِسْمِ اللّٰهِ الرَّحْمٰنِ الرَّح۪يمِ"
e = html.escape


def font_path():
    p = os.path.join(tempfile.gettempdir(), "KuranKerimFontHamdullah.ttf")
    if not os.path.exists(p):
        req = urllib.request.Request(FONT_URL, headers={"User-Agent": "Mozilla/5.0"})
        open(p, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    return p


CSS = """
@font-face { font-family: Mushaf; src: url("%(font)s"); }
@page { size: 148mm 210mm; margin: 0; }
html, body { margin: 0; padding: 0; background: #fff; }
.page { width: 148mm; height: 210mm; box-sizing: border-box; padding: 9mm 10mm 8mm;
        page-break-after: always; display: flex; flex-direction: column; font-family: Mushaf; color: #1b1a17; }
.run { display: flex; justify-content: space-between; direction: rtl; font-size: 11pt; color: #5b5140;
       height: 7mm; align-items: flex-end; padding: 0 1mm 1mm; }
.frame { flex: 1; border: 1.6pt solid #8a7440; outline: 0.5pt solid #8a7440; outline-offset: 1.2mm;
         margin: 1.4mm; padding: 2.5mm 3.2mm; overflow: hidden; display: flex; flex-direction: column; }
.body { direction: rtl; line-height: 1.95; }
.body.short { margin: auto 0; }
.seg { text-align: justify; text-align-last: center; }
.seg.last { text-align-last: justify; }
.head { border: 1pt solid #8a7440; background: #f6f0de; border-radius: 1.2mm; text-align: center;
        color: #14624F; line-height: 1.7; margin: 0.25em 0; }
.bes { text-align: center; }
.n { color: #8a7440; white-space: nowrap; }
.foot { text-align: center; font-size: 11pt; color: #5b5140; height: 5mm; }
"""

# Fit each page's text to its frame (binary search on font size), then clamp
# pages with little text to the typical size so they don't balloon.
JS = """
function fits(b, f) { return b.scrollHeight <= f.clientHeight + 0.5; }
const pages = [...document.querySelectorAll('.page')];
const sizes = [];
for (const p of pages) {
  const f = p.querySelector('.frame'), b = p.querySelector('.body');
  let lo = 8, hi = 40;
  for (let i = 0; i < 18; i++) { const m = (lo + hi) / 2; b.style.fontSize = m + 'px'; fits(b, f) ? lo = m : hi = m; }
  b.style.fontSize = lo + 'px'; sizes.push(lo);
}
const sorted = [...sizes].sort((a, b) => a - b), med = sorted[Math.floor(sorted.length / 2)];
pages.forEach((p, i) => {
  if (sizes[i] > med * 1.12) {
    const b = p.querySelector('.body'); b.style.fontSize = (med * 1.12) + 'px'; b.classList.add('short');
    b.querySelectorAll('.seg.last').forEach(x => x.classList.remove('last'));  // short page: no stretched line
  }
});
document.body.setAttribute('data-done', '1');
"""


def main():
    surahs = {s["number"]: s for s in json.load(open(os.path.join(ROOT, "surahs.json"), encoding="utf-8"))}
    pages_html = []
    n_pages = len(os.listdir(os.path.join(ROOT, "by_page")))
    for n in range(1, n_pages + 1):
        page = json.load(open(os.path.join(ROOT, "by_page", f"{n:03d}.json"), encoding="utf-8"))
        ayahs = page["ayahs"]
        # group consecutive ayahs by surah; a surah starting here gets its header
        segs = []
        for a in ayahs:
            if not segs or segs[-1][0] != a["surah"]:
                segs.append((a["surah"], []))
            segs[-1][1].append(a)
        body = []
        for i, (sid, items) in enumerate(segs):
            s = surahs[sid]
            if items[0]["ayah"] == 1:
                body.append(f'<div class="head">سُورَةُ {e(s["name_arabic"])}</div>')
                if s["besmele"]:
                    body.append(f'<div class="bes">{BESMELE}</div>')
            text = " ".join(f'{e(a["text"])}&nbsp;<span class="n">﴿{str(a["ayah"]).translate(AR)}﴾</span>'
                            for a in items)
            # Like the print: the page's last line is stretched full-width only when
            # the surah runs on to the next page; a line that ends a surah is centered.
            runs_on = items[-1]["ayah"] < s["ayah_count"]
            cls = "seg last" if i == len(segs) - 1 and runs_on else "seg"
            body.append(f'<div class="{cls}">{text}</div>')
        first = surahs[segs[0][0]]
        pages_html.append(
            f'<div class="page"><div class="run"><span>سُورَةُ {e(first["name_arabic"])}</span>'
            f'<span>اَلْجُزْءُ {str(page["juz"]).translate(AR)}</span></div>'
            f'<div class="frame"><div class="body">{"".join(body)}</div></div>'
            f'<div class="foot">{"" if n <= 2 else str(page["printed_page"]).translate(AR)}</div></div>')

    doc = (f'<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>{CSS % {"font": "file://" + font_path()}}</style></head>'
           f'<body>{"".join(pages_html)}<script>document.fonts.ready.then(() => {{ {JS} }});</script></body></html>')
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(doc)
    out = os.path.join(ROOT, "Kuran.pdf")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--allow-file-access-from-files",
                    "--no-pdf-header-footer", "--virtual-time-budget=120000",
                    f"--print-to-pdf={out}", "file://" + f.name], check=True, capture_output=True)
    os.unlink(f.name)
    print("wrote", out)


if __name__ == "__main__":
    main()
