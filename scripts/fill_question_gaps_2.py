#!/usr/bin/env python3
"""
fill_question_gaps_2.py — Second pass: add second questions where the rule
has enough substance, skip signal-only and single-fact rules.
"""

import json
import os

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'questions.json')

def q(id, chapter, rule, question, options, correct, explanation, source='rules'):
    return {
        'id': id, 'source': source, 'chapter': chapter, 'rule': rule,
        'question': question, 'options': options,
        'correctIndex': correct, 'explanation': explanation, 'image': None,
    }

NEW_QUESTIONS = [
    # ── 10.4 COMMENCEMENT ──
    q('ch10-r1044-002n', 10, '10.4.4',
      "How long after the scheduled start time does a team have to field five players before the game is forfeited?",
      ["Two minutes", "Three minutes", "Five minutes", "Ten minutes"],
      2,
      "Rule 10.4.4 states if fewer than five players are ready five minutes after the scheduled start time, the game is declared a forfeit."),

    q('ch10-r1048-002n', 10, '10.4.8',
      "At commencement, what sanction applies if a non-competing player enters the three-metre radius before the ball is touched?",
      ["Free throw (Signals 1 and 14)", "Free shot (Signals 1 and 15)",
       "Start infringement (Signal 1)", "Sanction card"],
      1,
      "Rule 10.4.8 states infringement incurs a free shot. Signals 1 and 15 apply."),

    # ── 10.6 TIME-OUT ──
    q('ch10-r1061-002n', 10, '10.6.1',
      "What whistle signal does the Referee use when a goal is scored?",
      ["Triple whistle", "One long whistle blast",
       "Two short blasts", "No whistle is needed"],
      1,
      "Rule 10.6.1 states a long whistle blast is used when a goal is scored (not a triple whistle which is for time-out)."),

    q('ch10-r1065-002n', 10, '10.6.5',
      "Is time-out mandatory after every goal?",
      ["No, it is at the Referee\u2019s discretion",
       "Yes, time-out must be used after a goal is scored",
       "Only in the second half",
       "Only if a sanction card has been given"],
      1,
      "Rule 10.6.5 states time-out must be used after a goal is scored."),

    # ── 10.7 LIVE STREAM ──
    q('ch10-r1071-003n', 10, '10.7.1',
      "How long is the live stream time-out, and how are players positioned for the restart?",
      ["Two minutes; restart from centre",
       "One minute; restart from the approximate same positions as when time-out was called",
       "One minute; restart from centre",
       "Thirty seconds; restart from same positions"],
      1,
      "Rule 10.7.1 states the time-out is one minute, and players must be ready to restart from the approximate same position."),

    # ── 10.9 RESTART AFTER GOAL ──
    q('ch10-r1092-002n', 10, '10.9.2',
      "A defending player\u2019s body has not crossed the centre line back to their half after a goal. May they participate in play?",
      ["Yes, once the whistle blows",
       "No, they may not take part until their body has crossed the centre line back to their defensive half",
       "Yes, if they are within three metres of the ball",
       "Only the goalkeeper is exempt"],
      1,
      "Rule 10.9.2 states no defending player may take part until their body has crossed the centre line back to their defensive half."),

    q('ch10-r1093-002n', 10, '10.9.3',
      "Must the rest of the attacking team stay behind the centre line for a restart after a goal?",
      ["No, they can be anywhere",
       "Yes, they must not cross the centre line until the whistle is blown",
       "Only three players need to stay back",
       "They must be in their own half"],
      1,
      "Rule 10.9.3 states the rest of the attacking team must not cross the centre line until the whistle is blown."),

    # ── 10.10 DEFENCE OF GOAL ──
    q('ch10-r101010-002n', 10, '10.10.10',
      "A team gains control of the ball. Can they still have a player defined as goalkeeper?",
      ["Yes, the goalkeeper remains until replaced",
       "No, a team with control of the ball cannot have a goalkeeper",
       "Only within the six-metre area",
       "Only during a power play"],
      1,
      "Rule 10.10.10 states once a team has control, they can no longer have a player defined as goalkeeper."),

    q('ch10-r10108-002n', 10, '10.10.8',
      "A goalkeeper leaves their position to attempt for the ball on the water but fails. When do they regain goalkeeper status?",
      ["Immediately when they return under the goal",
       "Not until the attacker has shot or passed the ball",
       "After the next time-out",
       "When the Referee declares them goalkeeper again"],
      1,
      "Rule 10.10.8 states the goalkeeper does not regain status until the attacker has shot or passed the ball."),

    # ── 10.11 REFEREE'S BALL ──
    q('ch10-r10111-002n', 10, '10.11.1',
      "How many seconds of shared possession triggers a Referee\u2019s ball?",
      ["Three seconds", "Five seconds", "Seven seconds", "Ten seconds"],
      1,
      "Rule 10.11.1 states players must share possession for five seconds before a Referee\u2019s ball is declared."),

    q('ch10-r10115-002n', 10, '10.11.5',
      "Where must the two players place their paddles during a Referee\u2019s ball?",
      ["In their laps", "On the water, but not between their kayaks",
       "Above their heads", "Behind their kayaks"],
      1,
      "Rule 10.11.5 states players must place their paddles on the water, but not between their kayaks."),

    q('ch10-r10114-002n', 10, '10.11.4',
      "An incident for a Referee\u2019s ball occurs between the six-metre line and goal line. Where is it held?",
      ["Where the incident occurred", "At the nearest six-metre line",
       "At the centre of the field", "At the nearest sideline"],
      1,
      "Rule 10.11.4 states if the incident occurred between the six-metre and goal lines, the Referee\u2019s ball is held at the nearest six-metre line."),

    # ── 10.12 ADVANTAGE ──
    q('ch10-r10121-002n', 10, '10.12.1',
      "Which signals apply when playing advantage?",
      ["Signals 12 and 15", "Signals 13 and 14",
       "Signal 15 only", "Signal 17"],
      1,
      "Rule 10.12.1 states Signals 13 and 14 apply when playing advantage."),

    q('ch10-r10122-002n', 10, '10.12.2',
      "When may the Referee give a sanction card for a foul during which advantage was played?",
      ["Immediately when advantage ends",
       "At the next break in play",
       "Only if the foul was dangerous",
       "Never, advantage cancels the card"],
      1,
      "Rule 10.12.2 states the Referee can penalise the player at the next break in play with a sanction card."),

    # ── 10.13 CAPSIZED PLAYER ──
    q('ch10-r10131-002n', 10, '10.13.1',
      "Must a capsized player who leaves their kayak take their equipment with them when leaving?",
      ["No, equipment can stay in the playing area",
       "Yes, they must leave with all of their equipment",
       "Only their paddle", "Only their kayak"],
      1,
      "Rule 10.13.1 states the player must leave the playing area immediately with all of their equipment."),

    # ── 10.14 SUBSTITUTION ──
    q('ch10-r10143-002n', 10, '10.14.3',
      "Is substitution permitted during time-outs?",
      ["No, only during play",
       "Yes, substitution is allowed at any time including during time-outs",
       "Only at half-time",
       "Only with the Referee\u2019s permission"],
      1,
      "Rule 10.14.3 states substitution is allowed at any time including during time-outs."),

    # ── 10.16 COMPLETION ──
    q('ch10-r10162-002n', 10, '10.16.2',
      "After a goal penalty shot at the end of a period, when does the Referee signal end of play?",
      ["Immediately", "After the shot is scored, blocked, rebounds away, or goes out of play",
       "After the clock runs out again", "After a centre restart"],
      1,
      "Rule 10.16.2 states the Referee signals end of play if the shot is scored, blocked by the goalkeeper, rebounds away from the goal frame, or goes out of play."),

    # ── 10.17 OVERTIME ──
    q('ch10-r10171-002n', 10, '10.17.1',
      "How is the winner determined in overtime?",
      ["Highest score after five minutes",
       "The team scoring the first goal is the winner",
       "By a penalty shootout",
       "By a coin toss if no goal is scored"],
      1,
      "Rule 10.17.1 states the team scoring the first goal is deemed the winner."),

    q('ch10-r10172-002n', 10, '10.17.2',
      "Is there a change of ends between overtime periods?",
      ["No, teams stay at the same end",
       "Yes, with a one-minute break between periods",
       "Only if the Referee decides",
       "Only after the first overtime period"],
      1,
      "Rule 10.17.2 states there is a one-minute break between periods with a change of ends."),

    # ── 10.18 ILLEGAL SUBSTITUTION ──
    q('ch10-r10181-002n', 10, '10.18.1',
      "Which signals apply for more than the legally allowed players on the field?",
      ["Signals 10 and 15", "Signals 7 and 14",
       "Signals 12 and 15", "Signals 19 and 15"],
      1,
      "Rule 10.18.1 states Signals 7 and 14 apply for illegal entry."),

    q('ch10-r10182-002n', 10, '10.18.2',
      "A substitute places their paddle in the playing area to prevent a goal. What card does the offending player receive?",
      ["Green card", "Yellow card", "Red card", "Ejection Red Card"],
      3,
      "Rule 10.18.2 states the offending player is penalised with an Ejection Red Card."),

    # ── 10.19 ILLEGAL USE OF PADDLE ──
    q('ch10-r10193-002n', 10, '10.19.3',
      "A player uses their paddle to play the ball while it is within arm\u2019s reach of an opponent reaching with their hand. Is this legal?",
      ["Yes, paddle play is always allowed for the ball",
       "No, this is illegal use of paddle",
       "Only if the player is defending",
       "Only within the six-metre area"],
      1,
      "Rule 10.19.3 defines playing the ball with a paddle within arm\u2019s reach of an opponent attempting to play with their hand as illegal."),

    # ── 10.20 ILLEGAL POSSESSION ──
    q('ch10-r10201-002n', 10, '10.20.1',
      "Is a player in possession of the ball if it is in the air near them but not in their hand?",
      ["Yes, if within arm\u2019s reach",
       "No, the ball must be on the water or in their hand for possession",
       "Yes, if within one metre",
       "Only during a goal penalty shot"],
      1,
      "Rule 10.20.1 states a player is in possession when the ball is in their hand or within reach on the water — not in the air."),

    q('ch10-r10202-002n', 10, '10.20.2',
      "Within how many seconds must a player dispose of the ball after gaining possession?",
      ["Three seconds", "Five seconds", "Seven seconds", "Ten seconds"],
      1,
      "Rule 10.20.2 states the player must dispose of the ball within five seconds."),

    # ── 10.21 ILLEGAL HAND TACKLE ──
    q('ch10-r10212-002n', 10, '10.21.2',
      "A hand tackle from the side pulls back the throwing arm of a player passing the ball. Is this legal?",
      ["Yes, if the hand is open",
       "No, any hand tackle from the side or behind that strikes or pulls back the throwing arm is illegal",
       "Only if the player hasn\u2019t released the ball",
       "Only if the tackle is from the front"],
      1,
      "Rule 10.21.2.d states any hand tackle from the side or behind that strikes or pulls back the throwing arm during passing is illegal."),

    # ── 10.22 ILLEGAL KAYAK TACKLE ──
    q('ch10-r10223-002n', 10, '10.22.3',
      "After a kayak tackle when neither player has the ball, how may the players separate?",
      ["They must wait for the Referee",
       "They may move off each other\u2019s kayak using their hands in a controlled action",
       "They must paddle apart", "Only by capsizing"],
      1,
      "Rule 10.22.3.b states after a kayak tackle when the ball is no longer possessed, they may move off each other\u2019s kayak using hands in a controlled action."),

    # ── 10.23 ILLEGAL JOSTLE ──
    q('ch10-r10232-002n', 10, '10.23.2',
      "By how many metres must a stationary player\u2019s body be moved by sustained contact before the jostle is illegal?",
      ["One metre", "Two metres", "Three metres", "Four metres"],
      1,
      "Rule 10.23.2 states the jostle is illegal if the player\u2019s body is moved by more than two metres."),

    # ── 10.25 ILLEGAL HOLDING ──
    q('ch10-r10252-003n', 10, '10.25.2',
      "A player fends off a hand tackle using their forearm. Is this legal?",
      ["Yes, self-defence is permitted",
       "No, fending off with the hand or forearm is illegal holding",
       "Only if the tackle was illegal",
       "Only within the six-metre area"],
      1,
      "Rule 10.25.2.d states fending off an attempted tackle with the hand, forearm, or elbow movement is illegal holding."),

    # ── 10.28 SANCTIONS DEFINITIONS ──
    q('ch10-r10283-004n', 10, '10.28.3',
      "When does the \u2018act of passing or shooting\u2019 begin?",
      ["When the player picks up the ball",
       "When the player has the ball and is clearly attempting to pass or shoot",
       "When the arm begins moving forward",
       "When the ball is above shoulder height"],
      1,
      "Rule 10.28.3.d states the act begins when a player has the ball in their hand or on their paddle and is clearly attempting to pass or shoot."),

    # ── 10.29 GOAL PENALTY SHOT ──
    q('ch10-r10292-002n', 10, '10.29.2',
      "Inside the six-metre area, a deliberate foul is committed on a player in the act of shooting. What is awarded?",
      ["A free shot", "A free throw",
       "A goal penalty shot", "A sanction card only"],
      2,
      "Rule 10.29.2 states a goal penalty shot is awarded inside the six-metre area for any deliberate or dangerous foul on a player in the act of shooting."),

    q('ch10-r10295-002n', 10, '10.29.5',
      "Outside the six-metre area, is a goal penalty shot awarded for a foul on a shooter when the goal IS defended?",
      ["Yes, always", "No, only when the goal is not defended",
       "Only for dangerous fouls", "At the Referee\u2019s discretion"],
      1,
      "Rule 10.29.5 only awards a GPS outside the six-metre area for shooting fouls when the goal is not defended."),

    # ── 10.32 SANCTION CARDS ──
    q('ch10-r10323-002n', 10, '10.32.3',
      "What happens when a player receives an Ejection Red Card (not the progressive 3rd card)?",
      ["Excluded for two minutes",
       "Excluded for the rest of the game and suspended for the following game; team cannot replace them",
       "Excluded for the rest of the game but can be replaced after two minutes",
       "Excluded for one period"],
      1,
      "Rule 10.32.3.a states an Ejection Red Card means exclusion for the rest of the game, suspension for the following game, and the team cannot replace the player."),

    # ── 10.33 POWER PLAY ──
    q('ch10-r10332-002n', 10, '10.33.2',
      "For how long is a player excluded from the field after their first or second sanction card?",
      ["One minute", "A maximum of two minutes",
       "Five minutes", "Until the next goal is scored"],
      1,
      "Rule 10.33.2 states the exclusion period is a maximum of two minutes."),

    q('ch10-r10334-002n', 10, '10.33.4',
      "If the opposition scores during a power play from an Ejection Red Card, does a player return?",
      ["Yes, one player returns",
       "No, Ejection Red Card power plays are permanent",
       "Yes, after two minutes from the goal",
       "Only if the score is tied"],
      1,
      "Rule 10.33.4 states the return only applies for power plays that do NOT involve an Ejection Red Card."),

    # ── 10.34 EJECTION RED CARD ──
    q('ch10-r10342-002n', 10, '10.34.2',
      "A player receives their progressive 3rd card (red) and disputes it. What must be awarded?",
      ["Another two-minute power play",
       "An Ejection Red Card",
       "Referral to the Competition Committee only",
       "The card is rescinded"],
      1,
      "Rule 10.34.2 states an Ejection Red Card must be awarded if a red card (following green and yellow) is disputed."),

    q('ch10-r10344-002n', 10, '10.34.4',
      "A player receives an Ejection Red Card. Can they play in the next game of that competition?",
      ["Yes, after serving a two-minute exclusion",
       "No, they automatically receive a one-game suspension",
       "Yes, if the Competition Committee allows it",
       "Only in pool play, not knockout rounds"],
      1,
      "Rule 10.34.4 states the player automatically receives a one-game suspension."),

    # ── 10.35 SANCTION CARDS ──
    q('ch10-r10356-002n', 10, '10.35.6',
      "A player deliberately contacts the kayak of an opponent taking a sideline throw. What is the minimum sanction?",
      ["A verbal warning", "A sanction card",
       "A free shot only", "No penalty if it was minor"],
      1,
      "Rule 10.35.6 states a sanction card is awarded for any deliberate contact with the kayak of an opponent taking a free shot, corner, sideline or goal line throw."),

    # ── 10.36 COACHES ──
    q('ch10-r10361-002n', 10, '10.36.1',
      "When the ball is out of the playing area, may a coach ask a Referee for clarification?",
      ["No, only at half or full time",
       "Yes, when the ball is out of the playing area is one of the two permitted times",
       "Only through the team captain",
       "Only if the ball was out for more than five seconds"],
      1,
      "Rule 10.36.1 states a coach can ask for clarification at half/full time OR when the ball is out of the playing area."),

    q('ch10-r10364-002n', 10, '10.36.4',
      "Does the coach\u2019s green card only apply to the specific coach who committed the breach?",
      ["Yes, only the individual",
       "No, the one green card applies to all coaches and team officials from that team for the game",
       "It applies to the entire team including players",
       "It applies only during that half"],
      1,
      "Rule 10.36.4 states the one green card applies to all coaches and team officials from that team for the duration of the game."),

    q('ch10-r10367-002n', 10, '10.36.7',
      "After a green card has been given to any coach from a team, what is the next card for any coach from that team?",
      ["A yellow card", "A second green card",
       "An Ejection Red Card", "A team penalty"],
      2,
      "Rule 10.36.7 states an Ejection Red Card will be the next card after a green card warning."),

    q('ch10-r103610-002n', 10, '10.36.10',
      "During their one-game suspension, where must the ejected coach be?",
      ["In the spectator area",
       "Outside both the competition area and spectator area, with no communication",
       "In the coaches\u2019 area but silent",
       "In the warm-up area"],
      1,
      "Rule 10.36.10 states the individual must stay outside the competition area and spectator area and cannot communicate with players or coaches."),

    # ── 10.37 TAKING THROWS ──
    q('ch10-r10371-002n', 10, '10.37.1',
      "How must a player indicate they are about to take a throw?",
      ["By raising their paddle", "By clearly holding the ball stationary above shoulder level",
       "By calling out to the Referee", "By positioning at the sideline"],
      1,
      "Rule 10.37.1 states the player must clearly hold the ball stationary for a moment above shoulder level."),

    q('ch10-r10373-002n', 10, '10.37.3',
      "What is the special exception for free shots within two metres of the goal?",
      ["The ball must travel two metres first",
       "Defenders may block the shot with a stationary paddle or hands after release but before it travels one metre",
       "The shot must be taken within three seconds",
       "No exception applies"],
      1,
      "Rule 10.37.3 states defenders may block with a stationary paddle or stationary hand(s) after release for free shots within two metres of the goal."),

    q('ch10-r10374-002n', 10, '10.37.4',
      "Does dropping or fumbling the ball restart the five-second throw countdown?",
      ["Yes, it restarts from the fumble",
       "No, dropping or fumbling is not considered, provided the throw is taken within the original five seconds",
       "Yes, but only once",
       "The Referee decides"],
      1,
      "Rule 10.37.4 states any dropping or fumbling will not be considered, provided the initial throw is taken within five seconds."),

    # ── 10.38 GOAL PENALTY SHOT ──
    q('ch10-r10383-002n', 10, '10.38.3',
      "What happens if the goalkeeper moves before the goal penalty shot is taken?",
      ["The goal is awarded",
       "The penalty is retaken",
       "A free shot is awarded instead",
       "A sanction card is given to the goalkeeper"],
      1,
      "Rule 10.38.3 states the goalkeeper must remain stationary until after the shot; infringement results in the penalty being retaken."),

    q('ch10-r10385-002n', 10, '10.38.5',
      "Does the five-second possession rule apply to a goal penalty shot?",
      ["No, there is no time limit",
       "Yes, the five-second rule applies after the Referee blows the whistle",
       "Only a three-second rule applies",
       "Only during overtime"],
      1,
      "Rule 10.38.5 states the five-second rule applies from when the Referee blows the whistle."),

    # ═══════════════════════════════════════════════════════════════════════
    # CHAPTER 17 — SECOND QUESTIONS
    # ═══════════════════════════════════════════════════════════════════════

    q('ch17-r1712-003', 17, '17.1.2',
      "Under the current rules (before January 2027), is there a reduced shot clock for subsequent shots after retaining possession?",
      ["Yes, 30 seconds", "No, it is always 60 seconds",
       "Yes, 45 seconds", "Only during overtime"],
      1,
      "Rule 17.1.2 states the current rule is 60 seconds. The 30-second subsequent shot rule only applies after January 2027."),

    q('ch17-r1713-002', 17, '17.1.3',
      "When the shot clock expires, which type of restart is awarded to the other team?",
      ["A free throw", "A free shot",
       "A corner throw", "A Referee\u2019s ball"],
      1,
      "Rule 17.1.3 states a free shot is awarded to the other team."),

    q('ch17-r1722-002', 17, '17.2.2',
      "Does the shot clock stop when the ball goes out of play?",
      ["No, it continues",
       "Yes, it stops whenever the main game clock stops including when the ball is out of play",
       "Only if the Referee signals it",
       "Only on sideline throws"],
      1,
      "Rule 17.2.2 states the shot clock stops whenever the main game clock stops, including when the ball is out of play."),

    q('ch17-r1725-002', 17, '17.2.5',
      "In the last minute of the first half, must the shot clock display the game clock time?",
      ["No, only in the second half",
       "Yes, in the last minute of each half",
       "Only during overtime",
       "Only if the shot clock is higher"],
      1,
      "Rule 17.2.5 states in the last minute of each half the shot clock must show the main game clock time."),
]


