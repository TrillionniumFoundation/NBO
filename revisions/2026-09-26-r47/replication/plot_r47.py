"""Replot archived data; each plot is descriptive and preserves all chosen cases."""
from pathlib import Path
import json,gzip
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parents[1]/'paper/generated'
old=root/'revisions/2026-09-25-r44';new=root/'revisions/2026-09-25-r46'
def main():
 fig,ax=plt.subplots(figsize=(7.2,4.1))
 for method,label in [('bellman','Original Bellman'),('aggregate','Original aggregate')]:
  trace=json.loads((old/'results/queue1'/f'{method}.json').read_text())['trace']
  ax.step([r['nodes'] for r in trace],[r['gap'] for r in trace],where='post',label=label)
 proof=json.loads(gzip.decompress((new/'proofs/queue1/price_search.json.gz').read_bytes()))
 ax.step([r['nodes'] for r in proof['trace']],[r['gap'] for r in proof['trace']],where='post',label='Restart-price search')
 ax.axhline(1e-3,linestyle='--',label='Registered absolute target');ax.set_yscale('log')
 ax.set_xlabel('Nodes evaluated');ax.set_ylabel('Certified absolute width');ax.legend(fontsize=9)
 fig.tight_layout();fig.savefig(out/'price_queue1_nodes.pdf');plt.close(fig)
 fig,ax=plt.subplots(figsize=(7.2,4.1))
 for family in ['maintenance','inventory','queue','tie']:
  rr=[json.loads((new/'results'/f'{family}{i}_price_search.json').read_text()) for i in range(4)]
  ax.scatter([r['summary']['nodes'] for r in rr],[r['proof_bytes']/1024 for r in rr],label=family.capitalize())
 ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Nodes in the complete price-search certificate');ax.set_ylabel('Compressed proof size (KiB)');ax.legend(fontsize=9)
 fig.tight_layout();fig.savefig(out/'price_proof_size.pdf');plt.close(fig)
if __name__=='__main__':main()
