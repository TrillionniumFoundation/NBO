"""Immutable, complete R13 finite-array target. Verification never rebuilds inputs."""
from __future__ import annotations
import os
for _k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_k]='1'
import sys, json, hashlib, dataclasses, platform, io
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from scipy.sparse import csr_matrix
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'replication/r11'))
import core
from model import Economy, SparseKernel

FIELDS=('base','duration','effort','settlement','exit_discount')
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def dump(path,obj):
    Path(path).write_text(json.dumps(core.r7.serial(obj),indent=2,sort_keys=True,allow_nan=False)+'\n')
def array_id(a):
    a=np.ascontiguousarray(a)
    return dict(shape=list(a.shape),dtype=a.dtype.str,sha256=hashlib.sha256(a.tobytes()).hexdigest())
def csr_data(m):
    return {**{f'csr.{k}':getattr(m,k) for k in ('data','indices','indptr')},'csr.shape':np.array(m.shape,dtype=np.int64)}
def csr_load(a):
    m=csr_matrix((a['csr.data'],a['csr.indices'],a['csr.indptr']),shape=tuple(a['csr.shape']))
    if not m.has_sorted_indices or np.any(m.data<0) or not np.isfinite(m.data).all():
        raise ValueError('noncanonical or invalid transition matrix')
    mass=np.asarray(m.sum(axis=1)).ravel()
    if np.any(mass>1+1e-12):raise ValueError('transition mass exceeds one')
    return m

def freeze(base,joint,directory):
    """Explicit new-target operation. Refuses to replace ANY existing target."""
    directory=Path(directory)
    if directory.exists():raise FileExistsError('target already exists; a check must not replace it')
    directory.mkdir(parents=True)
    files={}
    def save(name,arrays):
        np.savez_compressed(directory/name,**arrays)
        entry={'sha256':digest(directory/name),'arrays':{k:array_id(v) for k,v in arrays.items()}}
        if (directory/name).stat().st_size>32*1024*1024:
            parts=[]
            with (directory/name).open('rb') as f:
                for i,block in enumerate(iter(lambda:f.read(32*1024*1024),b'')):
                    part=f'{name}.part{i:03d}';(directory/part).write_bytes(block)
                    parts.append({'name':part,'sha256':digest(directory/part)})
            (directory/name).unlink();entry['parts']=parts
        files[name]=entry
    save('economy.npz',dict(states=base.e[0].states,boundary=base.e[0].boundary,
         terminal=base.terminal,menu=base.e[0].menu))
    for k,e in enumerate(base.e):
        for n,z in enumerate([e.common]+e.extra):
            aa={f:getattr(z,f) for f in FIELDS};aa.update(csr_data(z.matrix))
            if n:aa['actions']=z.actions
            save(f'kernel_{k}_{n}.npz',aa)
    aa={'actions':joint.fm.actions,'pairs':joint.fm.pairs}
    for k in (0,1):
        aa[f'reward.{k}']=joint.fm.reward[k];aa[f'duration.{k}']=joint.fm.duration[k]
        for f,v in csr_data(joint.fm.rows[k]).items():aa[f'{k}.{f}']=v
    save('first_date.npz',aa)
    meta=dict(schema='nbo-canonical-v1',spec=dataclasses.asdict(base.spec),models=[vars(e.model) for e in base.e],
              center=base.center,steps=base.steps,shape=list(base.e[0].shape),box=joint.box,
              first_lower=joint.fm.lower,first_upper=joint.fm.upper,source_commit=os.getenv('R13_SOURCE_SHA',os.getenv('GITHUB_SHA','local-development')),
              python=sys.version,numpy=np.__version__,platform=platform.platform(),
              target='new R13 stored arrays, not an asserted bit-identical reconstruction of R11')
    dump(directory/'metadata.json',meta);files['metadata.json']={'sha256':digest(directory/'metadata.json')}
    dump(directory/'manifest.json',dict(schema='nbo-canonical-manifest-v1',files=files))
    return digest(directory/'manifest.json')

