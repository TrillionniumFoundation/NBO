"""Portable read-only R121 source, artifact, record and cost integrity entry."""
from __future__ import annotations
from pathlib import Path
import sys


def main():
    # Only the postprocessing module is imported. All source-F economic,
    # fitting, sampling and statistical programs remain unimported.
    args=list(sys.argv[1:])
    if "--revision" in args:revision=Path(args[args.index("--revision")+1]).resolve()
    else:revision=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(revision/"code121"))
    import report121
    if "--revision" not in args:args=["--revision",str(revision)]+args
    if "--integrity-only" not in args:args.append("--integrity-only")
    return report121.main(args)


if __name__=="__main__":raise SystemExit(main())
