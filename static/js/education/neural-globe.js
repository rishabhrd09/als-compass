/* Retains the original 60-node globe, palette, connections, and gentle rotation. */
(() => {
    'use strict';
    const T=window.THREE, container=document.getElementById('three-container'), canvas=document.getElementById('three-cvs'), button=document.getElementById('hero-motion');
    if(!T||!container||!canvas)return;
    let renderer;
    try { renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'low-power'}); } catch { return; }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.75));
    const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
    const scene=new T.Scene(), camera=new T.PerspectiveCamera(55,1,.1,1000), group=new T.Group();
    camera.position.z=120;scene.add(group);
    const nodes=[],palette=[0x2dd4bf,0x2dd4bf,0xa78bfa,0xfbbf24];
    const dotGeometry=new T.SphereGeometry(1,8,8);
    for(let i=0;i<60;i++) {
        const phi=Math.acos(1-2*i/60),theta=Math.PI*(1+Math.sqrt(5))*i;
        const pos=new T.Vector3(46*Math.sin(phi)*Math.cos(theta),46*Math.sin(phi)*Math.sin(theta),46*Math.cos(phi));
        const dot=new T.Mesh(dotGeometry,new T.MeshBasicMaterial({color:palette[i%4],transparent:true,opacity:.55+(i%7)*.045}));
        dot.scale.setScalar(.6+(i%9)*.1);dot.position.copy(pos);group.add(dot);nodes.push(pos);
    }
    const edges=[];
    for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++) {
        const d=nodes[i].distanceTo(nodes[j]);
        if(d<38){const line=new T.Line(new T.BufferGeometry().setFromPoints([nodes[i],nodes[j]]),new T.LineBasicMaterial({color:0x2dd4bf,transparent:true,opacity:(1-d/38)*.22}));group.add(line);edges.push([i,j]);}
    }
    const pulse=new T.Mesh(new T.SphereGeometry(1.4,8,8),new T.MeshBasicMaterial({color:0xfbbf24,transparent:true,opacity:.8}));group.add(pulse);
    let raf=0,last=0,time=0,edge=0,phase=0,visible=true,paused=reduced.matches,disposed=false;
    function render(){pulse.position.lerpVectors(nodes[edges[edge][0]],nodes[edges[edge][1]],phase);renderer.render(scene,camera);}
    function resize(){const w=container.clientWidth,h=container.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.position.z=120*Math.max(1,.85/camera.aspect);camera.updateProjectionMatrix();renderer.setSize(w,h,false);render();}
    function tick(now){raf=0;if(disposed||paused||document.hidden||!visible){last=0;return;}const dt=last?Math.min((now-last)/1000,.05):0;last=now;time+=dt;group.rotation.y+=dt*.108;group.rotation.x+=dt*.036;phase+=dt*1.1;if(phase>=1){phase=0;edge=(edge+7)%edges.length;}pulse.material.opacity=.6+.3*Math.sin(time*7.2);render();raf=requestAnimationFrame(tick);}
    function sync(){if(!paused&&!document.hidden&&visible&&!disposed){if(!raf){last=0;raf=requestAnimationFrame(tick);}}else{cancelAnimationFrame(raf);raf=0;last=0;}}
    function label(){button.textContent=paused?'Play motion':'Pause motion';button.setAttribute('aria-label',(paused?'Play':'Pause')+' neural globe animation');}
    button.hidden=false;button.addEventListener('click',()=>{paused=!paused;label();sync();});
    reduced.addEventListener('change',()=>{paused=reduced.matches;label();sync();render();});
    const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();});observer.observe(container);
    const sizeObserver=new ResizeObserver(resize);sizeObserver.observe(container);
    document.addEventListener('visibilitychange',sync);
    canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();disposed=true;cancelAnimationFrame(raf);button.hidden=true;});
    window.addEventListener('pagehide',event=>{cancelAnimationFrame(raf);raf=0;if(event.persisted)return;disposed=true;observer.disconnect();sizeObserver.disconnect();const geometries=new Set(),materials=new Set();scene.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material)materials.add(o.material);});geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());renderer.dispose();});
    window.addEventListener('pageshow',event=>{if(event.persisted)sync();});
    label();resize();sync();
})();
