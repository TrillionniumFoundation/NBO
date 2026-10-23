"""Publication source lock after disclosed deterministic development work."""
from pathlib import Path
import subprocess
import frontier83 as f
R=Path(__file__).resolve().parents[1]
def current():
    names=set(f.read(R/'OWN_SOURCE83.json'))
    names.update(('OWN_SOURCE83.json','ECTA.tex','supp.tex','appendix.tex','response.md','SOURCE_FREEZE82.json','code/tables82.py','sections/actionwise82.tex','sections/proof82.tex','sections/study82.tex'))
    names.update(str(p.relative_to(R)) for p in (R/'results82').glob('*.json'))
    return {name:f.sha(R/name) for name in sorted(names)}
def verify():
    lock=f.read(R/'SOURCE_FREEZE83.json');f.need(lock['files']==current(),'Publication-locked source changed');return lock

def main():
    path=R/'SOURCE_FREEZE83.json'
    if path.exists():verify();print('Existing R83 publication lock verified.');return
    try:head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:head=None
    f.save(path,dict(kind='publication_and_reintegration_source_lock_not_prospective_random_design',prepared_from_commit=head,files=current(),
        controlling_review='4b27b56f4514f6c1d77b69fe707f7202f8b06b19',deterministic_development_preceded_lock=True,
        original_cost_outcomes_previously_observed=True,new_independent_samples=0,original_freeze82_sha256=f.sha(R/'SOURCE_FREEZE82.json')))
    print('R83 source lock written; statistical and development scope explicitly recorded.')
if __name__=='__main__':main()
