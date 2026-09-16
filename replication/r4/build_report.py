#!/usr/bin/env python3
"""Record actual PDF builds and source preservation, without claiming journal review."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-commit');ap.add_argument('--base',default='79a7d84be2cbbf9bd5d181599ee110540128e3b5');a=ap.parse_args();rows=[]
    rev=ROOT/'revisions/2026-09-16-r4'
    for name in ['ECTA_R4','SUPP_R4']:
        log=(ROOT/'build-r4'/f'{name}.log').read_text(errors='replace');pdf=ROOT/'build-r4'/f'{name}.pdf'
        bad=[line for line in log.splitlines() if ('undefined' in line and 'Font shape' not in line) or 'multiply defined' in line or 'Overfull \\hbox' in line or line.startswith('!')]
        assert not bad,(name,bad)
        info=subprocess.check_output(['pdfinfo',str(pdf)],text=True);pages=int(re.search(r'Pages:\s+(\d+)',info).group(1))
        target=rev/(name+'.pdf');target.write_bytes(pdf.read_bytes())
        (rev/(name+'_build.log')).write_text(log)
        rows.append(dict(manuscript=name,pages=pages,pdf_sha256=sha(target),log_sha256=sha(rev/(name+'_build.log')),unresolved_references_or_overfull_hboxes=bad))
    preserved={}
    if a.source_commit:
        for name in ['ECTA.tex','supp.tex','ECTA_R2.tex','SUPP_R2.tex','econsocart.cls','econsocart.cfg']:
            data=subprocess.check_output(['git','show',a.base+':'+name],cwd=ROOT);same=hashlib.sha256(data).hexdigest()==sha(ROOT/name);assert same,name;preserved[name]=same
    sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((rev/'paper').glob('*.tex'))}
    for name in ['ECTA_R4.tex','SUPP_R4.tex']:sources[name]=sha(ROOT/name)
    report=dict(source_commit=a.source_commit,review_base=a.base,builds=rows,manuscript_source_sha256=sources,historical_files_unchanged=preserved,
                visual_inspection='PDFs are rendered and inspected separately; this script checks compilation and byte identities only.')
    (rev/'build_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
