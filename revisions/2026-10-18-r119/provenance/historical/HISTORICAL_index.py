#!/usr/bin/env python3
"""Offline, content-addressed index of the captured reachable Git graph.

Reads only objects already local.  It never invokes a fetch or executes
historical source.  Parsing and keyword signatures are an inventory, not
an independent mathematical proof or verification of a reported run.
"""
from __future__ import annotations

import ast
import bisect
from collections import Counter, defaultdict, deque
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parents[2]
REPO = BASE / "NBO"
OUT = Path(__file__).resolve().parent
ENV = {**os.environ, "GIT_NO_LAZY_FETCH": "1"}
SCIENCE = {".tex", ".py", ".md", ".json"}
ANCILLARY = {".log", ".stdout", ".out", ".txt", ".yml", ".yaml", ".sh", ".b64", ".bib", ".csv"}
START = datetime.now(timezone.utc).isoformat()
T0 = time.monotonic()


def dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def progress(message, **kw):
    print(dump({"utc": datetime.now(timezone.utc).isoformat(), "stage": message, **kw}), flush=True)


def batch_read(ids):
    """Bounded batches avoid stdin/stdout pipe deadlock and huge captures."""
    p = subprocess.Popen(["git", "cat-file", "--batch"], cwd=REPO,
                         env=ENV, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    ids = list(ids)
    try:
        for first in range(0, len(ids), 32):
            chunk = ids[first:first + 32]
            p.stdin.write(("\n".join(chunk) + "\n").encode("ascii"))
            p.stdin.flush()
            for expected in chunk:
                header = p.stdout.readline().decode("ascii").strip().split()
                if len(header) == 2 and header[1] == "missing":
                    yield expected, "missing", None
                    continue
                if len(header) != 3 or header[0] != expected:
                    raise RuntimeError((expected, header))
                sha, kind, length = header
                length = int(length)
                data = p.stdout.read(length)
                trailer = p.stdout.read(1)
                if len(data) != length or trailer != b"\n":
                    raise RuntimeError("incomplete local cat-file record")
                actual = hashlib.sha1(kind.encode() + b" " + str(length).encode() + b"\0" + data).hexdigest()
                if actual != sha:
                    raise RuntimeError("object identity mismatch " + sha)
                yield sha, kind, data
    finally:
        p.stdin.close()
        status = p.wait()
        error = p.stderr.read().decode(errors="replace")
        if status:
            raise RuntimeError((status, error))


inventory = {}
with (OUT / "HISTORICAL_object_inventory.tsv").open() as handle:
    for r in csv.DictReader(handle, delimiter="\t"):
        inventory[r["sha1"]] = {
            "sha": r["sha1"], "kind": r["type"],
            "size": int(r["size"]) if r["type"] != "missing" else None,
            "representative_path": r.get("representative_path") or "",
        }

dbpath = OUT / "HISTORICAL_index.sqlite"
if dbpath.exists():
    raise SystemExit("Index already exists; retain it or choose a new snapshot filename.")
db = sqlite3.connect(dbpath)
db.executescript("""
PRAGMA journal_mode=OFF;
PRAGMA synchronous=OFF;
CREATE TABLE objects(sha TEXT PRIMARY KEY,kind TEXT,size INTEGER,available INTEGER,
 representative_path TEXT,sha256 TEXT,commit_mask_hex TEXT,witness_commit TEXT,witness_path TEXT,extensions TEXT);
CREATE TABLE commits(bit_index INTEGER PRIMARY KEY,sha TEXT UNIQUE,tree_sha TEXT,
 parents_json TEXT,committer_epoch INTEGER,subject TEXT);
CREATE TABLE tree_edges(parent_tree TEXT,name TEXT,mode TEXT,child_sha TEXT);
CREATE TABLE refs(ref TEXT PRIMARY KEY,sha TEXT,api_branch TEXT);
CREATE TABLE source_blobs(sha TEXT PRIMARY KEY,extensions TEXT,line_count INTEGER,
 utf8_valid INTEGER,parse_kind TEXT,parse_status TEXT,theorem_count INTEGER,
 proof_count INTEGER,function_count INTEGER,signature_count INTEGER);
CREATE TABLE theorems(id TEXT PRIMARY KEY,blob_sha TEXT,origin TEXT,environment TEXT,title TEXT,
 labels_json TEXT,start_line INTEGER,end_line INTEGER,statement_tex TEXT,normalized_sha256 TEXT);
CREATE TABLE latex_labels(blob_sha TEXT,origin TEXT,label TEXT,line INTEGER,context_id TEXT);
CREATE TABLE proofs(id TEXT PRIMARY KEY,blob_sha TEXT,origin TEXT,title TEXT,start_line INTEGER,
 end_line INTEGER,body_sha256 TEXT,explicit_targets_json TEXT,adjacent_theorem_id TEXT,heading TEXT);
CREATE TABLE proof_links(proof_id TEXT,label TEXT,kind TEXT,line INTEGER);
CREATE TABLE functions(id TEXT PRIMARY KEY,blob_sha TEXT,origin TEXT,qualified_name TEXT,
 kind TEXT,line INTEGER,end_line INTEGER,signature TEXT,economic_name_match INTEGER,docstring TEXT);
CREATE TABLE primitive_assignments(blob_sha TEXT,origin TEXT,name TEXT,line INTEGER,expression TEXT);
CREATE TABLE signatures(blob_sha TEXT,kind TEXT,line INTEGER,json_path TEXT,key TEXT,value TEXT);
CREATE TABLE parse_gaps(blob_sha TEXT,origin TEXT,kind TEXT,detail TEXT);
CREATE INDEX signatures_blob_idx ON signatures(blob_sha);
""")

trees = {}
tree_parents = defaultdict(list)
blob_parents = defaultdict(list)
aliases = defaultdict(set)
tree_ids = [sha for sha, obj in inventory.items() if obj["kind"] == "tree"]
progress("read_all_reachable_trees", count=len(tree_ids))
tree_rows = []
for sha, kind, data in batch_read(tree_ids):
    if kind != "tree":
        raise RuntimeError("tree disappeared from local snapshot")
    entries = []
    pos = 0
    while pos < len(data):
        stop = data.index(b"\0", pos)
        mode, name = data[pos:stop].split(b" ", 1)
        child = data[stop + 1:stop + 21].hex()
        mode = mode.decode("ascii")
        name = name.decode("utf-8", errors="replace")
        entries.append((mode, name, child))
        tree_rows.append((sha, name, mode, child))
        if mode in {"40000", "040000"}:
            tree_parents[child].append((sha, name))
        elif mode != "160000":
            blob_parents[child].append((sha, name))
            aliases[child].add(name)
        pos = stop + 21
    trees[sha] = entries
db.executemany("INSERT INTO tree_edges VALUES(?,?,?,?)", tree_rows)

commit_ids = sorted(sha for sha, obj in inventory.items() if obj["kind"] == "commit")
commits = []
commit_index = {}
tree_masks = defaultdict(int)
progress("read_all_reachable_commits", count=len(commit_ids))
for i, (sha, kind, data) in enumerate(batch_read(commit_ids)):
    text = data.decode("utf-8", errors="replace")
    head, _, message = text.partition("\n\n")
    tree = next(s[5:] for s in head.splitlines() if s.startswith("tree "))
    parents = [s[7:] for s in head.splitlines() if s.startswith("parent ")]
    clock = next((s for s in head.splitlines() if s.startswith("committer ")), "")
    match = re.search(r" (\d+) [+-]\d{4}$", clock)
    epoch = int(match.group(1)) if match else None
    c = {"bit_index": i, "sha": sha, "tree": tree, "parents": parents,
         "committer_epoch": epoch, "subject": message.splitlines()[0] if message else ""}
    commits.append(c)
    commit_index[sha] = i
    tree_masks[tree] |= 1 << i
    db.execute("INSERT INTO commits VALUES(?,?,?,?,?,?)",
               (i, sha, tree, dump(parents), epoch, c["subject"]))

# Propagate every commit-root identity through every available tree.  This
# records all containing commits without repeatedly expanding 1,595 snapshots.
indegree = Counter()
for parent, entries in trees.items():
    for mode, name, child in entries:
        if mode in {"40000", "040000"} and child in trees:
            indegree[child] += 1
queue = deque(sha for sha in trees if indegree[sha] == 0)
blob_masks = defaultdict(int)
processed = 0
while queue:
    parent = queue.popleft()
    processed += 1
    mask = tree_masks[parent]
    for mode, name, child in trees[parent]:
        if mode in {"40000", "040000"}:
            tree_masks[child] |= mask
            if child in trees:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        elif mode != "160000":
            blob_masks[child] |= mask
if processed != len(trees):
    raise RuntimeError("tree graph did not topologically close")


def witness(sha):
    mask = blob_masks.get(sha, 0)
    if not mask:
        return None, None
    bit = mask & -mask
    c = commits[bit.bit_length() - 1]
    root_tree = c["tree"]
    choices = [(parent, name) for parent, name in blob_parents[sha] if tree_masks[parent] & bit]
    if not choices:
        return c["sha"], None
    parent, name = min(choices)
    parts = [name]
    seen = set()
    while parent != root_tree:
        if parent in seen:
            raise RuntimeError("path witness cycle")
        seen.add(parent)
        choices = [(p, n) for p, n in tree_parents[parent] if tree_masks[p] & bit]
        if not choices:
            raise RuntimeError("unresolved containing-commit witness")
        parent, name = min(choices)
        parts.append(name)
    return c["sha"], "/".join(reversed(parts))


extensions = {}
object_rows = []
for sha, obj in inventory.items():
    names = aliases.get(sha, set())
    exts = {Path(name).suffix.lower() for name in names}
    if obj["representative_path"]:
        exts.add(Path(obj["representative_path"]).suffix.lower())
    extensions[sha] = sorted(exts)
    wc, wp = witness(sha) if obj["kind"] in {"blob", "missing"} else (None, None)
    obj.update(witness_commit=wc, witness_path=wp)
    object_rows.append((sha, obj["kind"], obj["size"], obj["kind"] != "missing",
                        obj["representative_path"], None, format(blob_masks.get(sha, 0), "x"),
                        wc, wp, dump(sorted(exts))))
db.executemany("INSERT INTO objects VALUES(?,?,?,?,?,?,?,?,?,?)", object_rows)

api = json.loads((BASE / "audit/branch_inventory.json").read_text())["branches"]
api_by_ref = {"refs/remotes/origin/" + r["branch"]: r for r in api}
ref_rows = []
for line in (OUT / "HISTORICAL_git_refs.tsv").read_text().splitlines():
    ref, sha, kind = line.split("\t")
    r = api_by_ref.get(ref)
    if r and r["sha"] != sha:
        raise RuntimeError("API/ref snapshot mismatch")
    ref_rows.append((ref, sha, r["branch"] if r else None))
db.executemany("INSERT INTO refs VALUES(?,?,?)", ref_rows)

HASH_RE = re.compile(r"(?<![A-Fa-f0-9])(?:[A-Fa-f0-9]{64}|[A-Fa-f0-9]{40})(?![A-Fa-f0-9])")
LABEL_RE = re.compile(r"\\label\s*\{([^{}]+)\}")
REF_RE = re.compile(r"\\(?:eqref|ref|cref|Cref|autoref|pageref)\*?\s*\{([^{}]+)\}")
BEGIN_RE = re.compile(r"\\begin\s*\{(theorem\*?|proposition\*?|lemma\*?|corollary\*?|claim\*?|conjecture\*?|thm\*?|prop\*?|lem\*?|cor\*?)\}(?:\s*\[([^\]]*)\])?")
PROOF_RE = re.compile(r"\\begin\s*\{(proof\*?|pf|Proof)\}(?:\s*\[([^\]]*)\])?")
HEADING_RE = re.compile(r"\\(?:(?:sub)*section|paragraph)\*?\s*(?:\[[^\]]*\])?\s*\{([^\n]*)")
MODEL_RE = re.compile(r"bellman|transition|dynamics|stage|terminal|payoff|cost|value|policy|critic|actor|risk|avar|cvar|continu|utility|capacity|shock|innov|discount|bsde|fbsde|ndu|drift|diffusion", re.I)
PARAM_RE = re.compile(r"(?:^|_)(?:beta|alpha|gamma|rho|sigma|discount|dim|dimension|horizon|capacity|radius|epsilon|eps|tolerance|target|seed|shock|risk|beta0|R|T|d)(?:$|_)", re.I)
IDENT_KEY = re.compile(r"sha|hash|commit|source|protocol|prereg|freeze|manifest|artifact|manuscript|referee|review|branch|tree|payload|handoff|custody|archive", re.I)
STATUS_KEY = re.compile(r"(?:^|_)(?:status|exit|exit_code|returncode|return_code|failure|failed|error|exception|timeout|success|passed|complete|completed|terminated|qualified)(?:$|_)", re.I)
METRIC_KEY = re.compile(r"regret|objective|welfare|loss|action_error|action_mismatch|violation|work|elapsed|runtime|duration|seconds|training|tuning|adopt|neural|quadratic|spline|polynomial", re.I)
TEXT_SIG = re.compile(r"source.{0,20}(?:sha|identity|freeze)|commit.{0,20}[0-9a-f]{7,40}|prereg|pre.?register|protocol|SOURCE_FREEZE|source_identity|MANIFEST|failed|failure|Traceback|FATAL|SIGKILL|timed? ?out|timeout|not certified|unqualified|incomplete|no.?go|nogo|terminated|exit.code", re.I)


def line_index(text):
    return [i for i, char in enumerate(text) if char == "\n"]


def line_number(newlines, offset):
    return bisect.bisect_left(newlines, offset) + 1


def strip_tex_comments(text):
    # Keep all offsets/line numbers. An escaped percent is retained.
    return re.sub(r"(?<!\\)%[^\n]*", lambda m: " " * len(m.group()), text)


def parse_tex(sha, text, origin="native"):
    clean = strip_tex_comments(text)
    newlines = line_index(text)
    okey = hashlib.sha256(origin.encode()).hexdigest()[:12]
    records = []
    for match in BEGIN_RE.finditer(clean):
        env = match.group(1)
        endmatch = re.search(r"\\end\s*\{" + re.escape(env) + r"\}", clean[match.end():])
        if not endmatch:
            db.execute("INSERT INTO parse_gaps VALUES(?,?,?,?)", (sha, origin, "unclosed_theorem_environment", str(match.start())))
            continue
        bodyend = match.end() + endmatch.start()
        end = match.end() + endmatch.end()
        body = text[match.end():bodyend]
        labels = LABEL_RE.findall(clean[match.start():end])
        rid = f"{sha}:{okey}:statement:{match.start()}"
        norm = re.sub(r"\s+", " ", LABEL_RE.sub("", strip_tex_comments(body))).strip()
        row = (rid, sha, origin, env, match.group(2) or "", dump(labels),
               line_number(newlines, match.start()), line_number(newlines, end), body,
               hashlib.sha256(norm.encode()).hexdigest())
        db.execute("INSERT INTO theorems VALUES(?,?,?,?,?,?,?,?,?,?)", row)
        records.append((match.start(), end, rid))
    headings = [(m.start(), m.group(1)) for m in HEADING_RE.finditer(clean)]
    proof_count = 0
    for match in PROOF_RE.finditer(clean):
        endmatch = re.search(r"\\end\s*\{" + re.escape(match.group(1)) + r"\}", clean[match.end():])
        if not endmatch:
            db.execute("INSERT INTO parse_gaps VALUES(?,?,?,?)", (sha, origin, "unclosed_proof_environment", str(match.start())))
            continue
        bodyend = match.end() + endmatch.start()
        end = match.end() + endmatch.end()
        body = text[match.end():bodyend]
        title = match.group(2) or ""
        prior_headings = [h for h in headings if h[0] < match.start()]
        heading = prior_headings[-1][1] if prior_headings else ""
        explicit = REF_RE.findall(title)
        targets = list(dict.fromkeys(label for group in explicit for label in group.split(",")))
        adjacent = None
        prior = [r for r in records if r[1] <= match.start()]
        if prior and not clean[prior[-1][1]:match.start()].strip():
            adjacent = prior[-1][2]
        rid = f"{sha}:{okey}:proof:{match.start()}"
        db.execute("INSERT INTO proofs VALUES(?,?,?,?,?,?,?,?,?,?)",
                   (rid, sha, origin, title, line_number(newlines, match.start()), line_number(newlines, end),
                    hashlib.sha256(body.encode()).hexdigest(), dump(targets), adjacent, heading))
        for target in targets:
            db.execute("INSERT INTO proof_links VALUES(?,?,?,?)", (rid, target, "explicit_proof_title_ref", line_number(newlines, match.start())))
        for group in REF_RE.findall(heading):
            for target in group.split(","):
                db.execute("INSERT INTO proof_links VALUES(?,?,?,?)", (rid, target, "enclosing_heading_ref_candidate", line_number(newlines, match.start())))
        for ref in REF_RE.finditer(clean[match.end():bodyend]):
            for target in ref.group(1).split(","):
                db.execute("INSERT INTO proof_links VALUES(?,?,?,?)", (rid, target, "proof_body_dependency_ref", line_number(newlines, match.end() + ref.start())))
        proof_count += 1
    for match in LABEL_RE.finditer(clean):
        context = next((r[2] for r in records if r[0] <= match.start() < r[1]), None)
        db.execute("INSERT INTO latex_labels VALUES(?,?,?,?,?)", (sha, origin, match.group(1), line_number(newlines, match.start()), context))
    # Some retained supplements use a proof heading followed by prose and qed,
    # rather than a proof environment. Preserve every such heading separately.
    for offset, heading in headings:
        if re.search(r"proof|demonstration", heading, re.I):
            db.execute("INSERT INTO signatures VALUES(?,?,?,?,?,?)", (sha, "proof_heading", line_number(newlines, offset), origin, "heading", heading))
    return len(records), proof_count


def parse_markdown_claims(sha, text):
    headings = list(re.finditer(r"(?m)^(#{1,6})\s+(.+)$", text))
    lines = line_index(text)
    count = 0
    for i, match in enumerate(headings):
        title = match.group(2)
        if not re.search(r"\b(theorem|proposition|lemma|corollary|claim|hypothes[ie]s|mathematical)\b|\bH[1-9]\d?\b", title, re.I):
            continue
        later = [m for m in headings[i + 1:] if len(m.group(1)) <= len(match.group(1))]
        end = later[0].start() if later else len(text)
        body = text[match.end():end]
        rid = f"{sha}:markdown_claim:{match.start()}"
        db.execute("INSERT INTO theorems VALUES(?,?,?,?,?,?,?,?,?,?)", (
            rid, sha, "native_markdown", "protocol_or_markdown_claim", title, dump([]),
            line_number(lines, match.start()), line_number(lines, end), body,
            hashlib.sha256(re.sub(r"\s+", " ", body).strip().encode()).hexdigest()))
        count += 1
    return count


def parse_python(sha, text, origin="native"):
    try:
        module = ast.parse(text)
    except (SyntaxError, ValueError, RecursionError) as exc:
        db.execute("INSERT INTO parse_gaps VALUES(?,?,?,?)", (sha, origin, "python_ast_error", str(exc)))
        return 0, "ast_error"
    count = 0
    okey = hashlib.sha256(origin.encode()).hexdigest()[:12]

    def visit(nodes, prefix=""):
        nonlocal count
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = prefix + node.name
                if isinstance(node, ast.ClassDef):
                    sig = "class " + node.name + "(" + ", ".join(ast.unparse(x) for x in node.bases) + ")"
                    kind = "class"
                else:
                    sig = ("async " if isinstance(node, ast.AsyncFunctionDef) else "") + "def " + node.name + "(" + ast.unparse(node.args) + ")"
                    if node.returns:
                        sig += " -> " + ast.unparse(node.returns)
                    kind = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
                rid = f"{sha}:{okey}:function:{node.lineno}:{name}"
                db.execute("INSERT INTO functions VALUES(?,?,?,?,?,?,?,?,?,?)", (
                    rid, sha, origin, name, kind, node.lineno, getattr(node, "end_lineno", None),
                    sig, bool(MODEL_RE.search(name)), ast.get_docstring(node) or ""))
                count += 1
                visit(node.body, name + ".")
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                visit(getattr(node, "body", []), prefix)
                visit(getattr(node, "orelse", []), prefix)
                visit(getattr(node, "finalbody", []), prefix)
                for handler in getattr(node, "handlers", []):
                    visit(handler.body, prefix)
    visit(module.body)
    for node in module.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                name = ast.unparse(target)
                if PARAM_RE.search(name) or MODEL_RE.search(name):
                    expression = ast.get_source_segment(text, node) or ast.unparse(node)
                    db.execute("INSERT INTO primitive_assignments VALUES(?,?,?,?,?)", (sha, origin, name, node.lineno, expression))
        if isinstance(node, ast.If) and "__name__" in ast.unparse(node.test):
            db.execute("INSERT INTO signatures VALUES(?,?,?,?,?,?)", (sha, "python_main_guard", node.lineno, origin, "condition", ast.unparse(node.test)))
    return count, "parsed"


def walk_json(value, path="$", depth=0):
    if depth > 200:
        raise RecursionError("JSON nesting beyond index traversal limit")
    if isinstance(value, dict):
        for key, item in value.items():
            p = path + "[" + dump(str(key)) + "]"
            yield str(key), item, p
            if isinstance(item, (dict, list)):
                yield from walk_json(item, p, depth + 1)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            p = path + f"[{i}]"
            if isinstance(item, (dict, list)):
                yield from walk_json(item, p, depth + 1)
            else:
                yield "[item]", item, p


all_counts = Counter()
source_stats = {}
selected = sorted(sha for sha, obj in inventory.items()
                  if obj["kind"] == "blob" and (set(extensions[sha]) & (SCIENCE | ANCILLARY)))
# Recover custom newtheorem aliases before scanning statement environments.
# This small10MB preliminary pass is also content-hash verified.
declared_environments = set()
tex_ids = [sha for sha in selected if ".tex" in extensions[sha]]
for sha, kind, data in batch_read(tex_ids):
    raw = strip_tex_comments(data.decode("utf-8", errors="replace"))
    for declaration in re.finditer(r"\\newtheorem\*?\s*\{([^{}]+)\}(?:\s*\[[^\]]*\])?\s*\{([^{}]+)\}", raw):
        declared_environments.add(declaration.group(1))
        db.execute("INSERT INTO signatures VALUES(?,?,?,?,?,?)", (sha, "newtheorem_declaration", line_number(line_index(raw), declaration.start()), None, declaration.group(1), declaration.group(2)))
default_environments = {"theorem", "proposition", "lemma", "corollary", "claim", "conjecture", "thm", "prop", "lem", "cor"}
all_environments = declared_environments | default_environments
BEGIN_RE = re.compile(r"\\begin\s*\{(" + "|".join(re.escape(e) + r"\*?" for e in sorted(all_environments, key=len, reverse=True)) + r")\}(?:\s*\[([^\]]*)\])?")
progress("read_available_science_and_evidence_blobs", count=len(selected),
         bytes=sum(inventory[sha]["size"] for sha in selected))
for number, (sha, kind, data) in enumerate(batch_read(selected), 1):
    if kind != "blob":
        raise RuntimeError("selected blob disappeared")
    exts = set(extensions[sha])
    sha256 = hashlib.sha256(data).hexdigest()
    db.execute("UPDATE objects SET sha256=? WHERE sha=?", (sha256, sha))
    try:
        text = data.decode("utf-8")
        utf8 = True
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="replace")
        utf8 = False
    tc = pc = fc = 0
    before_signatures = db.execute("SELECT total_changes()").fetchone()[0]
    statuses = []
    if ".tex" in exts:
        t, p = parse_tex(sha, text)
        tc += t
        pc += p
        statuses.append("tex_regex_parsed")
    if ".md" in exts:
        tc += parse_markdown_claims(sha, text)
        t, p = parse_tex(sha, text)
        tc += t
        pc += p
        statuses.append("markdown_claims_and_tex_parsed")
    if ".py" in exts:
        f, status = parse_python(sha, text)
        fc += f
        statuses.append(status)
    if ".json" in exts:
        try:
            value = json.loads(text)
            topkeys = list(value) if isinstance(value, dict) else {"root_type": type(value).__name__, "length": len(value) if isinstance(value, list) else None}
            db.execute("INSERT INTO signatures VALUES(?,?,?,?,?,?)", (sha, "json_root_schema", 1, "$", "root_keys", dump(topkeys)))
            for key, item, path in walk_json(value):
                if isinstance(item, (dict, list)):
                    continue
                matched_hashes = HASH_RE.findall(item) if isinstance(item, str) else []
                kinds = []
                if IDENT_KEY.search(key):
                    kinds.append("identity_or_custody_field")
                if STATUS_KEY.search(key):
                    kinds.append("reported_status_or_error_field")
                if METRIC_KEY.search(key):
                    kinds.append("reported_economic_or_work_field")
                if matched_hashes:
                    kinds.append("hash_literal")
                if isinstance(item, str) and TEXT_SIG.search(item):
                    kinds.append("reported_text_marker_not_execution_validation")
                for sigkind in kinds:
                    encoded = dump(item)
                    # Large embedded payloads remain in their source blob; the
                    # index records their exact length/hash and JSON position.
                    if len(encoded) > 8192:
                        encoded = dump({"embedded_value_not_copied": True,
                                        "characters": len(item) if isinstance(item, str) else len(encoded),
                                        "sha256_of_json_encoded_value": hashlib.sha256(encoded.encode()).hexdigest()})
                    db.execute("INSERT INTO signatures VALUES(?,?,?,?,?,?)", (sha, sigkind, None, path, key, encoded))
                if isinstance(item, str) and "\\begin{" in item and BEGIN_RE.search(item):
                    t, p = parse_tex(sha, item, "json:" + path)
                    tc += t
                    pc += p
                if isinstance(item, str) and key.endswith(".py") and re.search(r"(?m)^\s*(?:async\s+)?def\s+", item):
                    f, _ = parse_python(sha, item, "json:" + path)
                    fc += f
                if isinstance(item, str) and len(item) > 8192 and re.fullmatch(r"[A-Za-z0-9+/=\s]+", item):
                    db.execute("INSERT INTO signatures VALUES(?,?,?,?,?,?)", (sha, "unexpanded_possible_base64_payload", None, path, key, dump({"characters": len(item), "sha256": hashlib.sha256(item.encode()).hexdigest()})))
            statuses.append("json_parsed")
        except (ValueError, RecursionError) as exc:
            db.execute("INSERT INTO parse_gaps VALUES(?,?,?,?)", (sha, "native", "json_parse_or_walk_error", str(exc)))
            statuses.append("json_parse_error")
    if ".json" not in exts:
        for lineno, line in enumerate(text.splitlines(), 1):
            if TEXT_SIG.search(line):
                excerpt = line if len(line) <= 8192 else line[:8192]
                if len(line) > 8192:
                    excerpt += " [INDEX EXCERPT TRUNCATED; original line remains in Git blob]"
                db.execute("INSERT INTO signatures VALUES(?,?,?,?,?,?)", (sha, "source_text_marker_not_execution_validation", lineno, None, "keyword_match", excerpt))
            hashes = HASH_RE.findall(line)
            if hashes:
                db.execute("INSERT INTO signatures VALUES(?,?,?,?,?,?)", (sha, "hash_literals_in_source_line", lineno, None, "hashes", dump(list(dict.fromkeys(hashes)))))
    # Counts are obtained from the normalized records, not inferred from words.
    sc = db.execute("SELECT count(*) FROM signatures WHERE blob_sha=?", (sha,)).fetchone()[0]
    line_count = text.count("\n") + bool(text and not text.endswith("\n"))
    db.execute("INSERT INTO source_blobs VALUES(?,?,?,?,?,?,?,?,?,?)", (
        sha, dump(sorted(exts)), line_count, utf8,
        "science" if exts & SCIENCE else "ancillary_evidence",
        ";".join(statuses) or "text_signatures_only", tc, pc, fc, sc))
    source_stats[sha] = {"theorems": tc, "proofs": pc, "functions": fc, "science": bool(exts & SCIENCE)}
    all_counts.update({"indexed_blobs": 1, "indexed_bytes": len(data), "theorems": tc, "proofs": pc, "functions": fc, "signatures": sc})
    if number % 2000 == 0:
        progress("blob_scan_progress", scanned=number, total=len(selected), elapsed_seconds=round(time.monotonic() - T0, 2))

