"""Budget-financed compensation for the NEW neural policy family on K."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(Path(__file__).resolve().parent))
import policy_sensitive as P
I,Q,M=P.I,P.Q,P.M

def main():
    out=ROOT/'revisions/2026-09-23-r19/results/policy_sensitive';rows=json.loads((out/'uniform_state_regret.json').read_text());ans=[]
    delta=Q('.0092');qr=(1-M.exp(-Q('.02')))/Q('.02');dc=delta/qr;disc=(1-M.exp(-Q('.04')))/Q('.04')
    mu=M.exp(-Q('1.2')*M.log(Q('.8')));pe=2*M.exp(-Q('.58').square()/(2*Q('.05').square()))
    gain=dc*mu*disc*(1-pe)
    for r in rows:
        p=out/f"seed{r['seed']}/actor_step0800.json";a=json.loads(p.read_text())
        shifted=I(a['c'])+I(float((-Q('.01')/qr).lo),float((Q('.01')/qr).hi))+dc
        if shifted.lo.min()<Q('.7').hi or shifted.hi.max()>Q('.8').lo:raise ArithmeticError('Compensating consumption violates action bounds')
        if gain.lo<=r['uniform_K_regret_upper']:raise ArithmeticError('Sufficient compensation not verified')
        ans.append({'seed':r['seed'],'initial_wealth_increment_interval':delta.pair(),'consumption_increment_interval':dc.pair(),
          'compensated_consumption_range':[float(shifted.lo.min()),float(shifted.hi.max())],
          'uniform_certified_welfare_gain_lower':float(gain.lo),'uniform_K_neural_regret_upper':r['uniform_K_regret_upper'],
          'compensation_sufficient':True,'reference_wealth_percentage':.736,
          'scope':'Budget-financed sufficient compensation for the R19 neural-generated state-indexed time policy on K, k=2. Not exact compensating variation and not a normalization of the old 7-unit full-domain certificate.',
          'proof':'Initial wealth plus delta; add delta/Q_r to each consumption slab; terminal wealth unchanged, intermediate wealth weakly higher, same preference-exit time, positive settlement difference, marginal utility lower bound.'})
    P.write(out/'neural_wealth_compensation.json',ans);print(json.dumps(ans,indent=2))
if __name__=='__main__':main()
