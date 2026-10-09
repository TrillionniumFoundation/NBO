"""Publication tables generated only from replayed, complete fixed records."""
from pathlib import Path
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from fractions import Fraction as F
import json
R=Path(__file__).resolve().parents[1]
LABEL={'relu':'N','quadratic':'Q','extra-trees':'E','compiled-witness':'W','tensor-fvi':'F'}
def put(name,text):
    if any(ord(c)<32 and c not in '\n\r\t' for c in text):raise ValueError('Control character in '+name)
    f=R/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text)
def endpoint(x,lower=False,d=4):return format(Decimal.from_float(float(x)).quantize(Decimal(10)**-d,rounding=ROUND_FLOOR if lower else ROUND_CEILING),'f')
def band(v,d=4):return '['+endpoint(v[0],True,d)+', '+endpoint(v[1],False,d)+']'
def clock(x):return f'{x:.3f}'
def table(name,caption,head,rows,note,long=False):
    cols=''.join('r' for _ in head);label='tab:'+name
    if long:
        text='\\begingroup\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+'}\\\\\n\\toprule\n'+' & '.join(head)+r' \\'+'\n\\midrule\\endfirsthead\n\\toprule\n'+' & '.join(head)+r' \\'+'\n\\midrule\\endhead\n'
        text+='\n'.join(' & '.join(map(str,r))+r' \\' for r in rows)+'\n\\bottomrule\n\\end{longtable}\n\\noindent '+note+'\n\\endgroup\n'
    else:
        text='\\begin{table}[htbp]\n\\centering\n\\caption{'+caption+'}\\label{'+label+'}\n{\\small\\setlength{\\tabcolsep}{4pt}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+' & '.join(head)+r' \\'+'\n\\midrule\n'
        text+='\n'.join(' & '.join(map(str,r))+r' \\' for r in rows)+'\n\\bottomrule\n\\end{tabular}}\n\\par\\smallskip\n{\\footnotesize '+note+'}\n\\end{table}\n'
    put('tables/'+name+'.tex',text)
