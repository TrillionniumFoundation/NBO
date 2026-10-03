"""Verify a pinned source transport and materialize UTF-8 files only."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'PACK_MANIFEST.json').read_text())
parts = []
for entry in manifest['parts']:
    name = entry['name']
    if PurePosixPath(name).name != name:
        raise ValueError('unsafe transport filename')
    raw = (root / name).read_bytes()
    git_sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if len(raw) != entry['chars'] or git_sha != entry['git_blob']:
        raise ValueError('transport blob mismatch: ' + name)
    parts.append(raw.strip())
compressed = base64.b64decode(b''.join(parts), validate=True)
if hashlib.sha256(compressed).hexdigest() != manifest['compressed_sha256']:
    raise ValueError('compressed SHA-256 mismatch')
raw_json = lzma.decompress(compressed)
if hashlib.sha256(raw_json).hexdigest() != manifest['json_sha256']:
    raise ValueError('source JSON SHA-256 mismatch')
sources = json.loads(raw_json)
if set(sources) != set(manifest['files']):
    raise ValueError('source file inventory mismatch')
validated = []
for name, text in sources.items():
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('unsafe source path')
    if not isinstance(text, str):
        raise TypeError('source must be UTF-8 text')
    path = root.joinpath(*relative.parts)
    if root not in path.resolve().parents:
        raise ValueError('source path escapes revision directory')
    data = text.encode('utf-8')
    if hashlib.sha256(data).hexdigest() != manifest['files'][name]:
        raise ValueError('source file SHA-256 mismatch: ' + name)
    if path.exists() and path.read_bytes() != data:
        raise FileExistsError('refusing to overwrite different source: ' + name)
    validated.append((path, data))
for path, data in validated:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
print(json.dumps({'materialized_files': len(validated), 'json_sha256': manifest['json_sha256']}))
