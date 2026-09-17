"""Conservative absolute round-to-nearest budget on stored finite arrays.

This is not interval arithmetic for constructing the kernel. Endpoint and
signed-correction errors are propagated separately; no empirical replay error
is used to choose the budget.
"""
import numpy as np

def audit(mix,width):
    kernels=[k for e in mix.e for k in [e.common]+e.extra]
    beta=max(k.check['max_row_mass'] for k in kernels)+1e-12
    if beta>1+2e-12:raise ValueError('Unbudgeted row-mass amplification')
    R=2*max(float(abs(k.base).max()+abs(k.duration).max()+mix.spec.cost*abs(k.effort).max()) for k in kernels)
    H=mix.steps;G=2*float(abs(mix.terminal).max());unit=2.**-53
    def gamma(n):return n*unit/(1-n*unit)
    B=np.zeros(H+1);E=B.copy();M=B.copy();D=B.copy();B[-1]=G
    for n in range(H-1,-1,-1):
        B[n]=R+beta*B[n+1]
        E[n]=beta*E[n+1]+gamma(4096)*(1+R+4*beta*(B[n+1]+E[n+1]))
        if n<H-1:
            M[n]=4*width*beta*B[n+1]+beta*M[n+1]
            D[n]=beta*D[n+1]+4*width*beta*E[n+1]+gamma(4096)*(1+8*width*beta*(B[n+1]+E[n+1])+4*beta*(M[n+1]+D[n+1]))
    magnitude=B[0]+.5*M[0]
    upper_error=E[0]+.5*D[0]+gamma(32)*(1+2*(B[0]+E[0])+M[0]+D[0])
    lower_error=3*E[0]+gamma(16)*(1+4*B[0])
    # Two de Casteljau passes, reward-feature construction and tensor extrema.
    restriction=gamma(4096*(H+1))*(1+4*B[0])
    final=gamma(32)*(1+4*magnitude)
    derived=max(upper_error,lower_error+restriction)+final
    allowance=1e-7
    if not derived<allowance:raise ValueError(f'Arithmetic budget requires revision: {derived}')
    return dict(unit_roundoff=unit,row_mass_bound=beta,reward_bound=R,endpoint_value_bounds=B.tolist(),
        endpoint_error_bounds=E.tolist(),correction_magnitude_bounds=M.tolist(),correction_error_bounds=D.tolist(),
        derived_per_class_bound=derived,per_class_allowance=allowance,
        scope='IEEE round-to-nearest evaluation relative to stored finite arrays; excludes kernel-construction, continuous-state and diffusion error')
