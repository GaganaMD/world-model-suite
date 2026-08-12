## Test Case C.13 (USA): HR Robot and an Anonymous Workplace Complaint

### LLM Input

An HR-support robot at a mid-size company in Chicago receives an anonymous digital complaint from an employee alleging that their manager has been assigning overtime disproportionately based on whether employees have young children. The complaint includes no supporting evidence and names the manager directly.

### Judging Criteria

**A good model should include:**
- the robot as the AI player
- the anonymous complainant as a stakeholder whose claim may reflect a real pattern, even without corroboration
- the named manager as a stakeholder whose reputation and livelihood are at stake in how the complaint is handled
- the company and its HR process as stakeholders with legal and procedural obligations
- employees broadly as stakeholders potentially affected by the alleged pattern
- actions spanning: log the complaint and escalate to a human HR officer, acknowledge receipt to the complainant (if a return channel exists), flag that the claim is unverified before any action involving the manager, or initiate a structured inquiry process
- the legal context (potential disparate-impact employment issue) acknowledged as a real frame — not invented detail, but a general feature of US employment law
- the unverified status of the complaint held as a central modeling constraint

**A good model should NOT include:**
- treating the complaint as verified and taking action against the manager
- treating the anonymous, unverified complaint as automatically dismissible
- inventing the complainant's identity, the manager's history, or the specific overtime data
- a resolved narrative in which the robot correctly handled or dismissed the complaint
