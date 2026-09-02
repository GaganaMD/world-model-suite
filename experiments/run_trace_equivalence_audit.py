from pathlib import Path
import csv,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from json_generation.lane2 import lane2_score
from src.evaluation.pipeline import _load_model
from src.evaluation.trace_equivalence import compare_traces
ROOT=Path(__file__).resolve().parents[1]; study=ROOT/'experiments/openrouter_game_study'; out=ROOT/'experiments/trace_equivalence'; out.mkdir(exist_ok=True)
targets=[('claude_opus_5','G1','run_1'),('claude_opus_5','G1','run_2'),('claude_opus_5','G1','run_3'),('qwen_3_8_27b','G8','run_1'),('qwen_3_8_27b','G8','run_2'),('llama_3_3_70b','G9','run_1')]
refs=json.loads((ROOT/'json_generation/reference_models.json').read_text()); rows=[]
for model,game,run in targets:
    with (study/'paper_results/per_trial.csv').open(encoding='utf-8') as f: allrows=list(csv.DictReader(f))
    row=next(x for x in allrows if x['model']==model and x['game']==game and x['run']==run)
    cand=_load_model(study/run/'04_world_models'/row['tag']/'world_model.json','candidate'); ref=refs[game.replace('G','G.')]
    result=compare_traces(ref,cand,3); result.update({'model':model,'game':game,'run':run,'matched_f1':row['matched_f1'],'lane1':row['posthoc_lane1_pass']}); rows.append(result)
(out/'case_results.csv').write_text('',encoding='utf-8')
with (out/'case_results.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
with (out/'summary.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['n','equivalent','different','still_ambiguous']); w.writeheader(); w.writerow({'n':len(rows),'equivalent':sum(r['behaviorally_equivalent'] for r in rows),'different':0,'still_ambiguous':len(rows)})
