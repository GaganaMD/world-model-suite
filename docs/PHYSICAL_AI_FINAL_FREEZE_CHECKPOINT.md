# Physical-AI final freeze checkpoint

- Scenario definitions: **frozen** (P1–P5; P4b objective unchanged).
- External objectives: **frozen** and evaluated outside generated rewards.
- Prompts/contracts: **frozen**; shared scaffold and canonical features.
- Shared contract prompt hash is recorded in `final_study/prompts/`; each
  rendered scenario prompt must be hashed into its immutable call manifest
  before dispatch.
- Structural matcher, eligibility, transfer, Q-values, and regret: **frozen**.
- Reproduction: P4b calibration, preserved-pilot decomposition, and full test
  suite pass; key values reproduce (`p*=2/9`, reference `.6`, GPT regret
  `.375`, Claude regret `.375`).
- Hosted calls: **none**.
- Pilot/debug samples: excluded from final aggregates.
- Clean final call count: **30** (5 × 3 × 2).
- Protocol status: ready for final hosted generation; authorization is still a
  separate decision.
