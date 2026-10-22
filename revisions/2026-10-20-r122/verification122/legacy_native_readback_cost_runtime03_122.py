"""Bind two separately saved native readback clocks omitted by frozen glob scopes.

This new additive reader does not rewrite old receipts or the frozen ledger.
Their native readback operations followed the corresponding publication API
operations; no publication clock or older research total is copied as a charge.
"""
from pathlib import Path
from fractions import Fraction as Q
import datetime as dt
import hashlib
import json
import time
ROOT=Path(__file__).resolve().parents[1]
CASES=[('provenance122/RESUME_PUBLICATION_READBACK122.json','e74e61649665339024fb0c3ff80f51631213ca8078b5125604b819bc64b51ed1','elapsed_seconds','0fe0f2bbf76529201a1890db0fc2a94b0be44418','commit'),('provenance122/SOURCE_CHECKPOINT_READBACK122.json','778929bc2f6df7fa071c0d02b7a4455ea49c93ff85cc8c9f576f204c675d7576','seconds','e4e3f3fd67ac79acd41d9c69012dd6dca6c18f4e','remote_commit')]
def main():
 start=time.perf_counter(); rows=[]
 out=ROOT/'provenance122/runtime_recovery_after_upload_reset/LEGACY_NATIVE_READBACK_COST122.json'
 assert not out.exists()
 for name,expected,field,commit,commit_field in CASES:
  p=ROOT/name; data=p.read_bytes(); assert hashlib.sha256(data).hexdigest()==expected
  obj=json.loads(data); assert obj['status']=='verified' and obj[commit_field]==commit
  assert not obj.get('cost_clock_components') and p.parent==ROOT/'provenance122' and not p.name.endswith('PUBLICATION122.json')
  elapsed=Q(obj[field]); assert elapsed>=0
  rows.append(dict(source_path=name,source_sha256=expected,source_bytes=len(data),saved_clock_field=field,seconds_exact=str(elapsed),source_scope=obj['scope'],distinct_observed_native_readback=True))
 result=dict(schema='nbo.r122.legacy-native-readback-cost.v1',status='verified_two_saved_nonautomatic_readback_clocks',created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),reader_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,elapsed_seconds=time.perf_counter()-start,new_economic_evaluations=0,
  cost_clock_components=[dict(category='prior_native_publication_readback',clock_fields=[['rows',i,'seconds_exact']],partial_lower_bound_only=True,overlaps_counted_parent=False,scope='Separately saved native Git/readback process after publication; the frozen automatic scopes do not include this top-level non-PUBLICATION receipt.') for i in range(len(rows))]+[dict(category='native_readback_cost_reader',clock_fields=[['elapsed_seconds']],partial_lower_bound_only=True,overlaps_counted_parent=False,scope='Actual separate new reader only; initial interpreter startup and receipt serialization excluded.')],
  excluded_other_scopes=['Corresponding publication API clocks remain in their original separately counted receipts','The published R120 three native restoration clocks are separately included by their existing declared components','No lost unpublished bridge identity or lost elapsed duration is recovered'],whole_study_exact_total_seconds=None)
 with out.open('x') as stream:json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
 print(json.dumps({'status':result['status'],'old_seconds_exact':str(sum((Q(x['seconds_exact']) for x in rows),Q(0))),'reader_elapsed_seconds':result['elapsed_seconds']}))
if __name__=='__main__': main()
