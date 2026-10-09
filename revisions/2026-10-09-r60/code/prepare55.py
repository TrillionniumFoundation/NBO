"""One-time source preparation. No training or production observations."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];OLD=R.parent/'2026-10-08-r54'

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def replace(text,a,b):
    if a not in text:
        if b in text:return text
        raise AssertionError('Expected source fragment absent: '+a[:80])
    return text.replace(a,b)
def main():
    marker=R/'audit/SOURCE_PREPARATION55.json'
    if marker.exists():
        print('R55 ordinary sources already prepared; no source regeneration.');return
    own={str(p.relative_to(R)):p.read_bytes() for p in R.rglob('*') if p.is_file()}
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    for name,data in own.items():
        p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    if (R/'build').exists():shutil.rmtree(R/'build')
    (R/'build').mkdir();(R/'audit').mkdir(exist_ok=True)
    backup=R/'preserved/R54-current';backup.mkdir(parents=True,exist_ok=True)
    for name in ('ECTA.tex','supp.tex','complete.tex','complete-supp.tex','response.md','README.md'):
        shutil.copy2(OLD/name,backup/name)
    p=R/'code/neural55.py';text=p.read_text()
    text=replace(text,"if self.kind=='quadratic':return dot(x,p['Q']+p['Q'].T)+p['v']","if self.kind=='quadratic':return dot(x,p['Q'])+dot(x,p['Q'].T)+p['v']")
    text=replace(text,"return dot(active,(p['W']*p['u']).T)+p['v']","return self.weighted_slope(active)")
    text=replace(text,"return dot(s.stack(terms),(p['W']*p['u']).T)+p['v']","return self.weighted_slope(s.stack(terms))")
    if 'def weighted_slope' not in text:
        text=replace(text,'    def payload(self):\n',"""    def weighted_slope(self,prob):
        p=self.params;columns=[]
        for i in range(self.d):
            v=I.point(np.full(len(prob.lo),p['v'][i]))
            for j in range(len(p['u'])):
                v=v+s.col(prob,j)*I.point(p['W'][i,j])*I.point(p['u'][j])
            columns.append(v)
        return s.stack(columns)
    def payload(self):
""")
    text=replace(text,'logs.append(dict(date=t,samples=samples,bellman_actions=17*samples,','logs.append(dict(date=t,samples=samples,training_seed=seed,fitting_seed=seed+100+t,training_states=x.tolist(),training_labels=labels.tolist(),bellman_actions=17*samples,')
    p.write_text(text)
    p=R/'code/prospective55.py';text=p.read_text()
    text=replace(text,"('neural55.py','prospective55.py','null55.py','tests55.py')","('neural55.py','prospective55.py','null55.py','tests55.py','cohort55.py','prepare55.py')")
    p.write_text(text)
    retained={}
    for root in ('inputs','results','results52','results53','results53-extension','evidence','preserved'):
        for p in (OLD/root).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:
                name=str(p.relative_to(OLD));h=digest(p)
                if digest(R/name)!=h:raise AssertionError('Inherited input changed: '+name)
                retained[name]=h
    marker.write_text(json.dumps(dict(baseline_commit='00e837adb431f4d4b5248fc6d5ff1fc927dd3b65',review_commit='adf1256cff9cde365246a3db2dac90c72fda3b13',retained_sha256=retained,production_started=False,pre_freeze_corrections=['outward neural slope products','retained training states and labels','driver source included in freeze']),indent=2,sort_keys=True)+'\n')
    (R/'README.md').write_text('# Neural Bellman Operators — R55\n\nProspective source edition. The scientific protocol is frozen before production.\nThis directory is not a completed publication until its final release manifest exists.\nThe controlling R54 referee report and every older revision remain unchanged.\n')
    print(json.dumps(dict(status='prepared',retained_files=len(retained))))
if __name__=='__main__':main()
