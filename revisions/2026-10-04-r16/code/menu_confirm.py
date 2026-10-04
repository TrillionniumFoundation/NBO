"""Source-bound menu confirmation after all five complete fits are durable."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import resource
import sys
import time
import traceback
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from menu_economy import fixed_queries,load_economy,scalar_query_spec,canonical_hash
from menu_worker import verify_source,write,sha
from menu_verify import METHODS,verify_arrays,verify_scalar


def read(path):return json.loads(Path(path).read_text())


def preflight(fits,economy,queries,source,source_files,protocol_path,*,seed):
    """All fifteen fitted outputs must exist before any confirmation draw."""
    fits=Path(fits); records={}; inputs={}; actions={1:{},2:{},3:{}}
    protocol_hash=sha(protocol_path); protocol=read(protocol_path)
    for method in METHODS:
        base=fits/method; workpath=base/'FIT_WORK.json'; work=read(workpath)
        identity=(work.get('method'),work.get('calibration'),work.get('dimension'),work.get('seed'))
        if identity!=(method,economy.calibration['id'],economy.dimension,int(seed)):
            raise ValueError('fit belongs to another method, calibration, dimension, or seed')
        if work['source_commit']!=source or work['protocol_sha256']!=protocol_hash or work['final_confirmation_read']:
            raise ValueError('fitting source, protocol, or information barrier mismatch: '+method)
        if set(work['source_files'])!=set(source_files):
            raise ValueError('fit source closure differs from the complete frozen source closure')
        for path,actual in source_files.items():
            saved=work['source_files'].get(path)
            if saved is None or saved['sha256']!=actual['sha256'] or saved['bytes']!=actual['bytes']:
                raise ValueError('fit does not have the same complete frozen source closure')
        for name,item in work['payload_inventory'].items():
            p=base/name
            relative=Path(name)
            if (relative.is_absolute() or '..' in relative.parts or p.is_symlink() or
                any(parent.is_symlink() for parent in p.parents if parent!=base.parent and parent.is_relative_to(base)) or
                not p.resolve().is_relative_to(base.resolve()) or not p.is_file()):
                raise ValueError('invalid or missing fit payload: '+str(p))
            if p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:
                raise ValueError('fit payload hash mismatch: '+str(p))
            inputs[str(p.resolve())]=item['sha256']
        inputs[str(workpath.resolve())]=sha(workpath)
        for stage in [1,2,3]:
            path=base/f'stage{stage}.json'; row=read(path)
            if str(path.resolve()) not in inputs:
                raise ValueError('stage record is absent from the completed fit inventory')
            if row.get('schema')!='nbo-r16-menu-sealed-stage-v1' or row.get('sealed') is not True:
                raise ValueError('stage record was not atomically sealed by the completed worker')
            if (row.get('calibration'),row.get('dimension'),row.get('seed'),row.get('source_commit'))!=(
                    economy.calibration['id'],economy.dimension,int(seed),source):
                raise ValueError('sealed stage belongs to another economic trial or source')
            if row['stage']!=stage or row['method']!=method or row['continuation_sha256']!=economy.continuation_sha256:
                raise ValueError('stage identity mismatch')
            if row['query_catalog_sha256']!=queries['catalog_sha256']:
                raise ValueError('the saved actor was deployed on another catalog')
            actionpath=base/row['actions_file']
            if actionpath.resolve().parent!=base.resolve() or sha(actionpath)!=row['actions_sha256']:
                raise ValueError('saved action identity mismatch')
            if str(actionpath.resolve()) not in inputs:
                raise ValueError('stage actions are absent from the completed fit inventory')
            with np.load(actionpath,allow_pickle=False) as data:
                for key in ['states','state_id','task_id','utility_weight','adjustment','lower','upper']:
                    if not np.array_equal(np.asarray(data[key]),np.asarray(queries[key])):
                        raise ValueError('saved action query mismatch: '+key)
                actions[stage][method]=np.asarray(data['actions'],dtype=np.float64).copy()
            records[method,stage]=row
    scalarpath=fits/'nbo_scalar/SCALAR_CANDIDATE.json'
    if str(scalarpath.resolve()) not in inputs:
        raise ValueError('scalar candidate not present in the durable pre-confirmation fit inventory')
    scalar=read(scalarpath)
    if scalar.get('seed')!=int(seed) or scalar.get('stage')!=3:
        raise ValueError('scalar candidate belongs to another seed or work stage')
    specification=scalar_query_spec(protocol,economy)
    for key,value in specification.items():
        if canonical_hash(scalar.get(key))!=canonical_hash(value):
            raise ValueError('scalar candidate differs from the prescribed state, task, or segment: '+key)
    if not scalar.get('primary_vector_candidate_unchanged',False):
        raise ValueError('scalar selection changed the primary vector candidate')
    return actions,records,scalar,inputs


def save_npz(path,arrays):
    np.savez_compressed(path,**arrays)
    with Path(path).open('rb') as f:os.fsync(f.fileno())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol',type=Path,required=True)
    parser.add_argument('--calibration',required=True)
    parser.add_argument('--dimension',type=int,required=True)
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--fits',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    start=time.perf_counter(); usage=resource.getrusage(resource.RUSAGE_SELF)
    protocol=read(args.protocol)
    if args.seed not in protocol['training_streams']['seeds']:
        raise ValueError('undeclared complete training stream')
    source,source_files=verify_source(args.protocol,protocol)
    economy=load_economy(protocol,args.calibration,args.dimension)
    queries=fixed_queries(protocol,args.dimension)
    actions,fit_records,scalar,inputs=preflight(args.fits,economy,queries,source,source_files,args.protocol,seed=args.seed)
    out=args.out.resolve()
    if out.exists() and any(out.iterdir()):raise FileExistsError('confirmation cannot overwrite previous evidence')
    out.mkdir(parents=True,exist_ok=True)
    write(out/'START.json',dict(schema='nbo-r16-menu-confirmation-start-v1',
        source_commit=source,protocol_file_sha256=sha(args.protocol),
        calibration=args.calibration,dimension=args.dimension,seed=args.seed,
        all_five_methods_and_three_stages_durable=True,input_files=inputs,
        continuation_sha256=economy.continuation_sha256,query_catalog_sha256=queries['catalog_sha256']))
    failed=None; stage_work=[]; scalar_work=None
    try:
        for stage in [1,2,3]:
            record,arrays=verify_arrays(economy,queries,actions[stage],protocol,
                seed=args.seed,stage=stage,batch_rows=protocol['confirmation'].get('batch_rows',1024))
            raw=out/f'stage{stage}.npz';save_npz(raw,arrays)
            record.update(source_commit=source,source_files=source_files,
                protocol_file_sha256=sha(args.protocol),raw_file=raw.name,raw_sha256=sha(raw),
                fit_records={method:fit_records[method,stage] for method in METHODS})
            write(out/f'stage{stage}.json',record)
            stage_work.append(record['work'])
            print(json.dumps(dict(stage=stage,complete=True,independent_pairs=record['independent_observations'])),flush=True)
        record,arrays=verify_scalar(economy,None,scalar,protocol,seed=args.seed,
            batch_rows=protocol['confirmation'].get('batch_rows',1024))
        raw=out/'scalar.npz';save_npz(raw,arrays)
        record.update(source_commit=source,source_files=source_files,
            protocol_file_sha256=sha(args.protocol),raw_file=raw.name,raw_sha256=sha(raw))
        write(out/'scalar.json',record);scalar_work=record['work']
        for filename,digest in inputs.items():
            if sha(filename)!=digest:raise ValueError('a fixed candidate changed during independent confirmation')
        print(json.dumps(dict(scalar_complete=True,accuracy_gap_upper=record['implemented_candidate_gap_upper'])),flush=True)
        write(out/'RESULT.json',dict(schema='nbo-r16-menu-complete-confirmation-v1',complete=True,
            source_commit=source,source_files=source_files,protocol_file_sha256=sha(args.protocol),
            calibration=args.calibration,dimension=args.dimension,seed=args.seed,
            continuation_sha256=economy.continuation_sha256,query_catalog_sha256=queries['catalog_sha256'],
            stages={str(s):dict(record_file=f'stage{s}.json',record_sha256=sha(out/f'stage{s}.json'),
                                raw_file=f'stage{s}.npz',raw_sha256=sha(out/f'stage{s}.npz')) for s in [1,2,3]},
            scalar=dict(record_file='scalar.json',record_sha256=sha(out/'scalar.json'),
                        raw_file='scalar.npz',raw_sha256=sha(out/'scalar.npz'))))
    except Exception as exc:
        failed=exc
        write(out/'FAILURE.json',dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc()))
    finally:
        after=resource.getrusage(resource.RUSAGE_SELF)
        inventory={str(p.relative_to(out)):dict(sha256=sha(p),bytes=p.stat().st_size)
                   for p in sorted(out.rglob('*')) if p.is_file() and p.name!='CONFIRMATION_WORK.json'}
        write(out/'CONFIRMATION_WORK.json',dict(schema='nbo-r16-menu-confirmation-work-v1',
            complete=failed is None,source_commit=source,protocol_file_sha256=sha(args.protocol),
            calibration=args.calibration,dimension=args.dimension,seed=args.seed,
            elapsed_since_entry_seconds=time.perf_counter()-start,
            clock_scope='entry through input validation, constants, all three confirmations, scalar assessment and durable scientific outputs; enclosing process launch is timed by the pipeline',
            user_cpu_seconds=after.ru_utime-usage.ru_utime,system_cpu_seconds=after.ru_stime-usage.ru_stime,
            peak_rss_bytes=int(after.ru_maxrss)*1024,stage_work=stage_work,scalar_work=scalar_work,
            payload_inventory=inventory))
    if failed is not None:raise failed


if __name__=='__main__':main()
