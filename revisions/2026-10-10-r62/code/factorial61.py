"""Fresh native 2x2 factorial; same language, objective, lattice and tie rule."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import argparse,hashlib,json,os,random,statistics,subprocess,time,unittest
import search60 as u
import stress60 as st
import services60 as s
R=Path(__file__).resolve().parents[1];METHODS=('UE','RE','UP','RP')
FILES=('code/factorial61.py','FACTORIAL_PROTOCOL61.md')
def read(p):return json.loads(Path(p).read_text())
def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def need(c,m):
    if not c:raise AssertionError(m)
def save(p,v,exclusive=False):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x' if exclusive else 'w') as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def freeze():
    path=R/'audit/SOURCE_FREEZE61F.json'
    if path.exists():return verify()
    save(path,dict(files_sha256={x:digest(R/x) for x in FILES},parent_freeze_sha256=s.verify(),utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),scope='R61 native factorial frozen before any new production timing; old R60 results had been observed.'),True)
    return digest(path)
def verify():
    path=R/'audit/SOURCE_FREEZE61F.json';v=read(path);need(s.verify()==v['parent_freeze_sha256'],'R60 parent changed')
    for name,h in v['files_sha256'].items():need(digest(R/name)==h,'Factorial source changed: '+name)
    return digest(path)
def compile_native():
    (R/'build').mkdir(exist_ok=True);start=time.perf_counter();cmd=['g++','-O3','-std=c++17',str(R/'code/search60.cpp'),'-o',str(R/'build/native60')];subprocess.run(cmd,check=True,capture_output=True)
    return dict(seconds=time.perf_counter()-start,command=cmd,source_sha256=digest(R/'code/search60.cpp'),binary_sha256=digest(R/'build/native60'),compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0])
def original_reference(o,cap,Q):
    start=time.perf_counter();values=[o.value(F(j,Q)) for j in range(cap+1)];best=min(range(cap+1),key=lambda j:(values[j],j))
    return dict(index=best,objective_exact=str(values[best]),all_minimizers=[j for j,v in enumerate(values) if v==values[best]],seconds=time.perf_counter()-start)
def check(record,reference):need(record['index']==reference['index'] and F(record['objective_exact'])==F(reference['objective_exact']),'Wrong exact value or smallest minimizer')
def implement(o,cap,Q,method):
    if method not in METHODS:raise ValueError(method)
    start=time.perf_counter();active=o;offset=F(0)
    if method[0]=='R':active,offset=o.reduced(F(cap,Q))
    record=u.native(active,cap,Q,0 if method[1]=='E' else 1);record['objective_exact']=str(F(record['objective_exact'])+offset)
    need(o.value(F(record['index'],Q))==F(record['objective_exact']),'Original-objective postcheck')
    record.update(method=method,seconds=time.perf_counter()-start,original_ridges=len(o.features),active_ridges=len(active.features),offset_exact=str(offset));return record

def catalogue():
    out=[]
    for seed,width,size,regime in product(st.SEEDS,st.WIDTHS,st.SIZES,st.REGIMES):
        o,cap,Q=st.fixture(seed,width,size,regime);key=f's{seed}-m{width}-N{size}-{regime}'
        out.append(dict(key=key,seed=seed,width=width,size=size,regime=regime,objective=o,cap=cap,Q=Q,reference=original_reference(o,cap,Q)))
    return out

def batched(cases,method,batch_size):
    start=time.perf_counter();queries=[];offsets=[]
    for case in cases:
        active=case['objective'];offset=F(0)
        if method[0]=='R':active,offset=active.reduced(F(case['cap'],case['Q']))
        queries.append((active,case['cap'],case['Q'],0 if method[1]=='E' else 1,None));offsets.append(offset)
    values=[];indices=[];request=response=0;native_seconds=0.;exact=differences=0
    for begin in range(0,len(queries),batch_size):
        rows,work=u.native_batch(queries[begin:begin+batch_size]);request+=work['native_request_bytes'];response+=work['native_response_bytes'];native_seconds+=work['native_process_seconds']
        for j,row in enumerate(rows,begin):
            row['objective_exact']=str(F(row['objective_exact'])+offsets[j]);case=cases[j]
            need(case['objective'].value(F(row['index'],case['Q']))==F(row['objective_exact']),'Original batched objective postcheck')
            check(row,case['reference']);values.append(row['objective_exact']);indices.append(row['index']);exact+=row['exact_evaluations'];differences+=row['difference_queries']
    return dict(method=method,batch_size=batch_size,query_count=len(cases),seconds=time.perf_counter()-start,native_process_seconds=native_seconds,subprocesses=(len(cases)+batch_size-1)//batch_size,native_request_bytes=request,native_response_bytes=response,exact_evaluations=exact,difference_queries=differences,indices=indices,objective_exact=values)

def run(worker):
    fz=verify();root=R/'results61-factorial'/f'worker{worker}';root.mkdir(parents=True,exist_ok=False);begin=time.perf_counter();env=st.environment();compiler=compile_native();rng=random.Random(61631+worker);cases=catalogue();rows=[]
    for case in cases:
        order=list(METHODS);rng.shuffle(order);runs=[]
        for method in order:
            rec=implement(case['objective'],case['cap'],case['Q'],method);check(rec,case['reference']);runs.append(rec)
        row={k:v for k,v in case.items() if k!='objective'};row.update(objective=case['objective'].payload(),order=order,runs=runs);rows.append(row)
    repeated=[]
    for regime in st.REGIMES:
        case=next(x for x in cases if (x['seed'],x['width'],x['size'],x['regime'])==(60103,32,129,regime))
        for rep in range(7):
            order=list(METHODS);rng.shuffle(order);runs=[]
            for method in order:
                rec=implement(case['objective'],case['cap'],case['Q'],method);check(rec,case['reference']);runs.append(rec)
            repeated.append(dict(key=case['key'],regime=regime,rep=rep,order=order,runs=runs))
    batches=[]
    for size in (1,8,32):
        order=list(METHODS);rng.shuffle(order)
        for method in order:
            record=batched(cases,method,size);record['order']=order;batches.append(record)
    result=dict(status='passed',worker=worker,source_freeze_sha256=fz,environment=env,compiler=compiler,rows=rows,repetitions=repeated,batches=batches,reference_validation_seconds=sum(x['reference']['seconds'] for x in cases),seconds_through_execution=time.perf_counter()-begin,new_training_services=0,new_policy_cost_path_samples=0,scope='Fresh implementation-work observations on fixed rational objectives; all four cells use the same exact native engine, original postcheck and timing boundary. Host copies and repetitions are not independent economic samples. Batch timings are for the complete 90-query catalogue, not complete economic services.')
    save(root/'summary.json',result,True);print(json.dumps(dict(worker=worker,status='passed',instances=len(rows),repetitions=len(repeated),batch_runs=len(batches),seconds=result['seconds_through_execution'])),flush=True)

def audit():
    start=time.perf_counter();fz=verify();cases=catalogue();bykey={x['key']:x for x in cases};outputs=[];checked=0;aggregates=[];paired=[];batches=[]
    for worker in (0,1):
        file=R/'results61-factorial'/f'worker{worker}'/'summary.json';result=read(file)
        need(result['source_freeze_sha256']==fz and result['status']=='passed','Factorial source identity');need({x['key'] for x in result['rows']}==set(bykey) and len(result['rows'])==90,'Complete native factorial')
        for row in result['rows']:
            case=bykey[row['key']];need(row['objective']==case['objective'].payload(),'Unchanged rational objective')
            need(row['order']==[x['method'] for x in row['runs']] and set(row['order'])==set(METHODS),'All four randomized cells')
            for rec in row['runs']:check(rec,case['reference']);checked+=1
        need(len(result['repetitions'])==35,'Repeated subset completeness')
        for row in result['repetitions']:
            case=bykey[row['key']];need((case['seed'],case['width'],case['size'])==(60103,32,129),'Unselected repeated subset')
            for rec in row['runs']:check(rec,case['reference']);checked+=1
        need(len(result['batches'])==12,'Batch catalogue completeness')
        for row in result['batches']:
            need(row['batch_size'] in (1,8,32) and row['query_count']==90,'Batch contract')
            for case,index,value in zip(cases,row['indices'],row['objective_exact']):check(dict(index=index,objective_exact=value),case['reference']);checked+=1
            need(len(row['indices'])==len(row['objective_exact'])==90,'Complete batch answers')
            batches.append({k:v for k,v in dict(worker=worker,**row).items() if k not in ('indices','objective_exact')})
        for regime in st.REGIMES:
            agg=dict(worker=worker,regime=regime,methods={})
            for method in METHODS:
                vals=[r['seconds'] for x in result['repetitions'] if x['regime']==regime for r in x['runs'] if r['method']==method]
                agg['methods'][method]=dict(median_seconds=statistics.median(vals),minimum_seconds=min(vals),maximum_seconds=max(vals),repetitions=len(vals))
            aggregates.append(agg)
        for width,size in product(st.WIDTHS,st.SIZES):
            rows=[x for x in result['rows'] if x['width']==width and x['size']==size];ratios=[];wins=0
            for x in rows:
                bymethod={r['method']:r for r in x['runs']};a=bymethod['RE']['seconds'];b=bymethod['RP']['seconds'];ratios.append((a-b)/a);wins+=b<a
            paired.append(dict(worker=worker,width=width,size=size,instances=len(rows),reduced_piecewise_faster=wins,median_fraction_saved=statistics.median(ratios),minimum_fraction_saved=min(ratios),maximum_fraction_saved=max(ratios)))
        outputs.append(dict(worker=worker,summary_sha256=digest(file),environment=result['environment'],compiler=result['compiler']))
    out=dict(status='passed',source_freeze_sha256=fz,workers=2,distinct_rational_instances=90,checked_exact_answers=checked,repeated_subset=aggregates,reduced_representation_search_contrasts=paired,batches=batches,worker_records=outputs,seconds=time.perf_counter()-start,new_training_services=0,new_independent_policy_cost_samples=0,scope='Independent Fraction exhaustive validation of every original exact answer, all native factorial cells and batch outputs. Descriptive timing contrasts keep hosts and mathematical instances explicit; no clock is spliced into R60 prospective service work.')
    save(R/'audit/FACTORIAL_AUDIT61.json',out);print(json.dumps(out,indent=2),flush=True)

class Tests(unittest.TestCase):
    def test_four_cells_identical_on_disjoint_signed_fixture(self):
        o=u.Objective(F(-1,7),F(-1,3),F(4),[(F(5,9),F(-1,16),F(1),F(1,64)),(F(-2),F(2),F(-1),F(1,8))],[]);ref=original_reference(o,16,64)
        for method in METHODS:check(implement(o,16,64,method),ref)
    def test_four_cells_preserve_flat_tie(self):
        o=u.Objective(F(0),F(0),F(0),[(F(3),F(-1,16),F(1),F(1,64)),(F(-3),F(-1,16),F(1),F(1,64))],[])
        for method in METHODS:self.assertEqual(implement(o,16,64,method)['index'],0)
    def test_batch_sizes_preserve_every_answer(self):
        cases=[]
        for k in range(5):
            o=u.Objective(F(-k,13),F(1),F(4),[],[]);cases.append(dict(objective=o,cap=12,Q=64,reference=original_reference(o,12,64)))
        for method in METHODS:
            a=batched(cases,method,1);b=batched(cases,method,4);self.assertEqual(a['indices'],b['indices']);self.assertEqual(a['objective_exact'],b['objective_exact'])
    def test_reduction_does_not_change_value(self):
        o=u.Objective(F(1),F(1),F(4),[(F(-3),F(2),F(1),F(1,16))],[]);active,offset=o.reduced(F(1,4))
        for j in range(17):self.assertEqual(o.value(F(j,64)),active.value(F(j,64))+offset)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');parser.add_argument('--test',action='store_true');parser.add_argument('--audit',action='store_true');parser.add_argument('--worker',type=int);args=parser.parse_args()
    if args.freeze:print(freeze())
    elif args.test:compile_native();unittest.main(argv=['factorial61'],verbosity=2)
    elif args.audit:audit()
    elif args.worker in (0,1):run(args.worker)
    else:parser.error('Select --freeze, --test, --audit, or --worker 0/1')
