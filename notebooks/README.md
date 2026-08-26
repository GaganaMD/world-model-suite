# notebooks

| Notebook | What it does |
| --- | --- |
| cultural_qwen_evaluation.ipynb | **Cultural-track full evaluation with Qwen/Qwen2.5-VL-72B-Instruct.** Generates a world model for each of the 14 cultural cases (C1-C14) - from both data/Test_Cases/04_cultural and the location-stripped cultural_without_loc bank - then runs the repo's full pipeline (Lane 0/1/3 + WorldModelEDA + heatmaps) on each and compares the two banks to confirm the same level of expected output is reached with or without the place name. Rebuilt with python build_qwen_cultural_notebook.py. |