db.executescript("""
CREATE INDEX theorem_blob_idx ON theorems(blob_sha);
CREATE INDEX theorem_normalized_idx ON theorems(normalized_sha256);
CREATE INDEX labels_label_idx ON latex_labels(label);
CREATE INDEX proof_links_label_idx ON proof_links(label);
CREATE INDEX functions_name_idx ON functions(qualified_name);
CREATE INDEX IF NOT EXISTS signatures_blob_idx ON signatures(blob_sha);
CREATE INDEX tree_child_idx ON tree_edges(child_sha);
""")
db.commit()
progress("extract_portable_indexes")


def export_table(table, name=None):
    name = name or table
    cur = db.execute("SELECT * FROM " + table)
    columns = [d[0] for d in cur.description]
    target = OUT / ("HISTORICAL_" + name + ".jsonl.gz")
    with gzip.open(target, "wt", encoding="utf-8", compresslevel=6) as handle:
        for row in cur:
            handle.write(dump(dict(zip(columns, row))) + "\n")
    return {"file": target.name, "bytes": target.stat().st_size,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}


exports = [export_table(name) for name in (
    "objects", "commits", "tree_edges", "source_blobs", "theorems", "latex_labels",
    "proofs", "proof_links", "functions", "primitive_assignments", "signatures", "parse_gaps")]

