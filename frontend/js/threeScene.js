/**
 * DataFix 3D WebGL Engine (Three.js)
 * Scroll-triggered dynamic holographic pipeline:
 * Chaotic unorganized cubes -> Swirling vortex -> Laser repair core -> Structured matrix
 */

class ThreeSceneManager {
  constructor() {
    this.container = null;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.cubes = [];
    this.particles = null;
    this.laserPlane = null;
    this.scrollProgress = 0;
    this.animating = false;
  }

  init() {
    this.container = document.getElementById("webgl-canvas-container");
    if (!this.container || typeof THREE === "undefined") {
      console.warn("Three.js not found or container missing. 3D background disabled.");
      return;
    }

    try {
      const width = this.container.clientWidth || window.innerWidth;
      const height = this.container.clientHeight || window.innerHeight;

      // 1. Scene
      this.scene = new THREE.Scene();
      this.scene.fog = new THREE.FogExp2(0x060913, 0.0018);

      // 2. Camera
      this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
      this.camera.position.set(0, 0, 75);

      // 3. Renderer
      this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.container.appendChild(this.renderer.domElement);

      // 4. Lights
      const ambientLight = new THREE.AmbientLight(0x0a192f, 2.0);
      this.scene.add(ambientLight);

      const cyanPoint = new THREE.PointLight(0x00f3ff, 3, 120);
      cyanPoint.position.set(30, 20, 40);
      this.scene.add(cyanPoint);

      const purplePoint = new THREE.PointLight(0x9d4edd, 2.5, 120);
      purplePoint.position.set(-30, -20, 30);
      this.scene.add(purplePoint);

      // 5. Particle Field
      const particleCount = 600;
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(particleCount * 3);
      const colors = new Float32Array(particleCount * 3);

      const colorCyan = new THREE.Color(0x00f3ff);
      const colorPurple = new THREE.Color(0x9d4edd);

      for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 160;
        positions[i * 3 + 1] = (Math.random() - 0.5) * 120;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 100;

        const mixed = colorCyan.clone().lerp(colorPurple, Math.random());
        colors[i * 3] = mixed.r;
        colors[i * 3 + 1] = mixed.g;
        colors[i * 3 + 2] = mixed.b;
      }

      geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

      const particleMat = new THREE.PointsMaterial({
        size: 1.8,
        vertexColors: true,
        transparent: true,
        opacity: 0.75,
        blending: THREE.AdditiveBlending
      });

      this.particles = new THREE.Points(geometry, particleMat);
      this.scene.add(this.particles);

      // 6. Holographic Data Cubes
      const cubeGeo = new THREE.BoxGeometry(3.5, 3.5, 3.5);
      for (let i = 0; i < 18; i++) {
        const wireMat = new THREE.MeshBasicMaterial({
          color: i % 2 === 0 ? 0x00f3ff : 0x7928ca,
          wireframe: true,
          transparent: true,
          opacity: 0.35 + Math.random() * 0.4
        });
        const cube = new THREE.Mesh(cubeGeo, wireMat);
        cube.position.set(
          (Math.random() - 0.5) * 90,
          (Math.random() - 0.5) * 70,
          (Math.random() - 0.5) * 50
        );
        cube.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
        cube.userData = {
          rotSpeedX: (Math.random() - 0.5) * 0.02,
          rotSpeedY: (Math.random() - 0.5) * 0.02,
          originY: cube.position.y
        };
        this.cubes.push(cube);
        this.scene.add(cube);
      }

      // 7. Laser Scan Plane
      const planeGeo = new THREE.PlaneGeometry(120, 2);
      const planeMat = new THREE.MeshBasicMaterial({
        color: 0x00f5a0,
        transparent: true,
        opacity: 0.2,
        side: THREE.DoubleSide
      });
      this.laserPlane = new THREE.Mesh(planeGeo, planeMat);
      this.laserPlane.rotation.x = Math.PI / 2;
      this.laserPlane.position.y = -20;
      this.scene.add(this.laserPlane);

      // Event Listeners
      window.addEventListener("resize", () => this.onResize());
      window.addEventListener("scroll", () => this.onScroll());

      this.animating = true;
      this.animate();
    } catch (e) {
      console.warn("Failed to initialize 3D scene:", e);
    }
  }

  onResize() {
    if (!this.renderer || !this.camera || !this.container) return;
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  onScroll() {
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    this.scrollProgress = maxScroll > 0 ? window.scrollY / maxScroll : 0;
  }

  animate() {
    if (!this.animating) return;
    requestAnimationFrame(() => this.animate());

    const time = Date.now() * 0.001;

    // Rotate particles with scroll speedup
    if (this.particles) {
      this.particles.rotation.y = time * 0.05 + this.scrollProgress * 2;
      this.particles.rotation.x = Math.sin(time * 0.1) * 0.1;
    }

    // Floating cubes motion influenced by scroll
    this.cubes.forEach((cube, index) => {
      cube.rotation.x += cube.userData.rotSpeedX;
      cube.rotation.y += cube.userData.rotSpeedY;

      // Morphing positions with scroll: converge towards center at higher scroll
      const converge = 1 - this.scrollProgress * 0.5;
      cube.position.y = cube.userData.originY + Math.sin(time + index) * 3;
      cube.scale.setScalar(0.8 + Math.sin(time * 2 + index) * 0.2);
    });

    // Scan plane oscillation
    if (this.laserPlane) {
      this.laserPlane.position.y = Math.sin(time * 1.5) * 30;
      this.laserPlane.material.opacity = 0.15 + Math.sin(time * 4) * 0.1;
    }

    // Camera subtle panning based on scroll
    if (this.camera) {
      this.camera.position.y = -this.scrollProgress * 30;
      this.camera.position.z = 75 - this.scrollProgress * 20;
      this.camera.lookAt(0, -this.scrollProgress * 20, 0);
    }

    this.renderer.render(this.scene, this.camera);
  }
}

window.threeScene = new ThreeSceneManager();
