"""Pure byte partition of preserved proofs into current and archival routes.

No original proof or frozen scientific file is rewritten. This creates a new
recovery receipt rather than reconstructing a lost receipt from its digest.
"""
from pathlib import Path
import datetime, gzip, hashlib, json, re, time
R=Path(__file__).resolve().parents[1]
REPO=R.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,b):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise FileExistsError(path)
    path.write_bytes(b)
start=time.perf_counter();started=utc()
SNAP=R/'provenance122/drafts/runtime_recovery122/proof_partition_before'
for q in ['supp.tex','appendix.tex','new122/introduction122.tex','new122/inference122.tex']:
    b=(R/q).read_bytes();save(SNAP/(q.replace('/','__')+'.gz'),gzip.compress(b,mtime=0))
parts={
 'sections/proofs67.tex':[(0,1904,'active'),(1904,14456,'archive')],
 'sections/proofs95.tex':[(0,9232,'active'),(9232,18312,'archive')],
 'new120/policy_improvement_main.tex':[(0,787,'archive'),(787,2713,'active'),(2713,12078,'archive')],
 'new120/policy_improvement_proofs.tex':[(0,792,'archive'),(792,6330,'active'),(6330,25447,'archive'),(25447,32187,'active'),(32187,39808,'archive')],
 'new121/marginal_proofs.tex':[(0,49266,'active'),(49266,57318,'archive')],
}
records=[]
for source,ranges in parts.items():
    b=(R/source).read_bytes();assert ranges[0][0]==0 and ranges[-1][1]==len(b)
    assert all(a[1]==z[0] for a,z in zip(ranges,ranges[1:]))
    basename=source.replace('/','__').removesuffix('.tex')
    rec={'source':source,'source_bytes':len(b),'source_sha256':sha(b),'views':[]}
    for route in ['active','archive']:
        selected=[(lo,hi) for lo,hi,which in ranges if which==route]
        if route=='active' and source=='new120/policy_improvement_proofs.tex':
            groups=[[selected[0]],[selected[1]]]
        else:groups=[selected]
        for idx,group in enumerate(groups):
            content=b''.join(b[lo:hi] for lo,hi in group)
            suffix=f'_{idx+1}' if len(groups)>1 else ''
            path=f'new122/proof_views/{basename}_{route}{suffix}.tex'
            save(R/path,content)
            rec['views'].append({'path':path,'route':route,'ranges':group,'bytes':len(content),'sha256':sha(content)})
    assert sum(x['bytes'] for x in rec['views'])==len(b)
    records.append(rec)
views={r['source']:{route:[x['path'].removesuffix('.tex') for x in r['views'] if x['route']==route] for route in ['active','archive']} for r in records}
supp=(R/'supp.tex').read_text()
for source,byroute in views.items():
    needle='\\input{'+source.removesuffix('.tex')+'}'
    assert supp.count(needle)==1
    supp=supp.replace(needle,'\n'.join('\\input{'+p+'}' for p in byroute['active']))
move_to_archive=['new110/action-main','new119/active_tail_main','new/proofs99','new109/proofs','new110/budget_proofs','new119/active_tail_proofs','new119/budgeted_tail_proofs119','new119/packing_proofs119','new119/coupled_main','new119/coupled_proofs']
for q in move_to_archive:
    needle='\\input{'+q+'}'
    assert supp.count(needle)==1;supp=supp.replace(needle+'\n','')
needle='\\section{Retained action and continuous-risk comparison statements}\nThe following statements retain their original assumptions and mathematical\ncontent. Their move from the preceding main article to this supplement changes\npresentation, not their economic criterion or execution identity.'
replacement='''\\section{Current proof roadmap}
This supplement contains the complete mathematical chains needed for the
current article: original operator construction, signed and centered risk
qualification, original investment regularity, marginal learning and the
all-state policy service, paid-support policy improvement, its precise
information bound, and the declared simultaneous inference. Proofs specific
to historical experiments and additional retained models appear in the
development companion. All original source files remain unchanged; exact
byte views route shared statements and proofs without rewriting them.
\\input{sections/risk91}'''
assert needle in supp;supp=supp.replace(needle,replacement)
supp=supp.replace('\\input{sections/proofs92}','\\input{sections/proofs91}\n\\input{sections/proofs92}')
(R/'supp.tex').write_text(supp)
app=(R/'appendix.tex').read_text()
for q in ['sections/risk91','sections/proofs91']:
    needle='\\input{'+q+'}\n';assert app.count(needle)==1;app=app.replace(needle,'')
