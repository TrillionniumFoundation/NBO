"""Frozen 27-model controlled-density study; isolated run for each method.
The restricted comparator is an economic policy-class counterfactual, not
an external solver. Every cap failure is retained. No pilot model is counted.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,subprocess,sys,time,gzip,resource,platform
ROOT=Path(__file__).resolve().parent.parent

def models():
    centers={
      'A':dict(beta='3/4',eps='1/5',c='2',theta=['19/20','0'],g=['1/8','2/5'],h=['2/3','4/3'],k=['2/3','-1/4']),
      'B':dict(beta='3/4',eps='1/5',c='2',theta=['-19/20','1/2'],g=['1/4','5/4'],h=['3/8','1/24'],k=['5/4','1/8']),
      'C':dict(beta='3/4',eps='1/5',c='2',theta=['0','-19/20'],g=['3/8','1'],h=['1/2','7/6'],k=['11/8','-1/3'])}
    cells=[('A-base','A',{}),('A-beta05','A',{'beta':'1/2'}),('A-beta09','A',{'beta':'9/10'}),
           ('A-eps01','A',{'eps':'1/10'}),('A-eps03','A',{'eps':'3/10'}),
           ('A-no-control','A',{'theta':['0','0']}),('A-reverse','A',{'theta':['-19/20','0']}),
           ('B-base','B',{}),('C-base','C',{})]
    out=[]
    for cell,family,changes in cells:
        for seed in [5101,5102,5103]:
            d=json.loads(json.dumps(centers[family]));d.update(changes)
            # Common seed perturbations within a family keep OFAT comparisons paired.
            for key in ['g','h','k']:
                word=int(hashlib.sha256(f'NBO-R51:{family}:{seed}:{key}'.encode()).hexdigest()[:8],16)
                mult=1+F(word%21-10,200)
                d[key]=[str(F(x)*mult) for x in d[key]]
            d['id']=f'{cell}-{seed}';out.append(d)
    return out

def worker(raw,restricted):
    import controlled as c
    from check_controlled import check
    start=time.perf_counter();p=c.run(raw,F(1,1000),32767,12,restricted)
    name=raw['id']+('-uniform' if restricted else '-common')
    encoded=json.dumps(p,sort_keys=True,separators=(',',':')).encode()
    compressed=gzip.compress(encoded,mtime=0)
    (ROOT/'results'/f'{name}.json.gz').write_bytes(compressed)
    verification=check(json.loads(gzip.decompress(compressed)))
    allin=time.perf_counter()-start
    U,L=F(p['upper']),F(p['lower']);u,z=map(F,p['moment'])
    row={k:p[k] for k in ['raw','restricted','target','moment','lower','upper','width','construction_seconds','status','trace']}
    row.update(id=name,verification=verification,all_in_seconds=allin,nodes=len(p['nodes']),
               relative_width=float((U-L)/U),proof_bytes=len(compressed),raw_proof_bytes=len(encoded),
               peak_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
               moment_geometry='interior' if abs(z)<u*(1-u) and 0<u<1 else 'boundary',
               proof_sha256=hashlib.sha256(compressed).hexdigest())
    (ROOT/'results'/f'{name}.json').write_text(json.dumps(row,indent=2)+'\n')
    print(name,p['status'],float(U-L),len(p['nodes']),round(allin,4),flush=True)

def main():
    if len(sys.argv)>1:
        worker(json.loads(sys.argv[1]),sys.argv[2]=='1');return
    (ROOT/'results').mkdir(parents=True,exist_ok=True)
    design=models();(ROOT/'MODELS.json').write_text(json.dumps(design,indent=2)+'\n')
    for raw in design:
        for restricted in [False,True]:
            subprocess.run([sys.executable,__file__,json.dumps(raw),str(int(restricted))],check=True)
    rows=[json.loads(p.read_text()) for p in sorted((ROOT/'results').glob('*.json'))]
    common=[r for r in rows if not r['restricted']];uniform={r['raw']['id']:r for r in rows if r['restricted']}
    savings=[]
    for r in common:
        s=F(uniform[r['raw']['id']]['lower'])-F(r['upper'])
        savings.append({'model':r['raw']['id'],'certified_saving_lower':str(s),'strict':s>0})
    summary={'models':len(design),'runs':len(rows),'common_hits':sum(r['status']=='target' for r in common),
        'uniform_hits':sum(r['status']=='target' for r in rows if r['restricted']),
        'controlled_models':sum(any(F(t)!=0 for t in d['theta']) for d in design),
        'strict_common_continuation_savings':sum(r['strict'] for r in savings),'savings':savings,
        'max_common_width':max(float(F(r['width'])) for r in common),
        'all_in_seconds':sum(r['all_in_seconds'] for r in rows),'max_all_in_seconds':max(r['all_in_seconds'] for r in rows),
        'max_nodes':max(r['nodes'] for r in rows),'max_proof_bytes':max(r['proof_bytes'] for r in rows),
        'max_peak_mib':max(r['peak_mib'] for r in rows),'python':platform.python_version(),
        'claim_boundary':'two periods; proportional final implementation cost; designed primitives; no external scientific replication'}
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
if __name__=='__main__':main()
