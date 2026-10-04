"""Adversarial tests for irreversible publication and preservation gates.

Fixtures use temporary local Git repositories and synthetic bytes only. They
never train, sample a scientific bank, contact a remote service, or write any
NBO branch. Favorable numerical results are not a publication test condition.
"""
from __future__ import annotations

import copy
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import publication_audit as a
import publication_families as f
import delivery as d
import layout_diagnostics as layout


class TreeOnly:
    def __init__(self, trees):
        self.trees = trees

    def tree(self, commit):
        return self.trees[commit]

    def blob(self, oid):
        raise AssertionError('a sparse history check requested raw content')

    compare = blob


class PublicationGates(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='nbo-r16-publication-test-')
        self.repo = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def put(self, name, data=b'original'):
        p = self.repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return a.file_record(p)

    def test_all_history_leaves_preserved_without_materializing_raw(self):
        old = {'ECTA.tex': {'mode': '100644', 'git_blob': 'a' * 40},
               'raw/large-array.npz': {'mode': '100644', 'git_blob': 'b' * 40}}
        current = {str(a.ROOT_ARCHIVE['ECTA.tex']): old['ECTA.tex'], 'raw/large-array.npz': old['raw/large-array.npz']}
        result = a.check_history(self.repo, TreeOnly({'old': old, 'new': current}), 'new', commit='old', expected_count=2)
        self.assertEqual(result['blobs'], 2)
        self.assertFalse(any(r['materialized'] for r in result['files'].values()))

    def test_missing_root_archive_rejected_even_when_original_root_exists(self):
        old = {'ECTA.tex': {'mode': '100644', 'git_blob': 'a' * 40}}
        with self.assertRaisesRegex(ValueError, 'historical Git leaf'):
            a.check_history(self.repo, TreeOnly({'old': old, 'new': old}), 'new', commit='old', expected_count=1)

    def test_missing_or_mode_changed_raw_leaf_rejected(self):
        old = {'raw/data': {'mode': '100644', 'git_blob': 'b' * 40}}
        for current in [{}, {'raw/data': {'mode': '100755', 'git_blob': 'b' * 40}}]:
            with self.assertRaises(ValueError):
                a.check_history(self.repo, TreeOnly({'old': old, 'new': current}), 'new', commit='old', expected_count=1)

    def test_same_size_materialized_history_tamper_rejected(self):
        facts = self.put('raw/data', b'abcd')
        leaf = {'mode': '100644', 'git_blob': facts['git_blob']}
        self.put('raw/data', b'abce')
        with self.assertRaisesRegex(ValueError, 'materialized historical'):
            a.check_history(self.repo, TreeOnly({'old': {'raw/data': leaf}, 'new': {'raw/data': leaf}}), 'new', commit='old', expected_count=1)

    def test_checked_record_rejects_false_sha_or_git_identity(self):
        row = self.put('evidence/input.npz')
        for field in ['sha256', 'bytes', 'git_blob']:
            bad = dict(row)
            bad[field] = 99 if field == 'bytes' else '0' * len(row[field])
            with self.assertRaises(ValueError):
                f.checked_record(self.repo, 'evidence/input.npz', bad)

    def test_manifest_escape_and_symlink_rejected(self):
        for name in ['../escape', '/absolute', '.']:
            with self.assertRaises(ValueError):
                a.safe_path(self.repo, name)
        self.put('source')
        (self.repo / 'alias').symlink_to(self.repo / 'source')
        with self.assertRaises(ValueError):
            a.safe_path(self.repo, 'alias')

    def test_source_leaf_replacement_and_omission_rejected(self):
        source = {'code/source.py': {'mode': '100644', 'git_blob': 'a' * 40}}
        for final in [{}, {'code/source.py': {'mode': '100644', 'git_blob': 'b' * 40}}]:
            with self.assertRaises(ValueError):
                f.compare_git_leaves(source, final, source, 'scientific source')

    def test_evidence_parent_gate_uses_raw_commit_in_a_shallow_checkout(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        env = dict(os.environ, GIT_AUTHOR_NAME='test', GIT_COMMITTER_NAME='test',
                   GIT_AUTHOR_EMAIL='test@example.test', GIT_COMMITTER_EMAIL='test@example.test')
        self.put('source.txt', b'fixture')
        subprocess.run(['git', 'add', 'source.txt'], cwd=self.repo, check=True)
        tree = d.git(self.repo, 'write-tree').decode().strip()
        source = d.git(self.repo, 'commit-tree', tree, '-m', 'S', env=env).decode().strip()
        other = d.git(self.repo, 'commit-tree', tree, '-m', 'other', env=env).decode().strip()
        evidence = d.git(self.repo, 'commit-tree', tree, '-p', source, '-m', 'E', env=env).decode().strip()
        merge = d.git(self.repo, 'commit-tree', tree, '-p', source, '-p', other, '-m', 'invalid E', env=env).decode().strip()
        (self.repo / '.git/shallow').write_text(evidence + '\n')
        self.assertEqual(d.git(self.repo, 'rev-list', '--parents', '-n', '1', evidence).decode().split(), [evidence])
        store = a.GitStore(self.repo)
        try:
            self.assertEqual(f.require_commit_parent(store, evidence, source, 'fixture E'), source)
            for commit, predecessor in [(evidence, other), (merge, source), (source, other)]:
                with self.assertRaisesRegex(ValueError, 'declared predecessor'):
                    f.require_commit_parent(store, commit, predecessor, 'fixture E')
        finally:
            store.close()

    def test_proof_normalization_does_not_erase_changed_assumptions(self):
        one = r'\begin{theorem}If $h<1$, the bound holds.\end{theorem}'
        two = r'\begin{theorem}If $h<2$, the bound holds.\end{theorem}'
        self.assertNotEqual(a.canonical_math(one), a.canonical_math(two))
        self.assertEqual(a.canonical_math(one), a.canonical_math(one.replace('the bound', 'the\n bound') + '% editorial note'))

    def test_full_heading_proof_includes_entire_argument(self):
        text = r'\section{Proof of Theorem 1}' + '\nFirst step.\n' + r'\subsection{Second step}' + '\nLast step.\n' + r'\section{Other result}'
        blocks = list(a.proof_sections(text))
        self.assertEqual(len(blocks), 1)
        self.assertIn('Last step.', blocks[0][1])
        self.assertNotIn('Other result', blocks[0][1])

    def test_rebuilt_roots_cannot_differ_from_reviewed_delivery_source(self):
        names = [str(path) for path in a.ROOTS.values()] + [str(a.R / name) for name in
            ('ARCHIVE_MANIFEST.json', 'EDITORIAL_MAP.json', 'MATHEMATICAL_PRESERVATION.json')]
        tree = {}
        for name in names:
            facts = self.put(name, b'reviewed generated source')
            tree[name] = dict(mode='100644', git_blob=facts['git_blob'])
        tree['ECTA.tex']['git_blob'] = 'c' * 40
        with self.assertRaisesRegex(ValueError, 'reviewed source in D'):
            a.check_editorial_replay(self.repo, {}, TreeOnly({'D': tree}), 'D')
        tree['ECTA.tex']['git_blob'] = a.file_record(self.repo / 'ECTA.tex')['git_blob']
        tree[str(a.R / 'retained/omitted.tex')] = dict(mode='100644', git_blob='d' * 40)
        with self.assertRaisesRegex(ValueError, 'retained component set'):
            a.check_editorial_replay(self.repo, {}, TreeOnly({'D': tree}), 'D')

    def test_author_table_rejects_changed_or_omitted_target_counts(self):
        methods = {'NBO': 'nbo', 'Raw': 'raw_costate', 'Direct policy': 'direct_policy', 'Neural HJB': 'neural_hjb'}
        counts, rows = [], []
        for dimension in (10, 50):
            for method, method_id in methods.items():
                rows.append(f'{dimension} & {method} & 2--16 & 0--15' + r'\\')
                counts.extend([dict(dimension=dimension, method_id=method_id, target=target,
                                    definitely_attaining=lower, possibly_attaining=upper)
                               for target, lower, upper in [(.0005, 2, 16), (.001, 0, 15)]])
        report = self.repo / f.role_paths('replication')['evidence'] / 'report/REPORT.json'
        a.write(report, {'final_certified_attainment': counts})
        source = self.repo / a.R / 'manuscript/replication_supplement.tex'
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('\n'.join(rows) + '\n')
        self.assertTrue(f.check_author_tables(self.repo)['all_values_reproduced'])
        for text in ['\n'.join(rows).replace('2--16', '3--16', 1), '\n'.join(rows[:-1])]:
            source.write_text(text + '\n')
            with self.assertRaisesRegex(ValueError, 'author attainment table'):
                f.check_author_tables(self.repo)

    def test_worker_environment_spoof_rejected(self):
        actual = dict(packages={'numpy': 'x'}, threads=1, python='3.12.1', platform='Linux-x86')
        contract = dict(packages={'numpy': 'x'}, numeric_threads=1, python='3.12', platform='Linux')
        fp = hashlib.sha256(a.canonical(actual)).hexdigest()
        f.verify_environment(actual, fp, contract)
        changed = dict(actual, threads=2)
        with self.assertRaises(ValueError):
            f.verify_environment(changed, fp, contract)
        changed_fp = hashlib.sha256(a.canonical(changed)).hexdigest()
        with self.assertRaises(ValueError):
            f.verify_environment(changed, changed_fp, contract)

    def test_layout_rejects_blank_or_clipped_pages(self):
        def page(x):
            words = ''.join(f'<word xMin="{x}" xMax="100" yMin="20" yMax="30">word</word>' for _ in range(3))
            return ET.fromstring('<doc><page width="612" height="792">' + words + '</page></doc>')
        self.assertEqual(len(layout.check_bounds(page(10))), 1)
        with self.assertRaises(ValueError):
            layout.check_bounds(page(-3))
        with self.assertRaises(ValueError):
            layout.check_bounds(ET.fromstring('<doc><page width="612" height="792"/></doc>'))

    def test_visual_fingerprint_changes_with_any_scientific_source_byte(self):
        facts = self.put('theory.tex')
        left = {'theory.tex': facts}
        right = copy.deepcopy(left)
        right['theory.tex']['sha256'] = '0' * 64
        self.assertNotEqual(layout.source_fingerprint(left), layout.source_fingerprint(right))

    def test_atomic_push_has_three_empty_creation_leases(self):
        final = 'a' * 40
        command = d.atomic_push_command(final)
        self.assertIn('--atomic', command)
        self.assertNotIn('--force', command)
        self.assertNotIn('--delete', command)
        leases = [arg for arg in command if arg.startswith('--force-with-lease=')]
        self.assertEqual(leases, ['--force-with-lease=refs/heads/' + b + ':' for b in a.TARGET_BRANCHES])
        targets = [arg for arg in command if arg.startswith(final + ':')]
        self.assertEqual(targets, [final + ':refs/heads/' + b for b in a.TARGET_BRANCHES])

    def test_private_index_preserves_missing_raw_and_does_not_change_head(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        env = dict(os.environ, GIT_AUTHOR_NAME='test', GIT_COMMITTER_NAME='test',
                   GIT_AUTHOR_EMAIL='test@example.test', GIT_COMMITTER_EMAIL='test@example.test', GIT_NO_LAZY_FETCH='1')
        self.put('source.txt', b'frozen source')
        subprocess.run(['git', 'add', 'source.txt'], cwd=self.repo, check=True)
        # A deliberately unmaterialized object is placed in a valid tree. This
        # is the relevant partial-clone constraint: no command may read it.
        missing = 'a' * 40
        subprocess.run(['git', 'update-index', '--add', '--cacheinfo', '100644,' + missing + ',raw/absent.npz'], cwd=self.repo, check=True)
        tree = d.git(self.repo, 'write-tree', '--missing-ok', env=env).decode().strip()
        source = d.git(self.repo, 'commit-tree', tree, '-m', 'fixture D', env=env).decode().strip()
        subprocess.run(['git', 'update-ref', 'HEAD', source], cwd=self.repo, check=True)
        index_before = (self.repo / '.git/index').read_bytes()
        facts = self.put('article.pdf', b'generated document')
        updates = {'article.pdf': dict(**facts, mode='100644', storage='materialized')}
        store = a.GitStore(self.repo)
        try:
            old = store.tree(source)
            final, changed = d.construct_commit(self.repo, source, old, updates)
            new = store.tree(final)
            self.assertEqual(new['raw/absent.npz'], old['raw/absent.npz'])
            self.assertEqual(new['source.txt'], old['source.txt'])
            self.assertEqual(new['article.pdf']['git_blob'], facts['git_blob'])
            self.assertEqual(changed, ['article.pdf'])
            self.assertEqual(d.git(self.repo, 'rev-parse', 'HEAD').decode().strip(), source)
            self.assertEqual((self.repo / '.git/index').read_bytes(), index_before)
            self.assertEqual(d.git(self.repo, 'rev-list', '--parents', '-n', '1', final).decode().split(), [final, source])
            self.assertFalse((self.repo / '.git/objects' / missing[:2] / missing[2:]).exists())
        finally:
            store.close()

    def test_sparse_raw_cannot_be_invented_in_publication(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        self.put('base')
        subprocess.run(['git', 'add', 'base'], cwd=self.repo, check=True)
        env = dict(os.environ, GIT_AUTHOR_NAME='test', GIT_COMMITTER_NAME='test',
                   GIT_AUTHOR_EMAIL='test@example.test', GIT_COMMITTER_EMAIL='test@example.test')
        subprocess.run(['git', 'commit', '-qm', 'base'], cwd=self.repo, check=True, env=env)
        source = d.git(self.repo, 'rev-parse', 'HEAD').decode().strip()
        with self.assertRaisesRegex(ValueError, 'manufacture absent raw'):
            d.construct_commit(self.repo, source, {}, {'invented.npz': dict(mode='100644', git_blob='c' * 40, storage='preserved_git_leaf')})


class BboxParsingTests(unittest.TestCase):
    def test_poppler_math_control_codes_preserve_word_geometry(self):
        from layout_diagnostics import parse_bbox_xml, check_bounds
        data = b'<html><page width="600" height="800"><word xMin="10" yMin="20" xMax="30" yMax="40">\x14</word><word xMin="40" yMin="20" xMax="50" yMax="40">value</word><word xMin="50" yMin="20" xMax="60" yMax="40">\x15</word></page></html>'
        original = bytes(data)
        parsed, counts = parse_bbox_xml(data)
        self.assertEqual(data, original)
        self.assertEqual(counts, {'U+0014': 1, 'U+0015': 1})
        rows = check_bounds(parsed)
        self.assertEqual(rows[0]['extractable_words'], 3)
        self.assertEqual(rows[0]['text_outside_page'], [])
        words = parsed.findall('.//word')
        self.assertEqual(words[1].text, 'value')
        self.assertEqual(words[0].attrib, {'xMin': '10', 'yMin': '20', 'xMax': '30', 'yMax': '40'})


if __name__ == '__main__':
    unittest.main()
