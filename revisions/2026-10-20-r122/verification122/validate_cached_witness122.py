"""Independent exact checks of saved R122 rational meshes; no optimization.

The d=2 formulas below are reconstructed directly from the economic model.
No production, frozen exact121, terminal solver, or third-party package is
imported. Interior terminal choices are checked using the unique dyadic
bisection cell and exact endpoint signs, rather than rerunning optimization.
"""
from __future__ import annotations
from fractions import Fraction as Q
import hashlib, json, math, zlib
from pathlib import Path

R=Q(1,32);BETA=Q(15,16);EPS=Q(1,2**20)
FRACTION_FIELDS=('q_lower','q_upper','j_lower','j_upper','optimum_lower',
 'all_action_anchor','all_action_gradient','all_action_minimizer',
 'risk_bin_mass','future_controller_allowance_added_exactly_once')

def require(ok,message,counts):
 counts['exact_assertions']=counts.get('exact_assertions',0)+1
 if not ok:raise ArithmeticError('R122 cached witness: '+message)

def enc(v):
 if isinstance(v,Q):return str(v)
 if isinstance(v,dict):return {str(k):enc(w) for k,w in v.items()}
 if isinstance(v,(tuple,list)):return [enc(w) for w in v]
 return v

def decoded_result(row):
 result=dict(row)
 for k in FRACTION_FIELDS:result[k]=Q(row[k])
 return result

def key_of_result(row):
 return (tuple(row['state_hex']),row['action_hex'],float(row['alpha']).hex())

def kid(k):return hashlib.sha256(json.dumps(k,separators=(',',':')).encode()).hexdigest()

def capacity(x):return Q(1,8)+sum(x)/16

def state(x,a,z):
 u,v=x
 return [Q(1,16)+u/2+v/8+u*(1-v)/16+a/2+z,
         Q(1,16)+v/2+u/8+v*(1-u)/16+a/4-z]

def economy(x,terminal=False):
 u,v=x;h=max(Q(0),Q(1,2)-u-v)
 return (2 if terminal else 1)*((u-Q(5,8))**2+(v-Q(5,8))**2)+(u-v)**2/4+2*h*h

def gradient(x,terminal=False):
 u,v=x;h=max(Q(0),Q(1,2)-u-v);c=4 if terminal else 2
 return [c*(u-Q(5,8))+(u-v)/2-4*h,c*(v-Q(5,8))+(v-u)/2-4*h]

def integral(p,l,r):return sum((c*(r**(j+1)-l**(j+1))/(j+1) for j,c in enumerate(p)),Q(0))
def value(p,z):return sum((c*z**j for j,c in enumerate(p)),Q(0))

def objective(x,a,alpha):
 zero=state(x,a,Q(0));p=[economy(zero,True),5*(zero[0]-zero[1]),Q(5)]
 width=2*R*alpha;left=max(-R,min(R-width,-p[1]/10-width/2));right=left+width
 eta=max(value(p,left),value(p,right))
 dual=(integral(p,-R,left)+integral(p,right,R))/(2*R*(1-alpha))
 excess=list(p);excess[0]-=eta
 primal=eta+(integral(excess,-R,left)+integral(excess,right,R))/(2*R*(1-alpha))
 tail_mean=(left*left-right*right)/(4*R*(1-alpha))
 g=gradient(zero,True);mean=[g[0]+5*tail_mean,g[1]-5*tail_mean]
 derivative=2*a+16*a**3+BETA*(mean[0]/2+mean[1]/4)
 upper=economy(x)+a*a+4*a**4+BETA*dual
 return dict(polynomial=p,tail_left=left,tail_right=right,threshold=eta,
  risk_dual=dual,risk_primal=primal,upper=upper,derivative=derivative,mean=mean)

