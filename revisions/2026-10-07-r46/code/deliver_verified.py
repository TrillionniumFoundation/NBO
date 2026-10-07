"""Transport the exact validated R46 artifact; do not rebuild or retime science."""
import base64,hashlib,io,json,os,subprocess,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];ROOT=R.parent.parent
RUN=37655122929;ARTIFACT=11498666091
DIGEST='d82b0966276b6a31bc69390abbd8cbdee25ecfcbc64fb23338fb8e8f89670810'
def api(path):return subprocess.check_output(['gh','api','repos/TrillionniumFoundation/NBO/'+path])
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    jobs=json.loads(api(f'actions/runs/{RUN}/jobs'))['jobs']
    steps={s['name']:s.get('conclusion') for j in jobs for s in j['steps']}
    gates=['Verify inherited and additional source identities','Materialize the exact latest review without changing its text','Reconstruct all records, run 49 tests and compile all documents','Commit candidate without deleting historical files','Clean committed-source rebuild with no generated R46 tables or PDFs']
    assert all(steps.get(g)=='success' for g in gates),steps
    raw=api(f'actions/artifacts/{ARTIFACT}/zip');assert sha(raw)==DIGEST
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist();assert len(names)==len(set(names))
        for n in names:
            p=Path(n);assert not p.is_absolute() and '..' not in p.parts,n
            assert p.suffix.lower() not in {'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'},n
        z.extractall(R)
    manifest=json.loads((R/'audit/FILES_SHA256.json').read_text())
    for n,h in manifest.items():assert sha((R/n).read_bytes())==h,n
    sources=json.loads((R/'audit/PUBLICATION_SOURCE_SHA256.json').read_text())
    for n,h in sources.items():assert sha((R/n).read_bytes())==h,n
    a=json.loads((R/'audit/RELEASE_AUDIT.json').read_text());c=json.loads((R/'audit/CLEAN_REBUILD.json').read_text())
    assert a['publication_source_commit']=='668c214691f211180b05926f421b501a72107120'
    assert a['total_tests']==49 and a['release_entry_and_review_checks']
    assert all(t['success'] for t in a['tests'].values())
    assert a['results']['services']==36 and a['results']['rungs']==216
    assert c['successful'] and c['tests']==49 and not c['study_reexecuted']
    for d in a['compilation']:
        assert not any(d[k] for k in ('undefined_references','duplicate_labels','overfull_boxes','missing_characters'))
        assert sha((R/'build'/f"{d['document']}.pdf").read_bytes())==d['pdf_sha256']
    review=ROOT/'reviews/2026-10-07-econometrica-numerical-methods-r43';review.mkdir(parents=True,exist_ok=True)
    blobs={'referee_report.md':'bb6b050e1ac3feea091f8800e874e9f858281108','review_manifest.json':'4b1643babb93354e5b47a5361e7df9703b5040f3','verification_results.json':'085101f703d4843afe79aa7dc31ac1513d5a1133','verify_r43_review.py':'71a199e370f4dc1713fd7de6f11134ae8adb8663'}
    for n,h in blobs.items():
        b=base64.b64decode(json.loads(api('git/blobs/'+h))['content'])
        assert hashlib.sha1(('blob '+str(len(b))+'\0').encode()+b).hexdigest()==h,n
        p=review/n
        if p.exists():assert p.read_bytes()==b,n
        else:p.write_bytes(b)
    for n in ('ECTA.tex','supp.tex'):(ROOT/n).write_text(chr(92)+'input{revisions/2026-10-07-r46/'+n+'}\n')
    (ROOT/'README.md').write_text('# Neural Bellman Operators — R46\n\n## Integrated revision, 8 October 2026\n\n[Authoritative manuscript, response and reproduction instructions](revisions/2026-10-07-r46/README.md).\n\n[Main article](revisions/2026-10-07-r46/build/ECTA.pdf) | [Technical supplement](revisions/2026-10-07-r46/build/supp.pdf) | [Referee response](revisions/2026-10-07-r46/build/response.pdf).\n\nThe original NBO paper is extended by witness-preserving neural construction and feasible-witness transport under state-dependent constraints. All prior manuscripts, applications, reviews and adverse evidence remain preserved.\n\n[Release audit](revisions/2026-10-07-r46/audit/RELEASE_AUDIT.json) | [Clean rebuild](revisions/2026-10-07-r46/audit/CLEAN_REBUILD.json) | [Final delivery](revisions/2026-10-07-r46/audit/FINAL_DELIVERY.json).\n\nCanonical review branch: revision/econometrica-nbo-r46-review-ready-2026-10-08.\n')
    delivery={'validated_run':RUN,'validated_source_commit':a['publication_source_commit'],'artifact_id':ARTIFACT,'artifact_sha256':DIGEST,'manifest_files_verified':len(manifest),'source_anchors_verified':len(sources),'tests':49,'clean_rebuild':c,'publication_only':True,'delivery_run':os.environ.get('GITHUB_RUN_ID'),'delivery_source_commit':os.environ.get('GITHUB_SHA'),'reason':'Source, scientific, PDF and clean-rebuild gates passed. The prior git push was rejected by a GitHub Internal Server Error at 2026-10-07T16:55:58Z. This recovery publishes identical scientific bytes and does not relabel the failed run.','pdfs':a['compilation']}
    (R/'audit/FINAL_DELIVERY.json').write_text(json.dumps(delivery,indent=2)+'\n')
    extra={**manifest,'audit/FILES_SHA256.json':sha((R/'audit/FILES_SHA256.json').read_bytes()),'audit/FINAL_DELIVERY.json':sha((R/'audit/FINAL_DELIVERY.json').read_bytes()),'code/deliver_verified.py':sha(Path(__file__).read_bytes())}
    (R/'audit/DELIVERY_FILES_SHA256.json').write_text(json.dumps(extra,indent=2,sort_keys=True)+'\n')
    print(json.dumps(delivery,indent=2))
if __name__=='__main__':main()
