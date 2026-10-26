# Images to EPUB

Turn photos or scans of book pages into a **Fixed-Layout EPUB 3** file. Every page keeps its original look (fonts, spacing, layout), and the pages are ordered automatically.

Useful when a book you own has no digital edition and you want to read it comfortably on a screen, zoom in as much as you like, and keep everything in your e-reader library.

> **Status: v1.** This version packs page images into an EPUB. It does **not** run OCR yet, so the text inside the pages cannot be searched or selected. OCR support is planned (see [Roadmap](#roadmap)).

---

## Features

- Takes a folder of page images (`.png`, `.jpg`, `.jpeg`)
- Sorts pages by the number in the file name (`page2` comes before `page10`)
- Builds a valid Fixed-Layout EPUB 3 (`pre-paginated`), one image per page
- Right-to-left page progression, suited to Arabic books
- Table of contents with one entry per page
- Single file, one dependency (Pillow)

## Requirements

- Python 3.8 or newer
- [Pillow](https://pypi.org/project/pillow/)

```bash
pip install Pillow
```

## Usage

```bash
python images_to_epub.py <input_folder> [-o OUTPUT] [-t TITLE] [-a AUTHOR]
```

| Argument | Description | Default |
|---|---|---|
| `input_folder` | Folder containing the page images | required |
| `-o`, `--output` | Output EPUB file name | `result_fixed_layout.epub` |
| `-t`, `--title` | Book title | `عنوان الكتاب` |
| `-a`, `--author` | Book author | `المؤلف` |

### Example

```bash
python images_to_epub.py ./chapter1 -o chapter1.epub -t "My Book" -a "Author Name"
```

### Preparing your images

1. Put all page images in one folder.
2. Make sure each file name contains the page number, for example `1.jpg`, `2.jpg`, `page_3.png`. The **last number** in the name is used for ordering.
3. Photograph or scan pages upright and evenly lit. The EPUB shows the image as it is, so what you give is what you get.

```
chapter1/
├── page1.jpg
├── page2.jpg
├── page3.jpg
└── ...
```

### Reading the result

Open the `.epub` in any reader that supports Fixed-Layout EPUB 3, such as:

- Calibre viewer
- Thorium Reader
- Apple Books
- Many Android readers (for example Moon+ Reader, Librera)

Not every reader supports fixed-layout books. If pages look wrong, try one of the readers above.

## Windows executable

If you do not want to install Python, download `images_to_epub.exe` from the **[Releases](../../releases)** page and run it from a terminal:

```bat
images_to_epub.exe .\chapter1 -o chapter1.epub -t "My Book" -a "Author Name"
```

Windows may show a SmartScreen warning for unsigned programs. You can always inspect the source here and run the Python version instead.

## How it works

1. Reads the images and their dimensions.
2. Writes one XHTML page per image, with a `viewport` equal to the image size.
3. Generates `package.opf` (metadata, manifest and reading order) and `nav.xhtml` (table of contents).
4. Zips everything into an `.epub`, with the `mimetype` entry stored first and uncompressed as the EPUB spec requires.

## Known limitations

These are known in v1 and are good first issues if you want to contribute:

- **Working folder is reused.** The script builds the book in `./output` and does not clean it. Delete the `output` folder between runs, otherwise images from a previous book end up inside the new EPUB.
- **No OCR.** Text is part of the image, so it cannot be selected, searched or resized.
- **Fixed book identifier and date.** Every book gets the same `urn:uuid` and modified date, which can make some readers treat different books as the same one.
- **Arabic and RTL only.** Language is `ar` and page direction is right-to-left. There is no option for left-to-right books yet.
- **Titles with special characters.** Characters such as `&` or `<` in the title or author are not escaped and can produce an invalid EPUB.
- **Image formats.** Only PNG and JPEG are supported, and file names with spaces or non-ASCII characters may cause problems in some readers.

## Roadmap

- [ ] Clean the working folder automatically and use a temporary directory
- [ ] Unique identifier and real timestamp per book
- [ ] Escape title and author, and support left-to-right books
- [ ] OCR to extract text (Arabic and other languages) into a reflowable EPUB
- [ ] Optional hidden text layer so pages stay identical but become searchable
- [ ] Image cleanup: crop, deskew, contrast
- [ ] Simple GUI or web version

## Contributing

Contributions are welcome. Open an issue to discuss an idea or bug, or send a pull request.

## License

Released under the [MIT License](LICENSE). Add a `LICENSE` file to the repository, or choose another license if you prefer.

---

<div dir="rtl">

# تحويل صور الكتب إلى EPUB

أداة بسيطة تحوّل صور أو مسح صفحات كتاب إلى ملف **EPUB 3 ثابت التخطيط (Fixed-Layout)**، فتظهر كل صفحة بنفس شكلها الأصلي بالضبط، وتترتب الصفحات تلقائيًا.

مفيدة لو عندك كتاب ورقي ماله نسخة إلكترونية وعايز تقراه على الشاشة براحة، وتكبّر زي ما تحب.

> **الحالة: النسخة الأولى v1.** الأداة بتجمع صور الصفحات في ملف EPUB فقط، **من غير OCR**، يعني النص مش قابل للتحديد أو البحث لسه. دعم OCR مخطط له في الخطوات الجاية.

## التثبيت

```bash
pip install Pillow
```

## الاستخدام

```bash
python images_to_epub.py ./chapter1 -o chapter1.epub -t "اسم الكتاب" -a "المؤلف"
```

| الخيار | الوصف | الافتراضي |
|---|---|---|
| `input_folder` | مجلد صور الصفحات | مطلوب |
| `-o` | اسم ملف EPUB الناتج | `result_fixed_layout.epub` |
| `-t` | عنوان الكتاب | `عنوان الكتاب` |
| `-a` | اسم المؤلف | `المؤلف` |

**نصايح للصور:**
- حط كل الصور في مجلد واحد.
- لازم اسم كل ملف يحتوي رقم الصفحة (`1.jpg`، `page2.png`...). الترتيب بيعتمد على **آخر رقم** في الاسم.
- صوّر الصفحات مستقيمة وبإضاءة متساوية، لأن الصورة بتظهر زي ما هي.

**تنبيه مهم:** الأداة بتبني الكتاب في مجلد `output`. امسحه قبل كل تشغيل جديد، وإلا صور الكتاب السابق هتدخل في الملف الجديد.

للتفاصيل التقنية والقيود المعروفة وخطة التطوير، راجع الأقسام الإنجليزية أعلاه.

## الرخصة

MIT. المساهمات مرحّب بيها.

</div>
