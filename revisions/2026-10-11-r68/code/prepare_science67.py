"""One-time materialization of ordinary corrected R67 scientific sources."""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-10-r66'
NOTICE='''# R67 corrected source-frozen execution

This is a separately frozen rerun of all 212 R66 processes after an independent
rational trajectory check detected aliasing in the cumulative path-cost
interval. The inherited point constructor can share endpoint arrays; writing
a lower and then an upper endpoint in place overwrote the lower running total.
R67 allocates separate zero arrays. No Bellman kernel, model fitting rule,
proposal gate, target, workload or economic primitive is changed. Original R66
files, erroneous path lower endpoints and complete receipts remain unchanged.
The corrected service has its own source freeze and complete process clocks.

The random indices are unchanged to isolate the correction. R66 and R67 streams
must not be counted as independent datasets. Only the 16,384 distinct common-
path rows in the two corrected inference services enter the current cost
analysis, conditional on the frozen trained models. A rerun creates no extra
independent rows. The complete comparison, reuse and vector catalogues below
are repeated with the repaired accumulator, without selecting winners or seeds.
The original R66 protocol is reproduced below as the fixed design.

---

'''
EXTRA='''
class AccumulatorRegressionTests(unittest.TestCase):
    def test_point_endpoints_must_not_be_mutated_as_independent_buffers(self):
        z=s.I.point(np.zeros(3))
        self.assertTrue(np.shares_memory(z.lo,z.hi))
        fixed=s.I(np.zeros(3),np.zeros(3))
        self.assertFalse(np.shares_memory(fixed.lo,fixed.hi))
        fixed.lo[:]=-1.;fixed.hi[:]=1.
        self.assertTrue(np.all(fixed.lo==-1.))

    def test_repaired_path_contains_independent_rational_midpoint(self):
        F=s.F;B=s.B;den=2**s.BINBITS
        randoms,initial=s.workload(2,2,4,661204)
        trace,account=s.paths(k.Oracle('adaptive'),initial,randoms,2,'1/128')
        for row in range(4):
            x=[[F(0)]*2,[F(1)]*2,[F(1,4)]*2,[F(3,4)]*2][row];total=F(0)
            def cost(x,a=None):
                d=len(x);short=max(F(0),F(1,2)-2*sum(x)/d)
                value=(4 if a is None else 2)*sum((v-F(5,8))**2 for v in x)/d
                value+=sum((x[j]-x[(j+1)%d])**2 for j in range(d))/(4*d)+2*short**2
                return value if a is None else value+a*a+4*a**4
            for t in range(2):
                a=F(float(trace[f't{t}_action'][row]));total+=B**t*cost(x,a)
                z=F(2*int(randoms['shock_index'][t,row])+1,32*den)-F(1,32)
                x=[F(1,16)+F(9,16)*v+x[(j+1)%2]/8-v*x[(j+1)%2]/16+(F(1,2) if j%2==0 else F(1,4))*a+(z if j%2==0 else -z) for j,v in enumerate(x)]
            total+=B**2*cost(x)
            self.assertLessEqual(F(float(trace['cost_lo'][row])),total)
            self.assertLessEqual(total,F(float(trace['cost_hi'][row])))

'''
def main():
    if (R/'audit/SOURCE_FREEZE67.json').exists():raise FileExistsError('Scientific sources already frozen')
    for name in ('kernel66.py','vector66.py'):shutil.copy2(OLD/'code'/name,R/'code'/name)
    text=(OLD/'code/science66.py').read_text()
    for a,b in [('Prospectively frozen R66','Source-frozen R67 corrected'),('results66','results67'),('PROTOCOL66','PROTOCOL67'),('SOURCE_FREEZE66','SOURCE_FREEZE67'),('EXECUTION66','EXECUTION67'),('PROGRESS66','PROGRESS67'),("'science66.py','tests66.py'","'science67.py','tests67.py'")]:text=text.replace(a,b)
    old='cost=I.point(np.zeros(N));alive='
    if text.count(old)!=1:raise AssertionError('Expected accumulator not found')
    text=text.replace(old,'cost=I(np.zeros(N),np.zeros(N));alive=')
    text=text.replace('Before all declared new scientific services; development regression runs are not catalogue observations.','Before the corrected R67 rerun; same fixed streams as R66, not additional independent observations. Original R66 records remain unchanged.')
    (R/'code/science67.py').write_text(text)
    tests=(OLD/'code/tests66.py').read_text().replace('import science66 as s','import science67 as s')
    index=tests.index("if __name__")
    tests=tests[:index]+EXTRA+tests[index:]
    (R/'code/tests67.py').write_text(tests)
    (R/'PROTOCOL67.md').write_text(NOTICE+(OLD/'PROTOCOL66.md').read_text())
    (R/'audit').mkdir(exist_ok=True)
if __name__=='__main__':main()