def check_terminal(row,x,a,alpha,bins,node,key_id,counts):
 z=-R+Q(node,2*bins)*2*R;y=state(x,a,z);mid=node%2==1
 require(len(y)==2 and all(Q(1,32)<=v<=Q(27,32) for v in y),'successor domain',counts)
 b=Q(row['action']);cap=capacity(y)
 require(0<=b<=cap,'terminal feasible action',counts)
 obj=objective(y,b,alpha);g=obj['derivative'];upper=obj['upper']
 g0=objective(y,Q(0),alpha)['derivative'];gc=objective(y,cap,alpha)['derivative']
 if b==0:
  require(g0>=0,'original lower boundary sign',counts);steps=0
 elif b==cap:
  require(g0<0 and gc<=0,'original upper boundary sign',counts);steps=0
 else:
  require(g0<0<gc,'original interior boundary signs',counts)
  scaled=b*2**33/cap
  require(scaled.denominator==1 and scaled.numerator%2==1,'32-step odd dyadic midpoint',counts)
  m=(scaled.numerator-1)//2
  require(0<=m<2**32,'32-step dyadic cell index',counts)
  lo=cap*m/2**32;hi=cap*(m+1)/2**32
  require(objective(y,lo,alpha)['derivative']<0<=objective(y,hi,alpha)['derivative'],
          'unique exact terminal bisection cell signs',counts);steps=32
 step=max(-b,min(cap-b,-g/2));lower=upper+g*step+step*step
 require(0<=upper-lower<=EPS,'terminal original gap',counts)
 require(obj['risk_primal']==obj['risk_dual'],'continuous-risk primal-dual equality',counts)
 expected=dict(key_id=key_id,node=node,z=z,midpoint=mid,state=y,action=b,lower=lower,upper=upper,
  polynomial=obj['polynomial'],tail_left=obj['tail_left'],tail_right=obj['tail_right'],threshold=obj['threshold'],
  risk_primal=obj['risk_primal'],risk_dual=obj['risk_dual'],terminal_steps=32,
  terminal_steps_field_is_interior_budget=True,terminal_bisections_executed=steps,
  exact_boundary_sign_checks_precede_interior_bisection=True)
 if mid:
  mean=obj['mean'];s=gradient(y)
  pstate=[s[0]+BETA*(mean[0]*(Q(1,2)+(1-y[1])/16)+mean[1]*(Q(1,8)-y[1]/16)),
          s[1]+BETA*(mean[1]*(Q(1,2)+(1-y[0])/16)+mean[0]*(Q(1,8)-y[0]/16))]
  lam=max(Q(0),-g) if b==cap else Q(0);nu=max(Q(0),g) if b==0 else Q(0)
  residual=g+lam-nu;anchor=upper+lam*(b-cap)-nu*b-residual*residual/4
  slope=[v-lam/16 for v in pstate]
  expected.update(state_gradient=pstate,action_gradient=g,multiplier_upper=lam,multiplier_lower=nu,
   stationarity_residual=residual,support_anchor=anchor,support_slope=slope)
 expected['sequence']=row['sequence']
 require(row==enc(expected),'every serialized terminal witness field',counts)
 counts['terminal_contexts']=counts.get('terminal_contexts',0)+1
 counts['represented_terminal_bisections']=counts.get('represented_terminal_bisections',0)+steps
 counts['interior_terminal_cells_checked']=counts.get('interior_terminal_cells_checked',0)+int(steps==32)
 return expected

