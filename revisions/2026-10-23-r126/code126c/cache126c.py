"""Exact within-service envelope geometry reuse; no economic-query cache.

All inherited cases are immutable during a paid service. The cache owns strong
references to those cases and is destroyed on leaving the service context.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code126'))
from common126 import *
from bisect import bisect_right
from collections import Counter

REFERENCE_PRIMARY_SHA256='a780085786d8c1fcd6585f455b0a7b9489e9776a0b3955c773f2ba0feaf3251e'
VARIANTS=('uncached','cached')


def verify_sources():
    original=verify_inputs()
    manifest=ROOT/'SOURCE_FREEZE126C.json'; source=json.loads(manifest.read_text())
    for rel,entry in source['files'].items():
        digest=entry if isinstance(entry,str) else entry['sha256']
        if sha(ROOT/rel)!=digest: raise ValueError('R126C frozen byte mismatch: '+rel)
    boundary=json.loads((ROOT/'BOUNDARIES126C.json').read_text())
    if (not boundary.get('remote_source_readback_before_economics') or
        len(boundary['source_commit'])!=40 or boundary['source_manifest_sha256']!=sha(manifest)):
        raise ValueError('R126C complete remote source readback must precede economics')
    reference=ROOT/'results126/primary01/records126.jsonl.gz'
    if sha(reference)!=REFERENCE_PRIMARY_SHA256: raise ValueError('Original negative-cost primary evidence changed')
    return dict(original=original,files=len(source['files']),source_manifest_sha256=sha(manifest),boundaries=boundary,
                reference_primary_sha256=REFERENCE_PRIMARY_SHA256)


# Only clocks and declared design/run metadata are removed. All economics,
# query ledgers, certificates, counts, failures, menus and stop decisions remain.
_METADATA={'repeat','variant126c','cache_source_commit126c','cache_stats126c','paired_order126c'}
_CLOCKS={'clock','complete_seconds','complete_service_seconds126','seconds','seconds125','complete_service_seconds126c'}

def scientific(value):
    if isinstance(value,dict):
        return {k:scientific(v) for k,v in value.items() if k not in _METADATA and k not in _CLOCKS}
    if isinstance(value,list): return [scientific(v) for v in value]
    return value


def fingerprint(value):
    return hashlib.sha256(json.dumps(scientific(value),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


class ExactGeometry:
    def __init__(self,module):
        self.module=module
        self.original={name:getattr(module,name) for name in ('partition','contrast','gradient','envelope_root','support_minimum')}
        self.cases={}; self.ledgers={}; self.minima={}; self.counts=Counter()

    def __enter__(self):
        for name in self.original: setattr(self.module,name,getattr(self,name))
        return self

    def __exit__(self,kind,value,tb):
        for name,fn in self.original.items(): setattr(self.module,name,fn)
        self.cases.clear(); self.ledgers.clear(); self.minima.clear()

    def binding(self,case,subset=None):
        # Frozen callers never mutate case/payload contents. Strong references
        # prevent Python object-id reuse while the paid service is running.
        if subset is None:
            item=self.cases.get(id(case))
            if item is not None:
                self.counts['case_binding_hits']+=1
                return item[1]
        ps=case['payloads'] if subset is None else subset
        key=(F(case['A']),F(case['mu']),F(case['L']),
             tuple((F(p['a']),F(p['g_lower']),F(p['g_upper'])) for p in ps))
        if key not in self.ledgers:
            self.ledgers[key]=dict(case=case,subset=subset,parts={},roots={},gradients={})
            self.counts['distinct_geometry_ledgers']+=1
        ledger=self.ledgers[key]
        if subset is None:self.cases[id(case)]=(case,ledger)
        self.counts['case_bindings']+=1
        return ledger

    def geometry(self,case,upper,subset=None):
        ledger=self.binding(case,subset)
        if upper not in ledger['parts']:
            pieces=self.original['partition'](case,F(0),case['A'],upper,subset)
            prefix=[F(0)]
            for a,b,s,c in pieces: prefix.append(prefix[-1]+s*(b*b-a*a)/2+c*(b-a))
            ledger['parts'][upper]=dict(pieces=pieces,starts=[p[0] for p in pieces],prefix=prefix,primitive={F(0):F(0),F(case['A']):prefix[-1]})
            self.counts['full_domain_partition_builds']+=1
            self.counts['full_domain_pieces_built']+=len(pieces)
        return ledger['parts'][upper]

    def partition(self,case,lo,hi,upper,subset=None):
        lo,hi=F(lo),F(hi)
        if not 0<=lo<=hi<=case['A']:raise ValueError('Integral outside feasible domain')
        self.counts['partition_requests']+=1
        if lo==hi:return []
        g=self.geometry(case,upper,subset); pieces=g['pieces']
        i=max(0,bisect_right(g['starts'],lo)-1); answer=[]
        while i<len(pieces) and pieces[i][0]<hi:
            a,b,s,c=pieces[i]; left,right=max(a,lo),min(b,hi)
            if left<right:answer.append((left,right,s,c))
            i+=1
        self.counts['clipped_pieces_returned']+=len(answer)
        return answer

    def primitive(self,case,t,upper):
        t=F(t)
        if not 0<=t<=case['A']:raise ValueError('Primitive outside feasible domain')
        self.counts['primitive_requests']+=1
        g=self.geometry(case,upper)
        if t in g['primitive']:
            self.counts['primitive_hits']+=1
            return g['primitive'][t]
        i=max(0,bisect_right(g['starts'],t)-1)
        a,b,s,c=g['pieces'][i]
        result=g['prefix'][i]+s*(t*t-a*a)/2+c*(t-a)
        g['primitive'][t]=result
        self.counts['primitive_new_evaluations']+=1
        return result

    def contrast(self,case,origin,target,mode='fused'):
        self.counts['contrast_requests']+=1
        a,b=F(origin),F(target)
        if a==b:return F(0),F(0)
        if mode=='best_single':
            pairs=[self.contrast(dict(case,payloads=[p]),a,b,'fused') for p in case['payloads']]
            return max(x[0] for x in pairs),min(x[1] for x in pairs)
        if mode!='fused':raise ValueError('Unknown contrast mode')
        lower=self.primitive(case,b,False)-self.primitive(case,a,False)
        upper=self.primitive(case,b,True)-self.primitive(case,a,True)
        return (lower,upper) if a<b else (upper,lower)

    def gradient(self,case,b,upper):
        self.counts['gradient_requests']+=1
        b=F(b); ledger=self.binding(case); key=(b,upper)
        if key in ledger['gradients']:
            self.counts['gradient_hits']+=1
            return ledger['gradients'][key]
        if not 0<=b<=case['A']:raise ValueError('Gradient outside feasible domain')
        g=self.geometry(case,upper); i=max(0,bisect_right(g['starts'],b)-1)
        a,z,s,c=g['pieces'][i]; result=s*b+c
        ledger['gradients'][key]=result
        return result

    def envelope_root(self,case,upper):
        self.counts['root_requests']+=1
        ledger=self.binding(case)
        if upper in ledger['roots']:
            self.counts['root_hits']+=1
            return ledger['roots'][upper]
        A=case['A']
        if self.gradient(case,F(0),upper)>=0:result=F(0)
        elif self.gradient(case,A,upper)<=0:result=A
        else:
            result=None
            for a,b,s,c in self.geometry(case,upper)['pieces']:
                root=-c/s
                if a<=root<=b:result=root;break
            if result is None:raise ArithmeticError('A monotone derivative envelope lost its zero')
        ledger['roots'][upper]=result
        return result

    def support_minimum(self,case):
        self.counts['support_minimum_requests']+=1
        key=(F(case['A']),F(case['mu']),tuple(tuple(F(p[k]) for k in ('a','W','p_lower','p_upper')) for p in case['payloads']))
        if key not in self.minima:
            self.minima[key]=self.original['support_minimum'](case)
            self.counts['support_minimum_builds']+=1
        else:self.counts['support_minimum_hits']+=1
        return self.minima[key]


def self_test(output):
    sys.path.insert(0,str(R123/'code123'))
    import envelope123 as env
    points=[F(0),F(1,13),F(1,4),F(3,8),F(1,2),F(3,4),F(11,13),F(1)]
    checks=0; stats=Counter()
    for epsilon in (F(0),F(1,128),F(1,8)):
        ps=[]
        for a in (F(0),F(1,4),F(3,4),F(1)):
            g=2*a-F(3,4); value=(a-F(3,8))**2
            ps.append(dict(a=a,W=value-epsilon,U=value+epsilon,p_lower=g-epsilon,p_upper=g+epsilon,g_lower=g-epsilon,g_upper=g+epsilon))
        case=env.normalize(dict(A=F(1),mu=F(2),L=F(5),incumbent=F(1,4),delta=F(1,10000),tau=F(1),omega=F(1),old_optimum_lower=F(-1),payloads=ps))
        expected=[]
        for a in points:
            for b in points:
                for mode in ('fused','best_single'):expected.append(('contrast',(case,a,b,mode),env.contrast(case,a,b,mode)))
                if a<=b:
                    for upper in (False,True):expected.append(('partition',(case,a,b,upper),env.partition(case,a,b,upper)))
            for upper in (False,True):expected.append(('gradient',(case,a,upper),env.gradient(case,a,upper)))
        expected.extend([('envelope_root',(case,u),env.envelope_root(case,u)) for u in (False,True)])
        expected.append(('support_minimum',(case,),env.support_minimum(case)))
        expected.append(('candidate',(case,F(3,8),'fused'),env.candidate(case,F(3,8),'fused')))
        with ExactGeometry(env) as cache:
            for name,args,want in expected:
                assert getattr(env,name)(*args)==want,(epsilon,name,args[1:])
                checks+=1
            stats.update(cache.counts)
    write(output,dict(kind='synthetic rational cache identity fixtures before variant economics',checks=checks,
          original_economic_evaluations=0,source_sha256=sha(Path(__file__)),cache_counts=dict(stats)))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--self-test-output',required=True);a=p.parse_args();self_test(a.self_test_output)
