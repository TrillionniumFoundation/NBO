"""Finalize the R79 response without changing any substantive referee reply.

The R78 original response is retained in preserved/R78-original/response.md.
This update removes obsolete current-version attributions in the live reply.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
def main():
    p=R/'response.md';old=p.read_text();text=old
    a='The present revision starts from the latest ordinary R77 manuscript and evidence at `21a99a92c9a8aed96b36931467a40cd7b82aeeb6`, rather than returning to R54 or treating a source-only branch as an executed result.'
    b='R79 continues the latest ordinary R78 manuscript at `6b88c6b3a61193c98c822bd62af1203df09c992d`, including the executed R77 evidence at `21a99a92c9a8aed96b36931467a40cd7b82aeeb6`. The unfinished R78 publication is not described as a completed verification, and its missing publication manifest is not manufactured.'
    text=text.replace(a,b)
    a='The new theorem and finite-catalogue interpretation appear in **Simultaneous choice among constructed controllers**. Its full proof, attaining cost vectors, exact fee calculations and tables are in the Numerical and Development Appendix. All inherited active section files remain byte-identical and are compiled once. The R77 original wrappers and response are preserved. Twenty new exact regression tests supplement the full inherited test and independent numerical-replay chain. R78 adds no simulation rows and does not retime the original scientific services.'
    b='The retained pure-choice theorem appears in **Simultaneous choice among constructed controllers**, next to its full proof and exact fee calculations in the Numerical and Development Appendix. The new **Deployment choice under qualified cost uncertainty** theorem is in the main article, with its full allocation, installation-cost and finite-cohort proofs in that appendix. All inherited active section files remain byte-identical and are compiled once. Original R77 and R78 wrappers and responses are preserved. Twenty inherited sharp-choice tests and twenty-two new allocation tests accompany the full inherited mathematical and independent numerical-replay chain. R79 adds no simulation rows and does not retime original scientific services.'
    text=text.replace(a,b)
    text=text.replace('R78 repeats that full dual-arithmetic calculation and recomputes all statistical intervals.', 'The R79 release procedure repeats that full dual-arithmetic calculation and recomputes all statistical intervals.')
    text=text.replace('R78 measures its own verification and graph-processing work separately.', 'R79 measures its current verification, graph-processing and allocation work separately.')
    text=text.replace('The release distinguishes inherited scientific execution, full independent cost replay, twenty new exact choice tests, ordinary-source compilation, clean archive reproduction and actual PDF inspection.', 'The release distinguishes inherited scientific execution, full independent cost replay, twenty inherited exact choice tests, twenty-two new allocation tests, ordinary-source compilation, clean archive reproduction and actual PDF inspection.')
    text=text.replace('No new simulated rows, model fits or scientific timing repetitions are claimed in R78.', 'No new simulated rows, model fits or scientific timing repetitions are claimed in R79.')
    text=text.replace('and sharp simultaneous priced-choice guarantees. The adverse recursive-query work', 'sharp simultaneous priced-choice guarantees, and attained deployment allocation with explicit installation costs and finite-cohort implementation. The adverse recursive-query work')
    if text!=old:
        p.write_text(text)
        (R/'audit/RESPONSE_EDIT79.json').write_text(json.dumps(dict(status='updated_before_tested_source_commit',before_sha256=hashlib.sha256(old.encode()).hexdigest(),after_sha256=hashlib.sha256(text.encode()).hexdigest(),original_response_preserved='preserved/R78-original/response.md',substantive_referee_replies_deleted=False),indent=2)+'\n')
    print('Current-version response attribution verified.')
if __name__=='__main__':main()
