"""Independent high-precision evaluation of the R15 paired-transfer formulas.

This is a deterministic audit, not an economic experiment or a replacement
interval certificate. It reads no policy weight, payoff sample, or work result.
It uses mpmath at 90 decimal digits and exact exponential integrals instead
of the production implementation's positive series / quadrature enclosures.
Saved spectral majorants are inputs already certified by interval LDL; their
certificates are separately replayed by the frozen production checks.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import mpmath as mp
import numpy as np

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
parser.add_argument('--out',type=Path)
args=parser.parse_args()
ROOT=args.root.resolve()
R15=ROOT/'revisions/2026-10-04-r15'
R16=ROOT/'revisions/2026-10-04-r16'
sys.dont_write_bytecode=True
sys.path.insert(0,str(R15/'code'))
import actor_verifier as av

mp.mp.dps=90
def m(x): return mp.mpf(float(x)) if isinstance(x,(float,np.floating)) else mp.mpf(x)
def norm(x): return mp.sqrt(sum(t*t for t in x))
def weighted_majorant(proof):
    return m(proof['midpoint_proof']['norm_upper'])+m(proof['matrix_radius_frobenius_upper'])
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def check_account(a):
    d=a['dimension']; n=a['steps']; h=mp.mpf(1)/n
    p=a['economic_primitives']; cp=a['coefficient_proofs']
    B=[[m(t) for t in row] for row in av.old.coupling(d)]
    k,si,sc,rho,chi,eps=map(m,[p['coupling'],p['idiosyncratic_sigma'],p['common_sigma'],p['discount'],p['CHI'],a['epsilon']])
    b=m(cp['coupling']['norm_upper']); beta=k*b
    L2=4/(3*mp.sqrt(3)); r=2*eps; eT=mp.exp(-rho)
    rows=[sum(x) for x in B]
    norms=[norm(x) for x in B]
    q=[si*si*norms[i]**2+sc*sc*rows[i]**2 for i in range(d)]
    qrms=norm(q)/mp.sqrt(d)
    c=m(p['productivity'])-(si*si+sc*sc)/2
    mend=2/(1+mp.sqrt(1+4*m(p['adjustment'])))
    C0=mend-c
    M=C0+k+eps
    positive_gram=sum(max(sum(B[i][j]*B[l][j] for j in range(d)),mp.mpf(0)) for i in range(d) for l in range(d))
    bp=min(beta,k*mp.sqrt(positive_gram/d))
    Hm=k*L2*b*b; Hx=k*L2*b*max(norms)*mp.sqrt(d)
    qnorm=weighted_majorant(cp['weighted_noise'])
    sqnorm=weighted_majorant(cp['weighted_noise_root'])
    Rnorm=weighted_majorant(cp['weighted_drift'])
    Hs=k*L2*sqnorm
    Lv=k*L2*Rnorm+beta*beta+k*qnorm
    Lm=Hm*M+bp*beta+k*min(b*qrms,qnorm)
    K=k*(C0*norm(rows)/mp.sqrt(d)+b*(k+eps))+k*L2*qrms/2
    G=k*mp.sqrt(sum(q)/d)
    D=[]; I1=[]; I2=[]; eta=[]
    for j in range(n+1):
        t=h*j; eb=mp.exp(beta*t)
        D.append(r*(eb-1)/beta)
        I1.append(r*(eb-1-beta*t)/(beta*beta))
        I2.append(r*r/(beta*beta)*((mp.exp(2*beta*t)-1)/(2*beta)-2*(eb-1)/beta+t))
        eta.append(h*eb*(K*t/2+G*mp.sqrt(t/3)))
    xi=[mp.mpf(0)]; sumxi=mp.mpf(0); sumcross=mp.mpf(0)
    for j in range(1,n+1):
        t=h*j
        sumcross+=D[j-1]*eta[j-1]
        forcing=h*(Lv*I1[j]+beta*r*t)/2+h*Hs*mp.sqrt(max(I2[j],0)/3)+h*Hx*sumcross
        value=forcing+h*beta*sumxi
        xi.append(value); sumxi+=value
    prod_grid=mp.mpf(0); prod_inside=mp.mpf(0); sumB=mp.mpf(0)
    for j in range(n):
        t=h*j; e=mp.exp(-rho*t)
        A=e*(1-mp.exp(-rho*h))/rho
        Bw=A/rho+(1-1/rho)*eT*h
        Jw=e*(1-(1+rho*h)*mp.exp(-rho*h))/(rho**3)+(1-1/rho)*eT*h*h/2
        assert Bw>0 and Jw>0
        prod_grid+=Bw*(bp*xi[j]+Hm*D[j]*eta[j])
        prod_inside+=Jw*(Lm*(I1[j+1]-I1[j])/h+bp*r)
        sumB+=Bw
    s0=sum(m(v) for v in a['initial_spread_component_bounds'])/len(a['initial_spread_component_bounds'])
    S=s0+k+eps+si*mp.sqrt(1-mp.mpf(1)/d)
    terminal=chi*eT*((2*S+2*D[-1])*xi[-1]+2*D[-1]*eta[-1])
    ideal=prod_grid+prod_inside+terminal
    state=m(a['inherited_state_arithmetic_and_clipping_upper'])
    state_extra=2*bp*state*sumB+2*chi*eT*state*(2*S+state)
    total=ideal+state_extra+2*m(a['inherited_single_statistic_arithmetic_upper'])+m(a['direct_subtraction_cushion'])
    expected={
      'beta':beta,'beta_production':bp,'tanh_second_derivative_bound':L2,
      'vector_generator_lipschitz':Lv,'scalar_generator_lipschitz':Lm,
      'paired_diffusion_derivative_lipschitz':Hs,'scalar_production_hessian':Hm,
      'four_point_vector_cross_coefficient':Hx,'base_generator_bound':K,
      'base_diffusion_derivative_bound':G,'terminal_base_error':eta[-1],
      'terminal_pair_error':xi[-1],'terminal_state_distance':D[-1],
      'production_grid':prod_grid,'production_within_cell':prod_inside,
      'terminal_dispersion':terminal,'ideal_paired_transfer':ideal,
      'inherited_path_and_clipping_transfer':state_extra,
      'proposed_total_upper':total,
      'integrated_production_weight_upper':sumB,
      'averaged_conditional_dispersion_moment_upper':S}
    checks=[]
    for key,value in expected.items():
        upper=m(a[key]); passed=value<=upper
        if not passed: raise AssertionError((d,key,str(value),str(upper)))
        checks.append(dict(field=key,independent_real_evaluation=mp.nstr(value,70),
                           stored_outward_upper=a[key],stored_encloses_reference=True,
                           outward_excess=mp.nstr(upper-value,30)))
    return dict(dimension=d,steps=n,checks=checks,
                exact_exponential_weight_ideal_transfer=mp.nstr(ideal,70),
                stored_ideal_transfer=a['ideal_paired_transfer'],
                exact_exponential_weight_total=mp.nstr(total,70),
                stored_total=a['proposed_total_upper'])

if __name__=='__main__':
    path=R15/'results/paired_transfer_constants/PAIRED_TRANSFER_CONSTANTS.json'
    constants=json.loads(path.read_text())
    rows=[check_account(a) for a in constants['model_accounts']]
    files=['manuscript/paired_transfer.tex','code/report_paired_transfer.py',
           'code/paired_transfer_checks.py','PROTOCOL.json',
           'results/paired_transfer_constants/PAIRED_TRANSFER_CONSTANTS.json']
    result=dict(status='passed',kind='independent_90_digit_formula_audit',
      mathematical_scope='Two arbitrary adapted total-held tube controllers with common innovations; exact same R15 economy, grid, and mixture law.',
      data_scope='No checkpoint, policy, payoff, training result or work record read.',
      precision_decimal_digits=mp.mp.dps,
      numerical_limit='High-precision evaluation supplements the separately replayed outward interval certificates; it is not itself an interval proof.',
      independent_differences=['Exact exponential D,I1,I2 formulas instead of truncated positive series',
        'Exact integrated B,J weights instead of interval quadrature',
        'Fresh high-precision scalar and vector coefficient expressions',
        'A separate implementation of the cumulative positive error recursion'],
      source_files=[dict(path=(R15/f).relative_to(ROOT).as_posix(),sha256=sha(R15/f)) for f in files],
      accounts=rows)
    out=args.out or R16/'results/receipts/PAIRED_TRANSFER_INDEPENDENT_FORMULA_AUDIT.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        raise FileExistsError('refusing to replace an existing audit: '+str(out))
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],dimensions=len(rows),
      total_field_enclosures=sum(len(r['checks']) for r in rows),
      accounts=[{k:r[k] for k in ['dimension','stored_total','exact_exponential_weight_total']} for r in rows],
      output=str(out)),indent=2))
