"""Describe the roles of already selected cost blockers; no new selection/economics."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'code125/frozen_inputs/revisions/2026-10-22-r123/vendor/2026-10-20-r121'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    tick = time.perf_counter()
    diagnostic_path = ROOT / 'results125/ADOPTION_SUPPORT_DIAGNOSTIC125.json'
    before = sha(diagnostic_path)
    diagnostic = json.loads(diagnostic_path.read_text())
    source_paths = [VENDOR / 'code121/campaign121.py', VENDOR / 'code121/models121.py']
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in source_paths}
    inputs[str(diagnostic_path.relative_to(ROOT))] = before
    models = {}
    for budget in (5, 9):
        for index in (0, 1):
            for arm in ('relu', 'poly2'):
                for loss in ('value', 'marginal'):
                    p = VENDOR / f'results121/acquisition{budget}-attempt01/models/{index}-{arm}-{loss}/model.json'
                    model = json.loads(p.read_text())
                    assert model['index'] == index and model['loss'] == loss
                    assert model['basis']['arm'] == arm and model['basis']['budget'] == budget
                    models[(index, budget, arm, loss)] = model
                    inputs[str(p.relative_to(ROOT))] = sha(p)
            hashes = {models[(index, budget, arm, loss)]['label_sha256']
                      for arm in ('relu', 'poly2') for loss in ('value', 'marginal')}
            assert len(hashes) == 1
    assert len({model['label_sha256'] for model in models.values()}) == 4
    rows = []
    for original in diagnostic['positive_price_identity_blocker_witnesses']:
        own = original['cohort']; other = original['chosen_blocker']
        assert own[2] == 'relu' and own[0] == other[0]
        own_model = models[tuple(own[:4])]
        online = other[2] == 'online'
        assert online or other[2] == 'poly2'
        other_model = None if online else models[tuple(other[:4])]
        same_bundle = (other_model is not None and
                       other_model['label_sha256'] == own_model['label_sha256'])
        assert same_bundle == (not online and own[1] == other[1])
        # This compares immutable stored feature declarations, not finite test outputs.
        feature_equal = (other_model is not None and
                         own_model['basis']['type'] == other_model['basis']['type'] and
                         own_model['basis']['feature_count'] == other_model['basis']['feature_count'])
        assert not feature_equal
        rows.append(dict(
            cohort=own, N=original['N'], chosen_blocker=other,
            same_risk=True, same_actual_original_policy=True,
            same_actual_action_hex=original['same_actual_action_hex'],
            same_future_controller=original['same_future_controller'],
            same_budget_label=own[1] == other[1],
            same_fitting_loss_label=own[3] == other[3],
            same_budget_and_fitting_loss=own[1] == other[1] and own[3] == other[3],
            same_service_mode=own[4] == other[4],
            own_label_sha256=own_model['label_sha256'],
            blocker_label_sha256=None if online else other_model['label_sha256'],
            same_acquired_training_label_digest=same_bundle,
            own_basis_type=own_model['basis']['type'],
            own_feature_count=own_model['basis']['feature_count'],
            blocker_basis_type=None if online else other_model['basis']['type'],
            blocker_feature_count=None if online else other_model['basis']['feature_count'],
            same_feature_dictionary=feature_equal,
            matched_hinge_comparator=False,
            blocker_role=('direct online conventional service without fitted training labels'
                          if online else 'polynomial service with a different feature dictionary'),
            equal_complete_service_information_claim=False,
            cost_gap_unchanged=original['strictly_positive_complete_cost_gap'],
        ))
    count_keys = ('same_budget_label', 'same_fitting_loss_label',
                  'same_budget_and_fitting_loss', 'same_service_mode',
                  'same_acquired_training_label_digest', 'same_feature_dictionary',
                  'matched_hinge_comparator')
    counts = {k: sum(r[k] for r in rows) for k in count_keys}
    roles = Counter(r['chosen_blocker'][2] for r in rows)
    budget_relation = Counter('lower' if r['chosen_blocker'][1] < r['cohort'][1]
                              else 'higher' if r['chosen_blocker'][1] > r['cohort'][1]
                              else 'equal' for r in rows)
    assert counts == dict(same_budget_label=32, same_fitting_loss_label=32,
                         same_budget_and_fitting_loss=16, same_service_mode=32,
                         same_acquired_training_label_digest=32,
                         same_feature_dictionary=0, matched_hinge_comparator=0)
    assert roles == {'online': 64, 'poly2': 64}
    assert budget_relation == {'lower': 88, 'equal': 32, 'higher': 8}
    assert sha(diagnostic_path) == before
    result = dict(
        status='executed', economic_evaluations=0, services_retimed=0,
        existing_blockers_reselected=False, original_diagnostic_unchanged=True,
        original_adoption_classifications_unchanged=True,
        witnesses=len(rows), selected_blocker_roles=dict(roles), matching_counts=counts,
        blocker_budget_relation=dict(budget_relation),
        selected_training_label_roles=dict(
            same_stored_training_label_digest=32,
            different_stored_training_label_digest=32,
            direct_online_no_training_label_bundle=64),
        information_identity_evidence=(
            'The inherited frozen models record identical label_sha256 for each risk/budget '
            'across ReLU/poly2 and both fitting losses. The inherited acquisition code uses '
            'one complete value-and-marginal label bundle for every representation and loss '
            'at that risk/budget. This report compares those stored digest references; '
            'it does not independently re-hash the unmaterialized historical label byte streams. '
            'Equality of acquired training labels does not assert identical fitted losses, '
            'feature dictionaries or all subsequent paid decision-service oracle information.'),
        interpretation=(
            'This post-execution diagnostic describes cost competition among services with '
            'the same actual original policy at the first workload, conditional on the '
            'recorded timing ranges. It is not a matched-feature representation experiment, '
            'an equal-resource complexity bound, or neural representational dominance.'),
        rows=rows, input_sha256=inputs, script_sha256=sha(Path(__file__)),
        seconds=time.perf_counter()-tick,
    )
    output = ROOT / 'results125/ADOPTION_BLOCKER_COMPARABILITY125.json'
    with output.open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True); f.write('\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('rows', 'input_sha256')}, sort_keys=True))


if __name__ == '__main__':
    main()
