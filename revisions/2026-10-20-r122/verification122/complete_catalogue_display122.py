"""Eight-page legible display of the entire already verified catalogue.

The fixed 14/15 row split does not select outcomes. Every exact data field,
all116 contrasts,348 original timing points, and each complete-panel scale
are preserved. This reader does not import an economic or inference module.
"""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime, timezone
import argparse,hashlib,json,time

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--figures',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    start=time.perf_counter();src=a.figures.resolve();out=a.output.resolve()
    source_receipt_sha=sha(src/'FIGURES_RECEIPT122.json')
    rec=json.loads((src/'FIGURES_RECEIPT122.json').read_text())
    assert rec['all_intervention_contrasts']==116 and rec['all_timing_contrast_points']==348
    bound={}
    for row in rec['output_files']:
        p=src/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
        bound[row['path']]={'bytes':row['bytes'],'sha256':row['sha256']}
    assert {'PLOTTED_COMPLETE_DATA122.json','PANELS_LAYOUT122.json','complete_intervention_catalogue122.pdf'}<=set(bound)
    data=json.loads((src/'PLOTTED_COMPLETE_DATA122.json').read_text())
    layout=json.loads((src/'PANELS_LAYOUT122.json').read_text())
    assert len(data)==116 and sum(len(x['clocks']) for x in data)==348
    arms=('quadratic','relu','hinge','spline','poly2','poly3','grid')
    expected=[(i,b,arm,loss,s) for i in range(2) for s in ('recycled','adaptive') for b,arm,loss in [(0,'online','online')]+[(b,arm,loss) for b in (5,9) for arm in arms for loss in ('value','marginal')]]
    fields=('index','budget','arm','loss','service')
    assert [tuple(x[f] for f in fields) for x in data]==expected
    assert len(layout)==4
    out.mkdir(parents=True,exist_ok=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.lines import Line2D
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.facecolor':'white'})
    blue,orange,gray='#185c8d','#bc5a15','#9ca6ae';colors=('#175b8a','#b05a17','#477d48')
    pdf=out/'complete_catalogue_display122.pdf';pages_map=[]
    with PdfPages(pdf,metadata={'Title':'Complete NBO R122 intervention and cost catalogue','Author':'Qian QI','CreationDate':None,'ModDate':None}) as pages:
        for panel in layout:
            rows=[x for x in data if x['index']==panel['index'] and x['service']==panel['service']];assert len(rows)==29
            for part,(begin,end) in enumerate(((0,14),(14,29)),1):
                subset=rows[begin:end];fig,axes=plt.subplots(1,3,figsize=(11.7,8.3),sharey=True,gridspec_kw={'width_ratios':[1.16,1,1.05]})
                fig.subplots_adjust(left=.245,right=.985,top=.82,bottom=.19,wspace=.24)
                risk='1/2' if panel['index']==0 else '3/4';service=panel['service']
                fig.suptitle(f'Original-policy intervention: risk {risk}, {service}',x=.025,ha='left',y=.965,fontsize=15,fontweight='bold')
                fig.text(.025,.918,f'Fixed catalogue rows {begin+1}-{end} of 29; part {part} of 2. All 116 contrasts and 348 paired clocks appear in the eight-page display.',fontsize=8.4)
                labels=[]
                for y,row in enumerate(subset):
                    name='online' if row['arm']=='online' else f"b{row['budget']}  {row['arm']} / {row['loss']}"
                    labels.append(f"{name} [{row['changed_actions']}/32]")
                    raw=[float(F(row[k]))*1e6 for k in ('raw_independent_sample_gain_lower','raw_independent_sample_gain_upper')]
                    safe=[float(F(row[k]))*1e6 for k in ('sample_gain_lower','sample_gain_upper')]
                    pop=[float(F(row[k]))*1e6 for k in ('population_gain_lower','population_gain_upper')]
                    axes[0].plot(raw,[y,y],color=gray,linewidth=3,zorder=1)
                    axes[0].plot(safe,[y,y],color=blue,linewidth=1.7,zorder=2)
                    axes[0].plot(float(F(row['mean_certified_gain_lower']))*1e6,y,marker='o',markersize=3.8,color=orange,zorder=3)
                    axes[1].plot(pop,[y,y],color=blue,linewidth=1.7)
                    axes[1].plot(pop[0],y,marker='|',markersize=6,color=blue)
                    assert [x['scenario'] for x in row['clocks']]==['timing00','timing01','timing02']
                    for j,clock in enumerate(row['clocks']):
                        value=float(F(clock['added_full_allocated_seconds_per_decision']))*1000
                        axes[2].plot(value,y+(j-1)*.18,marker=('o','s','^')[j],markersize=4,color=colors[j],linestyle='none')
                for j,axis in enumerate(axes):
                    axis.axvline(0,color='#555555',linewidth=.8,zorder=0);axis.grid(axis='x',color='#e4e7ea',linewidth=.6)
                    axis.set_ylim(len(subset)-.4,-.6);axis.ticklabel_format(axis='x',style='plain',useOffset=False)
                    axis.set_xticks(panel['xticks'][j]);axis.set_xlim(panel['xlimits'][j]);axis.tick_params(axis='x',labelsize=8)
                    assert list(axis.get_xlim())==panel['xlimits'][j]
                axes[0].set_yticks(range(len(subset)),labels=labels);axes[0].tick_params(axis='y',labelsize=9)
                axes[0].set_title('Observed 32-state mean gain',fontsize=9);axes[0].set_xlabel('Original cost units x 10^-6',fontsize=9)
                axes[1].set_title('Joint conditional 95% mean interval',fontsize=9);axes[1].set_xlabel('Original cost units x 10^-6',fontsize=9)
                axes[2].set_title('Added complete work, first 16 states',fontsize=9);axes[2].set_xlabel('Milliseconds per decision',fontsize=9)
                fig.legend(handles=[Line2D([0],[0],color=gray,linewidth=3,label='Raw independent interval'),Line2D([0],[0],color=blue,linewidth=1.7,label='Proof-supported intersection'),Line2D([0],[0],marker='o',color=orange,linewidth=0,label='Mean certified gain lower bound')],loc='lower left',bbox_to_anchor=(.025,.108),ncol=3,frameon=False,fontsize=8)
                fig.legend(handles=[Line2D([0],[0],marker=('o','s','^')[j],color=colors[j],linewidth=0,label=f'Clock {j}') for j in range(3)],loc='upper right',bbox_to_anchor=(.985,.896),ncol=3,frameon=False,fontsize=8)
                notes=["Gain is relative to the same actor's completed control; [k/32] counts accepted action changes. Every gain interval uses the same 32 independent state units.","All three original timing processes use the fixed first 16 states. Complete acquisition and shared charges are retained; common costs cancel only in paired differences.","Both parts retain their full 29-row panel's axis limits. Timing and gain intervals are separate displays and do not establish price-adjusted population or neural adoption."]
                for yy,note in zip((.08,.055,.03),notes):fig.text(.025,yy,note,fontsize=7.7)
                fig.canvas.draw();pages.savefig(fig)
                name=f'catalogue_risk{panel["index"]}_{service}_part{part}122.png';fig.savefig(out/name,dpi=140);plt.close(fig)
                pages_map.append({'pdf_page':len(pages_map)+1,'index':panel['index'],'service':service,'first_catalogue_row':begin+1,'last_catalogue_row':end,'keys':[dict(zip(fields,(x[f] for f in fields))) for x in subset],'xlimits':panel['xlimits'],'xticks':panel['xticks']})
    assert len(pages_map)==8 and sum(len(p['keys']) for p in pages_map)==116
    # Preserve exact input data bytes, not a floating-point reserialization.
    (out/'PLOTTED_COMPLETE_DATA122.json').write_bytes((src/'PLOTTED_COMPLETE_DATA122.json').read_bytes())
    assert sha(out/'PLOTTED_COMPLETE_DATA122.json')==bound['PLOTTED_COMPLETE_DATA122.json']['sha256']
    (out/'DISPLAY_PAGES122.json').write_text(json.dumps(pages_map,indent=2)+'\n')
    for name,b in bound.items():
        p=src/name;assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256']
    assert sha(src/'FIGURES_RECEIPT122.json')==source_receipt_sha
    receipt={'kind':'Complete same-data, same-scale eight-page author display','created_utc':datetime.now(timezone.utc).isoformat(),'source_figure_directory':str(src),'source_figure_receipt_sha256':sha(src/'FIGURES_RECEIPT122.json'),'source_data_sha256':bound['PLOTTED_COMPLETE_DATA122.json']['sha256'],'source_layout_sha256':bound['PANELS_LAYOUT122.json']['sha256'],'builder_sha256':sha(__file__),'all_contrasts':116,'all_original_timing_points':348,'fixed_split':[[0,14],[14,29]],'pages':8,'original_economic_queries':0,'new_population_observations':0,'new_service_clocks':0,'seconds':time.perf_counter()-start,'matplotlib_version':matplotlib.__version__,'cost_clock_components':[{'category':'reporting','clock_fields':[['seconds']],'scope':'Actual read-validation and eight-page rendering; no earlier figure stage, scientific execution, or semantic review is included.','partial_lower_bound_only':False,'overlaps_counted_parent':False}],'output_files':[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(out.iterdir()) if p.is_file()]}
    (out/'DISPLAY_RECEIPT122.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'receipt':str(out/'DISPLAY_RECEIPT122.json'),'sha256':sha(out/'DISPLAY_RECEIPT122.json'),'pages':8,'contrasts':116,'seconds':receipt['seconds']}))
if __name__=='__main__':main()
