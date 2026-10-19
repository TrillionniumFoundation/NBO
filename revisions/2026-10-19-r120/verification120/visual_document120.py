"""Record all-page PDF structure and render declared pages for author layout QA.

This is a document inspection, not a mathematical proof or economic execution.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import time

import fitz
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path, required=True)
    parser.add_argument('--pages', required=True, help='One-based comma-separated pages or ranges')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--thumb-width', type=int, default=420)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start = time.time()
    document = fitz.open(args.pdf)
    selected = set()
    for part in args.pages.split(','):
        if '-' in part:
            first, last = map(int, part.split('-'))
            selected.update(range(first, last + 1))
        else:
            selected.add(int(part))
    assert selected and min(selected) >= 1 and max(selected) <= len(document)
    inventory = []
    for index, page in enumerate(document):
        spans = [span for block in page.get_text('dict')['blocks'] if 'lines' in block
                 for line in block['lines'] for span in line['spans']]
        outside = [span for span in spans if span['bbox'][0] < -.5 or span['bbox'][1] < -.5
                   or span['bbox'][2] > page.rect.width + .5
                   or span['bbox'][3] > page.rect.height + .5]
        text = page.get_text()
        inventory.append({'page': index + 1, 'characters': len(text),
                          'page_size_pt': [page.rect.width, page.rect.height],
                          'outside_page_spans': outside,
                          'replacement_character_count': text.count('\ufffd'),
                          'text_sha256': hashlib.sha256(text.encode()).hexdigest()})
    sheets = []
    chosen = sorted(selected)
    for offset in range(0, len(chosen), 6):
        group = chosen[offset:offset + 6]
        tiles = []
        for number in group:
            page = document[number - 1]
            pix = page.get_pixmap(matrix=fitz.Matrix(args.thumb_width / page.rect.width,
                                                    args.thumb_width / page.rect.width),
                                  alpha=False)
            raster = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            tile = Image.new('RGB', (args.thumb_width + 20, raster.height + 40), 'white')
            tile.paste(raster, (10, 25))
            ImageDraw.Draw(tile).text((12, 7), f'{args.pdf.stem}: page {number}', fill='black')
            tiles.append(tile)
        height = max(tile.height for tile in tiles)
        sheet = Image.new('RGB', (2 * (args.thumb_width + 20), 3 * height), '#dddddd')
        for position, tile in enumerate(tiles):
            sheet.paste(tile, ((position % 2) * tile.width, (position // 2) * height))
        path = args.output / f'contact-{offset // 6 + 1:03}.png'
        sheet.save(path)
        sheets.append({'path': path.name, 'pages': group, 'bytes': path.stat().st_size,
                       'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    result = {'scope': 'All-page structural text census and declared-page raster rendering; human visual findings require a separate receipt. No mathematical or scientific validation is inferred.',
              'status': 'rendered', 'started_unix': start, 'ended_unix': time.time(),
              'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'pdf': str(args.pdf), 'pdf_sha256': hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
              'pdf_bytes': args.pdf.stat().st_size, 'pages': len(document),
              'selected_pages': chosen, 'page_inventory': inventory, 'contact_sheets': sheets,
              'outside_page_span_count': sum(len(row['outside_page_spans']) for row in inventory),
              'replacement_character_count': sum(row['replacement_character_count'] for row in inventory),
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output / 'RENDER_RECEIPT120.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'pages', 'outside_page_span_count',
                                           'replacement_character_count', 'pdf_sha256']}))


if __name__ == '__main__':
    main()
