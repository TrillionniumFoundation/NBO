"""Losslessly expand compact transport records; never rerun Bellman services.

Blocks duplicated in summaries and receipt digests are reconstructed. The
rational moment catalogue is regenerated deterministically and matched against
the sealed hash of every original scientific file. All original timings and
hardware observations are restored, not replaced with replay clocks.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1]
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    payload=json.loads((R/'record_payload72.json').read_text());target=R/'results72'
    if target.exists() and any(target.iterdir()):
        manifest={str(p.relative_to(target)):sha(p) for p in sorted(target.rglob('*')) if p.is_file()}
        raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
        if hashlib.sha256(raw).hexdigest()!=payload['manifest_sha256']:raise AssertionError('Existing scientific data differ; refusing overwrite')
        print('All original scientific bytes already present and match the sealed manifest.');return
    target.mkdir(parents=True,exist_ok=True)
    freeze=R/'SOURCE_FREEZE72.json'
    if not freeze.exists():subprocess.run([sys.executable,str(R/'code/science72.py'),'--freeze'],stdout=subprocess.DEVNULL,check=True)
    if sha(freeze)!='f3d1c542cb6b5dfbe4cb8d470bef48c17080b58077ce983337ca622f3afa0468':raise AssertionError('Pre-execution source commitment differs')
    receipts={}
    for key,record in payload['services'].items():
        folder=target/key;folder.mkdir()
        for name in ('summary','trace','cache'):save(folder/(name+'.json'),record[name])
        (folder/'process.log').write_text(record['process_log'])
        for block in record['summary']['blocks']:save(folder/f"block-{block['index']:03d}.json",block)
        receipt={**record['receipt'],'files_sha256':{p.name:sha(p) for p in folder.iterdir() if p.is_file()}}
        save(folder/'receipt.json',receipt);receipts[key]=receipt
    for index,order in payload['catalogue_order'].items():save(target/f'catalogue-{index}.json',[receipts[k] for k in order])
    subprocess.run([sys.executable,str(R/'code/science72.py'),'--integration'],check=True)
    save(target/'conditional-summary.json',payload['conditional_summary'])
    manifest={str(p.relative_to(target)):sha(p) for p in sorted(target.rglob('*')) if p.is_file()}
    raw=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    got=hashlib.sha256(raw).hexdigest()
    if got!=payload['manifest_sha256']:raise AssertionError(('Lossless reconstruction failed',got,payload['manifest_sha256']))
    (R/'audit').mkdir(exist_ok=True);(R/'audit/SCIENTIFIC_RECORDS72.json').write_bytes(raw)
    save(R/'audit/RECORD_RECOVERY72.json',dict(status='passed',files=len(manifest),original_manifest_sha256=got,
        original_process_clocks_preserved=True,Bellman_services_rerun=False,
        scope='All 895 original scientific files reconstructed byte-for-byte; deterministic rational moments regenerated, not new scientific observations.'))
    print(json.dumps(dict(status='passed',files=len(manifest),manifest_sha256=got)))
if __name__=='__main__':main()
