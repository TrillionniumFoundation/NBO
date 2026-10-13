"""Idempotent correction of the R81 derived-table count before source binding."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parents[1]
TABLES=('basis81','calibration-gains81','interactions81','stability81','optimizer-classes81','precision81','work81','all-factorial81')

def main():
    path=R/'code/tables81.py';old=path.read_text();needle='tables=9)'
    if needle in old:
        if old.count(needle)!=1:raise AssertionError('Ambiguous table-count correction')
        new=old.replace(needle,'tables=8)',1);ast.parse(new);path.write_text(new)
    else:
        new=old
        if 'tables=8)' not in new:raise AssertionError('Unexpected table metadata')
    if len(TABLES)!=8:raise AssertionError('Table catalogue count')
    for name in TABLES:
        if "'"+name+"'" not in new:raise AssertionError('Missing table generator '+name)
    rec=dict(status='passed',table_count=8,table_names=TABLES,
        corrected_field='tables in TABLES81.json',numerical_results_modified=False,manuscript_modified=False,
        generator_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (R/'audit/TABLE_CATALOGUE81.json').write_text(json.dumps(rec,sort_keys=True,indent=2)+'\n')
    print(json.dumps(rec,indent=2))
if __name__=='__main__':main()
