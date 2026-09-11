/* The full review is server-rendered. These controls only change visibility. */
(() => {
    'use strict';
    const page = document.querySelector('.research-page');
    const form = page?.querySelector('.research-controls');
    if (!form) return;
    const search = page.querySelector('#research-search');
    const status = page.querySelector('#research-status');
    const sections = [...page.querySelectorAll('[data-section]')];
    const entries = [...page.querySelectorAll('[data-entry]')];
    const topics = [...page.querySelectorAll('[data-topic]')];
    const resultCount = page.querySelector('#research-result-count');
    const resetButton = page.querySelector('.research-reset');
    const empty = page.querySelector('.research-empty');
    const normalize = text => text.toLocaleLowerCase().replace(/[\u2010-\u2015-]/g, '').replace(/\s+/g, ' ').trim();
    const searchable = new Map(entries.map(entry => [entry, normalize(entry.dataset.search)]));
    let topic = 'approved';

    function render() {
        const words = normalize(search.value).split(' ').filter(Boolean);
        const filtered = words.length > 0 || status.value !== 'all';
        const selected = filtered ? 'all' : topic;
        let visibleCount = 0;
        sections.forEach(section => {
            let sectionCount = 0;
            section.querySelectorAll('[data-entry]').forEach(entry => {
                const visible = (selected === 'all' || section.dataset.section === selected)
                    && (status.value === 'all' || (status.value === 'recruiting'
                        ? entry.dataset.recruiting === 'true' : status.value === entry.dataset.status))
                    && words.every(word => searchable.get(entry).includes(word));
                entry.hidden = !visible;
                if (visible) sectionCount++;
            });
            section.hidden = sectionCount === 0;
            section.querySelector('.research-section-count').textContent = `${sectionCount} ${sectionCount === 1 ? 'entry' : 'entries'}`;
            visibleCount += sectionCount;
        });
        topics.forEach(link => {
            if (link.dataset.topic === selected) link.setAttribute('aria-current', 'true');
            else link.removeAttribute('aria-current');
        });
        const label = selected === 'all' ? 'All topics' : topics.find(link => link.dataset.topic === selected).firstElementChild.textContent;
        resultCount.textContent = `${visibleCount} of ${entries.length} entries · ${label}${filtered ? ' · Filtered' : ''}`;
        resetButton.hidden = !filtered;
        empty.hidden = visibleCount !== 0;
    }

    function clearFilters() {
        search.value = '';
        status.value = 'all';
        topic = 'all';
        history.replaceState(null, '', location.pathname + location.search);
        render();
    }

    function revealHash(shouldFocus = true) {
        let id;
        try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
        const target = document.getElementById(id);
        if (!target || !page.contains(target)) return;
        if (target.matches('[data-entry], [data-section]') || id === 'research-library') {
            topic = id === 'research-library' ? 'all' : (target.dataset.section || target.closest('[data-section]').dataset.section);
            search.value = '';
            status.value = 'all';
            render();
        }
        let parent = target.parentElement;
        while (parent && parent !== page) {
            if (parent.tagName === 'DETAILS') parent.open = true;
            parent = parent.parentElement;
        }
        requestAnimationFrame(() => {
            target.scrollIntoView({ block: 'start', behavior: 'instant' });
            if (shouldFocus && target.hasAttribute('tabindex')) target.focus({ preventScroll: true });
        });
    }

    form.addEventListener('submit', event => event.preventDefault());
    const filterChanged = () => {
        history.replaceState(null, '', location.pathname + location.search);
        render();
    };
    search.addEventListener('input', filterChanged);
    status.addEventListener('change', filterChanged);
    form.addEventListener('reset', event => { event.preventDefault(); clearFilters(); search.focus(); });
    page.querySelector('[data-clear-research]').addEventListener('click', () => { clearFilters(); search.focus(); });
    // Also handle a second click on the current hash after filtering.
    page.addEventListener('click', event => {
        const link = event.target.closest('a[href^="#"]');
        if (link && link.hash === location.hash) {
            event.preventDefault();
            revealHash();
        }
    });
    window.addEventListener('hashchange', () => revealHash());
    window.addEventListener('popstate', () => { if (!location.hash) { clearFilters(); } });

    let openBeforePrint = [];
    window.addEventListener('beforeprint', () => {
        openBeforePrint = [...page.querySelectorAll('details')].map(details => [details, details.open]);
        openBeforePrint.forEach(([details]) => { details.open = true; });
    });
    window.addEventListener('afterprint', () => { openBeforePrint.forEach(([details, open]) => { details.open = open; }); });
    const printButton = page.querySelector('#research-print');
    printButton.hidden = false;
    printButton.addEventListener('click', () => window.print());
    form.hidden = false;
    render();
    revealHash(false);
})();
