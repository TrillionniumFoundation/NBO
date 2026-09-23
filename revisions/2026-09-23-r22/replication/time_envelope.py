"""All-start-time discounted residual envelope from existing slab bounds."""
from pathlib import Path
import sys,json
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r22'
sys.path.insert(0,str(ROOT/'revisions/2026-09-23-r16/replication'))
import mpfr_interval as M
I,Q=M.I,M.I.rational

def main():
    rows=[]
    for phase in ['initial','candidate']:
        p=REV/f'results/full_state/{phase}_certificate.json';d=json.loads(p.read_text());n=len(d['slabs']);h=Q(Fraction(1,n))
        e=M.exp(-Q('.04')*h);mass=(1-e)/Q('.04');tail=I(0);values=[0.]
        for slab in reversed(d['slabs']):
            a=I(slab['positive_upper'])+I(slab['negative_policy']);tail=mass*a+e*tail;values.append(float(tail.hi))
        values=values[::-1]
        rows.append({'phase':phase,'slab_boundary_envelope_upper':values,'all_start_times_regret_upper':max(values),
             'earlier_undiscounted_all_times_bound':d['all_initial_times_regret_upper'],
             'proof':'within each time slab the discounted suffix is monotone or constant; its maximum is at an endpoint',
             'arithmetic':'MPFR directed interval recursion, all time slabs included'})
    (REV/'results/full_state/time_envelope.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
