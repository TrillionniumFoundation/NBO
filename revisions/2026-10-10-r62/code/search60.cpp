// Exact rational search. No floating approximation or root solver selects actions.
// Input: number of requests; then mode cap Q q1 q2 q4 m h, m ridges,
// h squared hinges; mode 2 additionally supplies an explicit index set.
#include <boost/multiprecision/cpp_int.hpp>
#include <algorithm>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using boost::multiprecision::cpp_int;
using boost::multiprecision::cpp_rational;
using R=cpp_rational;
using Z=cpp_int;
struct Ridge {R w,z,s,r;};
struct Square {R w,z,s;};
struct Query {long cap,Q;R q1,q2,q4;std::vector<Ridge> f;std::vector<Square> h;};
struct Counters {long evaluations=0, differences=0, pieces=0;unsigned bits=0;};
R read_r(){std::string s;if(!(std::cin>>s))throw std::runtime_error("missing rational");auto k=s.find('/');if(k==std::string::npos)return R(Z(s));R x=R(Z(s.substr(0,k)))/R(Z(s.substr(k+1)));return x;}
void watch(const R& x,Counters& c){Z a=numerator(x);if(a<0)a=-a;Z b=denominator(x);unsigned z=std::max(a==0?0U:unsigned(boost::multiprecision::msb(a)+1),unsigned(boost::multiprecision::msb(b)+1));c.bits=std::max(c.bits,z);}
R positive(R x){return x>0?x:R(0);}
long floor_r(const R& x){Z a=numerator(x),b=denominator(x),q=a/b;if(a<0&&a%b!=0)--q;return q.convert_to<long>();}
long ceil_r(const R& x){return -floor_r(-x);}
R value(const Query& x,long j,Counters& c){R a=R(j)/x.Q;R v=x.q1*a+x.q2*a*a+x.q4*a*a*a*a;watch(v,c);for(const auto& f:x.f){R y=f.z+f.s*a,z;if(f.r==0)z=positive(y);else if(y<=-f.r)z=0;else if(y>=f.r)z=y;else {R u=y+f.r;z=u*u/(4*f.r);}v+=f.w*z;watch(v,c);}for(const auto& h:x.h){R u=positive(h.z+h.s*a);v+=h.w*u*u;watch(v,c);}++c.evaluations;return v;}
R diff(long j,long Q,const R& c1,const R& c2,const R& c4,Counters& c){R k=j,q=Q;R v=c1/q+c2*(2*k+1)/(q*q)+c4*(4*k*k*k+6*k*k+4*k+1)/(q*q*q*q);++c.differences;watch(v,c);return v;}
R second(long j,long Q,const R& c2,const R& c4,Counters& c){R k=j,q=Q;R v=2*c2/(q*q)+c4*(12*k*k+24*k+14)/(q*q*q*q);++c.differences;watch(v,c);return v;}
void piece(long lo,long hi,long Q,const R& c1,const R& c2,const R& c4,std::set<long>& candidates,Counters& c){
 if(lo>hi)return;++c.pieces;candidates.insert(lo);candidates.insert(hi);if(hi-lo<=1)return;
 // On nonnegative indices, second differences are nondecreasing for c4>=0.
 if(second(hi-2,Q,c2,c4,c)<0)return; // concave throughout: endpoints suffice.
 long l=lo,r=hi-2;while(l<r){long mid=l+(r-l)/2;if(second(mid,Q,c2,c4,c)>=0)r=mid;else l=mid+1;}
 long pivot=l;candidates.insert(pivot);
 if(diff(hi-1,Q,c1,c2,c4,c)<0)return;
 l=pivot;r=hi-1;while(l<r){long mid=l+(r-l)/2;if(diff(mid,Q,c1,c2,c4,c)>=0)r=mid;else l=mid+1;}
 candidates.insert(l);
}
std::set<long> algebraic(const Query& x,Counters& c){
 if(x.q4<0)throw std::runtime_error("negative quartic not supported by finite-difference theorem");
 R cap=R(x.cap)/x.Q;std::set<R> knots={R(0),cap};
 for(const auto& f:x.f)if(f.s!=0){for(R e:std::vector<R>{-f.r,f.r}){R k=(e-f.z)/f.s;if(k>0&&k<cap)knots.insert(k);}}
 for(const auto& h:x.h)if(h.s!=0){R k=-h.z/h.s;if(k>0&&k<cap)knots.insert(k);}
 std::vector<R> ks(knots.begin(),knots.end());std::set<long> candidates={0,x.cap};
 for(size_t i=0;i+1<ks.size();++i){R mid=(ks[i]+ks[i+1])/2,c1=x.q1,c2=x.q2;
  for(const auto& f:x.f){R y=f.z+f.s*mid;if(y>=f.r)c1+=f.w*f.s;else if(f.r>0&&y>-f.r){c1+=f.w*f.s*(f.z+f.r)/(2*f.r);c2+=f.w*f.s*f.s/(4*f.r);}}
  for(const auto& h:x.h)if(h.z+h.s*mid>0){c1+=2*h.w*h.z*h.s;c2+=h.w*h.s*h.s;}
  watch(c1,c);watch(c2,c);long lo=std::max(0L,ceil_r(ks[i]*x.Q));long hi=std::min(x.cap,floor_r(ks[i+1]*x.Q));
  piece(lo,hi,x.Q,c1,c2,x.q4,candidates,c);
 }
 return candidates;
}
int main(){try{std::ios::sync_with_stdio(false);long count;if(!(std::cin>>count)||count<0)return 2;
 for(long v=0;v<count;++v){int mode;Query x;long m,h;if(!(std::cin>>mode>>x.cap>>x.Q))throw std::runtime_error("missing query");x.q1=read_r();x.q2=read_r();x.q4=read_r();std::cin>>m>>h;
 if(x.Q<=0||x.cap<0||x.cap>x.Q||m<0||h<0)throw std::runtime_error("invalid query");Counters c;watch(x.q1,c);watch(x.q2,c);watch(x.q4,c);
 for(long j=0;j<m;++j){Ridge f{read_r(),read_r(),read_r(),read_r()};if(f.r<0)throw std::runtime_error("negative radius");watch(f.w,c);watch(f.z,c);watch(f.s,c);watch(f.r,c);x.f.push_back(f);}
 for(long j=0;j<h;++j)x.h.push_back(Square{read_r(),read_r(),read_r()});
 std::set<long> candidates;
 if(mode==0)for(long j=0;j<=x.cap;++j)candidates.insert(j);
 else if(mode==1)candidates=algebraic(x,c);
 else if(mode==2){long n;std::cin>>n;for(long j=0;j<n;++j){long z;std::cin>>z;if(z<0||z>x.cap)throw std::runtime_error("bad selected index");candidates.insert(z);}}
 else throw std::runtime_error("bad mode");
 if(candidates.empty())throw std::runtime_error("empty candidates");long best=*candidates.begin();R score=value(x,best,c);long ties=1;
 for(auto it=std::next(candidates.begin());it!=candidates.end();++it){R z=value(x,*it,c);if(z<score){score=z;best=*it;ties=1;}else if(z==score)++ties;}
 std::cout<<best<<" "<<score<<" "<<c.evaluations<<" "<<c.differences<<" "<<c.pieces<<" "<<c.bits<<" "<<ties<<" "<<candidates.size()<<"\n";
 }
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}return 0;}
