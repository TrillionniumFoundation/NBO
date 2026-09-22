"""Rigorous absolute lower bound for the unchanged coupled nonconvex benchmark.
A pointwise running-cost relaxation and removal of control bounds yield a
Cole--Hopf problem. Orthogonal Gaussian coordinates integrate analytically;
one remaining positive scalar integral is enclosed with interval arithmetic.
"""
from __future__ import annotations
import pathlib,json,time,math,argparse
from mpmath import iv
import numpy as np
iv.dps=50
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=ROOT/'revisions/2026-09-22-r9/results'
def I(x):return iv.mpf(x)
def bounds(x):return [float(np.nextafter(float(x.a),-np.inf)),float(np.nextafter(float(x.b),np.inf))]
def run(d,cells=(1024,4096,16384)):
 r=1+I('.1')*iv.sin(I(1))**2;sig2=I('.32');lam=sig2*r/(2*d)
 mean=2*iv.sqrt(I(d))/(r+4);var=sig2*r/(r+4);eta=I('.2')/lam
 base=I('.25')*r/(r+4)+sig2*r/4*iv.ln(1+4/r)-I('.3')
 R=int(math.ceil(math.sqrt(2*(bounds(eta)[1]+50))));tail=2*iv.exp(eta-I(R)**2/2);rows=[]
 for n in cells:
  start=time.perf_counter();integral=I(0)
  for j in range(n):
   s=iv.mpf([(-I(R)+2*I(R)*j/n).a,(-I(R)+2*I(R)*(j+1)/n).b])
   y=iv.exp(-s*s/2-eta*iv.cos(mean+iv.sqrt(var)*s))/iv.sqrt(2*iv.pi)
   integral+=2*I(R)/n*y
  intr=iv.mpf([integral.a,(integral+tail).b]);value=base-lam*iv.ln(intr)
  row={'dimension':d,'cells':n,'normal_cutoff':R,'relaxed_value_interval':bounds(value),'lower_bound':bounds(value)[0],
    'quadrature_width':bounds(value)[1]-bounds(value)[0],'seconds':time.perf_counter()-start};rows.append(row);print(row,flush=True)
 payload={'dimension':d,'r_interval':bounds(r),'lambda_interval':bounds(lam),'records':rows,
  'inequality':'original optimum >= relaxed optimum >= reported lower_bound',
  'scope':'same original nonconvex payoff and terminal cost; a pointwise relaxation, not a manufactured replacement experiment',
  'arithmetic':'mpmath.iv 50 decimal digits; Gaussian tail enclosed analytically'}
 OUT.mkdir(parents=True,exist_ok=True);(OUT/f'absolute_lower_d{d}.json').write_text(json.dumps(payload,indent=2)+'\n');return payload
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--dimension',type=int,default=8);a=ap.parse_args();run(a.dimension)
