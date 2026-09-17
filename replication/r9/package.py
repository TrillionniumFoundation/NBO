"""Check and assemble the complete R9 reading package after an actual build."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];REV=ROOT/'revisions/2026-09-17-r9-participation-permissions';OUT=ROOT/'replication/r9/output'
BASE='8c20474bca5b7388f5ba4640ec165f1ad8f5e91a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def command(*args):return subprocess.check_output(args,cwd=ROOT,stderr=subprocess.DEVNULL,text=True).strip()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--build',default='build-r9');args=ap.parse_args();build=Path(args.build)
    if not build.is_absolute():build=ROOT/build
    sys.path.insert(0,str(ROOT/'replication/r9'));from run import verify_inputs
    inputs=verify_inputs();inventory=load(REV/'source_inventory.json')
    for name,digest in inventory.items():assert sha(ROOT/name)==digest,('authored source changed',name)
    idx=(ROOT/'REVISION_INDEX.md').read_text();old=idx[idx.index('# Current complete revision: R8'):]
    assert hashlib.sha256(old.encode()).hexdigest()==(REV/'historical_index.sha256').read_text().strip()
    oldpath='revisions/2026-09-17-r8-full-response/paper/';newpath='revisions/2026-09-17-r9-participation-permissions/paper/'
    aliases={newpath+x:oldpath+x for x in ('preamble','01_introduction','05d_decision_evidence','07_conclusion')}
    wrappers={}
    for name in ('ECTA','SUPP'):
        oldin=re.findall(r'\\input\{([^}]+)\}',(ROOT/f'{name}_R8.tex').read_text());newin=re.findall(r'\\input\{([^}]+)\}',(ROOT/f'{name}_R9.tex').read_text())
        normalized=[aliases.get(x,x) for x in newin]
        assert set(oldin)<=set(normalized)
        wrappers[name]=dict(inherited_inputs=len(oldin),new_inputs=len(newin),all_inherited_inputs_retained=True)
    git_audit={'mode':'local artifact checkout; pinned-input checks only'}
    try:
        head=command('git','rev-parse','HEAD');changed=command('git','diff','--name-only',BASE,'--').splitlines()
        allowed=lambda x:x in ('ECTA_R9.tex','SUPP_R9.tex','REVISION_INDEX.md','.github/workflows/revision-r9-participation.yml') or x.startswith(('replication/r9/','revisions/2026-09-17-r9-participation-permissions/'))
        assert all(allowed(x) for x in changed),changed
        git_audit=dict(mode='git diff against reviewed baseline',source_commit=head,baseline=BASE,changed_paths=changed,historical_scientific_paths_changed=[])
    except subprocess.CalledProcessError:pass
    val=load(OUT/'validation.json');sur=load(OUT/'surrender.json');proc=load(OUT/'procurement.json');perm=load(OUT/'permissions.json')
    assert val['toy']['class_point_comparisons']==120 and val['full']['class_point_comparisons']==80
    assert val['full']['selected_control_reconstruction_error']<2e-11
    certs={n:load(OUT/(n+'.json')) for n in ('noncancellable_certificate','fee_080_certificate','fee_085_090_certificate')}
    for name,expected in zip(certs,(True,False,True)):
        assert all(x['signs_certified']==expected for x in certs[name]['methods'])
        assert certs[name]['arithmetic']['derived_per_class_bound']<1e-7
    nominal=next(x for x in sur['center'] if x['min_term']==8)
    assert abs(nominal['adjusted']['delta']-.0001967406840267527)<2e-11
    assert next(x for x in sur['center'] if x['fee']==.7 and x['min_term']==1)['relative_option']<0
    assert abs(perm['nominal_full_continuum_vs_finite_error'])<2e-11
    assert proc['positive_capacity_cost_example'][0]['principal_surplus']>0 and proc['positive_capacity_cost_example'][1]['principal_surplus']<0
    pdfs={}
    for name in ('ECTA_R9','SUPP_R9'):
        log=(build/(name+'.log')).read_text(errors='replace')
        bad=[x for x in ('Overfull \\hbox','Overfull \\vbox','There were undefined references','multiply defined','LaTeX Error') if x in log]
        assert not bad,(name,bad)
        pdf=build/(name+'.pdf');info=command('pdfinfo',str(pdf));pages=int(re.search(r'Pages:\s+(\d+)',info).group(1));assert pages>=(55 if name=='ECTA_R9' else 33)
        text=command('pdftotext',str(pdf),'-').lower();assert 'participation' in text and 'surrender' in text
        shutil.copy2(pdf,REV/pdf.name);shutil.copy2(build/(name+'.log'),REV/(name+'.build.log'))
        pdfs[name]=dict(path=str((REV/pdf.name).relative_to(ROOT)),pages=pages,sha256=sha(pdf),overfull_boxes=0,undefined_reference_warnings=0)
    outputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.glob('*')) if p.is_file() and p.name!='probe.json'}
    manifest=dict(review_baseline=BASE,inputs=inputs,source_inventory_sha256=sha(REV/'source_inventory.json'),wrappers=wrappers,pdfs=pdfs,git_preservation=git_audit,executed_outputs=outputs,generated_tables={str(p.relative_to(ROOT)):sha(p) for p in sorted((REV/'paper').glob('table_r9_*.tex'))},generated_numbers_sha256=sha(REV/'paper/r9_numbers.tex'),scope='Compiled and checked after an actual numerical execution. Stored-array arithmetic is not a constructor/diffusion enclosure.')
    dump(REV/'build_manifest.json',manifest)
    for source in ('research_transcript.txt','validation_transcript.txt','main_build.txt','supplement_build.txt'):
        p=build/source
        if p.exists():shutil.copy2(p,REV/source)
    lines=['# Executed R9 evidence and complete manuscript build','',f"Review baseline: `{BASE}`.",f"Verified historical/numerical input entries: **{inputs['checked_files']}**.",'','## Manuscripts','']
    for n,z in pdfs.items():lines.append(f"- `{n}.pdf`: **{z['pages']} pages**; SHA-256 `{z['sha256']}`; no overfull boxes or unresolved-reference warnings.")
    lines+=['','## New executed evidence','',f"Small models: {val['toy']['random_models']} models, {val['toy']['class_point_comparisons']} class-point comparisons, 81 enumerated policies per class and point; maximum error {val['toy']['exhaustive_error']:.3g}.",f"Full-model validation: {val['full']['class_point_comparisons']} class-point comparisons; selected-control reconstruction error {val['full']['selected_control_reconstruction_error']:.3g}; polynomial replay error {val['full']['polynomial_evaluation_error']:.3g}.",'','Economic runs: 19 central fee/term specifications and 20 additional fee/contract rows, each with four class values and moments; 16 all-action supersolution checks; eight sufficient enforcement bounds; nine two-regime permission comparisons; eighteen reoptimized benefit roots.','',f"The noncancellable center participation saving is {sur['noncancellable_participation_saving']:.12f} utility-numeraire units.",f"The sufficient one-interval regional fee bound is {load(OUT/'reachable_fee.json')['sufficient_fee_bounds'][0]:.12f}, rounded upward in the manuscript.",'','## Regional certificates','']
    for name,c in certs.items():
        lines.append(f"`{name}`: "+'; '.join(f"{m['method']}: adjusted {m['bounds']['adjusted']}, no-adjustment {m['bounds']['no_adjustment']}, both signs = {m['signs_certified']}" for m in c['methods']))
    lines+=['','The negative intermediate-fee relative option, failed fee-0.80 region and adverse corner, free surrender, and both adverse initial-permission extensions are retained. The fee-0.85-to-0.90 certificate uses the original law/benefit rectangle.','', '## Preservation and target boundary','', 'Every inherited main/supplement input is retained, with the four R9 integration copies mapped to their R8 origins. The previous active index remains unchanged as a suffix. The git preservation record, when built on GitHub, additionally checks the entire diff against the reviewed baseline.','', 'These runs do not retrain a network, rerun historical fine settlement grids, establish an optimal contract-design result, enclose the exact transition constructor, certify global uniqueness of benefit roots, or transfer a sign to the diffusion. Numerical targets and assumptions are stated in the paper, response, and replication README. The source inventory and output hashes identify this actual execution; timing and environment fields can differ across executions.','']
    (REV/'execution_summary.md').write_text('\n'.join(lines));print(json.dumps(dict(pdfs=pdfs,validation=val,protected=inputs['checked_files']),indent=2))
if __name__=='__main__':main()
