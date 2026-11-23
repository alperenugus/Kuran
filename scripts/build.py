# -*- coding: utf-8 -*-
"""Build every data file in this repo from source/diyanet_mushaf.json.

    python3 scripts/build.py

Outputs (all UTF-8 JSON):
  kuran.json            full Qur'an: surah metadata + every ayah
  surahs.json           surah index (names, revelation, ayah count, first page, cüz)
  by_surah/001..114.json
  by_page/001..605.json Diyanet mushaf pages, one file per page of Diyanet's online
                        mushaf (kuran.diyanet.gov.tr/mushaf); each also carries
                        `printed_page`, the number printed in the Diyanet mushaf
  by_juz/01..30.json

Each ayah carries its text in two encodings of the same letters:
  text          codepoints the "Shaikh Hamdullah Mushaf" font draws
                (Diyanet's own encoding for that font, e.g. esre-i memdude U+06EA)
  text_unicode  standard Unicode (esre-i memdude U+0656, secâvend ط U+0615,
                dotless final yâ U+06CC, silent-letter circles U+08D1/U+08D2)
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diyanet page data (standard Unicode) -> the codepoints Shaikh Hamdullah draws.
# Derived by aligning the page data against Diyanet's own Hamdullah-encoded Word
# edition (kuran.diyanet.gov.tr/Content/dosyalar/kuran.docx).
TO_HAMDULLAH = {
    "ی": "ي",  # Farsi yeh -> yeh (the font draws final yeh dotless)
    "ٖ": "۪",  # esre-i memdude
    "ؕ": "ۜ",  # secâvend ط (mutlak)
    "ؗ": "ۘ",  # secâvend ز (mücevvez)
    "ࣕ": "ۖ",  # secâvend ص (murahhas)
    "ࣖ": "۟",  # secâvend ع
    "ࣗ": "ۗ",  # secâvend ق
    "ࣞ": "۠",  # secâvend قف
    "ۘ": "ۢ",  # small meem (iqlab)
    "ࣙ": "ۨ",  # small low noon
    "࣑": "۬",  # silent-letter circle
    "࣒": "۫",  # silent-letter circle (filled)
}


# Secde (prostration) ayahs as marked in the Diyanet mushaf — the 14 of the
# Hanafi school. 22:77 (a Shafi'i sajda, listed by Tanzil) carries no secde mark
# in the Diyanet print (printed page 340), so it is not included.
SAJDA = {(7, 206), (13, 15), (16, 50), (17, 109), (19, 58), (22, 18), (25, 60),
         (27, 26), (32, 15), (38, 24), (41, 38), (53, 62), (84, 21), (96, 19)}


def to_unicode(t):
    """Hamdullah-encoded (Diyanet sûre names) -> standard Unicode."""
    return t.replace("\u06EA", "\u0656")


def printed_page(page):
    """The printed mushaf treats its decorated opening spread (Fâtiha + Bakara 1-5,
    online pages 1-2) as page 1 and numbers on from there, so it has 604 pages."""
    return 1 if page <= 2 else page - 1


# Where Diyanet's page data differs from the printed mushaf (Kur'ân-ı Kerîm, Rahle
# Boy, Hat: Bilgisayar, 5. Baskı 2018, ISBN 978-975-19-5752-8), the print wins.
# (surah, ayah) -> [(as in the page data after clean(), as printed)]
CORRECTIONS = {
    # secâvend
    (2, 259): [("یَتَسَنَّهْۚ", "یَتَسَنَّهْؕ")],             # ج -> ط
    (4, 79): [("اللّٰهِۘ", "اللّٰهِؗ")],                        # م -> ز
    (4, 118): [("اللّٰهُؗ", "اللّٰهُۘ")],                       # ز -> م
    (11, 46): [("صَالِحٍࣗ", "صَالِحٍؗ")],                      # ق -> ز
    (60, 4): [("اللّٰهِۘ", "اللّٰهِؗ")],                        # م -> ز
    (14, 44): [("الْعَذَابُ ", "الْعَذَابُۙ ")],                # لا added
    (7, 44): [("الظَّالِمٖینَۙ", "الظَّالِمٖینَ")],            # لا removed
    (34, 34): [("مُتْرَفُوهَٓاۙ", "مُتْرَفُوهَٓا")],            # لا removed
    (56, 94): [("جَحٖیمٍۙ", "جَحٖیمٍ")],                        # لا removed
    # 48:5: لا added after عَظٖیمًا; hamza on its own seat in سَیِّـَٔاتِهِمْ
    (48, 5): [("عَظٖیمًا", "عَظٖیمًاۙ"), ("سَیِّئَات", "سَیِّـَٔات")],
    # silent-letter (kasr) circle
    (16, 90): [("وَاٖیتَٓائِ", "وَاٖیتَٓائِ࣑")],
    (38, 21): [("نَبَؤُا", "نَبَؤُ࣑ا")],
    (20, 94): [("یَبْنَؤُ࣑مَّ", "یَبْنَؤُمَّ")],
    # hamza printed on the elif
    (5, 29): [("تَبُٓواَ", "تَبُٓوأَ")],
    (10, 88): [("وَمَلَاَهُ", "وَمَلَأَهُ")],
    (12, 43): [("الْمَلَاُ", "الْمَلَأُ")],
    (15, 26): [("حَمَاٍ", "حَمَأٍ")],
    (15, 28): [("حَمَاٍ", "حَمَأٍ")],
    (15, 33): [("حَمَاٍ", "حَمَأٍ")],
    (16, 5): [("تَاْكُلُونَ", "تَأْكُلُونَ")],
    (28, 76): [("لَتَنُٓواُ", "لَتَنُٓوأُ")],
    # printed without a hamza: the elif carries the tenvin
    (12, 31): [("مُتَّكَـًٔا", "مُتَّكَاً")],
    (73, 6): [("وَطْـًٔا", "وَطْاً")],
    # 7:196: one yâ (shedde on the seat), not two
    (7, 196): [("وَلِيِّىَ", "وَلِـِّیَ")],
    # 104:2: small nûn (nûn-ı kasra) printed under the elif
    (104, 2): [("اَلَّذٖی", "اَࣙلَّذٖی")],
}


def clean(t):
    """Drop the page-justification kashida and normalise spaces. A kashida that
    carries a mark (the hamza seat in شَیْـًٔا, خَاسِـٖٔینَ, ...) is a letter
    form, not justification: one is kept."""
    t = re.sub(r"ـ+(?=[ً-ٟ])", "ـ", t)
    t = re.sub(r"ـ(?![ً-ٟ])", "", t)
    t = t.replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def correct(ref, t):
    for old, new in CORRECTIONS.get(ref, []):
        assert t.count(old) == 1, (ref, old, t.count(old))
        t = t.replace(old, new)
    return t


def to_hamdullah(t):
    return "".join(TO_HAMDULLAH.get(c, c) for c in t)


def dump(obj, *path):
    p = os.path.join(ROOT, *path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    src = json.load(open(os.path.join(ROOT, "source", "diyanet_mushaf.json"), encoding="utf-8"))

    ayahs = []  # flat, in mushaf order
    for p in src["pages"]:
        juz = min(p["cuz"], 30)  # Diyanet labels pages 602-605 "31"; they belong to cüz 30
        for a in p["ayahs"]:
            u = correct((a["surah"], a["ayah"]), clean(a["text"]))
            ayahs.append({"surah": a["surah"], "ayah": a["ayah"], "page": p["page"],
                          "printed_page": printed_page(p["page"]), "juz": juz,
                          "sajda": (a["surah"], a["ayah"]) in SAJDA,
                          "text": to_hamdullah(u), "text_unicode": u})
    assert len(ayahs) == 6236, len(ayahs)
    assert len({(a["surah"], a["ayah"]) for a in ayahs}) == 6236

    surahs = []
    for s in src["surahs"]:
        mine = [a for a in ayahs if a["surah"] == s["surah"]]
        assert len(mine) == s["ayah_count"], s["surah"]
        surahs.append({
            "number": s["surah"],
            "name_turkish": s["name_turkish"],
            "name_arabic": s["name_arabic"],
            "name_arabic_unicode": to_unicode(s["name_arabic"]),
            "name_transliteration": s["transliteration"],
            "revelation_place": s["revelation_place"],
            "revelation_order": s["revelation_order"],
            "ayah_count": s["ayah_count"],
            "first_page": mine[0]["page"],
            "first_printed_page": mine[0]["printed_page"],
            "juz": mine[0]["juz"],
            "besmele": s["besmele"],
        })

    def strip(a, *drop):
        return {k: v for k, v in a.items() if k not in drop}

    full = []
    for s in surahs:
        n = s["number"]
        entry = dict(s, ayahs=[strip(a, "surah") for a in ayahs if a["surah"] == n])
        full.append(entry)
        dump(entry, "by_surah", f"{n:03d}.json")
    meta = {"title": "Kur'ân-ı Kerîm — Diyanet mushaf text",
            "source": "Diyanet İşleri Başkanlığı, kuran.diyanet.gov.tr/mushaf",
            "license": "CC BY 4.0", "surah_count": 114, "ayah_count": 6236,
            "page_count": src["pages"][-1]["page"],
            "printed_page_count": printed_page(src["pages"][-1]["page"]), "juz_count": 30}
    dump(dict(meta, surahs=full), "kuran.json")
    dump(surahs, "surahs.json")

    for p in src["pages"]:
        n = p["page"]
        dump({"page": n, "printed_page": printed_page(n), "juz": min(p["cuz"], 30),
              "ayahs": [strip(a, "page", "printed_page", "juz") for a in ayahs if a["page"] == n]},
             "by_page", f"{n:03d}.json")
    for j in range(1, 31):
        mine = [a for a in ayahs if a["juz"] == j]
        dump({"juz": j, "first_page": mine[0]["page"], "last_page": mine[-1]["page"],
              "ayahs": [strip(a, "juz") for a in mine]}, "by_juz", f"{j:02d}.json")
    print(f"built {len(surahs)} surahs, {len(ayahs)} ayahs, {len(src['pages'])} pages, 30 juz")


if __name__ == "__main__":
    main()
