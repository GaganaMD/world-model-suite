import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from event_log import emit, read_events
class LedgerTests(unittest.TestCase):
 def test_required_event_fields_and_append(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/"x.jsonl"; emit(p,"id","A","task_001"); emit(p,"id","B")
   events=read_events(p); self.assertEqual(len(events),2)
   for e in events: self.assertTrue({"timestamp","monotonic_timestamp","pid","ppid","execution_id","task_id","event_type"} <= e.keys())
