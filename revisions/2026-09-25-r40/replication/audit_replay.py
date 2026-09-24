"""Read-only replay of frozen independent verifiers; write only R40 records."""
from pathlib import Path
import sys,json,gzip,hashlib,time,argparse,importlib.util
ROOT=Path(__file__).resolve().parents[1]; OLD=ROOT.parent/'2026-09-25-r39'

def load(name):
    p=OLD/'replication'/f'{name}.py'
    spec=importlib.util.spec_from_file_location(name,p); mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def main():
    if not __debug__ or sys.flags.optimize: raise RuntimeError('assertions required')
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['finite','continuum','nonlinear']);args=ap.parse_args()
    start=time.perf_counter();out=[]
    if args.mode=='finite':
        v=load('verify_finite')
        for p in sorted((OLD/'results/finite').glob('*.json.gz')):
            row=v.verify(json.loads(gzip.decompress(p.read_bytes())))
            row.update(file=str(p.relative_to(OLD)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());out.append(row);print(p.name,row,flush=True)
        assert len(out)==16
    elif args.mode=='continuum':
        v=load('verify_continuum')
        # Predeclared audit selection, not an out-of-sample performance cohort.
        for name in ('random_H4_neural31001_eps1_100.json.gz','random_H8_neural31002_eps1_20.json.gz','random_H12_defer_eps1_100.json.gz'):
            out.append(v.verify_one(OLD/'results/randomized'/name))
    else:
        v=load('verify_nonlinear');data=json.loads((OLD/'results/nonlinear_support.json').read_text())['outcomes']
        # The complete N=128,T=32 object extends the former N=64 coverage.
        r=next(r for r in data if r['mesh']==128 and r['T']==32);row=v.verify(r)
        row.update(proof_file=r['proof_file'],proof_sha256=r['proof_sha256']);out.append(row);print(row,flush=True)
    report=dict(schema='NBO-R40-read-only-replay-v1',mode=args.mode,outcomes=out,passed=all(r['passed'] for r in out),seconds=time.perf_counter()-start,
      source_revision='bf5d42b08debd4c26341ab1b1231a6a6242df4f9',verifier_sha256=hashlib.sha256(Path(v.__file__).read_bytes()).hexdigest(),
      coverage='Only the explicitly named complete objects. Historical full coverage is separately hash-linked.',python=sys.version)
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results'/f'replay_{args.mode}.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
