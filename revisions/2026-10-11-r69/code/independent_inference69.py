"""Independent exact-sum/80-digit audit of every R69 centered interval.

No NBO numerical module is imported. This checks the final arithmetic and
reported support of saved optimal-advantage endpoints, not the generation
of those endpoints or complete integration of their descendant trees.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
import hashlib, json
import numpy as np

R = Path(__file__).resolve().parents[1]

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def decimal(fraction):
    return Decimal(fraction.numerator) / Decimal(fraction.denominator)

def main():
    results = []
    for folder in sorted((R / "results69").glob("inference-*-paired-*")):
        summary_file = folder / "summary.json"
        summary = json.loads(summary_file.read_text())
        if summary["status"] != "returned":
            raise AssertionError("Inference service did not return: " + folder.name)
        paths = {}
        for method, arm in summary["arms"].items():
            file = folder / (method + "-paths.npz")
            if sha(file) != arm["trace_sha256"]:
                raise AssertionError("Trace identity mismatch: " + method)
            with np.load(file) as data:
                paths[method] = (data["center_lo"].copy(), data["center_hi"].copy())
        for name, reported in summary["centered"].items():
            first, second = name.split("-minus-")
            lo1, hi1 = paths[first]
            lo2, hi2 = paths[second]
            n = len(lo1)
            if not (n == len(lo2) == reported["rows"] == 1024):
                raise AssertionError("Unexpected sample size")
            exact_lower_mean = sum(
                (F(float(x)) - F(float(y)) for x, y in zip(lo1, hi2)), F(0)
            ) / n
            exact_upper_mean = sum(
                (F(float(x)) - F(float(y)) for x, y in zip(hi1, lo2)), F(0)
            ) / n
            width = F(reported["support_width_exact"])
            with localcontext() as context:
                context.prec = 80
                # Decimal.sqrt is correctly rounded in the current context.
                # A 10^-70 expansion is much larger than its rounding error here.
                slack = Decimal("1e-70")
                radius = decimal(width) * (
                    Decimal(str(reported["log_upper"])) / Decimal(2 * n)
                ).sqrt()
                required_lower = decimal(exact_lower_mean) - radius - slack
                required_upper = decimal(exact_upper_mean) + radius + slack
                reported_lower = Decimal.from_float(reported["interval"][0])
                reported_upper = Decimal.from_float(reported["interval"][1])
                if reported_lower > required_lower or reported_upper < required_upper:
                    raise AssertionError("Reported interval failed independent check: " + name)
                lower_clearance = required_lower - reported_lower
                upper_clearance = reported_upper - required_upper
            results.append({
                "task": [summary["d"], summary["T"]],
                "contrast": name, "rows": n,
                "lower_endpoint_mean_exact": str(exact_lower_mean),
                "upper_endpoint_mean_exact": str(exact_upper_mean),
                "support_width_exact": str(width),
                "reported_interval": reported["interval"],
                "lower_containment_clearance": str(lower_clearance),
                "upper_containment_clearance": str(upper_clearance),
                "summary_sha256": sha(summary_file),
                "status": "passed",
            })
    if len(results) != 12:
        raise AssertionError("The complete twelve-contrast catalogue is required.")
    output = R / "audit" / "INDEPENDENT_INFERENCE69.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({
        "status": "passed", "checked_contrasts": len(results),
        "arithmetic": "exact Fraction sums and 80-digit Decimal radius",
        "new_observations": 0, "imports_NBO_numerics": False,
        "scope": "Final interval arithmetic from saved endpoints; not independent "
                 "generation of Bellman endpoints or large-tree reintegration.",
        "comparisons": results,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "passed", "checked_contrasts": len(results)}))

if __name__ == "__main__":
    main()
