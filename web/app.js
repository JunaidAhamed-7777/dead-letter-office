'use strict';

const $ = (id) => document.getElementById(id);
const state = { archive: null, result: null, request: null, revision: 0, busy: false, returnFocus: null };
const initialResults = $('results').innerHTML;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = String(text);
  return node;
}

function announce(message) { $('live-status').textContent = message; }

function formatDate(value) {
  if (!value) return 'Undated';
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const date = new Date(`${value}T12:00:00Z`);
    if (!Number.isNaN(date.getTime())) return new Intl.DateTimeFormat('en', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(date);
  }
  return value;
}

function setBusy(busy) {
  state.busy = busy;
  $('ask-button').disabled = busy || !state.archive;
  $('ask-button').setAttribute('aria-busy', String(busy));
  $('ask-button').querySelector('.button-label').textContent = busy ? 'Searching the letters…' : 'Search the letters';
  $('results').setAttribute('aria-busy', String(busy));
}

function clearError() {
  $('question-error').textContent = '';
  $('question').removeAttribute('aria-invalid');
}

function invalidateRequest() {
  state.revision += 1;
  if (state.request) state.request.abort();
  state.request = null;
  setBusy(false);
}

function resetResults() {
  state.result = null;
  $('results').innerHTML = initialResults;
  $('result-meta').textContent = 'No invented testimony';
}

function clearQuestion() {
  invalidateRequest();
  $('question').value = '';
  $('question').style.height = '';
  $('clear-question').hidden = true;
  clearError();
  resetResults();
  $('question').focus();
  announce('Question cleared.');
}

function showView() {
  const view = window.location.hash === '#letters' ? 'letters' : 'ask';
  // A modal belongs to the view that opened it. Browser history must dismiss
  // it rather than leave an old letter obscuring the newly selected view.
  const openDialogs = document.querySelectorAll('dialog[open]');
  if (openDialogs.length) {
    state.returnFocus = $(`nav-${view}`);
    openDialogs.forEach((dialog) => dialog.close());
  }
  $('ask-view').hidden = view !== 'ask';
  $('letters-view').hidden = view !== 'letters';
  for (const item of ['ask', 'letters']) {
    if (view === item) $(`nav-${item}`).setAttribute('aria-current', 'page');
    else $(`nav-${item}`).removeAttribute('aria-current');
  }
  document.title = `Dead Letter Office — ${view === 'ask' ? 'Ask the archive' : 'Read the letters'}`;
}

function navigate(view) {
  if (window.location.hash !== `#${view}`) window.location.hash = view;
  else showView();
}

async function fetchArchive() {
  $('retry-archive').disabled = true;
  $('archive-load-error').hidden = true;
  $('connection-label').textContent = 'Opening archive';
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch('/api/archive', { signal: controller.signal, cache: 'no-store' });
    if (!response.ok) throw new Error('Archive unavailable');
    const data = await response.json();
    if (!Array.isArray(data.letters)) throw new Error('Archive data is incomplete');
    state.archive = data;
    $('nav-count').textContent = String(data.letters.length).padStart(2, '0');
    $('connection-label').textContent = 'Local archive';
    $('ask-button').disabled = false;
    $('collection-meta').textContent = `${data.letters.length} fictional letters. Nothing borrowed from real lives.`;
    renderExamples(data.examples || []);
    renderLetters(data.letters);
    renderModel(data.model || {});
    $('results').hidden = false;
    announce(`${data.letters.length} letters ready to search.`);
  } catch (error) {
    $('connection-label').textContent = 'Archive unavailable';
    $('archive-load-error').hidden = false;
    $('results').hidden = true;
    $('collection-meta').textContent = 'The local archive is unavailable. Return to Ask the archive to try again.';
    announce('The archive could not be opened. Check the local server and try again.');
  } finally {
    clearTimeout(timeout);
    $('retry-archive').disabled = false;
  }
}

