"""Inspect every R69 receipt and result without changing scientific records."""
from pathlib import Path
from collections import Counter
import json,hashlib,sys,statistics
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-11-r69'
sys.path.insert(0,str(OLD/'code'))
import science69 as s

def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(name,value):
    p=R/'audit'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def main():
    binding=s.verify();rows=[];files=0
    for spec in s.specs():
        folder=OLD/'results69'/spec['key'];receipt=read(OLD/'receipts69'/(spec['key']+'.json'));j=read(folder/'summary.json')
        assert receipt['spec']==spec and j['spec']==spec
        assert receipt['source_freeze_sha256']==binding==j['source_freeze_sha256']
        assert receipt['summary_sha256']==sha(folder/'summary.json')
        assert receipt['log_sha256']==sha(OLD/'logs69'/(spec['key']+'.log'))
        for name,h in j.get('files_sha256',{}).items():
            assert sha(folder/name)==h,(spec['key'],name);files+=1
        row=dict(spec=spec,status=j['status'],returned=receipt['returned'],seconds=receipt['complete_process_seconds'],rss=j.get('peak_rss_kib'),counts=j.get('counts'),training=j.get('training'),validation=j.get('validation'),account=j.get('account'),hardware=j.get('hardware_start'))
        if spec['group']=='inference':
            row.update(centered=j.get('centered'),raw_cost=j.get('raw_cost'),arms=j.get('arms'))
        if spec['group']=='reuse':
            row['initial_seconds']=j['initial_seconds'];row['blocks']=j['blocks']
            if len(j['blocks'])!=64:raise AssertionError('Incomplete reuse')
        rows.append(row)
    save('CATALOGUE70.json',dict(source_commit='2c07e464e81930f14b3122054704731ec5a139ff',freeze_sha256=binding,files_checked=files,rows=rows))
    summary=dict(planned=len(rows),returned=sum(x['returned'] for x in rows),status_counts=dict(Counter(x['status'] for x in rows)),files_checked=files,cold=[],reuse=[],validation=[],inference=[],vector=[],warnings=[])
    for group in ('comparison','reuse','vector'):
        group_rows=[x for x in rows if x['spec']['group']==group]
        keys=sorted({(x['spec']['d'],x['spec']['T'],x['spec']['kind']) for x in group_rows})
        for d,T,kind in keys:
            sample=[x for x in group_rows if (x['spec']['d'],x['spec']['T'],x['spec']['kind'])==(d,T,kind)]
            result=dict(d=d,T=T,kind=kind,n=len(sample),seconds_median=statistics.median(x['seconds'] for x in sample),seconds_range=[min(x['seconds'] for x in sample),max(x['seconds'] for x in sample)],rss_max=max(x['rss'] for x in sample),q_queries=[x['counts'].get('q_queries') if x['counts'] else None for x in sample])
            if group=='reuse':
                result['wins']=0;result['stable_crossings']=[];result['q_queries']=[]
                for x in sample:
                    ref=next(z for z in group_rows if z['spec']['d']==d and z['spec']['T']==T and z['spec']['kind']=='adaptive' and z['spec']['repeat']==x['spec']['repeat'])
                    result['wins']+=x['seconds']<ref['seconds']
                    differences=[a['cumulative_from_entry']-b['cumulative_from_entry'] for a,b in zip(x['blocks'],ref['blocks'])]
                    crossing=next((i for i in range(49) if all(v<0 for v in differences[i:])),None)
                    result['stable_crossings'].append(crossing)
                    result['q_queries'].append(sum(b['counts'].get('q_queries',0) for b in x['blocks']))
                    assert [b['block'] for b in x['blocks'] if not b['identity_valid']]==[16]
                    assert x['blocks'][16]['used_kind']=='adaptive'
            summary[{'comparison':'cold','reuse':'reuse','vector':'vector'}[group]].append(result)
    for x in rows:
        for date in (x.get('training') or {}).get('dates',[]):
            if not date.get('optimizer',{}).get('success',True):summary['warnings'].append(dict(key=x['spec']['key'],date=date))
        if x['spec']['group']=='validation':summary['validation'].append(dict(spec=x['spec'],dates=x['validation']))
        if x['spec']['group']=='inference':
            arms={}
            for kind,v in x['arms'].items():
                a=v['accounts'];arms[kind]=dict(seconds=v['seconds'],ambiguous_paths=sum(y['ambiguous_paths'] for y in a),evaluation_q_queries=sum(y['evaluation_work']['q_queries'] for y in a),G=a[0]['center_upper_exact'],conditional_mean=statistics.mean(y['mean_raw_conditional_width'] for y in a),bin_mean=statistics.mean(y['mean_state_expansion'] for y in a))
            summary['inference'].append(dict(spec=x['spec'],seconds=x['seconds'],centered=x['centered'],raw_cost=x['raw_cost'],arms=arms))
    save('SUMMARY70.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='validation'},indent=2))
if __name__=='__main__':main()
