"""Independent finite properties and explicit adversarial tree mutations."""
from pathlib import Path
from fractions import Fraction as Q
import itertools,random,json,gzip,copy,tempfile,hashlib
from verify_tree import Reader,verify,ip,Z
from run_case import frozen,write
from models import tie
HERE=Path(__file__).resolve().parents[1]

def properties():
    raw=json.loads(json.dumps(tie('0',n=2,T=2),default=str)); reader=Reader(raw,True)
    tested=0; inequalities=0
    policies=[]
    for choices in itertools.product(range(3),repeat=4):
        policies.append([[[Q(int(a==choices[2*t+i])) for a in range(3)] for i in range(2)] for t in range(2)])
    rng=random.Random(440000)
    for _ in range(64):
        pp=[]
        for t in range(2):
            period=[]
            for i in range(2):
                w=[rng.randrange(1,10) for a in range(3)];period.append([Q(x,sum(w)) for x in w])
            pp.append(period)
        policies.append(pp)
    # Test the transformed inequalities on every deterministic short policy
    # plus fixed mixed policies, whether operating-feasible or not.
    for pp in policies:
        D=[Z]*2;S=[Z]*2;J=reader.g;C=[Z]*2
        for t in reversed(range(2)):
            nd=[];ns=[];nj=[];nc=[]
            for i in range(2):
                p=pp[t][i]
                d=ip(p,[reader.d[t,i,a]+reader.b*ip(reader.P[i][a],D) for a in range(3)])
                s=ip(p,[reader.s[t,i,a]+reader.b*ip(reader.P[i][a],S) for a in range(3)])
                j=ip(p,[reader.r[i][a]+reader.b*ip(reader.P[i][a],J) for a in range(3)])
                c=ip(p,[reader.k[i][a]+reader.b*ip(reader.P[i][a],C) for a in range(3)])
                assert d==reader.V[t][i]-j and s==reader.H[t][i]-c
                for lam,lo,hi in reader.envelopes:
                    assert lo[t][i]<=s-lam*d<=hi[t][i];inequalities+=2
                nd.append(d);ns.append(s);nj.append(j);nc.append(c)
            D,S,J,C=nd,ns,nj,nc
        tested+=1
    return dict(passed=True,deterministic_policies=81,mixed_policies=64,transformed_policy_checks=tested,support_inequalities=inequalities,exact_operating_tie=True,analytic_proof_status='finite property tests, not a machine-checked general theorem')

def mutations(path,expected):
    original=json.loads(gzip.decompress(Path(path).read_bytes()))
    changes=[]
    def add(label,fn): changes.append((label,fn))
    add('forged upper endpoint',lambda o:o.__setitem__('upper',str(Q(o['upper'])+1)))
    add('forged lower endpoint',lambda o:o.__setitem__('lower',str(Q(o['lower'])+1)))
    add('negative deployed probability',lambda o:o['policy'][0][0].__setitem__(0,'-1'))
    add('negative inequality multiplier',lambda o:o['tree'][0]['ineq_dual'].__setitem__(0,'-1'))
    add('nonstochastic transition row',lambda o:o['model']['P'][0][0].__setitem__(0,'2'))
    add('altered discount',lambda o:o['model'].__setitem__('beta','1/2'))
    add('wrong LP dimension',lambda o:o['tree'][0].__setitem__('variables',0))
    add('truncated equality certificate',lambda o:o['tree'][0]['eq_dual'].pop())
    add('false target status',lambda o:o['summary'].__setitem__('target_met',not o['summary']['target_met']))
    add('incorrect primitive action disadvantage',lambda o:o['model']['r'][0].__setitem__(0,'100'))
    add('swapped primitive action labels',lambda o:o['model']['r'][0].reverse())
    add('malformed probability/product box',lambda o:o['tree'][0]['box'][0].__setitem__(1,'2'))
    add('forged repaired action row',lambda o:o['policy'][0][0].__setitem__(0,'1'))
    add('omitted tree leaf',lambda o:o['tree'].pop())
    split=next((i for i,v in enumerate(original['tree']) if v['kind']=='split'),None)
    if split is not None:
        add('missing sibling',lambda o:o['tree'][split]['children'].pop())
        add('cover gap at a cut',lambda o:o['tree'][split].__setitem__('cut','0'))
        add('cyclic tree',lambda o:o['tree'][split]['children'].__setitem__(0,split))
    answers=[]
    with tempfile.TemporaryDirectory() as tmp:
        for label,fn in changes:
            obj=copy.deepcopy(original);fn(obj);q=Path(tmp)/'mutated.json.gz';q.write_bytes(gzip.compress(json.dumps(obj).encode(),mtime=0))
            rejected=False;error=None
            try:verify(q,expected)
            except (AssertionError,ValueError,IndexError,KeyError,TypeError) as exc:rejected=True;error=type(exc).__name__
            answers.append(dict(mutation=label,rejected=rejected,error=error));assert rejected,label
    return answers

def main():
    frozen();write(HERE/'results'/'property_tests.json',properties())
    candidates=sorted((HERE/'proofs').glob('*/bellman.json.gz'))
    assert candidates,'run the frozen case suite first'
    # Select by tree structure, not by economic success or interval width.
    path=next((p for p in candidates if any(x['kind']=='split' for x in json.loads(gzip.decompress(p.read_bytes()))['tree'])),candidates[0])
    name=path.parent.name;res=mutations(path,HERE/'models'/f'{name}.json')
    write(HERE/'results'/'mutations.json',dict(source_case=name,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),tests=res,all_rejected=all(x['rejected'] for x in res)))

if __name__=='__main__':main()
