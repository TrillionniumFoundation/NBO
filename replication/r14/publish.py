"""Explicit release builder, separate from the read-only referee command.

Requires an actual successful independent receipt supplied via --receipt.
Does not create a target, solve a model, train a network, or fabricate a receipt.
Builds tables/PDFs and seals all cited inputs with SHA-256 in a release manifest.
"""
from __future__ import annotations
import argparse,json,shutil,subprocess,sys
from pathlib import Path
from review import ROOT,REL,DOCS,require,digest,compile_documents,run

def files_for_manifest()->list[Path]:
    paths=set()
    for name in DOCS:paths.add(ROOT/(name+'.tex'));paths.add(ROOT/REL/(name+'.pdf'))
    paths.update([ROOT/'README.md',ROOT/'REVISION_INDEX.md',ROOT/REL/'README.md'])
    for pattern in ('*.cls','*.cfg','*.sty','*.bst'):paths.update(ROOT.glob(pattern))
    paths.add(ROOT/'revisions/2026-09-17-r9-participation-permissions/paper/preamble.tex')
    paths.add(ROOT/'reviews/2026-09-19-econometrica-r13-certified-harsh/referee_report.md')
    for directory in ('replication/r13/canonical','replication/r13/output','replication/r13/extensions'):
        paths.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.update((ROOT/'replication/r13').glob('*.py'))
    paths.update((ROOT/'replication/r14').glob('*.py'))
    paths.add(ROOT/'replication/r14/blueprint.json')
    for name in ('continuum_certificate.json','continuum_witness.npz','economic_extensions.json','mechanism_values.npz'):
        paths.add(ROOT/'replication/r14/output'/name)
    paths.update((ROOT/REL/'paper').glob('*.tex'))
    paths.update(p for p in (ROOT/REL/'historical').iterdir() if p.is_file())
    # Execution/build receipts are immutable inputs. The post-seal reviewer receipt
    # is intentionally external, preventing a self-referential manifest.
    paths.update(p for p in (ROOT/REL/'logs').iterdir() if p.is_file() and not p.name.startswith('release-review'))
    return sorted(paths)

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--receipt',required=True,type=Path);ap.add_argument('--source-commit',required=True);args=ap.parse_args()
    require(len(args.source_commit)==40 and all(c in '0123456789abcdef' for c in args.source_commit),'invalid scientific source commit')
    validation=json.loads(args.receipt.read_text());require(validation.get('all_passed') is True,'no successful independent receipt')
    require(validation.get('checked_dynamic_problems',0)>=583,'receipt does not cover the full dynamic witness')
    require(validation['canonical_manifest_sha256']==digest(ROOT/'replication/r13/canonical/manifest.json'),'receipt is for another target')
    require(bool(validation.get('checked_input_hashes')),'receipt lacks checked-input hashes')
    for name,sha in validation['checked_input_hashes'].items():require(digest(ROOT/name)==sha,'receipt no longer binds current input: '+name)
    logs=ROOT/REL/'logs';logs.mkdir(parents=True,exist_ok=True)
    dest=logs/'independent-validation.json'
    if args.receipt.resolve()!=dest.resolve():shutil.copy2(args.receipt,dest)
    print(run([sys.executable,'replication/r14/build_tables.py'],ROOT).strip(),flush=True)
    docs=compile_documents(ROOT,logs)
    source_paths=sorted((ROOT/'replication/r14').glob('*.py'))
    manifest={'schema':'nbo-r14-release-v1','revision':'R14','date':'2026-09-19','review_branch':'review/econometrica-r13-certified-harsh-2026-09-19-dd9e0c7','review_commit':'13c946c4e9a352612647cd75a6930c5d86d7a564','reviewed_science_commit':'dd9e0c755b743efdea2a7637f7620bb8ebc3b3c6','completed_r13_extension_commit':'59024a9bccfcc71feecec310b690fb181da44386','scientific_source_commit':args.source_commit,'canonical_manifest_sha256':validation['canonical_manifest_sha256'],'independent_validation_sha256':digest(dest),'documents':docs,'source_hashes':{str(p.relative_to(ROOT)):digest(p) for p in source_paths},'files':{str(p.relative_to(ROOT)):digest(p) for p in files_for_manifest()},'scope':'Stored stochastic settlement target, exact-response continuous-fee certificate, all-response finite-query bounds, and retained historical evidence. No claim of a completed quantitative diffusion inclusion or demonstrated neural scaling advantage.','commit_semantics':'scientific_source_commit identifies checked source before generated documents. The final deposit commit identifies this manifest and its file tree; no self-referential final commit hash is embedded.'}
    (ROOT/REL/'release_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print('SEALED',len(manifest['files']),'files',flush=True)
if __name__=='__main__':main()
