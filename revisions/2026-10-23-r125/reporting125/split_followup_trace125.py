"""Lossless publication transport for a completed witness stream; no economics."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, time

ROOT = Path(__file__).resolve().parents[1]
PART_BYTES = 7_000_000


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    tick = time.perf_counter()
    source = ROOT/'results125/independent-followup512/terminal_witnesses125.jsonl.gz'
    execution = ROOT/'results125/independent-followup512/EXECUTION125.json'
    assert json.loads(execution.read_text())['exit_code'] == 0
    original_sha = sha(source)
    out = ROOT/'results125/independent_followup_transport'
    out.mkdir(exist_ok=False)
    parts = []
    digest = hashlib.sha256()
    with source.open('rb') as f:
        number = 0
        while block := f.read(PART_BYTES):
            target = out / f'terminal_witnesses125.part{number:02d}'
            with target.open('xb') as g:
                g.write(block)
            digest.update(block)
            parts.append(dict(path=str(target.relative_to(ROOT)), bytes=len(block),
                              sha256=hashlib.sha256(block).hexdigest()))
            number += 1
    assert digest.hexdigest() == original_sha
    assert sum(p['bytes'] for p in parts) == source.stat().st_size
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                  original_path=str(source.relative_to(ROOT)),
                  original_sha256=original_sha, original_bytes=source.stat().st_size,
                  original_file_modified=False, parts=parts,
                  maximum_part_bytes=PART_BYTES, economic_evaluations=0,
                  role='Lossless publication transport; concatenate ordered parts to recover exact original gzip.',
                  execution_receipt_sha256=sha(execution),
                  source_script_sha256=sha(Path(__file__)), seconds=time.perf_counter()-tick)
    (out/'TRANSPORT125.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
