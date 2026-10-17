"""Materialize and verify the R95 source/evidence overlay. Never refit frozen actors."""
from __future__ import annotations
import argparse,base64,csv,hashlib,io,json,os,pathlib,platform,shutil,subprocess,sys,tarfile,time,urllib.request
P=pathlib.Path
REPO=P(__file__).resolve().parents[3]
R=REPO/'revisions/2026-10-13-r95'
BASE=REPO/'revisions/2026-10-13-r94'
A=R/'audit/remote95'
ARCHIVE_SHA='23475e8118e69db3a185ef60351ad18d255731b53862b8b133148c7e9f0a1a92'
REVIEW='bd2945b4b4e76b6a997dbcf7548f5fe24d3e92e6'
BASE_SHA='84148cd179fe58c280a91ad281c7a81656d49788'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def dump(p,obj):
    p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')
def head():return subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
def source_manifest():
    paths=[R/n for n in ('ECTA.tex','supp.tex','appendix.tex','response.md','response.tex','preamble.tex','references92-canonical.bib','requirements95.txt')]
    paths+=list((R/'sections').glob('*.tex'))+list((R/'code').glob('*.py'))+list((R/'tables').glob('*.tex'))
    return {str(p.relative_to(R)):sha(p) for p in sorted(set(paths))}
def materialize():
    if (A/'TRANSPORT95.json').exists():raise RuntimeError('Materialization already completed; do not overwrite current sources')
    text=''.join((R/'bootstrap'/f'part-{i:02d}.b64').read_text().strip() for i in range(8))
    raw=base64.b64decode(text,validate=True)
    if hashlib.sha256(raw).hexdigest()!=ARCHIVE_SHA:raise RuntimeError('Transport checksum mismatch; no source extracted')
    shutil.copytree(BASE,R,dirs_exist_ok=True)
    preserved=R/'preserved/R92-wrappers';preserved.mkdir(parents=True,exist_ok=True)
    for n in ('ECTA.tex','supp.tex','appendix.tex','response.md','response.tex','preamble.tex','README.md','references92-canonical.bib'):
        if (R/n).exists():shutil.copy2(R/n,preserved/n)
    if (R/'build').exists():shutil.move(str(R/'build'),str(R/'preserved/R94-inherited-build'))
    files={}
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as archive:
        for member in archive:
            target=R/member.name
            if not member.isfile() or not target.resolve().is_relative_to(R.resolve()):raise RuntimeError('Unsafe archive member')
            data=archive.extractfile(member).read();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            files[member.name]=sha(target)
    for n in ('econsocart.cls','econsocart.cfg','ecta-fullname.bst'):
        if not (R/n).exists():shutil.copy2(REPO/n,R/n)
    url=f'https://raw.githubusercontent.com/TrillionniumFoundation/NBO/{REVIEW}/reviews/2026-10-13-econometrica-numerical-methods-r92/referee_report.md'
    data=urllib.request.urlopen(url,timeout=60).read()
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if blob!='f73302dda485323aed578071b5f7e94d845c83ab':raise RuntimeError('Pinned referee report identity mismatch')
    (R/'inputs').mkdir(exist_ok=True);(R/'inputs/referee-r92.md').write_bytes(data)
    dump(A/'TRANSPORT95.json',{'archive_sha256':ARCHIVE_SHA,'archive_bytes':len(raw),'files':files,'base_commit':BASE_SHA,'review_commit':REVIEW,'review_blob':blob,'materialization_parent':head(),'success':True})
    dump(R/'SOURCE95.json',{'base_commit':BASE_SHA,'review_commit':REVIEW,'materialization_parent':head(),'files':source_manifest(),'scope':'Current integrated source; historical freezes remain separate'})
    dump(R/'RELEASE95.json',{'status':'source-materialized-validation-pending','base_commit':BASE_SHA,'review_commit':REVIEW,'source_manifest_sha256':sha(R/'SOURCE95.json'),'remote_checks_passed':False})
    print(json.dumps({'materialized':len(files),'archive_verified':True}),flush=True)