def validate_policy(row,mesh,counts):
 bins=row['bins'];require(type(bins) is int and bins in (64,128,256,512),'fixed mesh ladder',counts)
 x=tuple(Q(v) for v in row['state']);a=Q(row['action']);alpha=Q(row['alpha']);k=key_of_result(row)
 require(len(x)==2 and alpha in (Q(1,2),Q(3,4)) and all(0<=v<=1 for v in x),'original state/risk domain',counts)
 require(0<=a<=capacity(x),'original root feasibility',counts)
 require(k==(tuple(float(v).hex() for v in x),float(a).hex(),float(alpha).hex()) and kid(k)==row['key_id'],
         'original exact policy identity',counts)
 require(len(mesh)==2*bins+1,'complete terminal mesh',counts)
 checked=[check_terminal(z,x,a,alpha,bins,n,row['key_id'],counts) for n,z in enumerate(mesh)]
 mids=checked[1::2];ends=checked[::2];stage=economy(x)+a*a+4*a**4
 tails=bins*(1-alpha);require(tails.denominator==1 and tails>0,'integral risk-bin mass',counts);tails=int(tails)
 qlo=stage+BETA*sum(sorted((r['lower'] for r in mids),reverse=True)[:tails])/tails
 atoms=[ends[j]['upper'] for j in range(bins)]+[ends[j+1]['upper'] for j in range(bins)]
 qhi=stage+BETA*sum(sorted(atoms,reverse=True)[:2*tails])/(2*tails)
 selected=sorted(range(bins),key=lambda j:(-mids[j]['support_anchor'],j))[:tails]
 anchor=stage+BETA*sum(mids[j]['support_anchor'] for j in selected)/tails
 slope=2*a+16*a**3+BETA*sum(mids[j]['support_slope'][0]/2+mids[j]['support_slope'][1]/4 for j in selected)/tails
 step=max(-a,min(capacity(x)-a,-slope/2));optimum=anchor+slope*step+step*step
 expected=dict(key_id=kid(k),state=[float(v) for v in x],state_hex=list(k[0]),action=float(a),action_hex=k[1],alpha=float(alpha),
  q_lower=qlo,q_upper=qhi,j_lower=qlo,j_upper=qhi+BETA*EPS,optimum_lower=optimum,
  all_action_anchor=anchor,all_action_gradient=slope,all_action_minimizer=a+step,
  risk_bin_indices=selected,risk_bin_mass=Q(1,tails),bins=bins,terminal_steps=32,terminal_contexts=2*bins+1,
  future_controller_allowance_added_exactly_once=BETA*EPS,seconds=row['seconds'])
 require(type(row['seconds']) in (int,float) and math.isfinite(row['seconds']) and row['seconds']>=0,'historical actual seconds',counts)
 require(qlo<=qhi and optimum<=qhi,'original independent bound order',counts)
 require(row==enc(expected),'every saved policy evaluation field',counts)
 counts['policies_validated']=counts.get('policies_validated',0)+1
 return row

def stream_part(path,sealed,diagnostics):
 """Read complete JSON lines; an unsealed prefix is never assigned a CRC pass."""
 decoder=zlib.decompressobj(16+zlib.MAX_WBITS);buffer=b'';sequence=0
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(64*1024),b''):
   buffer+=decoder.decompress(block)
   while b'\n' in buffer:
    line,buffer=buffer.split(b'\n',1)
    if not line:raise ValueError('Empty witness record')
    row=json.loads(line)
    if row.get('sequence')!=sequence:raise ValueError('Per-part witness sequence differs')
    sequence+=1;yield row
 if decoder.unused_data:raise ValueError('Unexpected bytes after gzip member')
 if sealed and (not decoder.eof or buffer):raise ValueError('Sealed gzip CRC/footer or final line is incomplete')
 diagnostics.append({'path':str(path),'sealed':sealed,'gzip_footer_validated':decoder.eof,
  'complete_records':sequence,'incomplete_unterminated_bytes':len(buffer)})

def witness_rows(source,allow_unsealed,diagnostics):
 source=Path(source);sealed=[json.loads(x) for x in (source/'SEALED_WITNESS_PARTS122.jsonl').read_text().splitlines()]
 expected={r['path']:r for r in sealed};parts=sorted((source/'terminal_witnesses122').glob('part*.jsonl.gz'))
 if [p.name for p in parts]!=[f'part{j:05d}.jsonl.gz' for j in range(len(parts))]:raise ValueError('Witness part sequence has a gap')
 if len(parts)!=len(sealed)+(1 if allow_unsealed else 0):raise ValueError('Unexpected sealed/unsealed witness census')
 for p in parts:
  rel=str(p.relative_to(source));is_sealed=rel in expected
  if is_sealed:
   row=expected[rel]
   if p.stat().st_size!=row['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Sealed witness byte identity differs')
  elif not allow_unsealed:raise ValueError('Unsealed witness outside declared interrupted source')
  yield from stream_part(p,is_sealed,diagnostics)
