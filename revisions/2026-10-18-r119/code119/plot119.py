"""Plot all contemporaneous phase-C F/G clocks; never execute or retime a policy."""
from pathlib import Path
import hashlib
import json
import statistics
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/nbo-matplotlib119")
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[1]
RAW = R / 'results119/primary119c'
OUT = R / 'figures119'
OUT.mkdir(exist_ok=True)
ARMS = ['online', 'quadratic', 'relu', 'hinge', 'spline', 'poly2', 'poly3', 'grid']
LABELS = ['Semi-analytic', 'Quadratic (rank six)', 'ReLU', 'Equivalent hinge',
          'Coordinate spline', 'Full quadratic', 'Cubic polynomial', 'Tensor grid']
data = {}
sources = []
for repeat in range(7):
    p = RAW / f'timing/PROCESS-{repeat}.json'
    sources.append({'path': str(p.relative_to(R)),
                    'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    for row in json.loads(p.read_bytes())['entries']:
        if row['service'] in ('geometric', 'fused-tail'):
            data[(row['index'], row['arm'], row['service'], repeat)] = row['seconds']

plt.rcParams.update({'font.family': 'DejaVu Serif', 'font.size': 10,
                     'pdf.fonttype': 42, 'axes.spines.top': False,
                     'axes.spines.right': False})
fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.8), sharey=True, layout='constrained')
records = []
for idx, ax in enumerate(axes):
    for y, arm in enumerate(ARMS):
        f = [data[idx, arm, 'fused-tail', rep] for rep in range(7)]
        g = [data[idx, arm, 'geometric', rep] for rep in range(7)]
        pairs = [x / z for x, z in zip(f, g)]
        ratio = statistics.median(f) / statistics.median(g)
        color = '#1b6a86' if ratio < 1 else '#a74934'
        for rep, p in enumerate(pairs):
            ax.scatter(p, y + (rep - 3) * .038, s=14, color='#a9b0b5', zorder=2)
        ax.scatter(ratio, y, marker='D', s=38, color=color, zorder=3)
        ax.text(1.57, y, f'{ratio:.4f}', ha='right', va='center', color=color, fontsize=9)
        records.append({'risk_index': idx, 'arm': arm,
                        'median_service_time_ratio': ratio,
                        'seven_paired_clock_ratios': pairs})
    ax.axvline(1, color='#333333', linestyle='--', linewidth=.9, zorder=1)
    ax.set_xlim(.58, 1.60)
    ax.set_xticks([.6, .8, 1.0, 1.2, 1.4])
    ax.grid(axis='x', alpha=.15)
    ax.set_title(r'$\alpha=1/2$' if idx == 0 else r'$\alpha=3/4$')
    ax.set_xlabel('Packed service time / geometric service time')
    ax.set_yticks(range(8), LABELS)
axes[0].invert_yaxis()
fig.suptitle('All 16 phase-C comparisons under the original investment objective', fontsize=12)
fig.savefig(OUT / 'phase_c_all_clocks119.pdf', metadata={'CreationDate': None, 'ModDate': None})
fig.savefig(OUT / 'phase_c_all_clocks119.png', dpi=180)
receipt = {'scope': 'Read-only figure from all seven contemporaneous original clocks.',
           'diamonds': 'ratio of the two seven-process median service times',
           'gray_points': 'individual paired clock ratios; not confidence intervals',
           'sources': sources, 'all_comparisons': records,
           'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT / 'FIGURE_RECEIPT119.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'cells': len(records), 'median_wins': sum(x['median_service_time_ratio'] < 1 for x in records),
                  'figure': str((OUT / 'phase_c_all_clocks119.pdf').relative_to(R))}))
