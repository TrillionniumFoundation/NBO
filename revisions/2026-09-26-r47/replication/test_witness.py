"""Adversarial reader smoke tests: every invalid variant must be rejected."""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,copy,sys
from verify_witness import verify_object
R=Path(__file__).resolve().parents[1]
mutations={
 'raised_lower':lambda o:o.update(lower=str(F(o['lower'])+1)),
 'reduced_upper':lambda o:o.update(upper=str(F(o['upper'])-1)),
 'forged_protocol':lambda o:o.update(protocol_sha256='0'*64),
 'forged_source':lambda o:o.update(source_price_sha256='0'*64),
 'forged_model_hash':lambda o:o.update(model_sha256='0'*64),
 'changed_discount':lambda o:o['model'].update(beta='1/2'),
 'changed_target':lambda o:o.update(target='1'),
 'missing_policy':lambda o:o.update(policy=None),
 'negative_probability':lambda o:o['policy'][0][0].__setitem__(0,'-1'),
 'omitted_policy_date':lambda o:o['policy'].pop(),
 'invalid_terminal_lower':lambda o:o['operating_lower'][-1].__setitem__(0,'1000000'),
 'invalid_supersolution':lambda o:o['operating_upper'][0].__setitem__(0,'-1000000'),
 'raised_price_potential':lambda o:o['lower_table'][0].__setitem__(0,'1000000'),
 'forged_lower_budget':lambda o:o.update(lower_error_budget='0'),
 'forged_upper_budget':lambda o:o.update(upper_error_budget='0'),
 'invalid_witness_precision':lambda o:o.update(witness_bits=-1),
 'invalid_policy_precision':lambda o:o.update(policy_bits=-1),
}
rows=[]
for case in ['maintenance1','inventory2','queue1']:
 src=json.loads(gzip.decompress((R/'proofs'/f'{case}_b24.json.gz').read_bytes()));verify_object(src)
 for name,change in mutations.items():
  obj=copy.deepcopy(src);change(obj)
  try:verify_object(obj)
  except (ValueError,AssertionError,KeyError,IndexError,TypeError) as e:rows.append(dict(case=case,mutation=name,rejected=True,reason=str(e)))
  else:raise AssertionError(f'Invalid proof accepted: {case} {name}')
(R/'results/witness_adversarial.json').write_text(json.dumps(dict(passed=True,mutations=len(rows),valid_controls=3,results=rows),indent=2)+'\n')
print('Rejected',len(rows),'invalid objects; accepted 3 valid controls.')
