"""Pinned R13 paths and explicit imports of unchanged historical kernels."""
from __future__ import annotations
import hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'revisions/2026-10-04-r11/code'))
import bellman_study as old
import policy_certificate as pc
import numpy as np
import torch
# Historical kernels add their own directories while importing dependencies.
# Restore the current namespace for unqualified current-revision modules.
sys.path.insert(0,str(R/'code'))
P=old.P; CHI=old.CHI
PROTOCOL=json.loads((R/'PROTOCOL.json').read_text())
torch.set_num_threads(1);torch.set_default_dtype(torch.float64)
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def profiles(d,design='population'):
    if design=='origin':return np.zeros((1,d),dtype=np.float64)
    if d==1:v=np.zeros(1)
    else:
        v=np.linspace(-1.,1.,d);v-=v.mean();v/=np.sqrt(np.mean(v*v))
    return np.asarray([mu+s*v for mu in PROTOCOL['population_means'] for s in PROTOCOL['population_spreads']],dtype=np.float64)
def source():return os.environ.get('NBO_R13_SOURCE_COMMIT','uncommitted-development')
