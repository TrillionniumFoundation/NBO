"""Source-bound exact checks of newly frozen policies and their evidence."""
import csv,json,pathlib,time,hashlib
from fractions import Fraction as F
import numpy as np
import independent94 as other
from interval94 import I
from investment94 import terminal_details,terminal_certificate
from continuum94 import policy_cost
from representations94 import Fit
from study94 import ROOT,ARMS,LEVELS,sha,dump,source_files,paired_interval

def audit(output,tag='primary'):
    start=time.perf_counter();cal=json.loads((output/'CALIBRATION94.json').read_text());dest=output/f'evaluation-{tag}';res=json.loads((dest/'RESULTS94.json').read_text())
    if cal['source_files']!=source_files() or res['source_files']!=source_files():raise AssertionError('Source identity mismatch')
    if res['calibration_sha256']!=sha(output/'CALIBRATION94.json'):raise AssertionError('Calibration freeze mismatch')
    detail=[];models_checked=0;rows_seen=0;all_pairs={}
    for idx,alpha in enumerate(LEVELS):
        observations={}
        for arm in ARMS:
            path=dest/f'alpha-{idx}-{arm}.csv'
            if sha(path)!=res['levels'][str(idx)]['arms'][arm]['data']['raw_sha256']:raise AssertionError('Raw row corruption')
            data=np.genfromtxt(path,delimiter=',',names=True)
            if len(data)!=2048 or not np.array_equal(data['row'],np.arange(2048)):raise AssertionError('Missing or duplicated evaluation rows')
            rows_seen+=len(data)
            if not np.all(np.isfinite(data['cost_lower'])) or np.any(data['cost_lower']>data['cost_upper']):raise AssertionError('Invalid raw cost interval')
            observations[arm]={'lower':data['cost_lower'],'upper':data['cost_upper']}
            if arm!='online-risk-dp':
                fpath=output/f'alpha-{idx}'/f'{arm}.json';obj=json.loads(fpath.read_text());model=Fit.from_dict(obj)
                if sha(fpath)!=cal['levels'][str(idx)]['constructions'][arm]['model_sha256']:raise AssertionError('Model corruption')
                for rowid in (0,1023,2047):
                    x=[data['x0'][rowid],data['x1'][rowid]];v=model.interval(I(x));exact=other.feature_value(obj,x)
                    if not F(float(v.lo))<=exact<=F(float(v.hi)):raise AssertionError('Independent serialized continuation mismatch')
                models_checked+=1
            for rowid in (0,2047):
                x=[data['x0'][rowid],data['x1'][rowid]];a=data['action'][rowid]
                if not F(0)<=F(a)<=F(1,8)+sum(map(F,x))/16:raise AssertionError('Original capacity violation')
                # A finer independent threshold integral encloses all qualified
                # terminal policies; require the production outer interval to
                # contain it, not merely overlap it.
                l,u=other.nested_policy_bounds(x,a,alpha,bins=512)
                if not F(float(data['cost_lower'][rowid]))<=l<=u<=F(float(data['cost_upper'][rowid])):raise AssertionError('Independent finer continuous-policy enclosure not contained')
                detail.append({'alpha':alpha,'arm':arm,'row':rowid,'independent_bins':512,'independent_lower':str(l),'independent_upper':str(u),'production_lower':float(data['cost_lower'][rowid]),'production_upper':float(data['cost_upper'][rowid]),'contained':True})
        import itertools
        for a,b in itertools.combinations(ARMS,2):
            obj=paired_interval(observations[a],observations[b]);expected=res['levels'][str(idx)]['pairwise'][a+' minus '+b]
            if obj!=expected:raise AssertionError('Pairwise inference does not replay from raw rows')
            all_pairs[str(idx)+':'+a+'-'+b]=True
    # Tampering is tested in-memory, not by altering retained observations.
    record={'source_files':source_files(),'audit_source_sha256':sha(pathlib.Path(__file__)),'calibration_sha256':sha(output/'CALIBRATION94.json'),'result_sha256':sha(dest/'RESULTS94.json'),'raw_arm_rows_checked':rows_seen,'independent_initial_states':4096,'serialized_fits_checked':models_checked,'exact_feature_fixtures':models_checked*3,'full_continuous_policy_fixtures':detail,'pairwise_replays':all_pairs,'seconds':time.perf_counter()-start,'scope':'Separately coded Fraction original primitives, threshold integrals and complete-policy enclosures. Not an external full learning-stack or largest-vector reimplementation.','success':True}
    dump(ROOT/'audit'/'reproduction94'/f'INDEPENDENT94-{tag}.json',record);print(json.dumps({'success':True,'seconds':record['seconds'],'policy_fixtures':len(detail),'raw_arm_rows':rows_seen}));return record
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,default=ROOT/'results94');p.add_argument('--tag',default='primary');a=p.parse_args();audit(a.output,a.tag)
