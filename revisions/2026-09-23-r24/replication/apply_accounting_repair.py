"""Metadata-only repair: a reference economy has no financing root.

This correction was specified while the first complete scientific execution was
running, before inspecting reference-model performance. It changes neither the
proposal objective, optimizer, tuning rule, seeds, checkpoints, nor certificates.
The original source payload and failed execution remain in the audit trail.
"""
from pathlib import Path
import hashlib,json
p=Path(__file__).with_name('study.py')
s=p.read_text()
a="'root_accounting':asdict(obj.accounting)"
b="'root_accounting':{k:(v if not isinstance(v,float) or math.isfinite(v) else None) for k,v in asdict(obj.accounting).items()}"
before=hashlib.sha256(s.encode()).hexdigest()
if a in s:
    assert s.count(a)==1
    s=s.replace(a,b);p.write_text(s)
else:
    assert b in s,'Unexpected scientific source: refuse to patch'
out=p.parent.parent/'results/accounting_repair.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'purpose':'Encode an unused infinite root-conditioning diagnostic as JSON null in a model without a financing equation','before_sha256':before,'after_sha256':hashlib.sha256(s.encode()).hexdigest(),'scientific_parameters_changed':False,'patch':{'old':a,'new':b}},indent=2)+'\n')
print('Reference metadata repair checked; no scientific design changed.')
