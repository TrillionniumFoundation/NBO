"""No data subsampling: plot all inherited local-LP executions."""
from pathlib import Path
from fractions import Fraction as F
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];data=json.loads((ROOT/'results/diagnostics.json').read_text())['local_lp_inherited']['outcomes']
for field,name,label in [('whole_cells_verified','local_cells','Verified whole cells'),('seconds','local_seconds','Construction time (seconds)')]:
    fig,ax=plt.subplots(figsize=(7.0,4.5))
    for witness in sorted({r['witness'] for r in data}):
        for epsilon in sorted({r['epsilon'] for r in data}):
            rows=sorted([r for r in data if r['witness']==witness and r['epsilon']==epsilon],key=lambda r:r[field])
            ax.plot([r[field] for r in rows],[float(F(r['continuous_local_upper'])-F(r['continuous_local_lower'])) for r in rows],marker='o',label=f'{witness}, allowance {float(F(epsilon)):.2f}')
    ax.set_xlabel(label);ax.set_ylabel('Certified local interval width');ax.set_xscale('log');ax.set_yscale('log');ax.legend(frameon=False,fontsize=9);fig.tight_layout()
    fig.savefig(ROOT/'paper/generated'/f'{name}.pdf');plt.close(fig)
