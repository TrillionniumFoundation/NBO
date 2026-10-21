"""Disclosed post-freeze adapter for one redundant reporter keyword collision.

The F-frozen reporter remains byte-for-byte unchanged. Its statistics input
already stores two raw independent means, while frozen economics() supplies
those same names again to dict(**row, ...). Python rejects duplicate keyword
arguments. Verify the saved values equal the intended exact recomputation,
remove only those two keys from shallow temporary copies, then call the
unchanged frozen implementation. No statistical, cost, menu or sample rule is
changed. Actual use requires this adapter's own immutable reporting commit.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys,time
from fractions import Fraction as Q
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
FROZEN_REPORTER_SHA256='b504bab12124c1a7dab04e5307b30297ab957aa918178c89f9c211556e8b11e2'
FIELDS=('raw_independent_sample_gain_lower','raw_independent_sample_gain_upper')

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def install_adapter(frozen,checks):
    original=frozen.economics
    def schema_checked_economics(data):
        copied={}
        for key,row in data['stats'].items():
            saved=[data['independent'][(key[0],j,*key[1:])] for j in range(frozen.N)]
            temporary=dict(row)
            for name,side in zip(FIELDS,('lower','upper')):
                value=sum((Q(z['independent_gain_'+side]) for z in saved),Q(0))/frozen.N
                if name not in row or Q(row[name])!=value:
                    raise ArithmeticError('Reporting adapter refuses changed raw independent mean: '+repr((key,name)))
                del temporary[name]
                checks['exact_redundant_value_equalities']=checks.get('exact_redundant_value_equalities',0)+1
            copied[key]=temporary
        checks['safe_cells_checked']=checks.get('safe_cells_checked',0)+len(copied)
        result=original(dict(data,stats=copied))
        for row in result[1]:
            key=tuple(row[f] for f in frozen.FIELDS)
            for name in FIELDS:
                if Q(row[name])!=Q(data['stats'][key][name]):
                    raise ArithmeticError('Frozen reporter recomputation changed a checked raw mean')
        checks['frozen_economics_calls']=checks.get('frozen_economics_calls',0)+1
        return result
    frozen.economics=schema_checked_economics

def main():
    original_argv=list(sys.argv)
    if '--repair-commit' not in sys.argv:
        raise ValueError('An independently published --repair-commit is required')
    position=sys.argv.index('--repair-commit');commit=sys.argv[position+1]
    if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('Full immutable reporting adapter commit required')
    own=Path(__file__).resolve();relative=str(own.relative_to(REPO))
    observed=subprocess.check_output(['git','show',commit+':'+relative],cwd=REPO)
    if observed!=own.read_bytes():raise ValueError('Adapter differs from its immutable reporting commit')
    if digest(ROOT/'code122/report122.py')!=FROZEN_REPORTER_SHA256:
        raise ValueError('Original F-frozen reporter bytes changed')
    del sys.argv[position:position+2]
    if '--output' not in sys.argv or '--source-commit' not in sys.argv:
        raise ValueError('Original frozen reporter output and source arguments required')
    output=Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    source=sys.argv[sys.argv.index('--source-commit')+1]
    sys.path.insert(0,str(ROOT/'code122'))
    import report122 as frozen
    checks={};install_adapter(frozen,checks);started=time.perf_counter();status='failed'
    try:
        frozen.main()
        if checks!={'exact_redundant_value_equalities':232,'safe_cells_checked':116,'frozen_economics_calls':1}:
            raise ArithmeticError('Actual complete116-cell adapter census differs')
        status='executed'
    finally:
        if output.is_dir():
            receipt=dict(status=status,source_commit_F=source,reporting_adapter_commit=commit,
                adapter_path=relative,adapter_sha256=digest(own),frozen_reporter_sha256=FROZEN_REPORTER_SHA256,
                actual_command=original_argv,checks=checks,elapsed_seconds=time.perf_counter()-started,
                removed_input_keys_only=list(FIELDS),original_frozen_files_changed=False,
                saved_input_files_changed=False,new_states=0,new_training=0,new_economic_evaluations=0,
                statistical_or_cost_rules_changed=False,original_frozen_attempt_success_asserted=False,
                scope='Only duplicate already-equal raw-mean keyword inputs are removed from shallow in-memory copies before the unchanged frozen economics/report functions run.')
            with (output/'REPORTING_ADAPTER122.json').open('x') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')

if __name__=='__main__':main()
