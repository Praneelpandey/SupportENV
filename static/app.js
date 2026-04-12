/**
 * SupportEnv — App Logic
 * Dark Precision theme. Clean functional code.
 */

const $ = sel => document.querySelector(sel);
const $$ = sel => document.querySelectorAll(sel);

const state = {
    currentTask: null,
    currentObs: null,
    taskConfig: null,
    history: [],
    isSubmitting: false,
};

const DOM = {
    sectionHero: $('#section-hero'),
    sectionTasks: $('#section-tasks'),
    sectionTicket: $('#section-ticket'),
    sectionAction: $('#section-action'),
    sectionResults: $('#section-results'),
    sectionHistory: $('#section-history'),
    taskCards: $('#task-cards'),
    ticketId: $('#ticket-id'),
    taskBadge: $('#current-task-badge'),
    ticketText: $('#ticket-text'),
    ticketHint: $('#ticket-hint'),
    actionForm: $('#action-form'),
    inputPriority: $('#input-priority'),
    inputReply: $('#input-reply'),
    wordCount: $('#word-count'),
    groupPriority: $('#group-priority'),
    groupReply: $('#group-reply'),
    replyTips: $('#reply-tips'),
    btnSubmit: $('#btn-submit'),
    btnNewTicket: $('#btn-new-ticket'),
    btnChangeTask: $('#btn-change-task'),
    btnNextEpisode: $('#btn-next-episode'),
    btnClearHistory: $('#btn-clear-history'),
    btnGetStarted: $('#btn-get-started'),
    scoreRingFill: $('#score-ring-fill'),
    scoreValue: $('#score-value'),
    scoreLabel: $('#score-label'),
    breakdownBars: $('#breakdown-bars'),
    comparisonTable: $('#comparison-table'),
    keywordsCard: $('#keywords-card'),
    keywordsList: $('#keywords-list'),
    statEpisodes: $('#stat-episodes'),
    statAvgScore: $('#stat-avg-score'),
    statBestScore: $('#stat-best-score'),
    historyEmpty: $('#history-empty'),
    historyWrapper: $('#history-table-wrapper'),
    historyTbody: $('#history-tbody'),
    toastContainer: $('#toast-container'),
};

// ── API ─────────────────────────────────────────────────
async function api(endpoint, method = 'GET', body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`/api${endpoint}`, opts);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'API error');
    return data;
}

// ── Toast ────────────────────────────────────────────────
function showToast(msg, type = 'info') {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = msg;
    DOM.toastContainer.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

// ── Init ─────────────────────────────────────────────────
async function init() {
    await loadTasks();
    bindEvents();
    updateStats();
    initTerminalTypewriter();
    initRippleEffect();
}

async function loadTasks() {
    try {
        const data = await api('/tasks');
        renderTaskCards(data.tasks);
    } catch (err) {
        showToast('Failed to load tasks: ' + err.message, 'error');
    }
}

const TASK_DESC = {
    classify: 'Categorize the ticket as billing, technical, or general. The simplest triage task.',
    prioritize: 'Classify the ticket and assign a priority level from low to urgent.',
    resolve: 'Full triage: classify, prioritize, and draft a customer-facing reply.',
};

const TASK_STATS = {
    classify: ['1 action / episode', 'score: exact match'],
    prioritize: ['2 actions / episode', 'score: weighted avg'],
    resolve: ['3 actions / episode', 'score: LLM graded'],
};

function renderTaskCards(tasks) {
    DOM.taskCards.innerHTML = tasks.map(t => {
        const isHard = t.difficulty === 'hard';
        const cardHTML = `
            <div class="task-card" data-task="${t.name}" data-difficulty="${t.difficulty}">
                <div class="tc-head">
                    <span class="tc-title">${t.name}</span>
                    <span class="diff-tag ${t.difficulty}">${t.difficulty}</span>
                </div>
                <p class="tc-desc">${TASK_DESC[t.name] || ''}</p>
                <div class="tc-foot">
                    <span>${TASK_STATS[t.name]?.[0] || ''}</span>
                    <span>${TASK_STATS[t.name]?.[1] || ''}</span>
                </div>
            </div>
        `;
        if (isHard) {
            return `<div class="task-card-glow" data-task="${t.name}">${cardHTML}</div>`;
        }
        return cardHTML;
    }).join('');
}

// ── Events ───────────────────────────────────────────────
function bindEvents() {
    DOM.btnGetStarted.addEventListener('click', () => {
        DOM.sectionTasks.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    DOM.taskCards.addEventListener('click', e => {
        const glow = e.target.closest('.task-card-glow');
        const card = e.target.closest('.task-card');
        if (glow) {
            selectTask(glow.dataset.task);
        } else if (card) {
            selectTask(card.dataset.task);
        }
    });

    $$('.priority-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            $$('.priority-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            DOM.inputPriority.value = btn.dataset.value;
        });
    });

    DOM.inputReply.addEventListener('input', () => {
        const words = DOM.inputReply.value.trim().split(/\s+/).filter(w => w.length > 0).length;
        DOM.wordCount.textContent = `${words} word${words !== 1 ? 's' : ''}`;
        DOM.wordCount.classList.toggle('enough', words >= 10);
    });

    DOM.actionForm.addEventListener('submit', e => { e.preventDefault(); submitAction(); });
    DOM.btnNewTicket.addEventListener('click', () => resetEpisode());
    DOM.btnChangeTask.addEventListener('click', () => goBackToTasks());
    DOM.btnNextEpisode.addEventListener('click', () => resetEpisode());
    DOM.btnClearHistory.addEventListener('click', clearHistory);
}

