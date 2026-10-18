"""Materialize the diagnostic-only amendment as an ordinary, inspectable runner.
The first-fit source stays unchanged. No actor, seed, tolerance or solver is edited.
"""
from pathlib import Path
import ast, hashlib, json
R=Path(__file__).resolve().parents[1]
source=R/'code/shared89.py'; target=R/'code/run89.py'
text=source.read_text()
old="            progress = np.asarray(oracle.progress)\n            zero_progress = sum(float(row[8]) <= 0 and float(row[9]) <= 0 for row in oracle.progress)"
new="            progress = np.concatenate(oracle.progress, axis=0) if oracle.progress else np.empty((0,13))\n            zero_progress = sum(float(row[8]) <= 0 and float(row[9]) <= 0 for row in progress)"
assert text.count(old)==1
fixed=text.replace(old,new)
oldsave="    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\\n')"
newsave="    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False, default=lambda x: x.tolist() if isinstance(x,np.ndarray) else x.item() if isinstance(x,np.generic) else (_ for _ in ()).throw(TypeError(type(x).__name__))) + '\\n')"
assert fixed.count(oldsave)==1
fixed=fixed.replace(oldsave,newsave)
# AST identity outside the recorder and JSON serializer proves the scope of amendment.
a=ast.parse(text);b=ast.parse(fixed)
for node in (a,b):
    node.body=[x for x in node.body if not isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) or x.name not in ('save','run_rows')]
assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
target.write_text(fixed)
audit=R/'audit';audit.mkdir(exist_ok=True)
(audit/'RECORDING_AMENDMENT89.json').write_text(json.dumps({'original_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'amended_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'changed_functions':['save','run_rows'],'unchanged_science_ast':True,'reason':'The inherited diagnostic API stores lists of two-dimensional batches, not a flat list of rows. Flatten batches for the zero-progress statistic and serialize NumPy arrays without changing their values.','refit':False,'changed_seed':False,'changed_tolerance':False,'changed_oracle':False},sort_keys=True,indent=2)+'\n')
print(str(target))
