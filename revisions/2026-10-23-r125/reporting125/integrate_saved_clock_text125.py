"""Author-text integration of a descriptive saved-clock profile, no economics."""
from pathlib import Path
import hashlib, json, time

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    tick = time.perf_counter()
    out = ROOT / 'results125/presentation-clockprofile'
    out.mkdir(exist_ok=False)
    manuscript = ROOT / 'new125/numerical_results125.tex'
    companion = ROOT / 'new125/development_results125.tex'
    before = {str(p.relative_to(ROOT)): sha(p) for p in (manuscript, companion)}
    (out/'before_numerical_results125.tex').write_bytes(manuscript.read_bytes())
    (out/'before_development_results125.tex').write_bytes(companion.read_bytes())
    main_text = (ROOT/'reporting125/PENDING_CLOCK_PROFILE_MAIN125.txt').read_text()
    development_text = (ROOT/'reporting125/PENDING_CLOCK_PROFILE_DEVELOPMENT125.txt').read_text()
    source = manuscript.read_text()
    marker = '\\begin{table}[t]\n\\centering\\small\n\\caption{Original economic objectives and decision-loss bounds}'
    assert source.count(marker) == 1 and main_text not in source
    assert '\\label{dev:clockprofile125}' not in companion.read_text()
    manuscript.write_text(source.replace(marker, main_text + marker))
    companion.write_text(companion.read_text() + '\n' + development_text)
    receipt = dict(status='executed', economic_evaluations=0, services_retimed=0,
                   script_sha256=sha(Path(__file__)), before=before,
                   after={str(p.relative_to(ROOT)): sha(p) for p in (manuscript, companion)},
                   profile_sha256=sha(ROOT/'results125/SAVED_CLOCK_PROFILE125.json'),
                   seconds=time.perf_counter()-tick)
    (out/'INTEGRATION125.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
