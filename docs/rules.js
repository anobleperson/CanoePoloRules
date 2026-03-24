/* rules.js — Rules viewer logic */

(function () {
  'use strict';

  let rulesData = null;

  // ── Bootstrap ──────────────────────────────────────────────────────────────

  fetch('rules.json')
    .then(r => {
      if (!r.ok) throw new Error('Failed to load rules.json');
      return r.json();
    })
    .then(data => {
      rulesData = data;
      buildNav(data);
      buildContent(data);
      if (isMobile()) {
        initMobileView(data);
      }
      handleHash();
    })
    .catch(err => {
      const navMsg = document.getElementById('navLoading');
      const contentMsg = document.getElementById('contentLoading');
      if (navMsg) navMsg.textContent = 'Error loading rules.';
      if (contentMsg) contentMsg.textContent = 'Could not load rules: ' + err.message;
    });

  window.addEventListener('hashchange', handleHash);

  // Mobile sidebar toggle
  document.getElementById('sidebarToggle').addEventListener('click', () => {
    const nav = document.getElementById('chapterNav');
    nav.classList.toggle('open');
  });

  // ── Build sidebar nav ──────────────────────────────────────────────────────

  function buildNav(chapters) {
    const nav = document.getElementById('chapterNav');
    nav.innerHTML = '';

    chapters.forEach(chapter => {
      const group = document.createElement('div');
      group.className = 'nav-chapter';
      group.dataset.chapter = chapter.chapter;

      const btn = document.createElement('button');
      btn.className = 'nav-chapter-btn';
      btn.setAttribute('aria-expanded', 'false');
      const chLabel = typeof chapter.chapter === 'number'
        ? 'Chapter ' + chapter.chapter + ' &mdash; ' + chapter.title
        : chapter.title;
      btn.innerHTML =
        '<span class="chevron">&#9658;</span>' +
        '<span class="ch-title">' + chLabel + '</span>';

      const ul = document.createElement('ul');
      ul.className = 'nav-section-list';
      ul.id = 'nav-ch-' + chapter.chapter;

      chapter.sections.forEach(section => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = '#' + section.id;
        a.textContent = section.id + ' ' + section.heading;
        a.dataset.rule = section.id;
        a.addEventListener('click', () => {
          // On mobile, close the sidebar after navigation
          if (window.innerWidth <= 768) {
            document.getElementById('chapterNav').classList.remove('open');
          }
        });
        li.appendChild(a);
        ul.appendChild(li);
      });

      btn.addEventListener('click', () => {
        const expanded = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', String(!expanded));
        ul.classList.toggle('open', !expanded);
      });

      group.appendChild(btn);
      group.appendChild(ul);
      nav.appendChild(group);
    });

  }

  // ── Build main content ─────────────────────────────────────────────────────

  function buildContent(chapters) {
    const body = document.getElementById('rulesBody');
    body.hidden = false;
    document.getElementById('contentLoading').remove();

    chapters.forEach(chapter => {
      const chDiv = document.createElement('section');
      chDiv.className = 'chapter-section';
      chDiv.id = 'chapter-' + chapter.chapter;

      const chTitle = document.createElement('h2');
      chTitle.className = 'chapter-title';
      chTitle.textContent = typeof chapter.chapter === 'number'
        ? 'Chapter ' + chapter.chapter + ' — ' + chapter.title
        : chapter.title;
      chDiv.appendChild(chTitle);

      chapter.sections.forEach(section => {
        const ruleDiv = buildRuleSection(section);
        chDiv.appendChild(ruleDiv);
      });

      body.appendChild(chDiv);
    });
  }

  function buildRuleSection(section) {
    const div = document.createElement('div');
    div.className = 'rule-section';
    div.id = section.id;

    const header = document.createElement('div');
    header.className = 'rule-header';
    header.setAttribute('role', 'button');
    header.setAttribute('tabindex', '0');
    header.setAttribute('aria-expanded', 'false');
    header.innerHTML =
      '<span class="rule-id">' + escHtml(section.id) + '</span>' +
      '<span class="rule-heading">' + escHtml(section.heading) + '</span>' +
      '<span class="rule-chevron">&#9658;</span>';

    const bodyDiv = document.createElement('div');
    bodyDiv.className = 'rule-body';

    const textLines = (section.text || '').split('\n').filter(l => l.trim());
    if (textLines.length === 0) textLines.push('(No text available for this section.)');

    // Sub-item pattern: line starts with a rule number containing 3+ parts (e.g. 10.25.2.a)
    const subItemRe = /^\d+\.\d+\.\d+/;
    textLines.forEach(line => {
      if (line.startsWith('IMAGE:')) {
        const img = document.createElement('img');
        img.src = 'images/' + line.slice(6);
        img.className = 'signal-img';
        img.alt = section.heading + ' signal';
        bodyDiv.appendChild(img);
        return;
      }
      const p = document.createElement('p');
      p.className = subItemRe.test(line) ? 'rule-text sub-item' : 'rule-text';
      p.innerHTML = linkSignals(escHtml(line));
      bodyDiv.appendChild(p);
    });

    const permalink = document.createElement('a');
    permalink.className = 'rule-permalink';
    permalink.href = '#' + section.id;
    permalink.textContent = '# ' + section.id;
    permalink.title = 'Direct link to rule ' + section.id;
    bodyDiv.appendChild(permalink);

    div.appendChild(header);
    div.appendChild(bodyDiv);

    // Toggle on click or keyboard
    function toggle() {
      const isOpen = div.classList.contains('open');
      div.classList.toggle('open', !isOpen);
      header.setAttribute('aria-expanded', String(!isOpen));
      if (!isOpen) {
        // Record this as the current location so the back button returns here
        history.pushState(null, '', '#' + section.id);
        setActiveNavLink(section.id);
        expandNavChapterForRule(section.id);
      }
    }

    header.addEventListener('click', toggle);
    header.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
    });

    return div;
  }

  // ── Mobile drill-down ──────────────────────────────────────────────────────

  function isMobile() {
    return window.innerWidth <= 768;
  }

  // Track which chapter is currently selected (for back-button label)
  let mobileCurrentChapter = null;

  function initMobileView(chapters) {
    const mobileView = document.getElementById('mobileView');
    mobileView.hidden = false;

    const list = document.getElementById('mobileChapterList');
    document.getElementById('mobileLoading').remove();

    chapters.forEach(chapter => {
      const btn = document.createElement('button');
      btn.className = 'mobile-chapter-card';
      btn.textContent = typeof chapter.chapter === 'number'
        ? 'Chapter ' + chapter.chapter + ' — ' + chapter.title
        : chapter.title;
      btn.addEventListener('click', () => showSectionList(chapter));
      list.appendChild(btn);
    });

    document.getElementById('mobileBackToChapters').addEventListener('click', showChapterList);
    document.getElementById('mobileBackToSections').addEventListener('click', () => {
      if (mobileCurrentChapter) showSectionList(mobileCurrentChapter);
    });
  }

  function showChapterList() {
    document.getElementById('mobileChapterList').hidden = false;
    document.getElementById('mobileSectionList').hidden = true;
    document.getElementById('mobileRuleView').hidden = true;
    mobileCurrentChapter = null;
  }

  function showSectionList(chapter) {
    mobileCurrentChapter = chapter;

    document.getElementById('mobileChapterList').hidden = true;
    document.getElementById('mobileSectionList').hidden = false;
    document.getElementById('mobileRuleView').hidden = true;

    document.getElementById('mobileChapterHeading').textContent = typeof chapter.chapter === 'number'
      ? 'Ch ' + chapter.chapter + ' — ' + chapter.title
      : chapter.title;

    const ul = document.getElementById('mobileSectionItems');
    ul.innerHTML = '';
    chapter.sections.forEach(section => {
      const li = document.createElement('li');
      const btn = document.createElement('button');
      btn.className = 'mobile-section-btn';
      btn.innerHTML =
        '<span class="section-id">' + escHtml(section.id) + '</span>' +
        '<span class="section-heading">' + escHtml(section.heading) + '</span>';
      btn.addEventListener('click', () => showMobileRule(section, chapter));
      li.appendChild(btn);
      ul.appendChild(li);
    });

    // Scroll to top of page
    window.scrollTo(0, 0);
  }

  function showMobileRule(section, chapter) {
    mobileCurrentChapter = chapter;

    document.getElementById('mobileChapterList').hidden = true;
    document.getElementById('mobileSectionList').hidden = true;
    document.getElementById('mobileRuleView').hidden = false;

    document.getElementById('mobileBackChapterName').textContent = typeof chapter.chapter === 'number'
      ? 'Ch ' + chapter.chapter
      : chapter.title;

    const content = document.getElementById('mobileRuleContent');
    content.innerHTML = '';
    const ruleDiv = buildRuleSection(section);
    // Always show the body open on mobile
    ruleDiv.classList.add('open');
    const header = ruleDiv.querySelector('.rule-header');
    if (header) header.setAttribute('aria-expanded', 'true');
    content.appendChild(ruleDiv);

    history.pushState(null, '', '#' + section.id);
    window.scrollTo(0, 0);
  }

  // ── Deep-link via hash ─────────────────────────────────────────────────────

  function handleHash() {
    const hash = window.location.hash.slice(1); // strip #
    if (!hash) return;

    // On mobile: navigate the drill-down directly to the rule
    if (isMobile() && rulesData) {
      const chapter = rulesData.find(ch => ch.sections.some(s => s.id === hash));
      const section = chapter && chapter.sections.find(s => s.id === hash);
      if (chapter && section) {
        showMobileRule(section, chapter);
        return;
      }
    }

    const target = document.getElementById(hash);
    if (!target) return;

    // Expand the rule if it's a rule section
    if (target.classList.contains('rule-section')) {
      openRule(target);
    }

    // Expand the parent chapter in the sidebar nav
    expandNavChapterForRule(hash);

    // Highlight active nav link
    setActiveNavLink(hash);

    // Scroll into view after a brief paint delay
    setTimeout(() => {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);

    // Briefly highlight the rule
    target.classList.add('highlight');
    setTimeout(() => target.classList.remove('highlight'), 2000);
  }

  function openRule(ruleDiv) {
    ruleDiv.classList.add('open');
    const header = ruleDiv.querySelector('.rule-header');
    if (header) header.setAttribute('aria-expanded', 'true');
  }

  function expandNavChapterForRule(ruleId) {
    if (!rulesData) return;
    const chapter = rulesData.find(ch => ch.sections.some(s => s.id === ruleId));
    if (!chapter) return;
    const group = document.querySelector('[data-chapter="' + chapter.chapter + '"]');
    if (!group) return;
    const btn = group.querySelector('.nav-chapter-btn');
    const ul = group.querySelector('.nav-section-list');
    if (btn && ul) {
      btn.setAttribute('aria-expanded', 'true');
      ul.classList.add('open');
    }
  }

  function setActiveNavLink(ruleId) {
    document.querySelectorAll('.nav-section-list li a').forEach(a => {
      a.classList.toggle('active', a.dataset.rule === ruleId);
    });
  }

  // ── Utils ──────────────────────────────────────────────────────────────────

  // Replace "Signal N" / "Signals N and M" / "Signals N, M & P" with links to 15.N
  function linkSignals(html) {
    // Match: Signal(s) followed by digits with separators (and / & / &amp; / comma)
    return html.replace(/\bSignals?\s+((?:\d+(?:\s*(?:,|and|&amp;|&)\s*)?)+)/g, (match, nums) => {
      const linked = nums.replace(/\d+/g, n =>
        '<a href="#15.' + n + '" class="signal-link">' + n + '</a>'
      );
      return 'Signal' + (match.startsWith('Signals') ? 's' : '') + ' ' + linked;
    });
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

}());