function renderExamples(examples) {
  $('examples').replaceChildren();
  for (const example of examples.slice(0, 3)) {
    const question = typeof example === 'string' ? example : example.question;
    if (!question) continue;
    const button = element('button', 'example-button');
    button.type = 'button';
    button.append(element('span', '', question), element('span', '', '→'));
    button.lastChild.setAttribute('aria-hidden', 'true');
    button.addEventListener('click', () => {
      invalidateRequest();
      $('question').value = question;
      $('clear-question').hidden = false;
      clearError();
      askQuestion();
    });
    $('examples').append(button);
  }
  $('examples-section').hidden = !$('examples').childElementCount;
}

function renderModel(model) {
  const lines = [model.name || 'Local semantic retrieval'];
  if (model.dimensions) lines.push(`${model.dimensions} embedding dimensions`);
  if (model.passages) lines.push(`${model.passages} searchable passages`);
  if (model.description) lines.push(model.description);
  $('model-details').replaceChildren(...lines.map((line) => element('div', '', line)));
}

function renderLetters(letters) {
  $('letter-grid').replaceChildren();
  for (const letter of letters) {
    const button = element('button', 'letter-card');
    button.type = 'button';
    button.append(element('span', 'eyebrow', `${letter.id} · ${formatDate(letter.date)}`));
    button.append(element('h2', '', letter.title));
    button.append(element('p', 'letter-description', letter.description || letter.location || 'A letter from the collection.'));
    const byline = element('span', 'letter-byline');
    byline.append(element('span', '', letter.author || 'Unknown writer'), element('span', '', '→'));
    byline.lastChild.setAttribute('aria-hidden', 'true');
    button.append(byline);
    button.addEventListener('click', () => openLetter(letter.id));
    $('letter-grid').append(button);
  }
}

function openDialog(dialog) {
  state.returnFocus = document.activeElement;
  dialog.showModal();
  document.body.style.overflow = 'hidden';
  dialog.querySelector('.dialog-close').focus();
}

function openLetter(letterId, passageId) {
  const letter = state.archive?.letters.find((entry) => entry.id === letterId);
  if (!letter) { announce('This source letter is not available in the loaded archive.'); return; }
  const content = $('letter-content');
  content.replaceChildren();
  content.append(element('p', 'eyebrow', `${letter.id} · Fictional letter`));
  const heading = element('h2', '', letter.title);
  heading.id = 'letter-dialog-title';
  content.append(heading);
  const metadata = element('div', 'letter-metadata');
  metadata.append(element('div', '', `${letter.author || 'Unknown writer'}${letter.recipient ? ` → ${letter.recipient}` : ''}`));
  metadata.append(element('div', '', `${formatDate(letter.date)}${letter.location ? ` · ${letter.location}` : ''}`));
  content.append(metadata);
  const body = element('div', 'letter-body');
  for (const passage of letter.passages || []) {
    const paragraph = element('p', passage.id === passageId ? 'highlight-passage' : '', passage.text);
    paragraph.dataset.passageId = passage.id;
    paragraph.append(element('span', 'passage-id', passage.id));
    body.append(paragraph);
  }
  content.append(body, element('p', 'letter-fiction-note', 'An original work of fiction. These are not the words or records of a real person.'));
  openDialog($('letter-dialog'));
  const highlighted = body.querySelector('.highlight-passage');
  if (highlighted) setTimeout(() => highlighted.scrollIntoView({ block: 'center', behavior: 'instant' }), 0);
  else $('letter-dialog').scrollTop = 0;
}

function loadingState() {
  const wrapper = element('div', 'loading-state');
  const mark = element('div', 'loading-mark');
  mark.setAttribute('aria-hidden', 'true');
  wrapper.append(mark, element('h2', '', 'Looking through the letters…'), element('p', '', 'Comparing your question with the local archive.'));
  $('results').replaceChildren(wrapper);
  $('result-meta').textContent = 'Local model running';
}

