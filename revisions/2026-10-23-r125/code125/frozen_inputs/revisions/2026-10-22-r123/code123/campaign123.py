"""Prospective R123 draw and complete catalogue; no selection after outcomes."""
import argparse,gzip,hashlib,json,os,time
from common123 import *

def sample(out,b):
    raw=os.urandom(320);(out/'entropy123.bin').write_bytes(raw)
    data=[]
    for j in range(N):
        ns=[int.from_bytes(raw[(2*j+k)*5:(2*j+k+1)*5],'little') for k in range(2)]
        x=[n/2**40 for n in ns]
        data.append(dict(row=j,integers=ns,state=x,state_hex=[v.hex() for v in x]))
    write(out/'states123.json',dict(source_commit=b['source_commit'],distribution='32 independent pairs of uniform 40-bit dyadic coordinates; duplicates retained',states=data))
    return dict(states=N,entropy_bytes=len(raw),entropy_sha256=digest(out/'entropy123.bin'),states_sha256=digest(out/'states123.json'))

def execute(out,b,kind,repeat):
    import service123 as svc
    svc.configure()
    data=json.loads((ROOT/'results123/states/states123.json').read_text())['states']
    if len(data)!=32:raise ValueError('Fixed complete state census required')
    n=32 if kind=='primary' else 16
    catalogue=groups();offset=0 if kind=='primary' else (11*repeat)%len(catalogue)
    catalogue=catalogue[offset:]+catalogue[:offset]
    count=0
    with gzip.open(out/'records123.jsonl.gz','xt',compresslevel=6) as stream:
        for k in catalogue:
            tick=time.perf_counter();load=time.perf_counter();p=model_path(k)
            model=None if p is None else json.loads(p.read_text())
            load_seconds=time.perf_counter()-load
            group=dict(zip(FIELDS,k));i,budget,arm,loss,mode=k
            for state in data[:n]:
                row=svc.service(state['state'],(.5,.75)[i],model,mode)
                row.update(group,row=state['row'],alpha=(.5,.75)[i],source_commit=b['source_commit'],state_commit=b['state_commit'],
                           population_observation=kind=='primary',repeat=None if kind=='primary' else repeat)
                if row['state_hex']!=state['state_hex'] or not row['qualified']:raise ArithmeticError('Invalid original state or qualification')
                stream.write(json.dumps(serial(row),sort_keys=True,allow_nan=False)+'\n');count+=1
            stream.flush()
            cohort=dict(group,seconds=time.perf_counter()-tick,load_seconds=load_seconds,records=n,n=n,
                        model_sha256=None if p is None else digest(p),model_bytes=0 if p is None else p.stat().st_size)
            append(out/'cohorts123.jsonl',cohort)
            print(json.dumps(dict(group,complete_rows=count,cohort_seconds=cohort['seconds'])),flush=True)
    return dict(records=count,cohorts=len(catalogue),states=n,records_sha256=digest(out/'records123.jsonl.gz'),
                all_declared_methods_states_and_refusals_retained=True,source_commit=b['source_commit'],state_commit=b['state_commit'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('kind',choices=['sample','primary','timing']);ap.add_argument('--repeat',type=int,default=0);ap.add_argument('--output',required=True);a=ap.parse_args()
    out,tick,initial=start(a.output,a.kind)
    try:
        source=verify_source();b=boundaries(a.kind!='sample')
        extra=sample(out,b) if a.kind=='sample' else execute(out,b,a.kind,a.repeat)
        finish(out,tick,initial,source=source,**extra)
    except BaseException:failed(out,tick);raise

if __name__=='__main__':main()
