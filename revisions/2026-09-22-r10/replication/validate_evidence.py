"""R10 record, analytic-identity, preservation, and manuscript checks.
Spot checks supplement, and do not replace, the outward mathematical certificate.
"""
from __future__ import annotations
import argparse,contextlib,hashlib,io,json,math,pathlib,platform,re,subprocess,time
import numpy as np
import mpmath as mp
from fractions import Fraction
import verify_inputs,make_tables
from flexible_dual import source,point
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r10';OUT=REV/'results'
CHECKS=[]
def load(p):return json.loads(p.read_text())
def require(name,condition,details=None):
    CHECKS.append({'check':name,'passed':bool(condition),'details':details})
    if not condition:raise AssertionError(name+': '+str(details))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(x):
    if isinstance(x,dict):return all(finite(v) for v in x.values())
    if isinstance(x,list):return all(finite(v) for v in x)
    return not isinstance(x,float) or math.isfinite(x)
def run(pdf=True):
    start=time.perf_counter();require('frozen inputs',verify_inputs.run()['status']=='PASS')
    require('binary .2 is correctly rejected as an exact .2 upper bound',Fraction(.2)>Fraction('.2'))
    require('inward .2 is admitted',Fraction(np.nextafter(.2,-np.inf))<Fraction('.2'))
    summary=load(OUT/'scientific_summary.json')
    require('all three original targets accepted',summary['all_three_central_targets_met'] and summary['status']=='PASS')
    for k in [.5,2,8]:
        tag=f'k{k:g}';p=load(OUT/f'policy_certificate_{tag}.json');d=load(OUT/f'flexible_dual_{tag}.json')
        a=load(OUT/f'actor_{tag}.json');require('exact feasible controls '+tag,verify_inputs.check_actor(a))
        require('finite records '+tag,finite(p) and finite(d))
        require('complete refinement plan '+tag,d['status']=='complete' and d['planned_resolutions']==[[4,64],[8,128],[16,256]] and [r['source_boxes'] for r in d['records']]==[4096,16384,65536])
        require('original contract '+tag,d['original_payoff'] and d['original_continuous_actions'] and d['original_stopping_contract'])
        require('strict wealth feasibility '+tag,p['terminal_wealth_interval'][0]>.5)
        require('exit allowance not omitted '+tag,0<p['exit_probability_upper']<1.077e-31 and p['exit_payoff_correction_upper']>0)
        require('policy intervals refine '+tag,all(x['width']>y['width'] for x,y in zip(p['records'],p['records'][1:])))
        L=p['records'][-1]['policy_value_interval'][0]
        for r in d['records']:
            name=f'{tag}/{r["source_boxes"]}'
            require('upper above feasible payoff '+name,r['optimal_value_upper']>=p['records'][-1]['policy_value_interval'][1])
            require('outward regret difference '+name,Fraction(r['certified_regret_upper'])>=Fraction(r['optimal_value_upper'])-Fraction(L))
            require('precision flag exact '+name,r['target_met']==(r['certified_regret_upper']<.01))
            require('all correction signs '+name,r['source_taylor_remainder_upper']>0 and r['tangent_control_gap_upper']>=0 and r['variance_allowance_upper']>0 and r['localization_upper']>0 and r['covariance_correction_interval'][0]<=r['covariance_correction_interval'][1]<0)
        require('final regret below exact .01 '+tag,Fraction(d['records'][-1]['certified_regret_upper'])<Fraction('.01'))
        require('first level not falsely accepted '+tag,not d['records'][0]['target_met'])
        v=next(v for v in summary['economy'] if v['k']==k)
        require('summary matches independent endpoints '+tag,v['policy_value_interval']==p['records'][-1]['policy_value_interval'] and v['optimal_value_interval']==[L,d['records'][-1]['optimal_value_upper']])
        require('positive access '+tag,v['optimal_access_welfare_interval'][0]>0)
    pc=load(OUT/'tangent_primitive_checks.json')
    require('supporting-plane primitive margins',pc['Huu_upper_u_1.5_to_2.3_at_y12']<-.0862 and pc['beta_upper_u_2.3_to_2.5_at_y12']<-.9687 and pc['beta_lower_u_2.2_at_y12']>-.9573)
    require('bounded source and trace',pc['source_floor']>-7.1 and pc['source_ceiling']<0 and pc['beta_absolute_upper']<1.1 and pc['continuation_source_floor']>-8)
    for e in summary['cost_effects']:
        require('positive optimal welfare effect '+str(e['cost_pair']),e['positive'] and e['optimal_welfare_loss_interval'][0]>0)
    require('cost-two-to-eight effect exceeds full width',next(e for e in summary['cost_effects'] if e['cost_pair']==[2,8])['entire_effect_exceeds_interval_width'])
    # Independent high-precision differentiation of the conjugate away from switches.
    mp.mp.dps=70;rng=np.random.default_rng(20260922)
    for i in range(48):
        u=float(rng.uniform(1.5,2.5));l=float(rng.uniform(math.log(.2),math.log(12)))
        def psi(uu,ll):
            c=min(mp.mpf('.8'),max(mp.mpf('.05'),mp.exp(-ll/uu)))
            return c**(1-uu)/(1-uu)-mp.exp(ll)*c+mp.mpf('.01')*mp.exp(ll)-mp.mpf('.004')*mp.log(mp.mpf('.5'))
        uu,ll=mp.mpf(u),mp.mpf(l)
        exact=[psi(uu,ll),mp.diff(lambda x:psi(x,ll),uu),mp.diff(lambda y:psi(uu,y),ll),mp.diff(lambda x:psi(x,ll),uu,2),mp.diff(lambda x:mp.diff(lambda y:psi(x,y),ll),uu),mp.diff(lambda y:psi(uu,y),ll,2)]
        box=source(point(u),point(l))
        require('independent conjugate derivatives '+str(i),all(mp.mpf(float(a))<=v<=mp.mpf(float(b)) for (a,b),v in zip(box,exact)))
    # Preserve the whole completed R9 tree, not merely a hand-picked source list.
    inherited=load(REV/'inherited_manifest.json');bad=[]
    for name,h in inherited['files'].items():
        p=ROOT/inherited['archived_replacement'].get(name,name)
        if not p.exists() or sha(p)!=h:bad.append(name)
    require('complete historical preservation',not bad,{'file_count':len(inherited['files']),'violations':bad})
    old=ROOT/'revisions/2026-09-22-r9/results/external';panels=load(old/'summary.json')['rows']
    require('complete six-panel frozen holdout',len(panels)==6)
    for panel in panels:
        d,b=panel['dimension'],panel['budget_seconds'];ds=[]
        for seed in range(720,732):
            r=load(old/f'd{d}_b{b}_s{seed}.json')
            require('paired and pinned holdout '+str((d,b,seed)),r['methods']['nbo']['initial_hash']==r['methods']['soc']['initial_hash'] and r['source_commit']=='46aef70a24f74cf57503018a7e7f21cb46af08e3')
            ds.append(r['paired_difference'])
        wins=sum(x<0 for x in ds);pv=sum(math.comb(12,j) for j in range(wins,13))/2**12
        require('exact sign inference retained '+str((d,b)),abs(panel['bonferroni_six_panels_p']-min(1,6*pv))<1e-14 and ds==panel['raw_differences'])
        require('stronger baseline retained '+str((d,b)),panel['means']['lq']<panel['means']['nbo']<panel['means']['soc'])
    before={p.name:p.read_bytes() for p in (REV/'paper/tables').glob('*.tex')}
    with contextlib.redirect_stdout(io.StringIO()):make_tables.run()
    after={p.name:p.read_bytes() for p in (REV/'paper/tables').glob('*.tex')}
    require('tables generated from current full-precision records',before==after)
    require('canonical R10 entry','canonical revision R10' in (ROOT/'REVISION_INDEX.md').read_text())
    if pdf:
        for stem in ['ECTA_R10','SUPP_R10']:
            log=(ROOT/(stem+'.log')).read_text(errors='replace') if (ROOT/(stem+'.log')).exists() else (REV/'build_logs'/(stem+'.final.log')).read_text(errors='replace')
            text=subprocess.check_output(['pdftotext',str(ROOT/(stem+'.pdf')),'-'],text=True)
            require('PDF exists '+stem,(ROOT/(stem+'.pdf')).stat().st_size>100000 and '??' not in text)
            require('no unresolved references '+stem,not re.search(r'Citation .* undefined|Reference .* undefined|There were undefined references|multiply-defined labels',log))
            require('no overfull or duplicate destinations '+stem,'Overfull ' not in log and 'destination with the same identifier' not in log)
    result={'status':'PASS','check_count':len(CHECKS),'checks':CHECKS,'seconds':time.perf_counter()-start,'python':platform.python_version(),'numpy':np.__version__,'mpmath':mp.__version__,
            'scope':'Record, independent derivative spot-check, preservation, exact-sign, table and build checks; mathematical certification is separately re-executed by run_cell.py.',
            'all_three_central_regrets_below_0_01':True}
    (REV/'validation_report.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2));return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--skip-pdf',action='store_true');a=p.parse_args();run(not a.skip_pdf)
