"""Preserve complete research pages using direct, unscaled PDF concatenation.

The Econometrica cover still compiles from TeX. Imported current pages and the
five original historical components are concatenated without placing them in
an econsocart picture environment. Every original file remains unchanged.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[2];REL=ROOT/'revisions/2026-09-20-r19'
OLD=ROOT/'revisions/2026-09-19-r14-referee-response'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def req(x,msg):
    if not x:raise ValueError(msg)

def main():
    old='\\includepdf[pages=-]';new='\\includepdf[pages=-,fitpaper=true,noautoscale=true,pagecommand={}]'
    note='The combined PDF restores page geometry by directly concatenating the unchanged standalone source PDFs. The original historical compendium remains archived byte-for-byte; its imported-page placement is not propagated into this reading copy. No research page is omitted.\n'
    for p in (ROOT/'COMPENDIUM_R19.tex',REL/'COMPENDIUM_R19.tex'):
        s=p.read_text().replace(old,new)
        req(s.count(new)==3,'expected three complete source imports')
        if note not in s:s=s.replace(new,note+new,1)
        p.write_text(s)
    preservation=REL/'PRESERVATION.md'
    text=preservation.read_text();paragraph='\n## Complete compendium page geometry\n\nThe original R14 compendium remains unchanged. Its reading copy in the R19 compendium is assembled from its original cover and five unchanged standalone components, because the old TeX imports clipped page content. The R19 cover is compiled with econsocart; direct PDF concatenation preserves every source page at its original size, including the current paper and supplement. `compendium_input_layout.json` records the full page map, source hashes, and the equality of page counts. This is a layout restoration, not an alteration or omission of scientific content.\n'
    if paragraph not in text:preservation.write_text(text+paragraph)
    publisher=ROOT/'replication/r19/publish.py';s=publisher.read_text()
    old="      doc=fitz.open(pdf);text='\\n'.join(page.get_text() for page in doc)"
    new="      if name=='COMPENDIUM_R19':\n        from compendium_layout import assemble_pdf\n        assemble_pdf(pdf)\n      doc=fitz.open(pdf);text='\\n'.join(page.get_text() for page in doc)"
    if new not in s:
        req(s.count(old)==1,'unknown publication insertion point');publisher.write_text(s.replace(old,new))
    print('Compendium publication restores original page geometry by direct PDF concatenation.')

def assemble_pdf(destination):
    current=fitz.open(destination)
    children=[OLD/'ECTA_R14.pdf',OLD/'SUPP_R14.pdf',OLD/'historical/ECTA_R12.pdf',OLD/'historical/COMPENDIUM_R12.pdf',OLD/'historical/SUPP_R12.pdf']
    historical=fitz.open(OLD/'COMPENDIUM_R14.pdf')
    docs=[fitz.open(p) for p in children]
    old_cover=len(historical)-sum(len(d) for d in docs)
    main=fitz.open(REL/'ECTA_R19.pdf');supp=fitz.open(REL/'SUPP_R19.pdf')
    new_cover=len(current)-len(main)-len(supp)-len(historical)
    req(1<=old_cover<=6 and 1<=new_cover<=6,'unexpected cover or preservation page count')
    output=fitz.open();mapping=[];toc=[]
    def add(source,path,start=0,end=None,title=None):
        end=len(source)-1 if end is None else end
        at=len(output);output.insert_pdf(source,from_page=start,to_page=end)
        req(len(output)-at==end-start+1,'page count changed while concatenating')
        # Direct insertion must preserve every page box and extracted text.
        for i,j in enumerate(range(start,end+1)):
            target=output[at+i];original=source[j]
            req(tuple(target.rect)==tuple(original.rect),'source page geometry changed')
            req(target.get_text()==original.get_text(),'source text changed while concatenating')
        mapping.append(dict(source=str(path.relative_to(ROOT)),sha256=sha(path),source_pages=[start+1,end+1],output_pages=[at+1,len(output)]))
        if title:toc.append([1,title,at+1])
    add(current,destination,0,new_cover-1,'R19 cover and reading guide')
    add(main,REL/'ECTA_R19.pdf',title='Current R19 manuscript')
    add(supp,REL/'SUPP_R19.pdf',title='Current R19 proof supplement')
    add(historical,OLD/'COMPENDIUM_R14.pdf',0,old_cover-1,'Preserved R14 research record')
    titles=['R14 main paper','R14 proof supplement','R12 main paper','R12 theoretical and computational compendium','R12 full supplement']
    for source,path,title in zip(docs,children,titles):add(source,path,title=title)
    req(len(output)==len(current),'a historical or current page was lost')
    output.set_toc(toc);output.set_metadata({'title':'Neural Bellman Operators: Complete Research Compendium, R19','author':'Qian QI','subject':'Current manuscript and complete preserved research record; source-page geometry restored'})
    temp=destination.with_name('COMPENDIUM_R19_geometry_restored.pdf');output.save(temp,garbage=4,deflate=True)
    count=len(output);output.close();current.close();main.close();supp.close();historical.close()
    for d in docs:d.close()
    temp.replace(destination)
    report=dict(schema='nbo-r19-compendium-page-preservation-v2',passed=True,pages=count,current_cover_pages=new_cover,historical_cover_pages=old_cover,source_page_map=mapping,all_source_page_rectangles_and_text_identical=True,original_historical_files_unchanged=True,
      scope='The generated TeX cover is retained. Every imported research page is directly copied from its unchanged standalone source PDF. Old compendium placement errors are not inherited. The archived original R14 compendium remains unchanged at its original path.')
    (REL/'compendium_input_layout.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('Direct compendium concatenation preserved',count,'pages and all source page text and geometry.',flush=True)
if __name__=='__main__':main()
