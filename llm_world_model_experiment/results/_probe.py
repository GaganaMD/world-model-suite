
import importlib.util, json, sys
path, actions = sys.argv[1], list(sys.argv[2])
spec = importlib.util.spec_from_file_location("generated_task", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
w = mod.GridWorld()
out = {
    "reset": list(w.reset()),
    "run_final": list(w.run(actions)),
    "is_goal_after_run": bool(w.is_goal()),
    "reachable": bool(w.reachable()),
    "shortest_path": w.shortest_path(),
}
checks = []
for a in ["N", "S", "E", "W"]:
    w.reset()
    checks.append([a, list(w.step(a))])
out["single_steps"] = checks
print(json.dumps(out, sort_keys=True))
