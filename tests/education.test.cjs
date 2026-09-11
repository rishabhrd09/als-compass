const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const lesson = require('../static/js/education/neuron-lesson.js');

function fixture({ reduced = false, modelFails = false } = {}) {
    class Element {
        constructor(id) { this.id=id;this.dataset={};this.attrs={};this.events={};this.style={};this.disabled=true;this.hidden=false;this.clientWidth=900;this.clientHeight=430;this.innerHTML='';this.textContent=''; }
        addEventListener(type,fn) { (this.events[type]??=[]).push(fn); }
        fire(type,event={}) { (this.events[type]||[]).forEach(fn=>fn(event)); }
        setAttribute(key,val) { this.attrs[key]=String(val); }
        getAttribute(key) { return this.attrs[key]; }
        removeAttribute(key) { delete this.attrs[key]; }
        getBoundingClientRect() { return {top:400}; }
        pause() { this.pauseCount=(this.pauseCount||0)+1; }
    }
    const ids=['explorer','neuron-viewport','neuron-canvas','model-status','model-motion','guided-tour','view-kicker','view-caption','model-description','connection-film','scroll-progress'];
    const elements=Object.fromEntries(ids.map(id=>[id,new Element(id)]));
    elements.explorer.dataset.state='loading';
    const cameras=Array.from({length:4},(_,i)=>{const el=new Element();el.dataset.camera=String(i);return el;});
    const states=Array.from({length:2},(_,i)=>{const el=new Element();el.dataset.neuronState=String(i);return el;});
    const labels=['dendrites','soma','axon','junction','muscle','loss'].map(name=>{const el=new Element();el.dataset.anatomy=name;return el;});
    const signalSteps=Array.from({length:3},(_,i)=>{const el=new Element();el.dataset.signalStep=String(i);return el;});
    const controls=[...cameras,...states,elements['model-motion'],elements['guided-tour']];
    elements.explorer.querySelectorAll=()=>controls;
    const doc=new Element('document');doc.hidden=false;doc.documentElement={scrollHeight:2000};
    doc.getElementById=id=>elements[id];doc.querySelectorAll=sel=>({'[data-camera]':cameras,'[data-neuron-state]':states,'[data-anatomy]':labels,'[data-signal-step]':signalSteps,'.als-nav-link':[]}[sel]||[]);
    const media=new Element('media');media.matches=reduced;
    const win=new Element('window');win.matchMedia=()=>media;win.innerHeight=800;win.scrollY=0;
    const model={renders:0,disposeCount:0,render(time,loss,pose){this.renders++;this.time=time;this.loss=loss;this.pose={...pose};return lesson.frameAt(time);},resize(w,h){this.width=w;this.height=h;},project(){return{x:200,y:100,visible:true};},dispose(){this.disposeCount++;}};
    win.createNeuronView=()=>{if(modelFails)throw new Error('No WebGL');return model;};
    let next=0;const frames=new Map();
    const intersections=[],resizes=[];
    class IntersectionObserver {constructor(fn){this.fn=fn;intersections.push(this);}observe(el){this.el=el;}disconnect(){this.disconnected=true;}trigger(visible){this.fn([{isIntersecting:visible}]);}}
    class ResizeObserver {constructor(fn){this.fn=fn;resizes.push(this);}observe(el){this.el=el;}disconnect(){this.disconnected=true;}}
    vm.runInNewContext(fs.readFileSync(path.join(root,'static/js/education/understanding.js'),'utf8'),{
        window:win,document:doc,console:{warn(){}},IntersectionObserver,ResizeObserver,
        requestAnimationFrame:fn=>{frames.set(++next,fn);return next;},cancelAnimationFrame:id=>frames.delete(id),
    });
    const advance=now=>{const pending=[...frames.values()];frames.clear();pending.forEach(fn=>fn(now));};
    return {elements,cameras,states,labels,signalSteps,controls,win,doc,media,model,frames,intersections,resizes,advance};
}

