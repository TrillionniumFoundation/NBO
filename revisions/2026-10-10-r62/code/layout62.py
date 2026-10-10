"""One-time ordinary print-layout edit; frozen mathematics is not rewritten."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
OLD=r'''\[
 Q_t^*(x,a)=S(x)+R(a)+\beta\mathbb E V_{t+1}^*(F(x,a,Z)),
 \qquad V_t^*(x)=\min_{a\in A(x)}Q_t^*(x,a),\quad V_T^*=g.
\]'''
NEW=r'''\begin{align*}
 Q_t^*(x,a)&=S(x)+R(a)+\beta\mathbb E V_{t+1}^*(F(x,a,Z)),\\
 V_t^*(x)&=\min_{a\in A(x)}Q_t^*(x,a),\qquad V_T^*=g.
\end{align*}'''

def main():
    marker=R/'audit/PRINT_REFLOW62.json'
    if marker.exists():print('Bellman-definition print display already reflowed.');return
    if (R/'audit/SOURCE_BINDING62.json').exists():raise RuntimeError('Do not silently replace a final publication binding')
    import science62
    freeze=science62.verify();path=R/'sections/accuracy62-print.tex';text=path.read_text()
    if text.count(OLD)!=1:raise AssertionError('Unique Bellman definition not found')
    old=hashlib.sha256(text.encode()).hexdigest();text=text.replace(OLD,NEW,1);path.write_text(text)
    if science62.verify()!=freeze:raise AssertionError('Frozen mathematical source changed')
    marker.write_text(json.dumps(dict(status='reflowed',source_freeze_sha256=freeze,print_copy_before=old,print_copy_after=hashlib.sha256(text.encode()).hexdigest(),change='One displayed line split into an align* environment; no mathematical token or hypothesis removed.',scope='Ordinary print-layout copy only. The exact scientific theorem source included in the prospective freeze is unchanged.'),indent=2)+'\n')
    print('Reflowed Bellman definition; frozen source unchanged.',flush=True)
if __name__=='__main__':main()
