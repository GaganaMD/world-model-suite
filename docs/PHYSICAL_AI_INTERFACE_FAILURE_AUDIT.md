# Physical-AI interface failure audit

All six responses returned a class named `GeneratedPOSG`, but the failures were
systematic interface mismatches rather than parser or provider failures.

| Model/runs | Inheritance | Methods/signatures observed | Primary failure | Preventable by scaffold? |
|---|---|---|---|---|
| GPT-5.6 Sol (2) | `AbstractPOSG` | omitted `players`, `legal_actions`, `observation`; used `actions` instead of `joint_action` | abstract/method contract failure | yes |
| Claude Opus 5 (2) | `AbstractPOSG` | extra framework methods; omitted `legal_actions`; wrong `transition`, `observation`, `reward`; missing `@property` | contract complexity/ignored exact API | yes |
| Llama 3.3 70B (2) | no base class | omitted most required methods; used `action`/`get_actions`/`get_initial_state` | framework boilerplate failure | yes |

The old prompt named the class, base class, and broad interface intent, but it
did not enumerate every required signature or provide a fill-in skeleton. It
also did not explicitly forbid extra framework APIs or require a pre-output
signature checklist. No parser defect or evaluator defect was found.

The six raw files remain unchanged. Counterfactually, a scaffold supplying the
abstract methods and exact argument names would have prevented every observed
interface error; semantic transition correctness remains unknown and is not
retroactively credited.
