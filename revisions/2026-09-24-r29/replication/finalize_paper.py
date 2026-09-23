"""Canonical R29 document generation, including final bibliography ordering."""
from __future__ import annotations
import hashlib, importlib.util, json, re, runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
REV=ROOT/'revisions/2026-09-24-r29'
ORDER=['AudetDennis2006','BrownSmith2014','BrownSmithSun2010','BrummScheidegger2017','ByrdEtAl1995','HureEtAl2021','JacotEtAl2018','Judd1998','KingmaBa2015','KoldaLewisTorczon2003','KoldaLewisTorczon2006','KushnerDupuis2001','MunosSzepesvari2008','Rump2010','SirignanoSpiliopoulos2018','Vicente2010']

def main():
    runpy.run_path(str(REV/'replication/prepare_response.py'),run_name='__main__')
    spec=importlib.util.spec_from_file_location('materialize29',REV/'replication/materialize.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.materialize()
    p=REV/'paper/references.tex';original=p.read_text()
    body=original.split(r'\end{thebibliography}',1)[0]
    parts=re.split(r'(?=\\bibitem\[)',body)
    entries={}
    for block in parts[1:]:
        key=re.search(r'\]\{([^}]+)\}',block).group(1)
        if key in entries:raise AssertionError('Repeated bibliography entry: '+key)
        entries[key]=block.strip()
    if set(entries)!=set(ORDER):raise AssertionError('Bibliography coverage changed')
    p.write_text(parts[0].rstrip()+'\n'+'\n\n'.join(entries[key] for key in ORDER)+'\n\n'+r'\end{thebibliography}'+'\n')
    readme=ROOT/'R29_REVIEW.md'
    text=readme.read_text().replace('python revisions/2026-09-24-r29/replication/materialize.py','python revisions/2026-09-24-r29/replication/finalize_paper.py')
    readme.write_text(text)
    mp=REV/'REVISION_MANIFEST.json';manifest=json.loads(mp.read_text())
    manifest['source_sha256']={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in sorted((REV/'paper').glob('*.tex'))}
    manifest['bibliography_entries_preserved']=len(entries)
    manifest['canonical_document_generator']='revisions/2026-09-24-r29/replication/finalize_paper.py'
    mp.write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
