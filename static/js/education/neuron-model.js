/* Original conceptual lower motor neuron. Three.js r128; no network assets. */
(() => {
    'use strict';
    const T = window.THREE;
    const lesson = window.NeuronLesson;
    if (!T || !lesson) return;
    window.createNeuronView = function createNeuronView(canvas) {
        const renderer = new T.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
        renderer.outputEncoding = T.sRGBEncoding;
        renderer.toneMapping = T.ACESFilmicToneMapping;
        renderer.toneMappingExposure = .95;
        const scene = new T.Scene();
        const camera = new T.PerspectiveCamera(36, 1, .1, 100);
        const target = new T.Vector3();
        scene.add(new T.HemisphereLight(0xd7eef2, 0x18313e, .65));
        [[0xffffff, 1.15, -5, 6, 7], [0x9ed8e0, .55, 2, -3, 5], [0xffd7bc, .7, 5, 5, -2]].forEach(([color, intensity, x, y, z]) => {
            const light = new T.DirectionalLight(color, intensity);
            light.position.set(x, y, z);
            scene.add(light);
        });
        const model = new T.Group();
        model.rotation.x = .13;
        model.rotation.y = -.12;
        scene.add(model);
        let seed = 3917;
        const random = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
        const v = (x,y,z) => new T.Vector3(x,y,z);
        const material = (color, more = {}) => new T.MeshPhysicalMaterial({ color, roughness: .5, metalness: .02, clearcoat: .2, clearcoatRoughness: .25, ...more });
        const tissue = material(0x3b9eae, { emissive: 0x204250, emissiveIntensity: .15 });
        const membrane = material(0x6fc5cb, { transparent: true, opacity: .78, depthWrite: false, roughness: .23, side: T.FrontSide });
        const myelin = material(0xcfc6a7, { roughness: .32 });
        const nucleusMaterial = material(0xccab71, { roughness: .4 });
        const muscleColor = new T.Color(0xc86f66), lostColor = new T.Color(0x64747c);
        const nerveColor = new T.Color(0x4bb0ba);
        const striationMaterial = material(0xe49a87, { roughness: .6 });
        const somaRoot = new T.Group(); somaRoot.position.x = -3.5; model.add(somaRoot);
        const somaGeometry = new T.SphereGeometry(.86, 48, 32);
        const positions = somaGeometry.attributes.position;
        for (let i=0; i<positions.count; i++) {
            const x=positions.getX(i), y=positions.getY(i), z=positions.getZ(i);
            const bump=1+.055*Math.sin(x*9)*Math.cos(y*7)*Math.sin(z*8)+.035*Math.cos(y*15+x*8);
            positions.setXYZ(i,x*bump,y*bump*.89,z*bump*.8);
        }
        somaGeometry.computeVertexNormals();
        somaRoot.add(new T.Mesh(somaGeometry, membrane));
        const nucleus = new T.Mesh(new T.SphereGeometry(.36, 28, 24), nucleusMaterial);
        nucleus.position.set(-.08,.04,.04); somaRoot.add(nucleus);
        const nucleolus = new T.Mesh(new T.SphereGeometry(.095, 12, 10), tissue);
        nucleolus.position.set(-.12,.1,.35); somaRoot.add(nucleolus);
        const granuleGeo = new T.SphereGeometry(.035, 8, 6);
        for(let i=0;i<42;i++) {
            const particle=new T.Mesh(granuleGeo, i%3 ? tissue : nucleusMaterial);
            const phi=random()*Math.PI*2, theta=Math.acos(random()*2-1), r=.44+random()*.21;
            particle.position.set(r*Math.sin(theta)*Math.cos(phi), r*Math.sin(theta)*Math.sin(phi)*.85, r*Math.cos(theta)*.78);
            particle.scale.set(1,1+random()*1.5,1); somaRoot.add(particle);
        }
        function tube(points, radius, mat, parent=model, taper=.3, segments=22) {
            const curve=new T.CatmullRomCurve3(points);
            const sides=8;
            const geo=new T.TubeGeometry(curve,segments,radius,sides,false);
            const pos=geo.attributes.position;
            for(let i=0;i<=segments;i++) {
                const center=curve.getPointAt(i/segments);
                const s=1-(1-taper)*Math.pow(i/segments,.8);
                for(let j=0;j<=sides;j++) {
                    const k=i*(sides+1)+j;
                    pos.setXYZ(k,center.x+(pos.getX(k)-center.x)*s,center.y+(pos.getY(k)-center.y)*s,center.z+(pos.getZ(k)-center.z)*s);
                }
            }
            geo.computeVertexNormals();
            const mesh=new T.Mesh(geo,mat); parent.add(mesh);
            return {mesh,curve};
        }
        function branch(start, direction, length, radius, depth) {
            const bend=v((random()-.5)*.5,(random()-.5)*.6,(random()-.5)*.5);
            const end=start.clone().addScaledVector(direction,length);
            const middle=start.clone().lerp(end,.5).add(bend);
            const result=tube([start,middle,end],radius,tissue,somaRoot,.32,12);
            if(depth>0) {
                for(let k=0;k<2;k++) {
                    const next=direction.clone().add(v((random()-.5)*1.0,(random()-.5)*1.0,(random()-.5)*.85)).normalize();
                    branch(end,next,length*(.56+random()*.15),radius*.49,depth-1);
                }
            }
        }
        for(let i=0;i<9;i++) {
            const angle=.55+(Math.PI*2-1.1)*i/8;
            const direction=v(Math.cos(angle),Math.sin(angle),(random()-.5)*.8).normalize();
            const start=direction.clone().multiplyScalar(.6);
            branch(start,direction,1.3+random()*.65,.14,2);
        }
        const axonPath=new T.CatmullRomCurve3([v(-2.85,0,0),v(-1.6,-.22,.18),v(.2,-.05,.32),v(2,.25,.08),v(3.55,.05,0)]);
        const axon=tube(axonPath.points,.105,tissue,model,.8,60);
        for(let i=0;i<7;i++) {
            const start=.1+i*.12, end=start+.092;
            const pts=Array.from({length:8},(_,j)=>axonPath.getPoint(start+(end-start)*j/7));
            const sheath=tube(pts,.23,myelin,model,.94,14);
            // Rounded ends avoid the hard-cut pipes of the former illustration.
            const capGeo=new T.SphereGeometry(.219,16,12);
            [0,7].forEach(j=>{ const cap=new T.Mesh(capGeo,myelin);cap.position.copy(pts[j]);cap.scale.set(1,.98,.98);model.add(cap); });
            sheath.mesh.userData.part='myelin';
        }
        const terminals=new T.Group(); terminals.name='nerve-terminals'; model.add(terminals);
        const muscles=new T.Group(); muscles.name='muscle-fibers'; model.add(muscles);
        const contacts=[];
        // Short, separated fiber segments make each individual connection visible.
        // Junction gaps are enlarged for teaching; neither scale nor counts are anatomical.
        const muscleGeo=new T.CylinderGeometry(.21,.21,2.65,24,10);
        const stripesGeo=new T.TorusGeometry(.214,.009,4,24);
        const receptorGeo=new T.TorusGeometry(.085,.015,6,20);
        const receptorMaterial=material(0xd9c8a7,{roughness:.65});
        const chemicalGeo=new T.SphereGeometry(.045,10,8);
        const chemicalMaterial=new T.MeshBasicMaterial({color:0xffce76,toneMapped:false});
        const glowCanvas=document.createElement('canvas');glowCanvas.width=64;glowCanvas.height=64;
        const ctx=glowCanvas.getContext('2d');
        const gradient=ctx.createRadialGradient(32,32,0,32,32,32);
        gradient.addColorStop(0,'rgba(189,240,255,1)');gradient.addColorStop(.2,'rgba(105,205,255,.95)');gradient.addColorStop(.6,'rgba(60,168,235,.18)');gradient.addColorStop(1,'rgba(60,168,235,0)');
        ctx.fillStyle=gradient;ctx.fillRect(0,0,64,64);
        const glow=new T.CanvasTexture(glowCanvas);
        function signal(parent, name) {
            // A teaching overlay keeps the signal visible through its insulating sheath.
            const sprite=new T.Sprite(new T.SpriteMaterial({map:glow,transparent:true,depthWrite:false,depthTest:false,blending:T.AdditiveBlending,toneMapped:false}));
            sprite.name=name;sprite.renderOrder=3;sprite.scale.setScalar(.46);parent.add(sprite);return sprite;
        }
        const axonSignal=signal(model,'axon-signal');
        for(let i=0;i<lesson.fiberCount;i++) {
            const y=(i-2)*.96;
            const fiber=new T.Group();fiber.name='fiber-'+i;fiber.position.set(7.1,y,0);fiber.rotation.z=-Math.PI/2;
            const fiberMaterial=material(muscleColor.clone(),{roughness:.6,emissive:0x7b3e29,emissiveIntensity:.05});
            fiber.add(new T.Mesh(muscleGeo,fiberMaterial));
            for(let j=0;j<18;j++) {
                const ring=new T.Mesh(stripesGeo,striationMaterial);ring.rotation.x=Math.PI/2;ring.position.y=-1.2+j*.14;fiber.add(ring);
            }
            muscles.add(fiber);
            const points=[v(3.55,.05,0),v(4.35,y*.7+.25,.15),v(5.62,y+.65,.05),v(6.12,y+.45,0)];
            const terminalMaterial=material(nerveColor.clone(),{transparent:true,opacity:1});
            const branch=tube(points,.085,terminalMaterial,terminals,.55,28);
            const restPositions=branch.mesh.geometry.attributes.position.array.slice();
            const bouton=new T.Mesh(new T.SphereGeometry(.12,20,14),terminalMaterial);
            bouton.position.copy(points[3]);bouton.scale.set(1.15,.85,1);terminals.add(bouton);
            const receptor=new T.Mesh(receptorGeo,receptorMaterial);receptor.rotation.x=Math.PI/2;receptor.position.set(6.12,y+.214,0);muscles.add(receptor);
            const electrical=signal(terminals,'terminal-signal-'+i);
            const chemicals=Array.from({length:3},(_,j)=>{
                const particle=new T.Mesh(chemicalGeo,chemicalMaterial);particle.name='chemical-'+i+'-'+j;model.add(particle);return particle;
            });
            contacts.push({fiber,fiberMaterial,branch,restPositions,bouton,terminalMaterial,electrical,chemicals,receptor,y,lastWithdrawal:-1});
        }
        const dustPositions=new Float32Array(150*3);
        for(let i=0;i<dustPositions.length;i+=3) { dustPositions[i]=(random()-.5)*22;dustPositions[i+1]=(random()-.5)*13;dustPositions[i+2]=-1-random()*6; }
        const dustGeo=new T.BufferGeometry();dustGeo.setAttribute('position',new T.BufferAttribute(dustPositions,3));
        const dust=new T.Points(dustGeo,new T.PointsMaterial({color:0x92b4c1,size:.025,transparent:true,opacity:.25,depthWrite:false}));scene.add(dust);
        const anchors={dendrites:v(-5.3,1.8,0),soma:v(-3.6,1.15,0),axon:v(.2,.8,.3),junction:v(5.7,2.7,.2),muscle:v(8.0,-2.45,.2),loss:v(5.45,-.5,.2)};
        const anchorWorld=new T.Vector3();
        let width=1,height=1;
        function resize(w,h) { width=Math.max(w,1);height=Math.max(h,1);camera.aspect=width/height;camera.updateProjectionMatrix();renderer.setSize(width,height,false); }
        function render(time, loss, pose) {
            const aspectExtra=Math.max(1,1.68/camera.aspect);
            camera.position.set(pose.x,pose.y,pose.z*aspectExtra);
            target.set(pose.tx,pose.ty,0);camera.lookAt(target);
            const frame=lesson.frameAt(time);
            axonSignal.position.copy(axonPath.getPoint(frame.axonProgress));
            axonSignal.visible=frame.axonActive;
            contacts.forEach((contact,i)=>{
                const strength=lesson.connectionStrength(i,loss);
                const withdrawn=1-strength;
                const connected=strength>1e-6;
                const c=contact;
                // Retract only the ending, keeping the branch attached to its axon.
                if(c.lastWithdrawal!==withdrawn) {
                    const positions=c.branch.mesh.geometry.attributes.position;
                    for(let k=0;k<positions.count;k++) {
                        const along=Math.floor(k/9)/28;
                        const weight=along*along*(3-2*along);
                        positions.setXYZ(k,c.restPositions[k*3]-withdrawn*.78*weight,c.restPositions[k*3+1]+withdrawn*.22*weight,c.restPositions[k*3+2]);
                    }
                    positions.needsUpdate=true;c.branch.mesh.geometry.computeVertexNormals();
                    c.branch.mesh.geometry.computeBoundingSphere();
                    c.bouton.position.copy(c.branch.curve.getPoint(1));
                    c.bouton.position.x-=withdrawn*.78;c.bouton.position.y+=withdrawn*.22;
                    c.terminalMaterial.color.copy(nerveColor).lerp(lostColor,withdrawn);
                    c.terminalMaterial.opacity=1-withdrawn*.55;
                    c.fiberMaterial.color.copy(muscleColor).lerp(lostColor,withdrawn*.85);
                    c.lastWithdrawal=withdrawn;
                }
                c.electrical.position.copy(c.branch.curve.getPoint(frame.terminalProgress));
                const t=frame.terminalProgress, weight=t*t*(3-2*t);
                c.electrical.position.x-=withdrawn*.78*weight;c.electrical.position.y+=withdrawn*.22*weight;
                c.electrical.material.opacity=strength;
                c.electrical.visible=connected&&frame.terminalActive;
                c.chemicals.forEach((particle,j)=>{
                    particle.visible=connected&&frame.chemicalActive;
                    // Gold dots start at the nerve terminal, then cross the enlarged gap.
                    const t=Math.max(0,Math.min(1,frame.chemicalProgress*1.2-j*.08));
                    particle.position.set(6.12+(j-1)*.065,c.y+.34-t*.126,0);
                    particle.scale.setScalar(strength);
                });
                const shortening=frame.contraction*.065*strength;
                const thickness=(1-withdrawn*.26)/Math.sqrt(1-shortening);
                c.fiber.scale.set(thickness,1-shortening,thickness);
                c.receptor.position.y=c.y+.214*thickness;
                c.fiberMaterial.emissiveIntensity=.05+frame.contraction*.2*strength;
                c.fiber.userData.connected=connected;
            });
            renderer.render(scene,camera);
            return frame;
        }
        function project(name) {
            model.updateMatrixWorld();
            anchorWorld.copy(anchors[name]);model.localToWorld(anchorWorld);anchorWorld.project(camera);
            return {x:(anchorWorld.x*.5+.5)*width,y:(-.5*anchorWorld.y+.5)*height,visible:Math.abs(anchorWorld.x)<.88&&Math.abs(anchorWorld.y)<.8&&anchorWorld.z<1};
        }
        function dispose() { const geos=new Set(),mats=new Set();scene.traverse(o=>{if(o.geometry)geos.add(o.geometry);if(o.material)mats.add(o.material);});geos.forEach(g=>g.dispose());mats.forEach(m=>m.dispose());glow.dispose();renderer.dispose(); }
        return {resize,render,project,dispose};
    };
})();
