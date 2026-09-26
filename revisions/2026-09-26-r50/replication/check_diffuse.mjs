/* Independent BigInt-rational continuous-state certificate reader.
   No Python or solver code is imported. This is within-project replication,
   not a claim of externally authored scientific replication. */
import fs from 'node:fs';import zlib from 'node:zlib';
function gcd(a,b){a=a<0n?-a:a;b=b<0n?-b:b;while(b){let c=a%b;a=b;b=c;}return a;}
class Q{
 constructor(a,b=1n){if(a instanceof Q){this.n=a.n;this.d=a.d;return;}if(typeof a==='string'&&a.includes('/')){[a,b]=a.split('/');}a=BigInt(a);b=BigInt(b);if(b===0n)throw Error('zero denominator');if(b<0n){a=-a;b=-b;}let g=gcd(a,b);this.n=a/g;this.d=b/g;}
 add(z){z=q(z);return new Q(this.n*z.d+z.n*this.d,this.d*z.d);}
 neg(){return new Q(-this.n,this.d);}
 sub(z){return this.add(q(z).neg());}
 mul(z){z=q(z);return new Q(this.n*z.n,this.d*z.d);}
 div(z){z=q(z);return new Q(this.n*z.d,this.d*z.n);}
 cmp(z){z=q(z);let v=this.n*z.d-z.n*this.d;return v<0n?-1:v>0n?1:0;}
 pow(n){return new Q(this.n**BigInt(n),this.d**BigInt(n));}
 str(){return `${this.n}/${this.d}`;}
 floor50(){let d=1n<<50n,n=this.n*d,k=n/this.d;if(n<0n&&n%this.d)k--;return new Q(k,d);}
}
const q=x=>x instanceof Q?x:new Q(x);const zero=q(0),one=q(1);const sum=xs=>xs.reduce((a,b)=>a.add(b),zero);const min=(a,b)=>a.cmp(b)<=0?a:b;const max=(a,b)=>a.cmp(b)>=0?a:b;const ok=(v,m)=>{if(!v)throw Error(m);};
function envelope(lines,left,right){let cuts=[left,right];for(let i=0;i<lines.length;i++)for(let j=0;j<i;j++){let [a,b]=lines[i],[c,d]=lines[j];if(b.cmp(d)!==0){let x=c.sub(a).div(b.sub(d));if(left.cmp(x)<0&&x.cmp(right)<0)cuts.push(x);}}cuts.sort((a,b)=>a.cmp(b));let total=zero;for(let j=1;j<cuts.length;j++){let x=cuts[j-1],y=cuts[j],mid=x.add(y).div(2);let line=lines.reduce((best,v)=>v[0].add(v[1].mul(mid)).cmp(best[0].add(best[1].mul(mid)))<0?v:best);total=total.add(y.sub(x).mul(line[0].add(line[1].mul(mid))));}return total;}
const [proofPath,modelPath]=process.argv.slice(2);if(!modelPath)throw Error('usage: node check_diffuse.mjs PROOF.json.gz MODEL.json');
const e=JSON.parse(zlib.gunzipSync(fs.readFileSync(proofPath))),r=JSON.parse(fs.readFileSync(modelPath));
const canon=x=>Array.isArray(x)?x.map(canon):(x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canon(x[k])])):x);
ok(JSON.stringify(canon(e.model))===JSON.stringify(canon(r)),'model identity');ok(e.schema==='nbo-r50-diffuse-v1','schema');ok(r.kernel==='uniform-independent-reset'&&r.initial_law==='uniform[0,1]','laws');
const {T,m}=r,N=e.N,beta=q(r.beta),eps=q(r.epsilon),ga=r.gamma.map(q),g=r.g.map(v=>v.map(q)),k=r.k.map(v=>v.map(w=>w.map(q))),p=e.policy.map(v=>v.map(w=>w.map(q)));
ok(T>=1&&m>=2&&N>=1&&beta.cmp(zero)>0&&beta.cmp(one)<0&&eps.cmp(zero)>0,'primitives');ok(ga.length===m&&ga.every(x=>x.cmp(zero)>=0&&x.cmp(one)<=0)&&ga.some(x=>x.cmp(one)===0),'gamma');
let M=Array(T+1).fill(zero),U=zero;
for(let t=T-1;t>=0;t--){ok(g[t][0].cmp(zero)>0&&sum(g[t]).cmp(zero)>0,'g positivity');for(let a=0;a<m;a++)ok(k[t][a][0].cmp(zero)>=0&&sum(k[t][a]).cmp(zero)>=0,'cost positivity');ok(p[t].length===N,'cells');for(let c=0;c<N;c++){let row=p[t][c],mid=new Q(2*c+1,2*N);ok(row.length===m&&row.every(z=>z.cmp(zero)>=0)&&sum(row).cmp(one)===0,'simplex');for(let j of [c,c+1]){let x=new Q(j,N);let d=sum(row.map((v,a)=>v.mul(one.sub(ga[a])).mul(g[t][0].add(g[t][1].mul(x)))));ok(d.add(beta.mul(M[t+1])).cmp(eps)<=0,'all-state regret');}M[t]=M[t].add(sum(row.map((v,a)=>v.mul(one.sub(ga[a])).mul(g[t][0].add(g[t][1].mul(mid))).div(N))));U=U.add(beta.pow(t).mul(sum(row.map((v,a)=>v.mul(k[t][a][0].add(k[t][a][1].mul(mid))).div(N)))));}M[t]=M[t].add(beta.mul(M[t+1]));}
ok(U.cmp(q(e.upper))===0&&M.every((v,t)=>v.cmp(q(e.moments[t]))===0),'upper/moments');
const lam=e.lambda_density.map(row=>row.map(q)),prices=e.moment_prices.map(q),avg=lam.map(row=>sum(row).div(N));ok(lam.length===T&&prices.length===T&&lam.every(row=>row.length===N&&row.every(z=>z.cmp(zero)>=0)),'prices');
let L=zero;
for(let t=0;t<T;t++){for(let c=0;c<N;c++){let lines=ga.map((gamma,a)=>[0,1].map(j=>beta.pow(t).mul(k[t][a][j]).add(lam[t][c].add(prices[t]).mul(one.sub(gamma)).mul(g[t][j]))));L=L.add(envelope(lines,new Q(c,N),new Q(c+1,N)).floor50());}let residual=prices[t].neg();if(t)residual=residual.add(beta.mul(prices[t-1].add(avg[t-1])));L=L.add(eps.mul(min(zero,residual))).sub(eps.mul(avg[t]));}
L=max(zero,L);ok(L.cmp(q(e.lower))===0&&L.cmp(U)<=0,'lower');console.log(JSON.stringify({valid:true,language:'JavaScript BigInt',proof:proofPath,target_met:U.sub(L).cmp(q(e.target))<=0,width:U.sub(L).str()}));
