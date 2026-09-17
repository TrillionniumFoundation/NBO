"""Load unchanged numerical definitions without importing neural-training runtime.

The selected AST nodes are taken from pinned, preserved R4/R6/R7 files. No
rewriting of the transition or Bellman formulas occurs. This keeps the finite
certificate executable with NumPy/SciPy when neural policies are already frozen.
"""
from __future__ import annotations
import ast,sys,types,math,itertools,json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
import numpy as np
ROOT=Path(__file__).resolve().parents[2]

def load(path,names,module):
    tree=ast.parse((ROOT/path).read_text(),filename=str(path));chosen=[];found=set()
    for node in tree.body:
        name=getattr(node,'name',None)
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and name in names:
            chosen.append(node);found.add(name)
        elif isinstance(node,ast.Assign):
            assigned={n.id for n in node.targets if isinstance(n,ast.Name)}
            if assigned and assigned<=names:chosen.append(node);found|=assigned
    if found!=set(names):raise RuntimeError(f'Numerical definition inventory changed: {path}: {set(names)-found}')
    exec(compile(ast.Module(body=chosen,type_ignores=[]),str(path),'exec'),module.__dict__)

old=types.ModuleType('r8_preserved_transition');sys.modules[old.__name__]=old
old.__dict__.update(np=np,math=math,itertools=itertools,dataclass=dataclass)
load('replication/r4/solver.py',{'LO','HI','ALO','AHI','SIGNS','Model','terminal','grid','interpolate','transition','action_mesh'},old)
c=SimpleNamespace(old=old)
this=sys.modules[__name__]
load('replication/r6/transport.py',{'bernstein_value','split','restrict','Mixture'},this)
load('replication/r6/kernel_certificate.py',{'continuation'},this)
load('replication/r7/core.py',{'serial','mask','solve','classes','CompactUpper','expand','chord','count'},this)
