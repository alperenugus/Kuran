# Kur'ân-ı Kerîm — Diyanet mushaf text (JSON + PDF)

The full Qur'an in the **Turkish print orthography of the Diyanet İşleri Başkanlığı mushaf**, as structured, open JSON data: by sûre, by page, and by cüz. It comes with a page-for-page PDF.

**Türkçe özet:** Diyanet İşleri Başkanlığı'nın Türkiye'de basılan mushafıyla aynı imladaki Kur'an metni: esre-i memdude, med, cezm, secâvend ve sessiz harf işaretleri basılı mushaftaki gibidir. Veriler sûre, sayfa ve cüz bazında JSON olarak sunulur. `Kuran.pdf`, Diyanet mushafının sayfa düzenini sayfa sayfa takip eder. Lisans: CC BY 4.0.

## Why this dataset

Most open Qur'an datasets (Tanzil, quran.com, …) use the **Arab/Medina orthography**, for example الْحَمْدُ, إِنَّ, الرَّحِيمِ, إِسْرَائِيلَ and Medina waqf marks. Mushafs printed in Türkiye use a different orthography:

| | Arab orthography (Tanzil) | Turkish print (this dataset) |
|---|---|---|
| Hareke on the bare elif | الْحَمْدُ, إِنَّ | اَلْحَمْدُ, اِنَّ |
| Long î (esre-i memdude) | الرَّحِيمِ | الرَّح۪يمِ |
| Final yâ | يِ with dots | dotless ى |
| Pause marks | ۖ ۗ ۚ | secâvend ط ج ز ص ع لا |
| Silent letters | — | small circle (اُو۫فِ) |
| Hamza | يَأْمُرُكُمْ, إِسْرَائِيلَ | يَاْمُرُكُمْ, اِسْرَٓائٖلَ |

The text is Diyanet's own mushaf page data (`kuran.diyanet.gov.tr/mushaf`). It was checked against Diyanet's printed *Bilgisayar Hatlı* mushaf and matches it spelling for spelling.

## Files

