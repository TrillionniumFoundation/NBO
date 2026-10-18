"""Assemble R99 from the pinned, retained R97 manuscript without deleting content.

Usage: python code99/assemble99.py --source /path/to/R97
The source remains untouched. Only this R99 directory is written. New R99
files already present here are retained; inherited files are copied only if absent.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',required=True,type=Path)
    args=parser.parse_args()
    source=args.source.resolve()
    root=Path(__file__).resolve().parents[1]
    if source==root or not (source/'ECTA.tex').is_file():
        raise SystemExit('A distinct pinned R97 source directory is required')
    required=['preamble.tex','econsocart.cls','econsocart.cfg','ecta-fullname.bst','references97.bib',
              'sections/core49.tex','sections/centeredrisk92.tex','sections/continuous95.tex']
    for name in required:
        if not (source/name).is_file(): raise SystemExit('Missing inherited dependency: '+name)
    for path in sorted(source.rglob('*')):
        if not path.is_file() or path.is_symlink(): continue
        relative=path.relative_to(source)
        if relative.parts[0] in {'build','publication','__pycache__'}: continue
        dest=root/relative
        if not dest.exists():
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,dest)
    article=(source/'ECTA.tex').read_text()
    article=article.replace('new/introduction97','new/introduction99').replace('new/conclusion97','new/conclusion99')
    for name in ['sections/recursive86','sections/risk91','new/theory97']:
        article=article.replace('\\input{'+name+'}','')
    splits=[('sections/centeredrisk92.tex', r'\subsection{Exact risk occupations and safe kernel exclusion}', 'centeredrisk92'),
            ('sections/continuous95.tex', r'\subsection{A fixed-accuracy horizon account', 'continuous95')]
    split_records=[]
    for name, marker, tag in splits:
        original=(source/name).read_text()
        offset=original.index(marker)
        head,tail=original[:offset],original[offset:]
        (root/('new/'+tag+'-active99.tex')).write_text(head)
        (root/('new/'+tag+'-tail99.tex')).write_text(tail)
        if head+tail!=original: raise SystemExit('Retention split failure')
        article=article.replace(r'\input{'+name[:-4]+'}',r'\input{new/'+tag+'-active99}')
        split_records.append({'source':name,'head':'new/'+tag+'-active99.tex','tail':'new/'+tag+'-tail99.tex',
                              'sha256':hashlib.sha256(original.encode()).hexdigest()})
    article=article.replace(r'\input{new/continuous95-active99}',r'\input{new/continuous95-active99}'+'\n'+r'\input{new/action99}')
    article=article.replace('\\input{new/precision96-revised}',
                            '\\input{new/precision99-link}\n\\input{new/information99}\n\\input{new/decision99}')
    abstract=r'''This paper develops Neural Bellman Operators that construct feasible dynamic policies and qualify their loss under the original economic law. Own-future neural realization and original-owner compilation are joined to reference-centered recursive-risk bounds. We derive an action-aligned supporting certificate whose enclosure width, directional mismatch and constrained stationarity residual control the proposal's original-action gap. Prospective selection then controls rejection or bounded complete work. For convex continuations, nonuniform-law AVaR enclosures attain the deterministic information exponent two; separately quantified randomized lower bounds distinguish sound intervals from point estimation. An exactly solved purchase mechanism turns acquired oblique geometry into a strict policy-loss separation from the best additive and quadratic classes, while identical conventional geometry remains equivalent. The retained continuous-investment evidence favors quadratic least squares and shows that smaller global residual spans can increase rejection. The construction, information and empirical accounts therefore retain distinct economic meanings.'''
    article=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:'\\begin{abstract}\n'+abstract+'\n\\end{abstract}',article,flags=re.S)
    article=article.replace('\\bibliography{references97}','\\bibliography{references99}')
    (root/'ECTA.tex').write_text(article)
    supplement=(source/'supp.tex').read_text()
    moved_proofs=['sections/proofs86','sections/proofs91','new/proofs97']
    for name in moved_proofs:supplement=supplement.replace('\\input{'+name+'}','')
    supplement=supplement.replace('\\bibliographystyle{ecta-fullname}',
                                   '\\input{new/proofs99}\n\\bibliographystyle{ecta-fullname}')
    supplement=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:r'\begin{abstract}'+
        'This supplement gives complete proofs of own-future construction, reference-centered risk qualification, continuous investment and decision-scale precision. It adds the action-support and prospective-selection arguments, nonuniform-law enclosures, explicitly quantified randomized information bounds, and exact economic decision separation. Complete prior expectation, signed-risk and uniform-information proofs remain in the Development Appendix.'+
        r'\end{abstract}',supplement,flags=re.S)
    supplement=supplement.replace('\\bibliography{references97}','\\bibliography{references99}')
    (root/'supp.tex').write_text(supplement)
    appendix=(source/'appendix.tex').read_text()
    extra=['sections/recursive86','sections/risk91','new/precision96-revised','new/theory97']+moved_proofs
    appendix=appendix.replace('\\input{sections/population86}',
                             '\n'.join('\\input{'+s+'}' for s in extra)+'\n\\input{sections/population86}')
    appendix=appendix.replace(r'\input{sections/population86}',
        r'\section{Retained risk occupations and computational consequences}\label{sec:riskextensions99}'+'\n'+
        r'\input{new/centeredrisk92-tail99}'+'\n'+
        r'\section{Retained uniform horizon and vector-control account}\label{sec:horizonextensions99}'+'\n'+
        r'\input{new/continuous95-tail99}'+'\n'+r'\input{sections/population86}')
    appendix=appendix.replace(r'\appendix',r'\appendix'+'\n'+r'\renewcommand{\thetheorem}{A.\arabic{theorem}}'+'\n'+r'\renewcommand{\theequation}{A.\arabic{equation}}',1)
    appendix=appendix.replace('\\bibliography{references97}','\\bibliography{references99}')
    (root/'appendix.tex').write_text(appendix)
    (root/'references99.bib').write_text((source/'references97.bib').read_text()+'\n'+
                                       (root/'new/references99-additions.bib').read_text())
    # Preserve original active entry points and changed editorial framing byte-for-byte.
    archive=root/'retained97';archive.mkdir(exist_ok=True)
    for name in ['ECTA.tex','supp.tex','appendix.tex','new/introduction97.tex','new/conclusion97.tex','response.md','response.tex','README.md']:
        dest=archive/name;dest.parent.mkdir(parents=True,exist_ok=True)
        if (source/name).exists(): shutil.copy2(source/name,dest)
    immutable=[]
    for folder in ['sections','code','tables']:
        for path in sorted((source/folder).rglob('*')):
            if path.is_file() and path.suffix!='.pyc':
                rel=path.relative_to(source);other=root/rel
                digest=hashlib.sha256(path.read_bytes()).hexdigest()
                if not other.is_file() or hashlib.sha256(other.read_bytes()).hexdigest()!=digest:
                    raise SystemExit('Inherited source changed: '+str(rel))
                immutable.append({'path':str(rel),'sha256':digest})
    record={'baseline_commit':'f802fe64d91d9f5c1c8f86123b0fbe114e622279',
            'review_commit':'9723c6cd2cc8b3e071422f3e522d4a843946db63',
            'moved_main_sections':extra[:4],'moved_proofs':moved_proofs,'exact_section_splits':split_records,
            'unchanged_inherited_files':immutable}
    (root/'results99/retention.json').write_text(json.dumps(record,indent=2)+'\n')
    (root/'README.md').write_text((root/'README99.md').read_text())
    (root/'response.md').write_text('# R99 response to the R97 advisory report\n\nSee `response99.tex` and `build/response99.pdf` for the full point-by-point response.\nThe original R97 response is preserved in `retained97/response.md`.\n')
    print('ASSEMBLED',root,'UNCHANGED',len(immutable))

if __name__=='__main__': main()
