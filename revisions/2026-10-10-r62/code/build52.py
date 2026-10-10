"""Offline build of the ordinary, complete R52 sources and frozen evidence."""
from pathlib import Path
import difflib, json, re, shutil, sys
import build as b
import build51 as previous
R=Path(__file__).resolve().parents[1]
def main():
    for tool in ('pdflatex','pandoc','pdfinfo'):
        if not shutil.which(tool):raise RuntimeError('Missing dependency: '+tool)
    b.LOGS.mkdir(parents=True,exist_ok=True);(R/'tables').mkdir(exist_ok=True);(R/'build').mkdir(exist_ok=True)
    inherited=b.historical()
    tests=dict(inherited)
    for name,file in [('construction50','tests50.py'),('publication50','publication_tests50.py'),('finite_sweeps51','tests51.py'),('contrasts52','tests52.py')]:
        tests[name]=b.tests([sys.executable,'code/'+file],name)
    for script,name in [('audit50.py','inherited-record-audit'),('tables50.py','inherited-tables'),('audit52.py','contrast-record-audit')]:
        b.run([sys.executable,'code/'+script],name)
    labels=lambda x:set(re.findall(r'\\label\{([^}]+)\}',x))
    preservation={}
    for n in ('ECTA','supp','complete','complete-supp'):
        before=R/'preserved/R51'/(n+'.tex');after=R/(n+'.tex')
        oldlabels=labels(previous.expand(before));newlabels=labels(previous.expand(after))
        if oldlabels-newlabels:raise AssertionError((n,'lost labels',oldlabels-newlabels))
        preservation[n]={'predecessor_labels':len(oldlabels),'current_labels':len(newlabels),'missing':[]}
        (R/'audit'/(n+'-R51-to-R52.diff')).write_text(''.join(difflib.unified_diff(before.read_text().splitlines(True),after.read_text().splitlines(True),fromfile='R51/'+n+'.tex',tofile='R52/'+n+'.tex')))
    frozen=json.loads((R/'audit/INHERITANCE52.json').read_text())
    for n,h in frozen['retained_sha256'].items():
        if b.digest(R/n)!=h:raise AssertionError('Altered inherited source or evidence: '+n)
    b.response();p=R/'response.tex';p.write_text(p.read_text().replace('Revision R50, 8 October 2026.','Revision R52, 8 October 2026.'))
    docs=[b.compile_document(n) for n in ('ECTA','supp','complete','complete-supp','response')]
    result={'status':'passed','tests':tests,'total_tests':sum(j['tests'] for j in tests.values()),
      'documents':docs,'preservation':preservation,'inherited_files_hash_checked':len(frozen['retained_sha256']),
      'new_record_audit':json.loads((R/'audit/RESULT_AUDIT52.json').read_text()),
      'new_independent_cost_estimands':0,'offline':True,
      'scope':'general conditional theorem; exact finite-state full sweeps; exhaustive terminal investment ablation'}
    b.write_json(R/'audit/RELEASE52.json',result)
    manifest={str(p.relative_to(R)):b.digest(p) for p in R.rglob('*') if p.is_file() and not any(v in p.parts for v in ('__pycache__','build','audit'))}
    b.write_json(R/'audit/PUBLICATION_FILES52.json',manifest)
    print(json.dumps({'tests':result['total_tests'],'documents':docs},indent=2))
if __name__=='__main__':main()
