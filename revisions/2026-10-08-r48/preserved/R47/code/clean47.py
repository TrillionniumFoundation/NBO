"""Rebuild from a committed Git archive, without retained generated R47 files."""
from pathlib import Path
import hashlib,io,json,os,shutil,subprocess,sys,tarfile,tempfile
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    candidate=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    paths=[f'revisions/2026-10-07-r{x}' for x in (44,45,46)]+['revisions/2026-10-08-r47']
    raw=subprocess.check_output(['git','archive',candidate,*paths],cwd=ROOT)
    canonical={n:H(R/n) for n in ('ECTA.tex','supp.tex','response.tex')}
    canonical.update({str(p.relative_to(R)):H(p) for p in (R/'tables').glob('*47.tex')})
    input_hashes={str(p.relative_to(R)):H(p) for p in (R/'results').rglob('*') if p.is_file()}
    with tempfile.TemporaryDirectory(prefix='nbo-r47-clean-') as temp:
        temp=Path(temp)
        with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
            for m in tf.getmembers():
                q=Path(m.name)
                if q.is_absolute() or '..' in q.parts or m.issym() or m.islnk():raise ValueError('Unsafe archive member')
            tf.extractall(temp)
        fresh=temp/'revisions/2026-10-08-r47'
        shutil.rmtree(fresh/'build');shutil.rmtree(fresh/'tables')
        for n in ('ECTA.tex','supp.tex','response.tex'):(fresh/n).unlink()
        env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
        p=subprocess.run([sys.executable,str(fresh/'code/build47.py')],cwd=temp,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (R/'audit/clean-rebuild.log').write_text(p.stdout)
        if p.returncode:raise RuntimeError('Clean rebuild failed; inspect audit/clean-rebuild.log')
        for n,h in canonical.items():assert H(fresh/n)==h,n
        for n,h in input_hashes.items():assert H(fresh/n)==h,n
        audit=json.loads((fresh/'audit/RELEASE_AUDIT.json').read_text());assert audit['total_tests']==69
        report={'successful':True,'candidate_commit':candidate,'archive_sha256':hashlib.sha256(raw).hexdigest(),
                'ordinary_source_tree':True,'generated_files_removed_before_build':['ECTA.tex','supp.tex','response.tex','build/','tables/'],
                'reconstructed_source_and_table_hashes':canonical,'frozen_result_files_verified':len(input_hashes),
                'tests':69,'compilation':audit['compilation'],'study_reexecuted':False,
                'network_or_expiring_artifact_required':False,'pdf_byte_identity_required':False}
        (R/'audit/CLEAN_REBUILD.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print(json.dumps(report,indent=2))
if __name__=='__main__':main()
