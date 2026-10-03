"""Compile the integrated journal documents without relaxing TeX file safety.

All TeX output paths are relative to the repository working directory. In
particular, BibTeX must not receive an absolute output stem: TeX Live's
openout_any=p correctly rejects that invocation. Nonzero exit codes and
unresolved references remain hard failures; a pre-existing PDF is never
accepted as evidence of a successful build.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R = Path(__file__).resolve().parents[1]
B = R / "build"


def call(args, log):
    """Run one build stage, retaining combined output on success or failure."""
    B.mkdir(parents=True, exist_ok=True)
    with (B / log).open("w", encoding="utf-8") as stream:
        completed = subprocess.run(
            args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
            check=False, timeout=240,
        )
    if completed.returncode:
        tail = (B / log).read_text(errors="replace")[-5000:]
        print(tail, flush=True)
        raise RuntimeError(
            f"compilation failed ({completed.returncode}): {B / log}"
        )


def compile_documents():
    B.mkdir(parents=True, exist_ok=True)
    relative_build = B.relative_to(ROOT)
    sources = [
        ("ECTA", "ECTA.tex"),
        ("supp", "supp.tex"),
        ("response", "revisions/2026-10-04-r10/response.tex"),
    ]
    for name, source in sources:
        # Do not mistake any PDF or bibliography left by a failed run for
        # newly compiled evidence. The journal's cross-document ECTA.aux is
        # produced first, before the supplement and response are compiled.
        for suffix in [".pdf", ".bbl", ".blg"]:
            (B / f"{name}{suffix}").unlink(missing_ok=True)
        for iteration in [1, 2, 3]:
            call([
                "pdflatex", "-no-shell-escape", "-file-line-error",
                "-interaction=nonstopmode", "-halt-on-error",
                f"-output-directory={relative_build}", source,
            ], f"{name}_pass{iteration}.stdout")
            if name == "ECTA" and iteration == 1:
                call(["bibtex", str(relative_build / "ECTA")], "bibtex.stdout")

    result = {}
    for name, _ in sources:
        text = (B / f"{name}.log").read_text(errors="replace")
        pages = re.findall(r"Output written on .*?\((\d+) pages?", text, re.S)
        if not pages:
            raise RuntimeError(f"No completed PDF page count in {name}.log")
        result[name] = {
            "pdf_sha256": hashlib.sha256((B / f"{name}.pdf").read_bytes()).hexdigest(),
            "pages": int(pages[-1]),
            "undefined": bool(re.search(
                r"undefined references|Citation .* undefined|Reference .* undefined|Undefined control sequence",
                text,
            )),
            "overfull_hbox_pt": [float(v) for v in re.findall(
                r"Overfull \\hbox \(([\d.]+)pt", text,
            )],
        }
        call([
            "pdftotext", "-layout", str(relative_build / f"{name}.pdf"),
            str(relative_build / f"{name}.txt"),
        ], f"{name}_text.stdout")
    (R / "results").mkdir(exist_ok=True)
    (R / "results/COMPILATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(result, indent=2), flush=True)
    if not all(not record["undefined"] for record in result.values()):
        raise RuntimeError("Unresolved citations or references")
    if not all(not record["overfull_hbox_pt"] for record in result.values()):
        raise RuntimeError("Overfull material requires layout review")
    return result


if __name__ == "__main__":
    compile_documents()
