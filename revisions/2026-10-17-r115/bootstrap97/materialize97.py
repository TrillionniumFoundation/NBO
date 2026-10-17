"""Publish ordinary R97 files from a verified source capsule and pinned R96.

The capsule is transport, not a substitute for deposited editable source.
Scientific history and old section files are never edited by this script.
"""
from pathlib import Path
import base64,hashlib,json,lzma,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
OLD=R.parent/'2026-10-13-r96'
EXPECTED='d857e2797aed012b8d61c266d04dd56754aca92c14a63767fc5372694a90a1e6'

def main():
    if (R/'audit97/SOURCE97.json').exists():
        print('Ordinary sources already materialized; retaining them.')
        return
    if not (OLD/'ECTA.tex').exists():
        raise FileNotFoundError('Pinned R96 ordinary source missing')
    raw=base64.b64decode(''.join((R/'bootstrap97'/f'source97.part{i}.b64').read_text().strip() for i in range(3)),validate=True)
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:
        raise ValueError('Source capsule identity failed; no file will be written')
    files=json.loads(lzma.decompress(raw))
    for name,text in files.items():
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or not isinstance(text,str):
            raise ValueError('Invalid source path or content')
    def ignore(folder,names):
        return [n for n in names if n=='__pycache__' or n.endswith('.pyc') or (Path(folder)==OLD and n=='build')]
    shutil.copytree(OLD,R,dirs_exist_ok=True,ignore=ignore)
    for name,text in files.items():
        p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    # Arithmetic editorial correction after transport freeze, before source
    # publication and experiments: h(1/4)=1/16+1/64=5/64, not 1/128.
    p=R/'response.md';s=p.read_text()
    old='normalized model investment charge $1/128$'
    if s.count(old)!=1:raise ValueError('Expected single normalization correction')
    p.write_text(s.replace(old,'maximal first-date investment charge $5/64$'))
    subprocess.run([sys.executable,str(R/'new/prepare97.py')],check=True)
    study=hashlib.sha256((R/'new/study97.py').read_bytes()).hexdigest()
    if study!='db947fbbe20a92f38d8b5b95e4f5d733f8a3162df30d2f670e13a472b493baba':
        raise ValueError('Experiment differs from remotely frozen protocol')
    record={'capsule_sha256':EXPECTED,'ordinary_files':sorted(files),'experiment_sha256':study,
      'scientific_parent':'9a80ab7d4de97c9a61747899766fab43ec3c2598',
      'review_parent':'e91a0702a4f1df4baa7b43fdfdd1305d0d62940c',
      'protocol_commit':'673d29e48922ae59908cdde245f312e077442539',
      'editorial_correction':'Response normalization: maximal first-date investment charge is 5/64 and its one percent is 1/1280. Frozen experiment unchanged.'}
    (R/'audit97/SOURCE97.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps(record,indent=2))
if __name__=='__main__':main()
