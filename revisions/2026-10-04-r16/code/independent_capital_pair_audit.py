"""Independent 90-digit general-horizon check of R16 capital transfer.

Exact exponential integrals and a separately expressed scalar recursion check
the outward coefficients before any new policy or confirmation is executed.
No statistical observation, checkpoint, learned coefficient or fit is read.
High-precision evaluation supplements, and does not replace, outward arithmetic.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import mpmath as mp
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
R16=ROOT/'revisions/2026-10-04-r16'
sys.dont_write_bytecode=True
sys.path.insert(0,str(R16/'code'))
from capital_adapter import bind_economy
mp.mp.dps=90
av=None
def m(x): return mp.mpf(float(x)) if isinstance(x,(float,np.floating)) else mp.mpf(x)

def norm(x): return mp.sqrt(sum(t*t for t in x))

def weighted_majorant(proof):
    return m(proof['midpoint_proof']['norm_upper'])+m(proof['matrix_radius_frobenius_upper'])

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def check_account(a):
    d=a['dimension']; n=a['steps']
    p=a['economic_primitives']; cp=a['coefficient_proofs']; T=m(p['T']); h=T/n
    B=[[m(t) for t in row] for row in av.old.coupling(d)]
    k,si,sc,rho,chi,eps=map(m,[p['coupling'],p['idiosyncratic_sigma'],p['common_sigma'],p['discount'],p['CHI'],a['epsilon']])
    b=m(cp['coupling']['norm_upper']); beta=k*b
    L2=4/(3*mp.sqrt(3)); r=2*eps; eT=mp.exp(-rho*T)
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
    S=s0+(k+eps)*T+si*mp.sqrt((1-mp.mpf(1)/d)*T)
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

def main():
    global av
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--protocol',type=Path,required=True)
    p.add_argument('--account',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError('refusing to overwrite an independent audit')
    protocol=json.loads(args.protocol.read_text())
    account=json.loads(args.account.read_text())
    c=next(x for x in protocol['calibrations'] if x['id']==account['calibration_id'])
    if account['economic_primitives'] != c['primitives'] or account['primitives_sha256'] != c['primitives_sha256']:
        raise ValueError('account and declared economic primitives differ')
    if account['steps'] != protocol['confirmation']['steps'] or account['epsilon'] != c['epsilon']:
        raise ValueError('account and declared decision grid or action tube differ')
    if account['protocol_sha256'] != hashlib.sha256(args.protocol.read_bytes()).hexdigest():
        raise ValueError('coefficient account does not belong to the frozen protocol')
    av=bind_economy(c['primitives'],c['epsilon'],c['initial_state_population'],c['id']).verifier
    row=check_account(account)
    result=dict(status='passed',kind='independent_general_horizon_formula_audit',
        calibration_id=c['id'],precision_decimal_digits=mp.mp.dps,account=row,
        account_sha256=hashlib.sha256(args.account.read_bytes()).hexdigest(),
        protocol_sha256=hashlib.sha256(args.protocol.read_bytes()).hexdigest(),
        data_scope='No fitted weights, training outcomes, payoffs or confirmation draws read.',
        scientific_scope='Arbitrary total-held adapted controllers in the same declared calibration/tube; fixed physical horizon T and independent source-frozen arithmetic.')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(status='passed',calibration=c['id'],dimension=account['dimension'],field_enclosures=len(row['checks']),upper=row['stored_total'])))

if __name__=='__main__':main()
