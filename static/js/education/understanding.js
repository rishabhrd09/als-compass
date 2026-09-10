/* Education interactions: optional 3D, bounded animation, no rendering API calls. */
(() => {
    'use strict';
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const explorer = document.getElementById('explorer');
    const viewport = document.getElementById('neuron-viewport');
    const canvas = document.getElementById('neuron-canvas');
    const status = document.getElementById('model-status');
    const motion = document.getElementById('model-motion');
    const tourButton = document.getElementById('guided-tour');
    const cameras = [...document.querySelectorAll('[data-camera]')];
    const stateButtons = [...document.querySelectorAll('[data-neuron-state]')];
    const labels = [...document.querySelectorAll('[data-anatomy]')];
    const viewData = [
        {x:0,y:1.4,z:19,tx:.1,ty:0,kicker:'THE COMPLETE PATHWAY',caption:'A motor neuron connects to muscle fibers through its long axon.'},
        {x:-3.4,y:.65,z:8,tx:-3.5,ty:0,kicker:'01 / THE CELL BODY',caption:'Dendrites receive input. The cell body supports the neuron.'},
        {x:.15,y:1.1,z:9.5,tx:.15,ty:0,kicker:'02 / ALONG THE AXON',caption:'An electrical signal travels along the axon toward the muscle.'},
        {x:5.1,y:1,z:7.8,tx:5,ty:0,kicker:'03 / THE NERVE–MUSCLE JUNCTION',caption:'Chemical messengers help the nerve activate a muscle fiber.'}
    ];
    let view=null, time=1, last=0, raf=0, inView=false, paused=reduced.matches;
    let currentCamera=0, chosenState=0, tour=false, tourTime=0, cameraTween=null, lossTween=null;
    let motionContext=null, disposed=false;
    const state={loss:0};
    const pose={x:0,y:1.4,z:19,tx:.1,ty:0};
    function updateMotionLabel() {
        motion.innerHTML=paused?'<span aria-hidden="true">▷</span> Play':'<span aria-hidden="true">Ⅱ</span> Pause';
        motion.setAttribute('aria-label',paused?'Play signal animation':'Pause signal animation');
    }
    function render() {
        if(!view||disposed)return;
        view.render(time,state.loss,pose);
        labels.forEach(label=>{
            const name=label.dataset.anatomy;
            const point=view.project(name);
            label.style.left=point.x+'px';label.style.top=point.y+'px';
            label.hidden=!point.visible || (currentCamera===1&&name!=='soma') || (currentCamera===2&&name!=='axon') || (currentCamera===3&&name!=='junction');
        });
    }
    function updateTourLabel() { tourButton.setAttribute('aria-pressed',String(tour));tourButton.innerHTML=tour?'<span aria-hidden="true">□</span> Stop tour':'<span aria-hidden="true">▷</span> Guided tour'; }
    function stopTour() { tour=false;tourTime=0;updateTourLabel(); }
    function selectCamera(index,animate=true) {
        currentCamera=index;
        const data=viewData[index];
        cameras.forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.camera)===index)));
        document.getElementById('view-kicker').textContent=data.kicker;
        document.getElementById('view-caption').textContent=data.caption;
        if(cameraTween)cameraTween.kill();
        const destination={x:data.x,y:data.y,z:data.z,tx:data.tx,ty:data.ty};
        if(window.gsap&&!reduced.matches&&animate)cameraTween=gsap.to(pose,{...destination,duration:1.7,ease:'power2.inOut',onUpdate:render});
        else {Object.assign(pose,destination);render();}
    }
    function selectState(index) {
        chosenState=index;
        stateButtons.forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.neuronState)===index)));
        document.getElementById('model-description').innerHTML=index
            ? '<span class="detail-dot" aria-hidden="true"></span><p><strong>Loss of nerve supply.</strong> As motor neurons degenerate, their connections with muscle can be lost. Fewer muscle fibers receive stimulation, contributing to weakness and wasting. This is a simplified comparison, not a disease stage.</p>'
            : '<span class="detail-dot" aria-hidden="true"></span><p><strong>A working connection.</strong> An electrical signal travels along the axon. At its terminals, chemical messengers help activate the muscle.</p>';
        if(lossTween)lossTween.kill();
        if(window.gsap&&!reduced.matches)lossTween=gsap.to(state,{loss:index,duration:1.5,ease:'power2.inOut',onUpdate:render});
        else {state.loss=index;render();}
    }
    function tick(now) {
        raf=0;
        if(!view||!inView||document.hidden||paused||disposed){last=0;return;}
        const dt=last?Math.min((now-last)/1000,.05):0;last=now;time+=dt;
        if(tour) {
            tourTime+=dt;
            const index=Math.min(3,Math.floor(tourTime/6));
            if(index!==currentCamera)selectCamera(index);
            if(tourTime>=24){stopTour();selectCamera(0);}
        }
        render();raf=requestAnimationFrame(tick);
    }
    function syncAnimation() {
        if(!view||disposed)return;
        if(inView&&!document.hidden&&!paused) { if(!raf){last=0;raf=requestAnimationFrame(tick);} }
        else {cancelAnimationFrame(raf);raf=0;last=0;}
        const canTween=inView&&!document.hidden;
        if(cameraTween)canTween?cameraTween.resume():cameraTween.pause();
        if(lossTween)canTween?lossTween.resume():lossTween.pause();
    }
    function fail() {
        if(view){view.dispose();view=null;}
        cancelAnimationFrame(raf);raf=0;stopTour();
        explorer.dataset.state='fallback';status.textContent='Illustration view · Film available below';
        explorer.querySelectorAll('button').forEach(b=>b.disabled=true);
        document.getElementById('view-caption').textContent='Explore the connection through the illustrated film and transcript below.';
    }
    function init() {
        if(view||explorer.dataset.state==='fallback'||disposed)return;
        try {
            if(!window.createNeuronView){fail();return;}
            view=window.createNeuronView(canvas);
            view.resize(viewport.clientWidth,viewport.clientHeight);render();
            explorer.dataset.state='ready';status.textContent='Interactive 3D · Conceptual model';
            explorer.querySelectorAll('button').forEach(b=>b.disabled=false);
            tourButton.disabled=reduced.matches;
            if(reduced.matches)tourButton.title='Choose individual views when reduced motion is enabled';
            updateMotionLabel();syncAnimation();
        } catch(error) { console.warn('The 3D teaching model is unavailable; the illustrated guide remains available.',error);fail(); }
    }
    motion.addEventListener('click',()=>{paused=!paused;if(paused){if(cameraTween)cameraTween.progress(1);if(lossTween)lossTween.progress(1);}updateMotionLabel();syncAnimation();});
    tourButton.addEventListener('click',()=>{if(tour){stopTour();return;}tour=true;tourTime=0;paused=false;updateTourLabel();updateMotionLabel();selectCamera(0);syncAnimation();});
    cameras.forEach(b=>b.addEventListener('click',()=>{stopTour();selectCamera(Number(b.dataset.camera));}));
    stateButtons.forEach(b=>b.addEventListener('click',()=>selectState(Number(b.dataset.neuronState))));
    canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();fail();});
    const resize=new ResizeObserver(()=>{if(view){view.resize(viewport.clientWidth,viewport.clientHeight);render();}});resize.observe(viewport);
    const observer=new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;if(inView)init();syncAnimation();},{rootMargin:'80px'});observer.observe(viewport);
    const film=document.getElementById('connection-film');
    const filmObserver=new IntersectionObserver(entries=>{if(!entries[0].isIntersecting)film.pause();});filmObserver.observe(film);
    film.addEventListener('play',()=>{paused=true;updateMotionLabel();syncAnimation();});
    document.addEventListener('visibilitychange',()=>{if(document.hidden)film.pause();syncAnimation();});
    reduced.addEventListener('change',()=>{
        paused=reduced.matches;stopTour();updateMotionLabel();
        if(view)tourButton.disabled=reduced.matches;
        if(cameraTween){cameraTween.progress(1);cameraTween.kill();}
        if(lossTween){lossTween.progress(1);lossTween.kill();}
        if(motionContext)motionContext.revert();
        syncAnimation();render();
    });
    // Location tracking works independently of optional animation libraries.
    const links=[...document.querySelectorAll('.als-nav-link')];
    const sections=links.map(a=>document.querySelector(a.getAttribute('href')));
    const progress=document.getElementById('scroll-progress');
    let scrollPending=false;
    function updateReading() {
        scrollPending=false;
        const total=document.documentElement.scrollHeight-window.innerHeight;
        progress.style.transform='scaleX('+(total>0?Math.min(1,window.scrollY/total):0)+')';
        let active=0;sections.forEach((s,i)=>{if(s.getBoundingClientRect().top<=180)active=i;});
        links.forEach((a,i)=>{if(i===active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});
    }
    window.addEventListener('scroll',()=>{if(!scrollPending){scrollPending=true;requestAnimationFrame(updateReading);}},{passive:true});updateReading();
    if(window.gsap&&window.ScrollTrigger&&!reduced.matches) {
        gsap.registerPlugin(ScrollTrigger);
        motionContext=gsap.context(()=>{
            gsap.from('.hero-text > *',{y:16,opacity:0,duration:.8,stagger:.1,ease:'power2.out',clearProps:'all'});
            // Animate headings only: educational text remains visible if motion stops.
            gsap.utils.toArray('.section-number').forEach(el=>{
                gsap.from(el,{y:12,duration:.7,ease:'power2.out',clearProps:'all',scrollTrigger:{trigger:el,start:'top 93%',once:true}});
            });
        });
    }
    window.addEventListener('pagehide',event=>{
        if(event.persisted){cancelAnimationFrame(raf);raf=0;return;}
        disposed=true;cancelAnimationFrame(raf);observer.disconnect();filmObserver.disconnect();resize.disconnect();
        if(cameraTween)cameraTween.kill();if(lossTween)lossTween.kill();if(motionContext)motionContext.revert();if(view)view.dispose();
    });
    window.addEventListener('pageshow',event=>{if(event.persisted)syncAnimation();});
})();