| Path | Contents |
|---|---|
| `kuran.json` | Everything: 114 sûres with metadata and all 6,236 ayahs |
| `surahs.json` | Sûre index |
| `by_surah/001.json` … `114.json` | One sûre per file |
| `by_page/001.json` … `605.json` | One page per file (Diyanet's page layout) |
| `by_juz/01.json` … `30.json` | One cüz per file |
| `Kuran.pdf` | The whole mushaf, page for page |
| `source/diyanet_mushaf.json` | The Diyanet page data everything is built from |
| `scripts/build.py` | Rebuilds all JSON from `source/` |
| `scripts/make_pdf.py` | Rebuilds `Kuran.pdf` (needs Google Chrome) |

### Ayah

```json
{
  "ayah": 7,
  "page": 3,
  "printed_page": 2,
  "juz": 1,
  "text": "خَتَمَ اللّٰهُ عَلٰى قُلُوبِهِمْ وَعَلٰى سَمْعِهِمْۜ وَعَلٰٓى اَبْصَارِهِمْ غِشَاوَةٌۘ وَلَهُمْ عَذَابٌ عَظ۪يمٌ۟",
  "text_unicode": "خَتَمَ اللّٰهُ عَلٰى قُلُوبِهِمْ وَعَلٰى سَمْعِهِمْؕ وَعَلٰٓى اَبْصَارِهِمْ غِشَاوَةٌؗ وَلَهُمْ عَذَابٌ عَظٖیمٌࣖ"
}
```

(`by_page` and `by_juz` entries also carry `surah`.)

- **`page`**: the page in Diyanet's online mushaf (1–605).
- **`printed_page`**: the number printed in the Diyanet mushaf (1–604). The print counts its decorated opening spread (Fâtiha + Bakara 1–5, online pages 1–2) as page 1.
- **`juz`**: cüz 1–30. Turkish mushafs start every cüz at the top of a page, so four cüz begin one ayah away from the Arab convention (cüz 4 starts at 3:92, 7 at 5:83, 11 at 9:94, 26 at 45:33).

### `text` vs `text_unicode`: pick the one that matches your font

Diyanet encodes the same marks with **different Unicode codepoints depending on the font**:

| Mark | `text_unicode` (standard Unicode) | `text` (Shaikh Hamdullah encoding) |
|---|---|---|
| esre-i memdude | U+0656 | U+06EA |
| secâvend ط | U+0615 | U+06DC |
| secâvend ز | U+0617 | U+06D8 |
| secâvend ع | U+08D6 | U+06DF |
| secâvend ص | U+08D5 | U+06D6 |
| silent-letter circle | U+08D1 / U+08D2 | U+06EC / U+06EB |
| yâ | U+06CC (dotless when final) | U+064A |

- **`text`** is for the **Shaikh Hamdullah Mushaf** font, which Diyanet distributes as [`KuranKerimFontHamdullah.ttf`](https://webdosya.diyanet.gov.tr/kuran/kuranikerim/dosyalar/font/KuranKerimFontHamdullah.ttf) on [kuran.diyanet.gov.tr/Yayinlar](https://kuran.diyanet.gov.tr/Yayinlar). That font has no glyph for U+0656 and draws empty boxes on the standard-Unicode text.
- **`text_unicode`** is for full-Unicode Qur'an fonts such as **Scheherazade New** (SIL OFL), and for copy/paste. Scheherazade reads U+06DC literally, as a small س.
- Tested and **not recommended**: Amiri, Noto Sans Arabic and system fonts. They lack the silent-letter circles and misplace the Turkish marks.

The kashida (U+0640) that Diyanet inserts to justify its page layout has been removed.

### Sûre

```json
{
  "number": 18, "name_turkish": "Kehf", "name_arabic": "الْكَهْفِ",
  "name_transliteration": "Al-Kahf", "revelation_place": "meccan", "revelation_order": 69,
  "ayah_count": 110, "first_page": 293, "first_printed_page": 292, "juz": 15, "besmele": true
}
```

`besmele` means the Besmele is printed above the sûre. It is `false` for Tevbe, and for Fâtiha, whose first ayah is the Besmele.

## Kuran.pdf

`Kuran.pdf` has 605 pages. Each page holds exactly the ayahs that Diyanet's mushaf puts on that page: sûre headers and Besmele where they are printed, cüz in the running header, and the printed page number in the footer. It is set in Diyanet's Shaikh Hamdullah Mushaf font.

Diyanet publishes no line-level data, so **line breaks within a page are made by the typesetter**. The text size is fitted so each page fills its frame the way a printed page does, which is about 15 lines. Line breaks are therefore close to the print but not identical.

## Usage

```python
import json
page = json.load(open("by_page/007.json", encoding="utf-8"))
for a in page["ayahs"]:
    print(a["surah"], a["ayah"], a["text_unicode"])
```

```javascript
const kuran = require("./kuran.json");
const kehf = kuran.surahs[17];
console.log(kehf.name_turkish, kehf.ayahs[0].text);
```

## Rebuilding

```bash
python3 scripts/build.py      # JSON from source/diyanet_mushaf.json
python3 scripts/make_pdf.py   # Kuran.pdf (downloads Diyanet's Hamdullah font at build time)
```

## Sources and attribution

- **Qur'an text, page and cüz layout, sûre names:** Diyanet İşleri Başkanlığı, [kuran.diyanet.gov.tr/mushaf](https://kuran.diyanet.gov.tr/mushaf), fetched 2026-09-26.
- **Checked against:** Diyanet's printed mushaf, *Kur'an-ı Kerim (Bilgisayar Hatlı)*, from [kuran.diyanet.gov.tr/Yayinlar](https://kuran.diyanet.gov.tr/Yayinlar).
- **Mapping between the two encodings:** derived by aligning the page data with Diyanet's Hamdullah-encoded Word edition (`kuran.docx`, same page).
- **Transliterated sûre names and revelation place:** Tanzil.net metadata (CC BY).

## License

The dataset structure, encodings, scripts and PDF layout are released under **[CC BY 4.0](LICENSE)**; please credit this repository and Diyanet İşleri Başkanlığı as the source of the text. The Qur'an text itself is Allah's word. This repository only provides a faithful digital form of Diyanet's mushaf orthography.

Please report any discrepancy with the printed Diyanet mushaf as an issue, with the sûre:ayah and the printed page.

---

See also: [Cevsen](https://github.com/alperenugus/Cevsen), the Cevşen-i Kebir dataset.