// ── Task Selection ───────────────────────────────────────
async function selectTask(taskName) {
    state.currentTask = taskName;
    DOM.sectionHero.classList.add('hidden');
    DOM.sectionHistory.classList.remove('hidden');
    await resetEpisode();
}

async function resetEpisode() {
    try {
        const data = await api('/reset', 'POST', { task_name: state.currentTask });
        state.currentObs = data.observation;
        state.taskConfig = data.task_config;
        showTicket();
        showActionForm();
        hideResults();
    } catch (err) {
        showToast('Failed to load ticket: ' + err.message, 'error');
    }
}

function goBackToTasks() {
    DOM.sectionTicket.classList.add('hidden');
    DOM.sectionAction.classList.add('hidden');
    DOM.sectionResults.classList.add('hidden');
    DOM.sectionTasks.classList.remove('hidden');
    state.currentTask = null;
}

// ── Ticket ───────────────────────────────────────────────
function showTicket() {
    const obs = state.currentObs;
    DOM.ticketId.textContent = obs.ticket_id;
    DOM.taskBadge.textContent = obs.task_name;
    DOM.ticketText.textContent = obs.ticket_text;

    const hints = {
        classify: 'Pick the right category: billing, technical, or general.',
        prioritize: 'Pick the category and assign a priority level.',
        resolve: 'Pick category, priority, and write a reply.',
    };
    DOM.ticketHint.textContent = hints[obs.task_name] || '';

    DOM.sectionTasks.classList.add('hidden');
    DOM.sectionTicket.classList.remove('hidden');

    DOM.sectionTicket.style.animation = 'none';
    DOM.sectionTicket.offsetHeight;
    DOM.sectionTicket.style.animation = '';
}

