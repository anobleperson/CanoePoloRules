/* scenario.js — Scenario Quiz app logic */

(function () {
  'use strict';

  const SESSION_SIZE = 10;
  const LETTERS = ['A', 'B', 'C', 'D'];

  let allScenarios = [];
  let session = [];         // [{scenario, shuffledOrder, displayCorrectIndices}]
  let current = 0;
  let score = 0;
  let pendingFeedback = null;  // cancel token — prevents stale setTimeout after navigation

  // ── Bootstrap ──────────────────────────────────────────────────────────────

  // btnScnStart is disabled in HTML until data is ready
  fetch('scenarios.json')
    .then(r => {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(data => {
      allScenarios = data;
      document.getElementById('btnScnStart').disabled = false;
      initStart();
    })
    .catch(err => {
      document.getElementById('scnStart').querySelector('.card').innerHTML =
        '<p style="color:var(--color-incorrect)">Could not load scenarios: ' + escHtml(err.message) + '</p>';
    });

  // ── Start screen ───────────────────────────────────────────────────────────

  function initStart() {
    showScreen('scnStart');
    document.getElementById('btnScnStart').addEventListener('click', startQuiz);
    document.getElementById('btnScnRestart').addEventListener('click', startQuiz);
  }

  function startQuiz() {
    cancelPendingFeedback();
    score = 0;
    current = 0;
    session = buildSession(allScenarios, SESSION_SIZE);
    showQuestion(0);
  }

  // ── Session building ───────────────────────────────────────────────────────

  function buildSession(scenarios, n) {
    const pool = shuffle(scenarios.slice());
    const picked = pool.slice(0, Math.min(n, pool.length));
    return picked.map(scenario => {
      const shuffledOrder = shuffledIndices(scenario.options.length);
      // Remap correctIndices from data-space to display-space
      const displayCorrectIndices = scenario.correctIndices
        .map(i => shuffledOrder.indexOf(i))
        .sort((a, b) => a - b);
      return { scenario, shuffledOrder, displayCorrectIndices };
    });
  }

  // Fisher-Yates shuffle, returns new array
  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  // Returns array of option indices in a shuffled display order
  function shuffledIndices(n) {
    const indices = Array.from({ length: n }, (_, i) => i);
    return shuffle(indices);
  }

  // ── Question display ───────────────────────────────────────────────────────

  function showQuestion(index) {
    const { scenario, shuffledOrder, displayCorrectIndices } = session[index];
    const total = session.length;

    updateProgress('scnNum', 'scnTotal', 'scnProgressFill', index + 1, total);

    // Meta
    document.getElementById('scnQuestionMeta').textContent =
      'Chapter ' + scenario.chapter + ' · Rule ' + scenario.rule;

    // Situation paragraph
    document.getElementById('scnSituationText').textContent = scenario.situation;

    // Options (checkbox list)
    const list = document.getElementById('scnOptionsList');
    list.innerHTML = '';
    shuffledOrder.forEach((originalIndex, displayIndex) => {
      const li = document.createElement('li');
      const label = document.createElement('label');
      label.className = 'option-btn';
      label.htmlFor = 'scn-opt-' + displayIndex;

      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.id = 'scn-opt-' + displayIndex;
      checkbox.name = 'scn-options';
      checkbox.value = String(displayIndex);
      checkbox.className = 'option-checkbox';

      const indicator = document.createElement('span');
      indicator.className = 'option-indicator';
      indicator.setAttribute('aria-hidden', 'true');

      const letter = document.createElement('span');
      letter.className = 'option-letter';
      letter.setAttribute('aria-hidden', 'true');
      letter.textContent = LETTERS[displayIndex];

      const text = document.createElement('span');
      text.className = 'option-text';
      text.textContent = scenario.options[originalIndex];

      label.appendChild(checkbox);
      label.appendChild(indicator);
      label.appendChild(letter);
      label.appendChild(text);
      li.appendChild(label);
      list.appendChild(li);
    });

    // Check Answer button — disabled until at least one checkbox is ticked
    const btnCheck = document.getElementById('btnScnCheck');
    btnCheck.disabled = true;
    btnCheck.onclick = () => handleCheck(index, displayCorrectIndices);

    // Enable button when any checkbox changes
    list.addEventListener('change', function syncBtn() {
      btnCheck.disabled = !list.querySelector('.option-checkbox:checked');
    });

    showScreen('scnQuestion');
    // Prevent carried focus rings when transitioning between questions
    if (document.activeElement) document.activeElement.blur();
  }

  // ── Answer handling ────────────────────────────────────────────────────────

  function handleCheck(index, displayCorrectIndices) {
    // Disable immediately — prevents double-tap before setTimeout fires
    const btnCheck = document.getElementById('btnScnCheck');
    btnCheck.disabled = true;

    // Cancel any pending feedback from a previous question (safety)
    cancelPendingFeedback();

    const checked = getCheckedIndices();  // sorted numerically

    // All-or-nothing: exact match of sorted checked vs sorted correct
    const isCorrect =
      checked.length === displayCorrectIndices.length &&
      checked.every((v, i) => v === displayCorrectIndices[i]);

    if (isCorrect) score++;

    revealOptionStates(displayCorrectIndices, checked);

    // Cancel token prevents stale callback firing after navigation
    const token = { canceled: false };
    token.id = setTimeout(() => {
      if (token.canceled) return;
      showFeedback(index, isCorrect);
    }, isCorrect ? 300 : 1200);
    pendingFeedback = token;
  }

  function cancelPendingFeedback() {
    if (pendingFeedback) {
      clearTimeout(pendingFeedback.id);
      pendingFeedback.canceled = true;
      pendingFeedback = null;
    }
  }

  function getCheckedIndices() {
    return [...document.querySelectorAll('.option-checkbox')]
      .map((cb, i) => cb.checked ? i : -1)
      .filter(i => i !== -1)
      .sort((a, b) => a - b);  // numeric sort
  }

  function revealOptionStates(correct, checked) {
    document.querySelectorAll('.option-btn').forEach((label, i) => {
      if (!document.contains(label)) return;  // detached node — skip
      const inCorrect = correct.includes(i);
      const inChecked = checked.includes(i);
      label.classList.toggle('correct',   inCorrect);
      label.classList.toggle('incorrect', inChecked && !inCorrect);
      label.classList.toggle('missed',    !inChecked && inCorrect);
      label.classList.add('revealed');
      // Append icon span for non-colour accessibility (✓ ✗ !)
      const icon = document.createElement('span');
      icon.className = 'option-icon';
      icon.setAttribute('aria-hidden', 'true');
      label.appendChild(icon);
      // Lock the checkbox
      const cb = label.querySelector('.option-checkbox');
      if (cb) { cb.disabled = true; cb.tabIndex = -1; }
    });
  }

  // ── Feedback display ───────────────────────────────────────────────────────

  function showFeedback(index, isCorrect) {
    const { scenario } = session[index];
    const total = session.length;

    updateProgress('fbScnNum', 'fbScnTotal', 'fbScnProgressFill', index + 1, total);

    const card = document.getElementById('scnFeedbackCard');
    card.className = 'card feedback-card ' + (isCorrect ? 'correct' : 'incorrect');

    const result = document.getElementById('scnFeedbackResult');
    result.className = 'feedback-result ' + (isCorrect ? 'correct' : 'incorrect');
    result.textContent = isCorrect ? 'Correct!' : 'Incorrect';

    document.getElementById('scnFeedbackExplanation').textContent = scenario.explanation;

    // Rule deep-link
    const ruleLink = document.getElementById('scnFeedbackRuleLink');
    if (scenario.rule) {
      ruleLink.hidden = false;
      ruleLink.href = 'rules.html#' + scenario.rule;
      document.getElementById('scnFeedbackRuleNum').textContent = scenario.rule;
    } else {
      ruleLink.hidden = true;
    }

    const btnNext = document.getElementById('btnScnNext');
    const isLast = index >= total - 1;
    btnNext.textContent = isLast ? 'See Results' : 'Next Question';

    btnNext.onclick = () => {
      if (isLast) {
        showEnd();
      } else {
        current++;
        showQuestion(current);
      }
    };

    showScreen('scnFeedback');
    document.getElementById('scnFeedbackCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // ── End screen ─────────────────────────────────────────────────────────────

  function showEnd() {
    cancelPendingFeedback();
    const total = session.length;
    const pct = Math.round((score / total) * 100);

    document.getElementById('scnScoreFraction').textContent = score + ' / ' + total;
    document.getElementById('scnScorePercent').textContent = pct + '%';
    document.getElementById('scnScoreMessage').textContent = scoreMessage(pct);

    showScreen('scnEnd');
  }

  function scoreMessage(pct) {
    if (pct >= 90) return 'Excellent! You have a strong grasp of applied game situations.';
    if (pct >= 70) return 'Good work. Review the explanations for any questions you missed.';
    if (pct >= 50) return 'Keep studying — focus on the rules cited in the explanations.';
    return 'Keep at it! Read through the rules viewer and try again.';
  }

  // ── Helpers ────────────────────────────────────────────────────────────────

  function showScreen(id) {
    ['scnStart', 'scnQuestion', 'scnFeedback', 'scnEnd'].forEach(s => {
      document.getElementById(s).hidden = s !== id;
    });
  }

  function updateProgress(numId, totalId, fillId, current, total) {
    document.getElementById(numId).textContent = current;
    document.getElementById(totalId).textContent = total;
    const fill = document.getElementById(fillId);
    const pct = (current / total) * 100;
    fill.style.width = pct + '%';
    fill.closest('.progress-bar').setAttribute('aria-valuenow', current);
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

}());
