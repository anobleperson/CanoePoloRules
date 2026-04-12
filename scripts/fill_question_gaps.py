#!/usr/bin/env python3
"""
fill_question_gaps.py — Remap existing questions to specific subsections
and generate new questions for all gaps in ch10, ch17, and clarifications.

Usage:
    python3 scripts/fill_question_gaps.py
"""

import json
import os

QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'questions.json')

# ── Step 1: Remap existing questions to specific subsection IDs ──────────────

REMAPS = {
    # ch10 parent-level → subsection based on explanation content
    'ch10-r101-001': '10.1.1',
    'ch10-r101-002': '10.1.2',
    'ch10-r101-003': '10.1.3',
    'ch10-r102-001': '10.2.1',
    'ch10-r102-002': '10.2.2',
    'ch10-r104-001': '10.4.1',
    'ch10-r104-002': '10.4.4',
    'ch10-r104-003': '10.4.8',
    'ch10-r104-004': '10.4.2',
    'ch10-r106-001': '10.6.1',
    'ch10-r106-002': '10.6.5',
    'ch10-r106-003': '10.6.7',
    'ch10-r107-001': '10.7.1',
    'ch10-r107-002': '10.7.1',
    'ch10-r107-003': '10.7.3',
    'ch10-r108-001': '10.8.1',
    'ch10-r108-002': '10.8.2',
    'ch10-r109-001': '10.9.2',
    'ch10-r109-002': '10.9.3',
    'ch10-r1010-001': '10.10.1',
    'ch10-r1010-002': '10.10.10',
    'ch10-r1010-003': '10.10.8',
    'ch10-r1011-001': '10.11.1',
    'ch10-r1011-002': '10.11.4',
    'ch10-r1011-003': '10.11.5',
    'ch10-r1012-001': '10.12.1',
    'ch10-r1012-002': '10.12.2',
    'ch10-r1013-001': '10.13.1',
    'ch10-r1013-002': '10.13.3',
    'ch10-r1013-003': '10.13.4',
    'ch10-r1014-001': '10.14.3',
    'ch10-r1014-002': '10.14.3',
    'ch10-r1015-001': '10.15',
    'ch10-r1015-002': '10.15',
    'ch10-r1016-001': '10.16.1',
    'ch10-r1016-002': '10.16.2',
    'ch10-r1017-001': '10.17.1',
    'ch10-r1017-002': '10.17.2',
    'ch10-r1018-001': '10.18.2',
    'ch10-r1018-002': '10.18.1',
    'ch10-r1018-003': '10.18.1',
    'ch10-r1019-001': '10.19.5',
    'ch10-r1019-002': '10.19.3',
    'ch10-r1020-001': '10.20.2',
    'ch10-r1020-002': '10.20.1',
    'ch10-r1020-003': '10.20.3',
    'ch10-r1021-001': '10.21.1',
    'ch10-r1021-002': '10.21.2',
    'ch10-r1021-003': '10.21.2',
    'ch10-r1022-001': '10.22.2',
    'ch10-r1022-002': '10.22.3',
    'ch10-r1022-003': '10.22.3',
    'ch10-r1022-004': '10.22.3',
    'ch10-r1023-001': '10.23.1',
    'ch10-r1023-002': '10.23.2',
    'ch10-r1023-003': '10.23.4',
    'ch10-r1024-001': '10.24.2',
    'ch10-r1024-002': '10.24.2',
    'ch10-r1024-003': '10.24.2',
    'ch10-r1025-001': '10.25.2',
    'ch10-r1025-002': '10.25.2',
    'ch10-r1026-001': '10.26.2',
    'ch10-r1026-002': '10.26.2',
    'ch10-r1027-001': '10.27.1',
    'ch10-r1027-002': '10.27.4',
    'ch10-r1027-003': '10.27.3',
    'ch10-r1028-001': '10.28.2',
    'ch10-r1028-002': '10.28.3',
    'ch10-r1029-001': '10.29.2',
    'ch10-r1029-002': '10.29.5',
    'ch10-r1030-001': '10.30.2',
    'ch10-r1030-002': '10.30.3',
    'ch10-r1031-001': '10.31.2',
    'ch10-r1031-002': '10.31.4',
    'ch10-r1032-001': '10.32.2',
    'ch10-r1032-002': '10.32.3',
    'ch10-r1032-003': '10.32.3',
    'ch10-r1033-001': '10.33.2',
    'ch10-r1033-002': '10.33.4',
    'ch10-r1034-001': '10.34.2',
    'ch10-r1034-002': '10.34.4',
    'ch10-r1035-001': '10.35.6',
    'ch10-r1035-002': '10.35.5',
    'ch10-r1035-003': '10.35.5',
    'ch10-r1035-004': '10.35.10',
    'ch10-r1036-001': '10.36.1',
    'ch10-r1036-002': '10.36.4',
    'ch10-r1036-003': '10.36.7',
    'ch10-r1037-001': '10.37.1',
    'ch10-r1037-002': '10.37.3',
    'ch10-r1037-003': '10.37.3',
    'ch10-r1038-001': '10.38.3',
    'ch10-r1038-002': '10.38.3',
    'ch10-r1038-003': '10.38.6',
    'ch10-r1038-004': '10.38.7',
    # 10.19.2 questions that actually test other subsections
    'ch10-r10192-001': '10.19.3',
    'ch10-r10192-002': '10.19.5',
    'ch10-r10192-003': '10.19.8',
    # Clarifications: use section IDs for deep-link
    'clarif-sprint1-001': 'clarif-sprint-starts',
    'clarif-sprint1-002': 'clarif-sprint-starts',
    'clarif-sprint1-003': 'clarif-sprint-starts',
    'clarif-defender-001': 'clarif-defenders-paddle',
    'clarif-handtackle-001': 'clarif-illegal-hand-tackle',
    'clarif-handtackle-002': 'clarif-illegal-hand-tackle',
}

# ── Step 2: New questions ────────────────────────────────────────────────────

def q(id, chapter, rule, question, options, correct, explanation, source='rules'):
    return {
        'id': id,
        'source': source,
        'chapter': chapter,
        'rule': rule,
        'question': question,
        'options': options,
        'correctIndex': correct,
        'explanation': explanation,
        'image': None,
    }

