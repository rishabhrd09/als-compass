const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'static/js/care-faq.js'), 'utf8');
const data = JSON.parse(fs.readFileSync(path.join(root, 'data/als_comprehensive_faq.json'), 'utf8'));

function fixture() {
    class Element {
        constructor(text = '') { this.textContent = text; this.dataset = {}; this.attrs = {}; this.hidden = false; this.value = ''; this.events = {}; this.children = []; this.classes = new Set(); this.classList = { toggle: (name, enabled) => enabled ? this.classes.add(name) : this.classes.delete(name) }; }
        addEventListener(name, fn) { this.events[name] = fn; }
        setAttribute(name, value) { this.attrs[name] = value; }
        getAttribute(name) { return this.attrs[name]; }
        append(...children) { this.children.push(...children); }
        appendChild(child) { this.children.push(child); }
        focus() { this.focused = true; }
        querySelectorAll() { return this.children; }
    }
    const sections = data.categories.map(category => {
        const section = new Element(); section.dataset.category = category.id;
        section.children = category.questions.map(question => {
            const item = new Element(`${question.question} ${question.answer}`); item.dataset.tags = (question.tags || []).join(' '); return item;
        }); return section;
    });
    const buttons = ['all', ...data.categories.map(c => c.id)].map(id => { const button = new Element(); button.dataset.categoryId = id; return button; });
    const ids = Object.fromEntries(['faqSearch','faqResultsTitle','faqResultCount','faqClear','faqEmpty','faqReset','faqRetry','faqContent','faqError','categoryNav','keyPrinciples'].map(id => [id, new Element()]));
    const doc = new Element(); doc.getElementById = id => ids[id]; doc.createElement = () => new Element();
    doc.querySelectorAll = selector => selector === '.category-pill' ? buttons : sections;
    const context = vm.createContext({ document: doc, console, fetch: async () => ({ ok: true, json: async () => data }) });
    vm.runInContext(source, context); vm.runInContext('faqData = ' + JSON.stringify(data), context);
    return { context, doc, ids, buttons, sections, Element };
}

test('search and topic filters remain combined when changing topics', () => {
    const f = fixture(); f.ids.faqSearch.value = 'BIPAP'; f.context.applyFilters();
    const allCount = f.sections.flatMap(s => s.children).filter(item => !item.hidden).length;
    assert.ok(allCount > 0);
    f.context.filterCategory('feeding');
    assert.ok(f.sections.filter(s => s.dataset.category !== 'feeding').every(s => s.hidden));
    const expected = data.categories.find(c => c.id === 'feeding').questions.filter(q => `${q.question} ${q.answer} ${(q.tags || []).join(' ')}`.toLowerCase().includes('bipap')).length;
    assert.equal(f.ids.faqResultCount.textContent, `${expected} ${expected === 1 ? 'question' : 'questions'} found`);
    assert.equal(f.ids.faqEmpty.hidden, expected !== 0);
    assert.equal(f.buttons.find(b => b.dataset.categoryId === 'feeding').attrs['aria-pressed'], 'true');
    f.context.filterCategory('all');
    assert.equal(f.sections.flatMap(s => s.children).filter(item => !item.hidden).length, allCount);
});

test('empty search, clearing and resetting give recoverable results and keyboard focus', () => {
    const f = fixture(); f.context.initSearch(); f.context.filterCategory('feeding');
    f.ids.faqSearch.value = 'no-such-question-4837'; f.ids.faqSearch.events.input();
    assert.equal(f.ids.faqEmpty.hidden, false); assert.equal(f.ids.faqClear.hidden, false);
    f.ids.faqClear.events.click(); assert.equal(f.ids.faqSearch.value, ''); assert.equal(f.ids.faqSearch.focused, true);
    assert.equal(f.ids.faqResultsTitle.textContent, 'Feeding & Nutrition');
    f.ids.faqReset.events.click(); assert.equal(f.ids.faqResultsTitle.textContent, 'All Topics');
    assert.ok(f.sections.every(s => !s.hidden)); assert.equal(f.ids.faqEmpty.hidden, true);
});

test('question buttons synchronize accessible state and answer visibility', () => {
    const f = fixture(); const item = new f.Element(); const answer = new f.Element(); answer.hidden = true;
    const button = new f.Element(); button.closest = () => item; item.querySelector = () => answer;
    button.setAttribute('aria-expanded', 'false');
    f.context.toggleFaq(button); assert.equal(button.attrs['aria-expanded'], 'true'); assert.equal(answer.hidden, false); assert.ok(item.classes.has('open'));
    f.context.toggleFaq(button); assert.equal(button.attrs['aria-expanded'], 'false'); assert.equal(answer.hidden, true);
});

