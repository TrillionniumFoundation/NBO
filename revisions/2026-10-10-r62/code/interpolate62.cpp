// R62 positive multilinear interpolation. No hidden BLAS/optimizer arithmetic.
// Python adds the proved absolute floating-point allowance to each endpoint.
#include <cmath>
#include <cstddef>
#include <cfenv>
#include <limits>
#include <vector>
static_assert(std::numeric_limits<double>::is_iec559 && std::numeric_limits<double>::digits==53,"binary64 required");
extern "C" int interpolate62(const double* values,const double* points,double* output,
                             std::size_t count,int d,int n) {
    if(d<2 || d>12 || n<1 || (n&(n-1)) || std::fegetround()!=FE_TONEAREST) return -1;
    const std::size_t corners=std::size_t(1)<<d;
    std::vector<std::size_t> stride(d),offset(corners);
    stride[d-1]=1;for(int j=d-2;j>=0;--j)stride[j]=stride[j+1]*(n+1);
    for(std::size_t mask=0;mask<corners;++mask){offset[mask]=0;for(int j=0;j<d;++j)if((mask>>j)&1)offset[mask]+=stride[j];}
    std::vector<double> weights(corners),fraction(d);
    for(std::size_t k=0;k<count;++k){
        std::size_t base=0;
        for(int j=0;j<d;++j){
            double x=points[k*d+j];if(!std::isfinite(x)||x<0||x>1)return -2;
            double scaled=x*n;int cell=static_cast<int>(scaled);if(cell==n)cell=n-1;
            fraction[j]=scaled-cell;base+=std::size_t(cell)*stride[j];
        }
        weights[0]=1.;std::size_t used=1;
        for(int j=0;j<d;++j){double w=fraction[j];for(std::size_t z=0;z<used;++z){double old=weights[z];weights[z+used]=old*w;weights[z]=old*(1.-w);}used*=2;}
        double sum=0.;
        for(std::size_t z=0;z<corners;++z){double value=values[base+offset[z]];if(!std::isfinite(value))return -3;sum=sum+weights[z]*value;}
        if(!std::isfinite(sum))return -4;output[k]=sum;
    }
    return 0;
}
