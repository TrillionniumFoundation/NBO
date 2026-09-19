"""Match each imported PDF's paper size instead of cropping to class defaults.

The standalone current documents are unchanged. The prior compendium remains
byte-identical. This correction changes only the new compendium's placement.
"""
import json
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[2];REL=ROOT/'revisions/2026-09-20-r19'
def main():
    old='\\includepdf[pages=-]'
    new='\\includepdf[pages=-,fitpaper=true,noautoscale=true,pagecommand={}]'
    for p in (ROOT/'COMPENDIUM_R19.tex',REL/'COMPENDIUM_R19.tex'):
        s=p.read_text()
        if old in s:s=s.replace(old,new);p.write_text(s)
        if s.count(new)!=3:raise ValueError('expected three complete unscaled imported documents')
    source=ROOT/'revisions/2026-09-19-r14-referee-response/COMPENDIUM_R14.pdf'
    d=fitz.open(source);outside=[]
    for page in d:
      for block in page.get_text('dict')['blocks']:
        if block.get('type')!=0:continue
        for line in block.get('lines',[]):
          for span in line.get('spans',[]):
            x0,y0,x1,y1=span['bbox']
            if x0<-1 or y0<-1 or x1>page.rect.width+1 or y1>page.rect.height+1:
              outside.append(dict(page=page.number+1,bbox=list(span['bbox']),text=span['text'][:100]))
    report=dict(schema='nbo-r19-compendium-input-layout-v1',legacy_source=str(source.relative_to(ROOT)),legacy_pages=len(d),legacy_outside_spans=outside,
      correction='Each imported PDF uses its own paper dimensions without autoscaling. Historical source PDFs are not rewritten.')
    (REL/'compendium_input_layout.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Compendium uses source-sized pages; preserved legacy input has',len(outside),'out-of-page text spans.')
if __name__=='__main__':main()
