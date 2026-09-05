import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SCRIPTS=ROOT/"scripts"
def run(mode, d):
 cmd=[sys.executable,str(SCRIPTS/"run_baseline.py"),"--mode",mode,"--execution-id","run","--results-root",str(d/"results")]
 subprocess.run(cmd,check=True,timeout=10,stdout=subprocess.DEVNULL)
 return json.loads((d/"results"/"run"/"summary.json").read_text())
class SupervisionTests(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.d=Path(self.tmp.name); (self.d/"results").mkdir()
 def tearDown(self): self.tmp.cleanup()
 def test_baseline_completes_normally(self):
  s=run("normal",self.d); self.assertEqual(s["provider_received_actions"],30); self.assertEqual(s["persisted_responses"],30)
 def test_fail_open_survives_and_actions_continue(self):
  s=run("fail-open",self.d); self.assertTrue(s["alive_descendants_after_controller_return"]); self.assertGreater(s["post_controller_requests"],0)
  self.assertLess(s["provider_received_actions"],s["planned_actions"]) # watchdog bounds the orphan
  ledger=(self.d/"results"/"run"/"worker_events.jsonl").read_text()
  self.assertIn('"WATCHDOG_STOP"',ledger)
 def test_inflight_provider_local_distinction(self):
  s=run("in-flight",self.d); self.assertGreaterEqual(s["unmatched_provider_requests"],1)
 def test_controlled_revocation_is_fail_closed(self):
  cmd=[sys.executable,str(SCRIPTS/"run_controlled_shutdown.py"),"--execution-id","run","--results-root",str(self.d/"results")]
  subprocess.run(cmd,check=True,timeout=10,stdout=subprocess.DEVNULL); s=json.loads((self.d/"results"/"run"/"summary.json").read_text())
  self.assertTrue(s["revocation_acknowledged"]); self.assertEqual(s["post_stop_requests"],0); self.assertEqual(s["provider_received_actions"],9)
