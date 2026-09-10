/* Original conceptual lower motor neuron. Three.js r128; no network assets. */
(() => {
    'use strict';
    const T = window.THREE;
    if (!T) return;
    window.createNeuronView = function createNeuronView(canvas) {
        const renderer = new T.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
        renderer.outputEncoding = T.sRGBEncoding;
        renderer.toneMapping = T.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.3;
        const scene = new T.Scene();
        const camera = new T.PerspectiveCamera(36, 1, .1, 100);
        const target = new T.Vector3();
        scene.add(new T.HemisphereLight(0xd7eef2, 0x18313e, 1.25));
        [[0xe1eff5, 2.2, -5, 6, 7], [0x80bccc, 1.8, 2, -3, 5], [0xf5cfaa, 1.6, 5, 5, -2]].forEach(([color, intensity, x, y, z]) => {
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
        const material = (color, more = {}) => new T.MeshPhysicalMaterial({ color, roughness: .35, metalness: .07, clearcoat: .45, clearcoatRoughness: .25, ...more });
        const tissue = material(0x99b9c2, { emissive: 0x204250, emissiveIntensity: .15 });
        const membrane = material(0xb4d4dc, { transparent: true, opacity: .61, depthWrite: false, roughness: .23, side: T.FrontSide });
        const myelin = material(0xd9e2de, { roughness: .32 });
        const nucleusMaterial = material(0xd2b291, { roughness: .4 });
        const muscleMaterial = material(0x976663, { roughness: .48, emissive: 0x512d2a, emissiveIntensity: .12 });
        const striationMaterial = material(0xb3847d, { roughness: .6 });
        const terminalMaterial = material(0xc0dcdd, { transparent: true, opacity: .9 });
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
        const dendriteCurves=[];
        function branch(start, direction, length, radius, depth) {
            const bend=v((random()-.5)*.5,(random()-.5)*.6,(random()-.5)*.5);
            const end=start.clone().addScaledVector(direction,length);
            const middle=start.clone().lerp(end,.5).add(bend);
            const result=tube([start,middle,end],radius,tissue,somaRoot,.32,12);
            if(depth===2) dendriteCurves.push(result.curve);
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
        const terminals=new T.Group(); model.add(terminals);
        const terminalCurves=[], boutons=[];
        for(let i=0;i<5;i++) {
            const y=(i-2)*.54, z=Math.sin(i*1.4)*.38;
            const points=[v(3.5,.05,0),v(4.03,y*.6,z*.5),v(4.7,y,z),v(4.92,y-.05,z+.05)];
            terminalCurves.push(tube(points,.1,terminalMaterial,terminals,.55,22).curve);
            const bouton=new T.Mesh(new T.SphereGeometry(.18,20,14),terminalMaterial);
            bouton.position.copy(points[3]); bouton.scale.set(1.15,.8,.85); terminals.add(bouton); boutons.push(bouton);
        }
        const muscles=new T.Group(); muscles.position.set(5.5,0,0); model.add(muscles);
        const muscleGeo=new T.CylinderGeometry(.27,.3,4.8,20,12);
        const stripesGeo=new T.TorusGeometry(.285,.012,4,24);
        for(let i=0;i<7;i++) {
            const x=(i%3)*.39, z=Math.floor(i/3)*.37-.33;
            const fiber=new T.Mesh(muscleGeo,muscleMaterial);fiber.position.set(x,(random()-.5)*.25,z); muscles.add(fiber);
            for(let j=0;j<24;j++) { const ring=new T.Mesh(stripesGeo,striationMaterial);ring.rotation.x=Math.PI/2;ring.position.set(x,-2.2+j*.19,z);muscles.add(ring); }
        }
        muscles.rotation.z=-.13;
        // Light particles represent messages; they are intentionally slower than physiology.
        const glowCanvas=document.createElement('canvas');glowCanvas.width=64;glowCanvas.height=64;
        const ctx=glowCanvas.getContext('2d');
        const gradient=ctx.createRadialGradient(32,32,0,32,32,32);
        gradient.addColorStop(0,'rgba(255,245,215,1)');gradient.addColorStop(.16,'rgba(240,218,171,.9)');gradient.addColorStop(.4,'rgba(184,211,219,.22)');gradient.addColorStop(1,'rgba(150,190,210,0)');
        ctx.fillStyle=gradient;ctx.fillRect(0,0,64,64);
        const glow=new T.CanvasTexture(glowCanvas);
        const signals=[];
        for(let i=0;i<12;i++) { const sprite=new T.Sprite(new T.SpriteMaterial({map:glow,transparent:true,depthWrite:false,blending:T.AdditiveBlending}));sprite.scale.setScalar(i<4?.48:.24);model.add(sprite);signals.push(sprite); }
        const dustPositions=new Float32Array(150*3);
        for(let i=0;i<dustPositions.length;i+=3) { dustPositions[i]=(random()-.5)*22;dustPositions[i+1]=(random()-.5)*13;dustPositions[i+2]=-1-random()*6; }
        const dustGeo=new T.BufferGeometry();dustGeo.setAttribute('position',new T.BufferAttribute(dustPositions,3));
        const dust=new T.Points(dustGeo,new T.PointsMaterial({color:0x92b4c1,size:.025,transparent:true,opacity:.25,depthWrite:false}));scene.add(dust);
        const anchors={soma:v(-3.6,1.35,0),axon:v(.2,.8,.3),junction:v(4.9,1.7,.2)};
        const anchorWorld=new T.Vector3();
        let width=1,height=1;
        function resize(w,h) { width=Math.max(w,1);height=Math.max(h,1);camera.aspect=width/height;camera.updateProjectionMatrix();renderer.setSize(width,height,false); }
        function render(time, loss, pose) {
            const aspectExtra=Math.max(1,1.68/camera.aspect);
            camera.position.set(pose.x,pose.y,pose.z*aspectExtra);
            target.set(pose.tx,pose.ty,0);camera.lookAt(target);
            terminalMaterial.opacity=.9-loss*.56;
            terminals.position.x=-loss*.68;
            somaRoot.scale.setScalar(1-loss*.075);
            const pulsePhase=(time*.22)%1;
            const contraction=(1-loss*.85)*Math.pow(Math.max(0,Math.sin((pulsePhase-.82)*Math.PI*9)),6)*.025;
            muscles.scale.set(1-loss*.12+contraction,1-contraction,1-loss*.12+contraction);
            muscleMaterial.emissiveIntensity=.08+contraction*7;
            for(let i=0;i<signals.length;i++) {
                const p=signals[i];
                if(i<4) {
                    const t=(time*.22+i*.26)%1;
                    p.position.copy(axonPath.getPoint(t));
                    p.material.opacity=(i===0?1:.5)*Math.min(1,t*12,(1-t)*12);
                    p.visible=loss<.5 || i===0;
                } else if(i<9) {
                    const t=(time*.22+.16)%1;
                    p.position.copy(terminalCurves[i-4].getPoint(t));p.position.x-=loss*.68;
                    p.visible=loss<.65;p.material.opacity=Math.sin(t*Math.PI)*.85*(1-loss);
                } else {
                    const curve=dendriteCurves[(i-9)*2]; const t=1-(time*.24+i*.3)%1;
                    p.position.copy(curve.getPoint(t)).multiplyScalar(1-loss*.075).add(somaRoot.position);
                    p.material.opacity=Math.sin(t*Math.PI)*.65;p.visible=true;
                }
            }
            renderer.render(scene,camera);
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
