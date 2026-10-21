"""Read-only Git/ref/report census; writes only a new scratch audit directory.

No Git objects are fetched, no ref/index is changed, and no scientific module
is imported. A full file-tree ledger is metadata, not a claim to have rerun or
semantically read every historical payload.
"""
from pathlib import Path
import datetime as dt
import gzip
import hashlib
import json
import os
import subprocess
import time

ROOT=Path('/workspace/scratch/913249553838')
REPO=ROOT/'NBO'
AUDIT=ROOT/'audit121/lineage'
R120=REPO/'revisions/2026-10-19-r120'
V='f06f220aea525088e82228e8e9be4947fb81b1ca'
ENV=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_OPTIONAL_LOCKS='0')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def git(*args):
    return subprocess.run(['git','-C',str(REPO),*args],env=ENV,check=True,capture_output=True).stdout
def identity(path,root):
    raw=path.read_bytes()
    return dict(path=path.relative_to(root).as_posix(),bytes=len(raw),sha256=sha(raw),git_blob_sha1=blob(raw))
def save(path,data):
    with path.open('x',encoding='utf-8') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
def tree_entries(raw):
    rows=[]
    for item in raw.split(b'\0'):
        if item:
            meta,path=item.split(b'\t',1);mode,kind,oid=meta.decode().split()
            rows.append(dict(path=path.decode(),mode=mode,kind=kind,git_oid=oid))
    return rows

