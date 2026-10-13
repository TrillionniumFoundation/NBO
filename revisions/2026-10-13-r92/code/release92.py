"""A compiled candidate is not a release: require matching actual-PDF inspection."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];A=R/'audit/reproduction92'
DOCS=('ECTA','supp','appendix','response')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise AssertionError(msg)
def read(p):return json.loads(p.read_text())

def verify():
    report=read(A/'VERIFICATION92.json');source=read(A/'SOURCE92.json');visual=read(A/'VISUAL92.json')
    need(report['status']=='compiled_candidate','Current complete numerical/publication verification must pass')
    need(bool(report['checks']) and all(v['status']=='passed' for v in report['checks'].values()),'A verification gate failed')
    for name in ('clean-typesetting','clean-new-science92','independent92','independent84','independent-original-law85','earlier-tree-preservation','bibliography','current-documents'):
        need(report['checks'].get(name,{}).get('status')=='passed','Missing mandatory gate '+name)
    need(source['source_commit']==report['source_commit']==visual['source_commit'],'Mismatched source identities')
    need(visual['status']=='passed','Actual-PDF visual review has not passed')
    # Verify the frozen ordinary sources, not just the four PDF filenames.
    for name,digest in source['files'].items():
        p=R/name;need(p.is_file() and sha(p)==digest,'Changed frozen source '+name)
    tests={}
    for name,value in report['checks'].items():
        if not name.startswith('tests'):continue
        rec=value['result'];need(rec['status']=='passed' and rec['tests']>0,'Missing unskipped suite '+name)
        p=R/rec['log'];need(sha(p)==rec['log_sha256'],'Changed test evidence '+name)
        tests[name]=rec['tests']
    documents={}
    clean=read(A/'CLEAN92.json');science=read(A/'CLEAN_SCIENCE92.json')
    need(clean['status']=='passed' and science['status']=='passed' and science['cases_identical']==84,'Incomplete clean reconstructions')
    for name in DOCS:
        p=R/'build'/(name+'.pdf');rec=report['documents'][name];vis=visual['documents'][name]
        need(p.is_file() and sha(p)==rec['pdf_sha256']==vis['pdf_sha256'],'Stale PDF or visual record '+name)
        need(rec['status']=='passed' and not any(rec['diagnostics'].values()),'Unqualified document '+name)
        need(vis['pages']==rec['pages'],'Wrong inspected page count '+name)
        need(sorted(vis['inspected_pages'])==list(range(1,rec['pages']+1)),'Incomplete page-layout inspection '+name)
        need(bool(vis.get('method')) and bool(vis.get('findings')),'Missing visual method/findings '+name)
        need(clean['comparison'][name]['pdf_identical'] and clean['comparison'][name]['text_identical'],'Clean document mismatch '+name)
        if name!='response':
            bbl=R/'build'/(name+'.bbl');need(bbl.is_file() and sha(bbl)==rec['bibliography_sha256'],'Missing current bibliography '+name)
        documents[name]={'pages':rec['pages'],'pdf_sha256':rec['pdf_sha256'],'visual_coverage':'all page layouts plus declared targeted full-size checks'}
    independent=read(A/'INDEPENDENT92.json')
    need(independent['status']=='passed' and independent['case_count']==84 and independent['interval_configurations']==252,'Incomplete independent catalogue')
    out={'status':'passed','revision':'R92','source_commit':report['source_commit'],
         'baseline_commit':report['baseline_commit'],'review_commit':report['review_commit'],
         'verification_sha256':sha(A/'VERIFICATION92.json'),'visual_sha256':sha(A/'VISUAL92.json'),
         'documents':documents,'test_suites':tests,'total_tests':sum(tests.values()),
         'scope':'Source-bound numerical, document, clean reconstruction and actual-PDF layout release; not a journal acceptance or independent mathematical referee verdict.',
         'new_fit_attempts':0,'new_independent_economic_rows':0,
         'remaining_empirical_scope':['Independent inherited largest-vector kernel and matched tournament','Measured energy','Application-specific monetary calibration']}
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--record',action='store_true');args=p.parse_args()
    try:
        out=verify()
        if args.record:(A/'RELEASE92.json').write_text(json.dumps(out,indent=2)+'\n')
        print(json.dumps(out,indent=2),flush=True)
    except Exception as e:
        print('R92 release refused: '+str(e),file=sys.stderr);sys.exit(1)
