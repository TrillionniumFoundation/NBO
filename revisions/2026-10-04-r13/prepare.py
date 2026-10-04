"""Materialize R13 from the pinned R12 source without editing any historical folder."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
R=Path(__file__).resolve().parent
BASE='65110ed2991f4b955d2df37b2ab8635b12df5d1c'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(b):return hashlib.sha256(b).hexdigest()
def patch(path,old,new):
    text=path.read_text()
    if text.count(old)!=1:raise RuntimeError(f'expected one patch site: {path.name}: {old[:80]}')
    path.write_text(text.replace(old,new))
def main():
    source=ROOT/'revisions/2026-10-04-r12'
    if (R/'MATERIALIZED.json').exists():
        print('R13 is already materialized; no source rewrite.');return
    inherited={}
    for p in source.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts:continue
        rel=p.relative_to(source);target=R/str(rel).replace('r12','r13')
        if target.exists():raise RuntimeError('refuse to overwrite authored source '+str(target))
        b=p.read_bytes();target.parent.mkdir(parents=True,exist_ok=True)
        if 'archive' not in rel.parts:
            b=b.decode().replace('r12','r13').replace('R12','R13').encode()
        target.write_bytes(b);inherited[str(rel)]=sha(p.read_bytes())
    for name in ['ECTA.tex','supp.tex','README.md','revision_reference.bib']:
        b=git('show',BASE+':'+name);(R/'archive'/(name+'.reviewed')).write_bytes(b)
    protocol=json.loads((R/'PROTOCOL.json').read_text())
    protocol.update(revision='R13',review_commit=BASE,final_noise_seed=92413000,development_noise_seed=82413000,
        fixed_work_budgets=[80,160],fixed_work_seeds=protocol['seeds'],fixed_work_dimensions=[10,20,50],
        fixed_work_noise_seed=93413000,mechanism_seed=7919,mechanism_states=12,mechanism_replicates=32,
        mechanism_steps=[32,64,128],mechanism_noise_seed=73413000,
        observation_seed=7919,observation_dimensions=[10,50],observation_cells=[32,64,128],
        observation_noise_rms=[0.0,0.01],observation_paths=256,observation_fine_cells=1024,
        accuracy_gain_targets=[0.0,0.0005,0.001],accuracy_regret_targets=[0.02,0.03,0.04],
        secondary_environment='Ubuntu 22.04, seed 7919, fixed 80/160 iterations, dimensions 10 and 50; same numerical versions; compare hashes and achieved endpoints, not wall-clock identity',
        protocol_status='R12 final design carried forward and extended before any R13 final outcome; development and final banks remain separate; not a historical preregistration')
    (R/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2)+'\n')
    patch(R/'code/test_runner.py',"roots=['ECTA.tex','supp.tex','revision_reference.bib']","roots=['ECTA.tex','supp.tex','revision_reference.bib','README.md']")
    patch(R/'code/finalize.py',"'README.md':'revisions/2026-10-04-r13/archive/README.r11.md'","'README.md':'revisions/2026-10-04-r13/archive/README.md.reviewed'")
    patch(R/'code/finalize.py',"    result=dict(source_commit=source_sha", "    from extra_report import verify as verify_extra\n    extra=verify_extra()\n    result=dict(extra=extra,source_commit=source_sha")
    # Retain component diagnostics without changing the scalar solver's equations.
    p=R/'code/reference.py'
    patch(p,'initial={};residual=0.;iterations=0;converged=True;stored_policy=None',
          "initial={};residual=0.;iterations=0;converged=True;stored_policy=None\n    policy_residual={name:0. for name in policies};bounds={name:[0,0,0] for name in policies}")
    patch(p,"values[name]=vv;residual=max(residual,res)","values[name]=vv;residual=max(residual,res);policy_residual[name]=max(policy_residual[name],res)\n            bounds[name][0]+=int((m<=P['lower']+1e-12).sum());bounds[name][1]+=int((m>=P['upper']-1e-12).sum());bounds[name][2]+=len(m)")
    patch(p,'row=dict(id=ident,nx=nx,nt=nt,L=L,', 'row=dict(fixed_policy_residuals=policy_residual,action_bound_counts=bounds,id=ident,nx=nx,nt=nt,L=L,')
    # Historical R12 counts concern only its primary family; extras are independently replayed.
    p=R/'manuscript/study.tex'
    text=p.read_text().replace('The new study separates','The completed-design study separates')
    text=text.replace('A family of 4,000 one-sided statements is allocated before final testing and covers both signs of every reported stochastic endpoint.','A family of 4,000 one-sided statements is allocated before final testing across the primary and additional work comparisons; it covers both signs of every reported certified stochastic endpoint.')
    p.write_text(text)
    # New text and executable extensions are separate authored files in this revision.
    for p in (R/'authored').glob('*'):
        destination=R/('code' if p.suffix=='.py' else 'manuscript')/p.name
        destination.write_bytes(p.read_bytes())
    (R/'MATERIALIZED.json').write_text(json.dumps(dict(base_commit=BASE,inherited_templates=inherited,
        historical_directories_modified=False,source='R12 templates copied and versioned as R13; exact old templates remain in their original folder'),indent=2)+'\n')
    print('Materialized',len(inherited),'inherited R13 files plus authored additions.')
if __name__=='__main__':main()
