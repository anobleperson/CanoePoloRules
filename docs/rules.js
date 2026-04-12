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

  // ── Helpers ────────────────────────────────────────────────────────────────

  // Find a section by ID anywhere in the data tree.
  // Returns { chapter, section } where section may be a subsection.
  function findSection(ruleId) {
    if (!rulesData) return null;
    for (const chapter of rulesData) {
      for (const section of chapter.sections) {
        if (section.id === ruleId) return { chapter, section };
        for (const sub of (section.subsections || [])) {
          if (sub.id === ruleId) return { chapter, section: sub };
        }
      }
    }
    return null;
  }

  // Find the top-level (X.Y) nav ID for a given rule ID (which may be a subsection).
  function navIdFor(ruleId) {
    if (!rulesData) return ruleId;
    for (const chapter of rulesData) {
      for (const section of chapter.sections) {
        if ((section.subsections || []).some(sub => sub.id === ruleId)) {
          return section.id;
        }
      }
    }
    return ruleId;
  }

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
        chDiv.appendChild(buildSectionGroup(section));
      });

      body.appendChild(chDiv);
    });
  }

  // Renders an X.Y section: a heading bar, optional text content, then child rule cards.
  // All top-level sections use this so they look consistent regardless of structure.
  function buildSectionGroup(section) {
    const groupDiv = document.createElement('div');
    groupDiv.className = 'rule-group';
    groupDiv.id = section.id;

    const heading = document.createElement('div');
    heading.className = 'rule-group-heading';
    heading.innerHTML =
      '<span class="rule-id">' + escHtml(section.id) + '</span>' +
      '<span class="rule-group-title">' + escHtml(section.heading) + '</span>';
    groupDiv.appendChild(heading);

    // Text content directly on the section (e.g. standalone rules, signal images)
    if (section.text && section.text.trim()) {
      section.text.split('\n').filter(l => l.trim()).forEach(line => {
        if (line.startsWith('IMAGE:')) {
          const img = document.createElement('img');
          img.src = 'images/' + line.slice(6);
          img.className = 'signal-img';
          img.alt = section.heading + ' signal';
          groupDiv.appendChild(img);
        } else {
          const p = document.createElement('p');
          p.className = 'rule-group-intro';
          p.innerHTML = linkSignals(escHtml(line));
          groupDiv.appendChild(p);
        }
      });
    }

    (section.subsections || []).forEach(sub => {
      groupDiv.appendChild(buildRuleSection(sub));
    });

    return groupDiv;
  }

  function buildRuleSection(section) {
    const hasText = (section.text || '').trim().length > 0;

    // Sections with no body text render as flat (non-collapsible) rule items.
    if (!hasText) {
      return buildFlatRule(section);
    }

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

    const subItemRe = /^\d+\.\d+\.\d+/;
    section.text.split('\n').filter(l => l.trim()).forEach(line => {
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

    function toggle() {
      const isOpen = div.classList.contains('open');
      div.classList.toggle('open', !isOpen);
      header.setAttribute('aria-expanded', String(!isOpen));
      if (!isOpen) {
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

  // A flat (non-collapsible) rule item — used when the heading is the entire rule text.
  function buildFlatRule(section) {
    const div = document.createElement('div');
    div.className = 'rule-flat';
    div.id = section.id;
    div.innerHTML =
      '<span class="rule-id">' + escHtml(section.id) + '</span>' +
      '<span class="rule-flat-text">' + linkSignals(escHtml(section.heading)) + '</span>';
    return div;
  }

  // ── Mobile drill-down ──────────────────────────────────────────────────────

  function isMobile() {
    return window.innerWidth <= 768;
  }

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

    window.scrollTo(0, 0);
  }

  function showMobileRule(section, chapter) {
    mobileCurrentChapter = chapter;

    document.getElementById('mobileChapterList').hidden = true;
    document.getElementById('mobileSectionList').hidden = true;
    document.getElementById('mobileRuleView').hidden = false;

    document.getElementById('mobileBackChapterName').textContent = typeof chapter.chapter === 'number'
      ? 'Ch ' + chapter.chapter + ' \u2014 ' + chapter.title
      : chapter.title;

    document.getElementById('mobileRuleHeading').textContent = section.id + ' \u2014 ' + section.heading;

    const content = document.getElementById('mobileRuleContent');
    content.innerHTML = '';

    const groupDiv = buildSectionGroup(section);
    groupDiv.querySelectorAll('.rule-section').forEach(el => {
      el.classList.add('open');
      const h = el.querySelector('.rule-header');
      if (h) h.setAttribute('aria-expanded', 'true');
    });
    content.appendChild(groupDiv);

    history.pushState(null, '', '#' + section.id);
    window.scrollTo(0, 0);
  }

  // ── Deep-link via hash ─────────────────────────────────────────────────────

  function handleHash() {
    const hash = window.location.hash.slice(1);
    if (!hash) return;

    if (isMobile() && rulesData) {
      const found = findSection(hash);
      if (found) {
        showMobileRule(found.section, found.chapter);
        return;
      }
    }

    const target = document.getElementById(hash);
    if (!target) return;

    if (target.classList.contains('rule-section')) {
      openRule(target);
    }

    expandNavChapterForRule(hash);
    setActiveNavLink(hash);

    setTimeout(() => {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);

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
    const navId = navIdFor(ruleId);
    const chapter = rulesData.find(ch =>
      ch.sections.some(s => s.id === navId)
    );
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
    const navId = navIdFor(ruleId);
    document.querySelectorAll('.nav-section-list li a').forEach(a => {
      a.classList.toggle('active', a.dataset.rule === navId);
    });
  }

  // ── Utils ──────────────────────────────────────────────────────────────────

  function linkSignals(html) {
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