// ── Action Form ──────────────────────────────────────────
function showActionForm() {
    const cfg = state.taskConfig;
    document.querySelectorAll('input[name="category"]').forEach(r => r.checked = false);
    DOM.inputPriority.value = '';
    DOM.inputReply.value = '';
    DOM.wordCount.textContent = '0 words';
    DOM.wordCount.classList.remove('enough');
    $$('.priority-btn').forEach(b => b.classList.remove('active'));

    DOM.groupPriority.classList.toggle('disabled', !cfg.requires_priority);
    DOM.groupReply.classList.toggle('disabled', !cfg.requires_reply);
    if (DOM.replyTips) DOM.replyTips.classList.toggle('hidden', !cfg.requires_reply);
    if (!cfg.requires_priority) DOM.inputPriority.value = 'low';

    DOM.btnSubmit.disabled = false;
    DOM.btnSubmit.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg> Submit triage`;

    DOM.sectionAction.classList.remove('hidden');
    DOM.sectionResults.classList.add('hidden');
}

// ── Submit ───────────────────────────────────────────────
async function submitAction() {
    if (state.isSubmitting) return;

    const sel = document.querySelector('input[name="category"]:checked');
    const category = sel ? sel.value : '';
    const priority = DOM.inputPriority.value || 'low';
    const reply = DOM.inputReply.value;

    if (!category) { showToast('Please select a category.', 'error'); return; }
    if (state.taskConfig.requires_priority && !priority) { showToast('Please select a priority.', 'error'); return; }

    state.isSubmitting = true;
    DOM.btnSubmit.disabled = true;
    DOM.btnSubmit.innerHTML = '<span class="spinner"></span> Evaluating...';

    try {
        const result = await api('/step', 'POST', { category, priority, reply });
        state.history.push(result);
        showResults(result);
        addHistoryRow(result);
        updateStats();
        const pct = (result.reward.score * 100).toFixed(0);
        showToast(`Score: ${pct}%`, result.reward.score >= 0.5 ? 'success' : 'error');
    } catch (err) {
        showToast('Submission failed: ' + err.message, 'error');
        DOM.btnSubmit.disabled = false;
        DOM.btnSubmit.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg> Submit triage`;
    } finally {
        state.isSubmitting = false;
    }
}

