"""Prepare R81 from the pinned executed R80 snapshot; never mutate old revisions."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,re,shutil,subprocess
R=Path(__file__).resolve().parents[1]
OLD=R.parent/'2026-10-12-r80'
BASE='ec8d40a058bfc03a88a62a223559698c5e849b22'
REVIEW='4b27b56f4514f6c1d77b69fe707f7202f8b06b19'

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def main():
    marker=R/'audit/PREPARATION81.json'
    if marker.exists():
        print('Ordinary R81 snapshot already prepared; author edits preserved.');return
    own={p.relative_to(R):p.read_bytes() for p in R.rglob('*') if p.is_file()}
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for rel,data in own.items():(R/rel).write_bytes(data)
    archive=R/'preserved/R80-snapshot';archive.mkdir(parents=True,exist_ok=True)
    for name in ('ECTA.tex','supp.tex','appendix.tex','response.md','response.tex','README.md'):
        shutil.copy2(OLD/name,archive/name)
    shutil.copytree(OLD/'audit',archive/'audit',dirs_exist_ok=True)
    shutil.copytree(OLD/'build',archive/'inherited-build',dirs_exist_ok=True)
    # Inherited build files are R79-era outputs, not newly compiled R80 or R81.
    shutil.rmtree(R/'build');(R/'build').mkdir()
    protected={}
    for p in OLD.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        rel=p.relative_to(OLD)
        if rel.parts[0].startswith('results') or rel.parts[0] in ('code','preserved') or p.name.startswith(('SOURCE_FREEZE','ACTOR_FREEZE','PROTOCOL')):
            protected[str(rel)]=sha(p)
    sections={}
    for doc in ('ECTA','supp','appendix'):
        for path in re.findall(r'\\input\{(sections/[^}]+)\}',(OLD/(doc+'.tex')).read_text()):
            f=path+'.tex'
            if f in sections:raise AssertionError('Inherited section duplicated '+f)
            sections[f]=dict(sha256=sha(OLD/f),document=doc)
    save(marker,dict(base_commit=BASE,review_commit=REVIEW,protected_files=protected,active_sections=sections,
        original_wrappers={n:sha(OLD/n) for n in ('ECTA.tex','supp.tex','appendix.tex','response.md')},
        wrapper_labels={n:re.findall(r'\\label\{([^}]+)\}',(OLD/n).read_text()) for n in ('ECTA.tex','supp.tex','appendix.tex')},
        source='R80 executed data, R79 active manuscript; inherited PDF labels remain historical',new_scientific_observations=0))
    report=json.loads((R/'results80/cost/summary.json').read_text())
    def compact(v):
        out={k:v[k] for k in ('interval','sign','equivalence_at_margin','first_minus_second_noninferior','paired_width_target_passed') if k in v}
        if 'width_decomposition' in v:out['width_components']={k:float(F(x)) for k,x in v['width_decomposition'].items()}
        return out
    inspection={k:report[k] for k in ('rows','policies','estimands','family_failure_upper','controller_metadata','peak_rss_kib','statistical_inference_seconds')}
    inspection['inference']={e:{kind:{name:compact(v) for name,v in rows.items()} for kind,rows in result.items()} for e,result in report['inference'].items()}
    inspection['work']=report['work']
    inspection['barriers']=json.loads((R/'audit/BARRIER80.json').read_text())
    inspection['source_manifest']=json.loads((R/'SOURCE_FREEZE80.json').read_text())
    save(R/'audit/INSPECTION81.json',inspection)
    print(json.dumps(dict(status='prepared',protected_files=len(protected),active_sections=len(sections),rows=report['rows'])))
if __name__=='__main__':main()
