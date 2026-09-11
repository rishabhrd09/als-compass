let faqData = null;
    let currentCategory = 'all';

    // Function to strip emojis from content
    function stripEmojis(text) {
        // Remove common emojis used in FAQs
        return text
            .replace(/[\u{1F600}-\u{1F64F}]/gu, '') // Emoticons
            .replace(/[\u{1F300}-\u{1F5FF}]/gu, '') // Misc symbols and pictographs
            .replace(/[\u{1F680}-\u{1F6FF}]/gu, '') // Transport and map symbols
            .replace(/[\u{1F700}-\u{1F77F}]/gu, '') // Alchemical symbols
            .replace(/[\u{1F780}-\u{1F7FF}]/gu, '') // Geometric shapes extended
            .replace(/[\u{1F800}-\u{1F8FF}]/gu, '') // Supplemental arrows
            .replace(/[\u{1F900}-\u{1F9FF}]/gu, '') // Supplemental symbols and pictographs
            .replace(/[\u{1FA00}-\u{1FA6F}]/gu, '') // Chess symbols
            .replace(/[\u{1FA70}-\u{1FAFF}]/gu, '') // Symbols and pictographs extended-A
            .replace(/[\u{2600}-\u{26FF}]/gu, '')   // Misc symbols
            .replace(/[\u{2700}-\u{27BF}]/gu, '')   // Dingbats
            .replace(/[\u{2300}-\u{23FF}]/gu, '')   // Misc technical
            .replace(/✅|❌|⚠️|⚠|🚨|📋|📝|💡|🔬|📊|💬|🇮🇳|🔀|✓/g, '') // Specific emojis
            .replace(/[ \t]+/g, ' ')  // Clean up extra whitespace
            .trim();
    }

    document.addEventListener('DOMContentLoaded', async function () {
        initSearch();
        await loadFAQData();
    });

    async function loadFAQData() {
        try {
            document.getElementById('faqError').hidden = true;
            document.getElementById('faqContent').setAttribute('aria-busy', 'true');
            const response = await fetch('/content/faq.json');
            if (!response.ok) throw new Error('FAQ request failed');
            faqData = await response.json();
            if (!Array.isArray(faqData.categories)) throw new Error('FAQ data unavailable');
            renderCategories();
            renderFAQ('all');
            renderKeyPrinciples();
            applyFilters();
        } catch (error) {
            document.getElementById('faqError').hidden = false;
            document.getElementById('faqResultCount').textContent = 'Questions unavailable';
        } finally {
            document.getElementById('faqContent').setAttribute('aria-busy', 'false');
        }
    }

    function renderCategories() {
        const nav = document.getElementById('categoryNav');
        const total = faqData.categories.reduce((sum, category) => sum + category.questions.length, 0);
        const categories = [{ id: 'all', name: 'All Topics', questions: { length: total } }, ...faqData.categories];
        nav.innerHTML = '';
        categories.forEach(category => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'category-pill';
            button.dataset.categoryId = category.id;
            const label = document.createElement('span'); label.textContent = category.name;
            const count = document.createElement('span'); count.className = 'faq-topic-count'; count.textContent = category.questions.length;
            count.setAttribute('aria-hidden', 'true');
            button.append(label, count);
            button.addEventListener('click', () => filterCategory(category.id));
            nav.appendChild(button);
        });
    }

    function filterCategory(categoryId) {
        currentCategory = categoryId;
        applyFilters();
    }

    function renderFAQ(categoryId) {
        const content = document.getElementById('faqContent');
        let html = '';

        const categoriesToShow = categoryId === 'all'
            ? faqData.categories
            : faqData.categories.filter(c => c.id === categoryId);

        categoriesToShow.forEach(category => {
            const questions = category.questions;

            if (questions.length === 0) return;

            html += `<div class="faq-section" data-category="${category.id}">
            <h2 class="faq-section-title">${category.name}</h2>`;

            // Display section note if present
            if (category.section_note) {
                html += `<div class="warning-box" style="margin-bottom: 1.25rem;"><strong>Important:</strong> ${withoutImportantPrefix(category.section_note)}</div>`;
            }

            questions.forEach((q, index) => {
                html += renderQuestion(q, `${category.id}-${index}`);
            });

            html += `</div>`;
        });

        content.innerHTML = html;
    }


    function withoutImportantPrefix(text) {
        return text.replace(/^(?:\s*(?:\*\*)?Important\s*:(?:\*\*)?\s*)+/i, '');
    }

    function renderQuestion(q, id) {
        let answerHtml = formatAnswer(q.answer);

        // Conditional guidance
        if (q.conditional) {
            answerHtml += renderConditional(q.conditional);
        }

        // Warning - no emoji
        if (q.warning) {
            answerHtml += `<div class="warning-box"><strong>Important:</strong> ${withoutImportantPrefix(q.warning)}</div>`;
        }

        // Recommendation - no emoji
        if (q.recommendation) {
            answerHtml += `<div class="recommendation-box"><strong>Tip:</strong> ${q.recommendation}</div>`;
        }

        // Perspectives
        if (q.perspectives && q.perspectives.length > 0) {
            answerHtml += `<div class="perspectives-box">
            <h4>Community Perspectives</h4>
            ${q.perspectives.map(p => `<div class="perspective-quote">"${p}"</div>`).join('')}
        </div>`;
        }

        // Evidence - no emoji
        if (q.evidence && q.evidence.length > 0) {
            answerHtml += `<div class="evidence-tags">
            ${q.evidence.map(e => renderEvidenceTag(e)).join('')}
        </div>`;
        }

        if (q.sources?.length) {
            const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
            const sources = q.sources.filter(source => /^https:\/\//i.test(source.url));
            if (sources.length) answerHtml += `<aside class="faq-sources" aria-label="Further reading"><h4>Further reading</h4><ul>${sources.map(source => `<li><a href="${escape(source.url)}" target="_blank" rel="noopener">${escape(source.label)}</a></li>`).join('')}</ul></aside>`;
        }

        return `
    <div class="faq-item" data-tags="${q.tags ? q.tags.join(' ') : ''}">
        <h3 class="faq-question-heading"><button type="button" class="faq-question" id="question-${id}" aria-expanded="false" aria-controls="answer-${id}" onclick="toggleFaq(this)">
            <span>${q.question}</span>
            <span class="faq-toggle" aria-hidden="true">+</span>
        </button></h3>
        <div class="faq-answer" id="answer-${id}" role="region" aria-labelledby="question-${id}" hidden>${answerHtml}</div>
    </div>`;
    }

    function formatAnswer(answer) {
        const text = stripEmojis(answer).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Reviewed HTML in the local FAQ data already has its own block structure.
        if (/^\s*<(?:p|h[2-6]|ul|ol|div|table|section)\b/i.test(text)) return text;
        // Keep paragraphs and bullet lists distinct; preserve the original wording.
        let html = '', paragraph = [], list = [];
        const flushParagraph = () => { if (paragraph.length) { html += `<p>${paragraph.join('<br>')}</p>`; paragraph = []; } };
        const flushList = () => { if (list.length) { html += `<ul class="faq-list">${list.map(line => `<li>${line}</li>`).join('')}</ul>`; list = []; } };
        text.split('\n').forEach(line => {
            if (/^\s*[•*-]\s+/.test(line)) { flushParagraph(); list.push(line.replace(/^\s*[•*-]\s+/, '')); }
            else if (!line.trim()) { flushParagraph(); flushList(); }
            else { flushList(); paragraph.push(line); }
        });
        flushParagraph(); flushList(); return html;
    }

    function renderConditional(conditional) {
        let html = '<div class="conditional-guidance"><h4>Conditional Guidance</h4>';

        if (conditional.if_then && Array.isArray(conditional.if_then)) {
            conditional.if_then.forEach(item => {
                html += `<div class="conditional-item">
                <span class="if-label">IF</span> ${item.if}
                <span class="then-label">→ THEN</span> ${item.then}
            </div>`;
            });
        } else if (conditional.if && conditional.then) {
            html += `<div class="conditional-item">
            <span class="if-label">IF</span> ${conditional.if}
            <span class="then-label">→ THEN</span> ${conditional.then}
        </div>`;
        }

        html += '</div>';
        return html;
    }

    function renderEvidenceTag(type) {
        const tags = {
            'clinically_proven': { label: 'Clinically Proven' },
            'community_observed': { label: 'Community Observed' },
            'individual_experience': { label: 'Individual Experience' },
            'caution_advised': { label: 'Caution Advised' }
        };

        const tag = tags[type] || { label: type };
        return `<span class="evidence-tag">${tag.label}</span>`;
    }

    function toggleFaq(element) {
        const item = element.closest('.faq-item');
        const open = element.getAttribute('aria-expanded') !== 'true';
        element.setAttribute('aria-expanded', String(open));
        item.classList.toggle('open', open);
        item.querySelector('.faq-answer').hidden = !open;
    }

    function renderKeyPrinciples() {
        if (!faqData.key_principles) return;

        const container = document.getElementById('keyPrinciples');
        let html = `<div class="key-principles">
        <h3>Key Principles from the Community</h3>
        <ul>${faqData.key_principles.map(p => `<li>${p}</li>`).join('')}</ul>
    </div>`;

        container.innerHTML = html;
    }

    function applyFilters() {
        if (!faqData) return;
        const query = document.getElementById('faqSearch').value.trim().toLowerCase();
        let visibleCount = 0;
        document.querySelectorAll('.faq-section[data-category]').forEach(section => {
            let sectionCount = 0;
            const matchesCategory = currentCategory === 'all' || section.dataset.category === currentCategory;
            section.querySelectorAll('.faq-item').forEach(item => {
                const text = `${item.textContent} ${item.dataset.tags || ''}`.toLowerCase();
                const matches = matchesCategory && text.includes(query);
                item.hidden = !matches;
                if (matches) { sectionCount++; visibleCount++; }
            });
            section.hidden = sectionCount === 0;
        });
        document.querySelectorAll('.category-pill').forEach(button => {
            const selected = button.dataset.categoryId === currentCategory;
            button.classList.toggle('active', selected);
            button.setAttribute('aria-pressed', String(selected));
        });
        const title = currentCategory === 'all' ? 'All Topics' : faqData.categories.find(category => category.id === currentCategory)?.name;
        document.getElementById('faqResultsTitle').textContent = title || 'All Topics';
        document.getElementById('faqResultCount').textContent = `${visibleCount} ${visibleCount === 1 ? 'question' : 'questions'}${query ? ' found' : ''}`;
        document.getElementById('faqClear').hidden = !query;
        document.getElementById('faqEmpty').hidden = visibleCount !== 0;
    }

    function initSearch() {
        const search = document.getElementById('faqSearch');
        search.addEventListener('input', applyFilters);
        document.getElementById('faqClear').addEventListener('click', () => { search.value = ''; applyFilters(); search.focus(); });
        document.getElementById('faqReset').addEventListener('click', () => { search.value = ''; currentCategory = 'all'; applyFilters(); search.focus(); });
        document.getElementById('faqRetry').addEventListener('click', loadFAQData);
    }
