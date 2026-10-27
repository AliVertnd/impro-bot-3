import * as THREE from "three";

const journey = document.getElementById("journey");
const canvas = document.getElementById("journey-view");
const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const narrow = window.matchMedia("(max-width: 860px)");
if (!journey || !canvas || reduce || narrow.matches) {
  // Static stack is handled in CSS.
} else {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
  renderer.setClearColor(0x0c0b09, 1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 200);
  function shot(selector) {
    const image = document.querySelector(selector);
    const tex = new THREE.Texture(image);
    tex.colorSpace = THREE.SRGBColorSpace;
    const mat = new THREE.MeshBasicMaterial({ map: tex });
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(16, 9), mat);
    if (!image.complete) {
      image.addEventListener("load", () => {
        tex.needsUpdate = true;
        frame();
      });
    }
    return mesh;
  }

  const hero = shot(".hero-photo");
  const hall = shot(".hall-photo");
  hall.position.set(14, 0, 0);
  hall.rotation.y = -Math.PI / 2;
  scene.add(hero, hall);

  const heroLook = new THREE.Vector3(0, 0, 0);
  const hallLook = hall.position.clone();
  const normal = new THREE.Vector3(0, 0, 1).applyQuaternion(hall.quaternion);
  let distance = 8;
  const end = hall.position.clone().add(normal.multiplyScalar(distance));
  const start = new THREE.Vector3(0, 0, distance);
  const mid = start.clone().lerp(end, 0.45);
  mid.y += 0.7;
  mid.x -= 1.4;

  function coverDistance() {
    const vFov = THREE.MathUtils.degToRad(camera.fov);
    const hFov = 2 * Math.atan(Math.tan(vFov / 2) * camera.aspect);
    const distH = 4.5 / Math.tan(vFov / 2);
    const distW = 8 / Math.tan(hFov / 2);
    return Math.min(distH, distW);
  }

  function resize() {
    const width = journey.clientWidth || window.innerWidth;
    const height = window.innerHeight;
    renderer.setSize(width, height, false);
    camera.aspect = width / Math.max(height, 1);
    camera.updateProjectionMatrix();
    distance = coverDistance();
    start.set(0, 0, distance);
    end.copy(hall.position).add(new THREE.Vector3(0, 0, 1).applyQuaternion(hall.quaternion).multiplyScalar(distance));
    mid.copy(start).lerp(end, 0.45);
    mid.y += 0.4;
    mid.z += distance * 0.35;
  }

  function bezier(a, b, c, t) {
    const ab = a.clone().lerp(b, t);
    const bc = b.clone().lerp(c, t);
    return ab.lerp(bc, t);
  }

  function ease(t) {
    return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  }

  let progress = 0;
  function frame() {
    const t = ease(progress);
    camera.position.copy(bezier(start, mid, end, t));
    camera.lookAt(heroLook.clone().lerp(hallLook, t));
    renderer.render(scene, camera);
  }

  function onScroll() {
    const total = journey.offsetHeight - window.innerHeight;
    const passed = Math.min(Math.max(-journey.getBoundingClientRect().top, 0), Math.max(total, 0));
    progress = total > 0 ? passed / total : 0;
    const forced = new URLSearchParams(location.search).get("frame");
    if (forced !== null && forced !== "") progress = Math.min(Math.max(Number(forced), 0), 1);
    const leave = Math.min(Math.max((progress - 0.08) / 0.32, 0), 1);
    const arrive = Math.min(Math.max((progress - 0.62) / 0.3, 0), 1);
    journey.style.setProperty("--leave", leave.toFixed(3));
    journey.style.setProperty("--arrive", arrive.toFixed(3));
    journey.classList.toggle("is-left", leave > 0.85);
    journey.classList.toggle("is-open", arrive > 0.92);
    frame();
  }

  resize();
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", () => { resize(); onScroll(); });
  const reveal = () => {
    hero.material.map.needsUpdate = true;
    hall.material.map.needsUpdate = true;
    frame();
    journey.classList.add("is-live");
  };
  if (document.querySelector(".hero-photo").complete) reveal();
  else document.querySelector(".hero-photo").addEventListener("load", reveal);
  setTimeout(reveal, 400);
}
