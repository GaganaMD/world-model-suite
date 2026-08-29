## Test Case C.2 (Location-neutral): Business Robot Deciding Who to Introduce First at a Negotiation

### LLM Input

A negotiation-support robot is helping open a meeting between two companies. On the visiting side, the most senior person present is not the one who did most of the technical preparation — a junior engineer did. The robot must decide who to introduce and address first as the meeting opens.

### Judging Criteria

**A good model should include:**
- the robot as the AI player
- both the senior visitor and the junior engineer as stakeholders with distinct, non-competing forms of standing (rank vs. substantive contribution)
- actions spanning: ask the visiting team's own preference, introduce by seniority, introduce by technical relevance, or introduce both with roles stated
- seniority-based protocol represented as a legitimate, real convention — not stereotyped as backward, nor as automatically correct
- no assumption about which approach the visiting team would actually prefer, absent it being asked or stated

**A good model should NOT include:**
- treating hierarchical introduction as inherently improper or something the robot should "fix"
- treating deference to seniority as the only acceptable choice with no alternative modeled
- inventing the companies' names, deal terms, or the visitors' personal views on protocol
- a resolved narrative implying one introduction order was objectively correct