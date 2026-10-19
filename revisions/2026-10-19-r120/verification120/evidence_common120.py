"""Standard-library evidence transport helpers; importing this runs no science."""
from __future__ import annotations
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

SOURCE = '369d02724cf12ae0e54390b4e7b5f894f703892e'
ACTORS = '1c5e4dc7e04c108fe698d4c247a144b625db301c'
STATES = 'aebc7a0175c0729b9ff5e833a7facc1ed5c4c2fd'
REPORT_SPEC = '594d9336d89bedfd360e942146ae490e0fabd3a0'
ARMS = ('online','quadratic','relu','hinge','spline','poly2','poly3','grid')
SERVICES = ('completed','legacy-safe','paired','direct-refine')
REVISION = Path(__file__).resolve().parents[1]

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def safe_relative(value):
    path=PurePosixPath(value)
    require(isinstance(value,str) and value and not path.is_absolute()
            and '\\' not in value and all(x not in ('','..','.') for x in value.split('/')),
            'Unsafe or noncanonical relative evidence path: '+str(value))
    return path.as_posix()

def path_in(root, value):
    value=safe_relative(value)
    root=Path(root).resolve()
    path=root/value
    require(not path.is_symlink(),'Evidence cannot be a symbolic link: '+value)
    path.resolve().relative_to(root)
    return path

def sha256(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):
            digest.update(block)
    return digest.hexdigest()

def record(path, root):
    path,root=Path(path),Path(root)
    require(path.is_file() and not path.is_symlink(),'Missing or linked evidence: '+str(path))
    size=path.stat().st_size
    h=hashlib.sha256();g=hashlib.sha1(b'blob '+str(size).encode()+b'\0')
    count=0
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):
            h.update(block);g.update(block);count+=len(block)
    require(count==size and path.stat().st_size==size,'Evidence changed during read: '+str(path))
    return {'path':path.relative_to(root).as_posix(),'bytes':size,
            'sha256':h.hexdigest(),'git_blob':g.hexdigest()}

def write_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
        stream.flush();os.fsync(stream.fileno())

def read_json(path):
    with Path(path).open(encoding='utf-8') as stream:
        return json.load(stream,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON '+x)))

def iter_rows(path):
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path,'rt',encoding='utf-8') as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON '+x)))

def git(repository, *args):
    env=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_OPTIONAL_LOCKS='0')
    result=subprocess.run(['git','-C',str(repository),*args],env=env,
                          check=True,capture_output=True)
    return result.stdout

def repository(revision=REVISION):
    return Path(git(revision,'rev-parse','--show-toplevel').decode().strip()).resolve()

def commit_sha(value):
    require(isinstance(value,str) and len(value)==40 and all(c in '0123456789abcdef' for c in value),
            'A full immutable commit SHA is required')
    return value

def tree(repository_path, commit, prefix):
    commit_sha(commit)
    entries={}
    for item in git(repository_path,'ls-tree','-r','-z',commit,'--',prefix).split(b'\0'):
        if not item:continue
        metadata,path=item.split(b'\t',1)
        mode,kind,oid=metadata.decode().split()
        if kind=='blob':entries[path.decode()]=oid
    return entries

def census(root, prefixes):
    root=Path(root).resolve();found={}
    for prefix in prefixes:
        base=path_in(root,prefix)
        require(base.is_dir(),'Missing retained evidence root: '+prefix)
        for path in sorted(base.rglob('*')):
            require(not path.is_symlink(),'Linked evidence member: '+str(path))
            if path.is_file():
                item=record(path,root)
                require(item['path'] not in found,'Overlapping census roots: '+item['path'])
                found[item['path']]=item
    return sorted(found.values(),key=lambda r:r['path'])

class JoinedParts(io.RawIOBase):
    """Read ordered archive parts without making a second concatenated archive."""
    def __init__(self,paths):
        super().__init__();self.paths=iter(paths);self.current=None
    def readable(self):return True
    def readinto(self,buffer):
        while True:
            if self.current is None:
                try:self.current=Path(next(self.paths)).open('rb')
                except StopIteration:return 0
            n=self.current.readinto(buffer)
            if n:return n
            self.current.close();self.current=None
    def close(self):
        if self.current is not None:self.current.close();self.current=None
        super().close()

def materialize(manifest, revision, target=None, allow_existing_target=False):
    """Verify and copy archive members into a new output; original bytes stay put."""
    revision=Path(revision)
    target=Path(target) if target is not None else None
    require(target is None or not target.exists() or (allow_existing_target and target.is_dir()),
            'Archive materialization target must be new or an explicitly shared fresh audit directory')
    archive=manifest.get('archive')
    require(archive and archive['kind']=='concatenated-tar-gzip-parts','No supported evidence archive')
    parts=[];combined=hashlib.sha256();size=0
    for wanted in archive['parts']:
        path=path_in(revision,wanted['path']);got=record(path,revision)
        require(got==wanted,'Archive part differs: '+wanted['path']);parts.append(path)
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(1<<20),b''):combined.update(block);size+=len(block)
    require(size==archive['compressed_bytes'] and combined.hexdigest()==archive['sha256'],
            'Concatenated archive identity differs')
    if target is not None:target.mkdir(parents=True,exist_ok=allow_existing_target)
    wanted={r['path']:r for r in manifest['files']};seen=set()
    with io.BufferedReader(JoinedParts(parts)) as stream:
        # The explicit gzip reader is drained after tar's logical end. A tar
        # iterator alone can finish before checking a truncated gzip footer.
        with gzip.GzipFile(fileobj=stream,mode='rb') as decoded:
          with tarfile.open(fileobj=decoded,mode='r|') as tar:
            for member in tar:
                name=safe_relative(member.name)
                require(member.isfile() and not member.issym() and not member.islnk(),
                        'Archive contains a nonregular member: '+name)
                require(name in wanted and name not in seen,'Unexpected/duplicate archive member: '+name)
                require(member.size==wanted[name]['bytes'],'Archive member size differs: '+name)
                payload=tar.extractfile(member);require(payload is not None,'Missing archive payload')
                path=path_in(target,name) if target is not None else None
                if path is not None:path.parent.mkdir(parents=True,exist_ok=True)
                out=path.open('xb') if path is not None else None
                h=hashlib.sha256();g=hashlib.sha1(b'blob '+str(member.size).encode()+b'\0');actual=0
                try:
                    with payload:
                        for block in iter(lambda:payload.read(1<<20),b''):
                            h.update(block);g.update(block);actual+=len(block)
                            if out is not None:out.write(block)
                finally:
                    if out is not None:out.close()
                got={'path':name,'bytes':actual,'sha256':h.hexdigest(),'git_blob':g.hexdigest()}
                require(got==wanted[name],'Archive member digest differs: '+name)
                seen.add(name)
          for block in iter(lambda:decoded.read(1<<20),b''):
              require(not any(block),'Unexpected nonzero payload beyond the declared tar stream')
    require(seen==set(wanted),'Archive member census incomplete')
    return {'kind':archive['kind'],'files':len(seen),'compressed_bytes':size,
            'archive_sha256':combined.hexdigest(),'original_archives_unchanged':True,
            'materialized_copy_created':target is not None,'gzip_crc_and_end_of_stream_verified':True}

def finite(value):
    require(isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value),
            'Expected a finite numeric field')
    return value
