"""Assemble immutable predecessors for R61; no scientific execution or rewriting."""
from pathlib import Path
from fractions import Fraction
import hashlib,json,shutil,statistics,sys
R=Path(__file__).resolve().parents[1]
BASE='00412e6a4f43100996b324ea1ace097232c3fbbf'
SCIENCE='c55d18af14ee1573a8e356021d2326fae703cd23'
CENTER='e94a8b867d6136ce14ba9697fc2288e0c7a7bc48'
THEORY='16d90ad07879c61dacd63c6f79162d0f2303f7ad'
REVIEW='8f56a3ae24ef3ce4383d0e9d1d757bd3ed7378c6'
DOCS=('ECTA','supp','complete','complete-supp','development','development-supp')
def read(p):return json.loads(Path(p).read_text())
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def prepare(external):
    marker=R/'audit/PREPARATION61.json'
    if marker.exists():return
    old=R.parent/'2026-10-09-r59';science=R.parent/'2026-10-09-r60'
    own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file()}
    shutil.copytree(old,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(science,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    centered=external/'centered/revisions/2026-10-09-r60'
    for name in ('code/centered60.py','code/tests_centered60.py','CENTERED_BELLMAN_AMENDMENT60.md','audit/SOURCE_FREEZE60C.json'):
        shutil.copy2(centered/name,R/name)
    shutil.copytree(centered/'results60-centered',R/'results60-centered',dirs_exist_ok=True)
    for p in (external/'theory/revisions/2026-10-09-r60/sections').glob('*.tex'):shutil.copy2(p,R/'sections'/p.name)
    shutil.copytree(external/'review/reviews/2026-10-09-econometrica-numerical-methods-r59',R/'inputs/reviews/R59',dirs_exist_ok=True)
    for name,data in own.items():p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    shutil.rmtree(R/'build',ignore_errors=True);(R/'build').mkdir()
    preserved=R/'preserved/R59-before-R61';preserved.mkdir(parents=True,exist_ok=True)
    for name in [d+'.tex' for d in DOCS]+['response.md','README.md']:shutil.copy2(old/name,preserved/name)
    sys.path.insert(0,str(R/'code'));from assemble56 import labels
    protected={}
    prefixes=('code','sections','results','results52','results53','results53-extension','results55','results55-tube','results57','results58','inputs','evidence','preserved','attempts')
    for folder in prefixes:
        for p in (old/folder).rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts:continue
            name=str(p.relative_to(old));h=digest(p)
            if not (R/name).exists() or digest(R/name)!=h:raise AssertionError('Changed R59 content: '+name)
            protected[name]=h
    scientific={}
    for folder in ('results60','attempts/R60-first-run'):
        for p in (science/folder).rglob('*'):
            if p.is_file():
                name=str(p.relative_to(science));h=digest(p)
                if digest(R/name)!=h:raise AssertionError('Changed R60 result: '+name)
                scientific[name]=h
    for p in (R/'results60-centered').rglob('*'):
        if p.is_file():scientific[str(p.relative_to(R))]=digest(p)
    for name in ('STUDY_PROTOCOL60.md','RECORDING_AMENDMENT60.md','CENTERED_BELLMAN_AMENDMENT60.md','audit/SOURCE_FREEZE60.json','audit/SOURCE_FREEZE60B.json','audit/SOURCE_FREEZE60C.json'):
        scientific[name]=digest(R/name)
    for freeze in ('SOURCE_FREEZE60.json','SOURCE_FREEZE60B.json','SOURCE_FREEZE60C.json'):
        for name,h in read(R/'audit'/freeze)['files_sha256'].items():
            if digest(R/name)!=h:raise AssertionError('Changed frozen source: '+name)
            scientific[name]=h
    save(marker,dict(baseline_commit=BASE,science_commit=SCIENCE,centered_commit=CENTER,theory_commit=THEORY,controlling_review_commit=REVIEW,protected_sha256=protected,scientific_sha256=scientific,baseline_labels={d:labels(old,d) for d in DOCS},scope='New R61 directory only. R59 manuscript and R60 scientific sources, all attempted records and completed outcomes preserved.'))
    (R/'README.md').write_text('# Neural Bellman Operators — R61\n\nRevision in verification. Completed publication requires audit/FINAL_DELIVERY61.json.\n')

def inspect():
    out={}
    for worker in (0,1):
        root=R/'results60'/f'worker{worker}';s=read(root/'stress/summary.json')
        methods=sorted({r['method'] for x in s['factorial'] for r in x['runs']})
        agg=[]
        for regime in ('mixed','crossing','cancellation','near-tie','flat'):
            for method in methods:
                rows=[r for x in s['factorial'] if x['regime']==regime for r in x['runs'] if r['method']==method]
                agg.append(dict(regime=regime,method=method,cases=len(rows),sum_seconds=sum(x['seconds'] for x in rows),median_seconds=statistics.median(x['seconds'] for x in rows),fallbacks=sum(x.get('fallback',False) for x in rows),maximum_survivors=max([0]+[x.get('screen_survivors',0) for x in rows]),maximum_bits=max([0]+[x.get('max_recorded_operand_bits',0) for x in rows]),maximum_pair_array_bytes=max([0]+[x.get('largest_single_pair_array_bytes',0) for x in rows])))
        pr=root/'prospective';cohort=read(pr/'cohort.json');services=[]
        for clock in cohort['runs']:
            folder=pr/'services'/clock['key'];v=read(folder/'service.json');last=v['stages'][-1];k=last['stage'];look=read(folder/f'stage{k}-look{last["look_paths"][-1]}.json')
            services.append(dict(key=clock['key'],mode=v['mode'],d=v['d'],T=v['T'],seed=v['seed'],target=v['target'],status=v['status'],stage=k,policy_sha256=v['final_policy_sha256'],critic_sha256=last['critic_parameters_sha256'],cost=look['cost'],gain=look['gain'],target_contrast=look['target_contrast'],complete_return_seconds=clock['complete_return_seconds'],cold_return_seconds=clock['cold_return_seconds'],maximum_loss_bound=max(map(lambda x:float(Fraction(x)),last['all_state_policy_loss_bound_exact'])),dates=last['dates'],stage_records=v['stages']))
        paired=[read(f) for f in sorted((pr/'paired').glob('*/paired.json'))]
        multi=read(root/'two-control/summary.json')
        bells=list(root.glob('**/*summary*.json'))
        out[str(worker)]=dict(stress_environment=s['environment'],stress_aggregate=agg,stress_example=s['factorial'][0],guards=s['fallback_frontier'],multi_rows=[{k:x[k] for k in ('seed','state','cap','Q','shocks','reference','adaptive')} for x in multi['rows']],services=services,paired=paired,cohort_environment=cohort.get('environment'),compile_record=cohort.get('compile_record'),summary_paths=[str(f.relative_to(R)) for f in bells])
    save(R/'audit/INSPECTION61.json',out)
    concise={w:{k:v[k] for k in ('stress_environment','stress_aggregate','multi_rows','cohort_environment','compile_record','summary_paths')} for w,v in out.items()}
    save(R/'audit/COMPACT_INSPECTION61.json',concise)
    print(json.dumps(dict(status='inputs_prepared',workers=2,services=sum(len(v['services']) for v in out.values()),new_scientific_runs=0)))
if __name__=='__main__':prepare(Path(sys.argv[1]));inspect()
