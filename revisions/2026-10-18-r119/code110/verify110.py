"""Verify active sources, final LaTeX logs, PDF bytes, and live raw evidence.
No theorem or remote CI verdict is inferred from typesetting success.
"""
from pathlib import Path
import re,json,hashlib,sys
import fitz
R=Path(__file__).resolve().parents[1];DOCS=('ECTA','supp','appendix','RESPONSE_TO_REFEREE')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seen=set();labels={};refs=set();cites=set();bibfiles=set()
def scan(p):
 p=p.resolve()
 if p in seen:return
 if not p.is_file():raise FileNotFoundError(p)
 seen.add(p);t=re.sub(r'(?<!\\)%[^\n]*','',p.read_text())
 for l in re.findall(r'\\label\{([^}]+)\}',t):
  if l in labels:raise AssertionError('Duplicate active label: '+l+' '+labels[l]+' '+str(p))
  labels[l]=str(p.relative_to(R))
 refs.update(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',t))
 for c in re.findall(r'\\cite\w*\*?(?:\[[^]]*\])*\{([^}]+)\}',t):cites.update(x.strip() for x in c.split(','))
 for b in re.findall(r'\\bibliography\{([^}]+)\}',t):bibfiles.update(x.strip()+'.bib' for x in b.split(','))
 for name in re.findall(r'\\(?:input|include)\{([^}]+)\}',t):scan(R/(name if name.endswith('.tex') else name+'.tex'))
for doc in DOCS:scan(R/(doc+'.tex'))
keys=set()
for b in bibfiles:
 p=R/b
 if not p.is_file():raise FileNotFoundError(p)
 keys.update(re.findall(r'@\w+\s*\{\s*([^,]+),',p.read_text()))
if refs-labels.keys():raise AssertionError(('Undefined source references',sorted(refs-labels.keys())))
if cites-keys:raise AssertionError(('Missing citations',sorted(cites-keys)))
report={'revision':'R110','active_source_files':len(seen),'active_labels':len(labels),'cited_keys':sorted(cites),
 'source_sha256':{str(p.relative_to(R)):sha(p) for p in sorted(seen)},
 'bibliography_sha256':{b:sha(R/b) for b in sorted(bibfiles)},'documents':{},
 'scope':'active source dependency/reference closure and actual PDF/log checks, not formal proof certification or remote CI'}
for doc in DOCS:
 logp=R/f'build/{doc}.log';log=logp.read_text(errors='replace')
 bad=[x for x in log.splitlines() if any(v in x.lower() for v in ('undefined references','undefined citations','multiply defined','label(s) may have changed','rerun to get cross-references'))]
 # Undefined individual reference warnings are also rejected.
 bad.extend(re.findall(r'(?:Reference|Citation) [^\n]*undefined[^\n]*',log))
 if bad:raise AssertionError((doc,bad))
 pdfp=R/f'build/{doc}.pdf';pdf=fitz.open(pdfp)
 pages=[p.get_text() for p in pdf];blanks=[i+1 for i,t in enumerate(pages) if not t.strip()]
 if blanks:raise AssertionError((doc,'Blank text pages',blanks))
 report['documents'][doc]={'pages':len(pdf),'bytes':pdfp.stat().st_size,'sha256':sha(pdfp),
  'overfull_warnings':re.findall(r'Overfull [^\n]+',log),'log_sha256':sha(logp),'pages_with_no_text':blanks,
  'rendered_visual_review':'recorded separately in VISUAL_REVIEW110.json'}
# Verify the exact frozen executable bytes, never adjusting the declared hashes.
freeze=json.loads((R/'SOURCE_FREEZE110.json').read_text())
for p,h in freeze['scientific_files'].items():
 if sha(R/p)!=h:raise AssertionError('Changed frozen current source: '+p)
f108=json.loads((R/'frozen108/SOURCE_FREEZE108.json').read_text())
for p,h in f108['scientific_files'].items():
 if sha(R/'frozen108'/p)!=h:raise AssertionError('Changed inherited frozen source: '+p)
if sha(R/'frozen108/PROTOCOL108.md')!=f108['protocol_sha256']:raise AssertionError('Inherited protocol changed')
publication_only='--publication-only' in sys.argv
for p in (() if publication_only else ('raw110/gain-budget/AUDIT110.json','raw110/r108-reproduction/AUDIT108.json','raw110/r108-reproduction/KERNEL_AUDIT108.json')):
 if json.loads((R/p).read_text())['status']!='passed':raise AssertionError('Missing successful actual audit '+p)
if publication_only:report['scope']+='; PUBLICATION-ONLY: no raw-data or scientific-execution success is asserted'
(R/('evidence110/PUBLICATION_BUILD110.json' if publication_only else 'evidence110/PUBLICATION110.json')).write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({'documents':report['documents'],'source_files':len(seen),'labels':len(labels)},indent=2))
