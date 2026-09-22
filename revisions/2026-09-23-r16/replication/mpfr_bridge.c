/* Directed endpoint evaluation. MPFR is linked, not vendored.
   Standard headers are preferred; fallback declarations match the public
   MPFR 4.x ABI on the recorded LP64 Linux host . */
#include <stddef.h>
#include <math.h>
#if defined(__has_include) && __has_include(<mpfr.h>)
#include <mpfr.h>
#else
typedef long mpfr_prec_t;
typedef long mpfr_exp_t;
typedef struct {mpfr_prec_t _mpfr_prec; int _mpfr_sign; mpfr_exp_t _mpfr_exp; unsigned long *_mpfr_d;} mpfr_struct;
typedef mpfr_struct mpfr_t[1];
typedef mpfr_struct *mpfr_ptr;
typedef const mpfr_struct *mpfr_srcptr;
typedef enum {MPFR_RNDN=0,MPFR_RNDZ=1,MPFR_RNDU=2,MPFR_RNDD=3,MPFR_RNDA=4,MPFR_RNDF=5} mpfr_rnd_t;
extern void mpfr_init2(mpfr_ptr,mpfr_prec_t);
extern void mpfr_clear(mpfr_ptr);
extern int mpfr_set_d(mpfr_ptr,double,mpfr_rnd_t);
extern double mpfr_get_d(mpfr_srcptr,mpfr_rnd_t);
extern const char *mpfr_get_version(void);
#define DECL(name) extern int name(mpfr_ptr,mpfr_srcptr,mpfr_rnd_t)
DECL(mpfr_exp);DECL(mpfr_log);DECL(mpfr_tanh);DECL(mpfr_sqrt);
#define BIN(name) extern int name(mpfr_ptr,mpfr_srcptr,mpfr_srcptr,mpfr_rnd_t)
BIN(mpfr_add);BIN(mpfr_mul);BIN(mpfr_div);
#endif
const char *version(void) {return mpfr_get_version();}
int unary(int op,size_t n,const double *x,double *out,int upper){
 mpfr_t a,b;mpfr_init2(a,128);mpfr_init2(b,128);
 mpfr_rnd_t r=upper?MPFR_RNDU:MPFR_RNDD;
 for(size_t i=0;i<n;i++){
  mpfr_set_d(a,x[i],MPFR_RNDN);
  switch(op){case 0:mpfr_exp(b,a,r);break;case 1:mpfr_log(b,a,r);break;case 2:mpfr_tanh(b,a,r);break;case 3:mpfr_sqrt(b,a,r);break;default:mpfr_clear(a);mpfr_clear(b);return 1;}
  out[i]=mpfr_get_d(b,r);
 }
 mpfr_clear(a);mpfr_clear(b);return 0;
}
int binary(int op,size_t n,const double *x,const double *y,double *out,int upper){
 mpfr_t a,b,c;mpfr_init2(a,128);mpfr_init2(b,128);mpfr_init2(c,128);
 mpfr_rnd_t r=upper?MPFR_RNDU:MPFR_RNDD;
 for(size_t i=0;i<n;i++){
  mpfr_set_d(a,x[i],MPFR_RNDN);mpfr_set_d(b,y[i],MPFR_RNDN);
  switch(op){case 0:mpfr_add(c,a,b,r);break;case 1:mpfr_mul(c,a,b,r);break;case 2:mpfr_div(c,a,b,r);break;default:mpfr_clear(a);mpfr_clear(b);mpfr_clear(c);return 1;}
  out[i]=mpfr_get_d(c,r);
 }
 mpfr_clear(a);mpfr_clear(b);mpfr_clear(c);return 0;
}
