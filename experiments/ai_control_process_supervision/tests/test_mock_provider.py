import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mock_provider import invoke
from event_log import read_events
class MockProviderTests(unittest.TestCase):
 def test_local_provider_records_receive_and_response(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp); self.assertEqual(invoke(d,"t","task_001",.001)["response"],"local-mock-response")
   self.assertEqual([x["event_type"] for x in read_events(d/"provider_events.jsonl")],["PROVIDER_RECEIVED","PROVIDER_RESPONSE"])
 def test_no_network_dependency(self):
  self.assertNotIn("requests", Path(__file__).resolve().parents[1].joinpath("src/mock_provider.py").read_text())
