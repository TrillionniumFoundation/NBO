"""Audit the complete saved R120 evidence; optionally replay statistics/reporting.

This standard-library program checks bytes, immutable Git identities, the full
record census and arithmetic among stored witnesses. It never calls a terminal
solver, acquires a label/sample, trains an actor, returns a new experimental
policy, or repeats a competitive timing. A successful audit is not a favorable
economic finding or an independent re-execution of the original economy.
"""
from __future__ import annotations
import argparse
from collections import Counter
import datetime as dt
from fractions import Fraction as Q
import hashlib
import gzip
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
import traceback

from evidence_common120 import (ACTORS,ARMS,REPORT_SPEC,REVISION,SERVICES,SOURCE,STATES,
    census,finite,git,iter_rows,materialize,path_in,read_json,record,repository,require,
    sha256,tree,write_json)

BETA=Q(15,16);EPS=Q(1,2**20);TAU=Q(1,256);WIDTH=Q(1,8192);R=Q(1,32)
THRESHOLDS=(Q(1,2**20),Q(1,2**18),Q(1,2**16),Q(1,2**14))
MEAN_RADIUS=33*TAU/128;EVENT_DELTA=Q(1,7680)

def exact(value):
    if isinstance(value,float):finite(value)
    require(not isinstance(value,bool),'Boolean is not a numerical enclosure')
    return Q(value)

