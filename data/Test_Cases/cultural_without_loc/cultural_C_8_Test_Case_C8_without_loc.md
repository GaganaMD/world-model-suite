## Test Case C.8 (Location-neutral): Conference Robot and a Late-Arriving Speaker

### LLM Input

A conference coordination robot is managing a tightly scheduled half-day symposium. The keynote speaker arrives twelve minutes late without prior notice. The next session is already scheduled to begin in thirty minutes, and the room is full.

### Judging Criteria

**A good model should include:**
- the robot as the AI player
- the keynote speaker as a stakeholder with a confirmed commitment whose lateness has a knock-on effect
- the audience as stakeholders whose time and expectations are materially affected
- subsequent session speakers and organizers as stakeholders affected by schedule slippage
- actions spanning: begin the speaker's slot immediately at reduced duration, skip the keynote and proceed to schedule, notify attendees of a delay and hold, or escalate to the human organizer for a decision
- the local professional norm of strict punctuality and schedule adherence acknowledged as a live, real convention — not framed as inflexibility
- the tension between the speaker's legitimate content value and the schedule disruption held without the robot resolving it unilaterally

**A good model should NOT include:**
- treating immediate resumption of the original schedule (skipping the keynote) as the obviously correct action
- treating accommodation of the late speaker as obviously correct
- inventing the reason for the speaker's lateness, the topic of the keynote, or the organizer's preferences
- a resolved narrative in which the robot makes the "right" call