// ── Results ──────────────────────────────────────────────
function showResults(result) {
    const score = result.reward.score;
    const breakdown = result.reward.breakdown;
    const gt = result.ground_truth;
    const action = result.action;
    const obs = result.observation;

    DOM.sectionAction.classList.add('hidden');

    // Score ring
    const circ = 2 * Math.PI * 52;
    const offset = circ - score * circ;
    DOM.scoreRingFill.style.strokeDasharray = circ;
    DOM.scoreRingFill.style.strokeDashoffset = circ;
    animateNumber(DOM.scoreValue, 0, Math.round(score * 100), 1000);
    requestAnimationFrame(() => {
        setTimeout(() => { DOM.scoreRingFill.style.strokeDashoffset = offset; }, 80);
    });

    let lc, lt;
    if (score >= 0.9) { lc = 'excellent'; lt = 'Excellent'; }
    else if (score >= 0.6) { lc = 'good'; lt = 'Good'; }
    else if (score >= 0.3) { lc = 'fair'; lt = 'Fair'; }
    else { lc = 'poor'; lt = 'Needs work'; }
    DOM.scoreLabel.className = `score-label ${lc}`;
    DOM.scoreLabel.textContent = lt;

    // Breakdown
    const bars = [];
    if ('category' in breakdown) {
        const mx = obs.task_name === 'classify' ? 1.0 : obs.task_name === 'prioritize' ? 0.5 : 0.3;
        bars.push({ label: 'Category', value: breakdown.category, max: mx, cls: 'cat' });
    }
    if ('priority' in breakdown) {
        const mx = obs.task_name === 'prioritize' ? 0.5 : 0.3;
        bars.push({ label: 'Priority', value: breakdown.priority, max: mx, cls: 'pri' });
    }
    if ('reply_quality' in breakdown) bars.push({ label: 'Reply quality', value: breakdown.reply_quality, max: 0.4, cls: 'rep' });
    if ('reply_penalty' in breakdown) bars.push({ label: 'Reply penalty', value: Math.abs(breakdown.reply_penalty), max: 0.1, cls: 'pen' });

    DOM.breakdownBars.innerHTML = bars.map(b => `
        <div class="bd-item">
            <div class="bd-label"><span>${b.label}</span><span>${b.value.toFixed(2)} / ${b.max.toFixed(1)}</span></div>
            <div class="bd-track"><div class="bd-fill ${b.cls}" data-w="${b.max > 0 ? (b.value / b.max * 100) : 0}"></div></div>
        </div>
    `).join('');

    requestAnimationFrame(() => {
        setTimeout(() => { $$('.bd-fill').forEach(el => { el.style.width = el.dataset.w + '%'; }); }, 150);
    });

    // Comparison
    const rows = [{ label: 'Category', yours: action.category, truth: gt.true_category, match: action.category.toLowerCase() === gt.true_category.toLowerCase() }];
    if (state.taskConfig.requires_priority) {
        rows.push({ label: 'Priority', yours: action.priority, truth: gt.true_priority, match: action.priority.toLowerCase() === gt.true_priority.toLowerCase() });
    }
    DOM.comparisonTable.innerHTML = `
        <div class="comp-row" style="border:none;padding-bottom:0">
            <div class="comp-label"></div>
            <div class="comp-label" style="text-align:center;font-weight:600;color:var(--white)">Yours</div>
            <div class="comp-label" style="text-align:center;font-weight:600;color:var(--white)">Correct</div>
        </div>
        ${rows.map(r => `<div class="comp-row">
            <div class="comp-label">${r.label}</div>
            <div class="comp-val ${r.match ? 'match' : 'mismatch'}">${r.yours || '\u2014'}</div>
            <div class="comp-val truth">${r.truth}</div>
        </div>`).join('')}
    `;

    // Keywords
    if (state.taskConfig.requires_reply && gt.ideal_reply_keywords?.length > 0) {
        const low = (action.reply || '').toLowerCase();
        DOM.keywordsList.innerHTML = gt.ideal_reply_keywords.map(kw => {
            const f = low.includes(kw.toLowerCase());
            return `<span class="kw-chip ${f ? 'found' : 'missing'}">${f ? '\u2713' : '\u2717'} ${kw}</span>`;
        }).join('');
        DOM.keywordsCard.classList.remove('hidden');
    } else {
        DOM.keywordsCard.classList.add('hidden');
    }

    DOM.sectionResults.classList.remove('hidden');
    DOM.sectionResults.style.animation = 'none';
    DOM.sectionResults.offsetHeight;
    DOM.sectionResults.style.animation = '';
    DOM.sectionResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function hideResults() { DOM.sectionResults.classList.add('hidden'); }

function animateNumber(el, from, to, dur) {
    const start = performance.now();
    const tick = now => {
        const p = Math.min((now - start) / dur, 1);
        el.textContent = Math.round(from + (to - from) * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
}

// ── History ──────────────────────────────────────────────
function addHistoryRow(result) {
    const idx = state.history.length;
    const score = result.reward.score;
    const action = result.action;
    const obs = result.observation;

    let tag;
    if (score >= 0.8) tag = '<span class="res-tag pass">Pass</span>';
    else if (score >= 0.3) tag = '<span class="res-tag partial">Partial</span>';
    else tag = '<span class="res-tag fail">Fail</span>';

    const row = document.createElement('tr');
    row.innerHTML = `
        <td style="font-family:var(--mono);color:var(--g555)">${idx}</td>
        <td><span class="diff-tag ${state.taskConfig.difficulty}">${obs.task_name}</span></td>
        <td style="font-family:var(--mono);font-size:12px">${obs.ticket_id}</td>
        <td>${action.category}</td>
        <td>${action.priority}</td>
        <td><div class="score-bar"><span class="score-bar-val">${(score*100).toFixed(0)}%</span><div class="score-bar-track"><div class="score-bar-fill" style="width:${score*100}%"></div></div></div></td>
        <td>${tag}</td>
    `;
    DOM.historyTbody.prepend(row);
    DOM.historyEmpty.classList.add('hidden');
    DOM.historyWrapper.classList.remove('hidden');
}

function updateStats() {
    const n = state.history.length;
    DOM.statEpisodes.textContent = n;
    if (n > 0) {
        const scores = state.history.map(h => h.reward.score);
        const avg = scores.reduce((a, b) => a + b, 0) / n;
        DOM.statAvgScore.textContent = (avg * 100).toFixed(0) + '%';
        DOM.statBestScore.textContent = (Math.max(...scores) * 100).toFixed(0) + '%';
    } else {
        DOM.statAvgScore.textContent = '\u2014';
        DOM.statBestScore.textContent = '\u2014';
    }
}

async function clearHistory() {
    try {
        await api('/history/clear', 'POST');
        state.history = [];
        DOM.historyTbody.innerHTML = '';
        DOM.historyEmpty.classList.remove('hidden');
        DOM.historyWrapper.classList.add('hidden');
        updateStats();
        showToast('History cleared.', 'info');
    } catch (err) {
        showToast('Failed to clear history.', 'error');
    }
}

document.addEventListener('DOMContentLoaded', init);

// ═══ IMPROVEMENT 1 — Terminal Typewriter ═════════════════
function initTerminalTypewriter() {
    const body = document.querySelector('.terminal-body');
    if (!body) return;
    const lines = body.querySelectorAll('.t-line');
    const cursorEl = body.querySelector('.cursor');
    const progressFill = document.querySelector('.terminal-progress-fill');

    // Store original HTML for each line, then blank them
    const originals = [];
    lines.forEach(line => {
        originals.push(line.innerHTML);
        line.style.opacity = '0';
        line.style.height = line.offsetHeight + 'px';
        line.innerHTML = '';
    });
    if (cursorEl) cursorEl.style.opacity = '0';
    if (progressFill) progressFill.style.width = '0%';

    function typeLineHTML(lineEl, html, charDelay) {
        return new Promise(resolve => {
            // We need to type the *visible text* char by char while preserving HTML tags.
            // Strategy: build a temp element, extract text nodes, type them.
            const temp = document.createElement('div');
            temp.innerHTML = html;
            const textContent = temp.textContent || '';

            // We'll reveal by setting innerHTML to progressively longer substrings
            // but we need to map text positions to HTML positions
            const htmlChars = html;
            let textIdx = 0;
            let htmlIdx = 0;
            const textToHtml = []; // maps text char index -> html index (end of that char)
            let inTag = false;

            for (let i = 0; i < htmlChars.length; i++) {
                if (htmlChars[i] === '<') inTag = true;
                if (!inTag) {
                    textToHtml.push(i + 1);
                    textIdx++;
                }
                if (htmlChars[i] === '>') inTag = false;
            }

            let typed = 0;
            const totalChars = textContent.length;

            if (totalChars === 0) {
                lineEl.innerHTML = html;
                resolve();
                return;
            }

            const interval = setInterval(() => {
                typed++;
                if (typed >= totalChars) {
                    lineEl.innerHTML = html;
                    clearInterval(interval);
                    resolve();
                } else {
                    // Find the HTML position for this text char
                    const cutAt = textToHtml[typed - 1];
                    // We need to close any open tags
                    let partial = htmlChars.substring(0, cutAt);
                    // Close any open span tags
                    const openTags = (partial.match(/<span[^>]*>/g) || []).length;
                    const closeTags = (partial.match(/<\/span>/g) || []).length;
                    for (let j = 0; j < openTags - closeTags; j++) {
                        partial += '</span>';
                    }
                    lineEl.innerHTML = partial;
                }
            }, charDelay);
        });
    }

    let lineIdx = 0;
    function revealNext() {
        if (lineIdx >= lines.length) {
            // All done — show cursor and progress bar
            if (cursorEl) cursorEl.style.opacity = '1';
            if (progressFill) {
                requestAnimationFrame(() => {
                    progressFill.style.width = '85%';
                });
            }
            return;
        }
        const line = lines[lineIdx];
        const html = originals[lineIdx];
        line.style.opacity = '1';
        typeLineHTML(line, html, 30).then(() => {
            lineIdx++;
            setTimeout(revealNext, 600);
        });
    }

    // Start after a brief delay for the terminal fadeInUp animation
    setTimeout(revealNext, 700);
}

// ═══ IMPROVEMENT 2 — Ripple Effect ════════════════════════
function initRippleEffect() {
    const btn = document.getElementById('btn-get-started');
    if (!btn) return;

    btn.addEventListener('click', function(e) {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const ripple = document.createElement('span');
        ripple.className = 'ripple-span';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        btn.appendChild(ripple);

        ripple.addEventListener('animationend', () => ripple.remove());
    });
}
