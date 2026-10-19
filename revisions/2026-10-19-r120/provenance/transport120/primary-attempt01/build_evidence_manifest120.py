"""Build an exclusive complete R120 evidence census after actual outputs exist.

This records and optionally archives existing bytes. It never acquires labels,
draws entropy, trains actors, evaluates a policy, re-times a service or builds
a PDF. The final publication source/PDF/ZIP chain is separate from this file.
"""
from __future__ import annotations
import argparse
import datetime as dt
import gzip
import hashlib
import io
import os
from pathlib import Path
import tarfile
import time
import traceback

from evidence_common120 import (ACTORS,ARMS,REPORT_SPEC,REVISION,SERVICES,SOURCE,STATES,
    census,path_in,read_json,record,require,safe_relative,write_json)

DEFAULTS={'acquisition':'results120/acquisition-attempt01','states':'results120/states-attempt01',
          'primary':'results120/primary-attempt01','independent':'results120/independent-attempt01',
          'statistics':'results120/stats-attempt01','reporting':'results120/reporting-attempt01'}
PUBLICATIONS={'source':'provenance/SOURCE_PUBLICATION120.json',
              'actors':'provenance/ACTOR_PUBLICATION120.json',
              'states':'provenance/STATE_PUBLICATION120.json',
              'reporting_spec':'provenance/REPORTING_PUBLICATION120.json'}
TOOLS=['verification120/evidence_common120.py','verification120/build_evidence_manifest120.py',
       'verification120/audit_evidence120.py','code120/report120.py','code120/stats120.py',
       'build120.py','requirements120.txt']

class SplitArchive(io.RawIOBase):
    def __init__(self,revision,prefix,limit):
        super().__init__();self.revision=revision;self.prefix=prefix;self.limit=limit
        self.current=None;self.current_bytes=0;self.parts=[];self.total=0;self.hash=hashlib.sha256()
    def writable(self):return True
    def write(self,data):
        view=memoryview(data);written=0
        while written<len(view):
            if self.current is None:
                name=self.prefix+f'.tar.gz.part{len(self.parts):04d}'
                path=path_in(self.revision,name);path.parent.mkdir(parents=True,exist_ok=True)
                self.current=path.open('xb');self.parts.append(path);self.current_bytes=0
            n=min(self.limit-self.current_bytes,len(view)-written)
            chunk=view[written:written+n];self.current.write(chunk);self.hash.update(chunk)
            self.current_bytes+=n;self.total+=n;written+=n
            if self.current_bytes==self.limit:self.finish_part()
        return written
    def finish_part(self):
        if self.current is not None:
            self.current.flush();os.fsync(self.current.fileno());self.current.close();self.current=None
    def close(self):
        self.finish_part();super().close()

def make_archive(revision,evidence,files,prefix,part_bytes):
    prefix=safe_relative(prefix)
    require(not prefix.startswith('results120/'),'Archive transport cannot enter its own raw census')
    sink=SplitArchive(revision,prefix,part_bytes)
    try:
        with gzip.GzipFile(filename='',mode='wb',fileobj=sink,mtime=0,compresslevel=6) as compressed:
            with tarfile.open(fileobj=compressed,mode='w|',format=tarfile.PAX_FORMAT) as archive:
                for item in files:
                    path=path_in(evidence,item['path'])
                    require(record(path,evidence)==item,'Input changed before archiving: '+item['path'])
                    info=tarfile.TarInfo(item['path']);info.size=item['bytes'];info.mode=0o644
                    info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
                    with path.open('rb') as stream:archive.addfile(info,stream)
    finally:
        sink.close()
    return {'kind':'concatenated-tar-gzip-parts','sha256':sink.hash.hexdigest(),
            'compressed_bytes':sink.total,'uncompressed_payload_bytes':sum(r['bytes'] for r in files),
            'member_count':len(files),'parts':[record(p,revision) for p in sink.parts],
            'scope':'Transport of all already-recorded raw results; originals are not deleted or modified.'}

