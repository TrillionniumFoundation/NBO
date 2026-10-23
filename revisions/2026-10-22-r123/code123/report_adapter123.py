"""Published, narrowly scoped correction of R123 reporting sample matching.

The original scientific reporter remains byte-for-byte frozen. This adapter
checks its complete SHA-256, changes only the in-memory price_tables function,
and invokes the original main program. It neither reads economic outcomes for
rule selection nor executes a solver, training, state draw, or timing run.
See REPORTING_AMENDMENT123.md and the separate published reporting boundary.
"""
from __future__ import annotations
import argparse
import ast
import datetime as dt
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import time
import traceback

import report123 as frozen

ROOT = Path(__file__).resolve().parents[1]
FROZEN_REPORT_SHA256 = '7aaf3396b04af4a1334f6cd0a44778f341c9f81739033dc2851811cd7cf8c9fa'
AMENDMENT_NAME = 'REPORTING_AMENDMENT123.json'
BOUNDARY_NAME = 'REPORTING_BOUNDARY123.json'

# Literal, one-occurrence changes to the hash-pinned original function. The
# first cache is indexed by the already declared sample sizes; no sample is
# selected by its economic result. Everything outside price_tables is reused.
REPLACEMENTS = (
    ('''    contrasts = {}
    for k in neural:
        for b in keys:
            if b[0] == k[0] and b[2] != 'relu':
                pairs,_ = paired(data,k,b)
                contrasts[k,b] = (average(max(-TAU,lo) for lo,hi in pairs),
                                  average(min(TAU,hi) for lo,hi in pairs))
    for scenario in SCENARIOS:
''', '''    contrasts = {}
    for n in (32,16):
        for k in neural:
            for b in keys:
                if b[0] == k[0] and b[2] != 'relu':
                    pairs,_ = paired(data,k,b,n=n)
                    contrasts[n,k,b] = (average(max(-TAU,lo) for lo,hi in pairs),
                                      average(min(TAU,hi) for lo,hi in pairs))
    for scenario in SCENARIOS:
        n = 32 if scenario == 'primary32' else 16
        require({clocks[scenario,k]['n'] for k in keys} == {n},
                'Price economics must match the declared scenario cohort')
'''),
    ('                    lo,hi = contrasts[k,b]\n',
     '                    lo,hi = contrasts[n,k,b]\n'),
    ('                        policy_means_conditional_on_32_saved_states=True,statistical_adoption_claim=False,\n',
     '                        policy_means_conditional_on_32_saved_states=n==32,\n'
     '                        policy_means_saved_state_units=n,matching_scenario_sample=True,statistical_adoption_claim=False,\n'),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def patched_source():
    """Return the exact original and three literal edits; no file is edited."""
    path = ROOT/'code123/report123.py'
    require(digest(path) == FROZEN_REPORT_SHA256, 'Frozen reporter identity differs')
    source = path.read_text()
    nodes = [node for node in ast.parse(source).body
             if isinstance(node, ast.FunctionDef) and node.name == 'price_tables']
    require(len(nodes) == 1, 'Exactly one original price_tables function required')
    node = nodes[0]
    original = ''.join(source.splitlines(keepends=True)[node.lineno-1:node.end_lineno])
    corrected = original
    for old,new in REPLACEMENTS:
        require(corrected.count(old) == 1, 'Reporting correction anchor differs')
        corrected = corrected.replace(old,new,1)
    require(len(ast.parse(corrected).body) == 1, 'Correction must define one function only')
    return original,corrected


def make_price_tables(environment=None):
    """Compile the checked function, optionally with constructed-test globals."""
    _,corrected = patched_source()
    namespace = dict(vars(frozen)) if environment is None else dict(environment)
    exec(compile(corrected,'<R123 published price sample correction>','exec'),namespace)
    return namespace['price_tables']


def verify_amendment():
    amendment_path,boundary_path = ROOT/AMENDMENT_NAME,ROOT/BOUNDARY_NAME
    amendment = json.loads(amendment_path.read_text())
    boundary = json.loads(boundary_path.read_text())
    original = json.loads((ROOT/'BOUNDARIES123.json').read_text())
    require(amendment['schema'] == 'nbo.r123.reporting-amendment.v1', 'Wrong reporting amendment schema')
    require(boundary['schema'] == 'nbo.r123.reporting-boundary.v1', 'Wrong reporting boundary schema')
    require(re.fullmatch(r'[0-9a-f]{40}',boundary['amendment_commit']) is not None,
            'A full published amendment commit is required')
    require(boundary['amendment_sha256'] == digest(amendment_path), 'Reporting amendment hash differs')
    for key in ('source_commit','state_commit','source_manifest_sha256','states_sha256'):
        require(amendment[key] == original[key], 'Amendment changed an original boundary: '+key)
    for key in ('source_commit','state_commit'):
        require(boundary[key] == original[key], 'Reporting boundary changed F123/D123: '+key)
    require(amendment['frozen_report_sha256'] == FROZEN_REPORT_SHA256,
            'Amendment refers to a different frozen reporter')
    for name,expected in amendment['files'].items():
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts and str(path)==name,
                'Invalid reporting amendment member')
        require((ROOT/name).resolve().is_relative_to(ROOT), 'Amendment member escapes revision')
        require(digest(ROOT/name) == expected, 'Reporting amendment member differs: '+name)
    for name,expected in amendment['frozen_authority_sha256'].items():
        require(digest(ROOT/name) == expected, 'Original reporting authority differs: '+name)
    _,corrected = patched_source()
    patched_hash = hashlib.sha256(corrected.encode()).hexdigest()
    require(patched_hash == amendment['in_memory_price_tables_sha256'],
            'In-memory correction differs from published amendment')
    return dict(amendment_sha256=digest(amendment_path),boundary_sha256=digest(boundary_path),
                amendment_commit=boundary['amendment_commit'],source_commit=original['source_commit'],
                state_commit=original['state_commit'],files=amendment['files'],
                frozen_authority_sha256=amendment['frozen_authority_sha256'],
                in_memory_price_tables_sha256=patched_hash)


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output',type=Path,required=True)
    args,_ = parser.parse_known_args()
    require(not args.output.exists(), 'A new reporting output directory is required')
    before = verify_amendment()
    frozen.price_tables = make_price_tables()
    tick = time.perf_counter()
    custody = dict(schema='nbo.r123.reporting-adapter-custody.v1',status='running',
                   started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),before=before,
                   original_frozen_report_unchanged=True,original_primary_n=32,
                   timing_scenario_n=16,new_economic_observations=0,new_service_clocks=0,
                   patch_scope='price_tables sample matching and truthful sample-size metadata only')
    try:
        frozen.main()
        after = verify_amendment()
        require(before == after, 'Reporting amendment changed during report execution')
        custody.update(status='passed',exit_code=0,after=after,all_before_after_hashes_equal=True)
    except BaseException:
        custody.update(status='failed',exit_code=1,traceback=traceback.format_exc())
        raise
    finally:
        custody.update(seconds=time.perf_counter()-tick,ended_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        if args.output.is_dir():
            frozen.common.write(args.output/'ADAPTER_CUSTODY123.json',custody)


if __name__ == '__main__':
    main()
