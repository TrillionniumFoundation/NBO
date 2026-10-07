"""Source-bound correction of inverse-softplus overflow; no catalogue change."""
from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[1]
def main():
    p=R/'code/coupled_training.py';s=p.read_text()
    assert hashlib.sha256(p.read_bytes()).hexdigest()=='262e46db77f6530c17087ec3b8ad39b7c1a494dee5b45efc1e9fbd9ba03ecfe4'
    s=s.replace('def fit(x,y,seed,width=48,steps=300):', '''def inverse_softplus(c):
    """log(exp(c)-1) without overflowing exp(c), for finite positive c."""
    c=np.asarray(c,dtype=float)
    if not np.isfinite(c).all() or np.any(c<=0):raise ValueError('Positive finite coefficient required')
    return c+np.log(-np.expm1(-c))

def fit(x,y,seed,width=48,steps=300):''')
    assert s.count('raw=np.log(np.expm1(c));')==1
    s=s.replace('raw=np.log(np.expm1(c));','raw=inverse_softplus(c);')
    p.write_text(s)
    p=R/'code/tests.py';s=p.read_text();assert s.count('    moment_checks=0')==1
    s=s.replace('    moment_checks=0','''    coefficients=np.array([1e-10,1e-6,.01,1.,20.,700.,1000.,1e6])
    raw=c.inverse_softplus(coefficients)
    assert np.isfinite(raw).all()
    assert np.allclose(np.logaddexp(0,raw),coefficients,rtol=2e-14,atol=1e-14)
    for bad in (0.,-1.,float('inf'),float('nan')):
        try:c.inverse_softplus(np.array([bad]));raise AssertionError('Invalid coefficient accepted')
        except ValueError:pass
    moment_checks=0''')
    p.write_text(s)
if __name__=='__main__':main()
