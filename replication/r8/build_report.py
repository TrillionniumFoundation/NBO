"""Audit source/history/evidence and deposit complete, compiled review copies."""
from pathlib import Path
import json,hashlib,os,shutil,subprocess,argparse
ROOT=Path(__file__).resolve().parents[2];REV=ROOT/'revisions/2026-09-17-r8-full-response';OUT=ROOT/'replication/r8/output'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def main(precompile=False):
    protected=read(REV/'protected_history.json')
    for p,h in protected.items():assert sha(ROOT/p)==h,('Historical input changed',p)
    inventory=read(REV/'source_inventory.json')
    for p,h in inventory.items():assert sha(ROOT/p)==h,('Authored source changed',p)
    cert=read(OUT/'decision_contest.json');assert all(r['signs_certified'] for r in cert['rows'])
    assert cert['arithmetic']['derived_per_class_bound']<cert['per_class_arithmetic_allowance']
    primitive=read(OUT/'primitive_robustness.json');assert primitive['uniform_lower_bound']>.0004173
    validation=read(OUT/'streaming_validation.json');assert validation['models']==60 and validation['class_recursions']==240
    mechanisms=read(OUT/'mechanisms.json');assert mechanisms['total_class_solves']==144 and mechanisms['max_replay_error']<2e-11
    spatial=[]
    for n in (49,97,145):
        s=read(OUT/f'spatial_{n}.json');assert len(s['rows'])==10
        c=read(OUT/f'spatial_nested_certificate_{n}.json');assert c['region']==[0.,.125,.4,.425]
        assert all(r['signs_certified'] for r in c['rows'])
        assert c['arithmetic']['derived_per_class_bound']<1e-7
        spatial.append(s)
    text=['# R8 executed evidence and manuscript audit','',
      'The latest substantive review is the parent of this complete revision. All numbers below are read from executed output, not inferred from branch names.','',
      '## Original full-target decision certificate','',
      '| Upper | Lower bank | Adjusted lower margin | Fixed upper difference | Total seconds |',
      '|---|---|---:|---:|---:|']
    for r in cert['rows']:text.append(f"| {r['method']} | {r['lower_bank']} | {r['bounds']['adjusted'][0]:.15g} | {r['bounds']['fixed'][1]:.15g} | {r['total_seconds']:.6f} |")
    text+=['','All arms include common construction, full-menu upper anchors, lower evaluation, arithmetic auditing, and independent replay. Timings are serial single-pass observations; common setup is charged identically. Historical neural training is not rerun.','',
      f"Derived per-class arithmetic bound: {cert['arithmetic']['derived_per_class_bound']:.16g}; charged allowance: 1e-7. Scope: stored finite arrays, not diffusion or kernel-construction error.",
      '',f"Kernel/reward payload: {cert['kernel_and_reward_bytes']} bytes. Retained policy indices: {cert['retained_policy_bytes']} bytes. Retained focal coefficients: {cert['retained_focal_lower_coefficient_bytes']} bytes. Shared process peak: {cert['maxrss_kib']} KiB.",'',
      '## Original corner and common nested region','',
      '| Wealth nodes | Full-menu fixed difference at old corner | Adjusted difference | Nested adjusted lower | Nested fixed upper |','|---:|---:|---:|---:|---:|']
    for s in spatial:
        r=next(r for r in s['rows'] if r['menu']=='full_prolonged_1568' and r['lambda_']==.25 and r['d']==.45)
        c=read(OUT/f"spatial_nested_certificate_{s['nx']}.json")['rows'][0]
        text.append(f"| {s['nx']} | {r['delta_fixed']:.15g} | {r['delta_adjusted']:.15g} | {c['bounds']['adjusted'][0]:.15g} | {c['bounds']['fixed'][1]:.15g} |")
    text+=['','The old corner is (lambda,d)=(0.25,0.45). The additional common nested rectangle is [0,0.125] by [0.4,0.425]. All 120 spatial class values, both menus, all old corners, the center, and the full bisection traces are retained. The grid protocols are not a proved diffusion limit.','',
      '## New theory and validation','',
      f"The uniform cardinal-tilt family has lower bound {primitive['uniform_lower_bound']:.16g} for |a| <= 0.25. The adverse examples at a=1 and a=2 remain in the output.",
      f"The dynamic mechanism analysis contains {mechanisms['total_class_solves']} class solves. Its maximum direct/feature reconstruction discrepancy is {mechanisms['max_replay_error']:.16g}.",
      f"The independent streaming audit contains {validation['models']} models, {validation['class_recursions']} class recursions, and {validation['parameter_value_checks']} point comparisons; maximum count replay error is {validation['max_count_error']:.16g} and minimum chord-minus-count coefficient is {validation['minimum_order']:.16g}.",
      '',f"Protected historical file hashes checked: {len(protected)}. Authored-source hashes checked: {len(inventory)}.",
      '', 'These checks support the deposited implementations, not a journal decision, a neural-dominance claim, an empirical causal identification theorem, or an unconditional continuous-state portfolio sign.']
    manifest=dict(review_parent='bb9144d3da7be059af7452dababb9fa5763b335c',prior_complete_manuscript='fbfbf9025ef9069d1f82af0887c2cd5ccfb8ef17',source_commit=os.environ.get('NBO_SOURCE_SHA','local-execution'),protected_files=len(protected),authored_files=len(inventory),evidence_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.glob('*')) if p.is_file()},pdfs={})
    if not precompile:
        for name in ('ECTA_R8','SUPP_R8'):
            p=ROOT/'build-r8'/f'{name}.pdf';assert p.exists()
            log=(ROOT/'build-r8'/f'{name}.log').read_text(errors='replace')
            bad=['There were undefined references','There were undefined citations','multiply defined','! LaTeX Error','! Emergency stop']
            for token in bad:assert token not in log,(name,token)
            shutil.copy2(p,REV/p.name)
            manifest['pdfs'][p.name]=dict(sha256=sha(p),pdfinfo=subprocess.check_output(['pdfinfo',str(p)],text=True))
        text+=['','## Complete manuscript build','','Both complete PDFs compiled without unresolved references or citations. The PDF hashes and page counts are recorded in build_manifest.json. Visual inspection is recorded separately after rendering.']
    (REV/'execution_summary.md').write_text('\n'.join(text)+'\n')
    (REV/'build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('R8 audit passed',len(protected),'protected files;',len(inventory),'authored files;', 'precompile' if precompile else 'complete PDFs')
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--precompile',action='store_true');args=a.parse_args();main(args.precompile)
