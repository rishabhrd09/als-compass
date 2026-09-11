/* FAQ-only assistant. Model options are display placeholders, never API arguments. */
(function (root) {
    'use strict';

    // Match by question, not array position: reordering the FAQ cannot pair a prompt
    // with the wrong answer. If an editor renames a question, update its match here.
    const SUGGESTIONS = [
        { key: 'bipap', label: 'When is BiPAP needed?', question: 'When Does a PALS Need BiPAP, How to Decide?' },
        { key: 'feeding', label: 'When should we consider a feeding tube?', question: 'When should we consider a feeding tube (PEG)?' },
        { key: 'saliva', label: 'How can we manage saliva and drooling?', question: 'How Do I Manage Excessive Saliva/Drooling?' },
        { key: 'bedsores', label: 'How can we prevent bedsores?', question: 'How to prevent bedsores?' },
        { key: 'equipment', label: 'What home care equipment do we need?', question: 'What Equipment Do We Need as ALS Progresses?' },
        { key: 'power', label: 'What if the power goes out?', question: 'How do I manage if there is a power cut while PALS is on BiPAP or ventilator?' },
        { key: 'emergency', label: 'How can we prepare for emergency care?', question: 'How can families work with hospital staff during an ALS emergency?' }
    ];
    const COMING_SOON = 'AI answers to your own questions are coming soon. For now, choose a suggested question for an answer from our FAQs, or browse all FAQs for more guidance.';

    function resolveSuggestions(data) {
        if (!Array.isArray(data?.categories)) throw new Error('FAQ data unavailable');
        return SUGGESTIONS.map(suggestion => {
            for (const category of data.categories) {
                const question = category.questions?.find(item => item.question === suggestion.question);
                if (question && typeof question.answer === 'string' && question.answer.trim()) {
                    return { ...suggestion, faq: question, category: category.name, sectionNote: category.section_note || '' };
                }
            }
            throw new Error('A suggested FAQ is unavailable');
        });
    }

    function createSession(fetchFAQ) {
        let questions = [];
        return {
            async load() {
                questions = [];
                const response = await fetchFAQ('/content/faq.json', { method: 'GET', cache: 'no-store' });
                if (!response.ok) throw new Error('FAQ request failed');
                questions = resolveSuggestions(await response.json());
                return questions;
            },
            choose(key) { return questions.find(question => question.key === key) || null; },
            submit(text) {
                const question = text.trim();
                return question ? { question, notice: COMING_SOON } : null;
            }
        };
    }

    function safeLink(value) {
        return typeof value === 'string' && (/^https:\/\//i.test(value) || /^\/(?![\/\\])/.test(value))
            && !/[\u0000-\u0020\\]/.test(value);
    }

    // Rebuild authored FAQ markup from a small allowlist. User messages always use
    // textContent; neither FAQ HTML nor link metadata can introduce executable HTML.
    function faqFragment(doc, html) {
        const template = doc.createElement('template');
        template.innerHTML = html;
        const allowed = new Set(['P', 'DIV', 'SECTION', 'H2', 'H3', 'H4', 'H5', 'H6', 'UL', 'OL', 'LI', 'STRONG', 'B', 'EM', 'I', 'BR', 'A', 'TABLE', 'CAPTION', 'THEAD', 'TBODY', 'TFOOT', 'TR', 'TH', 'TD', 'BLOCKQUOTE', 'SPAN', 'SUP', 'SUB']);
        const blocked = new Set(['SCRIPT', 'STYLE', 'IFRAME', 'OBJECT', 'EMBED', 'SVG', 'MATH', 'FORM', 'INPUT', 'BUTTON', 'TEMPLATE']);
        const classes = new Set(['faq-table-scroll', 'faq-table', 'faq-care-note']);
        function copy(node, parent) {
            if (node.nodeType === 3) { parent.append(doc.createTextNode(node.textContent)); return; }
            if (node.nodeType !== 1 || blocked.has(node.tagName)) return;
            let destination = parent;
            if (allowed.has(node.tagName)) {
                destination = doc.createElement(node.tagName.toLowerCase());
                const className = [...node.classList].filter(name => classes.has(name)).join(' ');
                if (className) destination.className = className;
                if (node.tagName === 'A' && safeLink(node.getAttribute('href'))) {
                    destination.setAttribute('href', node.getAttribute('href'));
                    if (/^https:/i.test(node.getAttribute('href'))) {
                        destination.setAttribute('target', '_blank');
                        destination.setAttribute('rel', 'noopener noreferrer');
                    }
                }
                if (node.tagName === 'TH' && ['row', 'col'].includes(node.getAttribute('scope'))) destination.setAttribute('scope', node.getAttribute('scope'));
                if (className.includes('faq-table-scroll')) {
                    destination.setAttribute('tabindex', '0');
                    destination.setAttribute('role', 'region');
                    destination.setAttribute('aria-label', node.getAttribute('aria-label') || 'FAQ table');
                }
                parent.append(destination);
            }
            node.childNodes.forEach(child => copy(child, destination));
        }
        const result = doc.createDocumentFragment();
        template.content.childNodes.forEach(node => copy(node, result));
        return result;
    }

    function mount(doc, win) {
        const wrapper = doc.getElementById('faqAssistant');
        if (!wrapper) return;
        const byId = id => doc.getElementById(id);
        const session = createSession(win.fetch.bind(win));
        const messages = byId('chatMessages');
        const input = byId('userInput');
        const send = byId('sendBtn');
        const tools = byId('assistantTools');
        const toggle = byId('assistantToolsToggle');
        const mobile = win.matchMedia('(max-width: 768px)');
        function element(tag, className, text) {
            const el = doc.createElement(tag);
            if (className) el.className = className;
            if (text) el.textContent = text;
            return el;
        }
        function faqLink() {
            const link = element('a', 'answer-faq-link', 'Browse all FAQs ↗');
            link.href = '/faq';
            return link;
        }
        function message(role) {
            const row = element('div', `message ${role}`);
            row.setAttribute('aria-label', role === 'user' ? 'Your question' : 'Care assistant');
            const avatar = element('div', 'avatar');
            avatar.setAttribute('aria-hidden', 'true');
            avatar.append(element('i', role === 'user' ? 'fas fa-user' : 'fas fa-compass'));
            const content = element('div', 'message-content');
            row.append(avatar, content);
            return { row, content };
        }
        function addUser(text) {
            const item = message('user');
            item.content.textContent = text;
            messages.append(item.row);
        }
        function reveal(item, focus) {
            messages.append(item.row);
            // A long FAQ must open at the beginning, not jump past its guidance.
            messages.scrollTop += item.row.getBoundingClientRect().top - messages.getBoundingClientRect().top - 20;
            if (focus) { item.content.tabIndex = -1; item.content.focus({ preventScroll: true }); }
        }
        function chooseQuestion(key) {
            const entry = session.choose(key);
            if (!entry) return;
            addUser(entry.faq.question);
            const answer = message('assistant');
            answer.content.append(element('p', 'message-eyebrow', `From our FAQs · ${entry.category}`));
            const body = element('div', 'faq-answer-content');
            body.append(faqFragment(doc, entry.faq.answer));
            answer.content.append(body);
            if (entry.sectionNote) answer.content.append(element('p', 'faq-care-note', entry.sectionNote));
            for (const [field, label] of [['warning', 'Important'], ['recommendation', 'Tip']]) {
                if (entry.faq[field]) answer.content.append(element('p', 'faq-care-note', `${label}: ${entry.faq[field]}`));
            }
            const sources = entry.faq.sources?.filter(source => safeLink(source.url)) || [];
            if (sources.length) {
                const reading = element('details', 'answer-sources');
                reading.append(element('summary', '', 'Further reading'));
                const list = element('ul');
                sources.forEach(source => {
                    const li = element('li');
                    const link = element('a', '', source.label);
                    link.href = source.url; link.target = '_blank'; link.rel = 'noopener noreferrer';
                    li.append(link); list.append(li);
                });
                reading.append(list); answer.content.append(reading);
            }
            answer.content.append(faqLink());
            if (mobile.matches) { tools.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); }
            reveal(answer, true);
        }
        async function loadQuestions() {
            const list = byId('suggestedQuestions');
            const status = byId('suggestionsStatus');
            list.replaceChildren(); list.setAttribute('aria-busy', 'true');
            status.textContent = 'Loading FAQ questions…'; status.hidden = false;
            byId('retryQuestions').hidden = true;
            try {
                const questions = await session.load();
                questions.forEach(question => {
                    const button = element('button', 'suggestion-btn', question.label);
                    button.type = 'button'; button.dataset.faqKey = question.key;
                    button.addEventListener('click', () => chooseQuestion(question.key));
                    list.append(button);
                });
                status.textContent = 'Seven FAQ questions ready.';
                status.hidden = true;
            } catch (_) {
                status.textContent = 'We couldn’t load the suggested questions. Please try again or browse the FAQs.';
                byId('retryQuestions').hidden = false;
            } finally { list.setAttribute('aria-busy', 'false'); }
        }
        function resizeInput() {
            input.style.height = 'auto';
            input.style.height = `${Math.min(input.scrollHeight, 140)}px`;
            send.disabled = !input.value.trim();
        }
        function submit(event) {
            event.preventDefault();
            const result = session.submit(input.value);
            if (!result) return;
            addUser(result.question);
            const reply = message('assistant');
            reply.content.classList.add('coming-soon-message');
            reply.content.append(element('p', 'message-eyebrow', 'AI integration coming soon'), element('p', '', result.notice), faqLink());
            input.value = ''; resizeInput();
            reveal(reply, false);
            input.focus({ preventScroll: true });
        }
        byId('questionForm').addEventListener('submit', submit);
        input.addEventListener('input', resizeInput);
        input.addEventListener('keydown', event => {
            if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) submit(event);
        });
        byId('retryQuestions').addEventListener('click', loadQuestions);
        toggle.addEventListener('click', () => {
            const open = toggle.getAttribute('aria-expanded') !== 'true';
            toggle.setAttribute('aria-expanded', String(open)); tools.classList.toggle('open', open);
        });
        function sizeWrapper() {
            const height = win.visualViewport?.height || win.innerHeight;
            const navHeight = doc.querySelector('.navbar')?.getBoundingClientRect().height || 120;
            wrapper.style.height = `${Math.max(420, height - navHeight)}px`;
        }
        sizeWrapper(); resizeInput();
        win.addEventListener('resize', sizeWrapper);
        win.visualViewport?.addEventListener('resize', sizeWrapper);
        if (win.ResizeObserver) new win.ResizeObserver(sizeWrapper).observe(doc.querySelector('.navbar'));
        loadQuestions();
    }
    if (typeof module !== 'undefined' && module.exports) module.exports = { SUGGESTIONS, COMING_SOON, resolveSuggestions, createSession, safeLink, faqFragment, mount };
    else mount(root.document, root);
})(typeof window === 'undefined' ? globalThis : window);
