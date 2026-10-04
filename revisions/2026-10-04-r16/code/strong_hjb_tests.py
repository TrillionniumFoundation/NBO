"""Manufactured derivative, root, binding and API checks; no payoffs."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import torch
import strong_hjb as h


P = dict(T=2., discount=.04, productivity=.1, coupling=.15,
         idiosyncratic_sigma=.6, common_sigma=.3, adjustment=.2,
         lower=.02, upper=2., CHI=.1)


def reference_jet(critic, states):
    x = states.detach().requires_grad_(True)
    v = critic(x)
    g = torch.autograd.grad(v.sum(), x, create_graph=True)[0]
    tr = 0.
    for j in range(critic.d):
        hj = torch.autograd.grad(g[:, j+1].sum(), x, create_graph=True, retain_graph=True)[0]
        tr = tr+critic.params["idiosyncratic_sigma"]**2*hj[:, j+1:j+2]
    common = torch.autograd.grad(g[:, 1:].sum(), x, create_graph=True, retain_graph=True)[0][:, 1:].sum(1, keepdim=True)
    tr = tr+critic.params["common_sigma"]**2*common
    return v, g[:, :1], g[:, 1:], tr


def reference_root(p, t, params, epsilon):
    low, high = h.action_bounds(t, params, epsilon)
    a, b = low.clone(), high.clone()
    for _ in range(50):
        z = (a+b)/2
        den = len(p[0])*p+params["adjustment"]*z
        action = torch.where(den>0, 1/den.clamp_min(1e-300), high.expand_as(p))
        action = torch.maximum(low, torch.minimum(high, action))
        above = action.mean(1, keepdim=True)>z
        a = torch.where(above, z, a)
        b = torch.where(above, b, z)
    den = len(p[0])*p+params["adjustment"]*(a+b)/2
    action = torch.where(den>0, 1/den.clamp_min(1e-300), high.expand_as(p))
    return torch.maximum(low, torch.minimum(high, action))


def check_arithmetic():
    rows = []
    for d in [1, 10, 50]:
        torch.manual_seed(87000+d)
        critic = h.ExactCritic(d, P)
        with torch.no_grad():
            for parameter in critic.parameters():
                parameter.add_(.08*torch.randn_like(parameter))
        states = torch.randn(13, d+1)
        states[:, 0] = P["T"]*torch.rand(13)
        exact, reference = critic.jet(states), reference_jet(critic, states)
        errors = [float((a-b).abs().max().detach()) for a, b in zip(exact, reference)]
        assert max(errors)<1e-11, errors
        fast = critic.jet(states, trace=False)
        fast_errors = [float((a-b).abs().max().detach()) for a, b in zip(fast[:3], reference[:3])]
        assert max(fast_errors)<1e-11, fast_errors
        parameters = list(critic.parameters())
        eobjective = sum(x.square().sum() for x in exact)
        robjective = sum(x.square().sum() for x in reference)
        eg = torch.autograd.grad(eobjective, parameters)
        rg = torch.autograd.grad(robjective, parameters)
        gradient_error = max(float((a-b).abs().max()) for a, b in zip(eg, rg))
        assert gradient_error<2e-10, gradient_error

        # Probe awkward active sets independently of network initialization.
        t = P["T"]*torch.rand(2048, 1)
        p = (torch.randn(2048, d)*.9+1)/d
        action, work = h.greedy_newton(p, t, P, .25)
        old = reference_root(p, t, P, .25)
        root_error = float((action-old).abs().max())
        assert root_error<2e-12, root_error

        # Terminal lift is exact in value and spatial derivative for arbitrary
        # nonzero network weights, because the residual is multiplied by tau.
        terminal = states.clone()
        terminal[:, 0] = P["T"]
        v, _, dp, _ = critic.jet(terminal)
        y = terminal[:, 1:]
        mean = y.mean(1, keepdim=True)
        expected_v = mean-P["CHI"]*(y-mean).square().mean(1, keepdim=True)
        expected_p = 1/d-2*P["CHI"]*(y-mean)/d
        assert torch.allclose(v, expected_v, rtol=0, atol=2e-15)
        assert torch.allclose(dp, expected_p, rtol=0, atol=2e-15)

        batch = torch.randn(128, d+1)
        batch[:, 0] = P["T"]*torch.rand(128)
        B = h.coupling(d)
        optimizer = torch.optim.Adam(critic.parameters(), lr=.0015)
        times = []
        for _ in range(12):
            start = time.perf_counter()
            optimizer.zero_grad(set_to_none=True)
            residual, _ = h.exact_residual(critic, batch, B, .25)
            residual.square().mean().backward()
            optimizer.step()
            times.append(time.perf_counter()-start)
        rows.append(dict(dimension=d, jet_absolute_errors=errors,
                         deployment_first_jet_absolute_errors=fast_errors,
                         weight_gradient_absolute_error=gradient_error,
                         optimized_root_max_error_against_50_bisections=root_error,
                         root_work=work,
                         median_exact_training_batch_seconds=float(torch.tensor(times[2:]).median()),
                         trace_mode="exact architecture-specific analytic propagation",
                         payoff_evaluations=0))
    return rows


def check_binding():
    code = r'''
import json
import sys
import tempfile
import capital_adapter as c
import strong_hjb as h
p=json.loads(sys.argv[1])
b=c.bind_economy(p,.2,dict(means=[-1.,0.,1.],spreads=[0.,.5,1.]),"manufactured_binding")
r=b.audit_record(16)
assert r["terminal_identity_error"] == 0
assert b.support(10).shape == (9,10)
assert b.verifier.population(10).tolist() == b.support(10).tolist()
assert b.core.configure_primitives(p) == p
assert b.verifier.bind_primitives(p)[1] == b.primitives_sha256
before=dict(b.core.old.P)
bad=dict(p)
bad["T"]=1. if p["T"] == 2. else 2.
try:
    b.core.configure_primitives(bad)
except ValueError:
    pass
else:
    raise AssertionError("cross-economy primitive mutation was accepted")
assert b.core.old.P == before
assert b.assert_bound()
weights=b.core.training_weights(16)
reference=b.core.ReferencePolicy(10,p,16,weights)
original,_=b.core.occupation(reference,10,23,424242,16,p,b.population)
new,_=h.reference_occupation(10,23,424242,p,b.population,16,b.held_reference(16))
assert h.torch.equal(original,new), float((original-new).abs().max())
methods=["nbo","raw_costate","direct_policy","hjb_greedy","hjb_distilled"]
with tempfile.TemporaryDirectory(prefix="nbo-r16-exact-zero-check-") as directory:
    for method in methods:
        actor=b.core.AnalyticalSchedule(10,p)
        row=b.verifier.verify(actor,dimension=10,steps=64,paths=4,noise_seed=474747,
            event_alpha=.1,primitives=p,out=directory,record_id=method,
            metadata=dict(method_id=method,stream_seed=0,is_confirmation=False,
                noise_key="DEVELOPMENT-EXACT-ZERO-IDENTITY",epsilon=.2,
                analytic_schedule=True,primitives_sha256=b.primitives_sha256))
        assert row["method_id"] == method
        assert row["mean"] == row["lower"] == row["upper"] == 0.
print(json.dumps(dict(status="passed",horizon=p["T"],CHI=p["CHI"],aliases=len(r["module_aliases"]),defining_functions=len(r["defining_functions"]),matched_occupation_bitwise=True,exact_zero_method_identity_checks=len(methods))))
'''
    rows = []
    for horizon, chi in [(1., .03), (2., .1)]:
        params = dict(P, T=horizon, CHI=chi)
        run = subprocess.run([sys.executable, "-c", code, json.dumps(params)],
            cwd=Path(__file__).resolve().parent, capture_output=True, text=True)
        if run.returncode:
            raise AssertionError(run.stderr)
        rows.append(json.loads(run.stdout))
    return rows


def check_family_api():
    design = Path(__file__).resolve().parents[1]/"protocols/strong_hjb_design.json"
    config = json.loads(design.read_text())["implementation_configuration"]
    config.update(training_rows=64, selection_rows_per_group=32, audit_rows_per_group=32,
        occupation_steps=16, adam_updates=4, checkpoint_every=2, minimum_adam_updates=4,
        lbfgs_iterations=2, lbfgs_evaluations=4, distillation_adam_updates=4,
        distillation_lbfgs_iterations=2, probe_diagnostic_rows=4, probe_diagnostic_banks=4)
    with tempfile.TemporaryDirectory(prefix="nbo-r16-hjb-check-") as directory:
        greedy, actor, report = h.run_hjb_family(dimension=10, params=P, epsilon=.2,
            population=dict(means=[-.5, 0., .5], spreads=[0., .25, .5]), seed=900012,
            configuration=config, out=directory,
            reference_held_schedule=h.schedule((torch.arange(config["occupation_steps"])+.5)*P["T"]/config["occupation_steps"], P),
            source_metadata={"role": "manufactured API check; no economic confirmation"})
        assert len(report["candidates"]) == 4
        assert report["payoff_evaluations"] == 0
        assert all(row["failure"] is None for row in report["candidates"])
        states = h.broad_states(10, 19, 939393, P,
            dict(means=[-.5, 0., .5], spreads=[0., .25, .5]))
        for method, original in [("hjb_greedy", greedy), ("hjb_distilled", actor)]:
            loaded, _, state = h.load_candidate(Path(directory)/(method+".pt"))
            assert state["params"] == P
            assert torch.equal(loaded(states), original(states))
        return dict(status="passed", candidates=4, persisted_deployments=2,
                    payoff_evaluations=0, selection_uses_payoff=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = dict(status="passed", role="manufactured arithmetic, binding and API checks; not economic evidence",
                  arithmetic=check_arithmetic(), capital_binding=check_binding(), family_api=check_family_api())
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
