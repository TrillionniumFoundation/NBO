"""Preserve safe repository-internal symlinks in an offline Git archive rebuild."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'code/clean48.py'
old_hash='aacae1ab9079b1442a1db38467940a4456662fd21375b746b2815356b5538fd9'
assert sha(p)==old_hash,'Unexpected clean-rebuild source; no patch applied'
original=p.read_text()
old='''        with tarfile.open(archive) as tf:
            for m in tf.getmembers():
                p=Path(m.name);assert not p.is_absolute() and '..' not in p.parts
                assert not m.issym() and not m.islnk(),m.name
            tf.extractall(work,filter='data')
'''
new='''        # A Git archive legitimately retains historical relative symlinks.
        # Permit only repository-internal links; never allow absolute paths,
        # archive-root escape, special files or hard links.
        links=[]
        with tarfile.open(archive) as z:
            for m in z.getmembers():
                assert not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
                assert m.isfile() or m.isdir() or m.issym(),m.name
                if m.issym():
                    target=Path(m.linkname)
                    assert not target.is_absolute(),m.name
                    resolved=Path(os.path.normpath(str(work/Path(m.name).parent/target)))
                    assert resolved.is_relative_to(work),m.name
                    links.append({'path':m.name,'target':m.linkname})
            z.extractall(work,filter='data')
        for link in links:
            # Resolve chains as well as individual lexical targets. Dangling
            # internal aliases remain faithful Git-checkout objects.
            resolved=(work/link['path']).resolve(strict=False)
            assert resolved.is_relative_to(work),link['path']
        print(json.dumps({'archived_internal_symlinks':links}),flush=True)
'''
assert original.count(old)==1
text=original.replace(old,new)
needle="'network_or_expiring_artifact_required':False,'scientific_execution_repeated':False"
assert text.count(needle)==1
text=text.replace(needle,"'network_or_expiring_artifact_required':False,'internal_symlinks':links,'scientific_execution_repeated':False")
(R/'audit').mkdir(exist_ok=True)
(R/'audit/clean48-before-symlink-fix.py').write_text(original)
manifest=R/'publication/PAPER_SOURCE_SHA256.json'
(R/'audit/PUBLICATION_INPUTS_BEFORE_CLEAN_ARCHIVE_FIX.json').write_bytes(manifest.read_bytes())
p.write_text(text)
disclosure=R/'DEVELOPMENT_DISCLOSURE.md'
disclosure.write_text(disclosure.read_text()+'''\n\n## Publication-only clean-archive correction\n\nPublication run 37718102816 compiled the 67-page article, 61-page supplement and 13-page response, reconstructed the frozen evidence and passed all 96 regressions. Its clean Git-archive check then stopped because the original check rejected every symbolic link. The historical repository contains the relative alias `revisions/2026-10-07-r44/evidence/2026-10-07-r41 -> ../../2026-10-07-r41`; the earlier local artifact restoration had materialized this alias as ordinary files and did not expose the distinction. No review-ready branch was pushed by that failed run.\n\nThe corrected archive check retains only safe, relative repository-internal symbolic links, validates each lexical target and every resolved link chain, uses Python's data extraction filter, and still rejects archive-root escape, absolute links, special files and hard links. The resulting archive is rebuilt with all 96 tests, ordinary-source comparisons, manuscript compilation and scientific hash checks unchanged. Link identities are included in the clean-rebuild audit. The original cleaner and publication input manifest are retained in the audit directory. No mathematical text, experimental protocol, frozen scientific source, candidate policy, result, timing observation or target is changed by this publication-only correction. The failed run remains failed.\n''')
audit={'failed_publication_run':37718102816,'failure':'Blanket symbolic-link rejection in clean Git-archive extraction','old_cleaner_sha256':old_hash,'new_cleaner_sha256':sha(p),'historical_files_modified':False,'scientific_sources_modified':False,'experimental_results_modified':False,'manuscript_text_modified':False,'security':'Relative internal symbolic links only; lexical and resolved-chain root confinement plus standard-library data filter; no absolute links, special files or hard links','all_original_gates_retained':True}
(R/'audit/CLEAN_ARCHIVE_CORRECTION.json').write_text(json.dumps(audit,indent=2)+'\n')
m=json.loads(manifest.read_text())
for n in ('code/clean48.py','code/repair_clean48.py','DEVELOPMENT_DISCLOSURE.md','audit/CLEAN_ARCHIVE_CORRECTION.json','audit/clean48-before-symlink-fix.py','audit/PUBLICATION_INPUTS_BEFORE_CLEAN_ARCHIVE_FIX.json'):
    m['inputs'][n]=sha(R/n)
m['publication_only_correction']='audit/CLEAN_ARCHIVE_CORRECTION.json'
manifest.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2),flush=True)
