from pathlib import Path
import sys, os, json, gzip, hashlib, base64, termios, datetime
base=Path("/workspace/scratch/913249553838/audit/review_lineage/final_ci119")
attrs=termios.tcgetattr(sys.stdin.fileno())
attrs[3] &= ~(termios.ECHO | termios.ICANON)
termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, attrs)
print(json.dumps({"status":"ready","scope":"Exact captured CI envelope storage only; no network or scientific execution."}),flush=True)
for frame in sys.stdin.buffer:
    request=json.loads(frame)
    if request.get("done"):
        print(json.dumps({"status":"writer_completed"}),flush=True)
        break
    logical_name=request["logical_name"]
    assert Path(logical_name).name==logical_name and logical_name.endswith(".json")
    target=base/(logical_name+".gz")
    data=base64.b64decode(request["base64_payload"],validate=True)
    envelope=json.loads(data)
    assert Path(envelope["path"]).name==logical_name
    compressed=gzip.compress(data,compresslevel=9,mtime=0)
    receipt={"path":str(target),"logical_path":str(base/logical_name),
        "raw_bytes":len(data),"raw_sha256":hashlib.sha256(data).hexdigest(),
        "gzip_bytes":len(compressed),"gzip_sha256":hashlib.sha256(compressed).hexdigest(),
        "recorded_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        if target.exists():
            existing=target.read_bytes()
            assert existing==compressed and gzip.decompress(existing)==data
            receipt["status"]="existing_exact_gzip_verified"
        else:
            with target.open("xb") as handle:
                handle.write(compressed);handle.flush();os.fsync(handle.fileno())
            saved=target.read_bytes()
            assert saved==compressed and gzip.decompress(saved)==data
            receipt["status"]="saved_and_inflation_verified"
    except Exception as exc:
        receipt["status"]="write_failed"
        receipt["error"]=repr(exc)
        receipt["saved_file_bytes"]=target.stat().st_size if target.exists() else None
    print(json.dumps(receipt),flush=True)
    if receipt["status"]=="write_failed":
        break

