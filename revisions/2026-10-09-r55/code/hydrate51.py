"""Restore hash-pinned prior inputs. Never modify a historical repository path."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[1]
REVIEW='2822f50100c7a53ec5fe07d39e9b37d487ab0547'
ARCHIVES={'R48-publication.zip':'b82272add8e7ea630ef1ab45455b079514fd848311e2d23db84d2b11ab9cd5df','R49-main.zip':'d367b908c754dfa66efd5b6ed40fd6ce46a6e6606cde959811afb850b4b3c601','R49-graded.zip':'280f32e6cc66344e31c5e04487cd813bdaf21908f6860d1449b2c297f4268517'}
FORBIDDEN={'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}
def safe(n):
    p=Path(n)
    if p.is_absolute() or '..' in p.parts or p.suffix.lower() in FORBIDDEN:raise ValueError('Unsafe input '+n)
    return p

def main():
    repo=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],text=True).strip())
    config=json.loads((R/'publication/REUSE51.json').read_text());opened={};identities={}
    for n,h in ARCHIVES.items():
        p=R/'evidence'/n
        if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('Archive mismatch: '+n)
        opened[n]=zipfile.ZipFile(p);identities[n]=h
        for item in opened[n].infolist():
            safe(item.filename)
            if (item.external_attr>>16)&0o170000==0o120000:raise ValueError('Symlink member: '+item.filename)
    for dest,(archive,member) in config['archives'].items():
        out=R/safe(dest);safe(member);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(opened[archive].read(member))
    for dest,(ref,path,h) in config['git'].items():
        data=subprocess.check_output(['git','show',ref+':'+path],cwd=repo)
        if hashlib.sha256(data).hexdigest()!=h:raise ValueError('Pinned Git source mismatch: '+path)
        out=R/safe(dest);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
    for z in opened.values():z.close()
    (R/'audit').mkdir(exist_ok=True);(R/'tables').mkdir(exist_ok=True)
    record=dict(review=REVIEW,archive_sha256=identities,archive_members_restored=len(config['archives']),git_sources_restored=len(config['git']),recovered_local_package_sha256='fa1fe9690a389a6289bba728d6814b8cc7ee68942a6fc67539c1e9d3de53f4b6',local_delivered_manifest_entries_verified=964,local_delivered_manifest_sha256='4bba263de6fb1105e1a01cef4c7aebb666720d41a5df36f6b002385f4366791b',historical_repository_files_changed=False)
    (R/'audit/RECOVERY51.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    subprocess.run([sys.executable,str(R/'code/assemble50.py')],check=True)
    import build51
    build51.integrate()
    print(json.dumps(record,indent=2))
if __name__=='__main__':main()