test('initializes only when needed, responds to camera and connection controls',()=>{
    const f=fixture();assert.equal(f.model.renders,0);
    f.intersections[0].trigger(true);assert.equal(f.elements.explorer.dataset.state,'ready');
    assert.ok(f.controls.every(b=>!b.disabled));
    f.cameras[3].fire('click');assert.equal(f.cameras[3].getAttribute('aria-pressed'),'true');
    assert.equal(f.model.pose.tx,6.3);assert.match(f.elements['view-caption'].textContent,/muscle/);
    f.states[1].fire('click');assert.equal(f.model.loss,1);
    assert.match(f.elements['model-description'].innerHTML,/not a disease stage/);
    f.states[0].fire('click');assert.equal(f.model.loss,0);
});

test('pause, offscreen, and hidden-document states stop continuous rendering',()=>{
    const f=fixture();f.intersections[0].trigger(true);f.advance(100);f.advance(132);
    const time=f.model.time;
    f.elements['model-motion'].fire('click');assert.equal(f.frames.size,0);
    f.advance(200);assert.equal(f.model.time,time);
    f.elements['model-motion'].fire('click');assert.equal(f.frames.size,1);
    f.intersections[0].trigger(false);assert.equal(f.frames.size,0);
    f.intersections[0].trigger(true);assert.equal(f.frames.size,1);
    f.doc.hidden=true;f.doc.fire('visibilitychange');assert.equal(f.frames.size,0);
    assert.equal(f.elements['connection-film'].pauseCount,1);
});

test('reduced motion retains a static model and functional viewpoint controls',()=>{
    const f=fixture({reduced:true});f.intersections[0].trigger(true);
    assert.equal(f.elements.explorer.dataset.state,'ready');assert.equal(f.frames.size,0);
    assert.equal(f.elements['guided-tour'].disabled,true);
    f.cameras[2].fire('click');assert.equal(f.model.pose.tx,.15);
    assert.equal(f.cameras[2].getAttribute('aria-pressed'),'true');
    f.states[1].fire('click');assert.equal(f.model.loss,1);
    f.elements['model-motion'].fire('click');assert.equal(f.frames.size,1); // Explicit playback is allowed.
});

test('changing reduced-motion preference stops animation and the tour',()=>{
    const f=fixture();f.intersections[0].trigger(true);f.elements['guided-tour'].fire('click');
    assert.equal(f.elements['guided-tour'].getAttribute('aria-pressed'),'true');
    f.media.matches=true;f.media.fire('change');assert.equal(f.frames.size,0);
    assert.equal(f.elements['guided-tour'].disabled,true);
    assert.equal(f.elements['guided-tour'].getAttribute('aria-pressed'),'false');
});

test('the guided tour advances by elapsed time and returns to overview',()=>{
    const f=fixture();f.intersections[0].trigger(true);f.elements['guided-tour'].fire('click');
    for(let i=0;i<200;i++)f.advance(i*33.333);
    assert.equal(f.cameras[1].getAttribute('aria-pressed'),'true');
    for(let i=200;i<750;i++)f.advance(i*33.333);
    assert.equal(f.elements['guided-tour'].getAttribute('aria-pressed'),'false');
    assert.equal(f.cameras[0].getAttribute('aria-pressed'),'true');
});

test('WebGL failure leaves a useful fallback without a retry loop',()=>{
    const f=fixture({modelFails:true});f.intersections[0].trigger(true);
    assert.equal(f.elements.explorer.dataset.state,'fallback');assert.equal(f.frames.size,0);
    assert.match(f.elements['model-status'].textContent,/Film available/);
    assert.ok(f.controls.every(b=>b.disabled));
    f.intersections[0].trigger(true);assert.equal(f.model.renders,0);
});

test('video playback pauses the model; leaving the video viewport pauses video',()=>{
    const f=fixture();f.intersections[0].trigger(true);f.elements['connection-film'].fire('play');
    assert.equal(f.frames.size,0);f.intersections[1].trigger(false);
    assert.equal(f.elements['connection-film'].pauseCount,1);
});

