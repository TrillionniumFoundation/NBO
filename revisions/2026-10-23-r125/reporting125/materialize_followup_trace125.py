"""Verify/reconstruct the exact published follow-up witness gzip; no economics."""
from pathlib import Path
import hashlib, json


def materialize(root):
    root = Path(root)
    m = json.loads((root/'results125/independent-followup512_transport/TRANSPORT_SPLIT125.json').read_text())
    assert m['logical_path'] == 'results125/independent-followup512/terminal_witnesses125.jsonl.gz'
    target = root/m['logical_path']
    digest = hashlib.sha256()
    total = 0
    for part in m['parts']:
        rel = Path(part['path'])
        assert not rel.is_absolute() and '..' not in rel.parts
        h = hashlib.sha256()
        size = 0
        with (root/rel).open('rb') as f:
            for block in iter(lambda: f.read(1024*1024), b''):
                h.update(block); digest.update(block); total += len(block); size += len(block)
        assert h.hexdigest() == part['sha256'] and size == part['bytes']
    assert digest.hexdigest() == m['original_sha256'] and total == m['original_bytes']
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as g:
            for part in m['parts']:
                with (root/part['path']).open('rb') as f:
                    for block in iter(lambda: f.read(1024*1024), b''):
                        g.write(block)
    h = hashlib.sha256()
    with target.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    assert h.hexdigest() == m['original_sha256'] and target.stat().st_size == total
    return dict(path=str(target), sha256=h.hexdigest(), bytes=total,
                parts=len(m['parts']), economic_evaluations=0)


if __name__ == '__main__':
    print(json.dumps(materialize(Path(__file__).resolve().parents[1]), sort_keys=True))
