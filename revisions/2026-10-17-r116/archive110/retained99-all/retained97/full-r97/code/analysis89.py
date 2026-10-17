"""Source-bound descriptive analysis; no refitting, selection change or new sampling."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, itertools, json, statistics
R=Path(__file__).resolve().parents[1]
ARMS=('adaptive','bisection','analytic','relu','polynomial')
LABEL={'adaptive':'Adaptive','bisection':'Bisection','analytic':'Analytic','relu':'ReLU','polynomial':'Quadratic'}
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
def need(x,message):
    if not x:raise AssertionError(message)
def decimal(x,lower=True,digits=6):
    x=F(x);s=10**digits;v=x.numerator*s//x.denominator if lower else -((-x.numerator*s)//x.denominator)
    return ('-' if v<0 else '')+str(abs(v)//s)+'.'+str(abs(v)%s).zfill(digits)
def code(name):
    if name=='zero':return 'Zero'
    rule,basis,n=name.split('-');return ('C' if rule=='calibrated' else 'L')+('R' if basis=='relu' else 'B')+n[1:]
def table(file,caption,label,heads,rows,note='',long=False):
    head=' & '.join(heads)+r' \\'+'\n';body=''.join(' & '.join(map(str,row))+r' \\'+'\n' for row in rows)
    cols='l'+'r'*(len(heads)-1)
    if long:
        text='{\\small\\setlength{\\tabcolsep}{3pt}\n\\begin{longtable}{'+cols+'}\n\\caption{'+caption+'}\\label{'+label+r'}\\'+'\n\\hline\n'+head+'\\hline\n\\endfirsthead\n\\hline\n'+head+'\\hline\n\\endhead\n'+body+'\\hline\n\\end{longtable}}\n\\noindent{\\footnotesize '+note+'}\n'
    else:
        text='\\begin{table}[htbp]\n\\centering\\caption{'+caption+'}\\label{'+label+'}\n{\\small\\setlength{\\tabcolsep}{3pt}\\begin{tabular}{'+cols+'}\n\\hline\n'+head+'\\hline\n'+body+'\\hline\n\\end{tabular}}\n\\par\\smallskip{\\footnotesize '+note+'}\n\\end{table}\n'
    (R/'tables'/file).write_text(text)

def economic():
    root=R/'results85';s=read(root/'SUMMARY85.json');rows=[]
    for stream in ('calibration','evaluation'):
        r=read(root/(stream+'.json'));need(r['estimands']==72,'Full paired family')
        for estimator in ('cash','conditional'):
            for pair in r['inference'][estimator]:
                lo,hi=map(F,pair['interval_exact']);w={k:F(v) for k,v in pair['width_decomposition'].items()}
                need(sum(w.values())==hi-lo,'Exact width decomposition')
                rows.append([('C' if stream=='calibration' else 'E')+('C' if estimator=='cash' else 'A'),code(pair['first'])+'--'+code(pair['second']),decimal(lo),decimal(hi,False),format(float(w['numerical']),'.2e'),decimal(w['sampling_variance'],False),decimal(w['finite_support'],False)])
    need(len(rows)==144,'All 144 contrasts')
    table('all-prospective86.tex','Complete original-law pairwise evaluation and interval widths','tab:allprospective89',
          ['Set','First--second','Lower','Upper','Enclosure','Variance','Support'],rows,
          'Set: C/E denotes calibration/evaluation; C/A denotes cash/analytically conditioned estimation. Controller codes C/L denote calibrated/legacy qualification, R/B denote ReLU/Bernstein, and 8/16 is the acquisition size. Directed endpoints and allowances round outwards; enclosure widths are displayed in scientific notation. Exact rational records determine all conclusions. These are reconstructions of the fixed R85 streams, not additional independent observations.',True)
    rows=[];selected=s['selected_controller']
    for other,interval in sorted(s['evaluation_selected_minus_comparators'].items()):
        if other==selected:continue
        lo,hi=map(F,interval);rows.append([code(other),decimal(lo),decimal(hi,False),decimal(-hi)])
    table('prices86.tex','Every selected-service quality and extra-fee breakpoint','tab:pricesprospective89',
          ['Comparator','Cost lower','Cost upper','Fee ceiling'],rows,
          'Selected service: calibrated Bernstein with acquisition size 16. At zero computation price and unit value of normalized loss, the sufficient extra-fee ceiling is minus the exact upper cost endpoint. Its display rounds down. At general prices, subtract the priced resource difference and multiply the quality term by the declared loss value. Negative ceilings remain in the table; the normalized units are not a monetary calibration.')
    return {'summary_sha256':sha(root/'SUMMARY85.json'),'original_rows':139264,'new_independent_rows_in_reconstruction':0,
            'contrasts':144,'selected':selected,'regret_upper':s['evaluation_selector_regret_upper']}

def shared():
    root=R/'results89';fit=read(root/'FIT89.json');models=read(root/'MODELS89.json');selector=read(root/'SELECTOR89.json');cal=read(root/'CALIBRATION89.json');inputs=read(root/'EVALUATION_INPUTS89.json')
    need(sha(root/'MODELS89.json')==fit['models_sha256']==selector['models_sha256']==inputs['models_sha256'],'Model freeze')
    need(sha(root/'TRAIN89.json')==fit['training_sha256'],'Training freeze')
    need(sha(root/'CALIBRATION89.json')==selector['calibration_sha256'],'Calibration freeze')
    need(sha(root/'SELECTOR89.json')==inputs['selector_sha256'],'Selector precedes evaluation')
    need(fit['fit_attempts']==2 and fit['training_rows']==256,'All attempted fits')
    need(set(inputs['states'])=={'2','4','8'} and all(len(v)==128 for v in inputs['states'].values()),'All held-out dimensions')
    score={}
    for arm in ARMS:
        rr=[x for group in cal['records'][arm].values() for x in group]
        need(len(rr)==128 and all(x['status']=='passed' for x in rr),'All calibration services')
        score[arm]=sum(x['counts']['q_queries'] for x in rr)
    need(score==selector['total_q_queries'],'Prespecified calibration score')
    need(selector['selected']==min(ARMS,key=lambda a:(score[a],ARMS.index(a))),'No ex post selection')
    result={};reference_records={};timing_rows=[];repetition_rows=[];mismatches=[]
    for machine in ('arm64','x86_64'):
        manifest=read(root/machine/'RUNS89.json');need(len(manifest['runs'])==45,'All complete-process repetitions')
        need(manifest['input_sha256']==sha(root/'EVALUATION_INPUTS89.json'),'Identical machine inputs')
        need(manifest['selector']==selector,'Identical machine selector')
        identities={(x['arm'],x['dimension'],x['repetition']) for x in manifest['runs']}
        need(identities==set(itertools.product(ARMS,(2,4,8),range(3))),'Complete process grid')
        result[machine]={'metadata':manifest['metadata'],'cells':{},'model_payload_bytes':manifest['model_payload_bytes']}
        for d,arm in itertools.product((2,4,8),ARMS):
            group=[x for x in manifest['runs'] if x['arm']==arm and x['dimension']==d];times=[];peak=[];canonical=None
            for run in sorted(group,key=lambda x:x['repetition']):
                p=root/run['output'];need(run['returncode']==0 and sha(p)==run['output_sha256'],'Actual successful output and exact hash')
                worker=read(p);rr=worker['records'];need(len(rr)==128,'Every evaluation state retained')
                for i,row in enumerate(rr):
                    need(row['row']==i and row['status']=='passed','State identity and service status')
                    c=row['counts'];need(c['q_queries']==c['nonterminal_queries']+c['terminal_queries'],'No terminal double counting')
                    need(0<=row['gap']<=1/64 and row['lower']<=row['upper'],'Same certified precision')
                if canonical is None:canonical=rr
                else:need(rr==canonical,'Repetition changes numerical work or result')
                times.append(run['complete_process_seconds']);peak.append(worker['peak_rss_kib'])
                repetition_rows.append([('ARM' if machine=='arm64' else 'x86'),d,LABEL[arm],run['repetition']+1,format(times[-1],'.6f'),worker['peak_rss_kib']])
            counts={k:sum(x['counts'][k] for x in canonical) for k in canonical[0]['counts'] if not k.startswith('max_')}
            dense={k:sum(x['model_work'][k] for x in canonical) for k in ('multiplications','additions','divisions','relu_gates')}
            item={'counts':counts,'dense_model_work':dense,'zero_progress_probes':sum(x['zero_progress_probes'] for x in canonical),
                  'largest_gap':max(x['gap'] for x in canonical),'process_seconds':times,'peak_rss_kib':peak,'mean_q_queries':counts['q_queries']/128}
            result[machine]['cells'][f'{arm}-d{d}']=item
            timing_rows.append([('ARM' if machine=='arm64' else 'x86'),d,LABEL[arm],format(min(times),'.4f'),format(statistics.median(times),'.4f'),format(max(times),'.4f'),max(peak)])
            if machine=='arm64':reference_records[(d,arm)]=canonical
            else:
                for i,(a,b) in enumerate(zip(reference_records[(d,arm)],canonical)):
                    if a['counts']!=b['counts'] or a['action']!=b['action']:mismatches.append({'dimension':d,'arm':arm,'row':i,'counts_differ':a['counts']!=b['counts'],'action_difference':b['action']-a['action']})
    rows=[];diagnostic=[];regret={}
    for d in (2,4,8):
        scores={a:result['arm64']['cells'][f'{a}-d{d}']['counts']['q_queries'] for a in ARMS};minimum=min(scores.values())
        regret[str(d)]={'selected':selector['selected'],'minimum_total_q':minimum,'selected_total_q':scores[selector['selected']],
                        'empirical_mean_work_regret':(scores[selector['selected']]-minimum)/128}
        for arm in ARMS:
            v=result['arm64']['cells'][f'{arm}-d{d}'];c=v['counts'];rows.append([d,LABEL[arm],c['nonterminal_queries'],c['terminal_queries'],c['model_rows'],format(v['mean_q_queries'],'.5f'),scores[arm]-minimum])
            diagnostic.append([d,LABEL[arm],c['prediction_free_returns'],c['screen_attempts'],c['screen_returns'],c['refinements'],c['invalid_predictions'],c['feasibility_repairs'],v['zero_progress_probes']])
    table('work89.tex','Shared proposals on the held-out original-law workload','tab:work89',
          ['$d$','Service','Nonterminal','Terminal','Model calls','Mean queries','Excess'],rows,
          'Each row covers the same 128 states in its dimension. All services meet tolerance $1/64$. Mean queries counts nonterminal and terminal queries once. Excess is total queries above the best declared service in that held-out dimension, not population or policy-cost regret. Dimension four is absent from training and calibration. Three repetitions and the second machine do not multiply the sample size.')
    table('timing89.tex','Complete service-process timing on two architectures','tab:timing89',
          ['Machine','$d$','Service','Minimum','Median','Maximum','Peak RSS'],timing_rows,
          'Times are seconds from process creation through shutdown, including loading and serialization, for all 128 states. RSS is the largest recorded process capacity in KiB, not an additive cost. All three repetitions are retained. Architecture and image differences are not a randomized hardware treatment.',True)
    table('all-timing89.tex','Every complete-process timing repetition','tab:alltiming89',
          ['Machine','$d$','Service','Run','Seconds','RSS (KiB)'],repetition_rows,
          'No repetition is selected or deleted. These 90 process runs evaluate the same 384 held-out states with five services; they are not 90 independent population experiments.',True)
    table('diagnostics89.tex','Distinct prediction, protection and service events','tab:diagnostics89',
          ['$d$','Service','No model','Screens','Close','Refine','Invalid','Repair','Zero'],diagnostic,
          'No model: prediction-free service returns. Close: screen closures. Refine: protected refinements. Invalid and repair count prediction diagnostics, not failed certificates. Zero counts probes improving neither bound. Learned-model calls and dense arithmetic are separate from these events. Logical network multiplication/addition/division counts are in the exact source-bound summary; interval-operation counts and energy are not measured.',True)
    out={'status':'passed','fit':fit,'calibration_total_queries':score,'selected':selector['selected'],'evaluation_regret':regret,'machines':result,
         'crossmachine_action_or_count_disagreements':mismatches,'source_hashes':{p.name:sha(p) for p in (root/'FIT89.json',root/'MODELS89.json',root/'SELECTOR89.json',root/'EVALUATION_INPUTS89.json')},
         'training_rows':256,'calibration_rows':128,'evaluation_rows':384,'fit_attempts':2,'process_runs':90,'independent_rows_added_by_machine_replay':0,
         'scope':'Seeded finite-catalogue query work and complete-process timings. No new original-law complete-policy cost sample or hardware/energy calibration.'}
    save(R/'audit/SHARED89.json',out);return out

if __name__=='__main__':
    econ=economic();study=shared();save(R/'audit/ANALYSIS89.json',{'status':'passed','economic_reconstruction':econ,'shared_summary_sha256':sha(R/'audit/SHARED89.json'),'crossmachine_disagreements':len(study['crossmachine_action_or_count_disagreements'])})
    print(json.dumps({'economic':econ,'selector':study['selected'],'query_regret':study['evaluation_regret'],'crossmachine_disagreements':len(study['crossmachine_action_or_count_disagreements'])},indent=2))
