/* Progressive navigation; all clinical guidance is rendered by the server. */
(() => {
    'use strict';
    const main = document.querySelector('.care-main');
    if (!main) return;
    const directory = document.querySelector('.care-directory');
    const mobile = window.matchMedia('(max-width: 900px)');
    const setDirectory = () => { if (directory) directory.open = !mobile.matches; };
    setDirectory();
    mobile.addEventListener('change', setDirectory);
    const nav = document.querySelector('.care-section-nav');
    const sections = [...main.querySelectorAll('[data-care-section]')];
    if (nav) {
        for (const section of sections) {
            const heading = section.matches('h2') ? section : section.querySelector('h2');
            if (!heading || !section.id) continue;
            const link = document.createElement('a');
            link.href = '#' + section.id;
            link.textContent = [...heading.childNodes].filter(node => node.nodeType === 3 || !node.hasAttribute?.('aria-hidden')).map(node => node.textContent).join('').trim();
            nav.appendChild(link);
        }
        if (nav.children.length) nav.parentElement.hidden = false;
        nav.addEventListener('click', () => { if (mobile.matches) directory.open = false; });
    }
    main.querySelectorAll('table').forEach(table => {
        let wrapper = table.parentElement;
        if (!wrapper.style.overflowX && !wrapper.classList.contains('care-table-scroll')) {
            wrapper = document.createElement('div');
            table.before(wrapper); wrapper.appendChild(table);
        }
        wrapper.classList.add('care-table-scroll');
        wrapper.tabIndex = 0;
        wrapper.setAttribute('role', 'region');
        const heading = table.closest('[data-care-section]')?.querySelector('h2');
        wrapper.setAttribute('aria-label', (heading?.textContent.trim() || 'Reference') + ' table');
    });
    // Keep the existing printable equipment list expanded during printing only.
    const references = [...main.querySelectorAll('.care-equipment-reference')];
    let previous = [];
    window.addEventListener('beforeprint', () => { previous = references.map(el => el.open); references.forEach(el => el.open = true); });
    window.addEventListener('afterprint', () => { references.forEach((el, i) => el.open = previous[i] ?? el.open); });
    if (!nav || !('IntersectionObserver' in window)) return;
    const active = new Set();
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => { if (entry.isIntersecting) active.add(entry.target.id); else active.delete(entry.target.id); });
        const first = sections.find(section => active.has(section.id));
        if (!first) return;
        for (const link of nav.children) {
            if (link.hash === '#' + first.id) link.setAttribute('aria-current', 'location');
            else link.removeAttribute('aria-current');
        }
    }, { rootMargin: '-140px 0px -55% 0px' });
    sections.forEach(section => observer.observe(section));
    window.addEventListener('pagehide', event => { if (!event.persisted) { observer.disconnect(); mobile.removeEventListener('change', setDirectory); } });
})();