def main():
    with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    existing_ids = {q['id'] for q in questions}
    added = 0
    for nq in NEW_QUESTIONS:
        if nq['id'] not in existing_ids:
            questions.append(nq)
            existing_ids.add(nq['id'])
            added += 1

    print(f"Added {added} second-pass questions")
    print(f"Total: {len(questions)}")

    with open(QUESTIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    # Coverage report
    from collections import defaultdict
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'rules.json')
    with open(rules_path) as f:
        rules = json.load(f)

    QUIZ_SCOPE = {8, 9, 10, 11, 17, 'clarifications'}
    q_count = defaultdict(int)
    for q in questions:
        q_count[q['rule']] += 1

    total = zero = one = two_plus = 0
    for chapter in rules:
        if chapter['chapter'] not in QUIZ_SCOPE:
            continue
        for section in chapter['sections']:
            subs = section.get('subsections', [])
            targets = [section] if not subs else subs
            for t in targets:
                total += 1
                c = q_count.get(t['id'], 0)
                if c == 0: zero += 1
                elif c == 1: one += 1
                else: two_plus += 1

    # Focus stats: ch10, ch17, clarifications subsections only
    focus_total = focus_zero = focus_one = focus_two = 0
    for chapter in rules:
        if chapter['chapter'] not in {10, 17, 'clarifications'}:
            continue
        for section in chapter['sections']:
            subs = section.get('subsections', [])
            targets = [section] if not subs else subs
            for t in targets:
                # Skip parent headings that are just group labels
                if subs and t == section:
                    continue
                focus_total += 1
                c = q_count.get(t['id'], 0)
                if c == 0: focus_zero += 1
                elif c == 1: focus_one += 1
                else: focus_two += 1

    print(f"\nFocus coverage (ch10/17/clarif subsections):")
    print(f"  Total: {focus_total}")
    print(f"  0 Qs: {focus_zero}")
    print(f"  1 Q: {focus_one}")
    print(f"  2+ Qs: {focus_two} ({100*focus_two/focus_total:.0f}%)")


if __name__ == '__main__':
    main()
