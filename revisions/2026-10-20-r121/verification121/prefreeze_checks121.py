"""Source syntax and independent algebra checks, never economic acquisition.

No original Bellman operator, economic label, fitted research readout, OS sample,
or experimental service is evaluated. The fixed algebra points exercise domain
endpoints, switches and each serialized finite representation.
"""
from pathlib import Path
from fractions import Fraction as F
import json
import sys
import time

REVISION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REVISION/'code121'))
import models121 as production
import training_audit121 as independent
import stats121
import numpy as np


def main():
    started = time.perf_counter(); parsed = []
    for path in sorted((REVISION/'code121').glob('*.py')):
        compile(path.read_bytes(), str(path), 'exec'); parsed.append(path.name)
    certificate = stats121.radius_certificate()
    points = [[0, 0, 0], [1, 1, 1], [.5, .5, .5], [.25, .75, .125],
              [.75, .25, .375], [.5, .5, .625], [.25, .25, .875],
              [.125, .875, .25], [.875, .125, .75], [.5, 0, 1]]
    comparisons = 0; largest = F(0); identities = 0
    for budget in (5, 9):
        for arm in production.ARMS:
            desc = production.definition(arm, budget)
            for derivative in (False, True):
                for side in (-1, 0, 1):
                    matrix = production.feature_matrix(desc, points, derivative, side)
                    for point, row in zip(points, matrix):
                        exact = independent.basis(desc, point, derivative, side)
                        for j, value in enumerate(row):
                            error = abs(F(float(value))-exact.get(j, F(0)))
                            largest = max(largest, error); comparisons += 1
                            if error > F(1, 2**38):
                                raise ArithmeticError(('Independent algebra mismatch', budget, arm, derivative, side, point, j, str(error)))
            if arm == 'relu':
                other = production.definition('hinge', budget)
                for derivative in (False, True):
                    for side in (-1, 1):
                        a = production.feature_matrix(desc, points, derivative, side)
                        b = production.feature_matrix(other, points, derivative, side)
                        if not np.array_equal(a, b):
                            raise ArithmeticError('Exact feature-matched ReLU/hinge encoding differs at algebra points')
                        identities += 1
    print(json.dumps(dict(status='passed', parsed_source_files=parsed, independent_feature_entry_comparisons=comparisons,
          largest_exact_assembly_difference=str(largest), relu_hinge_matrix_identities=identities,
          radius_certificate=stats121.encoded(certificate), elapsed_seconds=time.perf_counter()-started,
          original_economic_queries=0, acquired_research_models=0, sample_draws=0,
          prefreeze_algebra_diagnostic_not_a_scientific_campaign=True), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
