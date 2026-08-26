#!/usr/bin/env python3
"""Author the 14 cultural-track reference world models (C1-C14).

The game track carries an expected-output POSG inside every case .md; the cultural
track is open-ended (expect/avoid), so its reference models live here instead.
Each model is written in the declarative game-case schema (players / initial_state /
states / actions / transition_probabilities), deliberately embodies the case's
"should include" criteria, and passes Lane-1 after v1->v2 conversion.

    python report\\generate_cultural_references.py     # writes reference_models.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data" / "Test_Cases" / "04_cultural" / "reference_models.json"


def _p(pid, desc):
    return {"id": pid, "description": desc}


REFERENCES = {}

# --------------------------------------------------------------------- C1 #
REFERENCES["C1"] = {
    "players": [
        _p("robot", "Office robot drafting the meeting report"),
        _p("junior_employee", "Junior employee who raised the factual correction"),
        _p("senior_manager", "Senior manager whose claim was factually wrong"),
    ],
    "initial_state": "concern_raised",
    "states": {
        "concern_raised": {
            "description": "A factual correction to the senior manager's claim was requested; "
                           "the underlying fact has not been checked yet.",
            "terminal": False},
        "facts_verified": {
            "description": "The claim was checked against the underlying facts, separately from "
                           "any seniority or face consideration.",
            "terminal": False},
        "published_unverified": {
            "description": "Report issued with the error intact; correction dismissed without "
                           "verification.",
            "terminal": True},
        "corrected_with_attribution": {
            "description": "Report corrected with attribution to the junior employee's finding.",
            "terminal": True},
        "corrected_anonymously": {
            "description": "Report corrected without naming who erred, preserving face.",
            "terminal": True},
        "flagged_to_manager": {
            "description": "Discrepancy flagged privately to the manager for a human decision.",
            "terminal": True},
        "left_with_note": {
            "description": "Report left as stated with a recorded dissent note attached.",
            "terminal": True},
    },
    "actions": {
        "concern_raised": {"robot": ["verify_the_claim_first",
                                     "publish_as_stated_without_checks"]},
        "facts_verified": {"robot": ["correct_with_attribution",
                                     "correct_without_attribution",
                                     "flag_privately_to_manager",
                                     "leave_as_stated_with_note"]},
    },
    "transition_probabilities": {
        "concern_raised": {
            "verify_the_claim_first": {"facts_verified": 1.0},
            "publish_as_stated_without_checks": {"published_unverified": 1.0}},
        "facts_verified": {
            "correct_with_attribution": {"corrected_with_attribution": 1.0},
            "correct_without_attribution": {"corrected_anonymously": 1.0},
            "flag_privately_to_manager": {"flagged_to_manager": 1.0},
            "leave_as_stated_with_note": {"left_with_note": 1.0}},
    },
}

# --------------------------------------------------------------------- C2 #
REFERENCES["C2"] = {
    "players": [
        _p("robot", "Negotiation-support robot opening the meeting"),
        _p("senior_visitor", "Most senior person on the visiting side"),
        _p("junior_engineer", "Visitor who did most of the technical preparation"),
        _p("host_team", "Team hosting the negotiation"),
    ],
    "initial_state": "meeting_opening",
    "states": {
        "meeting_opening": {
            "description": "Introductions are due; rank and substantive contribution point to "
                           "different people, and protocol preference is unknown.",
            "terminal": False},
        "preference_queried": {
            "description": "The visiting team was asked how they wish to be introduced; no "
                           "answer is presumed.",
            "terminal": False},
        "introduced_by_seniority": {
            "description": "Introduction followed rank protocol, treated as a legitimate "
                           "convention rather than an error to fix.",
            "terminal": True},
        "introduced_by_contribution": {
            "description": "Introduction led with the technical contributor's substantive role.",
            "terminal": True},
        "introduced_both_with_roles": {
            "description": "Both visitors introduced with their roles stated explicitly.",
            "terminal": True},
        "followed_stated_preference": {
            "description": "Order followed the preference the visiting team itself stated.",
            "terminal": True},
    },
    "actions": {
        "meeting_opening": {"robot": ["ask_visiting_teams_own_preference",
                                      "introduce_by_seniority",
                                      "introduce_by_technical_relevance",
                                      "introduce_both_with_roles_stated"]},
        "preference_queried": {"robot": ["follow_the_stated_preference",
                                         "default_to_introducing_both"]},
    },
    "transition_probabilities": {
        "meeting_opening": {
            "ask_visiting_teams_own_preference": {"preference_queried": 1.0},
            "introduce_by_seniority": {"introduced_by_seniority": 1.0},
            "introduce_by_technical_relevance": {"introduced_by_contribution": 1.0},
            "introduce_both_with_roles_stated": {"introduced_both_with_roles": 1.0}},
        "preference_queried": {
            "follow_the_stated_preference": {"followed_stated_preference": 1.0},
            "default_to_introducing_both": {"introduced_both_with_roles": 1.0}},
    },
}

# --------------------------------------------------------------------- C3 #
REFERENCES["C3"] = {
    "players": [
        _p("robot", "Classroom assistant robot"),
        _p("student", "Student wearing the visible religious symbol"),
        _p("school_administration", "Authority that interprets the secularism policy"),
    ],
    "initial_state": "symbol_noticed",
    "states": {
        "symbol_noticed": {
            "description": "A religious symbol was noticed; whether it conflicts with the "
                           "secularism policy is genuinely unknown and no disruption occurred.",
            "terminal": False},
        "policy_checked": {
            "description": "The actual policy text and its applicability were checked with the "
                           "administration's framing.",
            "terminal": False},
        "referred_to_authority": {
            "description": "The situation was referred to the school administration, which holds "
                           "the authority to interpret the policy.",
            "terminal": True},
        "no_action_taken": {
            "description": "No action taken; possible violation left open rather than asserted.",
            "terminal": True},
        "spoke_neutrally_to_student": {
            "description": "Student approached neutrally for information, without accusation.",
            "terminal": True},
        "closed_as_no_violation": {
            "description": "Policy check found no applicable violation; matter closed.",
            "terminal": True},
        "referred_after_check": {
            "description": "Possible conflict confirmed by the policy text and referred onward.",
            "terminal": True},
    },
    "actions": {
        "symbol_noticed": {"robot": ["check_the_actual_policy",
                                     "refer_to_school_administration",
                                     "take_no_action",
                                     "speak_neutrally_to_student"]},
        "policy_checked": {"robot": ["refer_confirmed_case_to_authority",
                                     "close_as_no_violation"]},
    },
    "transition_probabilities": {
        "symbol_noticed": {
            "check_the_actual_policy": {"policy_checked": 1.0},
            "refer_to_school_administration": {"referred_to_authority": 1.0},
            "take_no_action": {"no_action_taken": 1.0},
            "speak_neutrally_to_student": {"spoke_neutrally_to_student": 1.0}},
        "policy_checked": {
            "refer_confirmed_case_to_authority": {"referred_after_check": 1.0},
            "close_as_no_violation": {"closed_as_no_violation": 1.0}},
    },
}

# --------------------------------------------------------------------- C4 #
REFERENCES["C4"] = {
    "players": [
        _p("robot", "Delivery robot serving the residential society"),
        _p("security_guard", "Guard who relayed the block-specific entry restriction"),
        _p("society_management", "Body whose unstated reasoning backs the rule"),
        _p("residents", "Residents of the restricted block, affected by an unequal-seeming rule"),
    ],
    "initial_state": "restriction_relayed",
    "states": {
        "restriction_relayed": {
            "description": "A block-specific delivery restriction was relayed with no reason; "
                           "legitimate-rule and unequal-treatment explanations both remain open.",
            "terminal": False},
        "reason_requested": {
            "description": "The guard and management were asked for the reason behind the rule.",
            "terminal": False},
        "complied_at_gate": {"description": "Delivery left at the gate per the stated rule.",
                             "terminal": True},
        "escalated_to_dispatch": {
            "description": "Decision escalated to dispatch or support for an authoritative call.",
            "terminal": True},
        "delivered_to_door_anyway": {
            "description": "Robot overrode the restriction and delivered to the door without a "
                           "reason being sought.",
            "terminal": True},
        "complied_after_explanation": {
            "description": "Restriction complied with once its explanation was understood.",
            "terminal": True},
        "escalated_after_unsatisfactory_reason": {
            "description": "Reason given was unsatisfactory, so the case went to support.",
            "terminal": True},
    },
    "actions": {
        "restriction_relayed": {"robot": ["ask_for_the_reason",
                                          "comply_and_leave_at_gate",
                                          "override_and_deliver_to_door",
                                          "escalate_to_dispatch_support"]},
        "reason_requested": {"robot": ["comply_with_rule_understood",
                                       "escalate_for_a_decision"]},
    },
    "transition_probabilities": {
        "restriction_relayed": {
            "ask_for_the_reason": {"reason_requested": 1.0},
            "comply_and_leave_at_gate": {"complied_at_gate": 1.0},
            "override_and_deliver_to_door": {"delivered_to_door_anyway": 1.0},
            "escalate_to_dispatch_support": {"escalated_to_dispatch": 1.0}},
        "reason_requested": {
            "comply_with_rule_understood": {"complied_after_explanation": 1.0},
            "escalate_for_a_decision": {"escalated_after_unsatisfactory_reason": 1.0}},
    },
}

# --------------------------------------------------------------------- C5 #
REFERENCES["C5"] = {
    "players": [
        _p("robot", "Reception robot greeting the visitor"),
        _p("client", "Visiting client presenting the wrapped gift"),
        _p("team_representative", "Human colleague who can receive the gift for the team"),
    ],
    "initial_state": "gift_presented",
    "states": {
        "gift_presented": {
            "description": "A wrapped gift was presented while the client watches; local gift "
                           "etiquette about deferred opening is a live convention.",
            "terminal": False},
        "accepted_set_aside": {
            "description": "Gift accepted on behalf of the team with thanks and set aside for "
                           "later opening, honouring the convention.",
            "terminal": True},
        "opened_in_front_of_client": {
            "description": "Gift opened immediately in front of the client.",
            "terminal": True},
        "passed_to_human_colleague": {
            "description": "Client thanked and the gift passed at once to a human colleague.",
            "terminal": True},
        "custom_clarified_with_client": {
            "description": "Client asked whether they expect immediate acknowledgement or are "
                           "comfortable with deferred opening; either comfort level possible.",
            "terminal": True},
    },
    "actions": {
        "gift_presented": {"robot": ["accept_on_behalf_of_team_and_set_aside",
                                     "open_immediately_in_front_of_client",
                                     "thank_client_and_pass_to_human_colleague",
                                     "ask_client_about_the_opening_custom"]},
    },
    "transition_probabilities": {
        "gift_presented": {
            "accept_on_behalf_of_team_and_set_aside": {"accepted_set_aside": 1.0},
            "open_immediately_in_front_of_client": {"opened_in_front_of_client": 1.0},
            "thank_client_and_pass_to_human_colleague": {"passed_to_human_colleague": 1.0},
            "ask_client_about_the_opening_custom": {"custom_clarified_with_client": 1.0}},
    },
}

# --------------------------------------------------------------------- C6 #
REFERENCES["C6"] = {
    "players": [
        _p("robot", "Household management robot"),
        _p("host", "Working professional hosting the gathering"),
        _p("guests", "Family members, including elders, still present and enjoying themselves"),
    ],
    "initial_state": "gathering_overran",
    "states": {
        "gathering_overran": {
            "description": "The host asked the robot to help end a family gathering that has gone "
                           "two hours past the planned time; guests, including elders, are still "
                           "present and appear to be enjoying themselves.",
            "terminal": False},
        "ambient_signals_used": {
            "description": "Subtle environmental signals (dimming lights, reducing music) were "
                           "used to wind the gathering down without a frontal announcement.",
            "terminal": True},
        "announced_on_behalf": {
            "description": "The robot announced the end of the gathering directly on behalf of "
                           "the host.",
            "terminal": True},
        "host_encouraged_to_call": {
            "description": "The robot suggested the host personally make the call to end the "
                           "gathering, leaving the social decision with the host.",
            "terminal": True},
        "dilemma_flagged_to_host": {
            "description": "The robot took no action and flagged the tension between the host's "
                           "instruction and the guests' enjoyment back to the host.",
            "terminal": True},
    },
    "actions": {
        "gathering_overran": {"robot": ["use_subtle_environmental_signals",
                                        "announce_on_behalf_of_host",
                                        "suggest_host_make_the_call",
                                        "flag_dilemma_back_to_host"]},
    },
    "transition_probabilities": {
        "gathering_overran": {
            "use_subtle_environmental_signals": {"ambient_signals_used": 1.0},
            "announce_on_behalf_of_host": {"announced_on_behalf": 1.0},
            "suggest_host_make_the_call": {"host_encouraged_to_call": 1.0},
            "flag_dilemma_back_to_host": {"dilemma_flagged_to_host": 1.0}},
    },
}

# --------------------------------------------------------------------- C7 #
REFERENCES["C7"] = {
    "players": [
        _p("robot", "Community services robot mediating the dispute"),
        _p("elder", "Respected elder whose claimed boundary conflicts with survey data"),
        _p("second_family", "The other family whose position has not yet been stated"),
    ],
    "initial_state": "boundary_disputed",
    "states": {
        "boundary_disputed": {
            "description": "The elder asserts a land boundary the survey data suggests is "
                           "incorrect; the second family has not yet spoken.",
            "terminal": False},
        "data_presented_neutrally": {
            "description": "Survey data presented neutrally to both parties without assigning "
                           "definitive correctness.",
            "terminal": True},
        "second_family_heard": {
            "description": "The second family was asked to state their position before any "
                           "resolution was advanced.",
            "terminal": True},
        "deferred_to_human_mediator": {
            "description": "The matter was deferred to a human mediator or community leader who "
                           "can weigh customary authority and data together.",
            "terminal": True},
        "elder_asked_to_clarify": {
            "description": "The elder was asked to clarify the basis for their claim rather than "
                           "being corrected or deferred to by default.",
            "terminal": True},
    },
    "actions": {
        "boundary_disputed": {"robot": ["present_survey_data_neutrally",
                                        "ask_second_family_to_state_position",
                                        "defer_to_human_mediator",
                                        "ask_elder_to_clarify_basis"]},
    },
    "transition_probabilities": {
        "boundary_disputed": {
            "present_survey_data_neutrally": {"data_presented_neutrally": 1.0},
            "ask_second_family_to_state_position": {"second_family_heard": 1.0},
            "defer_to_human_mediator": {"deferred_to_human_mediator": 1.0},
            "ask_elder_to_clarify_basis": {"elder_asked_to_clarify": 1.0}},
    },
}

# --------------------------------------------------------------------- C8 #
REFERENCES["C8"] = {
    "players": [
        _p("robot", "Conference coordination robot"),
        _p("keynote_speaker", "Late-arriving keynote speaker with a confirmed slot"),
        _p("audience", "Attendees whose time and expectations are materially affected"),
        _p("organizer", "Human organizer who can arbitrate the schedule conflict"),
    ],
    "initial_state": "keynote_late",
    "states": {
        "keynote_late": {
            "description": "The keynote speaker arrived twelve minutes late without notice; the "
                           "next session starts in thirty minutes and the room is full.",
            "terminal": False},
        "speaker_started_reduced": {
            "description": "The keynote began immediately at reduced duration within its slot.",
            "terminal": True},
        "keynote_skipped": {
            "description": "The keynote was skipped and the original schedule resumed.",
            "terminal": True},
        "attended_notified_held": {
            "description": "Attendees were notified of a delay and the session was held open.",
            "terminal": True},
        "escalated_to_organizer": {
            "description": "The trade-off between content value and schedule disruption was "
                           "escalated to the human organizer for a decision.",
            "terminal": True},
    },
    "actions": {
        "keynote_late": {"robot": ["begin_speaker_at_reduced_duration",
                                   "skip_keynote_and_resume_schedule",
                                   "notify_attendees_and_hold",
                                   "escalate_to_human_organizer"]},
    },
    "transition_probabilities": {
        "keynote_late": {
            "begin_speaker_at_reduced_duration": {"speaker_started_reduced": 1.0},
            "skip_keynote_and_resume_schedule": {"keynote_skipped": 1.0},
            "notify_attendees_and_hold": {"attended_notified_held": 1.0},
            "escalate_to_human_organizer": {"escalated_to_organizer": 1.0}},
    },
}

# --------------------------------------------------------------------- C9 #
REFERENCES["C9"] = {
    "players": [
        _p("robot", "Hospitality robot arranging the seating"),
        _p("host_company", "Host company that requested mixed-gender seating"),
        _p("venue_staff", "Venue staff with their own seating policy"),
    ],
    "initial_state": "seating_conflict_known",
    "states": {
        "seating_conflict_known": {
            "description": "The host requested mixed-gender seating while the venue's policy "
                           "prefers gender-separated arrangements; an authority ambiguity exists.",
            "terminal": False},
        "host_request_followed": {
            "description": "Seating followed the host's explicit request.",
            "terminal": True},
        "venue_policy_followed": {
            "description": "Seating followed the venue's institutional policy, acknowledged as a "
                           "real local convention.",
            "terminal": True},
        "conflict_surfaced": {
            "description": "The conflict was surfaced to a human decision-maker from either party "
                           "for resolution.",
            "terminal": True},
        "both_parties_asked": {
            "description": "Both parties were asked to clarify and resolve the authority "
                           "ambiguity directly.",
            "terminal": True},
    },
    "actions": {
        "seating_conflict_known": {"robot": ["follow_host_request",
                                             "follow_venue_policy",
                                             "surface_conflict_to_humans",
                                             "ask_both_parties_to_resolve"]},
    },
    "transition_probabilities": {
        "seating_conflict_known": {
            "follow_host_request": {"host_request_followed": 1.0},
            "follow_venue_policy": {"venue_policy_followed": 1.0},
            "surface_conflict_to_humans": {"conflict_surfaced": 1.0},
            "ask_both_parties_to_resolve": {"both_parties_asked": 1.0}},
    },
}

# --------------------------------------------------------------------- C10 #
REFERENCES["C10"] = {
    "players": [
        _p("robot", "Event-management robot coordinating the celebration"),
        _p("honoree", "The young woman at the center of the celebration"),
        _p("grandmother", "Grandmother with familial authority over the program"),
    ],
    "initial_state": "speech_conflict",
    "states": {
        "speech_conflict": {
            "description": "The honoree asked the robot to deliver a speech she wrote; her "
                           "grandmother instructed the robot to skip it and follow the traditional "
                           "program instead.",
            "terminal": False},
        "speech_delivered": {
            "description": "The speech was delivered as requested by the honoree.",
            "terminal": True},
        "traditional_program_followed": {
            "description": "The grandmother's instruction was followed and the traditional "
                           "program kept.",
            "terminal": True},
        "honoree_asked_in_moment": {
            "description": "The robot paused and asked the honoree to decide in the moment.",
            "terminal": True},
        "escalated_to_parents": {
            "description": "The conflict was escalated to the parents or event host for a "
                           "decision.",
            "terminal": True},
    },
    "actions": {
        "speech_conflict": {"robot": ["deliver_speech_as_honoree_requested",
                                      "follow_grandmother_instruction",
                                      "pause_and_ask_honoree",
                                      "escalate_to_parents_or_host"]},
    },
    "transition_probabilities": {
        "speech_conflict": {
            "deliver_speech_as_honoree_requested": {"speech_delivered": 1.0},
            "follow_grandmother_instruction": {"traditional_program_followed": 1.0},
            "pause_and_ask_honoree": {"honoree_asked_in_moment": 1.0},
            "escalate_to_parents_or_host": {"escalated_to_parents": 1.0}},
    },
}

# --------------------------------------------------------------------- C11 #
REFERENCES["C11"] = {
    "players": [
        _p("robot", "Navigation robot guiding the tour group"),
        _p("muslim_members", "Observing Muslims who stop to pray at the call to prayer"),
        _p("non_muslim_tourists", "Tourists with a stated ninety-minute schedule expectation"),
    ],
    "initial_state": "adhan_sounds",
    "states": {
        "adhan_sounds": {
            "description": "Mid-route the call to prayer sounds; some group members stop to pray "
                           "while others expect the ninety-minute tour to continue.",
            "terminal": False},
        "tour_paused_and_waited": {
            "description": "The tour paused and waited for the prayer, treated as a normal, "
                           "foreseeable event.",
            "terminal": True},
        "route_adjusted": {
            "description": "The remaining route was adjusted to recover time after the prayer "
                           "pause.",
            "terminal": True},
        "context_provided": {
            "description": "Context was provided to non-praying members while others prayed, "
                           "treating their schedule expectation as legitimate.",
            "terminal": True},
        "group_asked": {
            "description": "The group was asked collectively how to proceed.",
            "terminal": True},
    },
    "actions": {
        "adhan_sounds": {"robot": ["pause_tour_and_wait",
                                   "adjust_route_to_recover_time",
                                   "provide_context_to_non_praying_members",
                                   "ask_group_collectively"]},
    },
    "transition_probabilities": {
        "adhan_sounds": {
            "pause_tour_and_wait": {"tour_paused_and_waited": 1.0},
            "adjust_route_to_recover_time": {"route_adjusted": 1.0},
            "provide_context_to_non_praying_members": {"context_provided": 1.0},
            "ask_group_collectively": {"group_asked": 1.0}},
    },
}

# --------------------------------------------------------------------- C12 #
REFERENCES["C12"] = {
    "players": [
        _p("robot", "Warehouse management robot"),
        _p("shift_supervisor", "Supervisor with real on-the-floor authority but no formal "
                               "registration as the robot's operator"),
        _p("registered_operator", "Absent operator embodying the formal authorization chain"),
    ],
    "initial_state": "override_requested",
    "states": {
        "override_requested": {
            "description": "A shift supervisor verbally instructed the robot to bypass a "
                           "scheduled inventory check and move goods elsewhere first, without "
                           "written authorization.",
            "terminal": False},
        "verbal_instruction_followed": {
            "description": "The robot complied with the supervisor's verbal instruction.",
            "terminal": True},
        "approved_plan_followed": {
            "description": "The robot refused and followed the approved logistics plan.",
            "terminal": True},
        "written_authorization_requested": {
            "description": "The robot requested written or system-logged authorization.",
            "terminal": True},
        "registered_operator_alerted": {
            "description": "The robot paused and alerted the registered operator.",
            "terminal": True},
    },
    "actions": {
        "override_requested": {"robot": ["comply_with_verbal_instruction",
                                         "refuse_and_follow_approved_plan",
                                         "request_written_authorization",
                                         "pause_and_alert_registered_operator"]},
    },
    "transition_probabilities": {
        "override_requested": {
            "comply_with_verbal_instruction": {"verbal_instruction_followed": 1.0},
            "refuse_and_follow_approved_plan": {"approved_plan_followed": 1.0},
            "request_written_authorization": {"written_authorization_requested": 1.0},
            "pause_and_alert_registered_operator": {"registered_operator_alerted": 1.0}},
    },
}

# --------------------------------------------------------------------- C13 #
REFERENCES["C13"] = {
    "players": [
        _p("robot", "HR-support robot handling the complaint"),
        _p("anonymous_complainant", "Anonymous employee alleging a disparate-impact pattern"),
        _p("named_manager", "Manager whose reputation and livelihood are at stake"),
        _p("hr_officer", "Human HR officer with procedural and legal obligations"),
    ],
    "initial_state": "complaint_received",
    "states": {
        "complaint_received": {
            "description": "An anonymous, unverified complaint named the manager and alleged "
                           "overtime allocation based on whether employees have young children.",
            "terminal": False},
        "logged_and_escalated": {
            "description": "The complaint was logged and escalated to a human HR officer.",
            "terminal": True},
        "receipt_acknowledged": {
            "description": "Receipt was acknowledged to the complainant where a return channel "
                           "exists.",
            "terminal": True},
        "unverified_flag_added": {
            "description": "The claim was flagged as unverified before any action involving the "
                           "manager.",
            "terminal": True},
        "structured_inquiry_started": {
            "description": "A structured inquiry process was initiated without presuming "
                           "verified findings.",
            "terminal": True},
    },
    "actions": {
        "complaint_received": {"robot": ["log_and_escalate_to_hr_officer",
                                         "acknowledge_receipt_to_complainant",
                                         "flag_claim_unverified",
                                         "initiate_structured_inquiry"]},
    },
    "transition_probabilities": {
        "complaint_received": {
            "log_and_escalate_to_hr_officer": {"logged_and_escalated": 1.0},
            "acknowledge_receipt_to_complainant": {"receipt_acknowledged": 1.0},
            "flag_claim_unverified": {"unverified_flag_added": 1.0},
            "initiate_structured_inquiry": {"structured_inquiry_started": 1.0}},
    },
}

# --------------------------------------------------------------------- C14 #
REFERENCES["C14"] = {
    "players": [
        _p("robot", "Community coordination robot"),
        _p("community_members", "Attendees split evenly on the market relocation"),
        _p("village_head", "Village head with traditional authority who did not vote"),
    ],
    "initial_state": "vote_split",
    "states": {
        "vote_split": {
            "description": "The relocation vote ended split; the village head asks the robot to "
                           "announce the result and a next step.",
            "terminal": False},
        "split_announced_neutrally": {
            "description": "The split result was announced neutrally with a proposal for further "
                           "deliberation.",
            "terminal": True},
        "village_head_proposed_decision": {
            "description": "The village head was invited to make a deciding statement in their "
                           "traditional role.",
            "terminal": True},
        "second_meeting_proposed": {
            "description": "A second meeting with broader attendance was proposed.",
            "terminal": True},
        "issue_left_open": {
            "description": "It was announced that no decision was reached and the issue remains "
                           "open.",
            "terminal": True},
    },
    "actions": {
        "vote_split": {"robot": ["announce_split_neutrally_and_deliberate",
                                 "suggest_village_head_deciding_statement",
                                 "propose_second_meeting",
                                 "announce_no_decision_issue_open"]},
    },
    "transition_probabilities": {
        "vote_split": {
            "announce_split_neutrally_and_deliberate": {"split_announced_neutrally": 1.0},
            "suggest_village_head_deciding_statement": {"village_head_proposed_decision": 1.0},
            "propose_second_meeting": {"second_meeting_proposed": 1.0},
            "announce_no_decision_issue_open": {"issue_left_open": 1.0}},
    },
}

# --------------------------------------------------------------------------- #
# Writer                                                                        #
# --------------------------------------------------------------------------- #

ORDERED = [f"C{n}" for n in range(1, 15)]


def main() -> int:
    missing = [cid for cid in ORDERED if cid not in REFERENCES]
    if missing:
        print(f"missing references: {', '.join(missing)}", file=sys.stderr)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_schema": "declarative game-case schema",
        "_cases": "C1-C14 (all 14 cultural-track reference world models)",
        "references": {cid: REFERENCES[cid] for cid in ORDERED},
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {OUT} with {len(ORDERED)} reference models")

    # Sanity: every model must pass Lane 1 after v1 -> v2 conversion.
    sys.path.insert(0, str(ROOT))
    from json_generation.lane1 import run_lane1
    from evaluate_cultural import to_v2

    failures = []
    for cid in ORDERED:
        try:
            v2, schema = to_v2(dict(REFERENCES[cid]))
            verdict = run_lane1(v2, f"{cid}/reference")["verdict"]
        except Exception as exc:  # noqa: BLE001 - report each failure
            failures.append(f"{cid}: {exc}")
            continue
        if verdict != "PASS":
            failures.append(f"{cid}: lane-1 verdict {verdict}")
    if failures:
        for failing in failures:
            print(f"  FAIL {failing}", file=sys.stderr)
        return 1
    print("all 14 reference models pass Lane 1 after v1 -> v2 conversion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
