"""Recover four capped display dictionaries from complete retained key events."""
from pathlib import Path
import collections
import gzip
import hashlib
import json

HERE=Path(__file__).parent
OUT=HERE/'HISTORICAL_remote_closure119'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(65536),b''):h.update(b)
    return h.hexdigest()


def main():
    warnings=json.loads((OUT/'PARSE_WARNING_OBJECTS119.json').read_text())
    results=[]
    target=OUT/'COMPLETE_FIELD_INVENTORIES119.jsonl.gz'
    with gzip.open(target,'wt',encoding='utf-8') as output:
        for w in warnings:
            path=Path(w['record_path'])
            with path.open() as f:
                for n,line in enumerate(f,1):
                    if n==w['record_line']:break
                else:raise AssertionError('Missing original record line')
            assert hashlib.sha256(line.encode()).hexdigest()==w['record_line_sha256']
            record=json.loads(line)
            assert record['parse']['all_matched_events_retained'] is True
            event_file=path.parent/record['events_artifact']['path']
            assert sha(event_file)==record['events_artifact']['sha256']
            fields=collections.Counter()
            with gzip.open(event_file,'rt',encoding='utf-8') as events:
                for text in events:
                    event=json.loads(text)
                    if event['kind']=='json_key':fields[event['key']]+=1
            expected=record['parse']['event_counts']['map_key']
            assert sum(fields.values())==expected
            for k,v in record['parse']['field_occurrences'].items():assert fields[k]==v
            output.write(json.dumps({'git_blob_sha1':w['sha'],'raw_sha256':w['sha256'],
                         'witness_commit':w['witness_commit'],'witness_path':w['witness_path'],
                         'map_key_events':expected,'distinct_field_names':len(fields),
                         'field_occurrences':dict(sorted(fields.items()))},sort_keys=True)+'\n')
            results.append({'sha':w['sha'],'witness_path':w['witness_path'],
                            'distinct_field_names':len(fields),'map_key_events':expected,
                            'events_sha256_verified':True,'all_key_events_counted':True,
                            'all_original_retained_frequencies_match':True,
                            'original_summary_cap_preserved':True})
    summary={'scope':'Derived complete field-name frequency inventories from already retained and hash-verified SAX key events; no source bytes changed or redownloaded.',
             'objects':results,'all_four_completed':len(results)==4,
             'artifact':target.name,'artifact_bytes':target.stat().st_size,
             'artifact_sha256':sha(target),'script_sha256':sha(Path(__file__))}
    (OUT/'COMPLETE_FIELD_INVENTORY_RECEIPT119.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))


if __name__=='__main__':main()
