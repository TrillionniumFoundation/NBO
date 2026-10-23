"""Render the exact R126 author response map; no economic computation."""
from pathlib import Path
import json
import re
ROOT=Path(__file__).resolve().parents[1]

def latex_plain(text):
    table={'\\':r'\textbackslash{}','{':r'\{','}':r'\}','_':r'\_','#':r'\#','$':r'\$','%':r'\%','&':r'\&','^':r'\textasciicircum{}','~':r'\textasciitilde{}','<':r'\textless{}','>':r'\textgreater{}'}
    return ''.join(table.get(c,c) for c in text).replace('α',r'\(\alpha\)').replace('→',r'\(\rightarrow\)')

def latex(text):
    # Breakable URLs/hashes retain the original visible quotation text.
    pattern=r'https?://[^\s{}<>]+|\b(?:[0-9a-f]{64}|[0-9a-f]{40})\b'
    pieces=[];position=0
    for match in re.finditer(pattern,text,flags=re.IGNORECASE):
        pieces.append(latex_plain(text[position:match.start()]))
        pieces.append(r'\nolinkurl{'+match.group(0)+'}')
        position=match.end()
    pieces.append(latex_plain(text[position:]))
    return ''.join(pieces)

def human_status(text):
    text=text.replace('_',' ').replace('; ', '; ').strip()
    return text[0].upper()+text[1:] if text else text

def render():
    data=json.loads((ROOT/'response_inputs/RESPONSE_MAP126.json').read_text())
    intro=('This is an author revision of Neural Bellman Operators for the Econometrica numerical-methods objective. '
      'The controlling owner-commissioned advisory report is R97 at '+data['controlling_report_commit']+'. '
      'It is an advisory on the named source, not an Econometric Society editorial decision. It reviewed manuscript '+data['reviewed_manuscript_commit']+', not the subsequent author revisions. '
      'The current source baseline is the complete R125 author package at '+data['baseline_author_commit']+'. The actual published R126 scientific boundary is '+data['scientific_source_commit']+', with immutable readback before new economics. '
      'The original Bellman objective, continuation critics, feasible actors and economic research identity remain central. '
      'Each response separates the inherited amendment, current author action, actual evidence status and remaining scientific requirement. '
      'No source audit, smaller fitting residual or unchanged conventional winner is treated as completion of the research objective.')
    md=['# Response to the controlling referee advisory — R126 author revision','',intro,'',
        '**Response map status:** '+human_status(data['status']).rstrip('.')+'.','',data['historical_response_scope'],'']
    tex=[r'\section*{Response to the controlling referee advisory}',r'\label{sec:response126}',latex(intro),'',
         r'\paragraph{Response map status.} '+latex(human_status(data['status']).rstrip('.'))+'.','',latex(data['historical_response_scope']),'']
    if data.get('execution_overview'):
        md += [data['execution_overview'],'']
        tex += [latex(data['execution_overview']),'']
    if data.get('additional_experiment'):
        note=data['additional_experiment']['name']+' (source '+data['additional_experiment']['source_commit']+'): '+human_status(data['additional_experiment']['status']).rstrip('.')+'. '+data['additional_experiment']['scope']
        md += ['**Separately identified follow-up episode.** '+note,'']
        tex += [r'\paragraph{Separately identified follow-up episode.} '+latex(note),'']
    for row in data['records']:
        md+=['## '+row['title'],'','**Original request.** '+row['exact_original_request'],'',
             '**Inherited R125 amendment.** '+row['inherited_r125_amendment'],'',
             '**Current R126 author action.** '+row['r126_author_action'],'',
             '**Evidence status.** '+human_status(row['evidence_status']).rstrip('.')+'.','']
        tex += [r'\subsection*{'+latex(row['title'])+'}',r'\paragraph{Original request.} '+latex(row['exact_original_request']),'',
                r'\paragraph{Inherited R125 amendment.} '+latex(row['inherited_r125_amendment']),'',
                r'\paragraph{Current R126 author action.} '+latex(row['r126_author_action']),'',
                r'\paragraph{Evidence status.} '+latex(human_status(row['evidence_status']).rstrip('.'))+'.','']
        for evidence in row['r126_execution_evidence']:
            line=evidence if isinstance(evidence,str) else json.dumps(evidence,sort_keys=True)
            md+=['- '+line];tex+=[latex(line)+r'\par']
        for tag in row['pending_evidence_tags']:
            md+=['['+tag+']'];tex+=[r'\textbf{'+latex('['+tag+']')+'}'+r'\par']
        md+=['','**Remaining scientific requirement.** '+row['r126_remaining_scientific_requirement'],'']
        tex+=['',r'\paragraph{Remaining scientific requirement.} '+latex(row['r126_remaining_scientific_requirement']),'']
        if row['routes']:
            md+=['**Source routes:** '+', '.join('`'+x+'`' for x in row['routes'])+'.','']
            tex+=[r'\paragraph{Source routes.} '+', '.join(r'\nolinkurl{'+x+'}' for x in row['routes'])+'.','']
    (ROOT/'response126.md').write_text('\n'.join(md)+'\n')
    (ROOT/'new126/response126.tex').write_text('\n'.join(tex)+'\n')
    print('rendered',len(data['records']),'exact requests; pending tags',sum(len(r['pending_evidence_tags']) for r in data['records']))

if __name__=='__main__':render()
