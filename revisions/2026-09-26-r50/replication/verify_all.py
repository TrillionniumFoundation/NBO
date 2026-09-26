"""Replay every retained proof without invoking a numerical optimizer."""
import sys,json,gzip,hashlib,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;REPO=ROOT.parents[1]
from check_diffuse import verify as diffuse
from check_budget import verify as budget
from check_price import verify as price
sys.path.insert(0,str(REPO/'revisions/2026-09-26-r48/replication'))
import check as old

def main():
 start=time.perf_counter();counts={'diffuse':0,'finite-budget':0,'finite-price':0,'price-audit':0}
 protocol=json.loads((ROOT/'PROTOCOL.json').read_text())
 for name,digest in protocol['code_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 for path in sorted((ROOT/'proofs').glob('*.json.gz')):
  e=json.loads(gzip.decompress(path.read_bytes()))
  if path.name.startswith('price-audit-'):
   case=path.name[len('price-audit-'):-len('.json.gz')];raw=json.loads((REPO/'revisions/2026-09-26-r48/models'/f'{case}.json').read_text());price(e,raw);counts['price-audit']+=1
  elif path.name.startswith('finite-'):
   case=path.name.split('-')[1];raw=json.loads((REPO/'revisions/2026-09-26-r48/models'/f'{case}.json').read_text())
   if '-budget-' in path.name:budget(e,raw);counts['finite-budget']+=1
   else:old.verify(e,raw);counts['finite-price']+=1
  else:
   case=path.name.split('-highs-')[0];raw=json.loads((ROOT/'models'/f'{case}.json').read_text());diffuse(e,raw);counts['diffuse']+=1
 results=list((ROOT/'results').glob('*-highs-*.json'));assert len(results)==78
 assert counts['finite-budget']==counts['finite-price']==24 and counts['price-audit']==8
 assert counts['diffuse']==sum(len(json.loads(p.read_text())['trajectory']) for p in results)
 for p in results+list((ROOT/'results').glob('finite-*.json')):
  e=json.loads(p.read_text())
  for row in e.get('trajectory',[]) if 'highs-' in p.name else [e]:
   if 'proof' in row:assert hashlib.sha256((REPO/row['proof']).read_bytes()).hexdigest()==row['proof_sha256']
 out={'valid':True,'counts':counts,'seconds':time.perf_counter()-start,'frozen_hashes_match':True}
 (ROOT/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
