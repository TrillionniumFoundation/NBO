"""Materialize the checked R21 source transaction without altering old revisions."""
from pathlib import Path, PurePosixPath
import base64, gzip, hashlib, json, lzma, re, shutil

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'revisions/2026-10-05-r21'
BASE = '76b633dbf10b00861b7f06dba8d632dd25c96d61'
EXPECTED = 'a27206570f07e583e62f531e1e00104f4a30d5379dd99a4ffa839a0660590e41'
BASE_BLOBS = {'ECTA.tex':'755f777e770a3ba9ba94c7198a495fc0e40d45f4',
              'supp.tex':'12156e332c0e12a829fb7f8a0cc33215a68f5614',
              'README.md':'7e7244655050edf5a0a068c6845666d4d1f3cf85'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def main():
    payload = ''.join((R/f'transport/part{i:02d}.b64').read_text().strip() for i in range(5))
    raw = lzma.decompress(base64.b64decode(payload, validate=True))
    assert sha(raw) == EXPECTED, 'source payload mismatch'
    files = json.loads(raw)
    assert len(files) == 25
    for name, text in files.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts and isinstance(text, str)
        assert (R/path).resolve().is_relative_to(R.resolve())
    for name, expected in BASE_BLOBS.items():
        data = (ROOT/name).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blob == expected, 'base root changed: ' + name
    for name in ['code','manuscript','results/generated','archive','build','protocols']:
        (R/name).mkdir(parents=True, exist_ok=True)
    for name in BASE_BLOBS:
        shutil.copyfile(ROOT/name, R/'archive'/name)
    old = ROOT/'revisions/2026-10-05-r19-integrated'
    shutil.copyfile(old/'applications.tex', R/'archive/applications.tex')
    for name in ['introduction','conclusion']:
        shutil.copyfile(old/f'manuscript/{name}.tex', R/f'archive/r19_{name}.tex')
    report = ROOT/'reviews/2026-10-05-econometrica-numerical-methods-r18/referee_report.md'
    assert sha(report.read_bytes()) == '0c8405c262644ca949924a3ed1a6e58cedac9ccb345c5c52775d7fb0a572546f'
    shutil.copyfile(report, R/'archive/referee_report_r18.md')
    inheritance = dict(base_commit=BASE, reviewed_commit='20afc6c1c4828e3c469e7906366bcc8730cc04d0',
        review_branch='review/econometrica-numerical-methods-r18-2026-10-05-20afc6c',
        source_review_sha256=sha(report.read_bytes()), inherited_components={})
    def visit(name):
        if name in inheritance['inherited_components']:
            return
        data = (ROOT/name).read_bytes()
        text = data.decode('utf-8')
        inheritance['inherited_components'][name] = dict(sha256=sha(data), labels=re.findall(r'\\label\{([^}]+)\}', text))
        for child in re.findall(r'\\input\{([^}]+)\}', text):
            child = child if child.endswith('.tex') else child + '.tex'
            if (ROOT/child).exists():
                visit(child)
    for name in ['ECTA.tex','supp.tex','revisions/2026-10-05-r19-integrated/applications.tex']:
        visit(name)
    assert len(inheritance['inherited_components']) == 129
    assert len({x for v in inheritance['inherited_components'].values() for x in v['labels']}) == 408
    save(R/'protocols/INHERITANCE.json', inheritance)
    evidence = ROOT/'revisions/2026-10-05-r20/results/future-study/SUMMARY.json.gz'
    packed = evidence.read_bytes()
    assert sha(packed) == 'd30a4d9da86f00a481ef5c8c46067744f1fccb5f6ff2bb1dc7a1e9a38915fdad'
    summary_raw = gzip.decompress(packed)
    assert sha(summary_raw) == '9e22610f6af5996ce7781ba623cad9c2be49e0e77696ac09f58a201cc4be8550'
    summary = json.loads(summary_raw)
    assert len(summary['records']) == 168 and not summary['failures']
    save(R/'protocols/FUTURE_EXECUTION_METADATA.json', {k:v for k,v in summary.items() if k != 'records'})
    for name, text in files.items():
        dest = R/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding='utf-8')
    for name in ['ECTA.tex','supp.tex']:
        shutil.copyfile(R/name, ROOT/name)
    shutil.copyfile(R/'ROOT_README.md', ROOT/'README.md')
    save(R/'protocols/SOURCE_INSTALL.json', dict(base_commit=BASE, payload_sha256=EXPECTED,
        source_files={k:sha(v.encode('utf-8')) for k,v in files.items()},
        inherited_components=129, inherited_labels=408, original_summary_sha256=sha(summary_raw)))
    print('Installed 25 plain source/audit files; retained 129 original components and 408 labels.')

if __name__ == '__main__':
    main()
