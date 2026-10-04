"""Independent R15 publication gate; never retrain or alter numerical evidence.

The source ledger binds generating commits, the payload manifest excludes its
own bytes and the final audit, and the final audit hashes both predecessor
records. Publication-source identity is supplied externally, avoiding a commit
self-reference. Git blob content is streamed and compared byte for byte.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile

R15=Path('revisions/2026-10-04-r15')
BASE='f5021cefa71492babfcbfa580e0c984f59a9de26'
REVIEW='7aff61a41a3d28e5eaff73c9fe21e9856110f422'
ROOT_ARCHIVE={x:R15/'archive'/('r14-'+x) for x in ['ECTA.tex','supp.tex','README.md']}
FINAL_NAMES={'SOURCE_LEDGER.json','EVIDENCE_MANIFEST.json','FINAL_AUDIT.json'}
DERIVED_TOP={'EDITORIAL_MAP.json','MATHEMATICAL_PRESERVATION.json','EDITORIAL_PREVIEW_CHECK.json',
             'OBSERVATION_TABLE_MANIFEST.json','SOURCE_LEDGER.json','EVIDENCE_MANIFEST.json','FINAL_AUDIT.json','response.tex'}


def require(condition,message):
    if not condition:raise ValueError(message)


def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def read(path):return json.loads(Path(path).read_text())
def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')


def replay_environment(cache=None):
    environment=os.environ.copy()
    environment.update(PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',
                       OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMBA_NUM_THREADS='1')
    if cache is not None:environment['NUMBA_CACHE_DIR']=str(cache)
    return environment


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def safe_path(root,name):
    p=PurePosixPath(str(name))
    require(not p.is_absolute() and '..' not in p.parts,'unsafe manifest path: '+str(name))
    answer=Path(root)/Path(*p.parts)
    require(answer.resolve().is_relative_to(Path(root).resolve()),'manifest path escapes root')
    return answer


class GitStore:
    def __init__(self,repo):
        self.repo=Path(repo);self.trees={}
        self.process=subprocess.Popen(['git','cat-file','--batch'],cwd=repo,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    def git(self,*args):return subprocess.check_output(['git',*args],cwd=self.repo,stderr=subprocess.PIPE)

    def tree(self,commit):
        require(bool(re.fullmatch('[0-9a-f]{40}',commit or '')),'full immutable commit SHA required')
        require(self.git('rev-parse','--verify',commit+'^{commit}').decode().strip()==commit,'missing source commit '+commit)
        if commit not in self.trees:
            out={}
            for entry in self.git('ls-tree','-rz','--full-tree',commit).split(b'\0'):
                if not entry:continue
                metadata,name=entry.split(b'\t',1);mode,kind,oid=metadata.split()
                if kind==b'blob':out[name.decode()]=dict(mode=mode.decode(),git_blob=oid.decode())
            self.trees[commit]=out
        return self.trees[commit]

    def _start(self,oid):
        self.process.stdin.write((oid+'\n').encode());self.process.stdin.flush()
        fields=self.process.stdout.readline().split()
        require(len(fields)==3 and fields[0].decode()==oid and fields[1]==b'blob','invalid git blob '+oid)
        return int(fields[2])

    def blob(self,oid):
        size=self._start(oid);data=self.process.stdout.read(size)
        require(len(data)==size and self.process.stdout.read(1)==b'\n','truncated git blob')
        return data

    def compare(self,oid,path):
        path=Path(path);require(path.is_file() and not path.is_symlink(),'missing/nonregular retained file '+str(path))
        size=self._start(oid);digest=hashlib.sha256();remaining=size;equal=path.stat().st_size==size
        with path.open('rb') as local:
            while remaining:
                chunk=self.process.stdout.read(min(remaining,1024*1024))
                require(bool(chunk),'truncated git blob stream')
                digest.update(chunk);equal=(local.read(len(chunk))==chunk) and equal;remaining-=len(chunk)
            equal=(local.read(1)==b'') and equal
        require(self.process.stdout.read(1)==b'\n','invalid blob terminator')
        require(equal,'retained bytes differ from original Git blob: '+str(path))
        return dict(git_blob=oid,sha256=digest.hexdigest(),bytes=size)

    def close(self):
        self.process.stdin.close();self.process.wait(timeout=10)
        self.process.stdout.close();self.process.stderr.close()


def check_history(repo,git,commit=BASE,expected_count=8652):
    tree=git.tree(commit)
    require(len(tree)==expected_count,f'historical tree count differs: {len(tree)} != {expected_count}')
    records={}
    for name,facts in sorted(tree.items()):
        destination=ROOT_ARCHIVE.get(name,Path(name))
        require(facts['mode'] in ['100644','100755'],'unexpected historical Git object mode')
        record=git.compare(facts['git_blob'],safe_path(repo,destination))
        records[name]=dict(destination=str(destination),mode=facts['mode'],**record)
    return dict(commit=commit,blobs=len(records),root_archive_exceptions={k:str(v) for k,v in ROOT_ARCHIVE.items()},files=records)


def check_review(repo,git):
    directory=repo/R15/'review_source';source=read(directory/'SOURCE.json')
    require(source['review_commit']==REVIEW and source['reviewed_revision_commit']==BASE,'review source identity mismatch')
    tree=git.tree(REVIEW);records={}
    require(len(source['files'])==4,'review copy must retain all four original files')
    for local,facts in source['files'].items():
        origin=facts['source_path'];require(origin in tree,'review source path missing')
        require(tree[origin]['git_blob']==facts['git_blob'],'review Git blob identity mismatch')
        record=git.compare(facts['git_blob'],safe_path(directory,local))
        require(record['sha256']==facts['sha256'],'review SHA256 mismatch')
        records[local]=dict(source_path=origin,**record)
    return dict(review_commit=REVIEW,reviewed_commit=BASE,files=records)


def check_source_manifest(repo,git,source,manifest):
    require(manifest['numerical_source_commit']==source,'numerical generating source mismatch')
    tree=git.tree(source);records={}
    for name,facts in manifest['files'].items():
        require(name in tree and tree[name]['git_blob']==facts['git_blob'],'source manifest blob mismatch: '+name)
        record=git.compare(facts['git_blob'],safe_path(repo,name))
        require(record['sha256']==facts['sha256'] and record['bytes']==facts['bytes'],'source manifest bytes mismatch: '+name)
        records[name]=record
    if 'fingerprint_input' in manifest:
        expected=manifest.get('method_fingerprint',manifest.get('assessment_fingerprint'))
        require(hashlib.sha256(canonical(manifest['fingerprint_input'])).hexdigest()==expected,'method/assessment fingerprint mismatch')
    for item in manifest.get('method_fingerprints',{}).values():
        require(hashlib.sha256(canonical(item['input'])).hexdigest()==item['sha256'],'method fingerprint mismatch')
    return records


def check_inventory(repo,manifest_path,root=None):
    manifest=read(manifest_path);files=manifest['files'];checked={}
    for name,facts in files.items():
        expected=facts if isinstance(facts,str) else facts['sha256']
        p=safe_path(repo,name)
        require(p.resolve()!=Path(manifest_path).resolve(),'self-referencing digest manifest')
        require(p.is_file() and sha(p)==expected,'evidence digest mismatch: '+name)
        if root is not None:require(p.resolve().is_relative_to(Path(root).resolve()),'evidence path outside declared root')
        checked[name]=expected
    return checked


def check_work(folder,source,protocol_hash=None,environment_contract=None):
    path=folder/'WORK.json';work=read(path)
    require(work.get('complete') is True and work.get('returncode',0)==0,'incomplete numerical WORK receipt: '+str(path))
    require(work['numerical_source_commit']==source,'WORK generating source mismatch')
    if protocol_hash:require(work['protocol_sha256']==protocol_hash,'WORK protocol mismatch')
    if 'environment' in work:
        require(hashlib.sha256(canonical(work['environment'])).hexdigest()==work['environment_fingerprint'],'WORK environment fingerprint mismatch')
    if environment_contract:
        actual=work['environment'];contract=environment_contract
        packages=contract.get('packages',{key:contract[key] for key in ['numpy','scipy','numba','mpmath','torch'] if key in contract})
        require(all(actual['packages'].get(key)==version for key,version in packages.items()),'WORK packages differ from frozen environment contract')
        require(actual['python'].startswith(contract['python']+'.') and actual['platform'].startswith(contract['platform']),'WORK interpreter/platform differs from frozen environment contract')
        require(actual['threads']==contract['numeric_threads'],'WORK numeric thread contract differs')
        require(work['end_to_end_seconds']>0 and work.get('peak_rss_kib',work.get('peak_process_rss_kib',0))>0,'missing inclusive work clock or peak memory')
    inventory=work['files']
    for name,expected in inventory.items():
        p=safe_path(folder,name)
        require(p.is_file() and sha(p)==expected,'original worker file mismatch: '+str(p))
    actual={str(x.relative_to(folder)) for x in folder.rglob('*') if x.is_file() and x.name!='WORK.json'}
    require(actual==set(inventory),'unlisted or missing original worker files: '+str(folder))
    return dict(path=str(path),files=len(inventory),work_sha256=sha(path),method_id=work.get('method_id'),method_fingerprint=work.get('method_fingerprint'),environment_fingerprint=work.get('environment_fingerprint'))


def check_report_replay(repo,script,protocol,results,published):
    """Reconstruct every numerical report from original arrays in a fresh process."""
    with tempfile.TemporaryDirectory(prefix='nbo-r15-report-replay-') as tmp:
        out=Path(tmp)/'report';environment=replay_environment(Path(tmp)/'numba-cache')
        command=[sys.executable,str(safe_path(repo,script)),'--protocol',str(safe_path(repo,protocol)),
                 '--results',str(results),'--out',str(out)]
        process=subprocess.run(command,cwd=repo,env=environment,capture_output=True,text=True)
        require(process.returncode==0,'independent numerical report replay failed: '+process.stderr[-3000:])
        regenerated={str(p.relative_to(out)):p for p in out.rglob('*') if p.is_file()}
        original={str(p.relative_to(published)):p for p in Path(published).rglob('*') if p.is_file()}
        require(set(regenerated)==set(original),'replayed numerical report inventory differs')
        for name in regenerated:
            data=regenerated[name].read_bytes()
            if name.endswith('.tex'):
                # The frozen main reporter embeds its --out directory in TeX
                # input links. Normalize only this mechanical directory prefix;
                # numerical JSON, values, statements and labels remain exact.
                display=Path(published).relative_to(repo).as_posix() if Path(published).is_relative_to(repo) else str(published)
                data=data.replace(('\\input{'+out.as_posix()+'/').encode(),('\\input{'+display+'/').encode())
            require(data==original[name].read_bytes(),'numerical report differs from original-array replay: '+name)
        return dict(files=len(regenerated),sha256={name:sha(path) for name,path in original.items()},
                    scope='Fresh process, frozen report source and original raw arrays; only temporary output-directory prefixes in TeX input links are normalized. No numerical/statement changes, training, selection, resampling or overwritten published output.')


def check_role(repo,git,name,cfg):
    source=cfg['source_commit'];evidence=cfg['evidence_commit'];root=safe_path(repo,cfg['evidence_root'])
    sm_path=safe_path(repo,cfg.get('source_manifest',str(Path(cfg['evidence_root'])/'SOURCE_MANIFEST.json')))
    em_path=safe_path(repo,cfg.get('evidence_manifest',str(Path(cfg['evidence_root'])/'EVIDENCE_MANIFEST.json')))
    audit_path=safe_path(repo,cfg.get('final_audit',str(Path(cfg['evidence_root'])/'FINAL_AUDIT.json')))
    sm=read(sm_path);files=check_source_manifest(repo,git,source,sm)
    inventory=check_inventory(repo,em_path,root)
    evidence_tree=git.tree(evidence);prefix=Path(cfg['evidence_root']).as_posix()+'/'
    retained={k:v for k,v in evidence_tree.items() if k.startswith(prefix)}
    require(bool(retained),'evidence commit has no declared evidence tree')
    local={str(x.relative_to(repo)) for x in root.rglob('*') if x.is_file()}
    require(local==set(retained),'current evidence tree differs from the immutable evidence commit: '+name)
    for path,facts in retained.items():git.compare(facts['git_blob'],safe_path(repo,path))
    require(set(inventory)|{str(em_path.relative_to(repo))}==local,'evidence manifest is not exhaustive: '+name)
    audit=read(audit_path);require(audit.get('complete') is True,'incomplete numerical family '+name)
    require(audit['numerical_source_commit']==source,'family audit source mismatch')
    workers=[];replay=None
    if name=='observation':
        expected={x['cell_id'] for x in sm['matrix']['include']}
        require(len(expected)==4,'observation matrix must contain four registered cells')
        folders={p.parent.name:p.parent for p in root.glob('*/WORK.json')}
        require(set(folders)==expected,'observation cell omission or duplication')
        for folder in folders.values():workers.append(check_work(folder,source,sm['protocol_sha256'],sm['environment_contract']))
    elif name=='main':
        p=read(repo/R15/'PROTOCOL.json');seeds=p['design']['seeds'];methods=p['design']['methods'];dims=p['design']['dimensions']
        require(len(seeds)==len(set(seeds))==16,'main training distribution is incomplete')
        expected={(d,s,m) for d in dims for s in seeds for m in methods};found=set()
        for path in (root/'trials').glob('*/*/RESULT.json'):
            r=read(path);key=(r['dimension'],r['stream_seed'],r['method_id'])
            require(key not in found and key in expected,'unexpected/duplicate main trial');found.add(key)
            require(r['complete'] and r['confirmation_independent_of_selection'],'incomplete/selected main confirmation')
            require(r['numerical_source_commit']==source and r['protocol_sha256']==sm['protocol_sha256'],'main result source/protocol mismatch')
            require(r['method_fingerprint']==sm['method_fingerprints'][r['method_id']]['sha256'],'main algorithm fingerprint mismatch')
            c=r['final_confirmation']
            require(sha(safe_path(path.parent,c['raw_path']))==c['raw_sha256'],'main final path-array digest mismatch')
            for field in ['method_id','dimension','stream_seed','numerical_source_commit','protocol_sha256','primitives_sha256','method_fingerprint']:
                require(c.get(field)==r.get(field),'confirmation identity differs from RESULT: '+field)
            work=read(path.parent/'WORK.json')
            for field in ['method_id','numerical_source_commit','protocol_sha256','method_fingerprint','dimension','stream_seed']:
                require(work.get(field)==r.get(field),'WORK identity differs from RESULT: '+field)
            workers.append(check_work(path.parent,source,sm['protocol_sha256'],sm['environment_contract']))
        require(found==expected and len(found)==128,'missing main method/dimension/stream execution')
        scalar=read(root/'scalar/WORK.json')
        require(scalar['method_id']=='scalar_howard' and scalar['method_fingerprint']==sm['method_fingerprints']['scalar_howard']['sha256'],'scalar algorithm fingerprint mismatch')
        workers.append(check_work(root/'scalar',source,sm['scalar_protocol_sha256'],sm['environment_contract']))
        report=read(root/'report/REPORT.json')
        require(report['status']=='complete' and report['trial_count']==128 and report['confidence']['event_count']==238,'incomplete method report')
        replay=check_report_replay(repo,R15/'code/report_experiment.py',R15/'PROTOCOL.json',root/'trials',root/'report')
    elif name=='mechanism':
        p=read(repo/R15/'MECHANISM_PROTOCOL.json');expected={(d,s) for d in p['dimensions'] for s in p['declared_seeds']}
        main_root=repo/R15/'results/experiment';primary=read(main_root/'SOURCE_MANIFEST.json')
        candidate=cfg['candidate_source_commit'];candidate_evidence=cfg['candidate_evidence_commit']
        require(candidate==primary['numerical_source_commit']==sm['candidate_source_commit'],'mechanism candidate source mismatch')
        require(audit['candidate_source_commit']==candidate and audit['primary_evidence_commit']==candidate_evidence,'mechanism candidate audit identity mismatch')
        require(sha(root/'PRIMARY_SOURCE_MANIFEST.json')==sm['primary_source_manifest_sha256']==sha(main_root/'SOURCE_MANIFEST.json'),'mechanism primary source manifest mismatch')
        require(sm['candidate_method_fingerprint']==primary['method_fingerprints']['nbo']['sha256'],'mechanism candidate algorithm fingerprint mismatch')
        primary_protocol=str(R15/'MECHANISM_PROTOCOL.json')
        require(git.tree(candidate)[primary_protocol]['git_blob']==git.tree(source)[primary_protocol]['git_blob']==sm['preregistered_design_git_blob'],'mechanism preregistered design changed after primary source freeze')
        subtree=git.git('rev-parse',candidate_evidence+':'+str(R15/'results/experiment')).decode().strip()
        require(audit['primary_experiment_git_tree']==subtree,'mechanism primary evidence subtree identity mismatch')
        found=set()
        for path in root.rglob('BRIDGE.json'):
            r=read(path);key=(r['dimension'],r['stream_seed'])
            require(key in expected and key not in found,'unexpected/duplicate mechanism stream');found.add(key)
            require(r['complete'] and r['noise_independent_of_selection_and_primary_confirmation'],'incomplete/nonindependent mechanism bridge')
            proof=read(path.parent/'INPUT_MANIFEST.json');work=read(path.parent/'WORK.json')
            for field,value in [('numerical_source_commit',source),('candidate_source_commit',candidate),('protocol_sha256',sm['protocol_sha256']),('assessment_fingerprint',sm['assessment_fingerprint'])]:
                require(r[field]==work[field]==value,'mechanism dual-source assessment identity mismatch: '+field)
            require(work['trial']==proof['trial'] and work['trial']['trial_id']==r['trial_id'],'mechanism trial identity mismatch')
            selected_folder=main_root/'trials'/r['trial_id']/'nbo';selected=read(selected_folder/'RESULT.json')
            require(selected['dimension']==r['dimension'] and selected['stream_seed']==r['stream_seed'],'mechanism selected stream identity mismatch')
            require(proof['candidate_source_commit']==candidate and proof['candidate_method_fingerprint']==sm['candidate_method_fingerprint'],'mechanism input source/fingerprint mismatch')
            for relative,field in [('RESULT.json','primary_result_sha256'),('WORK.json','primary_work_sha256'),('../TRIAL.json','primary_trial_receipt_sha256')]:
                require(sha(selected_folder/relative)==proof[field],'mechanism primary receipt bytes differ: '+field)
            checkpoint=safe_path(selected_folder,selected['selected_checkpoint'])
            require(sha(checkpoint)==selected['selected_checkpoint_sha256']==r['candidate_sha256']==r['selected_checkpoint_sha256']==proof['candidate_sha256'],'mechanism did not assess the published selected checkpoint')
            require(sha(safe_path(path.parent,r['raw_path']))==r['raw_sha256'],'mechanism raw array digest mismatch')
            workers.append(check_work(path.parent,source,sm['protocol_sha256'],sm['environment_contract']))
        require(found==expected and len(found)==32,'incomplete 16-stream mechanism family')
        replay=check_report_replay(repo,R15/'code/report_mechanism.py',R15/'MECHANISM_PROTOCOL.json',root/'trials',root/'report')
    else:raise ValueError('unknown evidence role '+name)
    for worker in workers:worker['path']=str(Path(worker['path']).relative_to(repo))
    return dict(source_commit=source,evidence_commit=evidence,evidence_root=str(root.relative_to(repo)),
        source_manifest_sha256=sha(sm_path),evidence_manifest_sha256=sha(em_path),family_audit_sha256=sha(audit_path),
        source_files=files,evidence_files=len(retained),workers=workers,independent_report_replay=replay,
        candidate_source_commit=cfg.get('candidate_source_commit'),candidate_evidence_commit=cfg.get('candidate_evidence_commit'))


def tex_closure(repo,path,stack=()):
    name=str(Path(path));require(name not in stack,'cyclic TeX input')
    text=safe_path(repo,name).read_text()
    text=re.sub(r'%[^\n]*','',text)
    def expand(match):
        child=match.group(1);child=child if Path(child).suffix else child+'.tex'
        return tex_closure(repo,child,stack+(name,))
    return re.sub(r'\\input\{([^}]+)\}',expand,text)


def check_integration_replay(repo):
    """Rebuild editorial sources in isolation; never write the reviewed tree."""
    inventory=read(repo/R15/'SOURCE_INVENTORY.json')['source_files']
    inputs={Path(x) for x in inventory}|set(ROOT_ARCHIVE.values())
    inputs.update({R15/'SOURCE_INVENTORY.json',R15/'code/integrate.py'})
    inputs.update(x.relative_to(repo) for x in (repo/R15/'manuscript').glob('*.tex'))
    inputs.update(x.relative_to(repo) for x in (repo/R15/'results').rglob('*.tex'))
    with tempfile.TemporaryDirectory(prefix='nbo-r15-editorial-replay-') as tmp:
        target=Path(tmp)
        for name in inputs:
            destination=safe_path(target,name);destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(safe_path(repo,name),destination)
        # No Git checkout is needed: integrate's fallback verifies every source
        # byte against SOURCE_INVENTORY and uses the exact archived root files.
        process=subprocess.run([sys.executable,str(target/R15/'code/integrate.py'),'--write-roots'],cwd=target,env=replay_environment(),capture_output=True,text=True)
        require(process.returncode==0,'isolated editorial integration failed: '+process.stderr[-3000:])
        outputs={Path('ECTA.tex'),Path('supp.tex'),R15/'response.tex',R15/'EDITORIAL_MAP.json',R15/'MATHEMATICAL_PRESERVATION.json'}
        if (target/R15/'PRESENTATION_INPUTS.json').exists():outputs.add(R15/'PRESENTATION_INPUTS.json')
        outputs.update(x.relative_to(target) for x in (target/R15/'manuscript').glob('*.tex'))
        for name in outputs:
            require((target/name).read_bytes()==safe_path(repo,name).read_bytes(),'current integrated source differs from independent replay: '+str(name))
        return dict(files_compared=len(outputs),scope='Independent temporary-tree execution of the frozen editorial integrator; exact current roots, response wrapper, generated manuscript and preservation-map bytes.')


def check_outward_presentation(repo):
    script=repo/R15/'code/report_publication_tables.py';published=repo/R15/'results/publication_tables'
    with tempfile.TemporaryDirectory(prefix='nbo-r15-outward-replay-') as tmp:
        command=[sys.executable,str(script),'--protocol',str(repo/R15/'PROTOCOL.json'),
                 '--report',str(repo/R15/'results/experiment/report/REPORT.json'),
                 '--source-manifest',str(repo/R15/'results/experiment/SOURCE_MANIFEST.json'),'--out',tmp]
        process=subprocess.run(command,cwd=repo,env=replay_environment(),capture_output=True,text=True)
        require(process.returncode==0,'outward method presentation replay failed: '+process.stderr[-3000:])
        regenerated={p.name:p for p in Path(tmp).iterdir() if p.is_file()}
        original={p.name:p for p in published.iterdir() if p.is_file()}
        require(set(regenerated)==set(original),'outward presentation inventory differs')
        for name in regenerated:
            require(regenerated[name].read_bytes()==original[name].read_bytes(),'outward presentation differs from exact saved endpoint replay: '+name)
        return dict(files=len(regenerated),manifest_sha256=sha(published/'PUBLICATION_TABLES_MANIFEST.json'),
                    scope='Six-place lower floor/upper ceiling from exact frozen REPORT; all 238 original intervals retained, descriptive means nearest, no new statistical decision.')


def check_narrative(repo):
    status=read(repo/R15/'NARRATIVE_STATUS.json')
    for key in ['primary_result_narrative_pending','mechanism_numerical_narrative_pending']:
        require(status.get(key) is False,'publication narrative remains pending: '+key)
    require(not any(value is True for key,value in status.items() if 'pending' in key),'an additional declared publication narrative remains pending')
    folder=repo/R15/'manuscript'
    current={name:re.sub(r'(?<!\\)%[^\n]*','',(folder/name).read_text()) for name in ['response_body.tex','abstract.tex','introduction.tex','conclusion.tex']}
    expected={f'B{i}' for i in range(1,8)}|{f'M{i}' for i in range(1,10)}
    numbered=re.findall(r'\\(?:sub)?section\*?\{([BM]\d+)(?=[:.\s])',current['response_body.tex'])
    require(len(numbered)==16 and set(numbered)==expected,'response must have exactly one section for each B1--B7 and M1--M9')
    phrases=['this is a working response','still pending','not yet available in this draft']
    for name,text in current.items():
        normalized=' '.join(text.lower().split())
        require(not any(phrase in normalized for phrase in phrases),'old placeholder language in current narrative: '+name)
    abstracts=re.findall(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',current['abstract.tex'],re.S)
    require(len(abstracts)==1,'one current English abstract required')
    plain=re.sub(r'\\[A-Za-z]+\*?',' ',abstracts[0])
    words=re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",plain)
    require(0<len(words)<=150,'current English abstract exceeds 150 words')
    return dict(status_sha256=sha(repo/R15/'NARRATIVE_STATUS.json'),referee_sections=numbered,
                abstract_words=len(words),word_count_scope='English letter/number words; internal apostrophes and hyphens stay within a word; TeX commands/comments excluded.',
                placeholder_scope=list(current),scope='Narrative completeness and disclosure only; no favorable numerical outcome is required.')


def check_paired_semantics(protocol,original,refined):
    design=protocol['design'];seeds=design['seeds'];dims=design['dimensions']
    contrasts=[a+'__minus__'+b for a,b in protocol['confirmation']['direct_contrasts']]
    require(refined['status']=='complete' and refined['reused_direct_events']==102 and refined['additional_confidence_events']==0,'paired transfer must reuse exactly 102 existing events')
    require(refined['changed_payoff_observations']==0 and refined['fitted_weights_read'] is False,'paired transfer changed its input scope')
    require(refined['original_trial_count']==128 and refined['original_confidence']==original['confidence'],'paired transfer changed population or probability allocation')
    for field,origin in [('original_identity_records','identity_records'),('original_unchanged_attainment','attainment'),('original_unchanged_work','work')]:
        require(refined[field]==original[origin],'paired transfer changed an original record: '+field)
    old_seed={(x['dimension'],x['stream_seed'],x['endpoint']):x for x in original['seed_endpoints']}
    old_mean={(x['dimension'],x['endpoint']):x for x in original['method_endpoints']}
    flags={(x['dimension'],x['stream_seed'],x['method']):bool(x['fallback']) for x in original['identity_records']}
    rows=refined['seed_comparisons'];means=refined['method_comparisons']
    expected={(d,s,c) for d in dims for s in seeds for c in contrasts}
    require(len(rows)==96 and {(x['dimension'],x['stream_seed'],x['endpoint']) for x in rows}==expected,'paired transfer omitted or duplicated a stream event')
    require(len(means)==6 and {(x['dimension'],x['endpoint']) for x in means}=={(d,c) for d in dims for c in contrasts},'paired transfer omitted or duplicated a method event')
    event_fields=['paths','clipped_mean','variance','range_lower','range_upper','empirical_bernstein_margin','clipping_tail','event_alpha','clipped_paths']
    def unchanged_event(old,new):
        require(all(old[key]==new[key] for key in event_fields),'paired transfer changed an original empirical-Bernstein event')
        require(old['lower']<=new['lower']<=new['upper']<=old['upper'],'refined interval is not contained in original interval')
    for row in rows:
        d,s,name=row['dimension'],row['stream_seed'],row['endpoint'];left,right=name.split('__minus__')
        old=old_seed[d,s,name];new=row['refined']
        require(row['original']==old,'paired transfer altered its displayed original stream endpoint')
        unchanged_event(old,new);fa,fb=flags[d,s,left],flags[d,s,right]
        if fa or fb:
            kind='both_exact_reference' if fa and fb else 'mixed_fallback_original_transfer_retained'
            require(row['eligibility']==kind and row['refinement_applied'] is False,'invalid fallback refinement eligibility')
            require(row['new_theorem_bias_candidate'] is None and row['numerical_terms'] is None,'fallback received an ineligible paired-theorem allowance')
            require(all(old[k]==new[k] for k in ['lower','upper','bias']),'fallback original transfer or endpoints changed')
            if fa and fb:require(new['lower']==new['upper']==new['bias']==0.,'two analytical fallbacks must preserve exact zero')
        else:
            candidate=row['new_theorem_bias_candidate']
            require(row['eligibility']=='two_simulated_total_held_policies' and math.isfinite(candidate) and candidate>=0.,'invalid normal-normal transfer candidate')
            require(new['bias']==min(old['bias'],candidate) and row['refinement_applied']==(candidate<old['bias']),'refined allowance must be the smaller proved deterministic bias')
    for row in means:
        d,name=row['dimension'],row['endpoint'];old=old_mean[d,name];new=row['refined']
        require(row['original']==old,'paired transfer altered its displayed original method endpoint');unchanged_event(old,new)
        matching=[x for x in rows if x['dimension']==d and x['endpoint']==name]
        require(row['eligible_normal_normal_streams']==sum(x['eligibility']=='two_simulated_total_held_policies' for x in matching) and row['refined_streams']==sum(x['refinement_applied'] for x in matching),'refinement stream denominator/count changed')
        require(new['declared_seeds']==seeds and new['seed_count']==16,'paired method target changed')
        lower,upper,margin=new['lower'],new['upper'],protocol['economic_decision']['equivalence_margin_payoff']
        decisions={'statistical_superiority':lower>0,'economically_material_superiority':lower>margin,'noninferiority':lower>-margin,'practical_equivalence':lower>-margin and upper<margin,'economically_material_inferiority':upper<-margin}
        decisions['unresolved']=not(decisions['economically_material_superiority'] or decisions['economically_material_inferiority'] or decisions['practical_equivalence'])
        require(new['decision']==decisions,'paired refined decision changed the original economic rule')
    return dict(seed_events=len(rows),method_events=len(means),additional_events=0,fallbacks='Both exact and mixed cases preserve their original intervals and transfer; only two simulated total-held policies are eligible.')


def check_paired_transfer(repo):
    root=repo/R15/'results/paired_transfer';published=root/'PAIRED_TRANSFER_REPORT.json'
    original_path=repo/R15/'results/experiment/report/REPORT.json';protocol_path=repo/R15/'PROTOCOL.json'
    recorded=read(published);original=read(original_path);protocol=read(protocol_path)
    require(recorded['original_report_sha256']==sha(original_path) and recorded['protocol_sha256']==sha(protocol_path),'paired transfer original report/protocol identity mismatch')
    require(recorded['original_numerical_source_commit']==original['source_commit'],'paired transfer numerical source identity mismatch')
    semantics=check_paired_semantics(protocol,original,recorded)
    for entry in recorded['input_file_manifest']:
        path=safe_path(repo,entry['path'])
        require(path.is_file() and sha(path)==entry['sha256'],'paired transfer original input bytes changed')
    with tempfile.TemporaryDirectory(prefix='nbo-r15-paired-replay-') as tmp:
        replay_out=Path(tmp)/'report'
        command=[sys.executable,str(repo/R15/'code/report_paired_transfer.py'),'--protocol',str(protocol_path),
                 '--results',str(repo/R15/'results/experiment/trials'),'--original-report',str(original_path),
                 '--coefficient-record',str(published),'--out',str(replay_out)]
        environment=replay_environment(Path(tmp)/'numba-cache')
        process=subprocess.run(command,cwd=repo,env=environment,capture_output=True,text=True)
        require(process.returncode==0,'paired-transfer proof/report replay failed: '+process.stderr[-4000:])
        new=read(replay_out/'PAIRED_TRANSFER_REPORT.json')
        clocks={'generated_utc','postprocessing_seconds_before_writes'}
        require(set(recorded)==set(new),'paired-transfer report schema differs on replay')
        require(isinstance(recorded['generated_utc'],str) and math.isfinite(recorded['postprocessing_seconds_before_writes']) and recorded['postprocessing_seconds_before_writes']>=0.,'missing separate deterministic-postprocessing work record')
        require({k:v for k,v in recorded.items() if k not in clocks}=={k:v for k,v in new.items() if k not in clocks},'paired-transfer scientific fields differ after saved-proposal proof replay')
        files={'PAIRED_TRANSFER_REPORT.json','paired_transfer_main.tex','paired_transfer_supplement.tex'}
        require({x.name for x in replay_out.iterdir() if x.is_file()}==files,'paired-transfer replay output inventory differs')
        for name in files-{'PAIRED_TRANSFER_REPORT.json'}:
            require((replay_out/name).read_bytes()==(root/name).read_bytes(),'paired-transfer outward table differs from replay: '+name)
    return dict(**semantics,report_sha256=sha(published),coefficient_record=str(published.relative_to(repo)),runtime_fields_not_compared=sorted(clocks),
                scope='Stored spectral proposals revalidated by fresh outward LDL and exact matrix identity; all scientific JSON and both outward tables replay exactly, with no endpoint tolerance.')


def check_editorial(repo,git,history):
    mapping=read(repo/R15/'EDITORIAL_MAP.json')
    require(mapping['reviewed_commit']==BASE and mapping['root_write_authorized_by_cli'],'editorial map is a preview rather than publication integration')
    for field in ['pending_scientific_sections','mathematical_labels_missing_from_current','unresolved_current_references']:
        require(not mapping[field],'incomplete editorial preservation: '+field)
    current=tex_closure(repo,'ECTA.tex')+'\n'+tex_closure(repo,'supp.tex')
    # Integration changes preview-build cross-reference paths in this generated
    # wrapper. Its substantive response body remains a frozen publication input.
    preamble=(repo/'ECTA.tex').read_text().split(r'\begin{document}')[0]
    response=re.sub(r'\\externaldocument\{[^}]+\}(?:\[[^]]*\])?','',preamble)
    response+='\\externaldocument{'+str(R15/'build/ECTA_refs')+'}[ECTA.pdf]\n'
    response+='\\externaldocument{'+str(R15/'build/supp_refs')+'}[supp.pdf]\n'
    response+='\\begin{document}\n\\input{'+str(R15/'manuscript/response_body.tex')+'}\n\\end{document}\n'
    require((repo/R15/'response.tex').read_text()==response,'response wrapper differs from its declared generated article preamble/body')
    labels=re.findall(r'\\label\{([^}]+)\}',current)
    require(len(labels)==len(set(labels)),'duplicate current TeX labels')
    require(len(re.findall(r'\\begin\{algorithm\}',current))==1,'current manuscript must have one authoritative algorithm')
    source_inventory=read(repo/R15/'SOURCE_INVENTORY.json')['source_files']
    source_labels=[]
    for path,facts in source_inventory.items():
        require(path in history['files'],'editorial source absent from historical tree')
        old=history['files'][path]
        require(old['git_blob']==facts['git_blob'] and old['sha256']==facts['sha256'],'editorial source inventory mismatch')
        source_labels += [(path,x) for x in re.findall(r'\\label\{([^}]+)\}',git.blob(old['git_blob']).decode())]
    require(sorted(source_labels)==sorted((x['source_path'],x['label']) for x in mapping['labels']),'editorial label map omitted source content')
    for record in mapping['labels']:
        old=history['files'][record['source_path']]
        require(record['source_git_blob']==old['git_blob'] and record['source_sha256']==old['sha256'],'editorial label source identity mismatch')
        if record['destination']=='current':
            require(record['label'] in labels,'missing supposedly retained current label')
            for path in record['current_files']:
                require(r'\label{'+record['label']+'}' in safe_path(repo,path).read_text(),'editorial destination does not contain label')
        else:
            require(record['destination']=='exact_archive' and record['archive_commit']==BASE,'invalid archive mapping')
            require(not record['label'].startswith(('eq:','thm:','prop:','lem:','ass:')),'mathematical label removed from current manuscript')
    # Replay the declared editorial normalization, without invoking a writer.
    module_path=repo/R15/'code/integrate.py';spec=importlib.util.spec_from_file_location('r15_editorial_normalization',module_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    pattern=re.compile(r'\\begin\{(theorem|proposition|lemma|assumption|proof)\}(.*?)\\end\{\1\}',re.S)
    canonical_math=lambda text:re.sub(r'\s+',' ',re.sub(r'%[^\n]*','',module.present(text))).strip()
    current_math={canonical_math(m.group(0)) for m in pattern.finditer(current)}
    count=0
    for path in source_inventory:
        original=git.blob(history['files'][path]['git_blob']).decode()
        for match in pattern.finditer(original):
            require(canonical_math(match.group(0)) in current_math,'reviewed theorem/proof content not preserved: '+path)
            count+=1
    supplied=read(repo/R15/'MATHEMATICAL_PRESERVATION.json')
    require(supplied['preserved']==count and all(x['current_statement_equal_after_editorial_normalization'] for x in supplied['records']),'mathematical preservation record differs from replay')
    replay=check_integration_replay(repo)
    presentation=check_outward_presentation(repo)
    narrative=check_narrative(repo)
    paired=check_paired_transfer(repo)
    return dict(reviewed_labels=len(source_labels),current_labels=len(labels),mathematical_statements_and_proofs=count,editorial_map_sha256=sha(repo/R15/'EDITORIAL_MAP.json'),mathematical_preservation_sha256=sha(repo/R15/'MATHEMATICAL_PRESERVATION.json'),isolated_integration_replay=replay,outward_method_presentation_replay=presentation,narrative=narrative,paired_transfer=paired)


def check_pdfs(repo):
    compilation=read(repo/R15/'results/COMPILATION.json');answer={}
    require(set(compilation)=={'ECTA','supp','response'},'three publication PDFs required')
    for name,record in compilation.items():
        pdf=repo/R15/'build'/f'{name}.pdf';log=pdf.with_suffix('.log')
        require(pdf.is_file() and pdf.stat().st_size>1000 and sha(pdf)==record['pdf_sha256'],'compiled PDF identity mismatch: '+name)
        require(not any(record[k] for k in ['undefined','multiply_defined','duplicate_destinations','overfull_hbox_pt']),'compilation gate failed: '+name)
        text=log.read_text(errors='replace')
        require(not re.search(r'undefined references|Citation .* undefined|Reference .* undefined|Undefined control sequence|multiply.defined (?:labels|citations)|destination with the same identifier|duplicate destination|Overfull \\hbox',text,re.I),'compiler log contains unresolved material: '+name)
        info=subprocess.check_output(['pdfinfo',str(pdf)]).decode();pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
        require(pages==record['pages'] and pages>0,'PDF page count mismatch')
        answer[name]=dict(path=str(pdf.relative_to(repo)),sha256=sha(pdf),pages=pages,log_sha256=sha(log))
    return answer


def check_publication_inputs(repo,git,source):
    records={};prefix=R15.as_posix()+'/'
    for name,facts in git.tree(source).items():
        if not name.startswith(prefix):continue
        sub=Path(name).relative_to(R15)
        if sub.parts[0] in ['build','preview','previewbuild']:continue
        if sub.as_posix()=='results/COMPILATION.json':continue
        if len(sub.parts)>1 and sub.parts[0]=='results' and sub.parts[1] in ['experiment','observation','mechanism']:
            # Independently checked against each generating/evidence commit;
            # avoid copying their large inventories into this second ledger.
            continue
        if sub.name in DERIVED_TOP:continue
        if '__pycache__' in sub.parts or sub.suffix=='.pyc':continue
        records[name]=git.compare(facts['git_blob'],safe_path(repo,name))
    require(str(R15/'code/publication_audit.py') in records,'audit implementation absent from publication source')
    return records


def audit(repo,publication_source,sources,strict=False):
    repo=Path(repo).resolve();sources=Path(sources);sources=sources if sources.is_absolute() else repo/sources
    cfg=read(sources);git=GitStore(repo);issues=[];checks={}
    def run(name,function):
        try:checks[name]=function()
        except Exception as exc:
            issues.append(dict(check=name,error_type=type(exc).__name__,error=str(exc)))
            if strict:raise
    try:
        require(cfg.get('historical_commit',BASE)==BASE and cfg.get('expected_historical_blobs',8652)==8652,'publication historical preservation target cannot be changed')
        run('publication_inputs',lambda:check_publication_inputs(repo,git,publication_source))
        run('history',lambda:check_history(repo,git,cfg.get('historical_commit',BASE),cfg.get('expected_historical_blobs',8652)))
        run('review',lambda:check_review(repo,git))
        roles=cfg['roles'];require(set(roles)=={'observation','main','mechanism'},'all three numerical evidence roles required')
        require(roles['mechanism']['candidate_source_commit']==roles['main']['source_commit'] and roles['mechanism']['candidate_evidence_commit']==roles['main']['evidence_commit'],'publication roles disagree on the selected primary evidence identity')
        for name in ['observation','main','mechanism']:
            run(name,lambda name=name:check_role(repo,git,name,roles[name]))
        if 'history' in checks:run('editorial',lambda:check_editorial(repo,git,checks['history']))
        run('pdfs',lambda:check_pdfs(repo))
        require(not strict or not issues,'strict publication audit failed')
        ledger=dict(record_type='R15 immutable generating-source and publication ledger',complete=not issues,
            publication_source_commit=publication_source,configuration_sha256=sha(sources),
            historical_base_commit=BASE,review_commit=REVIEW,checks=checks,issues=issues,
            scope='Publication source is distinct from each numerical generating source and each later evidence commit. No hash or commit identity refers to a file containing itself.')
        ledger_path=repo/R15/'SOURCE_LEDGER.json';write(ledger_path,ledger)
        # Payload excludes final audit and digest manifest. Source ledger is an
        # already finalized predecessor and therefore safe to include.
        payload={}
        for path in sorted((repo/R15).rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc':continue
            relative=path.relative_to(repo/R15)
            if len(relative.parts)==1 and path.name in {'EVIDENCE_MANIFEST.json','FINAL_AUDIT.json'}:continue
            if relative.parts[0] in ['preview','previewbuild']:continue
            payload[str(path.relative_to(repo))]=dict(sha256=sha(path),bytes=path.stat().st_size)
        for name in ['ECTA.tex','supp.tex','README.md']:payload[name]=dict(sha256=sha(repo/name),bytes=(repo/name).stat().st_size)
        manifest_path=repo/R15/'EVIDENCE_MANIFEST.json'
        write(manifest_path,dict(record_type='R15 complete publication payload digests',publication_source_commit=publication_source,
            hash_scope='All R15 publication payload including source ledger, nested numerical manifests, raw evidence, compilation records and PDFs; excludes this manifest and FINAL_AUDIT.json to avoid circular hashes.',files=payload))
        final=dict(record_type='R15 independent final publication audit',complete=not issues,publication_source_commit=publication_source,
            source_ledger_sha256=sha(ledger_path),evidence_manifest_sha256=sha(manifest_path),payload_files=len(payload),
            historical_blobs_preserved=checks.get('history',{}).get('blobs'),review_files_preserved=len(checks.get('review',{}).get('files',{})),
            family_evidence_files={k:checks[k]['evidence_files'] for k in roles if k in checks},
            editorial=checks.get('editorial'),pdfs=checks.get('pdfs'),issues=issues,
            numerical_outcomes='No sign, superiority, equivalence, or success-rate outcome is an audit pass condition.',
            self_reference_policy='This final record hashes its two finalized predecessor records and is not included in their payload hashes.')
        write(repo/R15/'FINAL_AUDIT.json',final)
        return final
    finally:git.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repo',default='.');parser.add_argument('--publication-source',required=True);parser.add_argument('--sources',required=True);parser.add_argument('--strict',action='store_true');args=parser.parse_args()
    result=audit(**vars(args));print(json.dumps(result,indent=2,allow_nan=False))