def main():
    a=json.loads((R/'audit/RESULT_AUDIT56.json').read_text());groups=a['grouped'];rows=[]
    for z in groups:
        if z['cohort']=='tube' and z['kind']=='relu':
            f=z['final'];rows.append([z['d'],z['T'],z['target'],f['paths'],band(f['cost']),band(f['gain'])])
    table('economic56','Actual costs at the prospective neural-policy return',
          ['$d$','$T$','$q$','Paths','Expected cost','Installed minus returned'],rows,
          'N is the trained ReLU generator. Every row is a separately executed target service with the signed reference certificate. Endpoints are rounded outward. The interval covers the complete implemented policy under the original continuous law. Timing repetitions have identical policy and inference identities and are not additional economic observations. Other generators and every earlier-stage outcome are retained in the supplement.')
    rows=[]
    for z in groups:
        if z['cohort']=='primary' and z['kind']=='relu':
            f=z['final'];rows.append([z['d'],z['T'],z['target'],f['stage']+1,f['paths'],'Hit' if z['status']=='target_attained' else 'Exhausted',sum(t['changed'] for t in f['dates'])])
    table('stopping56','Outcomes before the signed reference refinement',
          ['$d$','$T$','$q$','Stages','Paths','Status','Last-pass changes'],rows,
          'This primary-cache cohort is not dropped after its limitations become visible. These are the neural rows; the candidate generators return policy-identical final arrays within each primary task and target. Exhausted means the declared finite service did not certify its target, not that improvement is impossible. All own construction, inference and failed-stage work remains charged.')
    rows=[]
    for z in groups:
        if z['cohort']=='tube' and z['target']=='9/10':rows.append([z['d'],z['T'],LABEL[z['kind']],clock(z['clock_min']),clock(z['clock_median']),clock(z['clock_max']),round(z['serialized_bytes']/1024),round(z['peak_rss_kib']/1024,1)])
    table('timing56','Complete process work to the ten-percent cost target',
          ['$d$','$T$','Method','Min (s)','Median (s)','Max (s)','Output KiB','RSS MiB'],rows,
          'N: trained ReLU; Q: quadratic FVI; E: ExtraTrees FVI; W: compiled witness; F: tensor FVI. Three isolated sequential processes use identical seeds within a method. Each clock includes its own imports, construction, verification, inference and durable output. Compare methods within a task runner, not across runners. Affinity and numerical-library threads are fixed; clock frequency is not controlled. Output excludes prior-stage archives outside the service; RSS is process peak memory. Both targets and all repetitions appear in the supplement.')
    z=next(z for z in groups if z['cohort']=='tube' and z['kind']=='relu' and z['d']==8 and z['target']=='9/10');rows=[]
    for t in z['final']['dates']:
        rows.append([t['date'],t['changed'],endpoint(t['base_candidate_width_max'],d=3),endpoint(t['intersected_candidate_width_max'],d=3),endpoint(t['candidate_enclosure_component'],d=3),endpoint(t['continuous_cover_component'],d=3),endpoint(t['gap'],d=3)])
    table('mechanism56','Where the signed reference certificate changes decisions',
          ['Date','Changed','Base width','Refined width',r'$U-C$',r'$C-L$',r'$U-L$'],rows,
          'Eight-dimensional state, six dates, trained ReLU, first stage, 32 non-tensor leaves. Widths are maxima over candidate enclosures; decomposition entries are maxima over leaves, rounded upward. The last row uses analytic terminal differences rather than differentiating an acquired actor. A tighter comparison certificate is not itself a new policy-cost observation.')
    rows=[];null=a['learned_null']
    for d in (2,4,8):
        for N in (512,4096,32768):
            fits=[v for v in null['fits'] if v['dimension']==d and v['validation_rows']==N];keys={v['key'] for v in fits};cases=[v for v in null['case_records'] if v['key'] in keys];sig=[v['robust_direction_exposure_upper'] for v in fits]
            rows.append([d,N,band([min(sig),max(sig)]),sum(v['changed'] for v in cases),sum(v['harmful_false_null'] for v in cases)])
    table('learned-null56','Validation-qualified learned directions',
          ['$d$','Validation rows','Projection-bound range','Corrected changes','Harmful plug-in'],rows,
          'Each row aggregates three independently fitted directions and three amplitudes on 64 leaves per case. The projection range reports the minimum and maximum robust upper allowance across fitted directions, not a confidence interval for a population mean. All 27 exposure boxes cover the simulator exposure in this record. No strictly harmful plug-in choice is identified here; the earlier known-perturbation catalogue is a different diagnostic and remains unchanged.')
    alg=json.loads((R/'audit/ALGEBRAIC_REGRESSION56.json').read_text());rows=[]
    for z in alg['fixtures']:
        difference=F(z['original_reduced_value_exact'])-F(z['value_exact'])
        rows.append([z['d'],z['T'],z['lattice_size'],len(z['candidate_indices']),z['original_proposal'],z['index'],f'{float(difference):.7f}'])
    table('algebraic56','Exact lattice search on saved fitted neural critics',
          ['$d$','$T$','Full lattice','Candidates','Old index','Exact index','Critic decrease'],rows,
          'One declared cell center and its saved next-date critic per task. Rational isolation and comparison agree with exhaustive rational lattice minimization. The reported decrease is in that fixed approximate Bellman objective, not actual economic policy cost. These solver regressions neither retrain a critic nor produce new policy-cost observations.')
    rows=[]
    for cohort in ('primary','tube'):
        for z in a[cohort]['services']:
            f=z['stages'][-1];rows.append(['P' if cohort=='primary' else 'S',z['d'],z['T'],LABEL[z['kind']],z['target'],z['repeat'],len(z['stages']),f['paths'],'H' if z['status']=='target_attained' else 'E',clock(z['whole_process_seconds'])])
    table('services56','Every prospective service and timing repetition',
          ['Cohort','$d$','$T$','Method','$q$','Rep.','Stages','Paths','End','Work (s)'],rows,
          'P: primary cache; S: signed reference extension. H: target attained; E: declared budget exhausted. Repetitions 0--2 have identical training and inference seeds, not independent training draws. All 132 processes and their immutable cumulative driver checkpoints are included. The full JSON retains every per-stage construction, cache, gate and inference clock.',True)
    rows=[]
    for z in groups:
        f=z['final'];rows.append(['P' if z['cohort']=='primary' else 'S',z['d'],z['T'],LABEL[z['kind']],z['target'],band(f['cost'],3),band(f['gain'],3),band(f['target_contrast'],3)])
    table('all-costs56','Every final actual-cost, gain and target interval',
          ['Cohort','$d$','$T$','Method','$q$','Cost','Gain','Target contrast'],rows,
          'Intervals are rounded outward and correspond to repetition zero; exact identities across repetitions are separately checked. A negative target-contrast upper endpoint licenses the stated prospective return. Gain intervals use paired path endpoints rather than subtraction of marginal cost intervals. Every intermediate look remains in the service archive.',True)
    rows=[]
    for cohort in ('primary','tube'):
        for z in a[cohort]['services']:
            if z['repeat']!=0:continue
            for stage in z['stages']:
                for t in stage['dates']:
                    rows.append(['P' if cohort=='primary' else 'S',z['d'],z['T'],LABEL[z['kind']],z['target'],stage['stage'],t['date'],t['changed'],endpoint(t['candidate_enclosure_component'],d=3),endpoint(t['continuous_cover_component'],d=3),endpoint(t['gap'],d=3)])
    table('all-gaps56','All datewise directed gaps and enclosure components',
          ['Cohort','$d$','$T$','Method','$q$','Stage','Date','Changes',r'$U-C$',r'$C-L$',r'$U-L$'],rows,
          'All stages of repetition zero are retained. A maximum of sums need not equal the sum of maxima. Quantities are upper bounds rounded upward, not estimates of disjoint causal errors. Complete cell arrays contain the exact endpoints used by the gate.',True)
    print('Nine R56 tables generated from complete replay')
if __name__=='__main__':main()