NEW_QUESTIONS = [
    # ═══════════════════════════════════════════════════════════════════════
    # CHAPTER 10 — GAME PLAY
    # ═══════════════════════════════════════════════════════════════════════

    # ── 10.1 NUMBER OF PLAYERS ──
    q('ch10-r1014-001n', 10, '10.1.4',
      "What must be handed to the appropriate official before the time indicated by the Competition Committee?",
      ["Team strategy documents", "Medical clearance certificates",
       "The list of players\u2019 names and numbers", "The team\u2019s colour preferences"],
      2,
      "Rule 10.1.4 states the list of players\u2019 names and numbers for a game must be handed to the appropriate official before the time indicated by the Competition Committee."),

    q('ch10-r1011-001n', 10, '10.1.1',
      "What is the maximum squad size allowed for any single game?",
      ["Five", "Six", "Seven", "Eight"],
      3,
      "Rule 10.1.1 states each team may consist of a maximum of eight players for any game."),

    q('ch10-r1012-001n', 10, '10.1.2',
      "Players not currently on the playing area are considered what?",
      ["Reserve players", "Substitutes", "Bench players", "Squad members"],
      1,
      "Rule 10.1.2 states players beyond the five on the playing area are to be considered as substitutes."),

    q('ch10-r1013-001n', 10, '10.1.3',
      "To how few players can a team be reduced before the Referee must end the game?",
      ["One", "Two", "Three", "Four"],
      1,
      "Rule 10.1.3 states if a team is reduced to two players the Referee must end the game."),

    # ── 10.2 PLAYING TIME ──
    q('ch10-r1023-001n', 10, '10.2.3',
      "What must teams do after each period of play?",
      ["Stay at their current end", "Change ends",
       "Take a five-minute break", "Conduct a coin toss"],
      1,
      "Rule 10.2.3 states the teams must change ends after each period of play."),

    q('ch10-r1024-001n', 10, '10.2.4',
      "Who restarts the clock after the Referee signals time-out?",
      ["The Timekeeper restarts it automatically after 30 seconds",
       "The Timekeeper restarts when the Referee restarts the game with a whistle",
       "The Chief Official signals the restart",
       "The clock restarts when both teams are ready"],
      1,
      "Rule 10.2.4 states the Timekeeper will restart the clock when the Referee restarts the game with a whistle."),

    q('ch10-r1021-001n', 10, '10.2.1',
      "What is the minimum permitted playing time per half?",
      ["Five minutes", "Six minutes", "Seven minutes", "Eight minutes"],
      2,
      "Rule 10.2.1 states the minimum playing time is two periods of seven minutes."),

    q('ch10-r1022-001n', 10, '10.2.2',
      "What is the minimum half time interval?",
      ["Thirty seconds", "One minute", "Two minutes", "Three minutes"],
      1,
      "Rule 10.2.2 states the minimum half time interval is one minute."),

    # ── 10.4 COMMENCEMENT OF PLAY ──
    q('ch10-r1043-001n', 10, '10.4.3',
      "What is the consequence if a team deliberately causes an unnecessary delay at the start?",
      ["A goal penalty shot is awarded", "The game is forfeited",
       "A start infringement is called (Signals 1 and 15)", "A yellow card is issued to the captain"],
      2,
      "Rule 10.4.3 states if a team deliberately causes an unnecessary delay, a start infringement will be called. Signal 1 and 15 apply."),

    q('ch10-r1045-001n', 10, '10.4.5',
      "How does the Referee start play at the commencement?",
      ["Blows the whistle, then places the ball at centre",
       "Blows the whistle, then releases or throws the ball into the centre",
       "Drops the ball at centre and then blows the whistle",
       "Hands the ball to a nominated player"],
      1,
      "Rule 10.4.5 states the Referee blows the whistle to start play and then releases or throws the ball into the centre of the playing area."),

    q('ch10-r1046-001n', 10, '10.4.6',
      "What happens if the Referee\u2019s throw at commencement gives one team a definite advantage?",
      ["Play continues; advantage is accepted",
       "The Referee calls for the ball and restarts the period",
       "A free throw is awarded to the disadvantaged team",
       "The ball is placed on centre and restarted"],
      1,
      "Rule 10.4.6 states if the ball gives one team a definite advantage, the Referee calls for the ball and restarts."),

    q('ch10-r1047-001n', 10, '10.4.7',
      "At commencement, what is the penalty for physical assistance from teammates on the player attempting for the ball?",
      ["Free shot (Signals 1 and 15)", "Free throw (Signals 1 and 14)",
       "Start infringement (Signal 1)", "Goal penalty shot (Signal 16)"],
      1,
      "Rule 10.4.7 states physical assistance from other players at commencement incurs a free throw. Signals 1 and 14 apply."),

    q('ch10-r1048-001n', 10, '10.4.8',
      "At commencement, how many players from each team may attempt to gain possession of the ball?",
      ["Two", "Three", "One", "Any number"],
      2,
      "Rule 10.4.8 states only one player from each team may attempt to gain possession of the ball."),

    q('ch10-r1041-001n', 10, '10.4.1',
      "At the start of the second half, may a team have fewer than five players on the goal line?",
      ["No, always five", "Yes, due to sanctions or injury",
       "Yes, but only with referee permission", "No, the game cannot continue with fewer"],
      1,
      "Rule 10.4.1 states at the beginning of the second half, teams must line up but may have less than 5 players due to sanctions or injury."),

    q('ch10-r1042-001n', 10, '10.4.2',
      "What is the specific term for sprinting before the referee\u2019s whistle at the start?",
      ["False start", "Start infringement", "Early sprint penalty", "Commencement violation"],
      1,
      "Rule 10.4.2 defines sprinting before the whistle as a start infringement."),

    # ── 10.6 TIME-OUT ──
    q('ch10-r1062-001n', 10, '10.6.2',
      "When must the Referee call time-out regarding a capsized player?",
      ["Only if the capsized player requests it",
       "If the capsized player or their equipment is interfering with play",
       "Always, immediately upon any capsize",
       "Only if the capsized player is injured"],
      1,
      "Rule 10.6.2 states time-out must be given if a capsized player or their equipment is interfering with play."),

    q('ch10-r1063-001n', 10, '10.6.3',
      "When should time-out be used immediately for equipment issues?",
      ["When any player requests a paddle change",
       "When game regulations are dangerously breached or field equipment needs correction",
       "When a team wants to discuss strategy",
       "When the ball is deflated"],
      1,
      "Rule 10.6.3 states time-out should be used immediately when regulations are dangerously breached or equipment needs correction (e.g. broken paddle endangering a player)."),

    q('ch10-r1064-001n', 10, '10.6.4',
      "Under what condition should time-out be used for an injury?",
      ["Always immediately", "Only if it does not disadvantage the other team",
       "Only at the next break in play", "Only if the player cannot continue"],
      1,
      "Rule 10.6.4 states time-out should be used for injury provided this does not disadvantage the other team."),

    q('ch10-r1066-001n', 10, '10.6.6',
      "If the Referee stops play where neither team is at fault and a capsized player caused the stoppage, who gets the free throw to restart?",
      ["The team of the capsized player", "The opposition",
       "A Referee\u2019s ball is used", "The team that last had possession"],
      1,
      "Rule 10.6.6 states where time-out was given for a capsized player, the opposition is given a free throw to restart."),

    q('ch10-r1066-002n', 10, '10.6.6',
      "If the Referee stops play due to faulty goals (neither team at fault), how is play restarted?",
      ["A Referee\u2019s ball", "A free throw to the team that last had possession",
       "A centre restart", "A free shot to the defending team"],
      1,
      "Rule 10.6.6 states if the Referee stops the game where neither team was at fault, play restarts with a free throw to the team that last had possession."),

    # ── 10.7 LIVE STREAM AND TIME OUT ──
    q('ch10-r1072-001n', 10, '10.7.2',
      "If a team has not called the live stream time-out after seven minutes of the second half, what happens?",
      ["The time-out is forfeited", "The Referee will call the time-out",
       "The opposing team may call it instead", "Play continues without interruption"],
      1,
      "Rule 10.7.2 states if a time-out is not called by the team after seven minutes of the second half, the Referee will call it."),

    q('ch10-r1074-001n', 10, '10.7.4',
      "Who must authorise live-stream advertising before a World Championship?",
      ["ICF Secretary General alone",
       "ICF Chair in consultation with ICF Secretary General",
       "Continental President", "The Chief Official"],
      1,
      "Rule 10.7.4 states World Championships require authorisation by the ICF Chair in consultation with the ICF Secretary General."),

    q('ch10-r1071-001n', 10, '10.7.1',
      "How many live stream time-outs may a coach or captain call during a game?",
      ["One per half", "One per game only", "Two per game", "Unlimited"],
      1,
      "Rule 10.7.1 states the coach or captain may call a live stream time-out on one occasion ONLY during the game."),

    q('ch10-r1071-002n', 10, '10.7.1',
      "Where must the team be positioned when calling a live stream time-out?",
      ["In their own half", "In possession and outside the six-metre area",
       "Anywhere on the field", "In their substitutes\u2019 area"],
      1,
      "Rule 10.7.1 states the time-out must be called when in possession and outside the six-metre area."),

    # ── 10.8 SCORING A GOAL ──
    q('ch10-r1081-001n', 10, '10.8.1',
      "If the goal is not rigidly fixed and moves, what must happen for a goal to be scored?",
      ["The ball must cross the original goal line", "The ball must go through the goal frame",
       "The Referee decides based on the ball\u2019s trajectory", "The goal is disallowed"],
      1,
      "Rule 10.8.1 states if a goal is not rigidly fixed and moves, the ball must go through the goal frame."),

    q('ch10-r1082-001n', 10, '10.8.2',
      "A substitute\u2019s paddle enters the goal from behind and prevents the ball from entering. What is the result?",
      ["Free shot to the attacking team", "Goal penalty shot",
       "A goal is awarded", "Referee\u2019s ball"],
      2,
      "Rule 10.8.2 states if a defender\u2019s or substitute\u2019s paddle enters from behind and prevents a goal, a goal is awarded."),

    # ── 10.9 RESTART AFTER GOAL ──
    q('ch10-r1091-001n', 10, '10.9.1',
      "After a goal is scored, what is the sanction for deliberately delaying the return to their own half?",
      ["Free throw to the opposition", "A sanction card for unsporting behaviour",
       "A goal penalty shot", "A verbal warning"],
      1,
      "Rule 10.9.1 states any deliberate delay returning to their own half will be sanctioned with a sanction card for Unsporting Behaviour (Deliberate Delaying Tactics)."),

    q('ch10-r1092-001n', 10, '10.9.2',
      "How many defending players must return to their own half before the Referee can restart play after a goal?",
      ["All five", "At least four", "At least three", "At least two"],
      2,
      "Rule 10.9.2 states play can restart when at least three players of the defending team have returned to their own half."),

    q('ch10-r1093-001n', 10, '10.9.3',
      "How does the player taking the restart throw after a goal indicate they are ready?",
      ["By raising their paddle", "By holding the ball up",
       "By positioning on the goal line", "By blowing a whistle"],
      1,
      "Rule 10.9.3 states the player must be stationary and indicate readiness by holding the ball up."),

    # ── 10.10 DEFENCE OF GOAL ──
    q('ch10-r10102-001n', 10, '10.10.2',
      "What happens if a player makes contact that moves or unbalances the goalkeeper when the goalkeeper does not have the ball?",
      ["No penalty, goalkeepers can be tackled freely",
       "The player has committed an illegal tackle (Signals 10 and 15)",
       "A free throw is awarded", "A warning is given"],
      1,
      "Rule 10.10.2 states if the goalkeeper is moved or unbalanced by contact from an opposing player while not in possession, it is an illegal tackle."),

    q('ch10-r10103-001n', 10, '10.10.3',
      "An attacker pushes a defender into the goalkeeper, and no defender has the ball. Who is penalised?",
      ["The defender", "The goalkeeper", "The attacker", "No one"],
      2,
      "Rule 10.10.3 states if an attacker moves the goalkeeper by pushing a defender into them, and no defender has possession, the attacker is penalised."),

    q('ch10-r10104-001n', 10, '10.10.4',
      "A defender is pushed towards the goalkeeper but has an opportunity to avoid contact. If they don\u2019t avoid it, who is penalised?",
      ["The attacker who pushed", "The defender who didn\u2019t avoid it",
       "The goalkeeper", "The attacker is not penalised"],
      3,
      "Rule 10.10.4 states if the defender has an opportunity to avoid contact with the goalkeeper after being pushed but does not, the attacker will not be penalised."),

    q('ch10-r10105-001n', 10, '10.10.5',
      "A defender pushes an attacker onto the goalkeeper. Is the attacker penalised?",
      ["Yes, always", "Yes, if the goalkeeper is moved",
       "No, the attacker is not penalised", "Only if the attacker had the ball"],
      2,
      "Rule 10.10.5 states if a defender pushes the attacker onto the goalkeeper, the attacker will not be penalised."),

    q('ch10-r10106-001n', 10, '10.10.6',
      "An attacker is pushed by a defender towards the goalkeeper but has opportunity to avoid contact. What happens if the attacker does not avoid it?",
      ["The defender is penalised", "The attacker is penalised",
       "No foul is called", "A Referee\u2019s ball is given"],
      1,
      "Rule 10.10.6 states if the attacker has an opportunity to avoid goalkeeper contact after being pushed but does not, the attacker will be penalised."),

    q('ch10-r10107-001n', 10, '10.10.7',
      "An attacker with the ball whose original direction would not have led to goalkeeper contact is pushed onto the goalkeeper by a defender. Is the attacker penalised?",
      ["Yes, for illegal tackle", "Yes, for unsporting behaviour",
       "No, the attacker is not penalised", "Only if a goal was scored"],
      2,
      "Rule 10.10.7 states if the attacker\u2019s original direction or speed would not have led to contact with the goalkeeper, and a defender pushed them, the attacker is not penalised."),

    q('ch10-r10109-001n', 10, '10.10.9',
      "Within the six-metre area, may a defender push an attacker with their kayak to take the goalkeeper position?",
      ["No, never", "Yes, without penalty unless dangerous play is used",
       "Yes, but only with a hand push", "Only during time-out"],
      1,
      "Rule 10.10.9 states within the six-metre area, a defender may push an attacker with their kayak to take the goalkeeper position without penalty, unless dangerous play is used."),

    q('ch10-r10109-002n', 10, '10.10.9',
      "Within the six-metre area, may an attacker actively prevent a defender from becoming goalkeeper?",
      ["Yes, it is always permitted", "No, this is not allowed",
       "Only if the attacker has the ball", "Only during a power play"],
      1,
      "Rule 10.10.9 states within the six-metre area, an attacker must not actively prevent a defender from taking the goalkeeper position."),

    q('ch10-r10101-001n', 10, '10.10.1',
      "How far from the centre of the goal line must the goalkeeper attempt to maintain their position?",
      ["Within two metres", "Within one metre",
       "Directly under the centre", "Within the six-metre area"],
      1,
      "Rule 10.10.1 states the goalkeeper must be attempting to maintain a position within one metre of the centre of the goal line."),

    q('ch10-r10108-001n', 10, '10.10.8',
      "After an attacker loses possession of the ball, what must they not do regarding the goalkeeper?",
      ["Touch the goalkeeper\u2019s kayak",
       "Actively impede the goalkeeper\u2019s attempt to regain or maintain their position",
       "Enter the six-metre area", "Use their paddle near the goal"],
      1,
      "Rule 10.10.8 states after the attacker loses possession, they must not actively impede the goalkeeper\u2019s attempt to regain or maintain their position."),

    # ── 10.11 REFEREE'S BALL ──
    q('ch10-r10112-001n', 10, '10.11.2',
      "During a Referee\u2019s ball situation, when does illegal holding apply?",
      ["Whenever players touch each other",
       "Only if either player uses the opposition for support",
       "If the ball is between the players", "Never during a Referee\u2019s ball"],
      1,
      "Rule 10.11.2 states if initial contact is made directly with the ball, illegal holding only applies if either player uses the opposition for support."),

    q('ch10-r10113-001n', 10, '10.11.3',
      "The Referee stops play (not during a break) due to faulty goals and cannot determine who had possession. How is play restarted?",
      ["Free throw to the home team", "A Referee\u2019s ball",
       "A centre restart", "Free throw to the team nearest the ball"],
      1,
      "Rule 10.11.3 states if the Referee needs to stop the game where neither team is at fault and cannot determine possession, a Referee\u2019s ball restarts play."),

    q('ch10-r10116-001n', 10, '10.11.6',
      "How far must all other players be from the two players taking a Referee\u2019s ball?",
      ["One metre", "Two metres", "Three metres", "Five metres"],
      2,
      "Rule 10.11.6 states all other players must be at least three metres away from the point between the two participating players."),

    q('ch10-r10117-001n', 10, '10.11.7',
      "During a Referee\u2019s ball, when may the players play the ball?",
      ["As soon as the Referee throws it", "As soon as it touches the water",
       "After the Referee blows the whistle", "After counting to three"],
      1,
      "Rule 10.11.7 states players must make an attempt for the ball with their hands as soon as it touches the water. They must not play it before it hits the water."),

    q('ch10-r10117-002n', 10, '10.11.7',
      "At a Referee\u2019s ball, must both players attempt for the ball?",
      ["No, only one needs to", "Yes, both must make an attempt with their hands",
       "Only the player nearest their own goal", "It is optional"],
      1,
      "Rule 10.11.7 states both players must make an attempt for the ball with their hands as soon as it touches the water."),

    q('ch10-r10114-001n', 10, '10.11.4',
      "Where is a Referee\u2019s ball normally taken?",
      ["At the centre of the field",
       "At the nearest point on the sideline to the incident",
       "Where the incident occurred", "At the six-metre line"],
      1,
      "Rule 10.11.4 states a Referee\u2019s ball is taken at the nearest point on the sideline to the incident."),

    # ── 10.12 ADVANTAGE ──
    q('ch10-r10123-001n', 10, '10.12.3',
      "While playing advantage, when must the Referee call back the original infringement?",
      ["After five seconds automatically",
       "If the next pass or shot is affected by the foul or there is no clear advantage",
       "Only if the other team complains",
       "Never, advantage always continues"],
      1,
      "Rule 10.12.3 states if the next pass or shot is affected by the original foul or there is no clear advantage, the original infringement must be called."),

    q('ch10-r10121-001n', 10, '10.12.1',
      "How must referees signal while playing advantage?",
      ["By blowing a short whistle",
       "By calling \u2018play on\u2019 and signalling throughout up to five seconds",
       "By raising a flag", "By not signalling at all"],
      1,
      "Rule 10.12.1 states referees must call \u2018play on\u2019 and signal throughout the time they are playing advantage, up to a maximum of five seconds."),

    # ── 10.13 CAPSIZED PLAYER ──
    q('ch10-r10132-001n', 10, '10.13.2',
      "How must a capsized player who wishes to re-join the game do so?",
      ["By re-entering from any point on the sideline",
       "According to the rules of entry to the field of play",
       "By waiting until the next time-out",
       "By getting permission from the Referee"],
      1,
      "Rule 10.13.2 states a capsized player must re-join according to the rules of entry to the field of play."),

    q('ch10-r10131-001n', 10, '10.13.1',
      "A player capsizes and leaves their kayak. May they touch the ball?",
      ["Yes, they can still play the ball with their hands",
       "No, they may not take any further part in play and must leave immediately",
       "Yes, but only to pass it to a teammate",
       "Only if they are within arm\u2019s reach"],
      1,
      "Rule 10.13.1 states a capsized player who leaves their kayak may not take any further part in play and must leave the playing area immediately with all equipment."),

    # ── 10.14 ENTRY, RE-ENTRY, SUBSTITUTION ──
    q('ch10-r10141-001n', 10, '10.14.1',
      "What is the maximum number of players from one team allowed on the playing area?",
      ["Four", "Five", "Six", "Eight"],
      1,
      "Rule 10.14.1 states no more than the legally allowed number of players (five) may be on the playing area at any one time."),

    q('ch10-r10142-001n', 10, '10.14.2',
      "Where must substitutes wait during a game?",
      ["Behind the sideline", "In their own substitute\u2019s area",
       "At the centre line", "In the spectator area"],
      1,
      "Rule 10.14.2 states substitutes must wait in their own substitute\u2019s area."),

    q('ch10-r10144-001n', 10, '10.14.4',
      "A capsized player exits the playing area at the sideline (not their goal line). When can they be substituted?",
      ["Immediately", "At the next break in play",
       "After two minutes", "They cannot be substituted"],
      1,
      "Rule 10.14.4 states a capsized player who leaves anywhere other than at their own goal line can only be substituted at the next break in play."),

    q('ch10-r10144-002n', 10, '10.14.4',
      "Before a capsized player who exited at the sideline can be substituted, what must happen?",
      ["The Referee must give permission",
       "All of the capsized player\u2019s equipment must be removed from the playing area",
       "A time-out must be called", "The team captain must request it"],
      1,
      "Rule 10.14.4 states all of the capsized player\u2019s equipment must be removed from the playing area before substitution is allowed."),

    q('ch10-r10145-001n', 10, '10.14.5',
      "Where must a player collect equipment being exchanged during a game?",
      ["From anywhere along the sideline", "From their substitute\u2019s area",
       "From the official\u2019s table", "From behind their own goal line"],
      1,
      "Rule 10.14.5 states the player must collect equipment being exchanged from their substitute\u2019s area."),

    q('ch10-r10143-001n', 10, '10.14.3',
      "Along which line must exit and entry for substitution occur?",
      ["The sideline", "The centre line",
       "The team\u2019s own goal line", "Any boundary line"],
      2,
      "Rule 10.14.3 states exit and entry for substitution may be anywhere along the team\u2019s own goal line."),

    # ── 10.16 COMPLETION OF PLAY ──
    q('ch10-r10163-001n', 10, '10.16.3',
      "When must all team members leave the playing area after their game?",
      ["Within five minutes", "Immediately upon completion",
       "After the next game begins", "When instructed by the Referee"],
      1,
      "Rule 10.16.3 states all members and officials must leave the playing, substitute and officials areas immediately upon completion of their game."),

    q('ch10-r10164-001n', 10, '10.16.4',
      "What must teams ensure about their equipment after a game?",
      ["It is locked away", "It is removed from the playing, substitute and officials areas",
       "It is inspected by the Scrutineer", "It is handed to the officials"],
      1,
      "Rule 10.16.4 states teams must ensure all their equipment is removed from these areas."),

    q('ch10-r10161-001n', 10, '10.16.1',
      "For a goal to count at the end of a period, when must the ball have left the player\u2019s hand?",
      ["Before the Referee\u2019s final whistle", "Prior to the timekeeper\u2019s signal sounding",
       "Within five seconds of the signal", "Before the ball crosses the goal line"],
      1,
      "Rule 10.16.1 states for a goal to be scored, the ball must have left the player\u2019s hand prior to the timekeeper\u2019s signal sounding."),

    # ── 10.19 ILLEGAL USE OF PADDLE ──
    q('ch10-r10191-001n', 10, '10.19.1',
      "Which signals apply for illegal use of paddle?",
      ["Signals 10 and 15", "Signals 12 and 15",
       "Signals 9 and 15", "Signals 11 and 14"],
      1,
      "Rule 10.19.1 states Signals 12 and 15 apply for illegal use of paddle."),

    q('ch10-r10192-001n', 10, '10.19.2',
      "Which of the following is an illegal use of paddle?",
      ["Blocking a shot with the paddle blade flat on the water",
       "Contacting an opponent\u2019s person with the paddle",
       "Using the paddle to splash water", "Holding the paddle above shoulder height"],
      1,
      "Rule 10.19.2 defines contacting an opponent\u2019s person as illegal use of paddle."),

    q('ch10-r10194-001n', 10, '10.19.4',
      "Is it legal to play the ball with a paddle across the bow of an opponent\u2019s kayak within arm\u2019s reach?",
      ["Yes, always", "No, it is illegal use of paddle",
       "Only if the opponent has the ball", "Only if the goalkeeper does it"],
      1,
      "Rule 10.19.4 defines playing or attempting to play the ball with a paddle across the bow of an opponent\u2019s kayak within arm\u2019s reach as illegal."),

    q('ch10-r10196-001n', 10, '10.19.6',
      "Using your paddle to restrict an opponent who is using their paddle is an example of what offence?",
      ["Illegal holding", "Illegal use of paddle",
       "Illegal obstruction", "Unsporting behaviour"],
      1,
      "Rule 10.19.6 defines using a paddle to restrict an opponent\u2019s paddle as illegal use of paddle."),

    q('ch10-r10197-001n', 10, '10.19.7',
      "Playing an opponent\u2019s paddle instead of the ball is classified as what?",
      ["Illegal holding", "Illegal kayak tackle",
       "Illegal use of paddle", "Unsporting behaviour"],
      2,
      "Rule 10.19.7 defines playing an opponent\u2019s paddle instead of the ball as illegal use of paddle."),

    q('ch10-r10199-001n', 10, '10.19.9',
      "Which catch-all rule covers any paddle use that endangers a player?",
      ["10.19.2 \u2014 contacting opponent\u2019s person",
       "10.19.9 \u2014 any other use of paddle that endangers a player",
       "10.26.2 \u2014 unsporting behaviour",
       "10.22.3 \u2014 illegal kayak tackle"],
      1,
      "Rule 10.19.9 covers any other use of a paddle that endangers a player."),

    q('ch10-r10195-001n', 10, '10.19.5',
      "Under what condition may a goalkeeper place their paddle within arm\u2019s reach of an opponent who has the ball?",
      ["Never, goalkeepers follow the same rules",
       "When directly defending a shot, provided the paddle is not moved towards the opponent and no significant contact results",
       "Only during a goal penalty shot",
       "Only within the six-metre area"],
      1,
      "Rule 10.19.5 states a goalkeeper may defend a shot provided the paddle is not moved towards the opponent at the time of the shot and it does not result in significant contact."),

    # ── 10.20 ILLEGAL POSSESSION ──
    q('ch10-r10204-001n', 10, '10.20.4',
      "When is a capsized player considered to have lost possession?",
      ["Whenever they capsize", "When their whole body and head go under water and the ball is not in their hand",
       "When any part of their body is underwater", "When the Referee blows the whistle"],
      1,
      "Rule 10.20.4 states a player who capsizes to the point of their whole body and head going under water is considered to have lost possession if the ball is not in their hand(s)."),

    q('ch10-r10205-001n', 10, '10.20.5',
      "May a player manoeuvre their kayak with their hands while the ball is on their spray deck?",
      ["Yes, freely", "No, this is illegal possession",
       "Only to move towards their own goal", "Only during time-out"],
      1,
      "Rule 10.20.5 states a player must not manoeuvre their kayak with their hands or paddle while the ball is resting on their spray deck."),

    q('ch10-r10206-001n', 10, '10.20.6',
      "May a player actively paddle with two hands on the paddle while carrying the ball?",
      ["Yes, as long as they throw within five seconds",
       "No, this is illegal possession",
       "Only if moving towards their own half",
       "Only the goalkeeper may do this"],
      1,
      "Rule 10.20.6 states a player must not actively paddle or manoeuvre their kayak with two hands on the paddle while carrying the ball."),

    q('ch10-r10201-001n', 10, '10.20.1',
      "When is a player considered to be in possession of the ball when it is on the water?",
      ["Only when holding it in their hand",
       "When they can reach the ball with their hand and it is on the water, not in the air",
       "When they are within three metres of the ball",
       "When the Referee indicates possession"],
      1,
      "Rule 10.20.1 states a player is in possession when they have the ball in their hand or are in a position to reach it with their hand, the ball being on the water and not in the air."),

    q('ch10-r10202-001n', 10, '10.20.2',
      "What is the minimum distance the ball must travel horizontally when a player disposes of it?",
      ["Half a metre", "One metre", "Two metres", "Three metres"],
      1,
      "Rule 10.20.2 states the ball must travel at least one metre measured horizontally from the point of release."),

    # ── 10.22 ILLEGAL KAYAK TACKLE ──
    q('ch10-r10221-001n', 10, '10.22.1',
      "Which signals apply for an illegal kayak tackle?",
      ["Signals 9 and 15", "Signals 10 and 15",
       "Signals 12 and 15", "Signals 19 and 15"],
      1,
      "Rule 10.22.1 states Signals 10 and 15 apply for illegal kayak tackle."),

    q('ch10-r10222-001n', 10, '10.22.2',
      "What is the purpose of a kayak tackle?",
      ["To capsize an opponent", "To gain possession of the ball",
       "To slow down an opponent", "To defend the goal"],
      1,
      "Rule 10.22.2 defines a kayak tackle as manoeuvring a kayak against an opponent\u2019s kayak in an attempt to gain possession of the ball."),

    q('ch10-r10223-001n', 10, '10.22.3',
      "Under rule 10.22.3.e, how far from the ball must a player be for a kayak tackle on them to be illegal?",
      ["More than one metre", "More than two metres",
       "More than three metres", "More than six metres"],
      2,
      "Rule 10.22.3.e makes it illegal to tackle an opponent who is not within three metres of the ball."),

    # ── 10.23 ILLEGAL JOSTLE ──
    q('ch10-r10233-001n', 10, '10.23.3',
      "When does contact during a jostle become an illegal kayak tackle?",
      ["When the player is moved more than two metres",
       "When the contact would be defined as illegal under any section of rule 10.22",
       "When the jostled player falls in the water",
       "When it occurs outside the six-metre area"],
      1,
      "Rule 10.23.3 states a jostle becomes illegal when the contact would be defined as an illegal kayak tackle under any section of rule 10.22."),

    q('ch10-r10231-001n', 10, '10.23.1',
      "A jostle can only occur in which area of the field?",
      ["Anywhere on the field",
       "Between the six-metre line and the goal line at the attacking end",
       "Within the six-metre area only",
       "Along the sidelines"],
      1,
      "Rule 10.23.1 defines a jostle as occurring between the six-metre line and the goal line, at the attacking end of the field."),

    # ── 10.24 ILLEGAL OBSTRUCTION ──
    q('ch10-r10241-001n', 10, '10.24.1',
      "Which signals apply for illegal obstruction?",
      ["Signals 10 and 15", "Signals 12 and 15",
       "Signals 9 and 15", "Signals 19 and 15"],
      2,
      "Rule 10.24.1 states Signals 9 and 15 apply for illegal obstruction."),

    # ── 10.25 ILLEGAL HOLDING ──
    q('ch10-r10251-001n', 10, '10.25.1',
      "Which signals apply for illegal holding?",
      ["Signals 10 and 15", "Signals 19 and 15",
       "Signals 12 and 15", "Signals 9 and 15"],
      1,
      "Rule 10.25.1 states Signals 19 and 15 apply for illegal holding."),

    q('ch10-r10252-001n', 10, '10.25.2',
      "Is it legal to use the goal supports for propulsion or support?",
      ["Yes, they are part of the playing area",
       "No, using playing area equipment for propulsion or support is illegal holding",
       "Only the goalkeeper may do this",
       "Only during a goal penalty shot"],
      1,
      "Rule 10.25.2.b states using for propulsion or support, or moving any playing area equipment (e.g. goal supports) is illegal holding."),

    q('ch10-r10252-002n', 10, '10.25.2',
      "A player uses their paddle to lift an opponent\u2019s kayak while jostling in the six-metre area. What offence is this?",
      ["Illegal kayak tackle", "Illegal holding",
       "Illegal use of paddle", "Illegal jostle"],
      1,
      "Rule 10.25.2.c defines using a paddle to lift, pull or hold an opponent\u2019s kayak while jostling in the six-metre area as illegal holding."),

    # ── 10.26 UNSPORTING BEHAVIOUR ──
    q('ch10-r10261-001n', 10, '10.26.1',
      "Which signals apply for unsporting behaviour?",
      ["Signals 12 and 15", "Signals 9 and 15",
       "Signals 17 and 18 with appropriate sanction card", "Signal 16"],
      2,
      "Rule 10.26.1 states Signal 17 and 18 with appropriate sanction card applies for unsporting behaviour."),

    q('ch10-r10262-001n', 10, '10.26.2',
      "Which of the following is classified as unsporting behaviour?",
      ["A hard but legal kayak tackle",
       "Bouncing the ball out of play off an opponent\u2019s kayak to gain advantage",
       "A legal hand tackle to the back",
       "Calling for the ball during play"],
      1,
      "Rule 10.26.2.i defines bouncing the ball out of play off an opponent\u2019s kayak to gain advantage as unsporting behaviour."),

    q('ch10-r10262-002n', 10, '10.26.2',
      "Any infringement committed during a break in play is classified as what?",
      ["Illegal play", "Unsporting behaviour",
       "Dishonourable play", "A technical foul"],
      1,
      "Rule 10.26.2.a states any infringement committed by a player during a break in play is unsporting behaviour."),

    q('ch10-r10262-003n', 10, '10.26.2',
      "Is pretending or feigning injury considered unsporting behaviour?",
      ["No, it is dishonourable play", "Yes, it is unsporting behaviour",
       "No, it is not penalised", "Only if the Referee saw it"],
      1,
      "Rule 10.26.2.h includes pretending or feigning injury as unsporting behaviour at the Referee\u2019s discretion."),

    # ── 10.27 DISHONOURABLE PLAY ──
    q('ch10-r10272-001n', 10, '10.27.2',
      "What is the maximum consequence for a team playing by dishonourable means?",
      ["A free shot to the opposition", "A sanction card to the captain",
       "Disqualification from the competition", "A verbal warning"],
      2,
      "Rule 10.27.2 states the Competition Committee may take whatever action it sees fit and the team may be disqualified from the competition."),

    # ── 10.28 SANCTIONS \u2013 DEFINITIONS ──
    q('ch10-r10281-001n', 10, '10.28.1',
      "May a Referee impose multiple different types of sanctions for a single offence?",
      ["No, only one sanction per offence",
       "Yes, any combination depending on severity and frequency",
       "Only if the Competition Committee agrees",
       "Only for dangerous fouls"],
      1,
      "Rule 10.28.1 states the Referee can impose any combination of sanctions depending on severity and/or frequency."),

    q('ch10-r10283-001n', 10, '10.28.3',
      "Under rule 10.28.3.f, how is \u2018control of the ball\u2019 defined?",
      ["Having the ball in your hand only",
       "Being in possession or being the nearest player within three metres of the ball on the water",
       "Being within six metres of the ball",
       "Any player on the attacking team"],
      1,
      "Rule 10.28.3.f states a player has control if in possession or is the nearest player to the ball and within three metres of it on the water."),

    q('ch10-r10283-002n', 10, '10.28.3',
      "What does \u2018significant contact\u2019 mean under the sanctions definitions?",
      ["Any physical contact",
       "Any hard contact that may result in equipment damage or personal injury",
       "Contact that moves a player more than two metres",
       "Contact that results in a capsize"],
      1,
      "Rule 10.28.3.c defines significant contact as any hard contact that may result in equipment damage or personal injury."),

    q('ch10-r10283-003n', 10, '10.28.3',
      "For a Referee to award a \u2018near certain goal\u2019, what standard of certainty is required?",
      ["The Referee thinks it was likely", "The Referee must be certain a goal was the most likely result",
       "Two out of three officials must agree", "The ball must have been within two metres of the goal"],
      1,
      "Rule 10.28.3.e states the Referee must be certain that a goal was the most likely end result if play had continued."),

    # ── 10.29 GOAL PENALTY SHOT ──
    q('ch10-r10291-001n', 10, '10.29.1',
      "Which signal applies for a goal penalty shot?",
      ["Signal 15", "Signal 16",
       "Signal 17", "Signal 14"],
      1,
      "Rule 10.29.1 states Signal 16 and time-out applies for a goal penalty shot."),

    q('ch10-r10293-001n', 10, '10.29.3',
      "Inside the six-metre area, a deliberate foul is committed on a player passing for a near-certain goal. What is awarded?",
      ["A free shot", "A free throw",
       "A goal penalty shot", "A sanction card only"],
      2,
      "Rule 10.29.3 states inside the six-metre area, a goal penalty shot is awarded for any deliberate or dangerous foul on a player in the act of passing or positioning for a near-certain goal."),

    q('ch10-r10294-001n', 10, '10.29.4',
      "Inside the six-metre area, a deliberate foul is committed on a player attempting to take a free shot. What is awarded?",
      ["Another free shot", "A goal penalty shot",
       "A free throw", "A sanction card only"],
      1,
      "Rule 10.29.4 states inside the six-metre area, a goal penalty shot is awarded for a deliberate or dangerous foul on a player attempting to take a free shot."),

    q('ch10-r10296-001n', 10, '10.29.6',
      "Outside the six-metre area, when is a goal penalty shot awarded for a foul on a player who is passing?",
      ["Always for any foul on a passer",
       "For any deliberate or dangerous foul while passing or positioning for a near-certain goal with the goal undefended",
       "Never, goal penalty shots are only for shooting fouls",
       "Only when a sanction card is also given"],
      1,
      "Rule 10.29.6 states outside the six-metre area, a GPS is awarded for any deliberate or dangerous foul on a player passing or positioning for a near-certain goal while the goal is not defended."),

    # ── 10.30 FREE SHOT ──
    q('ch10-r10301-001n', 10, '10.30.1',
      "Which signal applies for a free shot?",
      ["Signal 14", "Signal 15", "Signal 16", "Signal 17"],
      1,
      "Rule 10.30.1 states Signal 15 applies for a free shot."),

    # ── 10.31 FREE THROW ──
    q('ch10-r10311-001n', 10, '10.31.1',
      "Which signal applies for a free throw?",
      ["Signal 14", "Signal 15", "Signal 16", "Signal 17"],
      0,
      "Rule 10.31.1 states Signal 14 applies for a free throw."),

    q('ch10-r10313-001n', 10, '10.31.3',
      "When is a free throw awarded?",
      ["Only for ball out of play",
       "For any ball out of play, or when a goal penalty shot or free shot has not been awarded",
       "Only when the Referee stops play",
       "For any minor infringement"],
      1,
      "Rule 10.31.3 states a free throw is awarded for any ball out of play, or when a goal penalty shot or free shot has not been awarded."),

    q('ch10-r10312-001n', 10, '10.31.2',
      "What happens if a player takes a direct shot at goal from a free throw?",
      ["The goal counts", "The shot is retaken",
       "The opposition is awarded a free throw (Signals 11 and 14)", "A sanction card is given"],
      2,
      "Rule 10.31.4 states a free throw cannot be a direct shot at goal; infringement incurs a sanction with the opposition awarded a free throw."),

    # ── 10.32 SANCTION CARD SYSTEM ──
    q('ch10-r10321-001n', 10, '10.32.1',
      "Do sanction cards apply to the team or the individual?",
      ["The team", "The individual only",
       "Both team and individual", "The team captain"],
      1,
      "Rule 10.32.1 states sanction cards relate only to an individual."),

    q('ch10-r10324-001n', 10, '10.32.4',
      "Can a Referee skip directly to a yellow or red card without issuing a green first?",
      ["No, cards must follow the green-yellow-red sequence",
       "Yes, for any deliberate foul of major influence to the game",
       "Only for violent conduct",
       "Only with Competition Committee approval"],
      1,
      "Rule 10.32.4 states a referee may move straight to the 2nd or 3rd card level for any deliberate foul of major influence."),

    q('ch10-r10325-001n', 10, '10.32.5',
      "Can a player who receives a Red or Ejection Red Card during a competition be referred for further action?",
      ["No, the card is the final sanction",
       "Yes, either Referee may refer the player to the Competition Committee",
       "Only the Chief Official may refer them",
       "Only for Ejection Red Cards"],
      1,
      "Rule 10.32.5 states either Referee may refer a player receiving a Red or Ejection Red Card to the Competition Committee for further disciplinary action."),

    # ── 10.33 POWER PLAY ──
    q('ch10-r10331-001n', 10, '10.33.1',
      "Can a player sent off with an Ejection Red Card be replaced for the remainder of the game?",
      ["Yes, after two minutes", "No, they cannot be replaced",
       "Yes, at the next break in play", "Yes, but only by the captain"],
      1,
      "Rule 10.33.1 states a player receiving an Ejection Red Card is sent off for the rest of the game and cannot be replaced."),

    q('ch10-r10333-001n', 10, '10.33.3',
      "How long is a player excluded for when receiving their third sanction card?",
      ["One minute", "Two minutes",
       "Five minutes", "The rest of the game"],
      1,
      "Rule 10.33.3 states a player receiving their 3rd sanction card is excluded and cannot be replaced for two minutes."),

    q('ch10-r10335-001n', 10, '10.33.5',
      "Is the power play timer running during time-outs or between periods?",
      ["Yes, it always runs",
       "No, timing is suspended during time-outs and between periods",
       "Only during half-time", "Only during injury time-outs"],
      1,
      "Rule 10.33.5 states timing of the power play is suspended for periods of time-out or between periods of play."),

    q('ch10-r10336-001n', 10, '10.33.6',
      "Two players from the same team are excluded. The opposition scores. How many excluded players may return?",
      ["Both", "Only the first excluded player (or a non-excluded teammate)",
       "Neither, both must serve full time", "The team captain decides"],
      1,
      "Rule 10.33.6 states only the first excluded player or a non-excluded teammate can return. The remaining power play must be served in full."),

    # ── 10.34 EJECTION RED CARD ──
    q('ch10-r10341-001n', 10, '10.34.1',
      "What verbal statement must accompany an Ejection Red Card?",
      ["\u2018Red card\u2019", "\u2018You are out\u2019",
       "\u2018Ejection red\u2019", "\u2018Sent off\u2019"],
      2,
      "Rule 10.34.1 states Signal 20 with red card and verbal statement \u2018ejection red\u2019 to the player applies."),

    q('ch10-r10343-001n', 10, '10.34.3',
      "When should an Ejection Red Card be awarded (rather than must)?",
      ["For any deliberate foul",
       "For a repeated deliberate or dangerous foul of major influence to the game or that injuries/risks injury",
       "For any third card offence",
       "For any foul inside the six-metre area"],
      1,
      "Rule 10.34.3 states an Ejection Red Card should be awarded for a repeated deliberate or dangerous foul of major influence or that injures/risked injury."),

    q('ch10-r10345-001n', 10, '10.34.5',
      "Threatening, abusive or aggressive behaviour towards a referee during or after a game results in what?",
      ["A green card warning", "A yellow card",
       "An Ejection Red Card", "Referral to the Competition Committee only"],
      2,
      "Rule 10.34.5 states an Ejection Red Card will be awarded for threatening, abusive or aggressive behaviour towards any referee or game official."),

    # ── 10.35 GREEN, YELLOW AND RED SANCTION CARDS ──
    q('ch10-r10351-001n', 10, '10.35.1',
      "Which signal applies when awarding sanction cards?",
      ["Signal 16", "Signal 15",
       "Signal 17 with appropriate card", "Signal 18"],
      2,
      "Rule 10.35.1 states Signal 17 with appropriate card applies."),

    q('ch10-r10352-001n', 10, '10.35.2',
      "For which type of foul is a sanction card awarded under rule 10.35.2?",
      ["Any single foul", "A repeated deliberate foul or one with significant influence on the game",
       "Only dangerous fouls", "Only fouls inside the six-metre area"],
      1,
      "Rule 10.35.2 states a sanction card is awarded for a repeated deliberate foul or a deliberate foul with significant influence on the game."),

    q('ch10-r10353-001n', 10, '10.35.3',
      "A dangerous foul results in significant contact with an opponent\u2019s head. Is a sanction card awarded?",
      ["No, unless it is deliberate",
       "Yes, a sanction card is awarded for any dangerous foul with significant contact to arm, head or body",
       "Only a verbal warning", "Only if the player is injured"],
      1,
      "Rule 10.35.3 states a sanction card is awarded for a dangerous foul that results in significant contact with the opponent\u2019s arm, head or body."),

    q('ch10-r10354-001n', 10, '10.35.4',
      "Is a sanction card automatically awarded when a goal penalty shot is given?",
      ["No, only if the foul was dangerous",
       "Yes, for any deliberate or dangerous foul that results in a goal penalty shot",
       "Only if the goal penalty shot is missed",
       "Only at the Referee\u2019s discretion"],
      1,
      "Rule 10.35.4 states a sanction card will be awarded to the offending player for any deliberate or dangerous foul for which a goal penalty shot is awarded."),

    q('ch10-r10357-001n', 10, '10.35.7',
      "Repeatedly and continuously disputing Referee decisions results in what sanction?",
      ["A verbal warning", "A free throw to the opposition",
       "A sanction card", "An Ejection Red Card"],
      2,
      "Rule 10.35.7 states a sanction card will be awarded for repeated and continuous disputing of Referee\u2019s decisions."),

    q('ch10-r10358-001n', 10, '10.35.8',
      "Foul or abusive language directed at an opponent or official results in what?",
      ["A verbal warning", "A sanction card",
       "An automatic Ejection Red Card", "A free shot to the opposition"],
      1,
      "Rule 10.35.8 states a sanction card will be awarded for foul or abusive language directed at an opponent or official."),

    q('ch10-r10359-001n', 10, '10.35.9',
      "Unnecessary verbal communication directed at a Referee results in what?",
      ["No penalty", "A sanction card (unless an Ejection Red Card is given)",
       "An automatic Ejection Red Card", "A free throw"],
      1,
      "Rule 10.35.9 states a sanction card will be awarded for unnecessary verbal communication directed at a Referee, except where an Ejection Red Card is awarded."),

    # ── 10.36 TEAM OFFICIALS AND COACHES ──
    q('ch10-r10362-001n', 10, '10.36.2',
      "May other team officials (not the coach or captain) communicate with the referees?",
      ["Yes, at any time", "No, other team officials must not communicate with the referees",
       "Only at half-time", "Only through the team captain"],
      1,
      "Rule 10.36.2 states other team officials must not communicate with the referees."),

    q('ch10-r10363-001n', 10, '10.36.3',
      "May a coach leave the coaches\u2019 area during play?",
      ["Yes, at any time", "No, except where an Ejection Red Card is awarded",
       "Only during time-outs", "Only to assist an injured player"],
      1,
      "Rule 10.36.3.c states a coach must not leave the coaches\u2019 area during play except where an Ejection Red Card is awarded."),

    q('ch10-r10365-001n', 10, '10.36.5',
      "When can the one green card for coaches be issued?",
      ["Only immediately", "Only at the next break in play",
       "Either immediately or at the next break in play, at the Referee\u2019s discretion",
       "At half-time only"],
      2,
      "Rule 10.36.5 states the green card will be issued either immediately or at the next break in play at the Referee\u2019s discretion."),

    q('ch10-r10366-001n', 10, '10.36.6',
      "Is the one green card for coaches a warning with exclusion or without?",
      ["With exclusion for two minutes", "Without exclusion",
       "With exclusion for one minute", "Depends on severity"],
      1,
      "Rule 10.36.6 states the one green card is a warning without exclusion."),

    q('ch10-r10368-001n', 10, '10.36.8',
      "A coach receives an Ejection Red Card. What must they do immediately?",
      ["Return to the bench quietly",
       "Leave the competition area and cannot be replaced",
       "Wait in the substitutes\u2019 area",
       "Apologise to the referee"],
      1,
      "Rule 10.36.8 states the coach must immediately leave the competition area and cannot be replaced."),

    q('ch10-r10369-001n', 10, '10.36.9',
      "What happens if a coach refuses to leave the competition area after an Ejection Red Card?",
      ["The team receives a penalty",
       "The Referees will abandon the game and refer it to the Competition Committee",
       "The police are called",
       "The game continues without consequence"],
      1,
      "Rule 10.36.9 states if the individual refuses to leave, the Referees will abandon the game and refer it to the Competition Committee."),

    q('ch10-r103610-001n', 10, '10.36.10',
      "A team coach receives an Ejection Red Card. What automatic suspension do they receive?",
      ["No suspension beyond the current game",
       "A one-game suspension in that competition",
       "A three-game suspension",
       "Suspension for the entire competition"],
      1,
      "Rule 10.36.10 states a coach receiving an Ejection Red Card automatically receives a one-game suspension."),

    # ── 10.37 TAKING THROWS ──
    q('ch10-r10372-001n', 10, '10.37.2',
      "When taking a free throw or free shot, may opponents contact the player or their equipment before the ball is in play?",
      ["Yes, they can challenge immediately",
       "No, the player must be allowed to take up position without contact until the ball is in play",
       "Only with their kayak, not hands",
       "Only after the ball is held up"],
      1,
      "Rule 10.37.2 states no opponent may prevent the player from taking up position or contact them or their equipment until the ball is back in play."),

    q('ch10-r10374-001n', 10, '10.37.4',
      "From when do the five seconds for a restart throw begin?",
      ["From when the Referee blows the whistle",
       "From when any member of the team is in position to pick up the ball and take the throw",
       "From when the ball is placed on the water",
       "From when the player picks up the ball"],
      1,
      "Rule 10.37.4 states the five seconds apply from when any member of the team is in a position to pick up the ball and take the throw."),

    q('ch10-r10375-001n', 10, '10.37.5',
      "After an infringement, where is the free shot or throw taken?",
      ["Always where the infringement occurred",
       "Where the infringement occurred, where the ball was, or where the ball landed \u2014 whichever most advantages the team",
       "At the nearest sideline",
       "At the six-metre line"],
      1,
      "Rule 10.37.5 states the Referee will choose where the infringement occurred, where the ball was, or where it landed \u2014 whichever most advantages the team."),

    q('ch10-r10371-001n', 10, '10.37.1',
      "Before taking any throw, the player must be in the correct position and what?",
      ["Moving towards the opposition", "Stationary",
       "Facing the Referee", "Within the six-metre area"],
      1,
      "Rule 10.37.1 states the player taking any throw must be in the correct position and stationary before taking the throw."),

    # ── 10.38 TAKING A GOAL PENALTY SHOT ──
    q('ch10-r10381-001n', 10, '10.38.1',
      "A goal penalty shot is a shot between how many players?",
      ["One attacker and the goalkeeper only", "Two attackers and the goalkeeper",
       "One attacker and two defenders", "The entire team and the goalkeeper"],
      0,
      "Rule 10.38.1.b states a Goal Penalty Shot is a shot at goal between one attacking player and one goalkeeper."),

    q('ch10-r10382-001n', 10, '10.38.2',
      "When does general play resume after a goal penalty shot?",
      ["Immediately after the whistle", "After the shot at goal has been attempted",
       "After a centre restart", "After a time-out"],
      1,
      "Rule 10.38.2 states general play resumes after the shot at goal has been attempted."),

    q('ch10-r10384-001n', 10, '10.38.4',
      "Where must all other players be positioned during a goal penalty shot?",
      ["Behind the centre line", "Behind the six-metre line",
       "In the substitutes\u2019 area", "At least three metres from the shooter"],
      1,
      "Rule 10.38.4 states all other players and equipment must be positioned behind the six-metre line."),

    q('ch10-r10384-002n', 10, '10.38.4',
      "What happens if a player enters the six-metre area before the goal penalty shot is taken and the shot does not score?",
      ["Play continues", "The penalty is retaken and a sanction card is given",
       "A free throw is given instead", "The goal is awarded"],
      1,
      "Rule 10.38.4 states entry into the six-metre area before the shot results in the penalty being retaken if not scored, plus a sanction card."),

    q('ch10-r10385-001n', 10, '10.38.5',
      "Must the player taking a goal penalty shot present the ball before shooting?",
      ["Yes, they must hold it above shoulder level",
       "No, no presentation is required",
       "Yes, for at least two seconds",
       "Only if the Referee requests it"],
      1,
      "Rule 10.38.5 states no presentation of the ball is required for a goal penalty shot."),

    q('ch10-r10388-001n', 10, '10.38.8',
      "Must the player who committed the foul resulting in a goal penalty shot receive a sanction card?",
      ["No, only if the foul was dangerous",
       "Yes, a sanction card must be given (or Ejection Red if appropriate)",
       "Only if they have a previous card",
       "At the Referee\u2019s discretion"],
      1,
      "Rule 10.38.8 states the person committing the foul that caused the penalty must be given a sanction card."),

    # ═══════════════════════════════════════════════════════════════════════
    # CHAPTER 17 — SHOT CLOCK
    # ═══════════════════════════════════════════════════════════════════════

    # ── 17.1 DEFINITION ──
    q('ch17-r1711-001', 17, '17.1.1',
      "Which of the following qualifies as a shot at goal for shot clock purposes?",
      ["A shot that is blocked by any defender", "A shot that falls short and stays in play",
       "A shot that rebounds off the goal frame", "A pass that crosses the goal line"],
      2,
      "Rule 17.1.1 lists shots that rebound off the goal frame as qualifying shots at goal."),

    q('ch17-r1711-002', 17, '17.1.1',
      "A shot misses the goal and goes out of play. How far either side of the goal must it go out within to count as a shot at goal?",
      ["Two metres", "Three metres", "Four metres", "Six metres"],
      2,
      "Rule 17.1.1 states a shot that misses the goal counts if it goes out of play within four metres either side of the goal."),

    q('ch17-r1712-001', 17, '17.1.2',
      "How many seconds does a team have to attempt a shot at goal after gaining possession?",
      ["30 seconds", "45 seconds", "60 seconds", "90 seconds"],
      2,
      "Rule 17.1.2 states a team must attempt a shot at goal within 60 seconds of gaining possession or control."),

    q('ch17-r1712-002', 17, '17.1.2',
      "After January 2027, if a team retains possession after a shot, how long do they have for subsequent shots?",
      ["60 seconds again", "45 seconds", "30 seconds", "20 seconds"],
      2,
      "Rule 17.1.2.a states after January 2027, subsequent shots after retaining possession must be made within 30 second periods."),

    q('ch17-r1713-001', 17, '17.1.3',
      "What is the consequence of failing to attempt a shot within the shot clock period?",
      ["A free throw to the other team",
       "Possession and a free shot awarded to the other team",
       "A goal penalty shot to the other team",
       "A Referee\u2019s ball"],
      1,
      "Rule 17.1.3 states failure results in possession and a free shot being awarded to the other team."),

    q('ch17-r1714-001', 17, '17.1.4',
      "Where is the free shot taken when the shot clock expires?",
      ["At the centre line", "Where the ball is at the time of expiry",
       "At the six-metre line", "At the nearest sideline"],
      1,
      "Rule 17.1.4 states the free shot is taken where the ball is at the time of the shot clock expiring."),

    q('ch17-r1715-001', 17, '17.1.5',
      "If the ball is out of play when the shot clock expires, where is the free shot taken?",
      ["At centre", "From the closest point to where the ball went out",
       "Where the ball was last in play", "At the goal line"],
      1,
      "Rule 17.1.5 states the free shot is taken from the closest point to where the ball went out of play."),

    # ── 17.2 OPERATION ──
    q('ch17-r1721-001', 17, '17.2.1',
      "Who operates the shot clock?",
      ["The Referee", "The timekeeper",
       "A dedicated shot clock operator", "The Scorekeeper"],
      1,
      "Rule 17.2.1 states the shot clock will be operated by the timekeeper."),

    q('ch17-r1722-001', 17, '17.2.2',
      "When does the shot clock stop?",
      ["Only after a goal", "When the main game clock stops (goal, time-out, or ball out of play)",
       "Only when the Referee calls time-out", "At the end of each minute"],
      1,
      "Rule 17.2.2 states the shot clock stops whenever the main game clock stops."),

    q('ch17-r1723-001', 17, '17.2.3',
      "What triggers the shot clock to restart?",
      ["Only the Referee\u2019s whistle",
       "The Referee\u2019s whistle or when the player holds the ball up to take a throw",
       "When the player touches the ball",
       "Automatically after five seconds"],
      1,
      "Rule 17.2.3 states the shot clock restarts when the Referee restarts play with a whistle or when the player holds the ball up."),

    q('ch17-r1724-001', 17, '17.2.4',
      "Can the shot clock be stopped independently of the main game clock?",
      ["No, they are always linked", "Yes, it must be able to be stopped independently",
       "Only by the Chief Official", "Only during overtime"],
      1,
      "Rule 17.2.4 states the shot clock must be able to be stopped independently of the main game clock."),

    q('ch17-r1725-001', 17, '17.2.5',
      "In the last minute of each half, what must the shot clock show?",
      ["The remaining shot clock time", "The same time as the main game clock",
       "A countdown from 30 seconds", "It must be turned off"],
      1,
      "Rule 17.2.5 states in the last minute of each half, the shot clock must show the same as the main game clock."),

    # ── 17.3 VISIBILITY AND SOUND ──
    q('ch17-r1731-001', 17, '17.3.1',
      "How many shot clocks must be visible to players and spectators?",
      ["One", "Two", "Three", "Four"],
      1,
      "Rule 17.3.1 states two shot clocks must be clearly visible."),

    q('ch17-r1732-001', 17, '17.3.2',
      "Where must the shot clocks be positioned?",
      ["On the official\u2019s table only",
       "Above, below, or beside each goal, or in field corners on the controlling Referee\u2019s side",
       "Behind each goal", "Anywhere visible to players"],
      1,
      "Rule 17.3.2 states they must be positioned above, below, or beside each goal, or in field corners on the controlling Referee\u2019s side."),

    q('ch17-r1733-001', 17, '17.3.3',
      "What audible requirement must the shot clock have?",
      ["A whistle blast", "A distinctive tone clearly heard by all players and officials",
       "The same tone as the game clock", "A verbal announcement"],
      1,
      "Rule 17.3.3 states the shot clock must have an audible signal of distinctive tone clearly heard by all."),

    q('ch17-r1734-001', 17, '17.3.4',
      "Must the shot clock signal tone be different from the main timekeeper\u2019s signal?",
      ["No, the same is acceptable", "Yes, it must be a different tone",
       "Only at international competitions", "It is recommended but not required"],
      1,
      "Rule 17.3.4 states the tone must be different to the main timekeeper\u2019s signal."),

    q('ch17-r1735-001', 17, '17.3.5',
      "At what time does the shot clock signal sound?",
      ["At 30 seconds", "At 45 seconds",
       "At the completion of 60 seconds", "At the Referee\u2019s discretion"],
      2,
      "Rule 17.3.5 states the signal sounds at the completion of 60 seconds."),

    q('ch17-r1736-001', 17, '17.3.6',
      "How do the Referees confirm the change of possession after shot clock expiry?",
      ["A triple whistle blast", "A single blast of the whistle and award a free shot",
       "By raising a flag", "By stopping the game clock"],
      1,
      "Rule 17.3.6 states the Referees confirm with a single whistle blast and award a free shot."),

    # ── 17.4 Second questions for existing ones ──
    q('ch17-r1741-002', 17, '17.4.1',
      "If the shot clock expiry signal has already started sounding, can a subsequently released shot score?",
      ["Yes, any shot in flight counts",
       "No, the shot must have been taken before the signal starts",
       "Only if it was released within one second",
       "Only during overtime"],
      1,
      "Rule 17.4.1 states the shot at goal must have been taken prior to the start of the shot clock expiry signal."),

    q('ch17-r1742-002', 17, '17.4.2',
      "The shot clock expires while the ball is in flight towards the goal. Does the Referee stop play?",
      ["Yes, immediately", "No, the ball is allowed to travel to completion",
       "Only if it is clearly off target", "Only during the last minute"],
      1,
      "Rule 17.4.2 states if the ball is in flight at the time of the signal, it is allowed to travel to completion."),

    q('ch17-r1743-002', 17, '17.4.3',
      "The shot clock signal sounds at the exact moment the ball is still in the player\u2019s hand. Is this a valid shot?",
      ["Yes, simultaneous counts", "No, the ball must have left the hand before the signal",
       "Only if the Referee allows it", "The shot is retaken"],
      1,
      "Rule 17.4.3 states the ball must have left the player\u2019s hand prior to the signal sounding."),

    # ── 17.5 Second questions for existing ones ──
    q('ch17-r1751-002', 17, '17.5.1',
      "A change in team possession occurs without a shot at goal. Is the shot clock reset?",
      ["No, only shots reset it", "Yes, any change in possession resets it",
       "Only if the Referee signals it", "Only if possession changes twice"],
      1,
      "Rule 17.5.1 states the shot clock is reset whenever there is a shot at goal or a change in team possession."),

    q('ch17-r1752-002', 17, '17.5.2',
      "A shot rebounds off the goalkeeper\u2019s paddle and the same team regains the ball. Is the clock reset?",
      ["No, same team kept possession", "Yes, any shot that hits the goalkeeper\u2019s paddle resets the clock",
       "Only if the ball crossed the goal line", "Only during a power play"],
      1,
      "Rule 17.5.2 states if a shot rebounds off a goalkeeper\u2019s paddle, the clock resets even if the same team regains possession."),

    q('ch17-r1753-002', 17, '17.5.3',
      "A shot falls short, stays in play, and the same team picks it up. Does the shot clock reset?",
      ["Yes, any shot attempt resets it", "No, the clock does not reset",
       "Only if it travelled more than four metres", "Only if it hit the goal frame"],
      1,
      "Rule 17.5.3 states the clock does not reset if a shot falls short, remains in play, and the same team regains possession."),

    q('ch17-r1754-002', 17, '17.5.4',
      "A team not attempting a shot loses the ball out of bounds but gets the corner throw. Does the shot clock reset?",
      ["Yes, any out-of-bounds play resets it",
       "No, the clock does not reset",
       "Only if the ball crossed the goal line",
       "Only if the opposition touched it"],
      1,
      "Rule 17.5.4 states if a team not shooting loses control out of bounds and regains via sideline or corner throw, the clock is not reset."),

    q('ch17-r1755-002', 17, '17.5.5',
      "Two opponents momentarily both have hands on the ball but one team keeps possession. Does the shot clock reset?",
      ["Yes, any shared possession resets",
       "No, only a clear change of possession resets it",
       "Yes, after three seconds of shared possession",
       "Only if the Referee signals a reset"],
      1,
      "Rule 17.5.5 states the clock only resets if there is a clear change of possession to the other team."),

    q('ch17-r1756-002', 17, '17.5.6',
      "A player momentarily fumbles the ball and immediately picks it up again. Does the shot clock reset?",
      ["Yes, any loss of control resets it",
       "No, a very brief loss of control with immediate recovery does not reset the clock",
       "Only if an opponent touched it",
       "Only if it was on the water for more than one second"],
      1,
      "Rule 17.5.6 states a momentary loss of control with immediate recovery does not reset the shot clock."),

    q('ch17-r1757-002', 17, '17.5.7',
      "A team receives a free shot because the opposing team fouled them. Does the shot clock reset?",
      ["No, fouls never reset the clock",
       "Yes, the clock resets for a free shot or advantage from an opposing foul",
       "Only for goal penalty shots",
       "Only if a sanction card was given"],
      1,
      "Rule 17.5.7 states the clock resets when a team receives a free shot or the Referee plays advantage due to an opposing foul."),

    # ═══════════════════════════════════════════════════════════════════════
    # CLARIFICATIONS
    # ═══════════════════════════════════════════════════════════════════════

    q('clarif-sprint-001n', 0, 'clarif-sprint-starts',
      "At a sprint start, one player is clearly first to the ball. What must the other player do?",
      ["Continue sprinting regardless", "Stop immediately",
       "Make the effort to avoid any dangerous kayak tackle or contact",
       "Move to the sideline"],
      2,
      "The Sprint Starts clarification states if one player is clearly first, the other must make the effort to avoid any dangerous kayak tackle or contact with the opponent\u2019s body.",
      source='clarification'),

    q('clarif-sprint-002n', 0, 'clarif-sprint-starts',
      "At a sprint start, a player arrives late and makes contact with the nose of their kayak on the opponent\u2019s body. What is called?",
      ["No foul \u2014 normal play", "Illegal jostle",
       "Illegal kayak tackle with a sanction card", "Free throw to the opponent"],
      2,
      "The Sprint Starts clarification states late arrival with uncontrolled kayak nose contact on the opponent\u2019s body is considered deliberate/dangerous: illegal kayak tackle with a sanction card.",
      source='clarification'),

    q('clarif-defender-001n', 0, 'clarif-defenders-paddle',
      "A defender is stationary with their paddle beyond arm\u2019s reach. An attacker moves into that space and contacts the paddle while shooting. Who is responsible?",
      ["The defender, for illegal use of paddle",
       "The attacker \u2014 it is the attacker\u2019s responsibility to avoid contact",
       "Both players are penalised",
       "Neither, it is a Referee\u2019s ball"],
      1,
      "The Defender\u2019s Paddle clarification states it is the attacker\u2019s responsibility to avoid contact when the defender\u2019s paddle is stationary beyond arm\u2019s reach.",
      source='clarification'),

    q('clarif-defender-002n', 0, 'clarif-defenders-paddle',
      "For the defender\u2019s paddle rule to protect the defender, what must be true about the defender\u2019s position?",
      ["They must be within one metre of the goal",
       "Their hand(s) or paddle must be stationary and beyond arm\u2019s reach",
       "They must be the designated goalkeeper",
       "They must be facing the attacker"],
      1,
      "The Defender\u2019s Paddle clarification states the defender must be stationary with hand(s) or paddle positioned beyond arm\u2019s reach.",
      source='clarification'),

    q('clarif-ht-001n', 0, 'clarif-illegal-hand-tackle',
      "Before the throwing action begins, may a defender play the ball from the attacker\u2019s stationary hand?",
      ["No, never", "Yes, provided there is no forceful action, no danger, and contact is only with the ball",
       "Yes, without restrictions", "Only the goalkeeper may do this"],
      1,
      "The Illegal Hand Tackle clarification states before the throwing action begins, the defender may play the ball provided there is no forceful action, no danger, and contact is only with the ball.",
      source='clarification'),

    q('clarif-ht-002n', 0, 'clarif-illegal-hand-tackle',
      "At what point does the throwing action begin, after which no contact is permitted?",
      ["When the player picks up the ball",
       "When the ball is raised behind the attacker\u2019s head",
       "When the player starts their arm swing forward",
       "When the Referee signals play on"],
      1,
      "The Illegal Hand Tackle clarification states the throwing action begins when the ball is raised behind the attacker\u2019s head.",
      source='clarification'),
]


