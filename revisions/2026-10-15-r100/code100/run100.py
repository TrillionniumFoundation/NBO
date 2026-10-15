"""Run the source-frozen study with the separately declared certified warm oracle."""
from __future__ import annotations
import sys,traceback,time
from pathlib import Path
from certified_oracle100 import WarmEconomy
import study100
study100.Economy=WarmEconomy
if __name__=='__main__':
    try:
        if len(sys.argv)>1 and sys.argv[1]=='test':
            import unittest,test100
            test100.Economy=WarmEconomy
            result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test100))
            raise SystemExit(not result.wasSuccessful())
        study100.main()
    except Exception:
        folder=Path(__file__).resolve().parents[1]/'results100';folder.mkdir(exist_ok=True)
        (folder/('failure-warm-'+str(time.time_ns())+'.log')).write_text(traceback.format_exc());raise
