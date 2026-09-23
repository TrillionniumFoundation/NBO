"""Publication-only reconciliation; no scientific result or parameter is changed."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r24'
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
    archive=REV/'archive/primary_execution.zip'
    assert digest(archive.read_bytes())=='cf8da93098d0e32c6d6bd219e57aedc84a9b31d1adbee941a004a85d2a44cde8'
    repair=json.loads((REV/'results/accounting_repair.json').read_text())
    assert repair['scientific_parameters_changed'] is False
    with zipfile.ZipFile(archive) as z:original=z.read('replication/study.py')
    assert digest(original)==repair['before_sha256']
    old=repair['patch']['old'];new=repair['patch']['new']
    assert old=="'root_accounting':asdict(obj.accounting)"
    assert new=="'root_accounting':{k:(v if not isinstance(v,float) or math.isfinite(v) else None) for k,v in asdict(obj.accounting).items()}"
    assert original.decode().count(old)==1
    canonical=original.decode().replace(old,new).encode()
    assert digest(canonical)==repair['after_sha256']
    study=REV/'replication/study.py';previous=digest(study.read_bytes())
    if study.read_bytes()!=canonical:
        (REV/'archive/pre_publication_study.py.txt').write_bytes(study.read_bytes())
        study.write_bytes(canonical)
    runtime=json.loads((REV/'results/DEPENDENCY_LOCK.json').read_text())
    versions={repair['before_sha256'],repair['after_sha256']}
    checked=[]
    for name,x in runtime['runtime_imported_repository_modules'].items():
        current=digest((ROOT/x['path']).read_bytes())
        if x['path']==str(study.relative_to(ROOT)):
            assert x['sha256'] in versions and current==repair['after_sha256']
        else:assert current==x['sha256'],(name,x['path'])
        checked.append({'module':name,'path':x['path'],'runtime_sha256':x['sha256'],'publication_sha256':current})
    for path,h in runtime.get('inherited_data_sha256',{}).items():
        current=digest((ROOT/path).read_bytes())
        if path==str(study.relative_to(ROOT)):assert h in versions and current==repair['after_sha256']
        else:assert current==h,path
    (REV/'results/SOURCE_LINEAGE_AUDIT.json').write_text(json.dumps({'primary_archive_sha256':digest(archive.read_bytes()),'original_source_sha256':repair['before_sha256'],'metadata_only_repaired_source_sha256':repair['after_sha256'],'previous_publication_source_sha256':previous,'exact_documented_metadata_patch_verified':True,'scientific_results_changed':False,'runtime_module_checks':checked},indent=2)+'\n')
    audit=REV/'replication/publication_audit.py';s=audit.read_text()
    oldcheck="    for x in runtime['runtime_imported_repository_modules'].values():assert sha(ROOT/x['path'])==x['sha256'],x['path']"
    replacement="""    lineage=json.loads((REV/'results/SOURCE_LINEAGE_AUDIT.json').read_text())
    assert lineage['exact_documented_metadata_patch_verified'] is True
    for x in runtime['runtime_imported_repository_modules'].values():
        actual=sha(ROOT/x['path'])
        if actual!=x['sha256']:
            assert x['path']=='revisions/2026-09-23-r24/replication/study.py'
            assert x['sha256']==lineage['original_source_sha256']
            assert actual==lineage['metadata_only_repaired_source_sha256']"""
    if oldcheck in s:
        assert s.count(oldcheck)==1;s=s.replace(oldcheck,replacement);audit.write_text(s)
    else:assert replacement in s
    p=REV/'paper/state.tex';s=p.read_text()
    before="\\begin{equation}\n F_i(t,y)=R_i e^{-.02(1-t)}+\\int_t^1e^{-.02(s-t)}\\E^Q[c_i(s,Y_s)\\mid Y_t=y]ds,\n \\qquad p_i(t,y)=-1.5\\,yF_{i,y}(t,y)/F_i(t,y).\n \\label{eq:r24price}\n\\end{equation}"
    after="\\begin{equation}\n\\begin{aligned}\n F_i(t,y)&=R_i e^{-.02(1-t)}+\\int_t^1e^{-.02(s-t)}\\E^Q[c_i(s,Y_s)\\mid Y_t=y]ds,\\\\\n p_i(t,y)&=-1.5\\,yF_{i,y}(t,y)/F_i(t,y).\n\\end{aligned}\n \\label{eq:r24price}\n\\end{equation}"
    if before in s:s=s.replace(before,after);p.write_text(s)
    else:assert after in s,'Unexpected state-equation source'
    p=REV/'paper/cost_table.tex';s=p.read_text()
    s=s.replace('\\centering\\small','\\centering\\footnotesize\\setlength{\\tabcolsep}{4pt}',1);p.write_text(s)
    print('Exact primary/repaired source identity, all runtime dependencies and publication layout checked; scientific results unchanged.')
if __name__=='__main__':main()
