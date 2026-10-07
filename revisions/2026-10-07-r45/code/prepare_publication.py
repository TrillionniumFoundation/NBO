"""Restore retained publication inputs; never change a historical repository file."""
from pathlib import Path
import hashlib, json, sys, zipfile

R = Path(__file__).resolve().parents[1]
ARCHIVE_SHA = '5e80020a7a737fcb970e5e2c05ef8c7ad8fd103b524b4cf2ebe6110df9dacff9'
ASSEMBLER_SHA = '21893bc457b64fdb504258de3f14ebf14b393baa07849230a2ea89933b07829e'
sha = lambda data: hashlib.sha256(data).hexdigest()

def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: prepare_publication.py verified-r44-artifact.zip')
    raw = Path(sys.argv[1]).read_bytes()
    assert sha(raw) == ARCHIVE_SHA, 'R44 archive integrity failure'
    prefix = '2026-10-07-r44/evidence/2026-10-07-r41/'
    recorded = {}
    with zipfile.ZipFile(sys.argv[1]) as archive:
        for entry in archive.infolist():
            if not entry.filename.startswith(prefix) or entry.is_dir():
                continue
            relative = Path(entry.filename[len(prefix):])
            assert not relative.is_absolute() and '..' not in relative.parts
            if '__pycache__' in relative.parts or relative.suffix == '.pyc':
                continue
            assert relative.suffix.lower() not in {'.ttf','.otf','.woff','.woff2','.pfb','.pfa','.afm','.tfm'}, 'Do not distribute font files'
            content = archive.read(entry)
            target = R/'preserved/R41'/relative
            if target.exists():
                assert target.read_bytes() == content, str(target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            recorded[str(relative)] = sha(content)
    for required in ('econsocart.cls','econsocart.cfg','ecta-fullname.bst','ECTA.tex','supp.tex','applications.tex','build/ECTA.pdf','build/supp.pdf','build/applications.pdf'):
        assert required in recorded, required
    assembler = R/'code/assemble.py'
    old = assembler.read_bytes()
    assert sha(old) == ASSEMBLER_SHA
    anchor = "OLD41=OLD/'evidence/2026-10-07-r41'\n"
    replacement = anchor + "if not (OLD41/'econsocart.cls').is_file(): OLD41=R/'preserved/R41'\n"
    assert old.decode().count(anchor) == 1
    new = old.decode().replace(anchor, replacement).encode()
    assembler.write_bytes(new)
    correction = {
        'failed_publication_run': 37615450133,
        'cause': 'R44 repository checkout omitted retained R41 publication dependencies present in the pinned R44 artifact.',
        'repair': 'Materialize byte-identical R41 companions inside R45 and use them as the assembler fallback. Historical repository paths, scientific source, services, targets and paper text are unchanged.',
        'artifact_id': 11475101500,
        'artifact_sha256': ARCHIVE_SHA,
        'assembler_before_sha256': sha(old),
        'assembler_after_sha256': sha(new),
        'retained_companion_sha256': recorded,
        'future_reproduction': 'The final revision tracks all companions and template inputs. Its documented build needs no artifact download.'
    }
    (R/'audit/PUBLICATION_BUILD_CORRECTION.json').write_text(json.dumps(correction, indent=2, sort_keys=True)+'\n')
    disclosure = R/'audit/DEVELOPMENT_DISCLOSURE.md'
    disclosure.write_text(disclosure.read_text()+'\nThe first complete-source remote publication build (37615450133) failed before manuscript assembly because the R44 repository checkout omitted retained R41 template inputs present in its pinned publication artifact. PUBLICATION_BUILD_CORRECTION.json records restoration of byte-identical companions inside R45 and the single assembler fallback correction. The final revision explicitly tracks these dependencies, so subsequent builds do not require the expiring artifact. No historical source, scientific checkpoint, target, theorem text, or assembled main/supplement source is changed by this build repair.\n')
    print(json.dumps({'restored_companion_files':len(recorded),'assembler_sha256':sha(new)}))

if __name__ == '__main__':
    main()
