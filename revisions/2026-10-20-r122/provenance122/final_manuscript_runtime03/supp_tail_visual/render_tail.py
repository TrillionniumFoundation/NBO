"""Render only the final current inference proof and bibliography pages.

This administrative reader has no economic/model imports and changes no
scientific input, statistical rule, service clock, or author source.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

started = time.perf_counter()
started_utc = datetime.now(timezone.utc).isoformat()
root = Path.cwd()
out = Path(__file__).resolve().parent
pdf = root / "build/supp.pdf"
expected = "53955f0525c08742ca73b42eb01a5450083b2a4fcafcb69cbb79f964ecc39ad9"
assert sha256(pdf.read_bytes()).hexdigest() == expected
records = []
for page in (106, 107):
    target = out / f"supp-{page:04d}"
    command = ["pdftoppm", "-f", str(page), "-l", str(page), "-r", "110", "-png", "-singlefile", str(pdf), str(target)]
    t0 = time.perf_counter()
    proc = subprocess.run(command, capture_output=True, text=True)
    elapsed = time.perf_counter() - t0
    record = {"page": page, "command": command, "seconds": elapsed,
              "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    if proc.returncode == 0:
        image = target.with_suffix(".png")
        record.update(path=str(image.relative_to(root)), bytes=image.stat().st_size,
                      sha256=sha256(image.read_bytes()).hexdigest())
    records.append(record)
assert all(row["returncode"] == 0 for row in records)
assert sha256(pdf.read_bytes()).hexdigest() == expected
receipt = {"schema": "nbo.r122.supp-tail-render.v1", "status": "executed",
           "started_utc": started_utc, "finished_utc": datetime.now(timezone.utc).isoformat(),
           "seconds": time.perf_counter() - started,
           "source_path": str(Path(__file__).resolve().relative_to(root)),
           "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
           "pdf_path": "build/supp.pdf", "pdf_sha256": expected,
           "records": records,
           "scope": "Actual extra rendering only; manual visual review is recorded separately. The two command clocks are nested in the reader clock. Interpreter startup, this receipt write, and manual review are outside it."}
with (out / "SUPP_TAIL_RENDER122.json").open("x") as f:
    json.dump(receipt, f, indent=2, sort_keys=True)
    f.write("\n")
print(json.dumps({"seconds": receipt["seconds"], "pages": [106, 107]}))
