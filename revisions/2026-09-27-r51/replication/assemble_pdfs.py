"""Preserve historical PDF pages without the journal class's pdfpages offsets.

Only the new R51 outputs are changed. The pinned R50 and reconstructed R48
inputs remain byte-identical. Requires pdfinfo, pdfseparate and pdfunite.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, tempfile

R = Path(__file__).resolve().parent.parent
ROOT = R.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pages(path):
    info = subprocess.check_output(['pdfinfo', str(path)], text=True)
    match = re.search(r'^Pages:\s+(\d+)\s*$', info, re.M)
    if not match:
        raise RuntimeError('Cannot read PDF page count: ' + str(path))
    return int(match.group(1))


def install():
    # These publication-only amendments do not alter the four frozen scientific
    # sources. Keep an ordinary, readable source tree rather than a runtime patch.
    p = R / 'replication/publication.py'
    text = p.read_text()
    for name in ['SUPP_R50', 'RESPONSE_R50']:
        old = r'\includepdf[pages=-,pagecommand={}]' + '{' + name + '.pdf}'
        new = '% Historical ' + name + ' pages are appended by assemble_pdfs.py.'
        if old not in text and new not in text:
            raise RuntimeError('Missing known publication inclusion: ' + name)
        text = text.replace(old, new)
    p.write_text(text)
    b = ROOT / 'R51_BUILD.sh'
    text = b.read_text()
    hook = 'python "$R/replication/assemble_pdfs.py"\n'
    marker = 'python "$R/replication/manifest.py"\n'
    if hook not in text:
        if marker not in text:
            raise RuntimeError('Missing build insertion point')
        text = text.replace(marker, hook + marker)
    b.write_text(text)
    m = R / 'replication/manifest.py'
    text = m.read_text()
    if "'R48_RECONSTRUCTED_R50.pdf'" not in text:
        text = text.replace("'SUPP_R50.pdf','RESPONSE_R50.pdf'", "'SUPP_R50.pdf','RESPONSE_R50.pdf','R48_RECONSTRUCTED_R50.pdf'")
    m.write_text(text)
    print('Installed lossless historical-page assembly in the ordinary build sources.')


def main():
    for binary in ['pdfinfo', 'pdfseparate', 'pdfunite']:
        if not shutil.which(binary):
            raise RuntimeError('Required publication tool is absent: ' + binary)
    inputs = [ROOT / x for x in ['SUPP_R50.pdf', 'RESPONSE_R50.pdf', 'R48_RECONSTRUCTED_R50.pdf']]
    before = {p.name: digest(p) for p in inputs}
    # R50 appended the reconstructed R48 via pdfpages. Its original standalone
    # PDF is intact, so restore that exact page sequence rather than carrying
    # forward the earlier clipped embedding.
    numerical_pages = pages(inputs[0]) - pages(inputs[2])
    if numerical_pages <= 0:
        raise RuntimeError('Unexpected inherited supplement structure')
    records = []
    with tempfile.TemporaryDirectory(prefix='nbo-r51-pdf-') as directory:
        tmp = Path(directory)
        subprocess.run(['pdfseparate', '-f', '1', '-l', str(numerical_pages),
                        str(inputs[0]), str(tmp / 'r50-%04d.pdf')], check=True)
        historical_prefix = sorted(tmp.glob('r50-*.pdf'))
        if len(historical_prefix) != numerical_pages:
            raise RuntimeError('Incomplete historical numerical prefix')
        plans = [('SUPP_R51', historical_prefix + [inputs[2]]),
                 ('RESPONSE_R51', [inputs[1]])]
        for name, appendices in plans:
            destination = ROOT / (name + '.pdf')
            new_pages = pages(destination)
            # The TeX output is the new, unobstructed R51 prefix. No journal
            # offsets or rescaling are applied to the appended original pages.
            output = tmp / (name + '.pdf')
            subprocess.run(['pdfunite', str(destination), *map(str, appendices), str(output)], check=True)
            expected = new_pages + sum(pages(p) for p in appendices)
            if pages(output) != expected:
                raise RuntimeError('Page omission during assembly: ' + name)
            shutil.copyfile(output, destination)
            info = subprocess.check_output(['pdfinfo', str(destination)], text=True)
            (R / 'logs' / (name + '-pdfinfo.txt')).write_text(info)
            records.append({'output': destination.name, 'new_prefix_pages': new_pages,
                            'total_pages': expected, 'sha256': digest(destination)})
    if before != {p.name: digest(p) for p in inputs}:
        raise RuntimeError('An inherited input changed')
    record = {'method': 'lossless PDF page concatenation; no scaling, cropping or text replacement',
              'inherited_inputs_sha256': before, 'preserved_r50_numerical_pages': numerical_pages,
              'reconstructed_r48_pages': pages(inputs[2]), 'outputs': records}
    (R / 'logs' / 'PDF_ASSEMBLY.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Lossless historical PDF assembly verified:', [(x['output'], x['total_pages']) for x in records])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    install() if args.install else main()
