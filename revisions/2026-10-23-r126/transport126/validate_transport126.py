#!/usr/bin/env python3
"""Fresh byte restoration and refusal tests; no scientific calculations."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys,tempfile,time,importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('restore126_validation',ROOT/'transport126/restore126.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
identity=module.identity;tick=time.perf_counter()
index=json.loads((ROOT/'DATA_TRANSPORT126.json').read_text());assert index['kind']=='data' and len(index['files'])==1
record=index['files'][0];canonical=ROOT/record['path'];before=identity(canonical)
assert module.same(before,record)
assert subprocess.check_output(['git','hash-object',str(canonical)],text=True).strip()==record['git_blob']
base=Path(tempfile.mkdtemp(prefix='nbo-r126-transport-test-',dir='/dev/shm' if Path('/dev/shm').is_dir() else None))
fresh=base/'fresh';fresh.mkdir()
receipts=[]
def call(script,args,name,expected):
    receipt=ROOT/'transport126/attempts'/name
    command=[sys.executable,str(script),*args,'--output',str(receipt)]
    proc=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    (receipt/'stdout.log').write_text(proc.stdout);(receipt/'stderr.log').write_text(proc.stderr)
    actual=json.loads((receipt/'EXECUTION126.json').read_text())
    assert proc.returncode==expected and actual['exit_code']==expected,(name,proc.returncode,actual)
    receipts.append({'test':name,'expected_exit_code':expected,'actual_exit_code':proc.returncode,'path':(receipt/'EXECUTION126.json').relative_to(ROOT).as_posix(),'sha256':hashlib.sha256((receipt/'EXECUTION126.json').read_bytes()).hexdigest()})
    return actual
first=call(ROOT/'transport126/restore126.py',['--destination-root',str(fresh)],'fresh-restore01',0)
assert first['files'][0]['status']=='restored' and first['files'][0]['parts_read']==3
assert identity(fresh/record['path'])==before
(fresh/'transport126').mkdir();shutil.copyfile(ROOT/'transport126/restore126.py',fresh/'transport126/restore126.py');shutil.copyfile(ROOT/'DATA_TRANSPORT126.json',fresh/'DATA_TRANSPORT126.json')
assert not (fresh/'transport126/parts').exists()
second=call(fresh/'transport126/restore126.py',['--data'],'existing-without-parts01',0)
assert second['files'][0]['status']=='verified_existing' and second['files'][0]['parts_read']==0
unequal=base/'unequal';target=unequal/record['path'];target.parent.mkdir(parents=True);target.write_bytes(b'known unequal canonical sentinel\n');sentinel=identity(target)
third=call(ROOT/'transport126/restore126.py',['--destination-root',str(unequal)],'unequal-existing-refusal01',1)
assert identity(target)==sentinel and 'not overwritten' in third['error']
corrupt=base/'corrupt';(corrupt/'transport126').mkdir(parents=True);shutil.copyfile(ROOT/'transport126/restore126.py',corrupt/'transport126/restore126.py');shutil.copyfile(ROOT/'DATA_TRANSPORT126.json',corrupt/'DATA_TRANSPORT126.json')
part=corrupt/record['parts'][0]['path'];part.parent.mkdir(parents=True);part.write_bytes(b'corrupt fragment\n')
fourth=call(corrupt/'transport126/restore126.py',[],'corrupt-fragment-refusal01',1)
assert not (corrupt/record['path']).exists() and 'Fragment byte identity mismatch' in fourth['error']
assert not list(corrupt.rglob('.restore126-*'))
assert identity(canonical)==before
# Delete only the large duplicate created and verified by this validation.
duplicate=fresh/record['path'];require=identity(duplicate);assert require==before;duplicate.unlink()
assert not duplicate.exists() and identity(canonical)==before
sources=['DATA_TRANSPORT126.json','transport126/restore126.py','transport126/make_transport126.py','transport126/validate_transport126.py','transport126/README.md']
result={'schema':'nbo-r126-byte-transport-validation-v1','status':'passed','data_index':'DATA_TRANSPORT126.json','canonical_path':record['path'],'canonical_identity':before,
 'validated_source_hashes':{x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in sources},
 'parts':len(record['parts']),'part_limit':module.LIMIT,'fresh_restore_passed':True,'existing_file_without_parts_passed':True,
 'unequal_existing_file_refused_unchanged':True,'corrupt_fragment_refused_without_canonical_output':True,
 'canonical_original_unchanged':True,'generated_large_duplicate_deleted':True,'deleted_duplicate_path':str(duplicate),'external_test_root':str(base),
 'attempts':receipts,'archive_transport_generated':False,'economic_evaluations':0,'scientific_calculations':0,'seconds':time.perf_counter()-tick,'completed_utc':module.utc()}
with (ROOT/'transport126/VALIDATION126.json').open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
print(json.dumps(result,sort_keys=True))