def main():
    with open(QUESTIONS_PATH, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    print(f"Existing questions: {len(questions)}")

    # Step 1: Apply remaps
    remap_count = 0
    for q in questions:
        new_rule = REMAPS.get(q['id'])
        if new_rule and q['rule'] != new_rule:
            old = q['rule']
            q['rule'] = new_rule
            remap_count += 1
            # Don't print every one, just count

    print(f"Remapped {remap_count} existing questions to specific subsections")

    # Step 2: Add new questions, skip duplicates
    existing_ids = {q['id'] for q in questions}
    added = 0
    skipped = 0
    for nq in NEW_QUESTIONS:
        if nq['id'] in existing_ids:
            skipped += 1
            continue
        questions.append(nq)
        existing_ids.add(nq['id'])
        added += 1

    print(f"Added {added} new questions ({skipped} skipped as duplicates)")
    print(f"Total questions: {len(questions)}")

    # Step 3: Write
    with open(QUESTIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"Written to {QUESTIONS_PATH}")

    # Step 4: Coverage report
    from collections import defaultdict
    import os
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
            for target in [section] + section.get('subsections', []):
                total += 1
                c = q_count.get(target['id'], 0)
                if c == 0: zero += 1
                elif c == 1: one += 1
                else: two_plus += 1

    print(f"\nCoverage (in-scope rules): {total} total")
    print(f"  0 questions: {zero}")
    print(f"  1 question:  {one}")
    print(f"  2+ questions: {two_plus}")
    print(f"  Coverage: {two_plus}/{total} = {100*two_plus/total:.0f}%")


if __name__ == '__main__':
    main()
