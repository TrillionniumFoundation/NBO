"""Hash all R5 sources and executed files; verify without rerunning experiments."""
from pathlib import Path
import hashlib,json,argparse
D=Path(__file__).resolve().parents[1];ROOT=D.parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def included():
    paths=[p for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json' and p.suffix not in ('.aux','.out','.brf','.toc')]
    paths += [ROOT/n for n in ('ECTA_R5.tex','SUPP_R5.tex','README_R5.md') if (ROOT/n).is_file()]
    return sorted(set(paths))
def main():
    a=argparse.ArgumentParser();a.add_argument('--verify',action='store_true');opt=a.parse_args();f=D/'manifest.json'
    if opt.verify:
        m=json.loads(f.read_text());bad=[n for n,h in m['sha256'].items() if not (ROOT/n).is_file() or digest(ROOT/n)!=h]
        if bad:raise SystemExit('Hash mismatch: '+str(bad))
        print('Verified',len(m['sha256']),'committed R5 file hashes. No training or theorem proof was rerun.')
    else:
        m=dict(review_base='2cbcff05a9fccf263ae50cbcf36ac4a88285e237',revision='R5',hash_algorithm='SHA-256',sha256={str(p.relative_to(ROOT)):digest(p) for p in included()},scope='Exact delivered files. A hash validates identity, not mathematical correctness or experiment success.')
        f.write_text(json.dumps(m,indent=2));print('Hashed',len(m['sha256']),'files')
if __name__=='__main__':main()
