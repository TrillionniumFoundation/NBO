#!/usr/bin/env python3
"""Read-only reproduction of the recorded raw Git tree stream identities.

No Git fetch, checkout, index operation, scientific import or experiment.
The metadata repository must already contain the commits and trees.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",required=True,type=Path)
    p.add_argument("--index",type=Path,default=Path(__file__).with_name("ALL_BRANCH_FILE_LEDGER121.json"))
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--commit",action="append",default=[])
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    start=time.time()
    source=Path(__file__).read_bytes()
    idx=a.index.read_bytes()
    env={**os.environ,"GIT_NO_LAZY_FETCH":"1","GIT_OPTIONAL_LOCKS":"0"}
    rows=[]
    (a.output/"START121.json").write_text(json.dumps({
        "started_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope":__doc__,"source_sha256":hashlib.sha256(source).hexdigest(),
        "index_sha256":hashlib.sha256(idx).hexdigest(),
        "selected_commits":a.commit},indent=2)+"\n")
    try:
        obj=json.loads(idx)
        selected=[x for x in obj["ledgers"] if not a.commit or x["commit"] in set(a.commit)]
        if a.commit and {x["commit"] for x in selected}!=set(a.commit):
            raise ValueError("unknown or absent requested commit")
        for entry in selected:
            command=["git","-C",str(a.repo),"ls-tree","-r","-z",entry["commit"]]
            actual_tree=subprocess.run(["git","-C",str(a.repo),"rev-parse",entry["commit"]+"^{tree}"],
              env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.decode().strip()
            if actual_tree!=entry["tree"]:raise ValueError("root tree identity")
            errpath=a.output/(entry["commit"]+".stderr")
            digest=hashlib.sha256();count=0;size=0
            with errpath.open("xb") as err:
                proc=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=err)
                while True:
                    chunk=proc.stdout.read(1<<20)
                    if not chunk:break
                    digest.update(chunk);size+=len(chunk);count+=chunk.count(b"\0")
                code=proc.wait()
            row={"commit":entry["commit"],"tree":actual_tree,"command":command,
                 "exit_code":code,"raw_bytes":size,"entries":count,
                 "raw_sha256":digest.hexdigest()}
            rows.append(row)
            with (a.output/"TREE_ROWS121.jsonl").open("a") as f:f.write(json.dumps(row,sort_keys=True)+"\n")
            if code or size!=entry["raw_bytes"] or count!=entry["entries"] or digest.hexdigest()!=entry["raw_sha256"]:
                raise ValueError("tree stream mismatch at "+entry["commit"])
        result={"status":"passed","scope":__doc__,"tree_count":len(rows),
                "entries":sum(x["entries"] for x in rows),"seconds":time.time()-start,
                "ended_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
                "scientific_execution":False,"full_semantic_read_asserted":False}
        (a.output/"EXECUTION121.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps(result,sort_keys=True))
    except BaseException as e:
        (a.output/"FAILED121.json").write_text(json.dumps({
           "status":"failed","exception":type(e).__name__,"message":str(e),
           "completed_tree_records":len(rows),"seconds":time.time()-start},indent=2)+"\n")
        raise
if __name__=="__main__":main()

