# Final-study evaluator bug

The 30 authorized provider calls completed once each and all raw responses
were preserved. The collection runner then exposed contract/feature/Lane-1
stages but did not invoke the complete frozen structural matcher, generated
planner, policy-transfer, and regret evaluator. Consequently downstream fields
in `final_results.csv` are `NA` and must not be interpreted as measured
structural or decision results. Some rows also retain a default attribution
label despite provider success; this is a reporting defect, not a model
failure.

No protocol, prompt, reference, objective, or generated artifact was changed.
No calls were retried. The dataset is preserved for a separately reviewed
post-fix re-evaluation; these outputs are not promoted to paper aggregates.
