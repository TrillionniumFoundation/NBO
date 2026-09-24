"""Build the materialized R38 review package; publish only after every check passes.

Run from any directory inside a git checkout containing the completed R38 science.
This script does not commit, push, delete historical files, or change another branch.
"""
from pathlib import Path
import gzip,hashlib,json,os,re,subprocess,sys,time
import fitz
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
BASE='c81410887bca5c16975beabb2ca8d6be7f235a19'
SCIENCE_COMMIT='589b4a765d5d52de9a13b8a3058f1146f29f9519'
BRANCH='revision/econometrica-r38-verified-global-bounds-2026-09-24'
NAMES=('ECTA','SUPP','RESPONSE','COMPUTATION','HISTORY')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def read(name):return json.loads((ROOT/'results'/f'{name}.json').read_text())
def validate_science():
    ledger=read('execution_ledger')
    if not ledger['passed'] or any(x['returncode'] for x in ledger['programs']):raise RuntimeError('Unsuccessful scientific execution')
    expected=json.loads((ROOT/'replication/expected_objects.json').read_text());actual={}
    for directory in expected['directories']:
        for p in sorted((ROOT/'results'/directory).glob('*.json.gz')):
            data=json.loads(gzip.decompress(p.read_bytes()))
            b=json.dumps(data,sort_keys=True,separators=(',',':')).encode()
            actual[str(p.relative_to(ROOT))]=hashlib.sha256(b).hexdigest()
    digest=hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert len(actual)==expected['count']==187 and digest==expected['canonical_manifest_sha256']
    p=read('primary');v=read('independent_verification');f=read('frontier');vf=read('frontier_independent_verification');s=read('sensitivity');m=read('multistate')
    assert (p['cases'],p['exact_integrated'],p['positive_cost_exact'],p['exact_pointwise'])==(42,24,12,23)
    assert v['passed'] and v['objects']==42 and len(v['mutation_categories'])==20 and all(x['rejected'] for x in v['mutation_categories'])
    assert f['point_cases']==70 and f['strict_class_separations']==24 and vf['passed'] and vf['objects']==70
    assert s['cases']==66 and s['strict_savings']==22 and s['failed_certificates']==0
    assert m['cases']==76 and sum(x['certified'] for x in m['outcomes'] if x['method']=='restart')==26
    assert sum(x['certified'] for x in m['outcomes'] if x['method']=='pilot_raw')==0
    assert sum(x['certified'] for x in m['outcomes'] if x['method']=='classical_scalarization')==15
    assert read('local_lp')['cases']==12
    return {'passed':True,'exact_objects':len(actual),'canonical_manifest_sha256':digest,'independent_primary_objects':42,'independent_frontier_objects':70,'mutations_rejected':20}
