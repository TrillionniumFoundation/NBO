"""MPFR certificate of a fixed full-rank 16-node tanh interpolation design.

Nonsingularity proves equality of finite-node raw-output classes in real
arithmetic; it does not assert that an optimizer finds the interpolating weights.
"""
from pathlib import Path
from fractions import Fraction
import sys,json,time
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r23'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r16/replication'))
import mpfr_interval as M
I,Q=M.I,M.I.rational

def main():
 start=time.perf_counter();n=16
 nodes=[Q(Fraction(2*j+1,n)-1) for j in range(n)]
 thresholds=[Q(Fraction(2*j,n)-1) for j in range(n)]
 matrix=[[M.tanh(Q(Fraction(1,4))*M.tanh(80*(t-a))) for a in thresholds] for t in nodes]
 original=[[[float(x.lo),float(x.hi)] for x in row] for row in matrix]
 pivots=[]
 for k in range(n):
  pivot=matrix[k][k];assert float(pivot.lo)>0 or float(pivot.hi)<0
  pivots.append([float(pivot.lo),float(pivot.hi)])
  for i in range(k+1,n):
   multiplier=matrix[i][k]/pivot
   for j in range(k+1,n):matrix[i][j]=matrix[i][j]-multiplier*matrix[k][j]
   matrix[i][k]=I(0)
 determinant=I(1)
 for lo,hi in pivots:determinant=determinant*I(lo,hi)
 assert float(determinant.lo)>0
 result={'status':'PASS','nodes':16,'matrix_rank':16,'hidden_layers':[16,16],'first_layer_scale':80,'second_layer_scale':'1/4','nodes_formula':'(2*j+1)/16-1, j=0,...,15','thresholds_formula':'2*j/16-1, j=0,...,15','pivot_intervals':pivots,'determinant_interval':[float(determinant.lo),float(determinant.hi)],'matrix_intervals':original,'arithmetic':'MPFR 128-bit operations with outward binary64 endpoints','seconds':time.perf_counter()-start,'scope':'fixed rational-parameter feature matrix; exact real nonsingularity and existence of a final affine layer interpolating any finite raw-output array; not finite-precision optimizer convergence or general state-function approximation'}
 (REV/'results/interpolation_certificate.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['matrix_intervals','pivot_intervals']},indent=2))
if __name__=='__main__':main()
