"""Losslessly restore redundant large initial diagnostic fractions.
Only the diagnostic expression is transported by its exact source and inputs.
The complete restored original JSON file must match its recorded SHA-256.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[1]
legacy=R/'history/initial_frozen'
sys.path.insert(0,str(legacy))
# Deliberately execute the frozen original diagnostic, in a separate process.
import run_suite as original

def main():
    manifest=json.loads((R/'history/initial_record_manifest.json').read_text())
    for name,sha in manifest.items():
        p=legacy/name
        if hashlib.sha256(p.read_bytes()).hexdigest()==sha:continue
        row=json.loads(p.read_text());d=original.model(row['seed'],row['n'],row['T'],row['m'],row['beta'],row['epsilon'])
        row['theory']=original.theoretical(d)
        p.write_text(json.dumps(row,default=original.enc,indent=2)+'\n')
        assert hashlib.sha256(p.read_bytes()).hexdigest()==sha,name
        print('Restored exact initial record',name,flush=True)
if __name__=='__main__':main()
