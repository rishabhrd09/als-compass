/* Abstract 3D signal sphere. Decorative, not a model of the brain or a medical device. */
(() => {
    'use strict';
    const page = document.body.dataset.page;
    if (page !== 'communication_technology_page') return;
    const hero = document.querySelector('.ct-hero');
    if (!hero) return;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const connection = navigator.connection;
    let renderer, scene, camera, group, particles, lines, glowTexture, shell;
    let frame = 0, last = 0, elapsed = 0, visible = false, paused = reduced.matches;
    let disposed = false, started = false, loading = false, observer, resizeObserver;
    let pointerX = 0, pointerY = 0, smoothX = 0, smoothY = 0;
    const wrap = document.createElement('div');
    wrap.className = 'guide-atmosphere';
    wrap.setAttribute('aria-hidden', 'true');
    const canvas = document.createElement('canvas');
    wrap.appendChild(canvas);
    const control = document.createElement('button');
    control.className = 'guide-motion-control';
    control.type = 'button';
    const removers = [];
    function listen(target, event, handler, options) {
        target.addEventListener(event, handler, options);
        removers.push(() => target.removeEventListener(event, handler, options));
    }
    function updateControl() {
        control.textContent = paused ? 'Play motion' : 'Pause motion';
        control.setAttribute('aria-label', (paused ? 'Play' : 'Pause') + ' decorative background motion');
        control.setAttribute('aria-pressed', String(paused));
    }
    function releaseGraphics() {
        if (scene) {
            const geometries = new Set(), materials = new Set();
            scene.traverse(object => {
                if (object.geometry) geometries.add(object.geometry);
                if (object.material) materials.add(object.material);
            });
            geometries.forEach(geometry => geometry.dispose());
            materials.forEach(material => material.dispose());
        }
        if (glowTexture) glowTexture.dispose();
        if (renderer) renderer.dispose();
        renderer = null;
    }
    function dispose() {
        disposed = true;
        cancelAnimationFrame(frame); frame = 0;
        if (observer) observer.disconnect();
        if (resizeObserver) resizeObserver.disconnect();
        removers.splice(0).forEach(remove => remove());
        releaseGraphics(); wrap.remove(); control.remove();
    }
    function render() {
        if (!renderer || disposed) return;
        group.rotation.y = .18 + elapsed * .055 + smoothX * .1;
        group.rotation.x = -.13 + Math.sin(elapsed * .07) * .035 + smoothY * .035;
        group.position.y = Math.sin(elapsed * .12) * .08;
        particles.material.opacity = .72 + Math.sin(elapsed * .25) * .07;
        if (shell) shell.material.uniforms.time.value = elapsed;
        renderer.render(scene, camera);
    }
    function resize() {
        if (!renderer) return;
        const width = wrap.clientWidth, height = wrap.clientHeight;
        if (!width || !height) return;
        camera.aspect = width / height;
        camera.position.z = 8.8 * Math.max(1, .9 / camera.aspect);
        camera.updateProjectionMatrix(); renderer.setSize(width, height, false); render();
    }
    function tick(now) {
        frame = 0;
        if (disposed || !visible || document.hidden || paused || !renderer) { last = 0; return; }
        const dt = last ? Math.min((now - last) / 1000, .05) : 0;
        last = now; elapsed += dt;
        const damping = 1 - Math.exp(-dt * 3);
        smoothX += (pointerX - smoothX) * damping;
        smoothY += (pointerY - smoothY) * damping;
        render(); frame = requestAnimationFrame(tick);
    }
    function sync() {
        if (visible && !document.hidden && !paused && renderer && !disposed) {
            if (!frame) { last = 0; frame = requestAnimationFrame(tick); }
        } else { cancelAnimationFrame(frame); frame = 0; last = 0; }
    }
    function build() {
        if (disposed || started) return;
        const T = window.THREE;
        if (!T) { dispose(); return; }
        started = true;
        try {
            renderer = new T.WebGLRenderer({ canvas, antialias: false, alpha: true, powerPreference: 'low-power' });
            renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
            scene = new T.Scene(); camera = new T.PerspectiveCamera(40, 1, .1, 80);
            camera.position.set(0, 0, 10.5); group = new T.Group(); scene.add(group);
            const points = [], colors = [], segments = [], nodes = [];
            const palette = [new T.Color(0x92d7df), new T.Color(0x87afb9), new T.Color(0xc4b386)];
            // Evenly distributed nodes form a dimensional surface rather than a flat particle cloud.
            const count = 144, goldenAngle = Math.PI * (3 - Math.sqrt(5));
            for (let i = 0; i < count; i++) {
                const y = 1 - 2 * (i + .5) / count;
                const ringRadius = Math.sqrt(1 - y * y), angle = i * goldenAngle;
                const radius = 2.35 + Math.sin(angle * 3) * .045;
                const point = new T.Vector3(Math.cos(angle) * ringRadius, y, Math.sin(angle) * ringRadius).multiplyScalar(radius);
                nodes.push(point); points.push(point.x, point.y, point.z);
                const color = palette[i % palette.length]; colors.push(color.r, color.g, color.b);
            }
            for (let i = 0; i < nodes.length; i++) {
                for (let j = i + 1; j < nodes.length; j++) {
                    if (nodes[i].distanceToSquared(nodes[j]) < .78) {
                        segments.push(...nodes[i].toArray(), ...nodes[j].toArray());
                    }
                }
            }
            // A translucent Fresnel surface gives the signal network a quiet glass-like volume.
            const shellMaterial = new T.ShaderMaterial({
                uniforms: { time: { value: 0 } }, transparent: true, depthWrite: false,
                vertexShader: `varying vec3 vNormal; varying vec3 vView; varying vec3 vPosition;
                    void main() { vec4 p = modelViewMatrix * vec4(position, 1.0);
                        vNormal = normalize(normalMatrix * normal); vView = normalize(-p.xyz);
                        vPosition = position; gl_Position = projectionMatrix * p; }`,
                fragmentShader: `uniform float time; varying vec3 vNormal; varying vec3 vView; varying vec3 vPosition;
                    void main() { float edge = pow(1.0 - abs(dot(normalize(vNormal), normalize(vView))), 2.8);
                        float band = .5 + .5 * sin(vPosition.y * 4.0 + vPosition.x * 2.5 - time * .12);
                        vec3 color = mix(vec3(.12, .33, .42), vec3(.43, .75, .79), band);
                        gl_FragColor = vec4(color, .035 + edge * .28); }`
            });
            shell = new T.Mesh(new T.SphereGeometry(2.19, 48, 32), shellMaterial); group.add(shell);
            for (let orbit = 0; orbit < 3; orbit++) {
                const path = [];
                for (let i = 0; i < 96; i++) {
                    const theta = i / 96 * Math.PI * 2;
                    path.push(new T.Vector3(Math.cos(theta) * 2.62,
                        Math.sin(theta) * 2.62, Math.sin(theta * 3 + orbit) * .14));
                }
                const ribbon = new T.Mesh(
                    new T.TubeGeometry(new T.CatmullRomCurve3(path, true), 160, .008, 4, true),
                    new T.MeshBasicMaterial({ color: palette[orbit], transparent: true, opacity: .42, depthWrite: false })
                );
                ribbon.rotation.set(orbit * .95 + .4, orbit * .8, .35);
                group.add(ribbon);
            }
            const textureCanvas = document.createElement('canvas'); textureCanvas.width = textureCanvas.height = 32;
            const ctx = textureCanvas.getContext('2d');
            const gradient = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
            gradient.addColorStop(0, '#fff'); gradient.addColorStop(.25, '#ffffffdb'); gradient.addColorStop(1, '#ffffff00');
            ctx.fillStyle = gradient; ctx.fillRect(0, 0, 32, 32);
            glowTexture = new T.CanvasTexture(textureCanvas);
            const geometry = new T.BufferGeometry();
            geometry.setAttribute('position', new T.Float32BufferAttribute(points, 3));
            geometry.setAttribute('color', new T.Float32BufferAttribute(colors, 3));
            particles = new T.Points(geometry, new T.PointsMaterial({ size: .12, map: glowTexture, vertexColors: true, transparent: true, opacity: .75, depthWrite: false, blending: T.AdditiveBlending }));
            group.add(particles);
            const lineGeometry = new T.BufferGeometry(); lineGeometry.setAttribute('position', new T.Float32BufferAttribute(segments, 3));
            lines = new T.LineSegments(lineGeometry, new T.LineBasicMaterial({ color: 0x9bc6d7, transparent: true, opacity: .21, depthWrite: false }));
            group.add(lines);
            hero.appendChild(wrap); hero.appendChild(control); updateControl();
            resizeObserver = new ResizeObserver(resize); resizeObserver.observe(hero);
            resize(); sync();
        } catch (error) { dispose(); }
    }
    function load() {
        if (loading || started || disposed || connection?.saveData) return;
        loading = true;
        if (window.THREE) { build(); return; }
        const script = document.createElement('script');
        script.src = '/static/vendor/three-r128.min.js'; script.async = true;
        script.onload = build; script.onerror = dispose; document.head.appendChild(script);
    }
    listen(control, 'click', () => { paused = !paused; updateControl(); sync(); });
    listen(reduced, 'change', () => {
        paused = reduced.matches; pointerX = pointerY = smoothX = smoothY = 0;
        updateControl(); sync(); render();
    });
    listen(hero, 'pointermove', event => {
        if (event.pointerType !== 'mouse' || paused || reduced.matches) return;
        const rect = hero.getBoundingClientRect();
        pointerX = (event.clientX - rect.left) / rect.width - .5;
        pointerY = (event.clientY - rect.top) / rect.height - .5;
    }, { passive: true });
    listen(hero, 'pointerleave', () => { pointerX = pointerY = 0; });
    listen(document, 'visibilitychange', sync);
    listen(canvas, 'webglcontextlost', event => { event.preventDefault(); dispose(); });
    listen(window, 'pagehide', event => { if (event.persisted) { cancelAnimationFrame(frame); frame = 0; last = 0; } else dispose(); });
    listen(window, 'pageshow', event => { if (event.persisted) sync(); });
    observer = new IntersectionObserver(entries => { visible = entries[0].isIntersecting; if (visible) load(); sync(); });
    observer.observe(hero);
})();