test('every existing question still renders with unique accessible answer relationships', () => {
    const f = fixture(); const ids = new Set();
    for (const category of data.categories) category.questions.forEach((question, index) => {
        const id = `${category.id}-${index}`; const html = f.context.renderQuestion(question, id);
        assert.ok(html.includes(question.question));
        assert.ok(html.includes(`aria-controls="answer-${id}"`)); assert.ok(html.includes(`aria-labelledby="question-${id}"`));
        assert.ok(html.includes('aria-expanded="false"')); assert.ok(html.includes(' hidden>'));
        assert.ok(!ids.has(id)); ids.add(id);
        if (question.warning) assert.ok(html.includes(question.warning));
        if (question.recommendation) assert.ok(html.includes(question.recommendation));
        for (const perspective of question.perspectives || []) assert.ok(html.includes(perspective));
    });
    f.context.renderFAQ('all');
    assert.equal((f.ids.faqContent.innerHTML.match(/class="faq-item"/g) || []).length, ids.size);
});

test('answer formatting retains paragraphs, emphasis and separate bullet lists', () => {
    const f = fixture(); const html = f.context.formatAnswer('First paragraph.\n\n**Checklist**\n• First item\n• Second item\n\nLast paragraph.');
    assert.match(html, /<p>First paragraph\.<\/p>/);
    assert.match(html, /<strong>Checklist<\/strong>/);
    assert.match(html, /<ul class="faq-list"><li>First item<\/li><li>Second item<\/li><\/ul>/);
    assert.match(html, /<p>Last paragraph\.<\/p>/);
    assert.ok(!html.includes('<p><ul'));
});

test('structured answers retain valid blocks instead of nesting tables and headings in paragraphs', () => {
    const f = fixture();
    const html = '<p>Summary.</p><h4>Practical care</h4><ul><li>A step.</li></ul><div class="faq-table-scroll"><table><caption>Options</caption><tbody><tr><th scope="row">One</th><td>Two</td></tr></tbody></table></div>';
    assert.equal(f.context.formatAnswer(html), html);
    for (const category of data.categories) for (const question of category.questions) {
        const rendered = f.context.formatAnswer(question.answer);
        assert.ok(!/<p>\s*<(?:p|h4|ul|ol|div|table)\b/.test(rendered));
    }
});

test('further-reading links escape labels and attributes and omit non-HTTPS destinations', () => {
    const f = fixture();
    const rendered = f.context.renderQuestion({ question: 'Question?', answer: '<p>Answer.</p>', sources: [
        { label: 'Advice <script> & notes', url: 'https://example.org/guide?query="value"' },
        { label: 'Invalid link', url: 'javascript:alert(1)' }
    ] }, 'sources');
    assert.match(rendered, /aria-label="Further reading"/);
    assert.ok(rendered.includes('Advice &lt;script&gt; &amp; notes'));
    assert.ok(rendered.includes('query=&quot;value&quot;'));
    assert.ok(!rendered.includes('javascript:'));
});

test('Important labels appear once while the note and warning wording is preserved', () => {
    const f = fixture();
    for (const input of ['Important: Keep ready.', 'Important: Important: Keep ready.', '**Important:** Keep ready.', 'Keep ready.']) {
        assert.equal(f.context.withoutImportantPrefix(input), 'Keep ready.');
        const html = f.context.renderQuestion({ question: 'A question?', answer: 'An answer.', warning: input }, 'example');
        assert.equal((html.match(/Important:/g) || []).length, 1);
        assert.ok(html.includes('Keep ready.'));
    }
    f.context.renderFAQ('all');
    assert.ok(!/Important:<\/strong>\s*Important:/i.test(f.ids.faqContent.innerHTML));
    for (const category of data.categories) {
        if (category.section_note) assert.ok(f.ids.faqContent.innerHTML.includes(f.context.withoutImportantPrefix(category.section_note)));
    }
});

test('data load failures show a retry state and do not leave an indefinite loading indicator', async () => {
    const f = fixture(); f.context.fetch = async () => ({ ok: false });
    await f.context.loadFAQData(); assert.equal(f.ids.faqError.hidden, false); assert.equal(f.ids.faqContent.attrs['aria-busy'], 'false');
    f.context.fetch = async () => ({ ok: true, json: async () => data });
    await f.context.loadFAQData(); assert.equal(f.ids.faqError.hidden, true); assert.equal(f.ids.faqContent.attrs['aria-busy'], 'false');
    assert.ok(f.ids.categoryNav.children.length > 0); assert.ok(f.ids.faqContent.innerHTML.includes('faq-question'));
});
