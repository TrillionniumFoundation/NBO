"""Standard-library R121 source custody; no scientific imports or evaluation."""
from pathlib import Path
import json
from io121 import REVISION, digest, repository, verify_commit_file


def verify_source(commit, revision=REVISION):
    revision = Path(revision).resolve()
    repo = repository(revision)
    manifest = revision/"SOURCE_FREEZE121.json"
    bound = [verify_commit_file(manifest,commit,repo)]
    info = json.loads(manifest.read_text())
    files = info["scientific_files"]
    if not files or "PROTOCOL121.md" not in files:
        raise RuntimeError("The actual immutable source freeze must bind the protocol")
    for name, expected in sorted(files.items()):
        path=(revision/name).resolve(); path.relative_to(revision)
        if digest(path)!=expected:
            raise RuntimeError("Scientific source SHA differs: "+name)
        bound.append(verify_commit_file(path,commit,repo))
    return dict(source_commit=commit,source_manifest_sha256=digest(manifest),
                verified_files=bound,verified_before_scientific_import=True)