def preserve_index():
    old=git('show',f'{BASE}:REVISION_INDEX.md')
    p=ROOT/'history/REVISION_INDEX_before_R38.md';p.parent.mkdir(exist_ok=True);p.write_bytes(old)
    (REPO/'REVISION_INDEX.md').write_text('''# Current review object: R38

Read [R38_REVIEW.md](R38_REVIEW.md), then ECTA_R38.pdf, SUPP_R38.pdf,
RESPONSE_R38.pdf, COMPUTATION_R38.pdf, and HISTORY_R38.pdf.

Latest addressed report: reviews/2026-09-24-econometrica-r36/referee_report.md
at c81410887bca5c16975beabb2ca8d6be7f235a19.
The completed science is committed at 589b4a765d5d52de9a13b8a3058f1146f29f9519.
Publication provenance and hashes are in revisions/2026-09-24-r38/PUBLICATION_MANIFEST.json.

R38 retains all 42 primary configurations and tolerances 0.01/0.05. There are
24 exact initial-distribution deterministic optima, including 12 positive-cost
cases; 23 additionally have complete cost-function equality. The 18 residual
intervals, separate randomized policy classes, and original stopped-control target
are explicitly retained. No maintenance result is called a solution of that
separate all-domain stopped-control objective.

The preceding index is preserved byte-for-byte in
revisions/2026-09-24-r38/history/REVISION_INDEX_before_R38.md.
All other files inherited from the review base are unchanged.
''')
def preservation():
    records=[]
    for row in git('ls-tree','-rz','--full-tree',BASE).split(b'\0'):
        if not row:continue
        metadata,name=row.split(b'\t',1);mode,kind,old=metadata.decode().split();rel=name.decode();p=REPO/rel
        if kind!='blob':raise RuntimeError(f'Unsupported inherited object {rel}')
        data=os.readlink(p).encode() if mode=='120000' else p.read_bytes()
        new=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if rel=='REVISION_INDEX.md':
            saved=ROOT/'history/REVISION_INDEX_before_R38.md'
            assert saved.read_bytes()==git('show',f'{BASE}:{rel}')
            status='updated_pointer_original_preserved'
        else:
            if new!=old:raise RuntimeError(f'Inherited file changed: {rel}')
            status='unchanged'
        records.append({'path':rel,'base_blob':old,'current_blob':new,'status':status})
    result={'base_review_commit':BASE,'passed':True,'inherited_files':len(records),'allowed_pointer_updates':['REVISION_INDEX.md'],'records':records}
    (ROOT/'history/preservation_manifest.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result

def build():
    reports=[]
    for name in NAMES:
        stem=f'{name}_R38';tic=time.perf_counter()
        for i in range(1,4):
            with (ROOT/'build'/f'{stem}_pass{i}.txt').open('w') as log:
                process=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',stem+'.tex'],cwd=REPO,stdout=log,stderr=subprocess.STDOUT)
            if process.returncode:raise RuntimeError(f'{stem} compilation failed on pass {i}')
        content=(REPO/f'{stem}.log').read_text(errors='replace');(ROOT/'build'/f'{stem}.log').write_text(content)
        forbidden=('undefined references','undefined citations','LaTeX Error','Emergency stop','Fatal error')
        if any(x.lower() in content.lower() for x in forbidden):raise RuntimeError(f'{stem}: unresolved TeX diagnostic')
        if re.search(r'(Reference|Citation) .* undefined',content):raise RuntimeError(f'{stem}: unresolved reference')
        overflow=[float(x) for x in re.findall(r'Overfull \\[hv]box \(([\d.]+)pt too (?:wide|high)\)',content)]
        if any(x>0.75 for x in overflow):raise RuntimeError(f'{stem}: material layout overflow {overflow}')
        doc=fitz.open(REPO/f'{stem}.pdf')
        if not len(doc):raise RuntimeError('Empty PDF')
        if name!='HISTORY' and any(len(page.get_text().strip())<40 for page in doc):raise RuntimeError(f'{stem}: empty page')
        for i,page in enumerate(doc):
            if name=='HISTORY':continue
            for word in page.get_text('words'):
                if word[0]<-1 or word[1]<-1 or word[2]>page.rect.width+1 or word[3]>page.rect.height+1:
                    raise RuntimeError(f'{stem}: text extends beyond page {i+1}')
        reports.append({'entry':stem+'.tex','pdf':stem+'.pdf','pages':len(doc),'sha256':sha(REPO/f'{stem}.pdf'),'passes':3,'unresolved_references':0,'overflows_pt':overflow,'seconds':time.perf_counter()-tic})
        print('Built',reports[-1],flush=True)
    return reports

def history_check():
    out=fitz.open(REPO/'HISTORY_R38.pdf');offset=1;records=[]
    norm=lambda s:' '.join(s.split())
    for name in NAMES:
        old=REPO/f'{name}_R34.pdf';doc=fitz.open(old)
        for i,page in enumerate(doc):
            assert norm(page.get_text())==norm(out[offset+i].get_text()),f'Historical page text mismatch {old.name} {i+1}'
        records.append({'file':old.name,'sha256':sha(old),'pages':len(doc),'annex_first_page':offset+1,'annex_last_page':offset+len(doc),'full_page_text_check':True});offset+=len(doc)
    assert len(out)==offset
    d={'passed':True,'annex_pages':len(out),'new_cover_pages':1,'sources':records,'scope':'Every source page is included as an imported PDF page, with complete text equality; original source PDFs are separately preserved byte-for-byte.'}
    (ROOT/'history/pdf_preservation.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');return d

def main():
    start=time.perf_counter();source=git('rev-parse','HEAD').decode().strip()
    science=validate_science();preserve_index()
    subprocess.run([sys.executable,str(ROOT/'replication/generate_tables.py')],cwd=REPO,check=True)
    reports=build();oldpdf=history_check();preserved=preservation()
    checks={'passed':True,'source_commit':source,'scientific_checks':science,'pdfs':reports,'historical_pdf_pages':oldpdf['annex_pages'],'inherited_files_checked':preserved['inherited_files'],'seconds':time.perf_counter()-start,'renderer':fitz.__doc__,'scope':'Programmatic PDF/build checks; manual visual preparation review is separately documented.'}
    (ROOT/'results/publication_checks.json').write_text(json.dumps(checks,sort_keys=True,indent=2)+'\n')
    files={}
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.name!='PUBLICATION_MANIFEST.json':files[str(p.relative_to(REPO))]=sha(p)
    for name in NAMES:
        for ext in ('tex','pdf'):p=REPO/f'{name}_R38.{ext}';files[p.name]=sha(p)
    for name in ('R38_REVIEW.md','REVISION_INDEX.md'):files[name]=sha(REPO/name)
    manifest={'stage':'completed scientific execution and completed five-PDF publication','passed':True,'source_commit':source,'base_review_commit':BASE,'scientific_source_commit':'c65cb2d62b0c1673191bd1fd7092dcb94068a3cf','scientific_result_commit':SCIENCE_COMMIT,'scientific_workflow_run':'36026482259','publication_workflow_run':os.environ.get('GITHUB_RUN_ID','local'),'branch':BRANCH,'files':files,'pdfs':reports,'exact_objects':187,'independent_primary':42,'independent_frontiers':70,'mutations_rejected':20,'provenance_note':'The final Git commit containing this manifest identifies the complete review object; the manifest cannot include its own commit hash.'}
    (ROOT/'PUBLICATION_MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    print('Completed all publication checks',flush=True)
if __name__=='__main__':main()
