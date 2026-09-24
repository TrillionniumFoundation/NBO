"""Attach the local randomized LP to nonzero full-horizon support floors.
All three actions enter; the same uniform-initial randomized objective is bounded.
Whole-cell constant LP data give a downward dyadic bound, not a point sample.
"""
from randomized_primary import *

def local_value(q,z,b):
    vals=[z[a] for a in range(3) if q[a]>=b]
    for a in range(3):
        for c in range(3):
            if q[a]<b<q[c]:vals.append(((q[c]-b)*z[a]+(b-q[a])*z[c])/(q[c]-q[a]))
    assert vals
    return min(vals)

def lower_boxes(raw,V,support,eps,N):
    T=len(raw);grids=[None]*T+[{'xs':[Z,O],'lower':[0]}]
    for t in reversed(range(T)):
        qs=k.q_functions(V[t+1]);fs=[raw[t],V[t],support[t]]+qs
        xs=sorted({F(j,N) for j in range(N+1)}|{x for f in fs for x in f.xs})
        ng=grids[t+1];cl=[];chosen=[]
        for l,r in zip(xs,xs[1:]):
            mid=(l+r)/2;a0=int(raw[t].at(mid));target=min(affine_value(V[t].line(mid),x) for x in (l,r))-eps
            qu=[max(affine_value(q.line(mid),x) for x in (l,r)) for q in qs]
            z=[]
            for a in range(3):
                vals=[]
                for m,c in k.MAPS[a]:
                    il=max(0,bisect_right(ng['xs'],m*l+c)-1);ir=min(len(ng['lower'])-1,bisect_left(ng['xs'],m*r+c)-1)
                    assert il<=ir;vals.append(min(ng['lower'][il:ir+1]))
                cont=19*(3*vals[0]+2*vals[1])//100
                z.append(F(cont)+(floor((1+l)*S) if a!=a0 else 0))
            lp=floor(local_value(qu,z,target));fl=floor(S*min(affine_value(support[t].line(mid),x) for x in (l,r)))
            cl.append(max(0,lp,fl));chosen.append('lp' if lp>fl else 'support')
        grids[t]={'xs':xs,'lower':cl,'active':chosen}
    integrals={}
    g=grids[0]
    for name in ('uniform','high_condition','low_condition'):
        val=0
        for l,r,cl in zip(g['xs'],g['xs'][1:],g['lower']):
            mass=r-l if name=='uniform' else r*r-l*l if name=='high_condition' else 2*(r-l)-(r*r-l*l)
            val+=floor(cl*mass)
        integrals[name]=F(val,S)
    return grids,integrals

def run(N=1024):
    primary=read(OLD/'results/primary.json')['outcomes'];diag=read(OLD/'results/gap_study.json')['outcomes'];dm={(v['T'],v['proposal'],v['epsilon']):v for v in diag}
    random=read(ROOT/'results/randomized_primary.json')['outcomes'];rm={(v['T'],v['proposal'],v['epsilon']):v for v in random};rows=[]
    for row in sorted(primary,key=lambda z:(z['T'],z['proposal'],F(z['epsilon']))):
        tic=time.perf_counter();key=(row['T'],row['proposal'],row['epsilon']);base=read(OLD/'results'/row['proof_file']);d=dm[key];rr=rm[key]
        source=OLD/'results'/d['proof_file'];gf=read(source);support=list(map(k.PW.load,gf['B_V_refined']));raw=list(map(k.PW.load,base['raw']));V=list(map(k.PW.load,base['V']))
        grids,integrals=lower_boxes(raw,V,support,F(row['epsilon']),N);scopes={}
        for name,old in rr['initial_bounds'].items():
            lo=max(integrals[name],F(old['lower']));up=F(old['upper']);assert lo<=up
            scopes[name]={**old,'lower':str(lo),'gap':str(up-lo),'relative_gap':str((up-lo)/up) if up else '0',
                           'local_support_improvement':str(lo-F(old['lower']))}
        filename=f"restart_H{row['T']}_{row['proposal']}_eps{row['epsilon'].replace('/','_')}.json.gz"
        proof={'schema':'NBO-R39-primary-restart-v1','scale':S,'mesh':N,'T':row['T'],'epsilon':row['epsilon'],'proposal':row['proposal'],
               'grids':grids,'V':base['V'],'raw':base['raw'],'support':[v.dump() for v in support],
               'support_source':str(source.relative_to(ROOT.parents[1])),'support_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
               'initial_lower':integrals,'integral_scope':'absolutely_continuous_initial; positive affine maps preserve finite null sets'}
        p=ROOT/'results/restart'/filename;save(p,proof)
        out={'T':row['T'],'epsilon':row['epsilon'],'proposal':row['proposal'],'initial_bounds':scopes,'mesh':N,
             'proof_file':'restart/'+filename,'proof_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
             'seconds':time.perf_counter()-tic,'max_cells':max(len(v['lower']) for v in grids)}
        rows.append(out);save(ROOT/'results/primary_combined.json',{'outcomes':rows,'scope':'42 original continuous-state randomized Markov uniform objectives, plus two absolutely continuous initial-density sensitivities.'})
        z=scopes['uniform'];print(key,float(F(z['lower'])),float(F(z['upper'])),float(F(z['local_support_improvement'])),out['seconds'],flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--mesh',type=int,default=1024);args=ap.parse_args();run(args.mesh)
