"""Run ordinary publication and collect every PDF failure without weakening gates."""
from pathlib import Path
import json,subprocess,sys,time
import build as b
R=Path(__file__).resolve().parents[1]
DOCS=('ECTA','supp','development','development-supp','complete','complete-supp','response')
def main():
    start=time.perf_counter();(R/'audit/build-logs').mkdir(parents=True,exist_ok=True)
    log=R/'audit/PUBLICATION_RUN61.log'
    with log.open('w') as out:p=subprocess.run([sys.executable,'code/build61.py'],cwd=R,stdout=out,stderr=subprocess.STDOUT)
    print(log.read_text()[-12000:],flush=True)
    if p.returncode==0:return
    diagnoses={}
    # Diagnostic compilation cannot publish a manuscript. All ordinary gates
    # remain mandatory; errors are collected across the seven documents.
    for name in DOCS:
        try:
            rec=b.compile_document(name);diagnoses[name]=dict(status='passed',pages=rec['pages'])
        except Exception as error:
            entry=dict(status='failed',error=str(error)[-3500:]);path=R/'build'/(name+'.log')
            if path.exists():
                lines=path.read_text(errors='replace').splitlines();contexts=[]
                for j,line in enumerate(lines):
                    if any(word in line for word in ('Overfull','Undefined control sequence','LaTeX Error','Missing character:','Citation','multiply defined')):
                        contexts.append('\n'.join(lines[max(0,j-3):min(len(lines),j+9)]))
                entry['contexts']=contexts
            diagnoses[name]=entry
    file=R/'audit/PDF_DIAGNOSTICS61.json'
    file.write_text(json.dumps(dict(status='failed',documents=diagnoses,seconds=time.perf_counter()-start,scope='Diagnostics only; all ordinary-source gates remain mandatory.'),indent=2)+'\n')
    print(file.read_text(),flush=True)
    raise SystemExit(p.returncode)
if __name__=='__main__':
    main()
