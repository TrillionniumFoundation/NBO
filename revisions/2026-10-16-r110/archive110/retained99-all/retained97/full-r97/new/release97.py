"""Record actual R97 delivery gates, without inventing scientific closure."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
R=Path(__file__).resolve().parents[1]
def read(p):
    q=R/p
    return json.loads(q.read_text()) if q.exists() else None

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    c=read('results97/CAMPAIGN97.json');s=read('results97/SUMMARY97.json');i=read('audit97/INDEPENDENT97.json')
    b=read('audit97/build/BUILD97.json');t=read('audit97/inherited-tests/TESTS95.json')
    original=read('audit97/INHERITED_SCIENTIFIC_SOURCES97.json') or {}
    preserved=bool(original) and all((R/p).exists() and sha(R/p)==h for p,h in original.items())
    log=R/'audit97/NEW_TESTS97.log'
    tests97=log.exists() and '\nOK\n' in log.read_text() and 'Ran 8 tests' in log.read_text()
    arm=R/'evidence97/arm64-r96/audit/arm64-96/ARCHITECTURE96.json'
    gates=dict(protocol_source_hash=sha(R/'new/study97.py')=='db947fbbe20a92f38d8b5b95e4f5d733f8a3162df30d2f670e13a472b493baba',
      inherited_scientific_sources_preserved=preserved,
      inherited_tests=bool(t) and all(v['passed'] and not v['skipped'] for v in t.values()),new_tests=tests97,
      campaign=bool(c) and c.get('status')=='executed',source_bound_report=bool(s),
      independent_replay=bool(i) and i.get('status')=='passed' and not i.get('discrepancies'),
      manuscript_build=bool(b) and b.get('status')=='compiled',historical_arm_evidence_integrated=arm.exists())
    files={str(p.relative_to(R)):sha(p) for p in sorted(list((R/'new').glob('*'))+[R/'response.md',R/'README97.md',R/'PROTOCOL97.md']) if p.is_file()}
    out=dict(status='verified' if all(gates.values()) else 'incomplete',gates=gates,
      scientific_parent='9a80ab7d4de97c9a61747899766fab43ec3c2598',review_parent='e91a0702a4f1df4baa7b43fdfdd1305d0d62940c',
      protocol_commit='673d29e48922ae59908cdde245f312e077442539',source_commit=os.environ.get('NBO_SOURCE_COMMIT'),workflow_run=os.environ.get('GITHUB_RUN_ID'),
      inherited_test_count=sum(v['tests'] for v in t.values()) if t else None,new_test_count=8 if tests97 else None,
      source_sha256=files,documents=b.get('documents') if b else None,visual_inspection_recorded=(R/'VISUAL97.json').exists(),
      unresolved_scientific_scope=['new longer-horizon multicontrol multi-innovation continuous-risk tournament','external economic calibration','broader conventional representation frontier','independent fitting implementation'],
      interpretation='These are reproducibility and delivery gates, not an editorial decision or proof of universal neural superiority.')
    (R/'RELEASE97.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2))
    return 0 if all(gates.values()) else 1
if __name__=='__main__':sys.exit(main())
