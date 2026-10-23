"""Render specified final PDF pages for a recorded, scoped visual inspection."""
from pathlib import Path
import hashlib, json
import fitz
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'visual_qa125/final-author-pages'
OUT.mkdir(parents=True,exist_ok=False)
spec={'ECTA':[1,30,31,32,33,34,35,36,37],
      'supp':[142,143,144,145,146],
      'RESPONSE_TO_REFEREE':list(range(1,22))}
record={'scope':'Contact renders for all updated main results/discussion, new supplement identity proof, and entire current response. Earlier archived development has separate scoped QA.',
        'pdfs':{},'images':[],'inspection_not_implied_by_rendering':True}
for name,pages in spec.items():
    path=ROOT/'build'/f'{name}.pdf'
    doc=fitz.open(path)
    record['pdfs'][name]={'pages':len(doc),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rendered_pages':pages}
    for group in range(0,len(pages),9):
        selected=pages[group:group+9]
        sheet=Image.new('RGB',(1320,1920),'#d8d8d8')
        draw=ImageDraw.Draw(sheet)
        for index,page in enumerate(selected):
            pix=doc[page-1].get_pixmap(matrix=fitz.Matrix(0.8,0.8),alpha=False)
            im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            im.thumbnail((420,605))
            x=(index%3)*440+10;y=(index//3)*640+25
            sheet.paste(im,(x,y));draw.text((x,y-17),f'{name} page {page}',fill='black')
        target=OUT/f'{name}-contact-{group//9+1:02}.png'
        sheet.save(target)
        record['images'].append({'path':str(target.relative_to(ROOT)),'pages':selected,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    if name in {'ECTA','supp'}:
        detail=[31,33,34] if name=='ECTA' else [143,144,145]
        for page in detail:
            target=OUT/f'{name}-detail-{page:04}.png'
            doc[page-1].get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False).save(target)
            record['images'].append({'path':str(target.relative_to(ROOT)),'pages':[page],'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(OUT/'RENDER125.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'images':len(record['images']),'pdfs':record['pdfs']}))
