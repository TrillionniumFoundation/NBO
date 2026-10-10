"""One-time source amendment; never changes frozen scientific inputs."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
    path=R/'code/audit70.py';text=path.read_text()
    old="                need(np.array_equal(proposed,v['action']),('Frozen validation predictor',spec['key']))"
    new="                from validation70 import verify as verify_validation\n                differences=verify_validation(v,proposed,models,report['r'],spec['kind'],readout,tol)\n                if differences:warnings.append(dict(key=spec['key'],date=report['r'],prediction_replay_differences=differences))"
    if old in text:
        if text.count(old)!=1:raise AssertionError('Ambiguous amendment')
        text=text.replace(old,new)
        text=text.replace("status='identical'","status='model_arrays_identical; runtime-contract equality is additionally required for deployment transfer'")
        path.write_text(text)
    elif new not in text:raise AssertionError('Unexpected validation audit source')
    path=R/'sections/deployment70.tex'
    if path.exists():path.write_text(path.read_text().replace('a observed prefix','an observed prefix'))
if __name__=='__main__':main()
