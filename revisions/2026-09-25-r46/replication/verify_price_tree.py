"""Independently check added price planes before reconstructing the R44 LP/tree.

The only imported scientific checker is the earlier standalone checker. No
optimizer, constructor, or new tree-building module is imported.
"""
from pathlib import Path
from fractions import Fraction as Q
import gzip,hashlib,importlib.util,json,sys,time
from verify_prices import verify as verify_price, expect
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'revisions/2026-09-25-r46';B=ROOT/'revisions/2026-09-25-r44'
spec=importlib.util.spec_from_file_location('independent_previous_checker',B/'replication/verify_tree.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
Original=prior.Reader

def verify(path):
    path=Path(path);obj=json.loads(gzip.decompress(path.read_bytes()));envelopes=[]
    expect(obj['r46_extension']=='certified-price-planes-v1','extension version')
    expect(len(obj['price_sources'])==2,'price source count')
    for item,label in zip(obj['price_sources'],['constant','restart']):
        expected=R/'proofs'/path.parent.name/f'{label}.json.gz'
        expect(item['path']==str(expected.relative_to(ROOT)),'price source path')
        expect(hashlib.sha256(expected.read_bytes()).hexdigest()==item['sha256'],'price source hash')
        verify_price(expected);proof=json.loads(gzip.decompress(expected.read_bytes()))
        expect(obj['model']==proof['model'],'tree/price model identity')
        envelopes.append(([[Q(x) for x in row] for row in proof['prices']],[[Q(x) for x in row] for row in proof['transformed_lower']]))
    class Reader(Original):
        def extremes(self,box):
            tables=super().extremes(box)
            if tables is not None:
                for t in range(self.T):
                    for i in range(self.n):tables[2][t][i]=max([tables[2][t][i]]+[u[t][i] for lam,u in envelopes])
            return tables
        def program(self,box,tab):
            lp=super().program(box,tab)
            if lp is not None:
                names,bounds,eq,ub,obj=lp
                for lam,u in envelopes:
                    for t in range(self.T):
                        for i in range(self.n):
                            row={names['S',t,i]:Q(1),names['D',t,i]:-lam[t][i]}
                            ub.append(({j:c for j,c in row.items() if c},self.H[t][i]-u[t][i]-lam[t][i]*self.e))
            return lp
    prior.Reader=Reader
    result=prior.verify(path,B/'models'/f'{path.parent.name}.json')
    result['price_sources_checked']=2
    return result

if __name__=='__main__':
    paths=list((R/'proofs').glob('*/price_*.json.gz')) if len(sys.argv)==1 else [Path(s) for s in sys.argv[1:]]
    data={str(p.relative_to(ROOT)):verify(p) for p in paths}
    (R/'results/independent_price_trees.json').write_text(json.dumps({'passed':True,'certificates':len(data),'results':data},indent=2)+'\n')
    print('Checked',len(data),'price-strengthened covers.')
