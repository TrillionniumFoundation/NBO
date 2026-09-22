"""Validate historical preservation, actual manuscripts, and exact certificate inputs."""
import argparse,hashlib,json,pathlib,re,subprocess
import price_envelope as e

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(skip_pdf=False,require_ci=False):
 base=json.loads((e.REV/'inherited_manifest.json').read_text())
 for name,digest in base['files'].items():
  p=e.ROOT/base['archived_replacement'].get(name,name);assert sha(p)==digest,('history_changed',name)
 old=(e.REV/'archive/REVISION_INDEX_before_R12.md').read_bytes();assert (e.ROOT/'REVISION_INDEX.md').read_bytes().startswith(old)
 report=(e.REV/'review_input/referee_report.md').read_bytes()
 assert hashlib.sha1(b'blob '+str(len(report)).encode()+b'\0'+report).hexdigest()=='42cee0954515e5578dc579a4ca0428bb4e399b2e'
 # Every inherited main-text line survives as an ordered subsequence.
 a=(e.ROOT/'revisions/2026-09-22-r11/paper/main.tex').read_text().splitlines();b=(e.REV/'paper/main.tex').read_text().splitlines();i=0
 for line in b:
  if i<len(a) and a[i]==line:i+=1
 assert i==len(a),'Inherited prose removed or rewritten'
 nodes=e.load_nodes()
 for n in nodes:
  assert sha(e.ROOT/n['source_path'])==n['source_sha256']
  if n['origin']=='new':
   folder=(e.ROOT/n['source_path']).parent
   for name,digest in n['files'].items():assert sha(folder/name)==digest,('case_file_changed',folder,name)
   for name,digest in n['inherited_sources'].items():assert sha(e.ROOT/name)==digest
 env=e.certify(nodes);assert env['status']=='PASS' and len(nodes)==18
 canonical=json.loads((e.REV/'results/envelope.json').read_text());assert canonical==env
 tests=json.loads((e.REV/'validation_tests.json').read_text());assert tests['status']=='PASS'
 result={'status':'PASS','historical_files_preserved':len(base['files']),'inherited_main_lines_retained':len(a),'exact_review_blob':'42cee0954515e5578dc579a4ca0428bb4e399b2e','certified_prices':len(nodes),'uniform_regret_upper':env['uniform_regret_upper'],'tests':len(tests['checks']),'pdf_checked':not skip_pdf,'clean_checkout_reexecution_required':require_ci}
 if require_ci:
  ci=json.loads((e.REV/'ci_results/status.json').read_text());assert ci['status']=='PASS' and len(ci['cells'])==18
  result['independent_uniform_regret_upper']=ci['uniform_regret_upper']
 if not skip_pdf:
  for stem in ['ECTA_R12','SUPP_R12']:
   p=e.ROOT/f'{stem}.pdf';assert p.is_file()
   info=subprocess.check_output(['pdfinfo',str(p)],text=True);pages=int(re.search(r'Pages:\s+(\d+)',info).group(1))
   log=(e.REV/f'build_logs/{stem}.log').read_text(errors='replace')
   for bad in ['Overfull \\hbox','undefined references','undefined citations','multiply defined','! LaTeX Error','! Undefined control sequence']:assert bad not in log,(stem,bad)
   result[stem]={'pages':pages,'sha256':sha(p)}
  assert result['ECTA_R12']['pages']>=46 and result['SUPP_R12']['pages']>=148
  text=subprocess.check_output(['pdftotext',str(e.ROOT/'ECTA_R12.pdf'),'-'],text=True)
  for term in ['.009994024846927508','Certified parameter continuation','Finite refinement under local slack']:assert term in text,term
 result['typesetting_notice']='Inherited class emits an empty frontmatter anchor warning; no overfull box or unresolved reference is accepted.'
 e.dump(e.REV/'validation_report.json',result);print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--skip-pdf',action='store_true');p.add_argument('--require-ci',action='store_true');a=p.parse_args();main(a.skip_pdf,a.require_ci)
