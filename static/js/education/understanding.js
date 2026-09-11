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
    const signalSteps = [...document.querySelectorAll('[data-signal-step]')];
    const anatomyViews = [['soma','axon','junction','muscle'], ['dendrites','soma'], ['axon'], ['junction','muscle','loss']];
    let lastStage = -1;
    const viewData = [
        {x:.5,y:1.4,z:19,tx:.5,ty:0,kicker:'THE NERVE–MUSCLE CONNECTION',caption:'One lower motor neuron can supply several muscle fibers. Follow the three steps below.'},
        {x:-3.4,y:.65,z:8,tx:-3.5,ty:0,kicker:'01 / THE CELL BODY',caption:'Dendrites are branches that receive input. The cell body keeps the nerve cell functioning.'},
        {x:.15,y:1.1,z:9.5,tx:.15,ty:0,kicker:'02 / ALONG THE AXON',caption:'The axon carries an electrical signal. Myelin is its insulating covering, helping signals travel efficiently.'},
        {x:6.3,y:1,z:11.5,tx:6.3,ty:0,kicker:'03 / THE NERVE–MUSCLE JUNCTION',caption:'At each working connection, acetylcholine crosses a tiny gap and triggers a response in the muscle fiber.'}
    ];
    let view=null, time=.64, last=0, raf=0, inView=false, paused=reduced.matches;
    let currentCamera=0, chosenState=0, tour=false, tourTime=0, cameraTween=null, lossTween=null;
    let motionContext=null, disposed=false;
    const state={loss:0};
    const pose={x:.5,y:1.4,z:19,tx:.5,ty:0};
    function updateMotionLabel() {
        motion.innerHTML=paused?'<span aria-hidden="true">▷</span> Play':'<span aria-hidden="true">Ⅱ</span> Pause';
        motion.setAttribute('aria-label',paused?'Play signal animation':'Pause signal animation');
    }
    function render() {
        if(!view||disposed)return;
        const frame=view.render(time,state.loss,pose);
        if(frame && frame.stage!==lastStage) {
            signalSteps.forEach((step,index)=>{
                if(index===frame.stage)step.setAttribute('aria-current','step');
                else step.removeAttribute('aria-current');
            });
            lastStage=frame.stage;
        }
        labels.forEach(label=>{
            const name=label.dataset.anatomy;
            const point=view.project(name);
            const smallOverview=currentCamera===0&&viewport.clientWidth<600;
            const relevant=anatomyViews[currentCamera].includes(name)||(name==='loss'&&currentCamera===0&&!smallOverview);
            label.hidden=!point.visible || !relevant || (smallOverview&&name==='junction') || (name==='loss'&&state.loss<.95);
            if(!label.hidden) {
                const inset=(label.offsetWidth||0)/2+8;
                label.style.left=Math.max(inset,Math.min(viewport.clientWidth-inset,point.x))+'px';
                label.style.top=Math.max((label.offsetHeight||0)+8,point.y)+'px';
            }
        });
    }
    function updateTourLabel() { tourButton.setAttribute('aria-pressed',String(tour));tourButton.innerHTML=tour?'<span aria-hidden="true">□</span> Stop tour':'<span aria-hidden="true">▷</span> Guided tour'; }
    function stopTour() { tour=false;tourTime=0;updateTourLabel(); }
    function selectCamera(index,animate=true) {
        currentCamera=index;
        if(paused) { time=[6.96,.64,2.8,5.8][index];last=0; }
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
        chosenState=index;time=.64;last=0;
        stateButtons.forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.neuronState)===index)));
        document.getElementById('model-description').innerHTML=index
            ? '<span class="detail-dot" aria-hidden="true"></span><p><strong>Loss of nerve supply.</strong> Some connections are absent in this example. Only fibers with a working connection respond to the illustrated nerve signal. Fibers that have lost their nerve supply are shown smaller to illustrate wasting over time. This is a comparison, not a disease stage or a prediction.</p>'
            : '<span class="detail-dot" aria-hidden="true"></span><p><strong>A working connection.</strong> The blue light represents an electrical signal in the nerve. At the nerve ending, gold dots represent acetylcholine, a chemical messenger. It crosses the tiny gap and triggers muscle activation; the connected fiber then shortens.</p>';
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
        signalSteps.forEach(step=>step.removeAttribute('aria-current'));lastStage=-1;
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
