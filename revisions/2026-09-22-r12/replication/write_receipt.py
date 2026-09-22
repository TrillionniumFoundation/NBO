"""Separate source, execution, build, and review identities without a self-hash."""
import argparse,hashlib,json,os
import price_envelope as e
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--result',required=True);p.add_argument('--build');a=p.parse_args()
paths=[e.ROOT/'ECTA_R12.pdf',e.ROOT/'SUPP_R12.pdf',e.REV/'results/envelope.json',e.REV/'ci_results/status.json',e.REV/'validation_report.json']
r={'manuscript':'Neural Bellman Operators, R12','base_commit':'85e27ad0c9cdcb68645d62788e1fad2f59ea1a48','review_input_commit':'251ad29668788b2a911c4ca6f9c0a226886518d6','review_input_blob':'42cee0954515e5578dc579a4ca0428bb4e399b2e','manuscript_source_commit':a.source,'independent_result_commit':a.result,'manuscript_build_commit':a.build,'workflow_run':os.environ.get('GITHUB_RUN_ID'),'files':{str(p.relative_to(e.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()},'local_execution':'Adaptive case records deliberately retain local-development labels; they are archived inputs, not fictitiously preregistered experiments. The pinned clean-checkout reexecution validates every frozen policy and dual.','note':'Receipt is committed after the PDF build and intentionally does not include its own commit hash.'}
e.dump(e.REV/'publication_receipt.json',r)
