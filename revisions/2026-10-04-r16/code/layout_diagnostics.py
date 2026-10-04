"""Render all four publication PDFs and record deterministic layout diagnostics.

The automated gate checks page count, extraction, physical page boundaries,
nonblank raster output, and successful complete rendering. It complements the
author's separately recorded inspection of every page; it does not claim to
replace visual judgment. Raster files live outside the repository.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from publication_audit import (R, ROOTS, require, read, write, sha, canonical,
    all_current_sources)


def source_fingerprint(closure):
    files = {name: {key: row[key] for key in ('sha256', 'bytes', 'git_blob')}
             for name, row in sorted(closure.items())}
    return hashlib.sha256(canonical(files)).hexdigest()


def check_bounds(root):
    pages = []
    for number, page in enumerate(root.findall('.//{*}page'), 1):
        width, height = float(page.attrib['width']), float(page.attrib['height'])
        require(width > 300 and height > 300, 'invalid scientific PDF page geometry')
        words = page.findall('.//{*}word')
        require(len(words) >= 3, 'blank or unextractable PDF page: ' + str(number))
        outside = []
        for word in words:
            box = [float(word.attrib[k]) for k in ('xMin', 'yMin', 'xMax', 'yMax')]
            require(box[2] >= box[0] and box[3] >= box[1], 'invalid PDF text bounding box')
            if box[0] < -.5 or box[1] < -.5 or box[2] > width + .5 or box[3] > height + .5:
                outside.append(dict(text=word.text, box=box))
        require(not outside, 'text outside physical page: ' + str(number) + ' ' + str(outside[:3]))
        pages.append(dict(page=number, width_points=width, height_points=height,
                          extractable_words=len(words), text_outside_page=outside))
    require(pages, 'no PDF pages found')
    return pages


def parse_bbox_xml(data):
    """Preserve word geometry when Poppler emits XML-illegal math glyph codes.

    The PDF and original bbox file remain untouched. Only the parsing copy
    replaces C0 characters forbidden by XML 1.0; their exact counts are kept
    in the diagnostic record. Ordinary text and every element/attribute are
    retained, so the page-boundary and nonempty-word checks are unchanged.
    """
    text = data.decode('utf-8')
    illegal = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
    counts = Counter(illegal.findall(text))
    parsed = ET.fromstring(illegal.sub('\ufffd', text))
    return parsed, {f'U+{ord(char):04X}': count for char, count in sorted(counts.items())}


def inspect_pdf(pdf, output, dpi):
    output.mkdir(parents=True, exist_ok=True)
    bbox = output / 'text-bounds.html'
    subprocess.run(['pdftotext', '-bbox-layout', str(pdf), str(bbox)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    parsed, control_codes = parse_bbox_xml(bbox.read_bytes())
    pages = check_bounds(parsed)
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', str(pdf), str(output / 'page')],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    pngs = sorted(output.glob('page-*.png'), key=lambda p: int(re.search(r'-(\d+)\.png$', p.name).group(1)))
    require(len(pngs) == len(pages), 'not every page rendered successfully')
    for page, png in zip(pages, pngs):
        data = png.read_bytes()
        require(data.startswith(b'\x89PNG\r\n\x1a\n') and len(data) > 1000, 'empty or invalid page raster')
        page.update(render_sha256=hashlib.sha256(data).hexdigest(), render_bytes=len(data))
    return dict(pdf_sha256=sha(pdf), pages=len(pages), rendered_pages=len(pngs),
                raster_dpi=dpi, page_diagnostics=pages, complete=True,
                xml_illegal_math_glyph_codes=control_codes,
                xml_parsing_scope='C0 glyph codes replaced only in XML parsing copy; original PDF and bbox bytes retained.',
                text_bounds_sha256=sha(bbox))


def diagnostics(repo, out, dpi=60):
    repo, out = Path(repo).resolve(), Path(out).resolve()
    require(not out.is_relative_to(repo), 'page rasters must be written outside the repository')
    require(not out.exists() or not any(out.iterdir()), 'use a fresh layout output directory')
    out.mkdir(parents=True, exist_ok=True)
    _, closure, _ = all_current_sources(repo)
    documents = {name: inspect_pdf(repo / R / 'build' / (name + '.pdf'), out / name, dpi) for name in ROOTS}
    result = dict(schema='nbo-r16-final-layout-diagnostics-v1', complete=True,
        source_closure_fingerprint=source_fingerprint(closure), documents=documents,
        checks=['all four PDFs', 'every page rendered', 'extractable text on every page', 'text within physical page bounds'],
        scope='Automatic diagnostics supplement the separately source-bound human page review; they are not an aesthetic or scientific judgment.')
    write(repo / R / 'results/FINAL_LAYOUT_DIAGNOSTICS.json', result)
    return result


def check_visual_review(repo, closure, pdfs):
    review_path = repo / R / 'FINAL_VISUAL_REVIEW.json'
    review = read(review_path)
    require(review.get('complete') is True and review.get('unresolved_issues') == [], 'final visual review is incomplete')
    require(review['source_closure_fingerprint'] == source_fingerprint(closure), 'visual review describes different scientific source')
    require(set(review['documents']) == set(ROOTS), 'visual review omits one of four PDFs')
    for name, item in review['documents'].items():
        require(item.get('all_pages_inspected') is True and item.get('pages', 0) > 0 and
                re.fullmatch('[0-9a-f]{64}', item.get('pdf_sha256', '')), 'incomplete author page review: ' + name)
        require(item['pages'] == pdfs[name]['pages'], 'CI page count differs from the final visually inspected document: ' + name)
    layout = read(repo / R / 'results/FINAL_LAYOUT_DIAGNOSTICS.json')
    require(layout.get('complete') is True and layout['source_closure_fingerprint'] == source_fingerprint(closure),
            'layout diagnostics describe different final sources')
    require(set(layout['documents']) == set(ROOTS), 'layout diagnostics omit one PDF')
    for name, item in layout['documents'].items():
        require(item.get('complete') is True and item['pdf_sha256'] == pdfs[name]['sha256'] and
                item['pages'] == item['rendered_pages'] == pdfs[name]['pages'], 'incomplete final raster or stale PDF diagnostic')
        require(len(item['page_diagnostics']) == item['pages'] and
                all(not page['text_outside_page'] for page in item['page_diagnostics']), 'layout diagnostic reports clipping')
    return dict(final_visual_review_sha256=sha(review_path), layout_diagnostics_sha256=sha(repo / R / 'results/FINAL_LAYOUT_DIAGNOSTICS.json'),
                source_closure_fingerprint=source_fingerprint(closure), all_four_documents_reviewed=True,
                all_pages_rendered=sum(row['pages'] for row in pdfs.values()), unresolved_issues=[])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    parser.add_argument('--out', required=True)
    parser.add_argument('--dpi', type=int, default=60)
    args = parser.parse_args()
    result = diagnostics(args.repo, args.out, args.dpi)
    print('Rendered and checked', sum(x['pages'] for x in result['documents'].values()), 'pages across four PDFs.')
