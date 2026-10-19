#!/usr/bin/env python3
"""Record the actually observed source F in nonfrozen author metadata only.

Preserves each prior author file in an exclusive dated backup. This script
does not import scientific code, evaluate the model, or change Git or workflows.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
REV=HERE.parents[2]
F='369d02724cf12ae0e54390b4e7b5f894f703892e'
TREE='16c38ff041a7fa3c8972109e361494d4e5855c16'
AUDIT='provenance/resumption120/20261019T074800Z/LINEAGE_SOURCE_PUBLICATION_VERIFIED120.json'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def replace_exact(text,old,new):
    assert text.count(old)==1,(old[:100],text.count(old))
    return text.replace(old,new)

def main():
    manifest=json.loads((REV/'SOURCE_FREEZE120.json').read_text())
    paths=['new120/response120_body.tex','SOURCE_IDENTITY120.json',
           'provenance/R97_REQUIREMENTS120.json','CONTENT_RETENTION_MAP120.md','REVISION_BOUNDARY120.md']
    assert not set(paths).intersection(manifest['scientific_files'])
    audit=json.loads((REV/AUDIT).read_text())
    assert audit['status']=='passed' and audit['source_F']['commit']==F
    backup=HERE/'author_before_publication_update'
    assert not backup.exists()
    backup.mkdir()
    before=[]
    for name in paths:
        p=REV/name;b=p.read_bytes();q=backup/name;q.parent.mkdir(parents=True,exist_ok=True)
        with q.open('xb') as stream:stream.write(b)
        before.append({'path':name,'bytes':len(b),'sha256':sha(b)})
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    p=REV/'new120/response120_body.tex';body=p.read_text()
    body=replace_exact(body,'% R120 author response draft. No new numerical or publication success is asserted.',
                       '% R120 author response draft. Source F is published; numerical and final-publication outcomes remain pending.')
    old=next(x for x in body.splitlines() if x.startswith('The fresh complete remote observation on 19 October'))
    new=(r'The initial complete remote observation at 02:07 UTC on 19 October 2026 found 360 heads: all 359 historical heads unchanged and the R119 publication branch added. '
         r'The independent refresh at 07:48 UTC found all 360 of those heads unchanged and exactly one addition, the new R120 scientific-source branch, for 361 heads. '
         r'The 36 review refs still contain 35 distinct persisted documents, including the R50 threshold screen; the R16 ref contributes no new report. '
         r'The controlling advisory remains report commit \nolinkurl{9723c6cd2cc8b3e071422f3e522d4a843946db63}, report blob \nolinkurl{33ba8b144e2f7816b19b036404341402d23a582f}, assessing R97 manuscript \nolinkurl{f802fe64d91d9f5c1c8f86123b0fbe114e622279}. '
         r'Its complete bytes and all 35 retained report identities were reverified after the pause. It is an owner-commissioned AI-assisted advisory, not an Econometric Society decision and not a review of R119 or R120.')
    body=replace_exact(body,old,new)
    body=replace_exact(body,'The two actual staged protocols specify eight inherited representation',
                       'The two remotely frozen protocols specify eight inherited representation')
    old='''No R120 acquisition, sample, favorable policy contrast, independent
execution, PDF build or remote CI outcome has yet been supplied to this
response. The remaining fields are
\\texttt{R120\\_PENDING\\_PROTOCOL\\_SOURCE},
\\texttt{R120\\_PENDING\\_COMPLETE\\_EXPERIMENT},
\\texttt{R120\\_PENDING\\_INDEPENDENT\\_VALIDATION} and
\\texttt{R120\\_PENDING\\_PUBLICATION}. A real source freeze and every
completed or failed attempt will retain their own identities. Existing
R119 results and CI successes are not R120 observations.'''
    new=r'''\paragraph{Actually published scientific source.}
Source barrier $F$ is \nolinkurl{369d02724cf12ae0e54390b4e7b5f894f703892e},
with tree \nolinkurl{16c38ff041a7fa3c8972109e361494d4e5855c16}
and the unchanged final R119 publication as its parent. The Git commit is
dated 07:43:02 UTC on 19 October 2026; the actual remote publication was
recorded at 07:45:41 UTC and independently observed at 07:48 UTC.
The manifest's earlier 02:49 preparation time is not a remote publication
time. The independent read-back matches the exact manifest and all 157
scientific inputs, totaling 1,206,453 bytes, to their SHA-256 values and
the actual untruncated remote Git tree. The immutable manifest is
\nolinkurl{SOURCE_FREEZE120.json}; the actual publication receipt is
\nolinkurl{provenance/SOURCE_PUBLICATION120.json}, and the independent
source/report check is
\nolinkurl{provenance/resumption120/20261019T074800Z/LINEAGE_SOURCE_PUBLICATION_VERIFIED120.json}.
This completed source barrier fixes the scientific study. Actor barrier
$M$, sample barrier $D$, completed scientific observations and the final
source/PDF package require their own subsequent evidence.

At this source-publication update no R120 acquisition, sample, favorable
policy contrast, independent execution, PDF build or remote CI outcome
has been supplied to this response. The remaining fields are
\texttt{R120\_PENDING\_COMPLETE\_EXPERIMENT},
\texttt{R120\_PENDING\_INDEPENDENT\_VALIDATION} and
\texttt{R120\_PENDING\_PUBLICATION}. Every completed or failed attempt
retains its own identity. Existing R119 results and CI successes are not
R120 observations.'''
    body=replace_exact(body,old,new)
    body=replace_exact(body,'Neither study is completed by a new deterministic R120\ncatalogue or by borrowing another episode\'s observations.',
                       'Neither study is completed by the new R120 sample\nor by borrowing another episode\'s observations.')
    assert 'R120_PENDING_PROTOCOL_SOURCE' not in body.replace('\\_','_')
    p.write_text(body)

    p=REV/'SOURCE_IDENTITY120.json';identity=json.loads(p.read_text())
    identity['remote_inventory_after_source_publication']={
        'observed_utc':'2026-10-19T07:48:00Z','heads':361,'all_prior360_unchanged':True,
        'original359_unchanged':True,'only_added_branch':identity['revision_branch'],
        'only_added_head':F,'review_refs':36,'distinct_report_documents':35,
        'new_controlling_report_found':False,'new_completed_author_source_found':False,
        'verification_receipt':AUDIT,'verification_receipt_sha256':sha((REV/AUDIT).read_bytes())}
    current=identity['r120_scientific_execution']
    assert current['source_freeze_commit'] is None and current['actor_commit'] is None and current['state_commit'] is None
    current.update({'status':'Scientific source F remotely published and independently bound; no acquisition, sample or scientific execution outcome supplied to this author response.',
                    'source_freeze_commit':F,'source_freeze_tree':TREE,
                    'source_manifest_sha256':sha((REV/'SOURCE_FREEZE120.json').read_bytes()),
                    'source_publication_receipt':'provenance/SOURCE_PUBLICATION120.json',
                    'source_publication_receipt_sha256':sha((REV/'provenance/SOURCE_PUBLICATION120.json').read_bytes()),
                    'source_publication_verification_receipt':AUDIT,
                    'source_publication_update_utc':now})
    p.write_text(json.dumps(identity,indent=2,ensure_ascii=False)+'\n')

    p=REV/'provenance/R97_REQUIREMENTS120.json';requirements=json.loads(p.read_text())
    requirements['source_freeze_commit']=F
    requirements['source_publication_receipt']='provenance/SOURCE_PUBLICATION120.json'
    requirements['resumption_lineage_receipt']=AUDIT
    requirements['current_source_route_scope']='Written mathematical/executable sources are frozen at actual remote source F. Current author prose and receipt integration remain outside the scientific freeze and require refreshed source bindings. Inherited R119 routes and original request bytes are unchanged; no empirical or final-publication outcome is asserted.'
    requirements['source_publication_update_utc']=now
    p.write_text(json.dumps(requirements,indent=2,ensure_ascii=False)+'\n')

    note=('## Actual scientific-source publication after the pause\n\n'
          'Source barrier **F=`'+F+'`**, tree `'+TREE+'`, is actually published on the isolated R120 branch. '
          'The commit is dated 2026-10-19 07:43:02 UTC; [the actual publication receipt](provenance/SOURCE_PUBLICATION120.json) was recorded at 07:45:41 UTC. '
          'The independent 07:48 UTC observation verifies all prior 360 heads unchanged and only this new branch added, for 361 heads. '
          'All 36 review refs are unchanged and all 35 distinct reports reverify, so R97 remains controlling and R119 remains the latest complete manuscript. '
          'The [source/report read-back receipt]('+AUDIT+') binds the exact manifest and all 157 scientific inputs, 1,206,453 bytes, to their local hashes and the actual remote Git tree. '
          'The 02:49 manifest-preparation time is retained separately from actual publication. This source barrier supplies no actor/sample commitment, completed economic study or final source/PDF/CI result. '
          'All frozen scientific inputs remain unchanged; this update records source publication only.\n\n')
    for name in ['CONTENT_RETENTION_MAP120.md','REVISION_BOUNDARY120.md']:
        p=REV/name;text=p.read_text();lines=text.splitlines(keepends=True)
        text=''.join(lines[:2])+note+''.join(lines[2:])
        if name=='REVISION_BOUNDARY120.md':
            text=replace_exact(text,'count its own deterministic catalogue as completion of R98',
                               'count its own new sample as completion of R98')
            text=replace_exact(text,'R120 has no new completed scientific, independent-validation or publication result at this source-preparation stage. Its protocol, remote freeze, execution logs, evidence validation, source/PDF bindings and final CI status must be filled from their own actual records.',
                               'The R120 source barrier F is now actually published and bound as recorded above. Completed scientific observations, independent-validation outcomes, later actor/sample barriers, source/PDF bindings and final CI status still require their own actual records.')
        else:
            text=replace_exact(text,'At the present source-preparation stage, R120 scientific execution, independent economic validation and publication receipts are pending.',
                               'The source barrier F is actually published and verified as recorded above. Completed R120 scientific observations, independent economic validation and the final source/PDF publication remain pending in this author update.')
        p.write_text(text)

    after=[]
    for name in paths:
        data=(REV/name).read_bytes();after.append({'path':name,'bytes':len(data),'sha256':sha(data)})
    for name,digest in manifest['scientific_files'].items():
        assert sha((REV/name).read_bytes())==digest
    receipt={'schema':'NBO_R120_AUTHOR_SOURCE_PUBLICATION_UPDATE_V1','recorded_utc':now,
             'source_commit':F,'scope':'Nonfrozen author prose/metadata only; original request text, scientific inputs, R119 files and historical route map are unchanged.',
             'before':before,'after':after,'frozen_scientific_inputs_unchanged':157,
             'backup_directory':str(backup.relative_to(REV)),
             'source_publication_verification_receipt':AUDIT,
             'pending_markers':sorted(set(re.findall(r'R120_PENDING_[A-Z_]+',body.replace('\\_','_')))),
             'scientific_execution':False,'git_or_workflow_mutation':False,
             'wording_correction':'R120 uses a new finite-law random sample; the earlier unqualified phrase deterministic R120 catalogue was corrected without changing any protocol.'}
    output=HERE/'AUTHOR_SOURCE_PUBLICATION_UPDATE120.json'
    with output.open('x') as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':'updated','receipt':str(output),'sha256':sha(output.read_bytes()),'after':after},indent=2))

if __name__=='__main__':
    main()