def encoded(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {str(k):encoded(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encoded(v) for v in value]
    return value

def utc(value):
    return dt.datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()

def identity(row):
    return (row['index'],row['row'],row['arm'],row['service'])

def policy_key(row):
    return (tuple(float(x).hex() for x in row['state']),float(row['action']).hex(),float(row['alpha']).hex())

def key_id(key):
    return hashlib.sha256(json.dumps(key,separators=(',',':')).encode()).hexdigest()

def expected(n):
    return {(i,j,a,s) for i in range(2) for j in range(n) for a in ARMS for s in SERVICES}

def count_rows(rows,n):
    keys=[identity(r) for r in rows]
    require(len(rows)==len(set(keys))==len(expected(n)) and set(keys)==expected(n),
            'The full fixed Cartesian record census is required')
    return dict(zip(keys,rows))

def success(root,name='EXECUTION120.json'):
    data=read_json(root/name)
    require(data.get('status') in ('executed','passed') and data.get('exit_code')==0,
            'Selected completed execution is missing or failed: '+str(root/name))
    return data

def nonnegative_counts(mapping):
    require(isinstance(mapping,dict),'An operation-counter mapping is required')
    require(all(isinstance(v,int) and not isinstance(v,bool) and v>=0 for v in mapping.values()),
            'Operation counters must be actual nonnegative integer counts')

class EvidenceAudit:
    def __init__(self,revision,evidence,manifest,out,repo):
        self.revision=revision;self.evidence=evidence;self.manifest=manifest;self.out=out;self.repo=repo
        self.prefix=revision.relative_to(repo).as_posix()
        self.trees={};self.counts=Counter();self.details={}
        self.paths={k:path_in(evidence,v) for k,v in manifest['layout'].items()}

    def committed(self,path,commit,relative):
        if commit not in self.trees:self.trees[commit]=tree(self.repo,commit,self.prefix)
        got=record(path,path.parent);native=self.prefix+'/'+relative
        require(self.trees[commit].get(native)==got['git_blob'],'Git source/artifact blob differs: '+native)
        self.counts['committed_file_identities']+=1
        return got

    def artifact(self,kind,filename,commit=None,expected_kind=None):
        root=self.paths[kind];path=root/filename;data=read_json(path)
        require(data['source_commit']==SOURCE and data['kind']==expected_kind,'Wrong episode kind/source: '+filename)
        seen=set()
        for item in data['files']:
            require(item['path'] not in seen,'Duplicate artifact-manifest member')
            seen.add(item['path']);p=path_in(root,item['path'])
            require(record(p,root)==item,'Artifact-manifest byte identity differs: '+str(p))
            if commit:self.committed(p,commit,p.relative_to(self.evidence).as_posix())
        actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        require(actual==seen|{filename},'Artifact directory has unlisted or missing evidence: '+str(root))
        if commit:self.committed(path,commit,path.relative_to(self.evidence).as_posix())
        self.counts['artifact_manifest_members']+=len(seen)
        return data

    def sources_and_custody(self):
        m=self.manifest
        require(m['commits']=={'source':SOURCE,'actors':ACTORS,'states':STATES,'reporting_spec':REPORT_SPEC},
                'Scientific episode identities cannot be substituted')
        for previous,later in ((SOURCE,ACTORS),(ACTORS,STATES),(STATES,REPORT_SPEC)):
            require(previous!=later,'Distinct source/actor/sample/spec barriers are required')
            git(self.repo,'merge-base','--is-ancestor',previous,later)
            parents=git(self.repo,'show','-s','--format=%P',later).decode().strip().split()
            require(parents==[previous],'The recorded custody commits must have their actual direct parent')
        freeze=read_json(self.revision/'SOURCE_FREEZE120.json')
        self.committed(self.revision/'SOURCE_FREEZE120.json',SOURCE,'SOURCE_FREEZE120.json')
        require(freeze['total_files']==len(freeze['scientific_files'])==157
                and freeze['total_bytes']==1206453,'The declared scientific freeze census differs')
        total=0
        for item in freeze['files']:
            p=path_in(self.revision,item['path']);got=record(p,self.revision)
            require(got==item and got['sha256']==freeze['scientific_files'][item['path']],
                    'Frozen science file changed: '+item['path'])
            self.committed(p,SOURCE,item['path']);total+=got['bytes']
        require(total==1206453,'Frozen scientific byte census differs')
        self.counts['frozen_scientific_inputs']=157
        self.committed(self.revision/'REPORTING_SPEC120.md',REPORT_SPEC,'REPORTING_SPEC120.md')
        acquisitions=self.artifact('acquisition','ACQUISITION_MANIFEST120.json',ACTORS,'acquire')
        self.artifact('states','STATE_MANIFEST120.json',STATES,'sample')
        self.artifact('primary','RESULT_MANIFEST120.json',expected_kind='primary')
        models={r['path'] for r in acquisitions['files'] if Path(r['path']).name=='model.json'}
        require(models=={f'models/{i}-{a}/model.json' for i in range(2) for a in ARMS},'Exactly sixteen frozen models are required')
        self.counts['frozen_models']=len(models)
        executions={k:success(self.paths[k]) for k in ('acquisition','states','primary','independent','statistics')}
        for kind,data in executions.items():
            require(data['source']['source_commit']==SOURCE,'Execution used a different science source: '+kind)
            require(data['started_unix']<=data['ended_unix'],'Invalid execution clock order')
        publications={k:read_json(path_in(self.revision,v)) for k,v in m['publication_receipts'].items()}
        pubF,pubM,pubD,pubR=(publications[k] for k in ('source','actors','states','reporting_spec'))
        require(pubF['source_commit']==SOURCE and pubF['remote_update_success'] is True,'Source publication receipt differs')
        require(pubM['actor_commit']==ACTORS and pubM['source_commit']==SOURCE and pubM['github_plugin_update_ref_success'] is True,
                'Actor publication receipt differs')
        require(pubD['state_commit']==STATES and pubD['actor_commit']==ACTORS and pubD['source_commit']==SOURCE
                and pubD['github_plugin_update_ref_success'] is True,'State publication receipt differs')
        require(pubM['acquisition_manifest_sha256']==sha256(self.paths['acquisition']/'ACQUISITION_MANIFEST120.json'),
                'Published actor-manifest bytes differ')
        require(pubD['state_manifest_sha256']==sha256(self.paths['states']/'STATE_MANIFEST120.json'),
                'Published state-manifest bytes differ')
        require(utc(pubF['observed_utc'])<=executions['acquisition']['started_unix'],
                'Label/actor acquisition must follow observed source publication')
        require(executions['acquisition']['ended_unix']<=utc(pubM['observed_utc'])<=executions['states']['started_unix'],
                'State draw must follow the completed acquisition and observed actor publication')
        require(executions['states']['ended_unix']<=utc(pubD['observed_utc'])<=executions['primary']['started_unix'],
                'Primary decisions must follow observed sample publication')
        require(executions['primary']['ended_unix']<=executions['independent']['started_unix']
                and executions['independent']['ended_unix']<=executions['statistics']['started_unix'],
                'Independent solving and statistics must follow the completed prior stage')
        launches={}
        for kind,relative in m['external_launch_receipts'].items():
            p=path_in(self.evidence,relative);launch=read_json(p)
            require(launch.get('status')=='executed' and launch.get('exit_code')==0,'External launch did not finish successfully: '+kind)
            log=p.parent/'stdout.log'
            require(sha256(log)==launch['stdout_sha256'] and log.stat().st_size==launch['stdout_bytes'],
                    'External launch log differs: '+kind)
            require(utc(launch['started_utc'])<=utc(launch['ended_utc']),'External launch clock order differs')
            if kind in executions:
                run=executions[kind]
                require(utc(launch['started_utc'])<=run['started_unix']<=run['ended_unix']<=utc(launch['ended_utc']),
                        'Inner execution lies outside its actual external launch: '+kind)
            launches[kind]=launch
        require(set(launches)>={'acquisition','states','primary','independent','statistics'},'Complete external stage launch receipts are required')
        require(launches['primary']['head_at_launch']==REPORT_SPEC,'Primary launch did not bind the reporting/spec commit')
        require(pubR['reporting_spec_commit']==REPORT_SPEC and pubR['parent']==STATES
                and pubR['github_plugin_create_commit_response']['sha']==REPORT_SPEC
                and pubR['github_plugin_update_ref_response']['success'] is True,'Reporting-spec transport record differs')
        require(pubR['primary_launch_head']==REPORT_SPEC and pubR['primary_launch_started_utc']==launches['primary']['started_utc'],
                'Reporting-spec receipt and actual launch disagree')
        require(pubR['transport_order']==['GitHub create_tree','GitHub create_commit','GitHub expected-SHA update_ref success',
                'metadata-only fetch','local mixed reset preserving science','primary launch'],
                'Recorded reporting publication/launch operation order differs')
        require(pubR['reporting_spec_sha256']==sha256(self.revision/'REPORTING_SPEC120.md'),'Reporting specification bytes changed')
        self.details['custody']={'F':SOURCE,'M':ACTORS,'D':STATES,'reporting_spec':REPORT_SPEC,
            'distinct_direct_ancestor_order_verified':True,'source_actor_state_remote_observations_checked':True,
            'reporting_transport_receipt_recorded_utc':pubR['recorded_utc'],
            'reporting_receipt_was_written_after_primary_launch':utc(pubR['recorded_utc'])>utc(launches['primary']['started_utc']),
            'reporting_prelaunch_evidence_scope':'The retained actual operation sequence reports successful remote publication before launch; the independent launch HEAD is the same commit. The later receipt creation time and Git committer date are not represented as observed push timestamps.',
            'external_launches_verified':len(launches)}
        self.executions=executions

    def sampled_states(self):
        data=read_json(self.paths['states']/'states120.json');raw=(self.paths['states']/'entropy120.bin').read_bytes()
        require(len(raw)==640 and hashlib.sha256(raw).hexdigest()==data['entropy_sha256'],'Original entropy bytes differ')
        require(data['source_commit']==SOURCE and data['actor_commit']==ACTORS and data['rows']==64
                and data['dimension']==2 and len(data['states'])==64,'Sample identity or full dimensions differ')
        states={}
        for index,item in enumerate(data['states']):
            integers=[int.from_bytes(raw[(2*index+j)*5:(2*index+j+1)*5],'big') for j in range(2)]
            values=[v/2**40 for v in integers]
            require(item['row']==index and item['coordinate_numerators']==integers and item['denominator']==2**40
                    and item['state']==values and item['state_hex']==[v.hex() for v in values],
                    'A sample row differs from its exact original five-byte coordinates')
            states[index]=values
        self.states=states;self.counts['sample_rows']=64;self.counts['entropy_bytes']=640
        self.details['population']={'independent_units':64,'distinct_realized_states':len({tuple(v) for v in states.values()}),
            'duplicate_draws_retained':True,'entropy_law_is_a_stated_assumption_not_proved_by_byte_inspection':True,
            'timing_rows_add_no_independent_observations':True}

    def catalogue(self,root,n,repeat):
        rows=list(iter_rows(root/'records120.jsonl'));indexed=count_rows(rows,n)
        run=success(root);require(run['source']['source_commit']==SOURCE,'Wrong catalogue source')
        require(run['mode']==('primary' if repeat is None else 'timing-one'),'Wrong catalogue execution mode')
        catalogue=read_json(root/'CATALOGUE120.json')
        require(catalogue['status']=='executed' and catalogue['decisions']==n*64
                and catalogue['scientific_batch_count']==64 and catalogue['singleton_decision_calls']==n*64,
                'Catalogue summary census differs')
        source=catalogue['source']
        require(source['source_commit']==SOURCE and source['actor_commit']==ACTORS and source['state_commit']==STATES,
                'Catalogue F/M/D context differs')
        require(source['acquisition_manifest_sha256']==sha256(self.paths['acquisition']/'ACQUISITION_MANIFEST120.json')
                and source['state_manifest_sha256']==sha256(self.paths['states']/'STATE_MANIFEST120.json'),
                'Catalogue input-manifest identities differ')
        for row in rows:
            require(row['source_commit']==SOURCE and row['actor_commit']==ACTORS and row['state_commit']==STATES,'Row F/M/D identity differs')
            require(row['repeat']==repeat and row['population_observation'] is (repeat is None)
                    and row['original_initial_state_batch_size']==1,'Timing/population or singleton status differs')
            require(row['risk_index']==row['index'] and exact(row['alpha'])==(Q(1,2) if row['index']==0 else Q(3,4)),
                    'Original risk parameter changed')
            require(row['state']==self.states[row['row']] and row['state_hex']==[float(v).hex() for v in row['state']],
                    'Decision uses a different state')
            action=exact(row['action']);cap=Q(1,8)+sum(map(exact,row['state']))/16
            require(0<=action<=cap and row['action_hex']==float(action).hex(),'Original action feasibility/serialization differs')
            require(row['qualified'] is True and 0<=exact(row['loss'])<=TAU and 0<=exact(row['width'])<=WIDTH,
                    'Declared complete original service qualification failed')
            lo,hi=exact(row['complete_policy_lower']),exact(row['complete_policy_upper'])
            require(lo<=hi and exact(row['original_optimum_lower'])<=hi,'Malformed production policy/optimum interval')
            gain=exact(row['certified_gain_lower'])
            require(0<=gain<=exact(row['baseline_loss'])<=TAU,'Production gain is outside the original safe ceiling')
            require(isinstance(row['accepted_steps'],int) and row['accepted_steps']>=0
                    and row['safe_changes']==row['accepted_steps'],'Accepted-step accounting differs')
            if action==exact(row['completed_incumbent_action']):
                require(gain==0 and row['accepted_steps']==0,'Same incumbent action has a false positive gain')
            else:require(gain>0 and row['accepted_steps']>0,'Changed action lacks a strict recorded gain')
            require(finite(row['seconds'])>=0 and finite(row['cold_model_load_seconds'])>=0,'Negative actual service clock')
            nonnegative_counts(row['querycounts'])
            model=self.paths['acquisition']/f"models/{row['index']}-{row['arm']}/model.json"
            require(row['model_sha256']==sha256(model),'Decision used a different actor')
        for row in rows:
            base=indexed[(row['index'],row['row'],row['arm'],'completed')]
            require(exact(row['completed_incumbent_action'])==exact(base['action']),
                    'Service does not start from the same completed incumbent')
        expected_order=[]
        for risk in range(2):
            for arm in ARMS:
                order=list(SERVICES)
                if repeat is not None:
                    shift=(repeat+risk+ARMS.index(arm))%4;order=order[shift:]+order[:shift]
                expected_order.extend((risk,arm,service) for service in order)
        summaries=catalogue['records']
        require([(r['index'],r['arm'],r['service']) for r in summaries]==expected_order,
                'Declared complete service order or timing rotation differs')
        all_trials=[]
        for summary in summaries:
            risk,arm,service=summary['index'],summary['arm'],summary['service']
            batch=f'{risk}-{arm}-{service}';path=root/'batches'/f'{batch}.json'
            require(summary['batch_id']==batch and summary['batch_sha256']==sha256(path),'Batch receipt identity differs')
            data=read_json(path);group=[indexed[(risk,j,arm,service)] for j in range(n)]
            require(data['rows']==group and data['source']==source and data['repeat']==repeat,'Batch rows/source differ')
            counts=Counter()
            for row in group:counts.update(row['querycounts'])
            require(dict(counts)==data['counts']==summary['querycounts'],'Cohort counters omit or duplicate work')
            require(data['seconds']==sum(r['seconds'] for r in group)==summary['seconds'],'Singleton clock sum differs')
            require(data['cold_model_load_seconds']==summary['cold_model_load_seconds']
                    and data['cohort_end_to_end_seconds']==summary['cohort_end_to_end_seconds'],
                    'Cohort and load clocks differ')
            require(data['cohort_end_to_end_seconds']>=data['seconds'] and data['cold_model_load_seconds']>=0,
                    'A complete cohort clock is below its included service work')
            acq=read_json(self.paths['acquisition']/f'models/{risk}-{arm}/acquisition.json')
            require(data['standalone_acquisition_charge_seconds']==acq['actual_standalone_acquisition_charge_seconds']
                    and all(r['standalone_acquisition_charge_seconds']==data['standalone_acquisition_charge_seconds'] for r in group),
                    'Full standalone acquisition charge differs')
            require(summary['decisions']==n and summary['accepted_steps']==sum(r['accepted_steps'] for r in group)
                    and summary['changed_actions']==sum(r['action']!=r['completed_incumbent_action'] for r in group),
                    'Cohort accepted/changed-action summary differs')
            events=root/'events'/f'{batch}.jsonl.gz'
            require(sha256(events)==data['event_trace_sha256'],'Scientific event trace bytes differ')
            count=0;completed_rows=set()
            for event in iter_rows(events):
                require(event['sequence']==count,'Missing/reordered event record')
                if count==0:
                    require(event['event']=='cohort-start' and event['source']==source
                            and event['model_sha256']==group[0]['model_sha256'],'Event cohort start differs')
                elif event.get('event')=='service-complete':
                    j=event['initial_state_row'];require(0<=j<n and j not in completed_rows,'Duplicate service-complete trace')
                    completed_rows.add(j)
                require(event.get('event') not in ('cohort-failed','service-failed'),'A selected successful cohort retains a failed service')
                count+=1
            require(count==data['event_records'] and completed_rows==set(range(n)),'Full service event trace is incomplete')
            self.counts['event_records']+=count;self.counts['event_traces']+=1
            all_trials.extend(data['trials'])
        trial_path=root/'trials120.jsonl'
        require((list(iter_rows(trial_path)) if trial_path.exists() else [])==all_trials,'Rejected/accepted candidate trace census differs')
        self.counts['candidate_trial_records']+=len(all_trials)
        return indexed

    def primary_and_timing(self):
        primary=self.catalogue(self.paths['primary'],64,None);self.primary=primary
        self.counts['primary_decisions']=len(primary)
        timing=read_json(self.paths['primary']/'TIMING120.json')
        require(timing['status']=='executed' and timing['descriptive_only'] is True
                and timing['additional_new_iid_states']==0 and len(timing['repeats'])==3,'Timing protocol summary differs')
        mismatches=[];last_end=None
        for repeat,launcher in enumerate(timing['repeats']):
            root=self.paths['primary']/'timing'/f'attempt-{repeat:02d}'
            saved=read_json(root.parent/f'launcher-{repeat:02d}.json')
            require(saved==launcher and launcher['repeat']==repeat and launcher['exit_code']==0
                    and launcher['fresh_process'] is True and launcher['sequential_with_no_campaign_overlap'] is True,
                    'A declared timing process failed, was replaced or lacks its actual launcher')
            require(sha256(root.parent/f'launcher-{repeat:02d}.log')==launcher['log_sha256'],'Timing launch log differs')
            require(launcher['started_unix']<=launcher['ended_unix'] and (last_end is None or last_end<=launcher['started_unix']),
                    'Timing processes overlap or have invalid clocks')
            last_end=launcher['ended_unix']
            old=self.paths.get('timing_check');self.paths['timing_check']=root
            self.artifact('timing_check','RESULT_MANIFEST120.json',expected_kind='timing-one')
            if old is None:self.paths.pop('timing_check')
            else:self.paths['timing_check']=old
            run=self.catalogue(root,32,repeat)
            for key,row in run.items():
                base=primary[key]
                require(row['state_hex']==base['state_hex'],'Timing state differs from its primary match')
                if row['action_hex']!=base['action_hex']:
                    mismatches.append({'repeat':repeat,'identity':list(key),'primary_action_hex':base['action_hex'],
                                       'timing_action_hex':row['action_hex']})
            self.counts['timing_decisions']+=len(run)
        require(self.counts['timing_decisions']==6144,'All timing action comparisons are required')
        write_json(self.out/'TIMING_ACTION_MISMATCHES120.json',mismatches)
        self.details['timing']={'processes':3,'all_actions_compared':6144,'matching_actions':6144-len(mismatches),
            'mismatches':len(mismatches),'all_mismatches_retained':True,
            'scope':'A mismatch restricts use of the primary policy value for that clock. It is retained, never replaced by another timing, and is not an omitted experiment.'}

    def original_reports(self):
        index=read_json(self.revision/'provenance/reports120/REPORT_SOURCE_INDEX120.json')
        path=self.revision/'provenance/reports120/REPORT_REGISTRY_ORIGINAL119.json'
        registry=read_json(path);by_id={r['report_id']:r for r in registry}
        require(len(registry)==len(by_id)==len(index['files'])==index['distinct_report_documents']==35,
                'All thirty-five exact original report bodies are required')
        inherited='revisions/2026-10-18-r119/provenance/REPORT_REGISTRY.json'
        oldtree=tree(self.repo,'82618f037540233dda7d1ba8bfd3ddfdc88afbf9',inherited)
        require(oldtree.get(inherited)==record(path,path.parent)['git_blob'],
                'Original report registry differs from the immutable R119 publication')
        seen=set();total=0
        for item in index['files']:
            rid=item['report_id'];require(rid in by_id and rid not in seen,'Missing or duplicate original report')
            original=by_id[rid];got=record(path_in(self.revision,item['path']),self.revision)
            require(got['bytes']==item['bytes']==original['bytes']
                    and got['sha256']==item['sha256']==original['sha256']
                    and got['git_blob']==item['git_blob_sha1']==original['git_blob_sha1'],
                    'Original report text was altered: '+rid)
            require(item['source_review_commit']==original['review_commit']
                    and item['source_review_branch']==original['review_branch']
                    and item['source_path_in_review_commit']==original['source_path'],
                    'Report source identity differs: '+rid)
            seen.add(rid);total+=got['bytes']
        require(seen==set(by_id),'Report document census differs')
        self.counts['exact_original_report_documents']=35
        self.details['original_reports']={'documents':35,'bytes':total,
            'immutable_R119_registry_blob_verified':True,'scope':'Exact advisory originals and source identities; no new external review or assertion that every scientific request is closed.'}
        self.original_report_texts={r['report_id']:path_in(self.revision,r['path']).read_text() for r in index['files']}

    def author_routes(self):
        transport=read_json(self.revision/'provenance/reports120/inherited_maps/INDEX120.json')
        require(transport['original_commit']=='82618f037540233dda7d1ba8bfd3ddfdc88afbf9' and len(transport['files'])==2,
                'Inherited map custody source differs')
        maps={};map_hashes={}
        for item in transport['files']:
            p=path_in(self.revision,item['path']);got=record(p,self.revision)
            require(all(got[k]==item[k] for k in got),'Compressed inherited map changed')
            raw=gzip.decompress(p.read_bytes());digest=hashlib.sha256(raw).hexdigest()
            blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            require(len(raw)==item['original_bytes'] and digest==item['original_sha256']
                    and blob==item['original_git_blob'],'Lossless original author-map payload differs')
            inherited=tree(self.repo,transport['original_commit'],item['original_path'])
            require(inherited.get(item['original_path'])==blob,'Inherited author map is not the published R119 blob')
            maps[item['original_path']]=json.loads(raw);map_hashes[item['original_path']]=digest
        history=read_json(self.revision/'provenance/HISTORICAL_ROUTE_BINDINGS120.json')
        require(len(history['rows'])==1049,'All inherited major, minor, item and parent routes are required')
        seen=set();source_bindings=set()
        for row in history['rows']:
            require(row['key'] not in seen and row['r120_new_closure_asserted'] is False,
                    'Duplicate inherited route or unsupported new blanket closure')
            seen.add(row['key']);original=maps[row['r119_map']][row['r119_array']][row['r119_row_index']]
            require(map_hashes[row['r119_map']]==row['r119_map_sha256'] and original['key']==row['key']
                    and hashlib.sha256(original['exact_text'].encode()).hexdigest()==row['original_comment_hash']
                    and original['exact_text'] in self.original_report_texts[row['report_id']],
                    'An inherited route no longer identifies its exact original advisory request')
            # The inherited source identity is immutable; copies in the current
            # manuscript can subsequently receive explicit author corrections.
            for source in row['r119_current_source_bindings']:
                identity_key=(row['r119_source_base'],source['path'],source['git_blob_sha1'])
                if identity_key not in source_bindings:
                    relative=row['r119_source_base']+'/'+source['path']
                    inherited=tree(self.repo,transport['original_commit'],relative)
                    require(inherited.get(relative)==source['git_blob_sha1'],'An inherited proof/action source identity differs')
                    source_bindings.add(identity_key)
        requirements=read_json(self.revision/'provenance/R97_REQUIREMENTS120.json')
        require(len(requirements['items'])==30,'All thirty current R97 point responses are required')
        current_sources={};ids=set()
        for item in requirements['items']:
            ids.add(item['comment_id']);require(item['closed'] is False,'A broad controlling request is incorrectly blanket-closed')
            require(hashlib.sha256(item['exact_text'].encode()).hexdigest()==item['comment_sha256']
                    and any(item['exact_text'] in body for body in self.original_report_texts.values()),
                    'Current R97 exact quoted request differs')
            for route in item['r120_current_source_routes']:
                p=path_in(self.revision,route['path']);got=record(p,self.revision)
                require(got['sha256']==route['sha256'] and got['bytes']==route['bytes'],
                        'Refresh final current author-route source bindings: '+route['path'])
                for label in route.get('labels',[]):require('\\label{'+label+'}' in p.read_text(),'Current proof/action label is absent')
                current_sources[route['path']]=got
        body=(self.revision/'new120/response120_body.tex').read_text()
        labels=re.findall(r'\\label\{response120:([^}]+)\}',body)
        require(len(labels)==30 and set(labels)==ids,'Typeset controlling point-response census differs')
        self.counts.update({'inherited_author_response_routes':1049,'current_R97_point_responses':30,
                            'immutable_inherited_route_sources':len(source_bindings),'current_author_route_sources':len(current_sources)})
        self.details['author_routes']={'inherited_routes':1049,'current_R97_responses':30,
            'scope':'Exact original request and immutable inherited response/proof routes are verified. Parent sections overlap their retained item routes; these counts are neither independent scientific issues nor blanket closures.'}

    def independent_records(self):
        root=self.paths['independent'];run=self.executions['independent']
        link=read_json(root/'PRIMARY_INPUT120.json');primary_path=self.paths['primary']/'records120.jsonl'
        require(link['sha256']==sha256(primary_path) and link['bytes']==primary_path.stat().st_size,
                'Independent calculation used a different primary input')
        unique={policy_key(row) for row in self.primary.values()};ordered=sorted(unique)
        rows=list(iter_rows(root/'policies120.jsonl'));policies={policy_key(row):row for row in rows}
        require(len(rows)==len(policies)==len(unique) and set(policies)==unique
                and [policy_key(row) for row in rows]==ordered,
                'Every unique returned action must have exactly its fixed independent calculation')
        design=read_json(root/'INDEPENDENT_DESIGN120.json')
        require(design['unique_actions']==len(unique) and design['primary_rows']==4096
                and design['bins']==64 and design['terminal_steps']==32
                and design['expected_terminal_contexts']==129*len(unique)
                and design['independent_original_optimum_lower'] is True
                and design['population_gain_bounds_are_row_local'] is True,
                'Fixed independent design or all-action validation scope differs')
        primitive=design['primitives']
        require(primitive['path']=='frozen108/code/independent94.py'
                and primitive['sha256']==sha256(self.revision/primitive['path'])
                and primitive['sha256']=='a1a0e4ce5563d1105c3cea9eaad6678c609229446ba6794f7b8a7c03df01ebad',
                'Independent implementation source differs')
        trace=iter(iter_rows(root/'terminal_witnesses120.jsonl.gz'));sequence=0
        def tail(values,alpha):
            n=len(values)*(1-alpha);require(n.denominator==1 and n>0,'Invalid stored equal-mass tail count')
            return sum(sorted(values,reverse=True)[:int(n)])/n
        for k in ordered:
            policy=policies[k];kid=key_id(k);alpha=exact(policy['alpha']);x=tuple(map(exact,policy['state']));a=exact(policy['action'])
            require(policy['key_id']==kid and policy['state_hex']==list(k[0]) and policy['action_hex']==k[1]
                    and policy['bins']==64 and policy['terminal_steps']==32 and policy['terminal_contexts']==129,
                    'Independent policy identity or fixed resolution differs')
            mids=[];ends=[]
            for node in range(129):
                try:w=next(trace)
                except StopIteration:raise AssertionError('Independent terminal witness trace ended early')
                z=-R+Q(node,128)*2*R;mid=node%2==1
                require(w['sequence']==sequence and w['key_id']==kid and w['node']==node
                        and exact(w['z'])==z and w['midpoint'] is mid and w['terminal_steps']==32,
                        'A fixed independent terminal node is absent, reordered or substituted')
                y=tuple(map(exact,w['state']));v=exact(w['action'])
                expected_y=tuple(Q(1,16)+x[j]/2+x[(j+1)%2]/8+x[j]*(1-x[(j+1)%2])/16
                        +(Q(1,2) if j==0 else Q(1,4))*a+(z if j==0 else -z) for j in range(2))
                cap=Q(1,8)+sum(y)/16;lo,up=exact(w['lower']),exact(w['upper'])
                require(y==expected_y and all(Q(1,32)<=value<=Q(27,32) for value in y)
                        and 0<=v<=cap and 0<=up-lo<=EPS,'Stored terminal domain, feasibility or accuracy differs')
                left,right=exact(w['tail_left']),exact(w['tail_right'])
                require(-R<=left<=right<=R and right-left==2*R*alpha
                        and exact(w['risk_primal'])==exact(w['risk_dual'])
                        and len(w['polynomial'])==3 and exact(w['polynomial'][2])==5,
                        'Stored original-risk mass or primal-dual arithmetic differs')
                if mid:
                    gradient=list(map(exact,w['state_gradient']));slope=list(map(exact,w['support_slope']))
                    pa=exact(w['action_gradient']);lam=exact(w['multiplier_upper']);nu=exact(w['multiplier_lower'])
                    residual=pa+lam-nu;anchor=up+lam*(v-cap)-nu*v-residual**2/4
                    require(len(gradient)==len(slope)==2 and lam>=0 and nu>=0
                            and lam==(max(Q(0),-pa) if v==cap else 0)
                            and nu==(max(Q(0),pa) if v==0 else 0)
                            and exact(w['stationarity_residual'])==residual
                            and exact(w['support_anchor'])==anchor<=up
                            and slope==[p-lam/16 for p in gradient],
                            'Stored Lagrange support is not the actual affine minorant anchor')
                    mids.append({'lower':lo,'anchor':anchor,'slope':slope})
                else:ends.append(up)
                sequence+=1
            require(len(mids)==64 and len(ends)==65,'Whole-support independent mesh is incomplete')
            qlo,qup=exact(policy['q_lower']),exact(policy['q_upper'])
            # Reaggregation is conditional on the saved independent terminal
            # values and gradients. This does not execute their economic solver
            # or provide a second independent proof of each primitive endpoint.
            stage=qlo-BETA*tail([w['lower'] for w in mids],alpha)
            endpoint_atoms=ends[:-1]+ends[1:]
            require(qup==stage+BETA*tail(endpoint_atoms,alpha) and qlo<=qup,
                    'Saved full-support policy aggregation differs or endpoint multiplicity was lost')
            require(exact(policy['j_lower'])==qlo and exact(policy['j_upper'])==qup+BETA*EPS
                    and exact(policy['future_controller_allowance_added_exactly_once'])==BETA*EPS,
                    'The original deployed-future allowance was omitted or counted twice')
            n=int(64*(1-alpha));selected=sorted(range(64),key=lambda j:(-mids[j]['anchor'],j))[:n]
            anchor=stage+BETA*sum(mids[j]['anchor'] for j in selected)/n
            grad=2*a+16*a**3+BETA*sum(mids[j]['slope'][0]/2+mids[j]['slope'][1]/4 for j in selected)/n
            cap=Q(1,8)+sum(x)/16;delta=max(-a,min(cap-a,-grad/2));optlo=anchor+grad*delta+delta**2
            require(policy['risk_bin_indices']==selected and exact(policy['risk_bin_mass'])==Q(1,n)
                    and exact(policy['all_action_anchor'])==anchor and exact(policy['all_action_gradient'])==grad
                    and exact(policy['all_action_minimizer'])==a+delta
                    and exact(policy['optimum_lower'])==optlo<=qup,
                    'Saved original all-action lower witness reaggregation differs')
            require(finite(policy['seconds'])>=0,'Independent per-key execution cost is missing')
        try:next(trace)
        except StopIteration:pass
        else:raise AssertionError('Unlisted additional independent terminal witness')
        require(sequence==129*len(unique),'Independent terminal context census differs')
        progress=list(iter_rows(root/'PROGRESS120.jsonl'))
        require(len(progress)==2*len(unique),'Independent progress/failure record census differs')
        for j,k in enumerate(ordered):
            for offset,event in ((0,'action-start'),(1,'action-complete')):
                w=progress[2*j+offset]
                require(w['event']==event and w['index']==j and w['key_id']==key_id(k),'Independent key progress differs')
        state_bounds={}
        for k,p in policies.items():
            sk=(k[0],k[2]);bounds=(exact(p['optimum_lower']),exact(p['q_upper']))
            old=state_bounds.get(sk)
            state_bounds[sk]=bounds if old is None else (max(old[0],bounds[0]),min(old[1],bounds[1]))
        optima=list(iter_rows(root/'original_optima120.jsonl'));seen=set()
        for item in optima:
            sk=(tuple(item['state_hex']),item['alpha_hex']);require(sk not in seen and sk in state_bounds,'Duplicate/unlisted original optimum')
            require((exact(item['lower']),exact(item['upper']))==state_bounds[sk]
                    and exact(item['lower'])<=exact(item['upper']),'Shared original all-action bounds differ')
            seen.add(sk)
        require(seen==set(state_bounds),'Missing state/risk original optimum witness')
        comparisons=list(iter_rows(root/'comparisons120.jsonl'));indexed=count_rows(comparisons,64)
        containment=Counter()
        for identity_key,row in self.primary.items():
            got=indexed[identity_key];k=policy_key(row);p=policies[k]
            base=self.primary[(row['index'],row['row'],row['arm'],'completed')];inc_k=policy_key(base);inc=policies[inc_k]
            jl,ju=exact(p['j_lower']),exact(p['j_upper']);ol,ou=state_bounds[(k[0],k[2])]
            pl,pu=exact(row['complete_policy_lower']),exact(row['complete_policy_upper'])
            require(max(pl,jl)<=min(pu,ju) and exact(row['original_optimum_lower'])<=ou,
                    'Production and independent original-policy/optimum intervals are incompatible')
            relation=('equal' if (pl,pu)==(jl,ju) else 'production_contains_independent' if pl<=jl<=ju<=pu
                      else 'independent_contains_production' if jl<=pl<=pu<=ju else 'partial_overlap')
            containment[relation]+=1
            gl,gu=(Q(0),Q(0)) if k==inc_k else (max(Q(0),exact(inc['j_lower'])-ju),min(TAU,exact(inc['j_upper'])-jl))
            rl,ru=max(Q(0),jl-ou),ju-ol;cap=Q(1,8)+sum(map(exact,row['state']))/16;cert=exact(row['certified_gain_lower'])
            require(0<=gl<=gu<=TAU and 0<=cert<=gu and 0<=rl<=ru,'Original gain/regret interval differs')
            wanted={'index':row['index'],'row':row['row'],'arm':row['arm'],'service':row['service'],
                'key_id':key_id(k),'incumbent_key_id':key_id(inc_k),'state_hex':row['state_hex'],'action_hex':row['action_hex'],
                'j_lower':jl,'j_upper':ju,'original_optimum_lower':ol,'original_optimum_upper':ou,
                'original_regret_lower':rl,'original_regret_upper':ru,'squared_original_action_error_upper':min(cap**2,ru),
                'gain_lower':gl,'gain_upper':gu,'certified_gain_lower':cert,'same_action':k==inc_k,
                'compatibility_is_not_an_exact_value_equality':True,'gain_interval_uses_row_local_policy_values_only':True}
            require(got==encoded(wanted),'Full independent comparison reaggregation differs: '+str(identity_key))
        require(run['primary_observations']==4096 and run['unique_policy_keys']==len(unique)
                and run['counts']['terminal_contexts']==sequence
                and run['counts']['unique_original_policy_evaluations']==len(unique)
                and run['counts']['independent_policy_comparisons']==4096
                and run['independent_global_original_optimum_and_regret_bounds'] is True,
                'Independent executed receipt census differs')
        self.comparisons=indexed;self.policies=policies
        self.counts.update({'independent_policy_keys':len(unique),'independent_terminal_nodes':sequence,
                            'independent_comparisons':4096,'independent_original_state_optima':len(state_bounds)})
        self.details['independent']={'all_unique_keys':len(unique),'terminal_nodes':sequence,
            'original_state_risk_optimum_intervals':len(state_bounds),'comparison_containment':dict(containment),
            'scope':'Complete saved-independent-record census, byte custody and exact algebra/reaggregation of saved terminal values and gradients. The independent economic evaluator is not imported or rerun. Compatibility alone does not certify the narrower production endpoints.'}

    def population_records(self):
        root=self.paths['statistics'];run=self.executions['statistics']
        inputs=read_json(root/'INPUTS120.json')
        require(inputs['primary']['sha256']==sha256(self.paths['primary']/'records120.jsonl')
                and inputs['independent']['sha256']==sha256(self.paths['independent']/'comparisons120.jsonl'),
                'Population statistics use different observations')
        rows=list(iter_rows(root/'POPULATION_GROUPS120.jsonl'))
        expected_groups=[(i,a,s) for i in range(2) for a in ARMS for s in SERVICES[1:]]
        require([(r['index'],r['arm'],r['service']) for r in rows]==expected_groups,'Full forty-eight population groups are required')
        def binomial_tail_at_most(p,k):
            c,d=p.numerator,p.denominator
            numerator=sum(math.comb(64,j)*c**j*(d-c)**(64-j) for j in range(k,65))
            return numerator*EVENT_DELTA.denominator<=EVENT_DELTA.numerator*d**64
        cache={};positive=0
        for got,(risk,arm,service) in zip(rows,expected_groups):
            source=[self.primary[(risk,j,arm,service)] for j in range(64)]
            gains=[(exact(self.comparisons[(risk,j,arm,service)]['gain_lower']),
                    exact(self.comparisons[(risk,j,arm,service)]['gain_upper'])) for j in range(64)]
            require(got['independent_units']==64 and got['missing_independent_rows']==[]
                    and got['missing_rows_use_full_safe_support_and_are_not_excluded'] is True,
                    'Completed population audit may not discard or fabricate an independent row')
            events=got['positive_threshold_events'];require(len(events)==4,'Missing fixed event threshold')
            staircase=Q(0);previous=Q(0)
            for event,threshold in zip(events,THRESHOLDS):
                k=sum(lo>=threshold for lo,_ in gains);lo,hi=exact(event['lower']),exact(event['inversion_upper'])
                require(exact(event['threshold'])==threshold and event['successes']==k,'Event count or prespecified threshold differs')
                if k==0:require(lo==hi==0 and event['exact_bisections']==0,'Zero-count exact lower bound differs')
                else:
                    require(event['exact_bisections']==48 and 0<=lo<hi<=1 and hi-lo==Q(1,2**48)
                            and (lo*2**48).denominator==(hi*2**48).denominator==1,
                            'Fixed outward binomial inversion resolution differs')
                    cache_key=(k,lo,hi)
                    if cache_key not in cache:cache[cache_key]=binomial_tail_at_most(lo,k) and not binomial_tail_at_most(hi,k)
                    require(cache[cache_key] and event['lower_endpoint_has_tail_at_most_delta'] is True
                            and event['upper_endpoint_has_tail_above_delta'] is True,
                            'Exact binomial endpoint inequalities are false')
                staircase+=(threshold-previous)*lo;previous=threshold
            ml=sum(lo for lo,_ in gains)/64;mu=sum(hi for _,hi in gains)/64
            hl=max(Q(0),ml-MEAN_RADIUS);hu=min(TAU,mu+MEAN_RADIUS)
            wanted={'sample_mean_gain_lower':ml,'sample_mean_gain_upper':mu,
                'hoeffding_population_mean_lower':hl,'hoeffding_population_mean_upper':hu,
                'population_mean_staircase_lower':staircase,'simultaneous_population_mean_lower':max(hl,staircase),
                'simultaneous_population_mean_upper':hu}
            require(all(exact(got[k])==v for k,v in wanted.items()) and 0<=staircase<=hu<=TAU,
                    'Exact bounded-mean or staircase reaggregation differs')
            require(got['accepted_steps']==sum(r['accepted_steps'] for r in source)
                    and got['changed_state_actions']==sum(r['action']!=r['completed_incumbent_action'] for r in source)
                    and got['total_singleton_seconds']==sum(r['seconds'] for r in source)
                    and got['actual_costs_are_descriptive_not_a_population_runtime_interval'] is True,
                    'Population group action/cost accounting differs')
            positive+=staircase>0
        exponent=2*64*(MEAN_RADIUS/TAU)**2;taylor=sum(exponent**j/math.factorial(j) for j in range(21))
        cert=run['radius_certificate']
        require(exponent==Q(1089,128) and taylor>3840 and cert['n']==64
                and list(map(exact,cert['gain_support']))==[0,TAU]
                and exact(cert['exact_radius'])==MEAN_RADIUS and exact(cert['exact_hoeffding_exponent'])==exponent
                and cert['exponential_lower_taylor_degree']==20
                and exact(cert['exact_exponential_lower_bound'])==taylor
                and exact(cert['two_sided_tail_strictly_below'])==Q(1,1920)
                and exact(cert['family_failure_probability_at_most'])==Q(1,20),
                'Finite exact Hoeffding-radius certificate differs')
        require(run['groups']==48 and run['threshold_events']==192 and run['independent_units']==64
                and exact(run['global_simultaneous_coverage_at_least'])==Q(19,20)
                and exact(run['per_threshold_failure'])==EVENT_DELTA
                and exact(run['per_mean_two_sided_failure'])==Q(1,1920)
                and run['positive_staircase_groups']==positive and run['complete_independent_validation'] is True,
                'Simultaneous inference family, coverage or executed census differs')
        self.counts['population_groups']=48;self.counts['threshold_records']=192
        self.details['population_statistics']={'groups':48,'threshold_events':192,'independent_units':64,
            'positive_staircase_groups':positive,'simultaneous_coverage_lower':'19/20',
            'scope':'Exact reaggregation and verification of the fixed 192 binomial brackets and 48 bounded-mean intervals; classical coverage remains conditional on the stated sampling and safety assumptions. Timings add no iid units.'}

    def reporting_outputs(self):
        root=self.paths['reporting'];run=success(root,'EXECUTION_REPORT120.json')
        require(run['source_commit']==SOURCE and run['economic_solver_executed'] is False
                and run['all_scientific_input_bytes_unchanged'] is True
                and run['primary_decisions']==4096 and run['timing_decisions']==6144
                and run['sample_contrasts']==992 and run['population_groups']==48 and run['threshold_events']==192,
                'Original saved-record reporting receipt or complete output census differs')
        source=run['reporter_source'];actual=record(self.revision/'code120/report120.py',self.revision)
        require(source['sha256']==actual['sha256'] and source['bytes']==actual['bytes'],
                'Reporter source differs from the actual reporting execution')
        manifest=read_json(root/'OUTPUT_MANIFEST120.json');seen=set();stable=[]
        for item in manifest['files']:
            require(item['path'] not in seen,'Duplicate report output member');seen.add(item['path'])
            got=record(path_in(root,item['path']),root)
            require(all(got[k]==item[k] for k in got),'Reporting output bytes changed: '+item['path'])
            declared=(item['path'].startswith('tables120/') and not Path(item['path']).name.startswith('research_ledger120.')) or item['path'].startswith('new120/')
            require(item['stable_replay_bytes'] is declared,'Predesignated reporting replay membership differs')
            if declared:stable.append(item['path'])
            else:require(bool(item.get('replay_byte_exclusion_reason')),'Excluded report metadata needs an explicit retained scope')
        actual_files={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        require(actual_files==seen|{'OUTPUT_MANIFEST120.json'} and manifest['stable_replay_files']==stable
                and len(stable)==36,'Complete fixed scientific reporting products are required')
        self.report_output_manifest=manifest
        self.counts['report_output_files']=len(seen)+1;self.counts['stable_report_outputs']=len(stable)
        self.details['reporting']={'full_group_pair_contrasts':992,'stable_replay_files':stable,
            'scope':'Every report output is hash-bound; only the declared 34 table files and two TeX snippets require deterministic replay equality. Actual clocks, environment, input paths and research-ledger derivatives remain separately retained.'}

    def replay(self,kind):
        target=self.out/(kind+'-replay');log=self.out/(kind+'-replay.log')
        if kind=='statistics':
            command=[sys.executable,str(self.revision/'code120/stats120.py'),'--source-commit',SOURCE,
                     '--primary',str(self.paths['primary']/'records120.jsonl'),
                     '--independent',str(self.paths['independent']/'comparisons120.jsonl'),'--output',str(target)]
        else:
            require(kind=='reporting','Only statistics and saved-record reporting can be replayed')
            command=[sys.executable,str(self.revision/'code120/report120.py'),'--revision',str(self.revision),
                     '--evidence-root',str(self.evidence),'--repository',str(self.repo),
                     '--source-commit',SOURCE,'--output',str(target)]
            for label,field in (('acquisition','acquisition'),('states','states'),('primary','primary'),
                                ('independent','independent'),('stats','statistics')):
                command+=['--'+label,self.manifest['layout'][field]]
            for relative in self.manifest.get('report_ledger_paths',[]):
                command+=['--ledger',str(path_in(self.revision,relative))]
        started=time.time()
        with log.open('xb') as stream:
            run=subprocess.run(command,cwd=self.revision,stdout=stream,stderr=subprocess.STDOUT,
                env=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_OPTIONAL_LOCKS='0',PYTHONHASHSEED='0',
                         OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1'))
        receipt={'kind':kind,'argv':command,'started_unix':started,'ended_unix':time.time(),
            'elapsed_seconds':time.time()-started,'exit_code':run.returncode,'log':record(log,self.out),
            'scientific_solver_acquisition_policy_or_timing_reexecuted':False}
        write_json(self.out/(kind.upper()+'_REPLAY_LAUNCH120.json'),receipt)
        require(run.returncode==0,'Bounded '+kind+' replay failed; its actual log and partial outputs are retained')
        if kind=='statistics':
            original=self.paths[kind]/'POPULATION_GROUPS120.jsonl';replayed=target/original.name
            require(sha256(original)==sha256(replayed) and original.stat().st_size==replayed.stat().st_size,
                    'Exact population statistics replay differs from the prespecified saved result')
            old=success(self.paths[kind]);new=success(target)
            excluded={'source','total_seconds','started_unix','ended_unix','inputs'}
            require({k:v for k,v in old.items() if k not in excluded}=={k:v for k,v in new.items() if k not in excluded},
                    'Stable statistics receipt fields differ after replay')
            compared=[record(replayed,target)]
        else:
            actual=success(target,'EXECUTION_REPORT120.json')
            require(actual['source_commit']==SOURCE and actual['economic_solver_executed'] is False,
                    'Reporter replay source or computational scope differs')
            produced=read_json(target/'OUTPUT_MANIFEST120.json')
            require(produced['stable_replay_files']==self.report_output_manifest['stable_replay_files'],
                    'The replay excluded or added a scientific table/snippet')
            originals={r['path']:r for r in self.report_output_manifest['files']}
            compared=[]
            for relative in produced['stable_replay_files']:
                got=record(path_in(target,relative),target);wanted=originals[relative]
                require(all(got[k]==wanted[k] for k in got),'Stable reporting replay bytes differ: '+relative)
                compared.append(got)
        write_json(self.out/(kind.upper()+'_REPLAY_VERIFIED120.json'),
            {'status':'passed','exit_code':0,'kind':kind,'files_compared':compared,
             'all_designated_bytes_equal':True,'actual_replay_metadata_retained_separately':True,
             'economic_evaluator_or_policy_campaign_reexecuted':False})
        self.details[kind+'_replay']={'status':'passed','compared_files':len(compared),
            'actual_elapsed_seconds':receipt['elapsed_seconds'],'economic_scientific_execution':False}


def require_manifest(manifest):
    require(manifest.get('schema')=='NBO_R120_EVIDENCE_MANIFEST_V1','Unsupported evidence manifest schema')
    require(manifest['retained_roots']==['results120'] and manifest['all_retained_result_files_included'] is True,
            'The complete results tree must be retained without selection')
    files=manifest['files'];require(len(files)==manifest['file_count'] and len({r['path'] for r in files})==len(files),
                                  'Duplicate or inconsistent complete evidence file census')
    require(sum(r['bytes'] for r in files)==manifest['total_payload_bytes'],'Full evidence payload byte census differs')
    require(all(r['path'].startswith('results120/') for r in files),'Unlisted evidence root')
    expected_census={'source_files':157,'source_bytes':1206453,'actors':16,'state_rows':64,'entropy_bytes':640,
        'primary_decisions':4096,'primary_cohorts':64,'timing_processes':3,'timing_decisions':6144,
        'independent_comparisons':4096,'population_groups':48,'threshold_records':192,
        'full_group_pair_contrasts':992,'arms':list(ARMS),'services':list(SERVICES)}
    require(manifest['expected_census']==expected_census,'Prespecified experiment census cannot be amended by packaging')
    require(set(manifest['layout'])=={'acquisition','states','primary','independent','statistics','reporting'},
            'All completed source/acquisition/sample/decision/validation/inference/reporting stages are required')


def prepare_evidence(manifest,revision,out,requested=None):
    native=(requested or revision).resolve();wanted={r['path']:r for r in manifest['files']}
    loose_complete=all(path_in(native,relative).is_file() for relative in wanted)
    bundles=manifest.get('archives',[])
    if manifest.get('archive'):
        require(not bundles,'Legacy single archive and multiple archives cannot both be declared')
        bundles=[{'archive':manifest['archive'],'files':manifest['files'],'descriptor':None}]
    covered=set();verified=[]
    for bundle in bundles:
        for item in bundle['files']:
            require(item['path'] in wanted and item==wanted[item['path']] and item['path'] not in covered,
                    'Archive bundles overlap or differ from the full saved evidence manifest')
            covered.add(item['path'])
        if bundle.get('descriptor'):
            item=bundle['descriptor'];require(record(path_in(revision,item['path']),revision)==item,'Reused checkpoint descriptor changed')
        archive=bundle['archive']
        require(archive['member_count']==len(bundle['files'])
                and archive['uncompressed_payload_bytes']==sum(r['bytes'] for r in bundle['files']),
                'Archive checkpoint member census differs')
    if loose_complete:
        evidence=native
        for bundle in bundles:verified.append(materialize(bundle,revision))
    else:
        require(bundles,'Loose raw evidence is incomplete and no lossless transport is supplied')
        evidence=out/'materialized-evidence'
        for index,bundle in enumerate(bundles):
            verified.append(materialize(bundle,revision,evidence,allow_existing_target=index>0))
        for relative in sorted(set(wanted)-covered):
            source=path_in(native,relative);require(record(source,native)==wanted[relative],
                    'A raw member is absent from both archive transport and the native source')
            target=path_in(evidence,relative);target.parent.mkdir(parents=True,exist_ok=True)
            with source.open('rb') as stream,target.open('xb') as output:shutil.copyfileobj(stream,output,1<<20)
    require(census(evidence,manifest['retained_roots'])==manifest['files'],
            'Full saved-evidence census contains missing, changed or unlisted result files')
    return evidence,{'archive_bundles':verified,'loose_complete_before_audit':loose_complete,
        'duplicate_expanded_copy_created':not loose_complete,'all_saved_raw_files_verified':len(wanted),
        'scope':'When complete loose bytes exist, archives are stream-verified without extraction. A fresh local copy is materialized only when needed; original evidence is never changed.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision',type=Path,default=REVISION)
    parser.add_argument('--evidence-root',type=Path)
    parser.add_argument('--repository',type=Path)
    parser.add_argument('--manifest',type=Path,default=Path('EVIDENCE_MANIFEST120.json'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--replay-statistics',action='store_true')
    parser.add_argument('--replay-reporting',action='store_true')
    parser.add_argument('--require-current-commit',action='store_true',
                        help='Require the manifest, packaging tools and support files to be exact blobs of the checked-out publication commit.')
    parser.add_argument('--require-final-author',action='store_true',
                        help='Require complete active author prose with no pending result/publication markers.')
    args=parser.parse_args();revision=args.revision.resolve();repo=(args.repository or repository(revision)).resolve()
    out=args.output.resolve();manifest_path=(args.manifest if args.manifest.is_absolute() else revision/args.manifest).resolve()
    require(not out.exists(),'Preserve any earlier audit; choose a fresh exclusive output directory')
    out.mkdir(parents=True,exist_ok=False);started=time.time();clock=time.perf_counter()
    write_json(out/'START_AUDIT120.json',{'status':'started','started_unix':started,'argv':sys.argv,
        'python':sys.version,'platform':platform.platform(),'manifest':str(manifest_path),
        'scope':'Existing record, archive/source custody and optional exact statistics/reporting replay only. No new scientific decisions, independent economic solves, samples, fits or competitive clocks.'})
    audit=None
    try:
        manifest=read_json(manifest_path);require_manifest(manifest)
        for relative in manifest['retained_roots']:
            for base in (revision,(args.evidence_root or revision).resolve()):
                raw=path_in(base,relative)
                require(out!=raw and raw not in out.parents,'Audit output must not enter the retained raw evidence census')
        bound=[]
        for kind in ('tool_sources','support_files'):
            require(bool(manifest[kind]),'Missing packaging/support source binding')
            for item in manifest[kind]:
                got=record(path_in(revision,item['path']),revision);require(got==item,'Packaging/support source changed: '+item['path'])
                bound.append((revision/item['path'],got))
        for item in manifest.get('repository_tool_sources',[]):
            got=record(path_in(repo,item['path']),repo);require(got==item,'Repository workflow source changed: '+item['path'])
            bound.append((repo/item['path'],got))
        publication_head=git(repo,'rev-parse','HEAD').decode().strip()
        if args.require_current_commit:
            current=tree(repo,publication_head,revision.relative_to(repo).as_posix())
            current.update(tree(repo,publication_head,'.github/workflows/nbo-r120-author-package.yml'))
            for path,item in bound+[(manifest_path,record(manifest_path,manifest_path.parent))]:
                require(current.get(path.relative_to(repo).as_posix())==item['git_blob'],
                        'A publication tool/support/manifest file is not the current committed source: '+str(path))
        if args.require_final_author:
            active=[revision/n for n in ('ECTA.tex','supp.tex','appendix.tex','RESPONSE_TO_REFEREE.tex')]
            active+=list((revision/'new120').glob('*.tex'))
            pending=[]
            for path in active:
                content=path.read_text().replace('\\_','_')
                if re.search(r'R120_PENDING_[A-Z_]+|R120-INTEGRATION-PENDING|RECEIPT-PENDING',content):pending.append(path.relative_to(revision).as_posix())
            require(not pending,'Final active author source still contains pending evidence: '+str(pending))
        evidence,transport=prepare_evidence(manifest,revision,out,args.evidence_root)
        write_json(out/'TRANSPORT_VERIFIED120.json',transport)
        audit=EvidenceAudit(revision,evidence,manifest,out,repo)
        for method in ('sources_and_custody','sampled_states','original_reports','author_routes',
                       'primary_and_timing','independent_records','population_records','reporting_outputs'):
            getattr(audit,method)()
            with (out/'PROGRESS_AUDIT120.jsonl').open('a',encoding='utf-8') as stream:
                stream.write(json.dumps({'completed_step':method,'ended_unix':time.time(),'counts':dict(audit.counts)},sort_keys=True)+'\n')
        if args.replay_statistics:audit.replay('statistics')
        if args.replay_reporting:audit.replay('reporting')
        require(census(evidence,manifest['retained_roots'])==manifest['files'],'Raw scientific inputs changed during the audit/replay')
        for path,item in bound:
            root=repo if path==repo/'.github/workflows/nbo-r120-author-package.yml' else revision
            require(record(path,root)==item,'Audit tool/support input changed during verification')
        result={'schema':'NBO_R120_SAVED_EVIDENCE_AUDIT_V1','status':'passed','exit_code':0,
            'started_unix':started,'ended_unix':time.time(),'elapsed_seconds':time.perf_counter()-clock,
            'checked_out_commit':publication_head,'publication_tool_commit_binding_required':args.require_current_commit,
            'manifest':record(manifest_path,manifest_path.parent),'source_commit':SOURCE,'actor_commit':ACTORS,
            'state_commit':STATES,'reporting_spec_commit':REPORT_SPEC,'counts':dict(audit.counts),'details':audit.details,
            'evidence_files':manifest['file_count'],'evidence_payload_bytes':manifest['total_payload_bytes'],
            'all_original_raw_bytes_unchanged':True,'full_scientific_campaign_rerun':False,
            'independent_economic_evaluator_imported_or_rerun':False,'new_acquisition_training_sampling_or_timing':False,
            'economic_advantage_or_publication_success_implied':False,
            'scope':'Successful complete record/byte/source/arithmetic audit with only the explicitly requested statistics/reporting replays. This receipt does not itself certify a PDF build, remote CI status or an economic improvement.'}
        write_json(out/'AUDIT_EVIDENCE120.json',result)
        print(json.dumps({'status':'passed','counts':dict(audit.counts),'elapsed_seconds':result['elapsed_seconds'],
                          'receipt':str(out/'AUDIT_EVIDENCE120.json')},sort_keys=True))
    except BaseException:
        write_json(out/'FAILED_AUDIT120.json',{'status':'failed','exit_code':1,'started_unix':started,
            'ended_unix':time.time(),'elapsed_seconds':time.perf_counter()-clock,'exception':traceback.format_exc(),
            'completed_counts':dict(audit.counts) if audit is not None else {},
            'all_partial_audit_and_replay_outputs_retained':True,'scientific_campaign_rerun':False})
        raise


if __name__=='__main__':
    main()
