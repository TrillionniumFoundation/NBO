"""Package actual built PDFs and validated evidence; absent science is an error."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2];REV=ROOT/'revisions/2026-09-18-r11-dynamic-contract';OUT=ROOT/'replication/r11/output'
PARENT='30548ad06852cc0a447dedf1e63cc9e7f79f6c06'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((OUT/(n+'.json')).read_text())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--build',default='.');args=ap.parse_args();build=ROOT/args.build
    assert load('independent_validation')['all_passed']
    records={}
    for stem in ('ECTA_R11','SUPP_R11'):
        pdf=build/(stem+'.pdf');log=build/(stem+'.log');assert pdf.is_file() and log.is_file()
        text=log.read_text(errors='replace')
        assert not re.search(r'(undefined references|undefined citations|Reference .* undefined|Citation .* undefined|Overfull \\[hv]box)',text),stem
        assert '! ' not in text,stem
        info=subprocess.check_output(['pdfinfo',str(pdf)],text=True)
        pages=int(re.search(r'Pages:\s+(\d+)',info)[1]);assert pages>=(70 if stem.startswith('ECTA') else 42)
        ptext=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True)
        assert 'Revision R11' in ptext and 'Dynamic' in ptext
        shutil.copy2(pdf,REV/pdf.name);shutil.copy2(log,REV/(stem+'_build.log'))
        records[stem]={'pages':pages,'pdf_sha256':sha(pdf),'undefined_references':False,'overfull_boxes':False,
                       'benign_warnings':[x for x in text.splitlines() if 'Warning:' in x]}
    preservation={'parent':PARENT,'verified_by':'local archive source comparison recorded separately'}
    if (ROOT/'.git').is_dir():
        listing=subprocess.check_output(['git','ls-tree','-r',PARENT],cwd=ROOT,text=True)
        unchanged=[]
        for line in listing.splitlines():
            meta,path=line.split('\t');blob=meta.split()[2]
            if path=='REVISION_INDEX.md':
                old=subprocess.check_output(['git','show',PARENT+':'+path],cwd=ROOT)
                assert (ROOT/path).read_bytes().endswith(old)
            else:
                got=subprocess.check_output(['git','hash-object','--',path],cwd=ROOT,text=True).strip()
                assert got==blob,('inherited change',path);unchanged.append(path)
        preservation={'parent':PARENT,'unchanged_inherited_files':len(unchanged),'only_modified_inherited_path':'REVISION_INDEX.md (prior contents retained verbatim)'}
    result={'source_commit':os.getenv('GITHUB_SHA','local-authored-source'),'documents':records,'preservation':preservation,
            'scientific_checks':load('independent_validation'),'rendering':'Compiled PDFs inspected locally with MuPDF; CI rechecks TeX logs and PDF extraction.'}
    (REV/'build_report.json').write_text(json.dumps(result,indent=2)+'\n')
    a=load('chord_certificate');d=load('dominance');s=load('stress');w=load('work_account');v=load('validation')
    summary=f'''# Executed R11 evidence

Source commit of this execution: `{result['source_commit']}`. Exact primitive array hashes are in `replication/r11/output/array_manifest.json`. The source tree, not the branch name, defines this run.

Both signed chord and count-information methods certify the same five-dimensional box: `{a['box']}`. Bounds include the charged 2e-7 per difference:

| Comparison | Lower bound | Upper bound |
|---|---:|---:|
'''
    for k,bd in a['bounds'].items():summary+=f'| {k} | {bd[0]:.16g} | {bd[1]:.16g} |\n'
    summary+=f'''
All eight dates pass the signed transport test on complete feasible reachable support. The largest negative-minus-zero upper bound is {max(z['negative_minus_zero_upper'] for z in d['dates']):.16g}, after padding. There are {sum(z['tested_pairs'] for z in d['dates']):,} checked action pairs across the support tube; these are not independent parameter samples.

Nine directional contracts and the alternative initial-state witness were reoptimized. Twelve joint fee/permission cases were reoptimized; the maximum discrepancy from the rounded referee values is {s['maximum_report_replay_error']:.5g}, and the maximum independent selected-control discrepancy is {s['maximum_selected_direct_error']:.5g}. Both adjustment regimes implement the noncancellable values at all eight term alternatives with the recorded strict fee perturbations. Six new interior contracts validate, but do not prove, the regional bounds.

The derived stored-array arithmetic bound per compared value is {v['arithmetic']['derived_per_class_bound']:.16g}, below the charged 1e-7. This is not an enclosure of the real-arithmetic constructor or a diffusion. The displayed active gain implies that an additional per-initial-value target error below 1.7354e-5 would preserve all three value signs; such an error has not been estimated here. Directional transfer needs its own statewise bounds.

## Matched decision workload

Common construction: {w['constructor_seconds']:.6f} seconds. Common endpoint bill: {w['shared_endpoint_seconds']:.6f} seconds for {w['shared_endpoint_solves']} continuation solves. Common new validation: {w['validation_seconds']:.6f} seconds. Chord incremental work: {w['chord_nonendpoint_seconds']:.6f} seconds; count incremental work: {w['count_nonendpoint_seconds']:.6f} seconds. Matched totals are {w['chord_matched_total_seconds']:.6f} and {w['count_matched_total_seconds']:.6f} seconds. These are this execution's measurements, not universal complexity or neural-superiority claims. Full-script time is {w['full_script_seconds']:.6f} seconds. Kernel payload is distinct from unmeasured process peak memory.

The complete main paper has {records['ECTA_R11']['pages']} pages and the supplement {records['SUPP_R11']['pages']} pages. Both compiled with no unresolved references/citations or overfull boxes. Preserved class-level anchor/font warnings are recorded in the build report.
'''
    (REV/'execution_summary.md').write_text(summary)
    paths=[ROOT/'ECTA_R11.tex',ROOT/'SUPP_R11.tex',ROOT/'REVISION_INDEX.md']
    paths+=list((ROOT/'replication/r11').rglob('*'))+list(REV.rglob('*'))
    paths=[p for p in paths if p.is_file() and '__pycache__' not in p.parts and p.name not in ('manifest.json','revision_source.tar.xz')]
    manifest={'source_commit':result['source_commit'],'review_parent':PARENT,'files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}}
    (REV/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
