"""Record numerical provenance without collecting credentials or secrets."""
import platform,subprocess,sys
from common import *
import scipy,mpmath,numba
if __name__=='__main__':
    shard=sys.argv[1];out=R/'results'/shard;out.mkdir(parents=True,exist_ok=True)
    write(out/'ENVIRONMENT.json',dict(source_commit=source(),protocol_sha256=digest(R/'PROTOCOL.json'),python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,torch=torch.__version__,numba=numba.__version__,mpmath=mpmath.__version__,platform=platform.platform(),processor=platform.processor(),threads={k:os.environ.get(k) for k in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']},source_files={str(p.relative_to(ROOT)):digest(p) for p in (R/'code').glob('*.py')}))
    (out/'requirements-executed.txt').write_bytes(subprocess.check_output([sys.executable,'-m','pip','freeze']))