archive='''\\section{Retained mathematical developments and earlier experiments}
\\label{dev:proofpartition122}
The following exact source views retain the proof material specific to
historical statements and experiments. Their common mathematical premises
and the proofs used by the current article are in the technical supplement.
Every byte of each original source belongs to exactly one declared view;
\\texttt{PROOF\\_PARTITION122.json} records the source hashes, byte ranges
and routes. The complete original files also remain in the source package.
Words such as ``current'' inside these retained inputs refer to their original
revision. Moving a proof does not extend its assumptions or execution scope.
'''
archive+='\n'.join('\\input{'+p+'}' for p in move_to_archive)+'\n'
archive+='\n'.join('\\input{'+p+'}' for byroute in views.values() for p in byroute['archive'])+'\n'
needle='\\input{new122/development122}\n';assert app.count(needle)==1
app=app.replace(needle,needle+archive)
app=app.replace("The R121 marginal statements and complete proofs remain in the technical\nsupplement.","The R121 marginal statements and shared current proofs remain in the technical\nsupplement; its separate historical inference proof is retained in this companion.")
app=app.replace("Their policy-improvement\nstatements and full proofs are preserved in the technical supplement.","Their policy-improvement\nstatements and full proofs are preserved across the technical supplement and\nthis companion, with exact source routes recorded in the retention map.")
(R/'appendix.tex').write_text(app)
intro=(R/'new122/introduction122.tex').read_text().replace('All proofs appear in the technical supplement. The development companion','Complete proofs for the current main results appear in the technical supplement.\nThe development companion')
(R/'new122/introduction122.tex').write_text(intro)
inference=(R/'new122/inference122.tex').read_text()
old_count=inference.count('{\\cal X}')
inference=inference.replace('{\\cal X}','\\mathcal{X}')
(R/'new122/inference122.tex').write_text(inference)
freeze=json.loads((R/'SOURCE_FREEZE122.json').read_text())
checked=[];missing=[];mismatches=[]
for p,digest in freeze['scientific_files'].items():
    q=REPO/p
    if not q.is_file():missing.append(p);continue
    actual=sha(q.read_bytes());checked.append(p)
    if actual!=digest:mismatches.append({'path':p,'expected':digest,'actual':actual})
assert not mismatches
for rec in records:assert sha((R/rec['source']).read_bytes())==rec['source_sha256']
receipt={'kind':'Recovered current and archival proof routing by exact byte views','started_utc':started,'ended_utc':utc(),'elapsed_seconds':time.perf_counter()-start,'prior_lost_partition_receipt_recreated':False,'original_sources_unchanged':True,'source_file_count':len(records),'source_bytes':sum(x['source_bytes'] for x in records),'view_count':sum(len(x['views']) for x in records),'views_total_bytes':sum(v['bytes'] for x in records for v in x['views']),'sources':records,'whole_file_moves_to_development':move_to_archive,'whole_file_moves_to_supplement':['sections/risk91','sections/proofs91'],'frozen_source_members_present_checked':len(checked),'frozen_source_members_not_yet_materialized':missing,'frozen_source_mismatches':mismatches,'notation_only_replacements':{'source':'new122/inference122.tex','from':'{\\cal X}','to':'\\mathcal{X}','count':old_count,'reason':'econsocart compatibility; identical mathematical notation, no change to inference rules or proof'},'wrappers':{q:{'sha256':sha((R/q).read_bytes()),'bytes':(R/q).stat().st_size} for q in ['supp.tex','appendix.tex','new122/introduction122.tex','new122/inference122.tex']},'original_economic_queries':0,'source_script_sha256':sha(Path(__file__).read_bytes()),'scope':'Presentation and exact source routing only; no newly validated historical experiment or final PDF claim.'}
save(R/'PROOF_PARTITION122.json',(json.dumps(receipt,indent=2)+'\n').encode())
print(json.dumps({'source_files':receipt['source_file_count'],'views':receipt['view_count'],'source_bytes':receipt['source_bytes'],'frozen_members_present':len(checked),'frozen_members_missing':len(missing),'receipt_sha256':sha((R/'PROOF_PARTITION122.json').read_bytes())}))
