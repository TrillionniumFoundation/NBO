"""Compile and check the complete R18 review object with the repository class."""
from pathlib import Path
import json,re,subprocess
ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'revisions/2026-09-23-r18/build_logs'

def main():
    DEST.mkdir(parents=True,exist_ok=True);records=[]
    for name,short in [('ECTA_R18','main'),('SUPP_R18','supp'),('RESPONSE_R18','response')]:
        for i in range(1,4):
            p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            (DEST/f'{short}_pass{i}.txt').write_text(p.stdout)
            if p.returncode:raise RuntimeError(f'{name}: pass {i} failed; see build log')
        log=(ROOT/(name+'.log')).read_text(errors='replace')
        bad=[x for x in ['undefined references','undefined citations','multiply defined','Overfull \\hbox','Overfull \\vbox'] if x in log]
        if bad:raise RuntimeError(f'{name}: unresolved typesetting checks: {bad}')
        info=subprocess.check_output(['pdfinfo',str(ROOT/(name+'.pdf'))],text=True)
        pages=int(re.search(r'Pages:\s+(\d+)',info).group(1))
        records.append({'document':name+'.pdf','pages':pages,'bytes':(ROOT/(name+'.pdf')).stat().st_size,'passes':3,'undefined_references':False,'overfull_boxes':False})
    result={'status':'PASS','documents':records,'class':'repository econsocart.cls; [ecta] option'}
    (DEST/'pdf_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
