"""Independently check task, context, count and receipt admission boundaries.

This supplements the frozen arithmetic checker without modifying the original
scientific sources or observations. It imports no production implementation.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
R=Path(__file__).resolve().parents[1]
def need(x,label):
    if not x:raise AssertionError(label)
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    freeze=read(R/'SOURCE_FREEZE72.json');expected='f3d1c542cb6b5dfbe4cb8d470bef48c17080b58077ce983337ca622f3afa0468'
    need(sha(R/'SOURCE_FREEZE72.json')==expected,'pre-execution commitment')
    manifest={str(p.relative_to(R/'results72')):sha(p) for p in sorted((R/'results72').rglob('*')) if p.is_file()}
    blob=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    need(hashlib.sha256(blob).hexdigest()=='7c50690a3e7b08daf0afa8660335d5a9d71bf85f30148c7a17ffeb82ac42f582','sealed original scientific record tree')
    count=0;processes=0
    for task in freeze['tasks']:
        for rep in range(task['repetitions']):
            for mode in freeze['modes']:
                folder=R/'results72'/f"{task['name']}-{mode}-r{rep}";s=read(folder/'summary.json');receipt=read(folder/'receipt.json');trace=read(folder/'trace.json')
                need(s['task']==task and s['mode']==mode and s['repetition']==rep,'task identity')
                need(receipt['returncode']==0 and receipt['source_freeze_sha256']==expected,'process return identity')
                need(len(s['hardware_start']['affinity'])==1 and not s['hardware_start']['frequency_locked'],'declared hardware scope')
                need(len(trace)==len(s['blocks'])==task['blocks'],'full workload length')
                total=0
                for j,(row,block) in enumerate(zip(trace,s['blocks'])):
                    x=[F(float(.4)),F(float(.6))]*(task['d']//2)
                    if task['far'] and j==task['blocks']-2:x=[F(3,4)]*task['d']
                    elif j>0 and j%2==0:x[j%task['d']]+=F(-1 if j%4==0 else 1,2**20)
                    context='original-v2' if task['invalid'] is not None and j>=task['invalid'] else 'original-v1'
                    need(list(map(F,row['state']))==x,'prespecified state')
                    need(row['context']==context and row['remaining']==task['T'],'law epoch and horizon')
                    need(len(row['action'])==task['m'] and F(row['tolerance'])==F(task['tol']),'control and precision contract')
                    need(block['index']==j and block['kind']==row['kind'],'block identity')
                    need(block['additional_q_queries']>=0 and (row['kind']!='hit' or block['additional_q_queries']==0),'descendants charged on hits')
                    total+=block['additional_q_queries'];count+=1
                need(total==s['recursive_counts']['q_queries'],'complete descendant count')
                need(receipt['complete_process_seconds']>=s['service_body_seconds'],'complete clock boundary')
                need(s['new_statistical_policy_cost_rows']==0,'observation scope')
                processes+=1
    report=dict(status='passed',processes=processes,query_contracts=count,scientific_files=len(manifest),sealed_manifest_sha256=hashlib.sha256(blob).hexdigest(),controls_state_horizon_epoch_and_tolerance_checked=True,scope='Recorded cache reloads are same-process, same-model records. Arbitrary externally supplied bounds are not certified merely by deserialization or a file hash.')
    (R/'audit/TASK_CONTRACT72.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
