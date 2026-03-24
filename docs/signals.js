/* signals.js — Referee Signals Quiz logic */

(function () {
  'use strict';

  const LETTERS = ['A', 'B', 'C', 'D'];

  let signals = [];   // [{id, name, imageFile, description}]
  let session = [];   // shuffled signals with shuffled options
  let current = 0;
  let score = 0;

  // ── Bootstrap ──────────────────────────────────────────────────────────────

  fetch('rules.json')
    .then(r => {
      if (!r.ok) throw new Error('Failed to load rules.json');
      return r.json();
    })
    .then(data => {
      signals = parseSignals(data);
      if (signals.length === 0) throw new Error('No signals found in rules.json');
      initStart();
    })
    .catch(err => {
      document.getElementById('sigStart').querySelector('.card').innerHTML =
        '<p style="color:var(--color-incorrect)">Could not load signals: ' + err.message + '</p>';
    });

  // ── Parse signals from ch15 ─────────────────────────────────────────────

  function parseSignals(rulesData) {
    const ch15 = rulesData.find(ch => ch.chapter === 15);
    if (!ch15) return [];
    return ch15.sections.map(section => {
      const lines = section.text.split('\n').filter(l => l.trim());
      const imgLine = lines.find(l => l.startsWith('IMAGE:'));
      const imageFile = imgLine ? 'images/' + imgLine.slice(6) : '';
      const descLines = lines.filter(l => !l.startsWith('IMAGE:'));
      return {
        id: section.id,
        name: section.heading,
        imageFile,
        description: descLines.join(' '),
      };
    });
  }

  // ── Start screen ───────────────────────────────────────────────────────────

  function initStart() {
    showScreen('sigStart');
    document.getElementById('btnSigStart').addEventListener('click', startQuiz);
    document.getElementById('btnSigRestart').addEventListener('click', startQuiz);
  }

  function startQuiz() {
    score = 0;
    current = 0;
    session = buildSession();
    showSignal(0);
  }

  // ── Session building ───────────────────────────────────────────────────────

  function buildSession() {
    const shuffled = shuffle(signals.slice());
    return shuffled.map((sig, i) => {
      const options = buildOptions(sig);
      return { sig, options, correctDisplayIndex: options.indexOf(sig.name) };
    });
  }

  function buildOptions(correctSignal) {
    const others = shuffle(signals.filter(s => s.id !== correctSignal.id));
    const distractors = others.slice(0, 3).map(s => s.name);
    return shuffle([correctSignal.name, ...distractors]);
  }

  // ── Signal display ─────────────────────────────────────────────────────────

  function showSignal(index) {
    const { sig, options, correctDisplayIndex } = session[index];
    const total = session.length;

    updateProgress('sigNum', 'sigTotal', 'sigProgressFill', index + 1, total);

    const img = document.getElementById('sigPhoto');
    img.src = sig.imageFile;
    img.alt = sig.name + ' signal';

    const list = document.getElementById('sigOptionsList');
    list.innerHTML = '';
    options.forEach((name, displayIndex) => {
      const li = document.createElement('li');
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.innerHTML =
        '<span class="option-letter">' + LETTERS[displayIndex] + '</span>' +
        '<span class="option-text">' + escHtml(name) + '</span>';
      btn.addEventListener('click', () => handleAnswer(displayIndex, correctDisplayIndex, index));
      li.appendChild(btn);
      list.appendChild(li);
    });

    showScreen('sigQuestion');
  }

  // ── Answer handling ────────────────────────────────────────────────────────

  function handleAnswer(chosen, correct, index) {
    const isCorrect = chosen === correct;
    if (isCorrect) score++;

    const btns = document.querySelectorAll('#sigOptionsList .option-btn');
    btns.forEach((btn, i) => {
      btn.disabled = true;
      if (i === correct) btn.classList.add('correct');
      else if (i === chosen && !isCorrect) btn.classList.add('incorrect');
    });

    setTimeout(() => showFeedback(index, isCorrect), isCorrect ? 300 : 1200);
  }

  // ── Feedback display ───────────────────────────────────────────────────────

  function showFeedback(index, isCorrect) {
    const { sig } = session[index];
    const total = session.length;

    updateProgress('fbSigNum', 'fbSigTotal', 'fbSigProgressFill', index + 1, total);

    const card = document.getElementById('sigFeedbackCard');
    card.className = 'card feedback-card ' + (isCorrect ? 'correct' : 'incorrect');

    const result = document.getElementById('sigFeedbackResult');
    result.className = 'feedback-result ' + (isCorrect ? 'correct' : 'incorrect');
    result.textContent = isCorrect ? 'Correct!' : 'Incorrect';

    document.getElementById('sigFeedbackName').textContent = sig.id + ' — ' + sig.name;
    document.getElementById('sigFeedbackDescription').textContent = sig.description;

    const ruleLink = document.getElementById('sigFeedbackRuleLink');
    ruleLink.href = 'rules.html#' + sig.id;
    document.getElementById('sigFeedbackRuleNum').textContent = sig.id;

    const btnNext = document.getElementById('btnSigNext');
    const isLast = index >= total - 1;
    btnNext.textContent = isLast ? 'See Results' : 'Next Signal';
    btnNext.onclick = () => {
      if (isLast) {
        showEnd();
      } else {
        current++;
        showSignal(current);
      }
    };

    showScreen('sigFeedback');
    document.getElementById('sigFeedbackCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // ── End screen ─────────────────────────────────────────────────────────────

  function showEnd() {
    const total = session.length;
    const pct = Math.round((score / total) * 100);

    document.getElementById('sigScoreFraction').textContent = score + ' / ' + total;
    document.getElementById('sigScorePercent').textContent = pct + '%';
    document.getElementById('sigScoreMessage').textContent = scoreMessage(pct);

    showScreen('sigEnd');
  }

  function scoreMessage(pct) {
    if (pct >= 90) return 'Excellent! You can recognise the signals with confidence.';
    if (pct >= 70) return 'Good work. Review the signals you missed in the Rules Viewer.';
    if (pct >= 50) return 'Keep practising — focus on the signals you found difficult.';
    return 'Keep at it! Browse the signals in the Rules Viewer to build familiarity.';
  }

  // ── Helpers ────────────────────────────────────────────────────────────────

  function showScreen(id) {
    ['sigStart', 'sigQuestion', 'sigFeedback', 'sigEnd'].forEach(s => {
      document.getElementById(s).hidden = s !== id;
    });
  }

  function updateProgress(numId, totalId, fillId, cur, total) {
    document.getElementById(numId).textContent = cur;
    document.getElementById(totalId).textContent = total;
    const fill = document.getElementById(fillId);
    fill.style.width = ((cur / total) * 100) + '%';
    fill.closest('.progress-bar').setAttribute('aria-valuenow', cur);
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

}());
