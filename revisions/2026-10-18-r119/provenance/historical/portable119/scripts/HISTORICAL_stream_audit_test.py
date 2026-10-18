#!/usr/bin/env python3
"""Small parser/custody diagnostics; never execute historical scientific code."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("stream_audit", HERE / "HISTORICAL_stream_audit.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def npy(descr, shape, data):
    h = repr({"descr": descr, "fortran_order": False, "shape": shape}).encode("ascii")
    h += b" " * ((64 - (10 + len(h) + 1) % 64) % 64) + b"\n"
    return b"\x93NUMPY\x01\x00" + struct.pack("<H", len(h)) + h + data


def main():
    tests = []
    with tempfile.TemporaryDirectory(prefix="nbo-historical-parser-test-") as tmp:
        d = Path(tmp)

        def check(name, data, suffix, predicate, expect_error=False, budget=1024 * 1024):
            p = d / (name + suffix)
            p.write_bytes(data)
            evpath = d / (name + ".events.gz")
            ev = m.Events(evpath, 1000)
            err = None
            try:
                r = m.parse_file(p, suffix, ev, budget)
            except Exception as e:
                err, r = str(e), None
            ev.close()
            events = [json.loads(x) for x in gzip.open(evpath, "rt")]
            ok = bool(err) if expect_error else err is None and predicate(r, events)
            if not ok:
                raise AssertionError((name, r, err, events))
            tests.append({"name": name, "passed": True, "expected_parse_error": expect_error,
                          "observed_error": err, "sha256": hashlib.sha256(data).hexdigest()})

        check("exact_json", b'{"seed":123456789012345678901234567890,"cost":1.234567890123456789e-20,"x":[{"status":"failed"},{"status":"success"}],"x":[],"risk.alpha":0.75}', ".json",
              lambda r, e: r["json_roots"] == 1 and r["event_counts"]["map_key"] == 7
              and any(x.get("value") == 123456789012345678901234567890 for x in e)
              and any(x.get("value") == {"decimal_exact": "1.234567890123456789E-20"} for x in e)
              and any(x.get("path") == ["x", 1, "status"] for x in e)
              and any(x.get("path") == ["risk.alpha"] for x in e))
        check("empty_containers", b'{"a":[],"b":{},"c":[[],{},null,false]}', ".json",
              lambda r, e: r["semantic_complete"] and r["event_counts"]["null"] == 1)
        check("json_sequence", b'{"status":"a"}\n{"status":"b"}\n', ".jsonl",
              lambda r, e: r["json_roots"] == 2 and any(x.get("path") == [1, "status"] for x in e))
        for name, data in [("nonstandard_nan", b'{"x":NaN}'), ("truncated", b'{"a":[1,'),
                           ("bad_utf8", b'{"x":"\xff"}'), ("extra_root", b'{}{}')]:
            check(name, data, ".json", lambda r, e: False, expect_error=True)
        check("csv_exact", b'seed,policy,wall_time\r\n12345678901234567890123,"a\nb",0.125\r\n', ".csv",
              lambda r, e: r["rows_including_header"] == 2 and r["finite_numeric_bounds_exact_decimal"]["0"] == ["12345678901234567890123"] * 2)
        check("text_status", b'run started\nstatus=FAILED sha=0123456789012345678901234567890123456789\n', ".log",
              lambda r, e: r["lines"] == 2 and any(x.get("line") == 2 for x in e))
        check("npy_numeric", npy("<f8", (5,), struct.pack("<5d", -2.0, 3.0, float("nan"), float("inf"), 0.0)), ".npy",
              lambda r, e: e[0]["expected_size_matches"] and e[0]["simple_numeric_statistics"] ==
              {"available": True, "values": 5, "finite": 3, "nan": 1, "infinite": 1, "minimum": -2.0, "maximum": 3.0})
        check("npy_wrong_length", npy("<i8", (2,), struct.pack("<q", 1)), ".npy",
              lambda r, e: not r["semantic_complete"])
        check("npy_object_opaque", npy("|O", (1,), b"not-a-pickle-and-must-not-be-executed"), ".npy",
              lambda r, e: e[0]["dtype_interpretation"]["object"] is True and e[0]["expected_size_matches"] is None)
        p = d / "sample.npz"
        with zipfile.ZipFile(p, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("numbers.npy", npy("<i8", (3,), struct.pack("<3q", 1, 2, 3)))
            z.writestr("opaque.npy", npy("|O", (1,), b"not-a-pickle"))
        check("npz_all_members", p.read_bytes(), ".npz",
              lambda r, e: r["members_read"] == 2 and r["opaque_object_arrays"] == 1 and all(x["crc_checked_by_zipfile"] for x in e))
        check("npz_expansion_bound", p.read_bytes(), ".npz", lambda r, e: False,
              expect_error=True, budget=16)
        check("lfs_pointer", b'version https://git-lfs.github.com/spec/v1\noid sha256:' + b'a' * 64 + b'\nsize 1000\n', ".npz",
              lambda r, e: r["format"] == "git_lfs_pointer" and not r["semantic_complete"])
    report = {"completed_utc": m.utc(), "test_count": len(tests), "all_passed": True,
              "scientific_experiment": False, "tests": tests,
              "script_sha256": m.sha_file(HERE / "HISTORICAL_stream_audit.py")}
    m.dump(HERE / "HISTORICAL_stream_parser_validation.json", report)
    print(json.dumps({"tests": len(tests), "all_passed": True}))


if __name__ == "__main__":
    main()
