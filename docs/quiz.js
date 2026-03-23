/* quiz.js — Quiz app logic */

(function () {
  'use strict';

  const SESSION_SIZE = 20;
  const LETTERS = ['A', 'B', 'C', 'D'];

  let allQuestions = [];
  let session = [];       // {question, displayOrder, displayCorrectIndex}
  let current = 0;
  let score = 0;

  // ── Bootstrap ──────────────────────────────────────────────────────────────

  fetch('questions.json')
    .then(r => {
      if (!r.ok) throw new Error('Failed to load questions.json');
      return r.json();
    })
    .then(data => {
      allQuestions = data;
      initStart();
    })
    .catch(err => {
      document.getElementById('screenStart').querySelector('.card').innerHTML =
        '<p style="color:var(--color-incorrect)">Could not load questions: ' + err.message + '</p>';
    });

  // ── Start screen ───────────────────────────────────────────────────────────

  function initStart() {
    showScreen('screenStart');
    document.getElementById('btnStart').addEventListener('click', startQuiz);
    document.getElementById('btnRestart').addEventListener('click', startQuiz);
  }

  function startQuiz() {
    score = 0;
    current = 0;
    session = buildSession(allQuestions, SESSION_SIZE);
    showQuestion(0);
  }

  // ── Session building ───────────────────────────────────────────────────────

  function buildSession(questions, n) {
    const pool = shuffle(questions.slice());
    const picked = pool.slice(0, Math.min(n, pool.length));
    return picked.map(q => {
      const order = shuffledOrder(q.options.length);
      const displayCorrectIndex = order.indexOf(q.correctIndex);
      return { question: q, displayOrder: order, displayCorrectIndex };
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
  // e.g. [2, 0, 3, 1] means display-slot 0 shows option[2], etc.
  function shuffledOrder(n) {
    const indices = Array.from({ length: n }, (_, i) => i);
    return shuffle(indices);
  }

  // ── Question display ───────────────────────────────────────────────────────

  function showQuestion(index) {
    const { question, displayOrder, displayCorrectIndex } = session[index];
    const total = session.length;

    // Progress
    updateProgress('qNum', 'qTotal', 'progressFill', index + 1, total);

    // Meta (chapter / rule)
    const meta = document.getElementById('questionMeta');
    meta.textContent = 'Chapter ' + question.chapter + ' · Rule ' + question.rule;

    // Question text
    document.getElementById('questionText').textContent = question.question;

    // Options
    const list = document.getElementById('optionsList');
    list.innerHTML = '';
    displayOrder.forEach((originalIndex, displayIndex) => {
      const li = document.createElement('li');
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.dataset.displayIndex = displayIndex;
      btn.innerHTML =
        '<span class="option-letter">' + LETTERS[displayIndex] + '</span>' +
        '<span class="option-text">' + escHtml(question.options[originalIndex]) + '</span>';
      btn.addEventListener('click', () => handleAnswer(displayIndex, displayCorrectIndex, index));
      li.appendChild(btn);
      list.appendChild(li);
    });

    showScreen('screenQuestion');
  }

  // ── Answer handling ────────────────────────────────────────────────────────

  function handleAnswer(chosen, correct, index) {
    const isCorrect = chosen === correct;
    if (isCorrect) score++;

    // Disable all options and mark correct/incorrect
    const btns = document.querySelectorAll('.option-btn');
    btns.forEach((btn, i) => {
      btn.disabled = true;
      if (i === correct) btn.classList.add('correct');
      else if (i === chosen && !isCorrect) btn.classList.add('incorrect');
    });

    // Show feedback after brief pause so user sees highlight
    setTimeout(() => showFeedback(index, isCorrect), 300);
  }

  // ── Feedback display ───────────────────────────────────────────────────────

  function showFeedback(index, isCorrect) {
    const { question } = session[index];
    const total = session.length;

    updateProgress('fbQNum', 'fbQTotal', 'fbProgressFill', index + 1, total);

    const card = document.getElementById('feedbackCard');
    card.className = 'card feedback-card ' + (isCorrect ? 'correct' : 'incorrect');

    const result = document.getElementById('feedbackResult');
    result.className = 'feedback-result ' + (isCorrect ? 'correct' : 'incorrect');
    result.textContent = isCorrect ? 'Correct!' : 'Incorrect';

    document.getElementById('feedbackExplanation').textContent = question.explanation;

    // Optional rule link
    const ruleLink = document.getElementById('feedbackRuleLink');
    if (question.rule) {
      ruleLink.hidden = false;
      ruleLink.href = 'rules.html#' + question.rule;
      document.getElementById('feedbackRuleNum').textContent = question.rule;
    } else {
      ruleLink.hidden = true;
    }

    // Next button label
    const btnNext = document.getElementById('btnNext');
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

    showScreen('screenFeedback');
    document.getElementById('feedbackCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // ── End screen ─────────────────────────────────────────────────────────────

  function showEnd() {
    const total = session.length;
    const pct = Math.round((score / total) * 100);

    document.getElementById('scoreFraction').textContent = score + ' / ' + total;
    document.getElementById('scorePercent').textContent = pct + '%';
    document.getElementById('scoreMessage').textContent = scoreMessage(pct);

    showScreen('screenEnd');
  }

  function scoreMessage(pct) {
    if (pct >= 90) return 'Excellent! You have a strong grasp of the 2025 ICF rules.';
    if (pct >= 70) return 'Good work. Review the explanations for any questions you missed.';
    if (pct >= 50) return 'Keep studying — focus on the rules cited in the explanations.';
    return 'Keep at it! Read through the rules viewer to build your knowledge.';
  }

  // ── Helpers ────────────────────────────────────────────────────────────────

  function showScreen(id) {
    ['screenStart', 'screenQuestion', 'screenFeedback', 'screenEnd'].forEach(s => {
      const el = document.getElementById(s);
      el.hidden = s !== id;
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
