"""Audit the completed R24 publication without modifying scientific records."""
from pathlib import Path
import hashlib,json,os,re,subprocess
ROOT=Path(__file__).resolve().parents[3];REV=ROOT/'revisions/2026-09-23-r24'
BASE='fdc60e04d6aca33ad964da77db69c8ba3621a14b';TARGETS=['ECTA_R24','SUPP_R24','RESPONSE_R24']
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def main():
    expected={'tuning':30,'heldout':28,'multicell':36,'reference':12,'failure':4}
    counts={k:len(list((REV/'results'/k).rglob('record.json'))) for k in expected};assert counts==expected,counts
    lock=json.loads((REV/'results/PRIMARY_EVIDENCE_LOCK.json').read_text())
    for p,h in lock['files'].items():assert sha(REV/p)==h,p
    runtime=json.loads((REV/'results/DEPENDENCY_LOCK.json').read_text())
    lineage=json.loads((REV/'results/SOURCE_LINEAGE_AUDIT.json').read_text())
    assert lineage['exact_documented_metadata_patch_verified'] is True
    for x in runtime['runtime_imported_repository_modules'].values():
        actual=sha(ROOT/x['path'])
        if actual!=x['sha256']:
            assert x['path']=='revisions/2026-09-23-r24/replication/study.py'
            assert x['sha256']==lineage['original_source_sha256']
            assert actual==lineage['metadata_only_repaired_source_sha256']
    blobs=0;bad=[]
    for row in git('ls-tree','-rz',BASE).decode().split('\0'):
        if not row:continue
        meta,name=row.split('\t',1);mode,typ,h=meta.split()
        if typ!='blob':continue
        blobs+=1;p=ROOT/name
        if p.is_symlink():data=os.readlink(p).encode()
        elif p.is_file():data=p.read_bytes()
        else:bad.append((name,'missing'));continue
        now=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if now!=h:bad.append((name,h,now))
    assert not bad,bad[:20]
    response=(REV/'paper/response.tex').read_text()
    want={f'R23-SP-{c}{i}' for c,n in [('F',12),('T',8)] for i in range(1,n+1)}|{f'{p}-{c}{i}' for p,c,n in [('R23F','F',12),('R23T','T',8)] for i in range(1,n+1)}
    found=set(re.findall(r'R23(?:-SP|F|T)-[FT]\d+',response));assert want==found,(want-found,found-want)
    groups=[]
    for title,ids,body in re.findall(r'\\subsection\{([^}]+)\}\s*\\noindent\\textit\{([^}]+)\}\s*(.*?)(?=\\subsection|\\section|\Z)',response,re.S):
        codes=re.findall(r'R23(?:-SP|F|T)-[FT]\d+',ids)
        groups.append({'topic':title,'finding_ids':codes,'response':body.strip(),'disposition':'Response and evidence supplied within stated scope; not a blanket closure claim'})
    write(REV/'FINDING_DISPOSITION.json',{'findings':40,'groups':groups,'not_numerically_established':['original-state full-domain 0.01 certificate','separate full-state actor payoff improvement','successful nonreplicable stochastic execution','rigorous numerical stopped-objective gradient error','broad high-dimensional or universal neural superiority']})
    (REV/'FINDING_DISPOSITION.md').write_text('# R24 finding dispositions\n\nAll 40 finding identifiers are covered. Response delivery is not blanket scientific closure.\n\n'+'\n\n'.join('## '+g['topic']+'\n\n'+', '.join(g['finding_ids'])+'\n\n'+g['response'] for g in groups)+'\n')
    audit={'review_base_commit':BASE,'reviewed_blobs_checked':blobs,'all_reviewed_files_preserved_byte_identical':True,'scientific_counts':counts,'primary_result_files_checked':len(lock['files']),'primary_results_byte_identical':True,'finding_ids_covered':40}
    write(REV/'results/PRESERVATION_AUDIT.json',audit)
    todo=[ROOT/(t+'.tex') for t in TARGETS];seen=set()
    while todo:
        p=todo.pop().resolve()
        if p in seen:continue
        assert p.is_file(),p;seen.add(p)
        for name in re.findall(r'\\(?:input|include)\s*\{([^}]+)\}',p.read_text()):
            q=ROOT/name
            if not q.suffix:q=q.with_suffix('.tex')
            assert q.is_file(),q;todo.append(q)
    files={str(p.relative_to(ROOT)):sha(p) for p in seen}
    for p in list(ROOT.glob('*.cls'))+list(ROOT.glob('*.sty')):files[str(p.relative_to(ROOT))]=sha(p)
    for p in REV.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
        if p.name in ('PUBLICATION_MANIFEST.json','source_bundle.zip','publication_audit.log'):continue
        files[str(p.relative_to(ROOT))]=sha(p)
    pages={}
    for t in TARGETS:
        p=ROOT/(t+'.pdf');assert p.is_file();files[p.name]=sha(p)
        log=(ROOT/(t+'.log')).read_text(errors='replace')
        assert not re.search(r'(Undefined control sequence|There were undefined references|There were multiply-defined labels|Overfull \\[hv]box)',log),t
        m=re.search(r'Output written on .*?\((\d+) pages?',log,re.S);assert m,t;pages[t]=int(m.group(1))
    write(REV/'PUBLICATION_MANIFEST.json',{'schema_version':1,'revision':'R24','reviewed_manuscript_commit':'c09835c92042cb881d0bbdd3cab99b98d0a9d225','publication_parent_commit':git('rev-parse','HEAD').decode().strip(),'protocol_commit':'b54afa8c9107d70094a1d84be4a3c0279916530c','science_runs':[35832563885,35833755321],'pdf_pages':pages,'preservation':audit,'transitive_tex_inputs':len(seen),'files_sha256':dict(sorted(files.items())),'self_hash_exclusions':['PUBLICATION_MANIFEST.json','source_bundle.zip','publication_audit.log','Python bytecode'],'scope':'Current manuscript and response delimit each scientific result; full-domain and nonreplicable targets remain explicit.'})
    print(json.dumps({'preservation':audit,'pdf_pages':pages,'transitive_tex_inputs':len(seen),'locked_files':len(files),'all_checks_passed':True},indent=2))
if __name__=='__main__':main()