test('page teardown disposes graphics and observers; bfcache can resume',()=>{
    const f=fixture();f.intersections[0].trigger(true);
    f.win.fire('pagehide',{persisted:true});assert.equal(f.frames.size,0);assert.equal(f.model.disposeCount,0);
    f.win.fire('pageshow',{persisted:true});assert.equal(f.frames.size,1);
    f.win.fire('pagehide',{persisted:false});assert.equal(f.model.disposeCount,1);assert.equal(f.frames.size,0);
    assert.ok(f.intersections.every(o=>o.disconnected));assert.ok(f.resizes.every(o=>o.disconnected));
});

function sceneFixture() {
    const THREE=require(path.join(root,'static/vendor/three-r128.min.js'));
    let scene,camera;
    class Renderer {setPixelRatio(){}setSize(){}render(s,c){scene=s;camera=c;s.updateMatrixWorld(true);c.updateMatrixWorld(true);}dispose(){}}
    const context={window:{THREE:{...THREE,WebGLRenderer:Renderer},NeuronLesson:lesson,devicePixelRatio:2},document:{createElement(){return{width:64,height:64,getContext(){return{createRadialGradient(){return{addColorStop(){}};},fillRect(){}};}};}}};
    vm.runInNewContext(fs.readFileSync(path.join(root,'static/js/education/neuron-model.js'),'utf8'),context);
    const view=context.window.createNeuronView({});
    const pose={x:.5,y:1.4,z:19,tx:.5,ty:0};
    view.resize(1000,430);view.render(0,0,pose);
    return {view,pose,THREE,render(time,loss=0){return view.render(time,loss,pose);},get scene(){return scene;},get camera(){return camera;}};
}

test('the real Three.js scene has finite geometry, valid projected labels, and responsive framing',()=>{
    const {view,pose,scene,camera,THREE}=sceneFixture();
    for(const [width,height] of [[1000,430],[550,360],[335,310]]) {
        view.resize(width,height);
        for(const loss of [0,.5,1])view.render(2,loss,pose);
        scene.traverse(o=>{
            if(o.geometry?.attributes.position)assert.ok(o.geometry.attributes.position.array.every(Number.isFinite));
            assert.ok(o.position.toArray().every(Number.isFinite));
        });
        for(const name of ['soma','axon','junction','muscle']) {
            const anchor=view.project(name);assert.ok(Number.isFinite(anchor.x)&&Number.isFinite(anchor.y));assert.ok(anchor.visible,`${name} should fit ${width}px overview`);
        }
        // Check actual anatomy, rather than only the camera's anchor points.
        scene.traverse(o=>{
            if(!o.isMesh)return;
            const bounds=new THREE.Box3().setFromObject(o);
            for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]) {
                const p=new THREE.Vector3(x,y,z).project(camera);
                assert.ok(Math.abs(p.x)<1&&Math.abs(p.y)<1,`anatomy should fit ${width}px overview`);
            }
        });
        assert.ok(camera.aspect>0);
    }
    view.dispose();
});

test('electrical travel, chemical release and contraction occur in order',()=>{
    const f=sceneFixture();
    const count=prefix=>{let total=0;f.scene.traverse(o=>{if(o.name.startsWith(prefix)&&o.visible)total++;});return total;};
    f.render(2);assert.equal(count('axon-signal'),1);assert.equal(count('terminal-signal'),0);assert.equal(count('chemical-'),0);
    assert.equal(f.scene.getObjectByName('axon-signal').material.depthTest,false,'teaching signal should remain visible through myelin');
    f.render(4.6);assert.equal(count('axon-signal'),0);assert.equal(count('terminal-signal'),5);assert.equal(count('chemical-'),0);
    f.render(5.8);assert.equal(count('terminal-signal'),0);assert.equal(count('chemical-'),15);
    for(let i=0;i<5;i++)assert.equal(f.scene.getObjectByName('fiber-'+i).scale.y,1);
    f.render(6.96);assert.equal(count('chemical-'),0);
    for(let i=0;i<5;i++)assert.ok(f.scene.getObjectByName('fiber-'+i).scale.y<.95);
    f.render(8);assert.equal(count('chemical-'),0);
    for(let i=0;i<5;i++)assert.equal(f.scene.getObjectByName('fiber-'+i).scale.y,1);
    f.view.dispose();
});

