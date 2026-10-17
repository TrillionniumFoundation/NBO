"""Additional exact theorem and release regressions, not new scientific services."""
from pathlib import Path
from fractions import Fraction as F
import itertools,json,math,re,unittest
from certificates72 import Witness,transport,repair,capacity,moduli
R=Path(__file__).resolve().parents[1]
class ReleaseTests(unittest.TestCase):
    def test_capacity_repair_bound(self):
        for m,d in itertools.product((1,2),(2,8)):
            for n in range(17):
                y=tuple([F(n,16)]*d);x=tuple([F(16-n,16)]*d);q=F(1,2**12)
                a=tuple([F(math.floor(capacity(y)/m/q),2**12)]*m)
                new=repair(a,capacity(x),12);D=sum(abs(p-t) for p,t in zip(x,y));move=sum(abs(p-t) for p,t in zip(new,a))
                self.assertLessEqual(move,D/(8*d)+(m+1)*q)
    def test_positive_fill_radius_closes(self):
        d=2;m=2;r=3;delta=F(1,32);gamma=F(1,2);q=F(1,2**32);lv,lx,la=moduli(r,d)
        rho=((1-gamma)*delta-la*(m+1)*q)/(lv+lx+la/F(8*d))
        self.assertGreater(rho,0)
        y=(F(1,2),F(1,2));a=repair((F(1,8),F(1,16)),capacity(y));w=Witness(y,a,F(1),F(1)+gamma*delta,r,'law')
        for fraction in (F(0),F(1,4),F(1,2),F(1)):
            x=(y[0]-fraction*rho,y[1]);self.assertIsNotNone(transport(w,x,delta,'law'))
    def test_grid_packing_diameter(self):
        for d in (1,2,8):
            for rho in (F(1,3),F(3,2),F(17)):
                n=math.ceil(d/rho);self.assertLessEqual(F(d,n),rho);self.assertLessEqual(n**d,(1+F(d)/rho)**d)
    def test_every_prior_active_section_has_one_assignment(self):
        import hashlib
        a=json.loads((R/'audit/PREPARATION72.json').read_text())
        unchanged=a['unchanged_active_sections'];amended=a.get('amended_active_sections',{})
        self.assertFalse(set(unchanged)&set(amended))
        original=json.loads((R/'preserved/R95-source/PREPARATION72-failed-in-R95.json').read_text())
        self.assertEqual(set(unchanged)|set(amended),set(original['unchanged_active_sections']))
        for path,record in dict(unchanged,**amended).items():
            count=sum((R/(doc+'.tex')).read_text().count('\\input{'+path[:-4]+'}') for doc in ('ECTA','supp','appendix'))
            self.assertEqual(count,1)
            self.assertEqual(hashlib.sha256((R/path).read_bytes()).hexdigest(),record['sha256'])
            if path in amended:
                self.assertTrue(record['reason'])
                self.assertEqual(record['original_sha256'],original['unchanged_active_sections'][path]['sha256'])
                self.assertEqual(hashlib.sha256((R/record['original_path']).read_bytes()).hexdigest(),record['original_sha256'])
    def test_new_theorem_proofs_and_reference_keys(self):
        source='\n'.join((R/'sections'/p).read_text() for p in ('frozen72.tex','reuse72.tex','proofs72.tex'))
        for key in ('thm:frozen72','prop:moment72','thm:reuse72','prop:cover72'):
            self.assertEqual(source.count('\\label{'+key+'}'),1);self.assertIn('\\ref{'+key+'}',source)
        self.assertIn('munos2006variance',json.loads((R/'publication/bibliography-entries.json').read_text()))
    def test_control_character_guard_on_derived_tables(self):
        for p in (R/'tables').glob('*72.tex'):
            self.assertFalse(any(ord(c)<32 and c not in '\t\n\r' for c in p.read_text()),p.name)
if __name__=='__main__':unittest.main(verbosity=2)
