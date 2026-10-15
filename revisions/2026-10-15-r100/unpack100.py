"""Extract the complete frozen R100 Python source and verify every file hash."""
import hashlib,json,tarfile
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'SOURCE_FREEZE100.json').read_text())
archive=root/'SOURCE100_PREFLIGHT.tar.xz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['archive_sha256']
with tarfile.open(archive,'r:xz') as src:
    for member in src.getmembers():
        if not member.isfile() or member.name not in manifest['source_files']:
            raise ValueError('unexpected archive member')
        data=src.extractfile(member).read()
        assert hashlib.sha256(data).hexdigest()==manifest['source_files'][member.name]
        dest=root/member.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
print('R100 frozen source extracted and verified')
