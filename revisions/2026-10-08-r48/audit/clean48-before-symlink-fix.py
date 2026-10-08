"""Verify an offline clean rebuild of the staged R48 candidate Git commit.

Call after committing the ordinary manuscript, its frozen records, and all
historical dependencies. Does not rerun economic simulations or retime services.
"""
from __future__ import annotations
import hashlib,json,os,re,shutil,subprocess,sys,tarfile,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    candidate=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    paths=['revisions/'+s for s in ('2026-10-07-r44','2026-10-07-r45','2026-10-07-r46','2026-10-08-r47','2026-10-08-r48')]
    source={str(p.relative_to(R)):H(p) for p in R.glob('*.tex')}
    source.update({str(p.relative_to(R)):H(p) for folder in ('tables','sections') for p in (R/folder).glob('*.tex')})
    science=json.loads((R/'audit/EXECUTION_COMPLETE.json').read_text())
    before={'source':science['source_hashes'],'results':science['result_hashes']}
    full=[]
    with tempfile.TemporaryDirectory(prefix='nbo-r48-clean-') as tmp:
        temp=Path(tmp);archive=temp/'candidate.tar'
        with archive.open('wb') as f:subprocess.run(['git','archive',candidate,*paths],cwd=ROOT,stdout=f,check=True)
        work=temp/'work';work.mkdir()
        with tarfile.open(archive) as tf:
            for m in tf.getmembers():
                p=Path(m.name);assert not p.is_absolute() and '..' not in p.parts
                assert not m.issym() and not m.islnk(),m.name
            tf.extractall(work,filter='data')
        target=work/'revisions/2026-10-08-r48'
        # Generated objects are removed; ordinary inputs and frozen records stay.
        shutil.rmtree(target/'build');shutil.rmtree(target/'tables')
        for name in ('ECTA.tex','supp.tex','response.tex','response.md'):(target/name).unlink()
        env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
        q=subprocess.run([sys.executable,str(target/'code/build48.py')],cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (R/'audit/clean-rebuild.log').write_text(q.stdout)
        assert q.returncode==0,'Clean rebuild failed; inspect audit/clean-rebuild.log'
        for name,h in source.items():assert H(target/name)==h,name
        for group in before.values():
            for name,h in group.items():assert H(target/name)==h,name
        release=json.loads((target/'audit/RELEASE_AUDIT.json').read_text());assert release['total_tests']==96
        original=json.loads((R/'audit/RELEASE_AUDIT.json').read_text())
        for a,b in zip(original['compilation'],release['compilation']):
            assert a['document']==b['document'] and a['pages']==b['pages']
            assert not any(b[k] for k in ('undefined_references','duplicate_labels','missing_characters','overfull_boxes'))
        full=release['compilation']
    record={'successful':True,'candidate_commit':candidate,'tests':96,'ordinary_source_files_compared':source,'frozen_scientific_files_verified':sum(len(g) for g in before.values()),'compilation':full,'network_or_expiring_artifact_required':False,'scientific_execution_repeated':False,'scope':'Scoped git archive; generated R48 article, supplement, response, tables and PDF build directory removed before an ordinary-source rebuild. Historical dependencies and immutable scientific inputs retained. PDF byte identity is not required across timestamps/environments; source bytes, page counts, reference checks, all tests and frozen result hashes are verified.'}
    (R/'audit/CLEAN_REBUILD.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'successful':True,'candidate_commit':candidate,'tests':96,'source_files':len(source)},indent=2))
if __name__=='__main__':main()
