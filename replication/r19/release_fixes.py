"""Idempotent release corrections identified during independent review.

Restrict the primary receipt to files it actually checks: derived downstream
receipts/tables must not be hashed before they are regenerated. The publisher
then validates every recorded input hash against the actual released bytes.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def replace(path,old,new):
    s=path.read_text()
    if old in s:
        if s.count(old)!=1:raise ValueError('ambiguous correction '+str(path))
        path.write_text(s.replace(old,new))
    elif new not in s:raise ValueError('unknown source '+str(path)+' '+old[:70])

def main():
    p=ROOT/'replication/r19/verify.py'
    replace(p,"if p.suffix in ('.json','.npz') and p.name!='validation.json'", "if p.name in ('continuous_benchmark.json','theorem_fixtures.json','enforcement.json','enforcement_witness.npz','proposals.json','proposal_witness.npz','arithmetic.json','generation.json')")
    p=ROOT/'replication/r19/publish.py'
    replace(p,"require(phrase.lower() in text.lower(),name+' missing current argument '+phrase)","require(phrase.lower() in ' '.join(text.lower().split()),name+' missing current argument '+phrase)")
    old="    preserved=['replication/r13/canonical'"
    new="    receipt=json.loads((ROOT/'replication/r19/output/validation.json').read_text())\n    for name,expected in receipt['checked_sha256'].items():\n      require(digest(ROOT/'replication/r19/output'/name)==expected,'checked input changed: '+name)\n    preserved=['replication/r13/canonical'"
    replace(p,old,new)
    p=ROOT/'replication/r19/polish.py'
    old="    print('Current-source notation and signed-error scope reconciled; exact auxiliary examples passed.')"
    new="    for readme in (ROOT/'README.md',ROOT/'revisions/2026-09-20-r19/README.md'):\n      s=readme.read_text().replace('python replication/r19/assemble.py\\npython replication/r19/publish.py','python replication/r19/assemble.py\\npython replication/r19/polish.py\\npython replication/r19/publish.py')\n      readme.write_text(s)\n    print('Current-source notation and signed-error scope reconciled; exact auxiliary examples passed.')"
    replace(p,old,new)
    print('Receipts bind only actual checked inputs, and publication verifies their hashes.')
if __name__=='__main__':main()
