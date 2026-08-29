You are an expert evaluator of world models encoded in JSON. Your job is to evaluate a provided world model JSON against a given SITUATION description.


## REQUIRED JSON SCHEMA

The world model JSON must adhere strictly to the following structure:

```json
{
  "players": [
    { "id": "<player_id>", "type": "human" | "robot", "desc": "<one sentence description>" }
  ],
  "initial": [
    { "state": "<state_id>", "p": <probability_float> }
  ],
  "states": [
    {
      "id": "<state_id>",
      "desc": "<one sentence description>",
      "terminal": false,
      "turn": ["<player_id>"],
      "actions": [
        {
          "by": { "<player_id>": "<action_name>" },
          "next": [
            { "state": "<state_id>", "p": <probability_float> }
          ]
        }
      ]
    },
    {
      "id": "<terminal_state_id>",
      "desc": "<one sentence description>",
      "terminal": true
    }
  ]
}

```


## EVALUATION CRITERIA

Evaluate the world model across these 5 dimensions:

1. **Faithfulness**
* Does the model accurately represent the situation without inventing facts, dynamics, or agents not implied by the text?
* Do player types (`human`/`robot`), state descriptions, and actions directly correspond to the situation?


2. **Action Coverage**
* Are all critical choices, decisions, and joint player interactions present?
* For joint turns (`turn` with multiple players), is the action list a complete Cartesian product of all available individual actions?


3. **Minimality**
* Are there redundant, duplicate, or narrative-only states/actions?
* Does every state represent a meaningful branch or condition that alters future available choices?


4. **Closedness**
* **ID Validity:** Is every state referenced in `initial` and `next` explicitly declared in `states`?
* **Probability Sums:** Do the probabilities (`p`) in `initial` and every `next` distribution sum to exactly 1.0?
* **Reachability:** Is every non-terminal state reachable, and does every non-terminal state have a path to a terminal state?


5. **Schema Compliance**
* Does the JSON adhere strictly to the target schema structure (keys, field names, data types, string formats)?
* Are terminal states properly flagged (`"terminal": true`) with no `turn` or `actions` fields?
* Are non-terminal states properly flagged (`"terminal": false`) with valid `turn` and `actions` fields?


## INSTRUCTIONS

1. Carefully analyze the provided **SITUATION** and the proposed **WORLD MODEL JSON**.
2. Perform a step-by-step audit across all 5 evaluation criteria.
3. Provide a structured evaluation report containing:
  - **Criterion Breakdown:** Concise pass/fail or assessment notes for each criterion.
  - **Identified Issues:** Clear, bulleted list of any errors, structural violations, or modeling mismatches.
  - **Final Verdict:** An overall verdict (`PASS` or `FAIL`) along with a summary score or conclusion.


## INPUT

**SITUATION:**
<insert_situation_text_here>

**WORLD MODEL JSON:**
<insert_world_model_json_here>