def main():
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out=AUDIT/('census_'+stamp);out.mkdir(exist_ok=False);(out/'trees').mkdir()
    start=time.time();save(out/'START121.json',dict(started_utc=stamp,source=identity(Path(__file__),AUDIT),scope=__doc__))
    rows=[];pages=[]
    for page in range(1,6):
        p=AUDIT/'api'/f'branches_page_{page}.json';e=json.loads(p.read_text())
        assert not e['response'].get('isError')
        body=e['response']['structuredContent']['content'];items=json.loads(body);assert isinstance(items,list)
        pages.append(dict(page=page,rows=len(items),observed_utc=e['observed_utc'],envelope=identity(p,AUDIT),body_sha256=sha(body.encode())))
        rows.extend(items)
    assert [x['rows'] for x in pages]==[100,100,100,61,0]
    branches={x['name']:x['commit']['sha'] for x in rows};assert len(branches)==len(rows)==361
    old=json.loads((R120/'provenance/PREAUTHOR_BRANCHES120.json').read_text())
    before={x['name']:x['commit']['sha'] for x in old['branches']};assert len(before)==361
    changes=[dict(branch=k,before=before[k],current=branches.get(k)) for k in sorted(before) if branches.get(k)!=before[k]]
    added=[dict(branch=k,sha=branches[k]) for k in sorted(branches) if k not in before]
    current_name='revision/econometrica-nbo-r120-certified-policy-improvement-2026-10-19'
    assert not added and changes==[dict(branch=current_name,before='a6f3b8278d4502b174b05b19fafd5aacabaa60a3',current=V)]
    groups={}
    for name,oid in branches.items():groups.setdefault(oid,[]).append(name)
    ledgers=[];all_oids=set()
    for index,(oid,names) in enumerate(sorted(groups.items())):
        raw=git('ls-tree','-r','-z',oid);entries=tree_entries(raw)
        packed=gzip.compress(raw,compresslevel=6,mtime=0);path=out/'trees'/(oid+'.ls-tree.z.gz')
        with path.open('xb') as f:f.write(packed)
        all_oids.update(x['git_oid'] for x in entries if x['kind']=='blob')
        ledgers.append(dict(commit=oid,tree=git('rev-parse',oid+'^{tree}').decode().strip(),branches=sorted(names),entries=len(entries),raw_bytes=len(raw),raw_sha256=sha(raw),compressed=identity(path,out)))
        if (index+1)%50==0:print(json.dumps(dict(completed_unique_commits=index+1,total_unique_commits=len(groups))),flush=True)
    save(out/'ALL_BRANCH_FILE_LEDGER121.json',dict(schema='NBO_R121_ALL_BRANCH_TREE_LEDGER_V1',pages=pages,branches=rows,unique_commits=len(groups),unique_blob_ids=len(all_oids),ledgers=ledgers,scope='Exact full recursive Git tree listings for every unique observed branch head. File contents are not downloaded or executed.'))
    registry=R120/'provenance/reports120/REPORT_SOURCE_INDEX120.json';info=json.loads(registry.read_text());assert len(info['files'])==35
    reports=[]
    for row in info['files']:
        p=R120/row['path'];raw=p.read_bytes();assert len(raw)==row['bytes'] and sha(raw)==row['sha256'] and blob(raw)==row['git_blob_sha1']
        exact=tree_entries(git('ls-tree','-r','-z',row['source_review_commit'],'--',row['source_path_in_review_commit']))
        assert len(exact)==1 and exact[0]['git_oid']==blob(raw)
        assert branches[row['source_review_branch']]==row['source_review_commit']
        reports.append(dict(**row,whole_body_utf8_decoded=True,original_review_git_blob_verified=True,headings=[dict(line=n,heading=line) for n,line in enumerate(raw.decode().splitlines(),1) if line.startswith('#')]))
    save(out/'ORIGINAL_REPORT_CENSUS121.json',dict(schema='NBO_R121_ORIGINAL_REPORT_BODY_CENSUS_V1',registry=identity(registry,REPO),reports=reports,total_bytes=sum(x['bytes'] for x in reports),distinct_reports=35,review_refs=36,scope='Complete byte read, UTF-8 decode, original Git-blob and source-ref verification. Semantic reading and new author treatments are separately recorded; this is not a claim that 35 scientific reports are resolved.'))
    baseline_files=['PUBLICATION120.json','DELIVERY120.json','SOURCE_IDENTITY120.json','SOURCE_PDF_MANIFEST120.json','ECTA.tex','new120/response120_body.tex','REVISION_BOUNDARY120.md','CONTENT_RETENTION_MAP120.md','provenance/HISTORICAL_ROUTE_BINDINGS120.json','provenance/R97_REQUIREMENTS120.json','provenance/reports120/inherited_maps/INDEX120.json']
    vtree={x['path']:x['git_oid'] for x in tree_entries(git('ls-tree','-r','-z',V,'--',R120.relative_to(REPO).as_posix()))}
    baselines=[]
    for relative in baseline_files:
        p=R120/relative;record=identity(p,REPO);assert vtree[record['path']]==record['git_blob_sha1'];baselines.append(record)
    receipt=dict(schema='NBO_R121_LINEAGE_CENSUS_RECEIPT_V1',status='passed',exit_code=0,started_unix=start,ended_utc=dt.datetime.now(dt.timezone.utc).isoformat(),seconds=time.time()-start,remote_branches=361,all_original360_unchanged=True,only_change_since_R120_preauthor_snapshot=changes,new_branches=added,review_refs_unchanged=True,report_files=35,report_bytes=sum(x['bytes'] for x in reports),unique_commits=len(groups),full_tree_entries=sum(x['entries'] for x in ledgers),unique_blob_ids=len(all_oids),baseline_commit=V,baseline_files=baselines,prior_branch_inventory=identity(R120/'provenance/PREAUTHOR_BRANCHES120.json',REPO),tools_scope='Git metadata and actual retained document bytes only; no ref/index mutation, lazy blob fetch, scientific import, experiment, or build.')
    save(out/'LINEAGE_CENSUS_RECEIPT121.json',receipt)
    print(json.dumps(dict(output=str(out),status='passed',unique_commits=len(groups),tree_entries=receipt['full_tree_entries'],report_files=35,report_bytes=receipt['report_bytes'],seconds=receipt['seconds']),indent=2),flush=True)

if __name__=='__main__':main()
