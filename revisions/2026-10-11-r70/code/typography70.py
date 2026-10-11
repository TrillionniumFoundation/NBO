"""One-time longtable footer repair; scientific values and rows are unchanged."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
def main():
    marker=R/'audit/TYPOGRAPHY70.json'
    if marker.exists():return
    p=R/'code/tables70.py';text=p.read_text();before=hashlib.sha256(text.encode()).hexdigest()
    anchor="    put('tables/'+name+'.tex',text)"
    if text.count(anchor)!=1:raise AssertionError('Unique table-output anchor missing')
    fix="    if long:\n        text=text.replace('\\\\endhead'+chr(10),'\\\\endhead'+chr(10)+'\\\\hline\\\\endfoot'+chr(10)+'\\\\hline\\\\endlastfoot'+chr(10))\n        text=text.replace(chr(10)+'\\\\hline'+chr(10)+'\\\\end{longtable}',chr(10)+'\\\\end{longtable}')\n"
    text=text.replace(anchor,fix+anchor,1);p.write_text(text)
    marker.write_text(json.dumps(dict(status='ordinary_source_updated',scope='Longtable bottom rules use the footer mechanism; no row, endpoint, proof or scientific record changed.',generator_before_sha256=before,generator_after_sha256=hashlib.sha256(text.encode()).hexdigest()),indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
