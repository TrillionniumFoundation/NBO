"""Read-only reporter for an actually completed validation D.

No economic solver or production/scientific module is imported or executed.
Checks concern recorded bytes, exact saved interval arithmetic, aggregate
statistics and scope. This is not a rerun of the 983-policy validation.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import statistics
import subprocess
import time
import traceback

WORK = Path('/workspace/scratch/913249553838')
REV = WORK/'NBO/revisions/2026-10-18-r119'
SOURCE = 'cafd38aedc5bcbddf5aafee2481fbf5e9a267bab'
ARMS = ('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
SERVICES = ('compiled','geometric','active-tail','masked-tail','budgeted-tail','fused-tail')
LABELS = {'online':'Semi-analytic','quadratic':'Quadratic (rank six)','relu':'ReLU','hinge':'Equivalent hinge','spline':'Coordinate spline','poly2':'Full quadratic','poly3':'Cubic polynomial','grid':'Tensor grid'}
SHORT = dict(zip(ARMS, ('O','Q','R','H','S','P2','P3','G')))
SS = dict(zip(SERVICES, ('C','G','T','M','B','F')))
BETA, EPS = F(15,16), F(1,2**20)


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as s:
        for block in iter(lambda:s.read(1<<20),b''):h.update(block)
    return h.hexdigest()


def conv(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):conv(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [conv(v) for v in x]
    return x


def save(path,obj):
    with path.open('x') as s:json.dump(conv(obj),s,indent=2,sort_keys=True,allow_nan=False);s.write('\n')


def table_csv(path,rows):
    if not rows:return
    with path.open('x',newline='') as s:
        w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader()
        for row in rows:w.writerow(conv(row))


def fixed(v,digits=9,upper=False,scale=1):
    x=F(v)*scale*10**digits
    n=-((-x.numerator)//x.denominator) if upper else x.numerator//x.denominator
    sign='-' if n<0 else '';n=abs(n)
    return sign+str(n//10**digits)+'.'+str(n%10**digits).zfill(digits)


def interval_text(lo,hi,digits=9,scale=1):
    return '['+fixed(lo,digits,scale=scale)+', '+fixed(hi,digits,upper=True,scale=scale)+']'


def mean_sign(lo,hi):
    return 'negative' if hi<0 else 'positive' if lo>0 else 'exact_zero' if lo==hi==0 else 'contains_zero'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    out=args.output;started=time.time();checks=0
    ddir=REV/'results119/validation119d_attempt01'
    def need(condition,text):
        nonlocal checks
        checks+=1
        if not condition:raise AssertionError(text)
    try:
        external_path=REV/'results119/logs/validation119d_attempt01.json'
        external=json.loads(external_path.read_text())
        need(external.get('exit_code')==0,'External actual execution must have exited zero before reporting')
        need(external['source_commit']==SOURCE,'External actual source')
        need(external['log_sha256']==digest(REV/'results119/logs/validation119d_attempt01.log'),'External log hash')
        execution=json.loads((ddir/'EXECUTION119D.json').read_text())
        summary=json.loads((ddir/'SUMMARY119D.json').read_text())
        provenance=json.loads((ddir/'PROVENANCE119D.json').read_text())
        need(execution['status']=='passed' and summary['status']=='passed','Actual complete validation status')
        need(execution['custody_commit']==provenance['custody_commit']==SOURCE,'Exact actual prospective source')
        need(not (ddir/'FAILED119D.json').exists(),'Failed attempt is not a passed completion')
        source_inventory=[]
        for r in provenance['source_files']:
            p=REV/r['path'];actual=digest(p)
            need(actual==r['sha256'],'Current source SHA '+r['path'])
            rel=p.relative_to(WORK/'NBO').as_posix()
            raw=subprocess.run(['git','show',f'{SOURCE}:{rel}'],cwd=WORK/'NBO',check=True,capture_output=True).stdout
            need(hashlib.sha256(raw).hexdigest()==actual,'Git committed source SHA '+r['path'])
            source_inventory.append(dict(path=r['path'],bytes=p.stat().st_size,sha256=actual))
        need(len(source_inventory)==49,'All 49 committed source files')
        input_inventory=[]
        for r in provenance['input_files']:
            p=REV/r['path'];need(p.stat().st_size==r['bytes'] and digest(p)==r['sha256'],'Frozen input '+r['path'])
            input_inventory.append(r)
        need(len(input_inventory)==97,'All 97 input files')
        execution_files={r['path']:r for r in execution['files']}
        actual_before_receipt={p.relative_to(ddir).as_posix() for p in ddir.rglob('*') if p.is_file() and p.name!='EXECUTION119D.json'}
        need(set(execution_files)==actual_before_receipt,'Execution file manifest completeness')
        output_inventory=[]
        for rel,r in execution_files.items():
            p=ddir/rel;need(p.stat().st_size==r['bytes'] and digest(p)==r['sha256'],'Execution output '+rel)
            output_inventory.append(dict(path='results119/validation119d_attempt01/'+rel,**{k:r[k] for k in ('bytes','sha256')}))
        for p in [ddir/'EXECUTION119D.json',external_path,REV/'results119/logs/validation119d_attempt01.log']:
            output_inventory.append(dict(path=p.relative_to(REV).as_posix(),bytes=p.stat().st_size,sha256=digest(p)))
        frozen=json.loads((REV/'VALIDATION_D119_KEYS.json').read_text())
        keys={r['key_id']:r for r in frozen['keys']};need(len(keys)==983,'983 frozen exact keys')
        observed={};state_rows={}
        for i,arm,service in itertools.product((0,1),ARMS,SERVICES):
            p=REV/f'results119/primary119c/catalogue/{i}-{arm}-{service}.json'
            data=json.loads(p.read_text());need(len(data['rows'])==144,'All fixed primary rows')
            for raw in data['rows']:
                kid=f"{i}:{raw['row']}:{float(raw['action']).hex()}";key=keys[kid]
                need([float(raw['x0']).hex(),float(raw['x1']).hex()]==key['state_binary64'],'Exact observed state identity')
                need(str(F(float(raw['action'])))==key['action_exact'],'Exact observed action identity')
                state=(float(raw['x0']).hex(),float(raw['x1']).hex());sr=(i,raw['row'])
                need(sr not in state_rows or state_rows[sr]==state,'Common state over every representation/service')
                state_rows[sr]=state;observed[(i,raw['row'],arm,service)]=(kid,raw)
        need(len(observed)==13824,'Every primary decision covered')
        references={}
        for block in json.loads((REV/'results119/primary119c/REFERENCE119.json').read_text())['records']:
            for r in block['unique']:references[f"{block['index']}:{r['row']}:{float(r['action']).hex()}"]=r
        need(set(references)==set(keys),'All original reference keys covered')
        policies=[json.loads(line) for line in (ddir/'POLICY_ENCLOSURES119D.jsonl').read_text().splitlines()]
        need(len(policies)==983 and len({r['key_id'] for r in policies})==983,'Every D key appears exactly once')
        need({r['key_id'] for r in policies}==set(keys),'Exact D key exhaustion')
        results={r['key_id']:r for r in policies};terminal_nodes=0;primitive_bytes=0
        service_counts={'overlap':0,'production_contains_independent':0,'independent_contains_production':0}
        reference_counts=dict(service_counts);service_detail=[];policy_detail=[]
        def compare(record,lo,hi):
            a,b=F(float(record['lower'])),F(float(record['upper']))
            return a<=hi and lo<=b,a<=lo and hi<=b,lo<=a and b<=hi
        for row in policies:
            key=keys[row['key_id']];need(row['status']=='passed' and not row['failures'],'Passed D key with retained failures empty')
            need(list(map(F,row['state']))==list(map(F,key['state_exact'])) and F(row['action'])==F(key['action_exact']),'Saved exact policy identity')
            trace=ddir/row['trace']['path'];need(digest(trace)==row['trace']['sha256'],'Compressed primitive trace hash')
            h=hashlib.sha256();values=[];maximum_gap=F(0);trace_count=0
            with gzip.open(trace,'rb') as stream:
                for line in stream:
                    h.update(line);node=json.loads(line);k=trace_count;trace_count+=1
                    need(node['node']==k and F(node['z'])==-F(1,32)+F(k,2048),'Exact saved whole-support mesh')
                    lo,hi=F(node['lower']),F(node['upper']);need(lo<=hi and hi-lo<=EPS,'Saved terminal interval and allowance')
                    need(F(node['polynomial'][2])==5,'Saved exact original quadratic coefficient')
                    values.append((lo,hi));maximum_gap=max(maximum_gap,hi-lo)
            need(h.hexdigest()==row['trace']['uncompressed_jsonl_sha256'],'Uncompressed primitive stream hash')
            need(trace_count==129==row['terminal_contexts'],'Exactly 129 nodes per key')
            need(maximum_gap==F(row['maximum_terminal_gap']),'Per-policy maximum terminal gap')
            terminal_nodes+=trace_count;primitive_bytes+=trace.stat().st_size
            alpha=F(row['alpha']);lower_count=int(64*(1-alpha));upper_count=int(128*(1-alpha))
            low_values=sorted([values[2*j+1][0] for j in range(64)],reverse=True)
            upper_values=sorted([values[k][1] for j in range(64) for k in (2*j,2*j+2)],reverse=True)
            qlo=F(row['stage'])+BETA*sum(low_values[:lower_count],F(0))/lower_count
            qhi=F(row['stage'])+BETA*sum(upper_values[:upper_count],F(0))/upper_count
            jlo,jhi=qlo,qhi+BETA*EPS
            need(qlo==F(row['optimum_continuation_lower']) and qhi==F(row['optimum_continuation_upper']),'Independent saved-node Q aggregation')
            need(jlo==F(row['implemented_policy_lower']) and jhi==F(row['implemented_policy_upper']),'J allowance added exactly once')
            saved_comps={r['policy']:r for r in row['original_service_comparisons']}
            need(set(saved_comps)==set(key['policies']),'Every associated original service comparison retained')
            for policy in key['policies']:
                arm,service=policy.split('/');kid,raw=observed[(key['index'],key['row'],arm,service)]
                need(kid==row['key_id'],'Associated policy key')
                comp=compare(raw,jlo,jhi);saved=saved_comps[policy]
                need(comp==(saved['overlap'],saved['production_contains_independent_enclosure'],saved['independent_contains_production_interval']),'Saved service interval comparison')
                for field,value in zip(service_counts,comp):service_counts[field]+=int(value)
                service_detail.append(dict(index=key['index'],row=key['row'],arm=arm,service=service,key_id=kid,
                    overlap=comp[0],production_contains_independent=comp[1],independent_contains_production=comp[2]))
            comp=compare(references[row['key_id']],jlo,jhi);saved=row['existing_reference_comparison']
            need(comp==(saved['overlap'],saved['production_contains_independent_enclosure'],saved['independent_contains_production_interval']),'Saved shared-compiler reference comparison')
            for field,value in zip(reference_counts,comp):reference_counts[field]+=int(value)
            policy_detail.append(dict(key_id=row['key_id'],index=row['index'],row=row['row'],Q_lower=qlo,Q_upper=qhi,J_lower=jlo,J_upper=jhi,
                policy_width=jhi-jlo,policy_seconds=row['policy_seconds'],policy_cpu_seconds=row['policy_cpu_seconds'],reference_overlap=comp[0],
                shared_compiler_reference_contains_independent=comp[1],independent_contains_shared_compiler_reference=comp[2],
                maximum_retained_fraction_bits=row['maximum_retained_fraction_bits'],primitive_trace=row['trace']['path']))
        need(terminal_nodes==126807==summary['primitive_contexts'],'All 126807 primitive trace records retained')
        need(sum(row['checks'] for row in policies)==summary['checks'],'Actual native validation check count')
        need(service_counts['overlap']==13824 and reference_counts['overlap']==983,'All compatibility checks passed')
        means=[];contrasts=[];identities=[]
        def bounds(kid):return F(results[kid]['implemented_policy_lower']),F(results[kid]['implemented_policy_upper'])
        for index,arm,service in itertools.product((0,1),ARMS,SERVICES):
            kk=[observed[(index,j,arm,service)][0] for j in range(144)]
            lo=sum((bounds(k)[0] for k in kk),F(0))/144;hi=sum((bounds(k)[1] for k in kk),F(0))/144
            means.append(dict(index=index,alpha=('.5','.75')[index],arm=arm,service=service,lower=lo,upper=hi,width=hi-lo))
        for index,arm in itertools.product((0,1),ARMS):
            for left,right in itertools.combinations(SERVICES,2):
                same=all(observed[(index,j,arm,left)][0]==observed[(index,j,arm,right)][0] for j in range(144))
                identities.append(dict(index=index,arm=arm,left=left,right=right,identical_every_primary_state=same,exact_mean_policy_difference='0' if same else None))
        for index in (0,1):
            for left,right in itertools.combinations(ARMS,2):
                lo,hi,same=F(0),F(0),0
                for j in range(144):
                    a=observed[(index,j,left,'compiled')][0];b=observed[(index,j,right,'compiled')][0]
                    if a==b:same+=1;continue
                    al,au=bounds(a);bl,bu=bounds(b);lo+=al-bu;hi+=au-bl
                lo,hi=lo/144,hi/144
                contrasts.append(dict(index=index,alpha=('.5','.75')[index],left=left,right=right,lower=lo,upper=hi,
                    identical_policy_states=same,sign=mean_sign(lo,hi)))
        saved_means={(r['index'],r['arm'],r['service']):r for r in summary['all_96_arm_service_mean_intervals']}
        need(len(saved_means)==len(means)==96,'All 96 means')
        for row in means:
            old=saved_means[(row['index'],row['arm'],row['service'])]
            need(row['lower']==F(old['lower']) and row['upper']==F(old['upper']),'Exact independently reaggregated mean')
        saved_contrasts={(r['index'],r['left'],r['right']):r for r in summary['all_56_arm_mean_contrasts']}
        need(len(saved_contrasts)==len(contrasts)==56,'All 56 arm contrasts')
        for row in contrasts:
            old=saved_contrasts[(row['index'],row['left'],row['right'])]
            need(row['lower']==F(old['lower']) and row['upper']==F(old['upper']) and row['sign']==old['sign'] and row['identical_policy_states']==old['identical_policy_states'],'Exact independently reaggregated arm contrast')
        saved_id={(r['index'],r['arm'],r['left'],r['right']):r for r in summary['original_service_identity_cells']}
        need(len(saved_id)==len(identities)==240,'All 240 service identity cells')
        for row in identities:need(saved_id[(row['index'],row['arm'],row['left'],row['right'])]==row,'Exact original service identity record')
        need(all(r['identical_every_primary_state'] for r in identities),'All recorded complete policies remain identical across services')
        signs={s:sum(r['sign']==s for r in contrasts) for s in ('negative','positive','exact_zero','contains_zero')}
        def contrast(left,right,index):
            a=next((r for r in contrasts if (r['index'],r['left'],r['right'])==(index,left,right)),None)
            if a is not None:return a['lower'],a['upper']
            a=next(r for r in contrasts if (r['index'],r['left'],r['right'])==(index,right,left))
            return -a['upper'],-a['lower']
        relu_comparisons=[dict(index=i,control=c,lower=contrast('relu',c,i)[0],upper=contrast('relu',c,i)[1]) for i in (0,1) for c in ('quadratic','hinge','online','grid','spline','poly3','poly2')]
        report=dict(status='passed_read_only_record_hash_and_exact_aggregate_audit',checks=checks,source_commit=SOURCE,
            actual_validation_status=summary['status'],actual_validation_checks=summary['checks'],policy_keys=983,primary_records=13824,
            primitive_contexts=terminal_nodes,source_files=len(source_inventory),input_files=len(input_inventory),
            output_files_including_external_launcher=len(output_inventory),output_bytes=sum(r['bytes'] for r in output_inventory),
            compressed_primitive_trace_bytes=primitive_bytes,service_interval_comparisons=service_counts,shared_compiler_reference_comparisons=reference_counts,
            all_96_means_exactly_reaggregated=True,all_56_contrasts_exactly_reaggregated=True,all_240_service_identities_exactly_verified=True,
            arm_contrast_sign_counts=signs,relu_original_mean_cost_contrasts=relu_comparisons,
            policy_width_range=[min(r['policy_width'] for r in policy_detail),max(r['policy_width'] for r in policy_detail)],
            mean_interval_width_range=[min(r['width'] for r in means),max(r['width'] for r in means)],
            independent_validation_cost=dict(external_elapsed_seconds=external['elapsed_seconds'],internal_process_seconds=execution['inside_process_seconds'],
                total_cpu_seconds=execution['cpu_seconds'],per_policy_seconds_sum=sum(r['policy_seconds'] for r in policies),
                per_policy_seconds_range=[min(r['policy_seconds'] for r in policies),max(r['policy_seconds'] for r in policies)],
                per_policy_seconds_median=statistics.median(r['policy_seconds'] for r in policies),input_binding_seconds=provenance['input_binding_seconds'],
                aggregation_seconds=summary['aggregation_seconds'],max_rss_kib=summary['max_rss_kib']),
            failures=[],scope='No economic solver, campaign or competitive timer rerun. Independent saved-node arithmetic, recorded hashes and complete deterministic aggregates only. Interval overlap is compatibility, not verification of each fine shared-compiler endpoint. D uses independent V1* enclosures plus the unchanged beta*2^-20 future-controller allowance; it is not direct evaluation of the floating controller or an independent global date-zero regret optimum.',
            after_known_C=True,population_inference=False,neural_success_is_not_a_pass_condition=True,
            read_only_reporter_sha256=digest(Path(__file__)),read_only_report_created_unix=time.time())
        save(out/'R119D_NUMERICAL_REVIEW.json',report)
        table_csv(out/'R119D_MEANS96.csv',means);table_csv(out/'R119D_CONTRASTS56.csv',contrasts)
        table_csv(out/'R119D_IDENTITIES240.csv',identities);table_csv(out/'R119D_POLICY_ENCLOSURES983.csv',policy_detail)
        table_csv(out/'R119D_SERVICE_COMPATIBILITY13824.csv',service_detail)
        save(out/'R119D_EVIDENCE_MANIFEST.json',dict(source_commit=SOURCE,scope='D-only outputs and original input/source bindings; A/B/C files unchanged.',
            source_files=source_inventory,input_files=input_inventory,output_files=output_inventory,
            output_bytes=sum(r['bytes'] for r in output_inventory),scientific_rerun=False))
        write_tex(out,report,means,contrasts,identities)
        save(out/'R119D_REPORTER_EXECUTION.json',dict(status='passed',started_unix=started,ended_unix=time.time(),
            reporter_sha256=digest(Path(__file__)),scope='Read-only completed-record report; no scientific reexecution',
            outputs=[dict(path=p.name,bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(out.iterdir()) if p.is_file()]))
        print(json.dumps(conv({k:report[k] for k in ['status','checks','actual_validation_checks','policy_keys','primitive_contexts','arm_contrast_sign_counts','service_interval_comparisons','shared_compiler_reference_comparisons','independent_validation_cost']}),indent=2))
    except BaseException:
        save(out/'FAILED_REPORT119D.json',dict(status='failed_read_only_reporting_attempt',started_unix=started,ended_unix=time.time(),exception=traceback.format_exc(),reporter_sha256=digest(Path(__file__))))
        raise


def write_tex(out,report,means,contrasts,identities):
    selected=[r for r in means if r['service']=='compiled']
    table=['\\begin{table}[t]\\centering\\small',
      '\\caption{Independent Fraction original-policy mean-cost enclosures on the fixed catalogue.}\\label{tab:independent119d}',
      '\\begin{tabular}{llrr}\\hline','$\\alpha$ & Representation & Lower mean cost & Upper mean cost \\\\ \\hline']
    for r in selected:table.append(f"${'1/2' if r['index']==0 else '3/4'}$ & {LABELS[r['arm']]} & {fixed(r['lower'])} & {fixed(r['upper'],upper=True)} \\\\")
    table+=['\\hline\\end{tabular}',r'\\[4pt]\parbox{.96\linewidth}{\footnotesize Each endpoint is an outward decimal display of an exact rational bound. Every mean weights the same 144 realized original states equally. All six services return exactly the same complete policy within an arm; all 96 arm/service/risk means are retained in the development companion. The future-controller allowance is $\beta 2^{-20}$. These intervals are numerical enclosures, not sampling confidence intervals.}','\\end{table}']
    (out/'R119_TABLE119D_MEANS16.tex').write_text('\n'.join(table)+'\n')
    full=[r'\small\begin{longtable}{clcrr}',r'\caption{All 96 independently reconstructed arm/service/risk mean intervals.}\label{tab:means96d}\\',r'\hline $\alpha$ & Arm & Service & Lower & Upper \\ \hline\endfirsthead',r'\hline $\alpha$ & Arm & Service & Lower & Upper \\ \hline\endhead']
    for r in means:full.append(f"${'1/2' if r['index']==0 else '3/4'}$ & {SHORT[r['arm']]} & {SS[r['service']]} & {fixed(r['lower'])} & {fixed(r['upper'],upper=True)} \\\\")
    full += [r'\hline\end{longtable}\normalsize']
    (out/'R119_TABLE119D_MEANS96.tex').write_text('\n'.join(full)+'\n')
    cc=[r'\small\begin{longtable}{cccrrc}',r'\caption{All 56 independent original-policy mean contrasts, in units of $10^{-6}$.}\label{tab:contrasts56d}\\',r'\hline $\alpha$ & Left & Right & Lower & Upper & Sign \\ \hline\endfirsthead',r'\hline $\alpha$ & Left & Right & Lower & Upper & Sign \\ \hline\endhead']
    sn={'negative':'$-$','positive':'$+$','exact_zero':'$0$','contains_zero':'unresolved'}
    for r in contrasts:cc.append(f"${'1/2' if r['index']==0 else '3/4'}$ & {SHORT[r['left']]} & {SHORT[r['right']]} & {fixed(r['lower'],4,scale=1000000)} & {fixed(r['upper'],4,True,1000000)} & {sn[r['sign']]} \\\\")
    cc += [r'\hline\end{longtable}\normalsize']
    (out/'R119_TABLE119D_CONTRASTS56.tex').write_text('\n'.join(cc)+'\n')
    signs=report['arm_contrast_sign_counts'];cost=report['independent_validation_cost'];comp=report['shared_compiler_reference_comparisons'];svc=report['service_interval_comparisons']
    rq=[r for r in report['relu_original_mean_cost_contrasts'] if r['control']=='quadratic']
    main=rf'''\subsection{{Independent value enclosures for every recorded original policy}}
\label{{sec:study119d}}
The 1,024-bin reference uses a separate whole-support risk partition with the
shared verified terminal compiler. To check original policy values through a
separate implementation, validation D was frozen at \texttt{{cafd38ae}}
after all A--C outcomes were known. It fixes 64 whole-support cells and up to 32
rational terminal bisections on every one of the 983 realized state/action/risk
keys represented by C's 13,824 primary decisions. The exact binary state and
action identities are retained. This is validation of the known catalogue.

The standard-library implementation reconstructs the original nonlinear
economic primitives, the terminal shock polynomial and its continuous AVaR
integral, and a feasible strong-convexity bracket for $V_1^*$. Conditional
Jensen bounds for $(V_1^*\circ F-\eta)_+$ and the repeated-endpoint secant
mixture give independent whole-support bounds for the original $Q$.
Adding the unchanged $\beta 2^{{-20}}$ future-controller allowance once gives
the complete-policy $J$ enclosure. The production compiler is not imported.
This does not directly evaluate the deployed floating terminal controller or
independently determine the global date-zero regret optimum.

All 983 keys and 126,807 exact terminal contexts completed, with
{report['actual_validation_checks']:,} recorded checks and no failed key.
The independent intervals overlap all 13,824 corresponding service intervals
and all 983 shared-compiler reference intervals. Overlap establishes
compatibility; it does not certify each fine reference endpoint merely from
intersection. All exact traces, checks and containment directions are retained.

\input{{new119/R119_TABLE119D_MEANS16}}

All 96 arm/service/risk means and all 56 arm contrasts are independently
reaggregated. There are {signs['negative']} strictly negative, {signs['positive']}
strictly positive, {signs['exact_zero']} exact-zero and {signs['contains_zero']}
unresolved contrast intervals in the fixed left-minus-right orientation.
The ReLU-minus-quadratic original mean-cost intervals are
${interval_text(rq[0]['lower'],rq[0]['upper'],4,1000000)}\times10^{{-6}}$
at $\alpha=1/2$ and
${interval_text(rq[1]['lower'],rq[1]['upper'],4,1000000)}\times10^{{-6}}$
at $\alpha=3/4$. The full contrast table retains every sign and exact tie.
All 240 arm/risk/service-pair cells have identical complete policies, preserving
the exact zero economic effect of changing only the certification service.
No favorable economic sign was a validation pass condition.

D requires {cost['external_elapsed_seconds']:.3f} seconds of additional actual
author-side validation time ({cost['total_cpu_seconds']:.3f} CPU seconds),
including its separately recorded binding, rational solves, primitive traces
and aggregation. This cost is reported separately from the unchanged A--C
acquisition and service clocks. D strengthens independent original-model value
evidence; it creates neither an unseen population result nor a neural-specific
adoption claim.
'''
    (out/'study_d119.tex').write_text(main)
    development=rf'''\section{{Validation D: complete independent original-policy evidence}}
\label{{sec:development119d}}
Validation D is a separately prospectively frozen, post-C numerical validation
at \texttt{{cafd38aedc5bcbddf5aafee2481fbf5e9a267bab}}.
Its fixed 983 exact keys exhaust all C primary records, with 492 keys at risk
$1/2$ and 491 at risk $3/4$. All 49 source files passed committed-byte binding
and all 97 original input files passed exact size/hash verification before
any economic evaluation. The completed read-only reporter rechecks these
identities, all primitive trace hashes and all saved-node interval aggregation,
without invoking an economic solver.

All 983 gzip traces retain 126,807 original terminal-node records. Their total
compressed size is {report['compressed_primitive_trace_bytes']:,} bytes.
The 983 independent policy widths range from
${fixed(report['policy_width_range'][0],12)}$ to
${fixed(report['policy_width_range'][1],12,True)}$.
The 96 mean widths range from ${fixed(report['mean_interval_width_range'][0],12)}$
to ${fixed(report['mean_interval_width_range'][1],12,True)}$.
The widths include the unchanged $\beta 2^{{-20}}$ future-policy allowance;
the outer 64-cell bracket does not independently certify date-zero optimal regret.

Every one of the 13,824 original service intervals overlaps its independent
policy enclosure. The service interval contains the independent interval in
{svc['production_contains_independent']:,} cases; the reverse containment holds
in {svc['independent_contains_production']:,} cases. All 983 prior shared-compiler
reference intervals overlap: {comp['production_contains_independent']} contain
the independent interval, and {comp['independent_contains_production']} are
contained in it. These two containment counts are reported separately from
overlap. Compatibility is not a proof that every prior fine endpoint is correct.

The external process takes {cost['external_elapsed_seconds']:.6f} seconds;
the internal recorded scope takes {cost['internal_process_seconds']:.6f}
seconds and {cost['total_cpu_seconds']:.6f} CPU seconds. The per-policy sum is
{cost['per_policy_seconds_sum']:.6f} seconds, with a range
[{cost['per_policy_seconds_range'][0]:.6f}, {cost['per_policy_seconds_range'][1]:.6f}]
and median {cost['per_policy_seconds_median']:.6f}. Input/source binding takes
{cost['input_binding_seconds']:.6f} seconds, aggregation
{cost['aggregation_seconds']:.6f} seconds, and maximum RSS is
{cost['max_rss_kib']:,} KiB. Per-policy cost includes its rational solve,
primitive trace close/hash and comparisons; result-log serialization remains
in the process total. These are additional validation costs, not new competitive
measurements of the unchanged services. The maximum retained Fraction bit length
does not count all arithmetic intermediates or bit operations.

The notation in the complete tables is O: semi-analytic; Q: rank-six quadratic;
R: ReLU; H: exactly equivalent hinge; S: coordinate spline; P2: full quadratic;
P3: cubic polynomial; G: tensor grid. Service notation is C: compiled;
G: geometric; T: active tail; M: masked tail; B: budgeted tail; F: fused tail.
Every printed interval endpoint is rounded outward from its exact Fraction.
All 240 service-pair identities are exact and all 96 means are retained below,
including the six repeated policy means for each arm/risk cell. In the contrast
table the orientation is left mean original-policy cost minus right; the units
are $10^{{-6}}$. Identical policies at a state cancel exactly before averaging.

\input{{new119/R119_TABLE119D_MEANS96}}
\input{{new119/R119_TABLE119D_CONTRASTS56}}

The machine-readable companion retains all 983 policy enclosures, all 13,824
service compatibility/containment rows, all 240 service identities, all 96 means
and all 56 arm contrasts. Each primitive trace has both its compressed SHA256
and its uncompressed JSONL-stream SHA256. The output manifest binds these to the
actual executed source and the original immutable inputs. No failed scientific
key or unresolved sign is removed; no positive neural sign is required for an
audit pass. A/B/C observations and their earlier negative findings remain intact.
'''
    (out/'development_d119.tex').write_text(development)


if __name__=='__main__':main()