test('close-up labels fit each real camera position at desktop and phone sizes',()=>{
    const f=sceneFixture();
    const controller=fixture({reduced:true});controller.intersections[0].trigger(true);
    const names=[['soma','axon','muscle'],['dendrites','soma'],['axon'],['junction','muscle','loss']];
    for(const [width,height] of [[1000,430],[550,360],[335,310]]) {
        f.view.resize(width,height);
        controller.cameras.forEach((button,index)=>{
            button.fire('click');f.view.render(5.8,1,controller.model.pose);
            for(const name of names[index])assert.ok(f.view.project(name).visible,`${name} should fit camera ${index} at ${width}px`);
        });
    }
    f.view.dispose();
});

test('lost contacts cannot activate their muscle fibers, while intact contacts still work',()=>{
    const f=sceneFixture();
    let intactContractions=0;
    for(let time=0;time<8;time+=.08) {
        f.render(time,1);
        for(let i=0;i<5;i++) {
            const fiber=f.scene.getObjectByName('fiber-'+i);
            const lost=i===1||i===3;
            assert.equal(fiber.userData.connected,!lost);
            if(lost) {
                assert.equal(fiber.scale.y,1,'denervated fiber must not follow the nerve signal');
                assert.equal(fiber.scale.x,.74,'illustrative wasting is static once loss transition completes');
                assert.equal(f.scene.getObjectByName('terminal-signal-'+i).visible,false);
                for(let j=0;j<3;j++)assert.equal(f.scene.getObjectByName('chemical-'+i+'-'+j).visible,false);
            } else if(fiber.scale.y<.99)intactContractions++;
        }
    }
    assert.ok(intactContractions>0);
    f.render(5.8,0);
    for(let i=0;i<5;i++)assert.equal(f.scene.getObjectByName('chemical-'+i+'-0').visible,true);
    f.view.dispose();
});

test('static views highlight their teaching step and pause freezes the highlighted sequence',()=>{
    const f=fixture({reduced:true});f.intersections[0].trigger(true);
    const current=()=>f.signalSteps.findIndex(step=>step.getAttribute('aria-current')==='step');
    assert.equal(current(),0);
    f.cameras[3].fire('click');assert.equal(current(),1);
    f.cameras[0].fire('click');assert.equal(current(),2);
    f.advance(900);assert.equal(current(),2);
    f.states[1].fire('click');assert.equal(current(),0);
    f.elements['neuron-canvas'].fire('webglcontextlost',{preventDefault(){}});
    assert.equal(current(),-1);assert.equal(f.elements.explorer.dataset.state,'fallback');
});

test('labels follow the selected anatomy view and stay inside narrow viewports',()=>{
    const f=fixture({reduced:true});f.elements['neuron-viewport'].clientWidth=280;
    f.labels.forEach(label=>{label.offsetWidth=150;label.offsetHeight=28;});
    f.model.project=()=>({x:275,y:10,visible:true});
    f.intersections[0].trigger(true);
    const shown=()=>f.labels.filter(label=>!label.hidden).map(label=>label.dataset.anatomy);
    assert.deepEqual(shown(),['soma','axon','muscle']);
    for(const label of f.labels.filter(label=>!label.hidden)) {
        assert.equal(label.style.left,'197px');assert.equal(label.style.top,'36px');
    }
    f.cameras[1].fire('click');assert.deepEqual(shown(),['dendrites','soma']);
    f.cameras[3].fire('click');assert.deepEqual(shown(),['junction','muscle']);
    f.states[1].fire('click');assert.deepEqual(shown(),['junction','muscle','loss']);
});
