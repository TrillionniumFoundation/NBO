"""Reuse a completed continuum check only for byte-identical checked inputs.

This is for publication retries, not a substitute for the fresh R19 full run.
The source receipt must come from run 35464366825 or a committed copy of it.
The fresh checker command remains documented for complete reproduction.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'replication/r19/output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--artifact-root',type=Path,required=True);args=parser.parse_args()
    paths=list(args.artifact_root.rglob('inherited_validation.json'))
    if len(paths)!=1:raise ValueError('expected exactly one completed fresh continuum receipt')
    src=paths[0];r=json.loads(src.read_text())
    if r.get('schema')!='nbo-r14-independent-validation-v1' or r.get('all_passed') is not True or r.get('optimized_python') is not True:
        raise ValueError('not the completed R19 optimized-Python continuum check')
    checked=r.get('checked_input_hashes',{})
    if len(checked)<60:raise ValueError('incomplete input binding')
    for name,expected in checked.items():
        p=(ROOT/name).resolve()
        if ROOT.resolve() not in p.parents or not p.is_file() or sha(p)!=expected:
            raise ValueError('continuum input is absent or changed: '+name)
    if sha(ROOT/'replication/r13/canonical/manifest.json')!=r['canonical_manifest_sha256']:
        raise ValueError('canonical target identity')
    OUT.mkdir(parents=True,exist_ok=True);dst=OUT/'inherited_validation.json';shutil.copyfile(src,dst)
    report=dict(schema='nbo-r19-continuum-receipt-binding-v1',passed=True,source_workflow_run=35464366825,
      source_commit='93c9a450179c76e8923841a162a0fac0f24a3948',receipt_sha256=sha(dst),checked_files=len(checked),
      checked_dynamic_problems=r['checked_dynamic_problems'],institutional_comparisons=r['institutional_comparisons'],
      scope='The fresh independent continuum checker completed in the identified R19 run. This publication retry reuses that exact receipt only after rehashing every scientific and checker input. No previous timing is labeled as the runtime of this hash check.')
    (OUT/'continuum_receipt_binding.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
