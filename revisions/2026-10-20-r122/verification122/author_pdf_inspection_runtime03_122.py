"""Hash-bound PDF geometry and Poppler rendering for final author review.

This is document validation, not scientific execution or independent proof.
It records actual rendering work. Visual conclusions are a separate receipt.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,time
import fitz
from PIL import Image,ImageDraw

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
 if not ok: raise ValueError(msg)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--build-receipt',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();tick=time.perf_counter();started=datetime.now(timezone.utc).isoformat()
 rev=Path(__file__).resolve().parents[1];b=json.loads(a.build_receipt.read_text());require(b['status']=='compiled_clean' and not b['issues'] and not b['placeholders'],'A strict clean current build is required')
 a.output.mkdir(parents=True,exist_ok=False)
 pdfs=[];outside=[];requests={};content_checks=[];rendered=[];commands=[]
 for entry in b['pdfs']:
  p=rev/entry['path'];require(p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256'],'PDF differs from completed build')
  doc=fitz.open(p);name=p.stem;texts=[page.get_text() for page in doc]
  for i,page in enumerate(doc):
   for block in page.get_text('blocks'):
    if len(block)>6 and block[6]!=0:continue
    x0,y0,x1,y1=block[:4]
    if x0 < -.5 or y0 < -.5 or x1 > page.rect.width+.5 or y1 > page.rect.height+.5:
     outside.append({'document':name,'page':i+1,'bbox':[x0,y0,x1,y1],'page_size':[page.rect.width,page.rect.height],'text':str(block[4])[:180]})
  pdfs.append({**entry,'pages':len(doc),'page_sizes':sorted(set((round(p.rect.width,3),round(p.rect.height,3)) for p in doc))})
  (a.output/(name+'.txt')).write_text('\n\f\n'.join(texts))
  if name=='ECTA':
   requests[name]=list(range(1,len(doc)+1))
   required=['Neural Bellman Operators','824','102','768','29.006','14.855','0.655115692','0.655117504','0.664982692','0.664984805']
  elif name=='supp':
   requests[name]=[1]+list(range(82,min(len(doc),105)+1))
   required=['Propagation of certified action gains','Stationary certified policy improvement','Lower-gain occupations']
  elif name=='appendix':
   end=next(i+1 for i,t in enumerate(texts) if 'retained mathematical developments' in t.lower())
   requests[name]=list(range(1,end+1))
   required=['1,877,650','1,198,329','257,469','Complete current policy and work cells']
   # Exact source plotting text must survive inclusion, independent of page layout.
   source=fitz.open(rev/'figures122/runtime03-display/complete_catalogue_display122.pdf')
   included=[i for i,t in enumerate(texts) if 'Fixed catalogue rows' in t and 'Original-policy intervention:' in t]
   require(len(included)==8,'All eight complete catalogue pages must be included')
   for j,i in enumerate(included):
    normalize=lambda s:''.join(s.split())
    require(normalize(source[j].get_text())==normalize(texts[i]),'Embedded plot text differs from source page')
    require(abs(source[j].rect.width-doc[i].rect.width)<.1 and abs(source[j].rect.height-doc[i].rect.height)<.1,'Embedded plot paper size changed')
   content_checks.append({'kind':'complete_catalogue_inclusion','source_pdf_sha256':sha(rev/'figures122/runtime03-display/complete_catalogue_display122.pdf'),'source_pages':8,'manuscript_pages':[i+1 for i in included],'exact_whitespace_normalized_text_equal':True,'same_page_size':True})
  else:
   requests[name]=[1]
   required=['Author response','824','102']
  alltext=' '.join(' '.join(texts).split())
  for term in required:
   present=term.lower() in alltext.lower();content_checks.append({'document':name,'term':term,'present':present})
   require(present,'Expected current manuscript content absent: '+name+' '+term)
  for number in requests[name]:
   target=a.output/f'{name}-{number:04d}'
   argv=['pdftoppm','-f',str(number),'-l',str(number),'-singlefile','-r','96','-png',str(p),str(target)]
   start=time.perf_counter();run=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   commands.append({'argv':argv,'exit_code':run.returncode,'seconds':time.perf_counter()-start,'stderr':run.stderr.decode(errors='replace')})
   require(run.returncode==0,'Poppler rendering failed')
   png=target.with_suffix('.png');rendered.append({'document':name,'page':number,'path':str(png),'sha256':sha(png),'bytes':png.stat().st_size})
  doc.close()
 # Contact sheets show every selected page without implying full-resolution text review.
 contacts=[]
 for name,numbers in requests.items():
  for start in range(0,len(numbers),4):
   batch=numbers[start:start+4];thumbs=[]
   for number in batch:
    im=Image.open(a.output/f'{name}-{number:04d}.png').convert('RGB');im.thumbnail((540,720));thumbs.append((number,im))
   sheet=Image.new('RGB',(1120,1510),'#e5e8eb');draw=ImageDraw.Draw(sheet)
   for j,(number,im) in enumerate(thumbs):
    x=15+(j%2)*560;y=35+(j//2)*750;draw.text((x,y-20),f'{name}: actual PDF page {number}',fill='black');sheet.paste(im,(x,y))
   path=a.output/f'{name}-contact-{start//4+1:02d}.png';sheet.save(path);contacts.append({'document':name,'pages':batch,'path':str(path),'sha256':sha(path)})
 for p in pdfs: require(sha(rev/p['path'])==p['sha256'],'PDF changed during review rendering')
 out={'kind':'Actual final-PDF content, geometry and Poppler-rendering receipt','status':'executed','exit_code':0,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'seconds':time.perf_counter()-tick,'reader_sha256':sha(__file__),'build_receipt':str(a.build_receipt),'build_receipt_sha256':sha(a.build_receipt),'pdfs':pdfs,'physical_page_boundary_exceptions':outside,'content_checks':content_checks,'rendered_pages':rendered,'contact_sheets':contacts,'commands':commands,'scope':'Hash checks and text-box page-boundary scan cover every PDF page. Listed pages are actually rendered by Poppler; a separate signed visual-review receipt states which images were inspected. No new theorem, scientific sample, economic computation, or CI success is claimed.','cost_clock_components':[{'category':'publication','clock_fields':[['seconds']],'scope':'This document renderer and validation only; nested individual Poppler commands are included and not added again.','partial_lower_bound_only':False,'overlaps_counted_parent':False}]}
 (a.output/'PDF_INSPECTION122.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'receipt':str(a.output/'PDF_INSPECTION122.json'),'sha256':sha(a.output/'PDF_INSPECTION122.json'),'pdfs':pdfs,'page_boundary_exceptions':len(outside),'rendered_pages':len(rendered),'seconds':out['seconds']}))
if __name__=='__main__':main()
