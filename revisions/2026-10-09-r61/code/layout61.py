"""Idempotent editorial layout repairs; no scientific source/result is modified."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parents[1]
B=chr(92)
def sha(text):return hashlib.sha256(text.encode()).hexdigest()
def main():
    changes=[]
    def write(path,text,scope):
        file=R/path;old=file.read_text()
        if old!=text:
            file.write_text(text);changes.append(dict(path=path,before_sha256=sha(old),after_sha256=sha(text),scope=scope))
    file=R/'code/tables61.py';text=file.read_text()
    old="['Actor','Leaves','Modes','Aliases','Date 0 gap','All-date gap','Unclipped','Own work (s)']"
    heads=['Actor','Leaves','Modes','Aliases',B+'shortstack{Date 0'+B*2+'gap}',B+'shortstack{All-date'+B*2+'gap}','Unclipped',B+'shortstack{Own work'+B*2+'(s)}']
    new=repr(heads)
    if old in text:text=text.replace(old,new,1)
    elif new not in text:raise AssertionError('Unexpected fixed-policy table header')
    ast.parse(text);write('code/tables61.py',text,'Split three table headers into readable lines; all data and font sizes unchanged.')
    file=R/'sections/supp61.tex';text=file.read_text()
    old='The refinement grids are $(N,A,q)=(8,8,4),(16,16,8),(32,32,16),(64,64,32),(128,64,32)$.'
    new='The refinement grid $(N,A,q)$ follows the sequence\n'+B+'begin{gather*}\n(8,8,4),'+B+'quad(16,16,8),'+B+'quad(32,32,16),'+B*2+'\n(64,64,32),'+B+'quad(128,64,32).\n'+B+'end{gather*}\n'
    if old in text:text=text.replace(old,new,1)
    elif new not in text:raise AssertionError('Unexpected refinement-grid sentence')
    write('sections/supp61.tex',text,'Break a long inline sequence into an unnumbered two-line display; same grids and order.')
    file=R/'complete.tex';text=file.read_text();anchor=B+'input{sections/search60}'
    addition=B+'clearpage\n'+B+'section*{Current exact-search and accuracy additions}\n'+B+'setcounter{section}{0}\n'+B+'renewcommand{'+B+'thesection}{R61.'+B+'arabic{section}}\n'+B+'renewcommand{'+B+'theHsection}{R61.'+B+'arabic{section}}\n'
    if addition not in text:
        if text.count(anchor)!=1:raise AssertionError('Unexpected complete-edition addition anchor')
        text=text.replace(anchor,addition+anchor,1)
    write('complete.tex',text,'New R61 additions receive distinct numeric section and hyperlink names after the unchanged historical appendices; no original labels or content removed.')
    path=R/'audit/LAYOUT61.json'
    if changes:path.write_text(json.dumps(dict(changes=changes,scientific_code_changed=False,scientific_results_changed=False,publication_gates_relaxed=False),indent=2)+'\n')
    print(json.dumps(dict(layout_changes=len(changes),scientific_sources_changed=False)),flush=True)
if __name__=='__main__':
    main()