missing_extensions = Counter()
missing_science = Counter()
missing_tree_paths = []
with (OUT / "HISTORICAL_missing_objects.jsonl").open("w") as handle:
    for sha, obj in inventory.items():
        if obj["kind"] != "missing":
            continue
        exts = extensions[sha]
        missing_extensions.update(exts or ["unknown"])
        missing_science.update(set(exts) & SCIENCE)
        is_tree = sha in tree_parents
        if is_tree:
            missing_tree_paths.append(sha)
        handle.write(dump({**obj, "extensions": exts, "inferred_object_kind": "tree" if is_tree else "blob" if sha in blob_parents else "unknown",
                           "byte_size_known_locally": False,
                           "containing_commit_count": blob_masks.get(sha, 0).bit_count(),
                           "leaf_names": sorted(aliases.get(sha, []))}) + "\n")

branch_summaries = []
by_head = {}
for row in api:
    sha = row["sha"]
    if sha not in commit_index:
        branch_summaries.append({**row, "local_commit_available": False})
        continue
    if sha not in by_head:
        bit = 1 << commit_index[sha]
        count = Counter()
        for objsha, mask in blob_masks.items():
            if mask & bit:
                count["unique_blob_count"] += 1
                available = inventory.get(objsha, {}).get("kind") == "blob"
                count["available_blob_count" if available else "missing_blob_count"] += 1
                for ext in set(extensions.get(objsha, [])) & SCIENCE:
                    count[("available_" if available else "missing_") + ext] += 1
                if objsha in source_stats:
                    s = source_stats[objsha]
                    count["theorem_statement_records"] += s["theorems"]
                    count["proof_environment_records"] += s["proofs"]
                    count["python_entrypoint_records"] += s["functions"]
        by_head[sha] = dict(count)
    branch_summaries.append({**row, "local_commit_available": True, **by_head[sha]})
