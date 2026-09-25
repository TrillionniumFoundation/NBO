"""Replot complete archived traces and all scaling points; no numerical solving."""
from pathlib import Path
from fractions import Fraction
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'revisions/2026-09-25-r44/results'
OUT=Path(__file__).resolve().parents[1]/'paper/generated'
def main():
    for axis,name,xlabel in [('seconds','queue1_progress.pdf','Search time (seconds)'),('nodes','queue1_nodes.pdf','Nodes evaluated')]:
        fig,ax=plt.subplots(figsize=(7.2,4.1))
        for method,label in [('bellman','Bellman supports + simplex products'),('aggregate','Aggregate products')]:
            trace=json.loads((SOURCE/'queue1'/f'{method}.json').read_text())['trace']
            ax.step([r[axis] for r in trace],[r['gap'] for r in trace],where='post',label=label)
        ax.axhline(1e-3,linestyle='--',label='Registered target');ax.set_yscale('log')
        ax.set_xlabel(xlabel);ax.set_ylabel('Certified absolute gap');ax.legend(fontsize=9)
        fig.tight_layout();fig.savefig(OUT/name);plt.close(fig)
    rows=json.loads((SOURCE/'scaling_diagnostics.json').read_text())
    for family in ['maintenance','inventory','queue']:
        fig,ax=plt.subplots(figsize=(7.2,4.1))
        for mode in ['scaled','unscaled']:
            rr=sorted((r for r in rows if r['family']==family and r['mode']==mode),key=lambda r:float(Fraction(r['epsilon'])))
            ax.loglog([float(Fraction(r['epsilon'])) for r in rr],[r['verification']['gap'] for r in rr],marker='o',label=mode.capitalize())
        ax.set_xlabel('Operating allowance');ax.set_ylabel('Independently certified root width');ax.set_title(f'{family.capitalize()}: all seven frozen allowances');ax.legend()
        fig.tight_layout();fig.savefig(OUT/f'scaling_{family}.pdf');plt.close(fig)
if __name__=='__main__':main()
