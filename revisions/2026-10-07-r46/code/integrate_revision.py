"""One-time R46 integration. The resulting ordinary sources are committed.

Frozen study code and outcomes are never edited; the final build needs no patch,
artifact download, or capsule decode. All replacements are guarded.
"""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[1]


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError('Expected exactly one integration anchor: '+repr(old))
    return text.replace(old, new, 1)


def main():
    p = R/'code/build.py'
    source = p.read_text()
    if 'integration_tests_scope' in source:
        raise RuntimeError('Integration already applied; run code/build.py directly')
    (R/'audit').mkdir(exist_ok=True)
    (R/'audit/INHERITED_BUILD.py.txt').write_text(source)
    s = replace_once(source, '    preservation={}\n',
                    "    run([sys.executable,str(R/'code/audit.py')],R/'audit/aggregate.log')\n    preservation={}\n")
    s = replace_once(s, "    run([sys.executable,str(R/'code/audit.py')],R/'audit/aggregate.log',env=env)\n", '')
    bs = chr(92)
    main_old = repr(bs+'input{sections/witness}'+'\n\n'+bs+'section{Economic applications and conclusion}')
    main_new = repr(bs+'input{sections/witness}'+'\n'+bs+'input{sections/feasible-witness}'+'\n\n'+bs+'section{Economic applications and conclusion}')
    supp_old = repr(bs+'input{sections/witness-proof}'+'\n'+bs+'bibliographystyle{ecta-fullname}')
    supp_new = repr(bs+'input{sections/witness-proof}'+'\n'+bs+'input{sections/feasible-proof}'+'\n'+bs+'bibliographystyle{ecta-fullname}')
    s = replace_once(s, main_old, main_new)
    s = replace_once(s, supp_old, supp_new)
    extra = """    text=run([sys.executable,'-m','unittest','discover','-s',str(R/'code'),'-p','test_feasible.py','-v'],R/'audit/tests-feasible.log',env=env)
    match=re.search(r'Ran ([0-9]+) tests?',text);assert match and int(match[1])==8
    tests['feasible_transport']={'tests':8,'success':True,'mode':'independent exact rational checks; not a new performance catalogue'}
"""
    s = replace_once(s, "    body=subprocess.check_output(['pandoc'", extra+"    body=subprocess.check_output(['pandoc'")
    s = replace_once(s, "'publication_source_commit':os.environ", "'integration_date':'2026-10-08','integration_tests_scope':'feasible state-dependent witness transport',\n           'publication_source_commit':os.environ")
    s = replace_once(s, 'Exact witness compilation and an explicit numerical-selection allowance make that guarantee executable.',
                    'Exact witness compilation and an explicit numerical-selection allowance make that guarantee executable. Feasible-witness transport extends the construction to endogenous action constraints with an explicit repair budget.')
    p.write_text(s)
    for name in ('README.md','response.md'):
        q = R/name
        text = q.read_text()
        (R/'audit'/('PRE_INTEGRATION_'+name)).write_text(text)
        text = text.replace('7 October 2026.', '8 October 2026.', 1)
        text = text.replace('revision/econometrica-nbo-r46-review-ready-2026-10-07',
                            'revision/econometrica-nbo-r46-review-ready-2026-10-08')
        if name == 'README.md':
            text += '\n## Integrated state-dependent construction\n\nThe feasible-witness transport theorem extends the same neural construction to nonempty compact Hausdorff-Lipschitz action correspondences. Feasible node nets and measurable repair maps have explicit work and displacement allowances. A capacity-constrained two-state example and eight independent rational tests supplement the proof; they are not a new performance catalogue. The original 36 services and all prior evidence remain unchanged. The complete build now runs 49 tests.\n'
        else:
            text += '\n## V. State-dependent feasibility and final integration\n\nThe added main section, *State-dependent constraints and feasible witnesses*, and its proof supplement address the constructive gap between the original feasible correspondence and the common-action backend. Under a Hausdorff-Lipschitz modulus, feasible-pair primitive moduli, effective node-specific action nets and feasible Borel repairs, the theorem constructs the same min-plus ReLU continuation and a repaired feasible policy. The policy loss charges action-net error, query error, state coverage and repair displacement. It reduces to the common-action witness theorem when constraint variation and repair error vanish. A capacity-constrained two-state example has an exact clipping repair. Eight independent exact rational tests check its admissibility and bound formulas; the analytic proof establishes the all-state result. This is additional mathematical scope, not evidence of high-dimensional comparative speed or a calibrated application.\n\nThe inherited R46 publication attempt 37626921466 stopped because its label-preservation traversal preceded generation of the tables it traversed. We generate and audit the actual tables first; no missing input, test, or label check is waived. A separate source branch holds the integration, and only a successful complete build is promoted to the new review-ready branch dated 8 October 2026. The final build runs 49 tests, preserves the old 36-service/216-rung catalogue and all earlier result paths, and includes the complete latest R43 report. The former failed run remains a failed run.\n'
        q.write_text(text)
    report = {'integration_date':'2026-10-08','staging_parent':'91f0ec98e963f2d2ea537607bbfe7560ed5f9eb8',
              'inherited_publication_run':37626921466,
              'old_build_sha256':hashlib.sha256(source.encode()).hexdigest(),
              'new_build_sha256':hashlib.sha256(s.encode()).hexdigest(),
              'scientific_catalogue_changed':False,
              'new_theory':'feasible-witness transport for state-dependent constraints',
              'new_exact_tests':8,
              'build_repair':'Generate and audit tables before checking all transitive LaTeX labels; no gate skipped'}
    (R/'audit/INTEGRATION.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    main()