(OUT / "HISTORICAL_branch_coverage.json").write_text(json.dumps(branch_summaries, indent=2) + "\n")

schema_counts = {name: db.execute("SELECT count(*) FROM " + name).fetchone()[0]
                 for name in ("objects", "commits", "tree_edges", "refs", "source_blobs", "theorems",
                              "latex_labels", "proofs", "proof_links", "functions", "primitive_assignments",
                              "signatures", "parse_gaps")}
label_variants = db.execute("SELECT count(*) FROM (SELECT label FROM latex_labels GROUP BY label)").fetchone()[0]
formal_count = db.execute("SELECT count(*) FROM theorems WHERE environment!='protocol_or_markdown_claim'").fetchone()[0]
scientific_available = sum(obj["kind"] == "blob" and bool(set(extensions[sha]) & SCIENCE) for sha, obj in inventory.items())
science_indexed = sum(s["science"] for s in source_stats.values())
coverage = {
    "snapshot_started_utc": START, "completed_utc": datetime.now(timezone.utc).isoformat(),
    "elapsed_seconds": time.monotonic() - T0,
    "repository": "TrillionniumFoundation/NBO",
    "offline_policy": "GIT_NO_LAZY_FETCH=1; git cat-file and captured reachable graph only; no historical program execution",
    "captured_git_refs": len(ref_rows), "inventoried_api_branches": len(api),
    "api_branch_ref_sha_mismatches": 0,
    "reachable_objects": len(inventory), "object_kind_counts": dict(Counter(x["kind"] for x in inventory.values())),
    "all_reachable_available_trees_read_and_hash_verified": len(trees),
    "all_reachable_available_commits_read_and_hash_verified": len(commits),
    "available_science_blobs": scientific_available, "indexed_science_blobs": science_indexed,
    "available_science_bytes": sum(inventory[s]["size"] for s in source_stats if source_stats[s]["science"]),
    "indexed_ancillary_blobs": len(selected) - science_indexed,
    "schema_counts": schema_counts, "formal_tex_statement_records": formal_count,
    "statement_environment_counts": dict(db.execute("SELECT environment,count(*) FROM theorems GROUP BY environment")),
    "markdown_protocol_claim_records": schema_counts["theorems"] - formal_count,
    "unique_latex_labels": label_variants,
    "missing_extensions_alias_count": dict(missing_extensions), "missing_science_extension_alias_count": dict(missing_science),
    "missing_tree_sha": missing_tree_paths,
    "missing_object_byte_size_scope": "Sizes not present locally; no claim that every missing object exceeds256KiB. The earlier small-object fetch is a custody claim to check against its own retained log.",
    "theorem_parser_scope": "Named standard theorem/proposition/lemma/corollary/claim/conjecture environments and common aliases; markdown mathematical/hypothesis headings separately classified. Unexpanded macro-generated statements and encoded archives remain explicit scope limitations.",
    "newtheorem_environments_discovered": sorted(declared_environments),
    "proof_link_scope": "Explicit title references, enclosing-heading candidates, body-dependency references, and separately marked immediate-adjacency links. Duplicate historical labels are not forced into a single theorem/proof identity.",
    "large_signature_values": "Values over8192characters are represented by exact JSON-position/length/hash; original bytes remain addressable in their indexed Git blob.",
    "scientific_verification_scope": "Machine content inventory and syntax extraction; not independent proof of every theorem or validation of every reported execution.",
    "exports": exports,
}
(OUT / "HISTORICAL_coverage.json").write_text(json.dumps(coverage, indent=2) + "\n")
db.close()
progress("complete", **{k: coverage[k] for k in ("elapsed_seconds", "available_science_blobs", "indexed_science_blobs", "schema_counts", "missing_science_extension_alias_count")})
