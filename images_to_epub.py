#!/usr/bin/env python3
import argparse
from pathlib import Path
from PIL import Image
import zipfile
import shutil
import re

def parse_arguments():
    # Parse Command Line Arguments
    parser = argparse.ArgumentParser(description="Convert scanned book images into Fixed-Layout EPUB 3.")
    parser.add_argument("input_folder", type=str, help="Path to the folder containing book images.")
    parser.add_argument("-o", "--output", type=str, default="result_fixed_layout.epub", help="Output EPUB file name.")
    parser.add_argument("-t", "--title", type=str, default="عنوان الكتاب", help="Book title.")
    parser.add_argument("-a", "--author", type=str, default="المؤلف", help="Book author.")
    return parser.parse_args()

def create_directories(output_path="./output"):
    # Create Main Sructure Of The Book
    output_dir = Path(output_path)
    epub_root = output_dir / "EPUB"
    images_folder = epub_root / "images"
    meta_inf = output_dir / "META-INF"
    
    epub_root.mkdir(parents=True, exist_ok=True)
    images_folder.mkdir(exist_ok=True)
    meta_inf.mkdir(exist_ok=True)
    
    return output_dir, epub_root, images_folder, meta_inf

def get_image_files(input_folder):
    # Get Images And Return Them Sorted Numerically
    folder = Path(input_folder)
    if not folder.exists():
        raise FileNotFoundError(f"The directory '{input_folder}' does not exist.")
    image_extensions = ('.png', '.jpg', '.jpeg')
    files = [f for f in folder.iterdir() if f.suffix.lower() in image_extensions]
    
    # دالة استخراج الرقم من اسم الملف لضمان الترتيب التصاعدي الصحيح (1, 2, 3 ... 10, 11)
    def extract_number(file_path):
        numbers = re.findall(r'\d+', file_path.stem)
        return int(numbers[-1]) if numbers else 0

    return sorted(files, key=extract_number)

def extract_image_dimensions(image_files):
    pages_data = []
    for index, img_path in enumerate(image_files, start=1):
        with Image.open(img_path) as img:
            width, height = img.size
        
        page_info = {
            "page_num": index,
            "filename": img_path.name,
            "width": width,
            "height": height,
            "path": img_path
        }
        pages_data.append(page_info)
        print(f"Processed Page {index}: {img_path.name} (Width: {width}, Height: {height})")
    return pages_data

def build_xhtml_content(page_num, width, height, filename):
    # Build The XHTML Conntent
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ar" dir="rtl">
<head>
    <title>Page {page_num}</title>
    <meta name="viewport" content="width={width}, height={height}"/>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #ffffff;
            width: {width}px;
            height: {height}px;
        }}
        .image-container {{
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}
    </style>
</head>
<body>
    <div class="image-container">
        <img src="images/{filename}" alt="Page {page_num}"/>
    </div>
</body>
</html>
"""

def build_nav_content(book_title, pages_data):
    # Build The Top Of Book
    nav_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="ar" dir="rtl">
<head><title>{book_title}</title></head>
<body>
<nav epub:type="toc">
    <h1>Top Of Book</h1>
    <ol>
"""
    for p in pages_data:
        idx = p['page_num']
        nav_content += f'        <li><a href="page_{idx}.xhtml">صفحة {idx}</a></li>\n'
    nav_content += """    </ol>
</nav>
</body>
</html>
"""
    return nav_content

def build_opf_content(book_title, book_author, pages_data):
    #  Build The OPF
    opf_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="ar" dir="rtl">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:uuid:b6ab01d0-8f29-40ef-b83f-e9b4d44c355d</dc:identifier>
    <dc:title>{book_title}</dc:title>
    <dc:creator>{book_author}</dc:creator>
    <dc:language>ar</dc:language>
    <meta property="dcterms:modified">2026-10-22T12:00:00Z</meta>
    
    <meta property="rendition:layout">pre-paginated</meta>
    <meta property="rendition:orientation">auto</meta>
    <meta property="rendition:spread">auto</meta>
</metadata>
<manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
"""
    for p in pages_data:
        idx = p['page_num']
        opf_content += f'    <item id="page_{idx}" href="page_{idx}.xhtml" media-type="application/xhtml+xml"/>\n'
        ext = p['filename'].split('.')[-1].lower()
        mtype = "image/jpeg" if ext in ['jpg', 'jpeg'] else "image/png"
        opf_content += f'    <item id="img_{idx}" href="images/{p["filename"]}" media-type="{mtype}"/>\n'

    opf_content += """</manifest>
<spine page-progression-direction="rtl">
"""
    for p in pages_data:
        idx = p['page_num']
        opf_content += f'    <itemref idref="page_{idx}"/>\n'

    opf_content += """</spine>
</package>
"""
    return opf_content

def save_project_files(epub_root, pages_data, nav_content, opf_content):
    # Save XHTML, OPF and NAV on disk
    for p in pages_data:
        idx = p['page_num']
        xhtml = build_xhtml_content(idx, p['width'], p['height'], p['filename'])
        with open(epub_root / f"page_{idx}.xhtml", "w", encoding="utf-8") as f:
            f.write(xhtml)
            
    with open(epub_root / "nav.xhtml", "w", encoding="utf-8") as f:
        f.write(nav_content)
        
    with open(epub_root / "package.opf", "w", encoding="utf-8") as f:
        f.write(opf_content)

def copy_images_to_project(pages_data, images_folder):
    for p in pages_data:
        shutil.copy(p['path'], images_folder / p['filename'])

def create_epub_archive(output_epub_name, epub_root):
    # Create Final Result .epub
    with zipfile.ZipFile(output_epub_name, 'w', zipfile.ZIP_DEFLATED) as epub:
        epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        
        container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
        epub.writestr("META-INF/container.xml", container_xml)
        
        for file_path in epub_root.rglob('*'):
            if file_path.is_file():
                arcname = f"EPUB/{file_path.relative_to(epub_root)}"
                epub.write(file_path, arcname)
                
    print(f"Fixed-Layout EPUB Created Successfully: {output_epub_name}")

def main():
    # main function 
    args = parse_arguments()
    
    epub_dirs = create_directories()
    epub_root = epub_dirs[1]
    
    image_files = get_image_files(args.input_folder)
    pages_data = extract_image_dimensions(image_files)
    
    nav_content = build_nav_content(args.title, pages_data)
    opf_content = build_opf_content(args.title, args.author, pages_data)
    
    save_project_files(epub_root, pages_data, nav_content, opf_content)
    copy_images_to_project(pages_data, epub_dirs[2])
    create_epub_archive(args.output, epub_root)

if __name__ == "__main__":
    main()