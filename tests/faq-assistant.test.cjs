const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { SUGGESTIONS, resolveSuggestions, createSession, safeLink } = require('../static/js/faq-assistant.js');
const faq = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/als_comprehensive_faq.json'), 'utf8'));

function fixture(data = faq) {
    const requests = [];
    const session = createSession(async (...args) => {
        requests.push(args);
        return { ok: true, json: async () => data };
    });
    return { session, requests };
}

test('all seven suggestions resolve to their exact FAQ answer and sources', async () => {
    const { session, requests } = fixture();
    const suggestions = await session.load();
    assert.equal(suggestions.length, 7);
    assert.equal(new Set(suggestions.map(q => q.key)).size, 7);
    for (const suggestion of suggestions) {
        const original = faq.categories.flatMap(c => c.questions).find(q => q.question === suggestion.question);
        const selected = session.choose(suggestion.key);
        assert.strictEqual(selected.faq, original);
        assert.ok(selected.faq.sources.length > 0);
    }
    assert.equal(requests.length, 1);
    assert.deepEqual(requests[0], ['/content/faq.json', { method: 'GET', cache: 'no-store' }]);
});

test('reordering FAQs cannot pair a suggested question with the wrong answer', () => {
    const reordered = structuredClone(faq);
    reordered.categories.reverse().forEach(c => c.questions.reverse());
    const before = resolveSuggestions(faq);
    const after = resolveSuggestions(reordered);
    assert.deepEqual(after, before);
    const respiratory = after.find(q => q.key === 'bipap');
    assert.equal(respiratory.sectionNote, faq.categories.find(c => c.id === 'respiratory').section_note);
});

test('every typed question gets the coming-soon notice and makes no network request', async () => {
    const { session, requests } = fixture();
    for (const question of ['A personal question', SUGGESTIONS[0].question, '<img src=x onerror=alert(1)>']) {
        const result = session.submit(`  ${question}  `);
        assert.equal(result.question, question);
        assert.match(result.notice, /coming soon/);
        assert.match(result.notice, /browse all FAQs/);
        assert.equal(requests.length, 0);
    }
    assert.equal(session.submit(' \n '), null);
    await session.load();
    session.submit(SUGGESTIONS[0].question);
    session.choose('feeding');
    session.choose('power');
    assert.equal(requests.length, 1, 'only the FAQ download is allowed');
});

test('unknown or unavailable suggestions never fabricate an answer', async () => {
    const { session } = fixture();
    assert.equal(session.choose('bipap'), null);
    await session.load();
    assert.equal(session.choose('unknown'), null);
    for (const invalid of [{}, { categories: [] }, { categories: [{ questions: [] }] }]) {
        assert.throws(() => resolveSuggestions(invalid));
    }
    const missing = structuredClone(faq);
    missing.categories[0].questions = missing.categories[0].questions.filter(q => q.question !== SUGGESTIONS[0].question);
    assert.throws(() => resolveSuggestions(missing));
});

test('failed loading is recoverable without falling back to an LLM or stale answers', async () => {
    let healthy = false;
    const session = createSession(async () => ({ ok: healthy, json: async () => faq }));
    await assert.rejects(session.load());
    assert.equal(session.choose('bipap'), null);
    healthy = true;
    assert.equal((await session.load()).length, 7);
    healthy = false;
    await assert.rejects(session.load());
    assert.equal(session.choose('bipap'), null);
    assert.match(session.submit('Question').notice, /coming soon/);
});

test('FAQ links allow HTTPS or local paths, rejecting executable and disguised URLs', () => {
    for (const link of ['https://www.nice.org.uk/guidance/NG42', '/faq', '/emergency-protocol#airway-escalation']) assert.equal(safeLink(link), true);
    for (const link of ['javascript:alert(1)', 'data:text/html,hello', '//example.com', '/\\example.com', ' https://example.com', 'https://exam\nple.com', null]) assert.equal(safeLink(link), false);
});
