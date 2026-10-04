"""Standalone checks for the unfrozen presentation layer, not numerical tests."""
from decimal import Decimal
import json
import math
from pathlib import Path
import tempfile
import unittest

from report_publication_tables import ROOT, number, render, sha


class PresentationChecks(unittest.TestCase):
    def test_positive_negative_and_zero_boundary_enclosures(self):
        values=[.000530916,-.000530916,0.,-0.,1e-30,-1e-30,.125,-.125,
                math.nextafter(.000001,0.),math.nextafter(.000001,math.inf),
                math.nextafter(-.000001,0.),math.nextafter(-.000001,-math.inf)]
        for value in values:
            with self.subTest(value=value):
                lower,upper=Decimal(number(value,'lower')),Decimal(number(value,'upper'))
                self.assertLessEqual(lower,Decimal.from_float(value))
                self.assertGreaterEqual(upper,Decimal.from_float(value))
                self.assertLessEqual(upper-lower,Decimal('0.000001'))
        self.assertEqual(number(.000530916,'lower'),'0.000530')
        self.assertEqual(number(-.000530916,'lower'),'-0.000531')
        self.assertEqual(number(-0.,'upper'),'0.000000')
        self.assertEqual(number(.000530916),'0.000531')

    def test_nonfinite_and_invalid_direction_rejected(self):
        for value in [math.inf,-math.inf,math.nan]:
            with self.assertRaisesRegex(ValueError,'nonfinite'):number(value,'lower')
        with self.assertRaisesRegex(ValueError,'direction'):number(.1,'nearest')

    def fixture(self,base):
        p=json.loads((ROOT/'revisions/2026-10-04-r15/PROTOCOL.json').read_text())
        protocol=base/'PROTOCOL.json';protocol.write_text(json.dumps(p))
        evidence=base/'experiment';report_dir=evidence/'report';report_dir.mkdir(parents=True)
        methods=p['design']['methods'];names=methods+[a+'__minus__'+b for a,b in p['confirmation']['direct_contrasts']]
        conditional=[];means=[];attainment=[]
        for d in p['design']['dimensions']:
            for name in names:
                contrast='__minus__' in name
                lower,upper=(-.000020123,.000030987) if contrast else (.000530916,.002000605)
                for seed in p['design']['seeds']:
                    conditional.append({'dimension':d,'stream_seed':seed,'endpoint':name,'mean':.000002 if contrast else .00123,'lower':lower,'upper':upper})
                row={'dimension':d,'endpoint':name,'raw_mean':.000002 if contrast else .00123,'lower':lower,'upper':upper}
                if contrast:row['decision']={'practical_equivalence':True,'economically_material_superiority':False,'economically_material_inferiority':False}
                else:attainment.append({'dimension':d,'method':name,'target':p['stopping']['primary_certified_gain_target'],'definitely_attaining':16,'seed_count':16})
                means.append(row)
        data={'status':'complete','trial_count':128,'source_commit':'a'*40,'protocol_sha256':sha(protocol),
              'primitives_sha256':p['design']['primitives_sha256'],'confidence':{'event_count':238},
              'method_endpoints':means,'seed_endpoints':conditional,'attainment':attainment}
        report=report_dir/'REPORT.json';report.write_text(json.dumps(data))
        source=evidence/'SOURCE_MANIFEST.json';source.write_text(json.dumps({'numerical_source_commit':'a'*40,'protocol_sha256':sha(protocol),'primitives_sha256':p['design']['primitives_sha256']}))
        return protocol,report,source,data

    def test_full_238_event_fixture_keeps_inputs_and_all_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);protocol,report,source,data=self.fixture(base)
            before={p:sha(p) for p in [protocol,report,source]}
            out=base/'publication_tables';manifest=render(protocol,report,source,out)
            self.assertEqual([x['rows'] for x in manifest['tables'].values()],[8,6,224])
            self.assertEqual(manifest['represented_events'],238)
            self.assertEqual(manifest['confidence_alpha_added'],0.)
            self.assertFalse(manifest['numerical_decisions_changed'])
            text=(out/'table_method_summary.tex').read_text()
            self.assertIn('0.000530 & 0.002001',text)
            self.assertIn('Equivalent',(out/'table_method_comparisons.tex').read_text())
            self.assertEqual(before,{p:sha(p) for p in before})
            with self.assertRaisesRegex(ValueError,'immutable numerical evidence'):
                render(protocol,report,source,report.parent/'changed')

    def test_missing_stream_and_changed_decision_cannot_be_rendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);protocol,report,source,data=self.fixture(base)
            saved=data['seed_endpoints'].pop();report.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'stream endpoint'):
                render(protocol,report,source,base/'presentation')
            data['seed_endpoints'].append(saved)
            next(x for x in data['method_endpoints'] if 'decision' in x)['decision']['practical_equivalence']=False
            report.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'unrounded endpoint rule'):
                render(protocol,report,source,base/'presentation')


if __name__=='__main__':unittest.main()