async function askQuestion() {
  const question = $('question').value.trim();
  if (!question) {
    $('question-error').textContent = 'Write a question to search the letters.';
    $('question').setAttribute('aria-invalid', 'true');
    $('question').focus();
    return;
  }
  if (!state.archive || state.busy) return;
  clearError();
  invalidateRequest();
  const revision = state.revision;
  const controller = new AbortController();
  state.request = controller;
  const timeout = setTimeout(() => controller.abort(), 20000);
  setBusy(true);
  loadingState();
  announce('Searching the local archive.');
  try {
    const response = await fetch('/api/ask', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }), signal: controller.signal, cache: 'no-store'
    });
    if (!response.ok) throw new Error('Search unavailable');
    const result = await response.json();
    if (revision !== state.revision) return;
    if (!Array.isArray(result.sources) || !Array.isArray(result.answer)) throw new Error('Search result is incomplete');
    state.result = result;
    renderResult(result);
    announce(result.status === 'unknown' ? 'The archive does not have enough evidence to answer.' : `${result.sources.length} source passages found. Read the quotations and limitations.`);
  } catch (error) {
    if (revision !== state.revision) return;
    state.result = null;
    const wrapper = element('div', 'error-state');
    wrapper.append(element('p', 'eyebrow', 'The search stopped'), element('h2', '', 'The reading room lost its connection.'), element('p', '', 'Your question is still here. Check that the local server is running, then search again.'));
    const retry = element('button', 'paper-button', 'Search again');
    retry.type = 'button';
    retry.addEventListener('click', askQuestion);
    wrapper.append(retry);
    $('results').replaceChildren(wrapper);
    $('result-meta').textContent = 'No answer returned';
    announce('The search failed. Your question has been kept. You can search again.');
  } finally {
    clearTimeout(timeout);
    if (revision === state.revision) { state.request = null; setBusy(false); }
  }
}

function renderResult(result) {
  const finding = element('div', 'finding');
  finding.dataset.status = result.status;
  const statusText = { found: 'Related passages · check the sources', uncertain: 'Partial or conflicting evidence', unknown: 'The archive cannot answer this' };
  finding.append(element('p', 'finding-status', statusText[result.status] || statusText.uncertain));
  finding.append(element('h2', '', result.question || $('question').value.trim()));
  if (result.summary) finding.append(element('p', 'finding-summary', result.summary));
  if (result.sources.length) finding.append(element('p', 'retrieval-note', 'Related text is not proof that an answer exists. These are source quotations, not a generated answer.'));
  const quotes = element('div', 'answer-quotes');
  for (const answer of result.answer) {
    const quote = element('blockquote', 'answer-quote');
    quote.append(element('p', '', `“${answer.text}”`));
    const sourceIndex = result.sources.findIndex((source) => source.id === answer.source_id);
    const source = result.sources[sourceIndex];
    if (source) {
      const citation = element('button', 'citation', `[${sourceIndex + 1}] ${source.title} · ${answer.source_id} →`);
      citation.type = 'button';
      citation.setAttribute('aria-label', `Read source ${sourceIndex + 1}: ${source.title}, passage ${answer.source_id}`);
      citation.addEventListener('click', () => openLetter(answer.letter_id || source.letter_id, answer.source_id));
      quote.append(citation);
    } else {
      quote.append(element('span', 'citation', 'Source not available. Do not rely on this passage.'));
    }
    quotes.append(quote);
  }
  finding.append(quotes);
  if (result.limitation) {
    const note = element('p', 'limit-note');
    note.append(element('strong', '', 'What this does not tell us. '), document.createTextNode(result.limitation));
    finding.append(note);
  }
  if (result.sources.length) {
    const section = element('section', 'source-section');
    section.setAttribute('aria-label', 'Source passages');
    section.append(element('h3', 'eyebrow', `The paper trail · ${result.sources.length} ${result.sources.length === 1 ? 'passage' : 'passages'}`));
    const list = element('div', 'source-list');
    result.sources.forEach((source, index) => {
      const button = element('button', 'source-card');
      button.type = 'button';
      button.setAttribute('aria-label', `Read source ${index + 1}: ${source.title}`);
      const top = element('span', 'source-topline');
      top.append(element('span', 'source-title', source.title), element('span', 'source-number', `[${index + 1}] →`));
      button.append(top);
      const score = Number.isFinite(source.score) ? ` · Similarity ${source.score.toFixed(3)}` : '';
      button.append(element('div', 'source-details', `${source.author || 'Unknown writer'} · ${formatDate(source.date)}${score}`));
      if (source.included_because) button.append(element('div', 'source-details', source.included_because));
      button.append(element('p', 'source-excerpt', source.text));
      button.addEventListener('click', () => openLetter(source.letter_id, source.id));
      list.append(button);
    });
    section.append(list);
    finding.append(section);
  }
  const actions = element('div', 'finding-actions');
  const exportButton = element('button', 'paper-button', 'Save findings .txt ↓');
  exportButton.type = 'button';
  exportButton.addEventListener('click', exportResult);
  actions.append(exportButton);
  finding.append(actions);
  $('results').replaceChildren(finding);
  const elapsed = Number.isFinite(result.elapsed_ms) ? `${Math.round(result.elapsed_ms)} ms · ` : '';
  $('result-meta').textContent = `${elapsed}Local retrieval`;
}

