"""Publish additive R43 documents only after numerical and preservation checks."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
import fitz
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
BASE='7d54e728a9732979605697895e3a07444dc1e528'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    check=json.loads((R/'results/publication_rechecks.json').read_text());assert check['passed'] and check['objects']==41 and check['all_restart_checks']==6648
    assert all(x['rejected'] for x in json.loads((R/'results/mutations.json').read_text()))
    assert all(x['passed'] for x in json.loads((R/'results/unit_checks.json').read_text()))
    pdfs=[];pages={}
    for prefix in ('ECTA','SUPP','RESPONSE','COMPUTATION'):
        pdf=ROOT/(prefix+'_R43.pdf');log=(ROOT/(prefix+'_R43.log')).read_text(errors='replace')
        for bad in ('Overfull \\hbox','There were undefined references','multiply-defined labels','Citation `'):
            assert bad not in log,(pdf,bad)
        doc=fitz.open(pdf);assert len(doc)>0 and all(len(p.get_text().strip())>30 for p in doc)
        pages[pdf.name]=len(doc);pdfs.append(pdf)
    # Root navigation is the sole permitted inherited-file change and is archived.
    index=ROOT/'REVISION_INDEX.md';old=subprocess.check_output(['git','show',BASE+':REVISION_INDEX.md'],cwd=ROOT)
    hist=R/'history/REVISION_INDEX_R42.md';hist.parent.mkdir(parents=True,exist_ok=True);hist.write_bytes(old)
    index.write_text('# Current NBO revision: R43\n\n'+(R/'README.md').read_text()+'\n\nThe preceding complete index is preserved at `revisions/2026-09-25-r43/history/REVISION_INDEX_R42.md`.\n')
    (ROOT/'R43_REVIEW.md').write_text((R/'README.md').read_text())
    diff=subprocess.check_output(['git','diff',BASE,'--name-status'],cwd=ROOT,text=True)
    inherited=[]
    for line in diff.splitlines():
        status,path=line.split('\t',1)
        if status.startswith('A'):continue
        if path=='REVISION_INDEX.md':continue
        # Files absent from the R42 base are new even if they were staged earlier.
        exists=subprocess.run(['git','cat-file','-e',BASE+':'+path],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
        if exists:inherited.append(line)
    assert not inherited,inherited
    preservation=dict(base=BASE,passed=True,changed_inherited_scientific_files=inherited,navigation_exception='REVISION_INDEX.md, exact previous bytes archived',archived_index_sha256=sha(hist),diff=diff)
    (R/'results/preservation.json').write_text(json.dumps(preservation,indent=2)+'\n')
    files=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name not in ('PUBLICATION_MANIFEST.json','process.json') and not p.name.startswith('payload.')]
    files+=pdfs+[ROOT/(prefix+'_R43.tex') for prefix in ('ECTA','SUPP','RESPONSE','COMPUTATION')]+[ROOT/'R43_REVIEW.md',index]
    files=sorted(set(files));manifest=dict(revision='R43',base=BASE,checked_objects=41,all_restart_checks=6648,pages=pages,files={str(p.relative_to(ROOT)):sha(p) for p in files})
    mp=R/'PUBLICATION_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')
    # Current sources plus inherited dependencies permit compilation from the ZIP.
    archive=ROOT/'NBO_R43_review_package.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files+[mp]:z.write(p,str(p.relative_to(ROOT)))
        for p in (ROOT/'revisions/2026-09-25-r42/paper').rglob('*'):
            if p.is_file():z.write(p,str(p.relative_to(ROOT)))
        for name in ['econsocart.cls','econsocart.cfg','ecta-fullname.bst','ECTA_R42.pdf','SUPP_R42.pdf','RESPONSE_R42.pdf','COMPUTATION_R42.pdf','HISTORY_R42.pdf']:
            p=ROOT/name
            if p.exists():z.write(p,name)
    print(json.dumps(dict(passed=True,pages=pages,archive_sha256=sha(archive),files=len(files)),indent=2))
if __name__=='__main__':main()
