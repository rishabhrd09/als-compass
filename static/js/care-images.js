/* Keep real image links usable without JavaScript; enhance with a native dialog. */
(() => {
    'use strict';
    const links = [...document.querySelectorAll('a[data-care-image]')];
    const dialog = document.getElementById('careImageViewer');
    if (!links.length || !dialog || typeof dialog.showModal !== 'function') return;
    const byId = id => document.getElementById(id);
    const image = byId('careImageFull'), stage = byId('careImageStage');
    const zoom = byId('careImageZoom'), error = byId('careImageError');
    let current = 0, opener, previousOverflow = '', zoomed = false;
    function setZoom(active) {
        zoomed = active;
        stage.classList.toggle('is-zoomed', active);
        zoom.setAttribute('aria-pressed', String(active));
        zoom.textContent = active ? 'Fit image' : 'Zoom in';
        stage.scrollTop = 0; stage.scrollLeft = 0;
    }
    function show(index) {
        current = (index + links.length) % links.length;
        const link = links[current];
        setZoom(false); error.hidden = true; image.hidden = false; zoom.disabled = false;
        image.alt = link.dataset.caption || link.querySelector('img')?.alt || 'Equipment photograph';
        byId('careImageTitle').textContent = image.alt;
        byId('careImagePosition').textContent = 'Image ' + (current + 1) + ' of ' + links.length;
        byId('careImageCredit').textContent = link.dataset.credit || 'Reference photograph';
        byId('careImageOriginal').href = link.href;
        image.src = link.href;
        byId('careImagePrevious').disabled = links.length < 2;
        byId('careImageNext').disabled = links.length < 2;
    }
    links.forEach((link, index) => link.addEventListener('click', event => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button > 0) return;
        event.preventDefault(); opener = link;
        show(index); previousOverflow = document.body.style.overflow;
        dialog.showModal(); document.body.style.overflow = 'hidden';
    }));
    image.addEventListener('error', () => { image.hidden = true; error.hidden = false; zoom.disabled = true; });
    image.addEventListener('load', () => { error.hidden = true; image.hidden = false; zoom.disabled = false; });
    zoom.addEventListener('click', () => setZoom(!zoomed));
    byId('careImageClose').addEventListener('click', () => dialog.close());
    byId('careImagePrevious').addEventListener('click', () => show(current - 1));
    byId('careImageNext').addEventListener('click', () => show(current + 1));
    dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener('keydown', event => {
        if (event.key === 'ArrowLeft' && !zoomed) { event.preventDefault(); show(current - 1); }
        if (event.key === 'ArrowRight' && !zoomed) { event.preventDefault(); show(current + 1); }
    });
    dialog.addEventListener('close', () => {
        document.body.style.overflow = previousOverflow;
        setZoom(false); image.removeAttribute('src'); opener?.focus({ preventScroll: true });
    });
})();
