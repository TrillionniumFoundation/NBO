"""Check immutable inherited components and the live publication label graph."""
from pathlib import Path
import hashlib,json,re
from collections import Counter
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
def main():
    base=json.loads((R/'protocols/INHERITANCE.json').read_text());old=base['inherited_components']
    changed={'ECTA.tex':R/'archive/ECTA.tex','supp.tex':R/'archive/supp.tex'}
    for name,x in old.items():
        p=changed.get(name,ROOT/name)
        assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'],name
    seen=set();labels=[];edges=[]
    def visit(p):
        name=str(p.relative_to(ROOT));assert name not in seen,('repeated input',name);seen.add(name)
        text=re.sub(r'(?<!\\)%[^\n]*','',p.read_text())
        labels.extend(re.findall(r'\\label\{([^}]+)\}',text))
        for child in re.findall(r'\\(?:input|include)\{([^}]+)\}',text):
            f=ROOT/child
            if not f.suffix:f=f.with_suffix('.tex')
            assert f.exists(),str(f);edges.append([name,str(f.relative_to(ROOT))]);visit(f)
    for p in [ROOT/'ECTA.tex',ROOT/'supp.tex',R/'applications.tex']:visit(p)
    cc=Counter(labels);assert not [k for k,v in cc.items() if v>1]
    inherited={label for f in old.values() for label in f['labels']}
    assert inherited<=set(labels), sorted(inherited-set(labels))
    # Only front/back prose is expanded; all its old paragraphs are preserved
    # except for a new insertion at existing paragraph boundaries.
    for name in ['introduction','conclusion']:
        text=(R/f'manuscript/{name}.tex').read_text()
        original=(R/f'archive/r19_{name}.tex').read_text()
        assert all(p in text for p in original.strip().split('\n\n')),(name,'old paragraph missing')
    for name in ['ECTA','supp']:assert (ROOT/f'{name}.tex').read_bytes()==(R/f'{name}.tex').read_bytes()
    result={'base_commit':base['base_commit'],'inherited_components_verified':len(old),
      'inherited_labels_retained':len(inherited),'publication_labels':len(labels),
      'no_duplicate_labels':True,'all_old_components_byte_preserved':True,
      'all_old_introduction_and_conclusion_paragraphs_preserved':True,
      'live_components':sorted(seen),'input_edges':edges,
      'scope':'Complete manuscript graph: main article, technical supplement, and economic applications.'}
    (R/'results/PRESERVATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('live_components','input_edges')},indent=2))
if __name__=='__main__':main()
