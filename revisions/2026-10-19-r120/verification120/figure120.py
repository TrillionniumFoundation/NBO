"""Descriptive display of every P/L cell from completed, immutable R120 tables.

No solver, training, new timing, sample selection or inference is performed.
The exact input intervals and all three clocks remain authoritative.
"""
from pathlib import Path
from fractions import Fraction
import datetime as dt
import hashlib
import json
import os
import time

ROOT = Path(__file__).resolve().parents[1]
ARMS = ('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
LABELS = ('Online','Quadratic','ReLU','Hinge','Spline','Poly2','Poly3','Grid')

def main():
    start=time.time()
    out=ROOT/'figures120'
    out.mkdir(exist_ok=False)
    names=('groups120','raw_timing_clocks120','sample_contrasts120')
    paths={n:ROOT/'tables120'/f'{n}.json' for n in names}
    hashes={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in paths.items()}
    data={n:json.loads(p.read_text()) for n,p in paths.items()}
    assert tuple(len(data[n]) for n in names)==(64,192,992)
    groups={(r['index'],r['arm'],r['service']):r for r in data[names[0]]}
    clocks={(r['index'],r['arm'],r['service'],r['repeat']):r for r in data[names[1]]}
    pairs={}
    for r in data[names[2]]:
        if r['a_arm']==r['b_arm'] and {r['a_service'],r['b_service']}=={'legacy-safe','paired'}:
            lo=Fraction(r['mean_original_j_a_minus_b_lower'])
            hi=Fraction(r['mean_original_j_a_minus_b_upper'])
            if r['a_service']=='paired':lo,hi=-hi,-lo
            pairs[r['index'],r['a_arm']]=(lo,hi)
    assert len(pairs)==16
    rows=[]
    for risk in range(2):
        for arm,label in zip(ARMS,LABELS):
            g=lambda s:groups[risk,arm,s]
            ratios=[Fraction(clocks[risk,arm,'paired',k]['complete_observed32_total_seconds'])/
                    Fraction(clocks[risk,arm,'legacy-safe',k]['complete_observed32_total_seconds']) for k in range(3)]
            primary=Fraction(g('paired')['complete_observed64_total_seconds'])/Fraction(g('legacy-safe')['complete_observed64_total_seconds'])
            lo,hi=pairs[risk,arm]
            rows.append(dict(index=risk,arm=arm,label=label,clock_ratios=list(map(str,ratios)),
                             primary_ratio=str(primary),gain_lower=str(lo),gain_upper=str(hi)))
    os.environ.setdefault('MPLCONFIGDIR','/tmp/nbo-figure120')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,(a,b)=plt.subplots(1,2,figsize=(8.0,5.35),sharey=True,gridspec_kw={'width_ratios':[1.08,1]})
    for i,row in enumerate(rows):
        y=15-i
        vals=[float(Fraction(v)) for v in row['clock_ratios']]
        a.plot([min(vals),max(vals)],[y,y],color='#236b8e',lw=1.3,zorder=2)
        a.scatter(vals,[y]*3,color='#236b8e',s=12,zorder=3)
        a.scatter(float(Fraction(row['primary_ratio'])),y,marker='x',color='#b34e24',s=26,zorder=4)
        lo,hi=(float(Fraction(row[k])*10**6) for k in ('gain_lower','gain_upper'))
        b.plot([lo,hi],[y,y],color='#236b8e',lw=1.5,zorder=3)
        b.plot([lo,hi],[y,y],linestyle='none',marker='|',color='#236b8e',ms=6,zorder=4)
    a.axvline(1,color='#444444',ls='--',lw=.8)
    b.axvline(0,color='#444444',ls='--',lw=.8)
    for ax in (a,b):
        ax.axhline(7.5,color='#aeb8be',lw=.6)
        ax.grid(axis='x',color='#e2e7e9',lw=.6)
        ax.set_ylim(-.75,15.75)
        ax.set_axisbelow(True)
    a.set_yticks(range(16),[f"{'1/2' if r['index']==0 else '3/4'}  {r['label']}" for r in reversed(rows)])
    a.set_title('Complete cost ratio P / L',loc='left',fontsize=10)
    b.set_title('Original policy gain from P over L',loc='left',fontsize=10)
    a.set_xlabel('Ratio of standalone workload seconds')
    b.set_xlabel(r'$J_L-J_P$ in $10^{-6}$ original-cost units')
    b.xaxis.set_major_locator(MaxNLocator(5))
    a.scatter([],[],color='#236b8e',s=12,label='All three 32-state clocks')
    a.scatter([],[],color='#b34e24',marker='x',s=26,label='Actual 64-state primary')
    a.legend(loc='lower right',fontsize=7.5,frameon=False)
    fig.tight_layout(pad=1.1,w_pad=1.5)
    fixed=dt.datetime(2026,10,19,tzinfo=dt.timezone.utc)
    fig.savefig(out/'paired_legacy120.pdf',metadata={'Title':'Complete R120 paired versus legacy comparison','Author':'NBO authors','CreationDate':fixed,'ModDate':fixed})
    fig.savefig(out/'paired_legacy120.png',dpi=170)
    plt.close(fig)
    (out/'PLOTTED_VALUES120.json').write_text(json.dumps(rows,indent=2)+'\n')
    assert hashes=={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in paths.items()}
    receipt={'status':'rendered','started_unix':start,'ended_unix':time.time(),
             'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'inputs_sha256':hashes,'all_risk_arm_cells':16,'all_matched_clock_ratios':48,
             'original_sample_interval_pairs':16,'matplotlib_version':matplotlib.__version__,
             'scope':'Post-execution descriptive formatting of the full predeclared comparator table. Clock ranges are descriptive. Economic brackets are exact-sample enclosures, not confidence intervals or point estimates. No new solver, timing, training, sample or inference.',
             'outputs':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir())}}
    (out/'FIGURE_RECEIPT120.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':'rendered','cells':16,'outputs':list(receipt['outputs'])}))

if __name__=='__main__':main()