def successful(path,name='EXECUTION120.json'):
    data=read_json(path/name)
    require(data.get('status') in ('executed','passed') and data.get('exit_code',0)==0,
            'Selected completed episode is not successful: '+str(path/name))
    return data

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision',type=Path,default=REVISION)
    parser.add_argument('--evidence-root',type=Path)
    parser.add_argument('--output',type=Path,default=Path('EVIDENCE_MANIFEST120.json'))
    for kind,value in DEFAULTS.items():parser.add_argument('--'+kind,default=value)
    parser.add_argument('--launch-reporting',default=None,
                        help='Optional existing external reporter launch receipt; report self-receipts remain required.')
    parser.add_argument('--archive-prefix',default=None,
                        help='Optional new relative transport prefix, e.g. evidence120/results120')
    parser.add_argument('--part-bytes',type=int,default=48*1024*1024)
    args=parser.parse_args();revision=args.revision.resolve()
    evidence=(args.evidence_root or revision).resolve()
    output=args.output if args.output.is_absolute() else revision/args.output
    require(not output.exists(),'Preserve earlier manifest; choose a new output filename')
    require(args.part_bytes>=1<<20,'Archive parts must be at least one MiB')
    started=time.time();stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    attempt=revision/'provenance/evidence120'/stamp
    attempt.mkdir(parents=True,exist_ok=False)
    write_json(attempt/'START_MANIFEST120.json',{'started_utc':stamp,'argv':__import__('sys').argv,
               'scope':'Existing-byte census and optional archive only; no science/build/replay.'})
    try:
        layout={kind:safe_relative(getattr(args,kind)) for kind in DEFAULTS}
        for kind in ('acquisition','states','primary','independent','statistics'):
            data=successful(path_in(evidence,layout[kind]))
            require(data['source']['source_commit']==SOURCE,'Wrong source in selected '+kind+' episode')
        report=successful(path_in(evidence,layout['reporting']),'EXECUTION_REPORT120.json')
        # The auditor, rather than this builder, verifies every substantive
        # field. A builder exit zero is only successful byte-manifest creation.
        launches={kind:'results120/launches/'+label+'/LAUNCH120.json' for kind,label in
                  [('acquisition','acquisition-attempt01'),('states','states-attempt01'),
                   ('primary','primary-attempt01'),('independent','independent-attempt01'),
                   ('statistics','stats-attempt01')]}
        if args.launch_reporting:launches['reporting']=safe_relative(args.launch_reporting)
        for kind,path in launches.items():
            launch=read_json(path_in(evidence,path))
            require(launch.get('status')=='executed' and launch.get('exit_code')==0,
                    'Missing/completed external launch receipt: '+kind)
        files=census(evidence,['results120'])
        sources=[record(path_in(revision,p),revision) for p in TOOLS]
        support_names=['SOURCE_FREEZE120.json','REPORTING_SPEC120.md',*PUBLICATIONS.values()]
        support=[record(path_in(revision,p),revision) for p in support_names]
        frozen=read_json(revision/'SOURCE_FREEZE120.json')
        require(frozen['total_files']==157 and frozen['total_bytes']==1206453,'Unexpected source freeze census')
        failures=[r['path'] for r in files if any(token in Path(r['path']).name.upper()
                  for token in ('FAILED','FAILURE','ERRORS'))]
        archive=make_archive(revision,evidence,files,args.archive_prefix,args.part_bytes) if args.archive_prefix else None
        require(census(evidence,['results120'])==files,'Raw evidence changed while the manifest was built')
        manifest={'schema':'NBO_R120_EVIDENCE_MANIFEST_V1','prepared_utc':stamp,
            'scope':'Complete original saved-evidence inventory and source/custody interface. Creation is not a record-audit, economic evaluation, CI success or final publication claim.',
            'commits':{'source':SOURCE,'actors':ACTORS,'states':STATES,'reporting_spec':REPORT_SPEC},
            'layout':layout,'retained_roots':['results120'],'files':files,
            'file_count':len(files),'total_payload_bytes':sum(r['bytes'] for r in files),
            'all_retained_result_files_included':True,'failure_named_records':failures,
            'publication_receipts':PUBLICATIONS,'external_launch_receipts':launches,
            'support_files':support,'tool_sources':sources,'archive':archive,
            'expected_census':{'source_files':157,'source_bytes':1206453,'actors':16,
                'state_rows':64,'entropy_bytes':640,'primary_decisions':4096,
                'primary_cohorts':64,'timing_processes':3,'timing_decisions':6144,
                'independent_comparisons':4096,'population_groups':48,'threshold_records':192,
                'full_group_pair_contrasts':992,'arms':list(ARMS),'services':list(SERVICES)},
            'report_replay_contract':{'output_manifest':'OUTPUT_MANIFEST120.json',
                'required_stable_member_field':'stable_replay_files',
                'scope':'Only predesignated deterministic scientific report products; actual replay receipts, absolute paths and explicitly derivative research-ledger outputs keep separate identities.'},
            'audit_scope':'File and archive bytes, full identities, recorded arithmetic/invariants, exact-statistics replay and saved-record reporting only. No original terminal solve, new policy evaluation, label/training/sample acquisition or timing campaign is rerun.',
            'publication_scope':'The final author source, actual build/PDF hashes, CI observation and ZIP are bound by later separate source-bound publication receipts.'}
        write_json(output,manifest)
        write_json(attempt/'MANIFEST_BUILD120.json',{'status':'manifest_created','exit_code':0,
            'started_unix':started,'ended_unix':time.time(),'elapsed_seconds':time.time()-started,
            'manifest':record(output,revision),'file_count':len(files),
            'scientific_execution':False,'evidence_audit_execution':False,
            'archive_created':archive is not None,'original_files_deleted_or_modified':False})
        print(__import__('json').dumps({'status':'manifest_created','manifest':str(output),
                                      'files':len(files),'bytes':manifest['total_payload_bytes']}))
    except BaseException:
        write_json(attempt/'FAILED_MANIFEST120.json',{'status':'failed','ended_unix':time.time(),
            'elapsed_seconds':time.time()-started,'exception':traceback.format_exc(),
            'partial_transport_files_preserved':True,'scientific_execution':False})
        raise

if __name__=='__main__':
    main()
