"""Pin noncircular source/result/build identities and all delivered file bytes."""
import argparse,hashlib,json,os,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-22-r10'
REVIEW='251ad29668788b2a911c4ca6f9c0a226886518d6';BLOB='42cee0954515e5578dc579a4ca0428bb4e399b2e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(source,result,build=None):
    common={'canonical_source_commit':source,'execution_result_commit':result,'review_report_commit':REVIEW,
            'review_report_blob':BLOB,'reviewed_early_R9_source_commit':'46aef70a24f74cf57503018a7e7f21cb46af08e3',
            'inherited_complete_R9_commit':'23f40e730fcea04efe3d84690d4f0fff5ae466e8',
            'inherited_frozen_holdout_result_commit':'58007e6edf8a6d80e930e025138f38d978a82aba',
            'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
            'branch':'revision/econometrica-r10-referee-resolution-2026-09-22',
            'PDF_sha256':{n:sha(ROOT/n) for n in ('ECTA_R10.pdf','SUPP_R10.pdf')},
            'ci_recheck_status':json.loads((REV/'ci_results/ci_recheck.json').read_text())['status'],
            'validation_check_count':json.loads((REV/'validation_report.json').read_text())['check_count'],
            'pipeline_fault_cases':len(json.loads((REV/'pipeline_tests.json').read_text())['cases'])}
    assert common['ci_recheck_status']=='PASS'
    if build:
        common['manuscript_build_commit']=build
        common['receipt_convention']='This receipt is a subsequent commit and deliberately does not claim its own hash.'
        path=REV/'publication_receipt.json'
    else:
        files=[ROOT/n for n in ('ECTA_R10.tex','SUPP_R10.tex','R10_REVIEW.md','REVISION_INDEX.md')]
        files += [p for p in REV.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name not in ('source_manifest.json','publication_receipt.json')]
        common['files']={str(p.relative_to(ROOT)):sha(p) for p in sorted(files)}
        common['build_identity_convention']='Build commit is the next commit containing these files; recorded afterward in publication_receipt.json.'
        path=REV/'source_manifest.json'
    path.write_text(json.dumps(common,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--result',required=True);p.add_argument('--build');a=p.parse_args();run(a.source,a.result,a.build)
