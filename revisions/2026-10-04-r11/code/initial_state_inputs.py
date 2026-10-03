"""Normalize JSON numeric initial-state parameters before numerical allocation.

The verification API declares floating-point shift/spread parameters. JSON
preserves integer spellings; these adapters preserve their numeric values while
preventing NumPy from allocating integer state arrays before adding dispersion.
"""
import math

def floating_initial_state(kwargs):
    result=dict(kwargs)
    for name in ('shift','spread'):
        if name in result:
            result[name]=float(result[name])
            if not math.isfinite(result[name]):
                raise ValueError('initial-state parameters must be finite')
    if result.get('spread',0.)<0:
        raise ValueError('initial-state spread must be nonnegative')
    return result
