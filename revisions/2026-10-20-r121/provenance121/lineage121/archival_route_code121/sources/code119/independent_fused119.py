"""Reapply the declared independent exact suite to phase C, before performance."""
from pathlib import Path
import sys,os,json,hashlib,subprocess,time,traceback,argparse
import independent_tail119 as independent
ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser();p.add_argument('--custody-commit',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve every independent phase-C attempt')
    a.output.mkdir(parents=True);started=time.time()
    try:
        provenance=independent.bind_sources(a.custody_commit)
        frozen=json.loads((ROOT/'SOURCE_FREEZE119C.json').read_text())
        repo=ROOT.parents[1];bound=[]
        for name in list(frozen['files'])+['SOURCE_FREEZE119C.json']:
            path=ROOT/name;relative=path.relative_to(repo).as_posix()
            data=subprocess.check_output(['git','show',a.custody_commit+':'+relative],cwd=repo)
            if data!=path.read_bytes():raise ArithmeticError('Different committed phase-C bytes: '+relative)
            sha=hashlib.sha256(data).hexdigest()
            if name in frozen['files'] and frozen['files'][name]!=sha:raise ArithmeticError('Different phase-C freeze: '+name)
            bound.append(dict(path=name,sha256=sha))
        provenance.update(phase='R119-C',phase_C_sources=bound,started_unix=started,
            validation='Declared reuse of the phase-A fixed exact suite, not unseen-case selection',
            density_suite_scope='The shared tail_mesh allocates zero-weight geometry. The inherited phrase production still pays those nodes describes phase A only; phase C omits their compiler queries, independently counted in audit119c.')
        independent.save(a.output/'PROVENANCE119C.json',provenance)
        original_loader=independent.load_science
        def new_loader():
            old,np,exact=original_loader()
            import fused_tail119 as new
            return new,np,exact
        independent.load_science=new_loader
        result=independent.audit(a.output)
        independent.save(a.output/'EXECUTION119C.json',dict(status=result['status'],phase='R119-C',
            custody_commit=a.custody_commit,started_unix=started,ended_unix=time.time(),checks=result['checks'],
            files=[dict(path=p.name,sha256=independent.digest(p)) for p in sorted(a.output.iterdir()) if p.is_file()]))
        if result['status']!='passed':raise ArithmeticError('One or more retained exact checks failed')
    except BaseException:
        independent.save(a.output/'FAILED119C.json',dict(status='failed',custody_commit=a.custody_commit,
            started_unix=started,ended_unix=time.time(),exception=traceback.format_exc()))
        raise


if __name__=='__main__':main()
