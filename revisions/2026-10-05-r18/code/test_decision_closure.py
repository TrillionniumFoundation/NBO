"""Exact deterministic tests independent of favorable economic signs."""
import unittest,math,random
from fractions import Fraction as F
from decision_closure import closure,summaries,upper_float,lower_float,rational
class ClosureTests(unittest.TestCase):
 def test_orientation(self):
  d=closure(['a','b'],[('b','a',2,3)])
  self.assertEqual(d['a','b'],3);self.assertEqual(d['b','a'],-2)
 def test_indirect_sharpening(self):
  d=closure('abc',[('b','a',1,2),('c','b',2,3),('c','a',0,10)])
  self.assertEqual(d['a','c'],5);self.assertEqual(d['c','a'],-3)
 def test_diagonal(self):
  d=closure('abc',[('b','a',1,2),('c','b',2,3)])
  self.assertTrue(all(d[i,i]==0 for i in 'abc'))
 def test_contradiction(self):
  with self.assertRaises(ValueError):closure('ab',[('b','a',1,2),('b','a',3,4)])
 def test_negative_cycle(self):
  with self.assertRaises(ValueError):closure('abc',[('a','b',1,2),('b','c',1,2),('c','a',1,2)])
 def test_disconnected(self):
  with self.assertRaises(ValueError):closure('abc',[('a','b',0,1)])
 def test_duplicate_nodes(self):
  with self.assertRaises(ValueError):closure(['a','a'],[])
 def test_invalid_endpoints(self):
  for lo,hi in ((2,1),(math.nan,2),(0,math.inf),(False,2)):
   with self.subTest(lo=lo,hi=hi):
    with self.assertRaises(ValueError):closure('ab',[('a','b',lo,hi)])
 def test_binary64_exact(self):self.assertEqual(rational(.1),F.from_float(.1))
 def test_directed_rounding(self):
  for x in [F(1,3),F(-1,3),F(1,10**20),F(0),F(12)]:
   self.assertLessEqual(F(lower_float(x)),x);self.assertGreaterEqual(F(upper_float(x)),x)
 def test_zero_tolerance_exact_best(self):
  d,g,w=summaries('ab',[('b','a',2,3)],{'a':0,'b':7},0)
  self.assertEqual(w,'b');self.assertEqual(g['b'],0)
 def test_empty_certified_set(self):
  _,_,w=summaries('ab',[('b','a',-2,2)],{'a':1,'b':2},1)
  self.assertIsNone(w)
 def test_deterministic_ties(self):
  _,_,w=summaries(['b','a'],[('b','a',0,0)],{'a':1,'b':1},0)
  self.assertEqual(w,'a')
 def test_common_bill_invariant(self):
  edges=[('b','a',-.1,.1)]
  self.assertEqual(summaries('ab',edges,{'a':1,'b':2},.2)[2],summaries('ab',edges,{'a':51,'b':52},.2)[2])
 def test_unverified_cheaper_can_be_truly_accurate(self):
  _,gap,w=summaries('ab',[('b','a',0,2)],{'a':1,'b':2},1)
  self.assertEqual(w,'b');self.assertGreater(gap['a'],1)
 def test_invalid_costs(self):
  for costs in ({'a':-1,'b':2},{'a':1}):
   with self.assertRaises(ValueError):summaries('ab',[('b','a',0,2)],costs,1)
 def test_sharp_extremal_potentials(self):
  rng=random.Random(1805)
  for _ in range(50):
   nodes=tuple(range(5));v=[F(rng.randint(-10,10),7) for _ in nodes]
   edges=[(j,i,v[j]-v[i]-F(rng.randint(0,5),11),v[j]-v[i]+F(rng.randint(0,5),13)) for i in nodes for j in nodes if i<j]
   d=closure(nodes,edges)
   for i in nodes:
    for p in ([d[i,k] for k in nodes],[-d[k,i] for k in nodes]):
     self.assertEqual(p[i],0)
     for a,b,lo,hi in edges:self.assertTrue(lo<=p[a]-p[b]<=hi)
    self.assertEqual(max(d[i,k] for k in nodes),max([d[i,k]-d[i,i] for k in nodes]))
    self.assertEqual(max(-d[k,i] for k in nodes),max([-d[k,i]+d[i,i] for k in nodes]))
 def test_significant_digit_presentation(self):
  from tables import directed
  self.assertEqual(directed(-8354.2,False),'-8360')
  self.assertEqual(directed(-4767.5,True),'-4760')
 def test_no_need_for_direct_all_pairs(self):
  d=closure(range(4),[(i,0,i,i+1) for i in range(1,4)])
  self.assertEqual(len(d),16)
if __name__=='__main__':unittest.main()
