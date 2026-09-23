"""Three-pass Econometrica paper build with structural and layout checks."""
from pathlib import Path
import subprocess,json,re
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-23-r19'

def main():
    logs=R/'build_logs';logs.mkdir(exist_ok=True,parents=True);records=[]
    for name in ['ECTA_R19','SUPP_R19','RESPONSE_R19']:
        for k in range(1,4):
            with (logs/f'{name}_pass{k}.txt').open('w') as f:
                subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
        log=(ROOT/(name+'.log')).read_text(errors='replace')
        failures=[s for s in log.splitlines() if re.search(r'Overfull \\[hv]box|undefined|multiply defined|^!',s)]
        if failures:raise RuntimeError(name+': '+repr(failures))
        info=subprocess.check_output(['pdfinfo',str(ROOT/(name+'.pdf'))],text=True)
        pages=int(re.search(r'Pages:\s+(\d+)',info).group(1))
        records.append({'document':name,'pages':pages,'bytes':(ROOT/(name+'.pdf')).stat().st_size,'passes':3,
          'overfull_boxes':0,'undefined_references':0,'status':'PASS',
          'benign_class_warning':'econsocart frontmatter may emit hyperref Ignoring empty anchor; no unresolved link or layout error'})
        print('BUILT',name,pages,flush=True)
    (R/'results/build_validation.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
