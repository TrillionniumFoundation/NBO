"""Copy immutable R58 development inputs and inspect all 36 frozen services.
This preparatory description is not the independent solver/certificate replay.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,shutil,statistics,sys
R=Path(__file__).resolve().parents[1];BASE=R.parent/'2026-10-09-r58'
BASE_SHA='4b5f1cc3241fe8df103844f225913d91c387795b'
REVIEW_SHA='adf1256cff9cde365246a3db2dac90c72fda3b13'

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def main():
    marker=R/'audit/PREPARATION59.json'
    if not marker.exists():
        own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file()}
        shutil.copytree(BASE,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','build'))
        for n,v in own.items():p=R/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
        docs=('ECTA','supp','complete','complete-supp','development','development-supp')
        sys.path.insert(0,str(R/'code'));from assemble56 import labels
        labelsets={d:labels(BASE,d) for d in docs}
        preserved=R/'preserved/R58-before-R59';preserved.mkdir(parents=True,exist_ok=True)
        for n in [*(d+'.tex' for d in docs),'response.md','README.md']:
            shutil.copy2(BASE/n,preserved/n)
        retained={}
        for folder in ('code','results','results52','results53','results53-extension','results55','results55-tube','results57','results58','attempts','evidence','inputs','preserved'):
            for p in (BASE/folder).rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts:
                    n=str(p.relative_to(BASE));h=digest(p)
                    if digest(R/n)!=h:raise AssertionError('Inherited file differs: '+n)
                    retained[n]=h
        save(marker,dict(baseline_commit=BASE_SHA,controlling_review_commit=REVIEW_SHA,baseline_labels=labelsets,retained_sha256=retained,old_branches_changed=False))
    out=R/'results58';clocks={}
    for f in sorted(out.glob('process-clocks-*.json')):
        for row in read(f)['runs']:clocks[row['key']]=row
    rows=[]
    for folder in sorted((out/'services').iterdir()):
        if not folder.is_dir():continue
        s=read(folder/'service.json');clock=clocks[s['key']];last=s['stages'][-1];look=read(folder/f"stage{last['stage']}-look{last['look_paths'][-1]}.json")
        rows.append(dict(key=s['key'],d=s['d'],T=s['T'],target=s['target'],mode=s['mode'],rep=s['repetition'],status=s['status'],stages=len(s['stages']),policy=s['final_policy_sha256'],parameters=[x['critic_parameters_sha256'] for x in s['stages']],cost=look['cost']['interval'],gain=look['gain']['interval'],target_contrast=look['target_contrast']['interval'],looks=[x['look_paths'] for x in s['stages']],process_seconds=clock['whole_process_seconds'],search_seconds=sum(x['action_search_seconds'] for x in s['stages']),fit_seconds=sum(x['construction_seconds'] for x in s['stages']),verification_seconds=sum(x['verification_seconds'] for x in s['stages']),bytes=clock['serialized_bytes'],rss_kib=s['peak_rss_kib'],neural_queries=sum(x['neural_searches'] for x in s['stages']),root_isolations=sum(x['neural_root_isolations'] for x in s['stages']),exact_evaluations=sum(x['neural_exact_evaluations'] for x in s['stages']),screened_points=sum(x['neural_screened_points'] for x in s['stages']),retained_points=sum(x['neural_retained_points'] for x in s['stages']),active_ridges=sum(x['neural_active_ridges'] for x in s['stages']),eliminated_ridges=sum(x['neural_eliminated_ridges'] for x in s['stages']),fallbacks=sum(x['fallbacks'] for x in s['stages']),nonterminal_changes=sum(z['changed'] for x in s['stages'] for z in x['dates'][:-1])))
    groups=[]
    for d,T in ((2,2),(4,4),(8,6)):
        for q in ('9/10','4/5'):
            a=[r for r in rows if (r['d'],r['T'],r['target'],r['mode'])==(d,T,q,'algebraic')];b=[r for r in rows if (r['d'],r['T'],r['target'],r['mode'])==(d,T,q,'screened')]
            if len(a)!=3 or len(b)!=3:raise AssertionError('Incomplete repetitions')
            eq=all(all(x[k]==y[k] for k in ('policy','parameters','status','looks','cost','gain','target_contrast')) for x,y in zip(a,b))
            am=statistics.median(r['process_seconds'] for r in a);bm=statistics.median(r['process_seconds'] for r in b)
            groups.append(dict(d=d,T=T,target=q,identity=eq,status=a[0]['status'],algebraic_seconds=[r['process_seconds'] for r in a],screened_seconds=[r['process_seconds'] for r in b],algebraic_median=am,screened_median=bm,process_speedup=am/bm,algebraic_search_median=statistics.median(r['search_seconds'] for r in a),screened_search_median=statistics.median(r['search_seconds'] for r in b),cost=a[0]['cost'],gain=a[0]['gain'],target_contrast=a[0]['target_contrast'],algebraic_operations={k:a[0][k] for k in ('neural_queries','root_isolations','exact_evaluations')},screened_operations={k:b[0][k] for k in ('neural_queries','root_isolations','exact_evaluations','screened_points','retained_points','active_ridges','eliminated_ridges','fallbacks')}))
    inspection=dict(status='descriptive_inspection_only',services=len(rows),attained=sum(r['status']=='target_attained' for r in rows),exhausted=sum(r['status']=='budget_exhausted' for r in rows),all_recorded_matches=all(g['identity'] for g in groups),groups=groups,rows=rows)
    save(R/'audit/INSPECTION59.json',inspection)
    print(json.dumps({k:v for k,v in inspection.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
