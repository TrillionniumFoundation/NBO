#!/usr/bin/env python3
"""Independent standard-library checks used by the NBO R15 referee review.

Usage:
  python verify_r15_review.py --table-dir PATH --raw-artifact PATH --output PATH
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import zipfile

REVISION = "1cb3cc9efe135966ec228dfaf51c6841a6dfc97c"
TREE = "4d26e498db033a16adfd7d3c38968766a2b9878e"
SOURCE = "9142f404bb9c5163aa94d3a4ded4d0fa48a49c50"
ARTIFACT_SHA256 = "59f286008800b3453d680acdceea76a0116ea403d717cfecfbfbd15edb53160b"
TABLE_BLOBS = {
    "table_method_summary.tex": "fae6c8021822049d655d08c662953a420eb73775",
    "table_method_comparisons.tex": "fef0acc4f9a5fa3c623a1d7a0b1793f2d7d436ee",
    "paired_transfer_main.tex": "6966177751494857ea28d4ba07e27aac542726d4",
    "table_method_work.tex": "c60db3c0e5af66b0c4eddd01bd633504e1a3b80f",
    "table_method_operations.tex": "73a39704934c6f69f15fdf7859ecf9fc7a850239",
    "table_mechanism_evaluation.tex": "73525c0166a90ce9da7eac8566d6369b24371bf7",
    "table_mechanism_welfare.tex": "ff39a55ec65e77602a03951a206b637c2eda44ec",
    "table_scalar_deployment.tex": "14e42ca2a5efd414b9fffbf97aba41498ad13b42",
    "table_observation_main.tex": "5d1b5eb3720e5eadc86cadc4965b26c7f45c3aff",
}
EXPECTED = {
    "nbo": (0.001346184423298548, 0.0005637745516599289, 0.0021285942949371677, True, 394.001041944),
    "raw_costate": (0.001347936838371215, 0.000565559688436295, 0.0021303139883061353, True, 382.2286529520002),
    "direct_policy": (0.0013467169612393325, 0.000564471457077012, 0.0021289624654016533, True, 639.987274575),
    "neural_hjb": (-0.00033192208915752957, -0.0011648974695692674, 0.000501053291254208, False, 1795.6325946830002),
}


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def table_checks(directory: Path) -> dict:
    identities = {}
    for name, expected in TABLE_BLOBS.items():
        path = directory / name
        require(path.is_file(), f"missing table {name}")
        actual = blob_sha(path)
        require(actual == expected, f"blob mismatch {name}: {actual}")
        identities[name] = actual

    text = {name: (directory / name).read_text() for name in TABLE_BLOBS}
    require("10 & NBO & 0.001268 & 0.000944" in text["table_method_summary.tex"], "d10 NBO summary")
    require("50 & Neural HJB & -0.000156" in text["table_method_summary.tex"], "d50 HJB summary")
    require("10 & NBO--Neural HJB & 0.000295 & -0.000073" in text["table_method_comparisons.tex"], "original d10 HJB interval")
    require("50 & NBO--Neural HJB & 0.001498 & 0.001052" in text["table_method_comparisons.tex"], "original d50 HJB interval")
    require("[0.000179, 0.000411]" in text["paired_transfer_main.tex"], "refined d10 HJB interval")
    require("developed after the original source freeze" in text["paired_transfer_main.tex"], "post-freeze disclosure")
    require("50 & Raw & 16/16 & 346.22" in text["table_method_work.tex"], "Raw work")
    require("50 & NBO & 16/16 & 357.80" in text["table_method_work.tex"], "NBO work")
    require("50 & Neural HJB & 0.07 & 134.22 & 0 & 700 & 67.20 & 2956.73" in text["table_method_operations.tex"], "HJB work proxies")
    require("10 & -0.000849 & 0.005630" in text["table_mechanism_welfare.tex"], "d10 mechanism")
    require("50 & -0.000153 & 0.004285" in text["table_mechanism_welfare.tex"], "d50 mechanism")
    require("NBO (R12) & 0.1036 & 1.5557 & 0.5683 & 0.7412" in text["table_scalar_deployment.tex"], "scalar NBO")
    require("F4 & 0.1136 & 1.5586 & 0.6772 & 0.7819" in text["table_scalar_deployment.tex"], "scalar classical")
    require("50 & 4096 & 0.001193 & 0.001054 & -0.000239 & -0.011873" in text["table_observation_main.tex"], "observation sensitivity")
    return {
        "blob_identities": identities,
        "derived": {
            "original_d10_hjb_unresolved": True,
            "original_d50_hjb_materially_positive": True,
            "refined_d10_hjb_materially_positive": True,
            "raw_cheaper_than_nbo_d50": True,
            "mechanism_gain_lowers_negative": 2,
            "scalar_classical_population_gain_above_nbo": True,
            "observation_nu_0_001_positive_count": 0,
        },
    }


def artifact_checks(path: Path) -> dict:
    actual = sha256(path)
    require(actual == ARTIFACT_SHA256, f"artifact SHA mismatch: {actual}")
    with zipfile.ZipFile(path) as zf:
        trial = json.loads(zf.read("TRIAL.json"))
        require(trial["complete"] is True, "incomplete trial")
        require(trial["numerical_source_commit"] == SOURCE, "source commit")
        require(trial["trial"]["dimension"] == 50, "dimension")
        require(trial["trial"]["stream_seed"] == 964082955, "stream seed")
        outcomes = {}
        for method, expected in EXPECTED.items():
            result = json.loads(zf.read(f"{method}/RESULT.json"))
            confirmation = json.loads(zf.read(f"{method}/confirmation/confirmation.json"))
            require(result["complete"] is True, f"{method} incomplete")
            require(result["numerical_source_commit"] == SOURCE, f"{method} source")
            mean, lower, upper, attained, seconds = expected
            require(math.isclose(confirmation["mean"], mean, abs_tol=1e-15), f"{method} mean")
            require(math.isclose(confirmation["lower"], lower, abs_tol=1e-15), f"{method} lower")
            require(math.isclose(confirmation["upper"], upper, abs_tol=1e-15), f"{method} upper")
            require(result["attained_online"] is attained, f"{method} attainment")
            require(math.isclose(result["seconds_before_final_result_write"], seconds, abs_tol=1e-9), f"{method} seconds")
            outcomes[method] = {
                "mean": confirmation["mean"],
                "lower": confirmation["lower"],
                "upper": confirmation["upper"],
                "attained_online": result["attained_online"],
                "seconds_before_final_result_write": result["seconds_before_final_result_write"],
                "counters": {
                    "critic_updates": result["counters"].get("critic_updates", 0),
                    "actor_updates": result["counters"].get("actor_updates", 0),
                    "first_derivative_rows": result["counters"].get("first_derivative_rows", 0),
                    "action_search_iterations": result["counters"].get("action_search_iterations", 0),
                },
            }
        require(outcomes["neural_hjb"]["counters"]["action_search_iterations"] == 2956732416, "HJB searches")
        require(outcomes["neural_hjb"]["counters"]["first_derivative_rows"] == 67198464, "HJB derivative rows")
        require(outcomes["raw_costate"]["seconds_before_final_result_write"] < outcomes["nbo"]["seconds_before_final_result_write"], "Raw faster than NBO")
    return {
        "artifact_id": 11301120232,
        "sha256": actual,
        "trial_id": trial["trial"]["trial_id"],
        "numerical_source_commit": trial["numerical_source_commit"],
        "outcomes": outcomes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table-dir", required=True, type=Path)
    parser.add_argument("--raw-artifact", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "status": "passed",
        "reviewed_revision": {"commit": REVISION, "tree": TREE, "numerical_source_commit": SOURCE},
        "tables": table_checks(args.table_dir),
        "raw_artifact": artifact_checks(args.raw_artifact),
        "limitations": [
            "The script checks nine committed publication tables and one original raw trial artifact.",
            "It does not rerun the 128 training executions or formally verify every interval-arithmetic proof.",
            "A falling sampled HJB objective is not a convergence certificate.",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
