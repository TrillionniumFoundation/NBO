"""Install the complete reading sources from immutable reviewed editorial inputs.

The original editorial payload is verified before use. Completed-evidence edits
are readable text, applied to that exact payload, and checked against the exact
sources that passed the full local three-document build. No scientific data is
changed, and an incomplete or altered source cannot enter the publication gate.
"""
from pathlib import Path,PurePosixPath
import base64,hashlib,json,zlib
S=Path(__file__).resolve().parent
P=S.parent
EXPECTED={
 'COMMENT_STATUS.json':'ef976e36fd3cdc1b385ef86209e40ff0f718f245307da3a8ae65c6ec34d3ea4d',
 'README.md':'322afe50a907feba65398cfc783a13281eb9c3ff70f483953266c641ed70275b',
 'ROOT_README.md':'f463ff279c4cd4e5f94b92739486766137cd96db741592617cc3867e193b2fda',
 'code/assemble_publication.py':'a819341178ce3f3c24cd9dabd4953ed6501c66b20e50dd80e80b3945d2c31167',
 'code/completed_evidence_audit.py':'93d09aed89a05c9eb6b7b368c5495020306d94c54a96af34865cbe6fc68b415c',
 'code/publication_audit.py':'a5704600d2d99f918b6938e81b9ba397666874081e0fe7e94e0a2ca355fd5b02',
 'editorial/abstract.tex':'24e3f8ec2c6248af6d4c68dceb315626ca318baf7481e25724ddf9636bc4814d',
 'editorial/completed_evidence.tex':'970d5a52f39ee6799941ceeb9dd60ef9329aea5be6dfe5aec5f14eae96aca5d5',
 'editorial/conclusion.tex':'c8abb565178823505e593bf64fdb45399649594a7fd8f23f230872516b0424cf',
 'editorial/introduction.tex':'27356a38ca15ef9dddde39d923b069dd5308fd0a0d170a4d4d4f66a4dd75307a',
 'editorial/registered_extensions.tex':'b3ad293a94b1e3943a9e31e32687cf9076ab198fa799dc58eb8b1a063a5282a2',
 'editorial/response_body.tex':'48bdc87bfb47d7d1797ad82bce045aa1d5de258ed1b3dbe6b4eacac7651c0402'
}
def main():
 names=[f'payload.part{i:02}.b64' if i!=2 else 'payload.correct02.b64' for i in range(7)]
 packed=''.join(''.join((P/'transport'/n).read_text().split()) for n in names)
 raw=zlib.decompress(base64.b64decode(packed,validate=True))
 digest=hashlib.sha256(raw).hexdigest()
 assert digest=='0b5d8dd37644bb232d84c0996d699445d272416f33bf6e68568262eb4544f8c4',digest
 original=json.loads(raw);assert len(original)==27
 patches=json.loads((S/'remaining_edits.json').read_text())
 assert len(patches)==6 and set(patches)<=set(EXPECTED)
 updated={}
 for name,operations in patches.items():
  lines=original[name].splitlines(keepends=True)
  previous=0
  for first,last,text in operations:
   assert 0<=previous<=first<=last<=len(lines)
   assert isinstance(text,str)
   previous=last
  for first,last,text in reversed(operations):lines[first:last]=[text]
  updated[name]=''.join(lines)
 for name in set(EXPECTED)-set(patches):updated[name]=(S/name).read_text()
 actual={name:hashlib.sha256(text.encode()).hexdigest() for name,text in updated.items()}
 errors={name:{'expected':EXPECTED[name],'actual':value} for name,value in actual.items() if value!=EXPECTED[name]}
 assert not errors,json.dumps(errors,indent=2)
 files={**original,**updated}
 for name,text in files.items():
  rel=PurePosixPath(name)
  assert not rel.is_absolute() and '..' not in rel.parts
  dest=P/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
 receipt={'original_payload_sha256':digest,'original_segments':names,'original_file_count':27,'completed_source_sha256':actual,'completed_source_count':12,'total_editable_files':len(files),'scope':'Exact editable source installation, not a numerical rerun or alteration of registered evidence.'}
 (P/'COMPLETE_SOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