def check(directory,expected=None):
    directory=Path(directory)
    if expected is not None and digest(directory/'manifest.json')!=expected:
        raise ValueError('canonical manifest differs from the immutable witness identity')
    manifest=json.loads((directory/'manifest.json').read_text())
    if manifest['schema']!='nbo-canonical-manifest-v1':raise ValueError('unknown canonical schema')
    listed={p['name'] for name,e in manifest['files'].items() for p in e.get('parts',[{'name':name}])}
    if {p.name for p in directory.iterdir()}!=listed|{'manifest.json'}:
        raise ValueError('unlisted or missing canonical input')
    for name,entry in manifest['files'].items():
        for part in entry.get('parts',[{'name':name,'sha256':entry['sha256']}]):
            pn=part['name']
            if Path(pn).name!=pn or digest(directory/pn)!=part['sha256']:
                raise ValueError('canonical file identity mismatch: '+pn)
    return manifest

def load(directory,expected=None):
    """Read stored bytes only: no transition/reward/first-date constructor calls."""
    directory=Path(directory);manifest=check(directory,expected)
    def arrays(name):
        entry=manifest['files'][name]
        if 'parts' in entry:
            data=b''.join((directory/p['name']).read_bytes() for p in entry['parts'])
            if hashlib.sha256(data).hexdigest()!=entry['sha256']:raise ValueError('concatenated archive identity')
            source=io.BytesIO(data)
        else:source=directory/name
        with np.load(source,allow_pickle=False) as z:a={k:z[k] for k in z.files}
        if set(a)!=set(manifest['files'][name]['arrays']):raise ValueError('array inventory differs')
        for k,v in a.items():
            if array_id(v)!=manifest['files'][name]['arrays'][k]:raise ValueError('array identity: '+name+':'+k)
            if v.dtype.kind not in 'bifu' or not np.isfinite(v).all():raise ValueError('invalid array data')
            v.flags.writeable=False
        return a
    meta=json.loads((directory/'metadata.json').read_text());a=arrays('economy.npz')
    b=core.Model.__new__(core.Model);b.spec=core.Specification(**meta['spec']);b.steps=meta['steps']
    b.ns=len(a['states']);b.terminal=a['terminal'];b.center=meta['center'];b.build_seconds=0.
    es=[]
    for k in (0,1):
        e=Economy.__new__(Economy);e.spec=b.spec;e.shape=tuple(meta['shape']);e.steps=b.steps;e.k=b.spec.cost
        e.model=SimpleNamespace(**meta['models'][k]);e.states=a['states'];e.boundary=a['boundary'];e.ns=b.ns;e.menu=a['menu']
        kk=[]
        for n in range(b.steps+1):
            ar=arrays(f'kernel_{k}_{n}.npz');z=SparseKernel.__new__(SparseKernel)
            z.ns=b.ns;z.na=len(e.menu) if n==0 else ar['actions'].shape[1]
            z.actions=np.broadcast_to(e.menu,(b.ns,len(e.menu),3)) if n==0 else ar['actions']
            z.shape=e.shape;z.model=e.model;z.h=1/b.steps;z.states=e.states;z.parts=None;z.matrix=csr_load(ar)
            if z.matrix.shape!=(b.ns*z.na,b.ns):raise ValueError('kernel dimensions')
            for f in FIELDS:setattr(z,f,ar[f])
            z.check={'max_row_mass':float(np.asarray(z.matrix.sum(1)).max()),'min_weight':float(z.matrix.data.min()),'sparse_vs_gather':0.}
            kk.append(z)
        e.common=kk[0];e.extra=kk[1:];es.append(e)
    b.e=tuple(es);b.backend_checks=[]
    fm=core.FirstDateMenu.__new__(core.FirstDateMenu);fm.base=b;fm.center=b.center
    fm.lower=meta['first_lower'];fm.upper=meta['first_upper'];fm.max_knot_error=0.
    ar=arrays('first_date.npz');fm.actions=ar['actions'];fm.pairs=ar['pairs'];fm.nknots=len(fm.actions)
    fm.endpoints=b.e[0].states[[b.center]];fm.reward=[];fm.duration=[];fm.rows=[]
    for k in (0,1):
        fm.reward.append(ar[f'reward.{k}']);fm.duration.append(ar[f'duration.{k}'])
        fm.rows.append(csr_load({f:ar[f'{k}.{f}'] for f in ('csr.data','csr.indices','csr.indptr','csr.shape')}))
    j=core.Joint.__new__(core.Joint);j.base=b;j.box=meta['box'];j.fm=fm;j.groups=[]
    for pair in fm.pairs:
        ix=np.where(np.all(fm.actions[:,:2]==pair,axis=1))[0];ix=ix[np.argsort(fm.actions[ix,2])];j.groups.append((pair,ix))
    j.cache={};j.solve_seconds=0.;j.solve_count=0;j.artifacts={}
    return b,j
