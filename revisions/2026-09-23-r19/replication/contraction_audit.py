"""A posteriori TRUE-regret contraction tests, separate from training claims."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(Path(__file__).resolve().parent))
import policy_sensitive as P
I,Q=P.I,P.Q

def main():
    out=ROOT/'revisions/2026-09-23-r19/results/policy_sensitive';rr=json.loads((out/'results.json').read_text());rows=[]
    states={r['seed']:r for r in json.loads((out/'uniform_state_regret.json').read_text())}
    gains={r['seed']:r for r in json.loads((out/'uniform_policy_gain.json').read_text())}
    for seed in P.SEEDS:
        seq=sorted([r for r in rr if r['seed']==seed],key=lambda r:r['step']);tests=[]
        for a,b in zip(seq,seq[1:]):
            margin=I(b['value_interval'][0])-I(a['value_interval'][1])-Q('.02')*I(a['regret_upper'])
            if margin.lo<=0:raise ArithmeticError('Two-percent step contraction was not certified')
            tests.append({'from':a['step'],'to':b['step'],'kappa_rational':'1/50','test_margin_lower':float(margin.lo)})
        a,b=seq[0],seq[-1];delta=I(b['value_interval'][0])-I(a['value_interval'][1]);direct=delta-Q('.75')*I(a['regret_upper'])
        if direct.lo<=0:raise ArithmeticError('75-percent reference-state contraction was not certified')
        B=I(states[seed]['uniform_K_regret_upper']);D=I(gains[seed]['uniform_payoff_gain_interval'][0]);ratio=B/(B+D)
        if ratio.hi>=Q('.42').lo:raise ArithmeticError('58-percent K-uniform contraction was not certified')
        rows.append({'seed':seed,'step_tests':tests,'reference_initial_to_final_true_regret_reduction_at_least':.75,
          'reference_test_margin_lower':float(direct.lo),'uniform_K_final_to_initial_true_regret_ratio_upper':float(ratio.hi),
          'uniform_K_true_regret_reduction_at_least':.58,
          'scope':'a posteriori verified inequalities for these newly executed policies; not an a priori Adam convergence rate'})
    P.write(out/'true_regret_contraction.json',rows);print('PASS: 15 step contractions, 5 central 75% and 5 K-uniform 58% reductions')
if __name__=='__main__':main()
