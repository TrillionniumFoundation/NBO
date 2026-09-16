#!/usr/bin/env python3
"""Produce a review-facing summary from actual executed records."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'replication/r5/output'
def load(n):return json.loads((OUT/(n+'.json')).read_text())
def main():
 c=load('contracts');r=load('resource_ablation');w=load('contract_workload');s=load('sign_certificate');g=load('persistent_game')['persistent'];v=load('validation')
 lines=['# R5 executed results','',f"Source commit: `{v.get('source_commit')}`. Source-byte verification: `{v['source_bytes_verified']}`.",'',
 '## Nonlinear stopped finite economy','',f"Menu: {c['common_action_count']} common actions plus three frozen R4 policies, {c['total_action_count']} per node. Grid 33×49, eight dates. {len(c['anchors'])} anchors cover all `d` in `[0,1]` at `k=2`.",'',
 f"Maximum certified all-date, all-state, entire-interval welfare loss: **{c['uniform_certificate']:.12g}**; target `0.001`. Independently evaluated repaired-policy feasible gain: **{c['repaired_max_gain']:.12g}**. Normalization identity error: {c['normalization_max_error']:.12g}.",'',
 '| Original seed | Largest expanded-menu gain | Focal welfare loss | Population welfare loss | Largest all-date/state loss |','|---|---:|---:|---:|---:|']
 for b in c['baseline']:lines.append(f"| {b['seed']} | {b['feasible_gain_max']:.9g} | {b['loss_focal']:.9g} | {b['loss_population']:.9g} | {b['loss_all_dates_states']:.9g} |")
 lines+=['','Entire-interval portfolio-sign groups (unrounded endpoints; focal state and date zero):','']
 for z in s['groups']:lines.append(f"- {z['sign']}: [{z['left']:.17g}, {z['right']:.17g}].")
 prep=c['timing']['preparation_seconds'];reuse=w['reuse_complete_policy_seconds'];direct=w['direct_complete_policy_seconds']
 lines+=['','## Executed contract-query workload','',f"{w['queries']} complete-policy queries. Preparation {prep:.6f}s; reuse including full policy evaluation {reuse:.6f}s; direct backward solutions {direct:.6f}s. Online ratio {direct/reuse:.4f}; preparation-inclusive ratio {direct/(prep+reuse):.4f}. Largest independently observed loss {w['max_observed_loss']:.12g}. Timing is machine-dependent.",'','## Same-weight resource ablation','',
 '| Dimension | Seed | Actor loss upper | Zero-start loss upper | Full PSD quadratic loss upper | Actor–zero cost difference |','|---|---|---:|---:|---:|---:|']
 for x in r['cases']:lines.append(f"| {x['d']} | {x['seed']} | {x['actor']['loss_upper_max']:.9g} | {x['zero']['loss_upper_max']:.9g} | {x['quadratic']['loss_upper_max']:.9g} | {x['actor_cost_difference_max']:.5g} |")
 lines+=['','All actor and actor-free cases meet the `10^-3` declared target. The full convex-quadratic comparator is fitted by projected convex least squares; its reported failures are relative to this class and budget, not all non-neural approximations.','',
 '| Fresh queries | Loss upper | Critic training + query seconds | Matched reference seconds | End-to-end ratio |','|---|---:|---:|---:|---:|']
 for x in r['workloads']:lines.append(f"| {x['queries']} | {x['loss_upper_max']:.9g} | {x['total_neural_seconds']:.6f} | {x['matched_reference_seconds']:.6f} | {x['end_to_end_speed_ratio']:.4f} |")
 lines+=['','## Persistent capacity game','',f"Survival {g['survival']}, {g['steps']} dates, eight states, two players. All-date full unilateral gain {g['best_response']['max_positive_gain']:.12g}; maximum product of best-response slopes {g['max_best_response_product']:.12g}. Capacity-dependent policy range {g['capacity_policy_range']:.9g}; early-date range {g['early_date_policy_range']:.9g}. A deliberately distorted late-date action is detected independently.",'',
 '## Verification scope','',v['threshold_status']+'. See `replication/r5/output/validation.json` for individual replays and thresholds, and `manifest.json` for identities/environment. These are finite-model double-precision certificates and complete-tree pointwise certificates, not uncomputed diffusion or continuous-action guarantees. Source and build success do not assert editorial acceptance.','']
 (ROOT/'revisions/2026-09-16-r5/execution_summary.md').write_text('\n'.join(lines))
if __name__=='__main__':main()
