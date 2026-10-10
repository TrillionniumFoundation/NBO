"""Ordinary author-source clarification before the final publication binding.

Only unfrozen publication files change. The measured science and its source
freeze are preserved byte for byte. Subsequent builds use these ordinary
committed sources; this authoring step is not part of numerical verification.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]

def main():
    marker=R/'audit/AUTHOR_TIMING_CLARIFICATION62.json'
    if marker.exists():print('Complete-work author clarification already present.');return
    if (R/'audit/SOURCE_BINDING62.json').exists():raise RuntimeError('A previous final publication binding must not be silently replaced')
    import science62
    fz=science62.verify();changes=[]
    def edit(name,pairs):
        path=R/name;old=path.read_text();new=old
        for before,after in pairs:
            if before not in new:raise AssertionError('Expected author text missing in '+name+': '+before[:90])
            new=new.replace(before,after,1)
        path.write_text(new);changes.append(dict(file=name,before_sha256=hashlib.sha256(old.encode()).hexdigest(),after_sha256=hashlib.sha256(new.encode()).hexdigest()))
    paragraph=r'''\paragraph{Closing the measured production boundary.}
The frozen per-method release field sums measured core components. The publication audit found that common-certificate bookkeeping, some output records and the final actor-file serialization were outside those individual clocks. We preserve the field unchanged as a component sum, rather than calling it an isolated complete runtime. The recorded outer production step spans 466 seconds at whole-second timestamp resolution; a transparent two-second reserve gives a 468-second accounting envelope. Subtracting the nonoverlapping component clocks leaves a shared unallocated residual. The table charges that entire residual to every method, in addition to its own component sum. These are conservative complete-production charges, not separately observed method runtimes or statistical timing confidence bounds. Remote publication, document production and replay have their own receipts. This correction changes neither a scientific result nor a measured service clock.
'''
    edit('sections/study62.tex',[(r'\input{tables/release-work62}',r'\input{tables/release-work62}'+'\n'+paragraph),
        ('Minimizing recorded complete-catalogue work among eligible methods defines the finite release frontier.', 'Minimizing the conservative complete-production charge among eligible methods defines the finite release frontier.'),
        ('The timing evidence is descriptive for the recorded host and arithmetic engine.', 'The component timings are descriptive for the recorded host and arithmetic engine; the shared-residual charge is an explicitly stated accounting convention.')])
    edit('sections/supp62.tex',[(r'\section{Combined resource and reliability account}\label{supp:resources62}',r'\section{Combined resource and reliability account}\label{supp:resources62}'+'\n'+paragraph)])
    note='''The publication audit also closes a boundary omission in the frozen component-sum field. Common-certificate bookkeeping, some JSON outputs and final actor-file serialization were not separately timed inside that sum. The original outer production step is recorded as 466 seconds at whole-second resolution; a transparent two-second reserve gives a 468-second accounting envelope. We sum the nonoverlapping measured components and charge the entire remaining shared residual to each method. Both the original component sum and the corrected conservative charge are retained. This is a postproduction accounting correction, not a scientific rerun, an isolated method timing, a probabilistic clock bound, or a change to the prospective accuracy targets. Remote publication, document production and replay retain separate receipts.\n\n'''
    for name in ('response62.md','response.md'):
        edit(name,[('## M8: Bit complexity and its role in the full algorithm',note+'## M8: Bit complexity and its role in the full algorithm')])
    edit('code/tables62.py',[
        ('Recorded work through complete catalogue release','Conservative complete-production work charges'),
        ('This is measured catalogue-release work, not an unexecuted minimal stopping schedule. Times are one-host descriptive measurements; frequency was not controlled.', 'The entire unallocated outer-production residual is additionally charged to every method. These are conservative complete-production charges, not isolated measured method runtimes or an unexecuted minimal stopping schedule. Frequency was not controlled.')])
    if science62.verify()!=fz:raise AssertionError('Author clarification changed frozen science')
    marker.write_text(json.dumps(dict(status='ordinary_sources_clarified',source_freeze_sha256=fz,changes=changes,scope='Postproduction disclosure and conservative residual charging; immutable scientific sources, outputs and clocks are unchanged.'),sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(status='clarified',files=len(changes),source_freeze_sha256=fz)),flush=True)
if __name__=='__main__':main()