def replay(tag):
    sys.path.insert(0,str(R/'code'))
    from study94 import evaluate,evaluate_arm,rows,ARMS,LEVELS,source_files
    from investment94 import terminal_certificate
    from representations94 import Fit
    from interval94 import I
    out=R/'results94';cal=json.loads((out/'CALIBRATION94.json').read_text());old=json.loads((out/'evaluation-local95/RESULTS94.json').read_text())
    if cal['source_files']!=source_files():raise RuntimeError('Original numerical source hash mismatch')
    dest=out/f'evaluation-{tag}'
    record={'source_commit':head(),'tag':tag,'original_report_sha256':sha(out/'evaluation-local95/RESULTS94.json'),'calibration_sha256':sha(out/'CALIBRATION94.json'),'new_fits':0,'additional_independent_observations':0,'original_csv_hashes':{},'success':False}
    t=time.perf_counter()
    def admit(path,target,expected):
        actual=sha(path);match=actual==expected
        record['original_csv_hashes'][str(target.relative_to(R))]={'expected':expected,'actual':actual,'match':match}
        dump(A/'REPLAY95.json',record)
        if not match:raise RuntimeError('Original-record byte identity failed: '+str(target))
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    result=evaluate(out,tag)
    for idx,alpha in enumerate(LEVELS):
        folder=out/f'alpha-{idx}';temp=A/'reconstruction'/f'alpha-{idx}';temp.mkdir(parents=True,exist_ok=True)
        x=rows(1,idx,1024);labels=terminal_certificate(I(x),alpha)
        path=temp/'training.csv'
        with path.open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['x0','x1','label_lower','label_upper']);w.writerows(zip(x[:,0],x[:,1],labels['lower'],labels['upper']))
        admit(path,folder/'training.csv',cal['levels'][str(idx)]['training_sha256'])
        for arm in ARMS:
            model=None if arm=='online-risk-dp' else Fit.from_dict(json.loads((folder/f'{arm}.json').read_text()))
            path=temp/f'calibration-{arm}.csv';evaluate_arm(rows(2,idx,128),alpha,model,path)
            admit(path,folder/path.name,cal['levels'][str(idx)]['calibration'][arm]['raw_sha256'])
            path=dest/f'alpha-{idx}-{arm}.csv'
            admit(path,out/'evaluation-local95'/path.name,old['levels'][str(idx)]['arms'][arm]['data']['raw_sha256'])
    record.update(success=True,seconds=time.perf_counter()-t,cloud_report_sha256=sha(dest/'RESULTS94.json'),all_original_optimum_certificates_pass=result['all_first_date_certificates_pass'])
    dump(A/'REPLAY95.json',record);print(json.dumps(record,indent=2),flush=True)
def release(tag):
    def read(p):return json.loads(p.read_text()) if p.exists() else None
    tests=read(A/'tests/TESTS95.json');build=read(A/'build/BUILD95.json');rep=read(A/'REPLAY95.json');ind=read(R/'audit/reproduction94'/f'INDEPENDENT94-{tag}.json')
    gates={'tests':bool(tests) and all(x['passed'] and not x['skipped'] for x in tests.values()),'current_pdfs':bool(build) and build['status']=='compiled' and all(not x['unresolved_references'] and not x['overfull_hbox'] for x in build.get('documents',{}).values()),'original_csv_identity':bool(rep) and rep['success'],'independent_kernel':bool(ind) and ind['success']}
    record={'status':'verified' if all(gates.values()) else 'validation-incomplete','gates':gates,'validation_source_commit':head(),'base_commit':BASE_SHA,'review_commit':REVIEW,'archive_sha256':ARCHIVE_SHA,'tests_total':sum(x['tests'] or 0 for x in (tests or {}).values()),'tests':tests,'documents':build.get('documents') if build else None,'replay':rep,'independent_kernel_success':ind.get('success') if ind else False,'github_run_id':os.environ.get('GITHUB_RUN_ID'),'machine':platform.platform(),'source_files':source_manifest(),'scope':'Original frozen local measurements are not replaced by cloud timings. Replication adds no independent economic observations. Rank-matched superiority, a second full largest-vector implementation and energy evidence are not claimed.'}
    dump(R/'RELEASE95.json',record);print(json.dumps(record,indent=2),flush=True)
    return 0 if all(gates.values()) else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['materialize','replay','release']);p.add_argument('--tag',default='cloud95');args=p.parse_args()
    if args.mode=='materialize':materialize()
    elif args.mode=='replay':replay(args.tag)
    else:sys.exit(release(args.tag))
