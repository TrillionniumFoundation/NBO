from pathlib import Path
import hashlib,json,unittest
R=Path(__file__).resolve().parents[1]
class Preservation96(unittest.TestCase):
 def test_every_scientific_section_unchanged(self):
  rec=json.loads((R/'audit/reproduction96/INTEGRATION96.json').read_text())
  for path,digest in rec['inherited_section_hashes'].items():self.assertEqual(hashlib.sha256((R/path).read_bytes()).hexdigest(),digest,path)
 def test_full_assignment_not_dropped(self):
  rec=json.loads((R/'audit/reproduction96/INTEGRATION96.json').read_text());text='\n'.join((R/(doc+'.tex')).read_text() for doc in ('ECTA','supp','appendix'))
  for name in rec['assignments']:self.assertEqual(text.count('\\input{'+name+'}'),1,name)
 def test_historical_failure_is_retained(self):
  before=json.loads((R/'preserved/R95-source/PREPARATION72-failed-in-R95.json').read_text());now=json.loads((R/'audit/PREPARATION72.json').read_text());path='sections/core49.tex'
  self.assertNotIn(path,now['unchanged_active_sections']);self.assertIn(path,now['amended_active_sections'])
  self.assertEqual(before['unchanged_active_sections'][path]['sha256'],now['amended_active_sections'][path]['original_sha256'])
  self.assertNotEqual(now['amended_active_sections'][path]['sha256'],now['amended_active_sections'][path]['original_sha256'])
if __name__=='__main__':unittest.main()