function exportResult() {
  const result = state.result;
  if (!result) return;
  const lines = ['DEAD LETTER OFFICE', 'Fictional collection · source quotations, not generated testimony', '', `Question: ${result.question}`, `Result: ${result.status}`, '', result.summary || '', ''];
  for (const answer of result.answer) lines.push(`“${answer.text}”`, `Source: ${answer.source_id}`, '');
  lines.push(`Limitations: ${result.limitation || 'Retrieval similarity is not a truth or confidence score.'}`, '', 'SOURCE PASSAGES');
  result.sources.forEach((source, index) => lines.push(`[${index + 1}] ${source.title} — ${source.author || 'Unknown writer'}, ${source.date || 'undated'}`, `Passage ID: ${source.id}`, source.text, ''));
  const url = URL.createObjectURL(new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' }));
  const link = element('a');
  link.href = url;
  link.download = 'dead-letter-office-findings.txt';
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  announce('Findings downloaded as a text file.');
}

$('question-form').addEventListener('submit', (event) => { event.preventDefault(); askQuestion(); });
$('question').addEventListener('input', () => {
  $('clear-question').hidden = !$('question').value;
  clearError();
  if (state.busy) { invalidateRequest(); resetResults(); announce('Previous search canceled. Submit your updated question.'); }
  $('question').style.height = 'auto';
  $('question').style.height = `${Math.min($('question').scrollHeight, 360)}px`;
});
$('question').addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && (event.ctrlKey || event.metaKey) && !event.isComposing) { event.preventDefault(); askQuestion(); }
});
$('clear-question').addEventListener('click', clearQuestion);
$('nav-ask').addEventListener('click', () => navigate('ask'));
$('nav-letters').addEventListener('click', () => navigate('letters'));
$('retry-archive').addEventListener('click', fetchArchive);
$('about-button').addEventListener('click', () => openDialog($('about-dialog')));
$('close-letter').addEventListener('click', () => $('letter-dialog').close());
$('close-about').addEventListener('click', () => $('about-dialog').close());
for (const id of ['letter-dialog', 'about-dialog']) {
  $(id).addEventListener('close', () => { document.body.style.overflow = ''; if (state.returnFocus?.isConnected) state.returnFocus.focus(); });
  $(id).addEventListener('click', (event) => {
    if (event.target !== $(id)) return;
    const bounds = $(id).getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) $(id).close();
  });
}
window.addEventListener('hashchange', showView);
// Pure-JavaScript actions remain disabled until their handlers are bound.
document.querySelectorAll('[data-js-control]').forEach((button) => { button.disabled = false; });
showView();
fetchArchive();
