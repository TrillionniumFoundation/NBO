"""Independent finite rational regressions for R48; no study observations."""
import itertools, tempfile, unittest
from common import *
from tensor import Model
from service import adaptive_axes,nearest_excess,midpoint_sum,rung
from direct48 import moments,confidence,support,Policy,FAMILY,ALPHA,LOG
from diagnostics import sensor_curve

class ExactCompiler(unittest.TestCase):
    def compare(self,axes,labels,L):
        m=Model(axes,labels,'witness',L)
        for j in range(13):
            x=[F((j*(k+2)+1)%17,16) for k in range(len(axes))]
            truth,owner=m.exact(x);xf=np.array([list(map(float,x))]);q=m.point(xf)
            self.assertLessEqual(F(float(q.lo[0])),truth);self.assertLessEqual(truth,F(float(q.hi[0])))
            a,_=m.actor(I.point(xf),np.arange(m.S,dtype=float))
            self.assertEqual(a.lo[0],owner);self.assertEqual(a.hi[0],owner)
        return m
    def test_dimension_one(self):self.compare([[0,.25,.5,1]],[1,-2,3,0],F(5,4))
    def test_dimension_two(self):self.compare([[0,.5,1]]*2,[1,-2,3,0,1,4,-1,2,0],F(3,2))
    def test_dimension_three(self):self.compare([[0,.5,1]]*3,[(i*7)%11-5 for i in range(27)],F(3))
    def test_dimension_four(self):self.compare([[0,1]]*4,[(i*3)%7-3 for i in range(16)],F(2))
    def test_nonuniform_axes(self):self.compare([[0,.125,.75,1],[0,.5,1]],[i%5 for i in range(12)],F(7,3))
    def test_zero_slope_lowest_original_owner(self):
        m=self.compare([[0,.5,1]]*2,[3,0,1,0,2,0,1,2,0],F(0));self.assertTrue(np.all(m.owners==1))
    def test_dominated_labels_keep_original_witness(self):
        m=self.compare([[0,.5,1]],[0,100,100],F(1));self.assertEqual(m.owners.tolist(),[0,0,0])
    def test_exact_switch_tie(self):
        m=Model([[0,1]],[0,0],'witness',F(1));a,_=m.actor(I.point([[.5]]),[3,7]);self.assertEqual(a.lo[0],3)
    def test_switch_box_encloses_both_actions(self):
        m=Model([[0,1]],[0,0],'witness',1);a,amb=m.actor(I([[.49]],[[.51]]),[3,7]);self.assertEqual((a.lo[0],a.hi[0],amb),(3,7,1))
    def test_closed_corner_and_far_owner(self):
        m=self.compare([[0,.5,1]]*2,[100,100,100,100,100,100,100,100,-10],1);self.assertTrue(np.all(m.owners==8))
    def test_metric_closure_lipschitz(self):
        m=Model([[0,.25,.5,.75,1]]*2,[(j*11)%19 for j in range(25)],'witness',F(7,3))
        z=np.array(m.z,dtype=object).reshape(5,5)
        for j in (0,1):self.assertTrue(all(abs(v)<=m.L/4 for v in np.diff(z,axis=j).ravel()))
    def test_preprocessing_and_query_counts(self):
        m=Model([[0,.5,1]]*3,[i%4 for i in range(27)],'witness',1)
        self.assertEqual(m.counts['transform_relaxations'],108)
        m.point(np.full((10,3),.2));self.assertEqual(m.counts['corner_terms'],80)
    def test_roundtrip_compilation(self):
        m=Model([[0,.5,1]]*2,list(range(9)),'witness',F(3,2));n=Model.load(m.payload());self.assertEqual(n.payload(),m.payload())
    def test_bilinear_exact_polynomial(self):
        axes=[[0,.5,1]]*2;nodes=list(itertools.product(*axes));m=Model(axes,[1+x+2*y+3*x*y for x,y in nodes],'fvi')
        for x,y in itertools.product([F(1,8),F(3,8),F(7,8)],repeat=2):
            q=m.point([[float(x),float(y)]]);v=1+x+2*y+3*x*y
            self.assertLessEqual(F(float(q.lo[0])),v);self.assertGreaterEqual(F(float(q.hi[0])),v)
    def test_nearest_tie(self):
        m=Model([[0,1],[0,1]],[0,0,0,0],'fvi');a,_=m.actor(I.point([[.5,.5]]),[1,2,3,4]);self.assertEqual(a.lo[0],1)
    def test_nearest_vertex_bound(self):
        m=Model([[0,.25,1],[0,.5,1]],[i%4 for i in range(9)],'fvi');bound,_=nearest_excess(m,F(6))
        for x,y in itertools.product(np.arange(17)/16,repeat=2):
            node=[np.argmin(abs(ax-z)) for ax,z in zip(m.axes,(x,y))];i=np.ravel_multi_index(node,m.shape)
            val=m.point([[x,y]])
            excess=F(float(m.v[i]))+6*sum(abs(F(float(z))-F(float(v))) for z,v in zip((x,y),m.nodes[i]))-F(float(val.hi[0]))
            self.assertLessEqual(excess,bound)
    def test_adaptive_grid_and_actual_cover(self):
        a,w=adaptive_axes(np.arange(25).reshape(5,5)**2,[[0,.25,.5,.75,1]]*2,16)
        self.assertTrue(all(len(ax)==17 and np.all(np.diff(ax)>0) for ax in a))
        m=Model(a,np.zeros(289),'fvi');self.assertEqual(m.h,sum(F(float(np.max(np.diff(ax))))/2 for ax in a))
    def test_fast_sum_encloses_exact_sum(self):
        x=np.array([[.1,.2,-.4,1e-12],[1.,-1.,2.**-53,2.**-54]])
        q=midpoint_sum(I.point(x),1)
        for i,row in enumerate(x):
            truth=sum(map(lambda v:F(float(v)),row),F(0));self.assertLessEqual(F(float(q.lo[i])),truth);self.assertGreaterEqual(F(float(q.hi[i])),truth)
    def test_general_primitives_reduce_to_R47(self):
        x=I.point([[.125,.5],[.75,.25]]);a=I.point([.1,.2]);z=I.point([0.,1/64])
        sys.path.insert(0,str(P47/'code'));import constrained as old
        for aa,bb in [(costs(x,a,4),old.costs(x,a,4)),(transition(x,a,z),old.transition(x,a,z))]:
            self.assertTrue(np.all(aa.lo<=bb.hi) and np.all(bb.lo<=aa.hi))
    def test_general_domain_invariance(self):
        for d in (2,3,4):
            nodes=np.array(list(itertools.product((0.,1.),repeat=d)));capacity=cap(I.point(nodes))
            for z in (-1/32,1/32):
                v=transition(I.point(nodes),I.point(capacity.lo),I.point(np.full(len(nodes),z)))
                self.assertTrue(np.all(v.lo>=0) and np.all(v.hi<=1))
    def test_small_rung_identity_and_action_feasibility(self):
        for d in (2,3,4):
            r=rung(2,1,1,'compiled-witness',d)
            gap=sum(BETA**t*F(v['component']) for t,v in enumerate(r['rows']))+BETA**r['T']*F(r['terminal_width'])
            self.assertEqual(gap,F(r['policy_bound_exact']))
            for m,a in zip(r['models'],r['actors']):
                for x,u in zip(itertools.product(*m['axes']),a):self.assertLessEqual(F(float(u)),F(1,8)+sum(map(lambda v:F(float(v)),x),F(0))/F(8*d))
    def test_primitive_support(self):
        for T,p in itertools.product((2,3),(1,4)):
            a,b=support(T,p);self.assertEqual(a,-b);self.assertGreater(b,0)
    def test_bernstein_exact_constant(self):
        x=np.full(128,.125);s=moments(x,-1,1);lo,hi=confidence(s,s,-1,1);self.assertLessEqual(lo,F(1,8));self.assertGreaterEqual(hi,F(1,8))
    def test_log_is_certified(self):
        import math
        self.assertGreater(sum((F(LOG)**j/math.factorial(j) for j in range(41)),F(0)),4*FAMILY/ALPHA)
    def test_immutable_output(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.json';save(p,{'a':1})
            with self.assertRaises(FileExistsError):save(p,{'a':2})
    def test_sensor_integer_optimum(self):
        p=read(P47/'results/constrained/feasible-cone-witness-T2-p1-r0/checkpoint-N16.json');curve=sensor_curve(p,F(1,4096));best=curve['selected_bits']
        v={r['bits']:F(r['augmented_upper']) for r in curve['rows']};self.assertEqual(v[best],min(v.values()))
        differences=[v[b+1]-v[b] for b in range(4,16)];self.assertTrue(all(a<=b for a,b in zip(differences,differences[1:])))
    def test_acquired_feasibility_whole_cell(self):
        p=Policy(P47/'results/constrained/feasible-cone-witness-T2-p1-r0/checkpoint-N16.json')
        x=I.point(np.array(list(itertools.product(np.arange(9)/8,repeat=2))))
        for bits in (6,10):
            a=p.action(0,x,bits);bins=np.minimum(2**bits-1,np.floor(x.lo*2**bits));lower=1/8+np.sum(bins,axis=1)/(16*2**bits)
            self.assertTrue(np.all(a.lo>=0) and np.all(a.hi<=lower))

if __name__=='__main__':unittest.main(verbosity=2)
