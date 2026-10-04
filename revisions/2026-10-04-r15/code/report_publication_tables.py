"""Outward decimal presentation of the unchanged, frozen R15 method report.

This layer never computes a new confidence interval or changes a decision. It
prints each saved binary64 lower endpoint toward minus infinity and each upper
endpoint toward plus infinity. Means remain descriptive, rounded to nearest.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN, localcontext
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
NAMES={'nbo':'NBO','raw_costate':'Raw','direct_policy':'Direct policy','neural_hjb':'Neural HJB'}
TABLES={'table_method_summary.tex':'tab:r15methodmeans',
        'table_method_comparisons.tex':'tab:r15methodcontrasts',
        'table_method_seed_endpoints.tex':'tab:r15methodstreams'}


def require(ok,message):
    if not ok:raise ValueError(message)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())


def number(value,side=None,digits=6):
    value=float(value);require(math.isfinite(value),'nonfinite displayed value')
    require(side in (None,'lower','upper'),'unknown rounding direction')
    require(isinstance(digits,int) and digits>=0,'invalid decimal precision')
    exact=Decimal.from_float(value)
    with localcontext() as context:
        context.prec=max(80,abs(exact.adjusted())+digits+10)
        direction={None:ROUND_HALF_EVEN,'lower':ROUND_FLOOR,'upper':ROUND_CEILING}[side]
        displayed=exact.quantize(Decimal(10)**-digits,rounding=direction)
    if displayed.is_zero():displayed=displayed.copy_abs()
    if side=='lower':require(displayed<=exact,'displayed lower endpoint is not outward')
    if side=='upper':require(displayed>=exact,'displayed upper endpoint is not outward')
    return f'{displayed:.{digits}f}'


def endpoint_name(name):
    if name in NAMES:return NAMES[name]
    left,right=name.split('__minus__');return NAMES[left]+'--'+NAMES[right]


def table(caption,label,headers,rows,note,long=False):
    columns='l'+'r'*(len(headers)-1);header=' & '.join(headers)+r' \\'
    if long:
        lines=[r'\begingroup\small',r'\begin{longtable}{'+columns+'}',r'\caption{'+caption+r'}\label{'+label+r'}\\',r'\toprule',header,r'\midrule',r'\endfirsthead',r'\toprule',header,r'\midrule',r'\endhead']
    else:
        lines=[r'\begin{table}[!htbp]',r'\centering\small',r'\caption{'+caption+'}',r'\label{'+label+'}',r'\begin{tabular}{'+columns+'}',r'\toprule',header,r'\midrule']
    lines+=[' & '.join(map(str,row))+r' \\' for row in rows]
    lines += [r'\bottomrule',r'\end{longtable}' if long else r'\end{tabular}',r'\par\medskip\noindent\begin{minipage}{\linewidth}\footnotesize\emph{Notes:} '+note,r'\end{minipage}',r'\endgroup' if long else r'\end{table}']
    return '\n'.join(lines)+'\n'


def validate(p,r,source,protocol_path):
    require(p['status']=='frozen_before_confirmatory_execution','unfrozen method protocol')
    require(r['status']=='complete' and r['trial_count']==128,'incomplete method report')
    require(r['source_commit']==source['numerical_source_commit'],'report source differs from source manifest')
    require(r['protocol_sha256']==source['protocol_sha256']==sha(protocol_path),'report/protocol/source-manifest mismatch')
    require(r['primitives_sha256']==p['design']['primitives_sha256']==source['primitives_sha256'],'primitive identity mismatch')
    design=p['design'];dims=design['dimensions'];seeds=design['seeds'];methods=design['methods']
    require(len(seeds)==len(set(seeds))==16 and len(dims)==2 and len(methods)==4,'incomplete finite method design')
    names=methods+[a+'__minus__'+b for a,b in p['confirmation']['direct_contrasts']]
    expected_methods={(d,m) for d in dims for m in names}
    expected_seeds={(d,s,m) for d in dims for s in seeds for m in names}
    method_rows=r['method_endpoints'];seed_rows=r['seed_endpoints']
    require(len(method_rows)==14 and {(x['dimension'],x['endpoint']) for x in method_rows}==expected_methods,'missing or duplicate method endpoint')
    require(len(seed_rows)==224 and {(x['dimension'],x['stream_seed'],x['endpoint']) for x in seed_rows}==expected_seeds,'missing or duplicate stream endpoint')
    require(r['confidence']['event_count']==p['inference']['method_confirmation_events']==238,'wrong simultaneous event family')
    for row in method_rows+seed_rows:
        require(math.isfinite(row['lower']) and math.isfinite(row['upper']) and row['lower']<=row['upper'],'invalid saved confidence interval')
    for row in method_rows:
        if '__minus__' not in row['endpoint']:continue
        lower,upper,margin=row['lower'],row['upper'],p['economic_decision']['equivalence_margin_payoff']
        expected={'practical_equivalence':lower>-margin and upper<margin,
                  'economically_material_superiority':lower>margin,
                  'economically_material_inferiority':upper<-margin}
        require(all(row['decision'][key]==value for key,value in expected.items()),'decision differs from original unrounded endpoint rule')
    return names


def render(protocol,report,source_manifest,out):
    protocol,report,source_manifest,out=map(Path,(protocol,report,source_manifest,out))
    originals={str(x):sha(x) for x in [protocol,report,source_manifest]}
    require(not out.resolve().is_relative_to(source_manifest.parent.resolve()),'presentation must not write inside the immutable numerical evidence tree')
    p,r,source=read(protocol),read(report),read(source_manifest);names=validate(p,r,source,protocol)
    dims=p['design']['dimensions'];seeds=p['design']['seeds'];methods=p['design']['methods']
    means={(x['dimension'],x['endpoint']):x for x in r['method_endpoints']}
    conditional={(x['dimension'],x['stream_seed'],x['endpoint']):x for x in r['seed_endpoints']}
    summary_rows=[];comparison_rows=[];seed_rows=[]
    target=p['stopping']['primary_certified_gain_target']
    for d in dims:
        for name in names:
            z=means[d,name]
            values=[d,endpoint_name(name),number(z['raw_mean']),number(z['lower'],'lower'),number(z['upper'],'upper')]
            if name in methods:
                count=sum(conditional[d,s,name]['lower']>=target for s in seeds)
                attainment=[x for x in r['attainment'] if x['dimension']==d and x['method']==name and x['target']==target]
                require(len(attainment)==1 and attainment[0]['definitely_attaining']==count and attainment[0]['seed_count']==len(seeds),'attainment fraction differs from exact original endpoints')
                summary_rows.append(values+[f'{count}/{len(seeds)}'])
            else:
                decision=z['decision']
                status='Equivalent' if decision['practical_equivalence'] else 'Superior' if decision['economically_material_superiority'] else 'Inferior' if decision['economically_material_inferiority'] else 'Unresolved'
                comparison_rows.append(values+[status])
        for seed in seeds:
            for name in names:
                z=conditional[d,seed,name]
                seed_rows.append([d,seed,endpoint_name(name),number(z['mean']),number(z['lower'],'lower'),number(z['upper'],'upper')])
    rounding='Every lower endpoint is rounded down and every upper endpoint up to six decimal places; displayed intervals therefore contain the original protected intervals. Means are descriptive and rounded to nearest.'
    texts={
        'table_method_summary.tex':table('Payoff of the Finite-Distribution Computational Methods',TABLES['table_method_summary.tex'],
            ['$d$','Method','Mean gain','Lower','Upper','At least target'],summary_rows,
            'Means average all sixteen declared execution streams. Endpoints enclose continuous-time payoff gains on the analytical schedule. The last column counts streams whose unrounded simultaneous final lower endpoint attains 0.0005; it is a lower bound on attainment under the declared finite distribution. No stream is excluded. '+rounding),
        'table_method_comparisons.tex':table('Direct Method Comparisons at the Declared Economic Margin',TABLES['table_method_comparisons.tex'],
            ['$d$','Comparison','Mean','Lower','Upper','Decision'],comparison_rows,
            r'Pathwise differences use common profiles and innovations within each stream. The equivalence margin is $10^{-4}$ payoff units. Superior and inferior refer to economic differences exceeding that margin. Decisions use the original unrounded endpoints. An unresolved comparison is not evidence of equivalence. The schedule transfer cancels between two simulated candidates; comparison with an exact analytical fallback retains the other candidate\textquotesingle s full schedule-relative transfer. '+rounding),
        'table_method_seed_endpoints.tex':table('Every Declared Stream Payoff and Direct Contrast',TABLES['table_method_seed_endpoints.tex'],
            ['$d$','Stream','Endpoint','Mean','Lower','Upper'],seed_rows,
            'Every declared stream and endpoint is retained. These conditional-policy intervals and the method averages belong to the single registered confirmation family; their simulation banks are independent of stopping. '+rounding,long=True)}
    out.mkdir(parents=True,exist_ok=True)
    for name,text in texts.items():(out/name).write_text(text)
    require(all(sha(Path(name))==expected for name,expected in originals.items()),'presentation changed an original numerical input')
    def path_name(path):return path.resolve().relative_to(ROOT).as_posix() if path.resolve().is_relative_to(ROOT) else str(path.resolve())
    manifest={'schema':'nbo-r15-outward-method-presentation-v1','complete':True,
              'numerical_source_commit':r['source_commit'],'protocol_sha256':sha(protocol),'source_manifest_sha256':sha(source_manifest),
              'original_report_sha256':sha(report),'presentation_source_sha256':sha(__file__),
              'inputs':{path_name(Path(name)):expected for name,expected in originals.items()},
              'tables':{name:{'sha256':sha(out/name),'label':TABLES[name],'rows':len(rows)} for name,rows in zip(TABLES,[summary_rows,comparison_rows,seed_rows])},
              'represented_events':238,'confidence_alpha_added':0.,'numerical_decisions_changed':False,
              'rounding':{'lower':'Decimal.from_float, ROUND_FLOOR','upper':'Decimal.from_float, ROUND_CEILING','mean':'Decimal.from_float, ROUND_HALF_EVEN','decimal_places':6},
              'scope':'Presentation only. Frozen REPORT and original generated tables remain byte-for-byte unchanged; all statistical decisions use their original endpoints.'}
    (out/'PUBLICATION_TABLES_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True,allow_nan=False)+'\n')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['protocol','report','source-manifest','out']:parser.add_argument('--'+name,required=True)
    result=render(**vars(parser.parse_args()));print(json.dumps({'complete':result['complete'],'events':result['represented_events'],'tables':list(result['tables'])}))
