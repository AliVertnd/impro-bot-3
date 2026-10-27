import * as THREE from "three";
import { GLTFLoader } from "./vendor/GLTFLoader.js";

const canvas = document.getElementById("case-view");

const films = [
  {
    href: "black-gold.html",
    src: "media/black-gold.jpg",
    title: "Black Gold",
    ru: "Нефтяное поле на закате. Имиджевый фильм, 45 секунд.",
    en: "An oilfield at sunset. A brand film, 45 seconds."
  },
  {
    href: "night-road.html",
    src: "media/night-road.jpg",
    title: "Night Road",
    ru: "Ночная дорога над морем. Рекламный ролик, 30 секунд.",
    en: "A night road above the sea. A commercial, 30 seconds."
  },
  {
    href: "above-the-clouds.html",
    src: "media/above-clouds.jpg",
    title: "Above the Clouds",
    ru: "Дом над облаками. Фильм о месте, 60 секунд.",
    en: "A house above the clouds. A film about a place, 60 seconds."
  }
];

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
renderer.setClearColor(0x0c0b09, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(34, 1, 0.05, 80);
scene.add(new THREE.HemisphereLight(0xf3e6d2, 0x1a120c, 0.85));
const key = new THREE.DirectionalLight(0xffe2b8, 2.4);
key.position.set(2.2, 6.5, 4.2);
scene.add(key);
const rim = new THREE.DirectionalLight(0xc47a3a, 1.1);
rim.position.set(-3.5, 2.4, -2);
scene.add(rim);

const texLoader = new THREE.TextureLoader();
const textures = films.map((film) => {
  const tex = texLoader.load(film.src);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.flipY = false;
  return tex;
});

let plates = [];
let modelRoot = null;
let index = 0;
let flipping = false;
let active = false;
let shown = false;

function findOne(root, part) {
  let found = null;
  root.traverse((obj) => {
    if (!found && obj.name && obj.name.indexOf(part) !== -1) found = obj;
  });
  return found;
}

function paintNamed(root, part, texture, strength) {
  root.traverse((obj) => {
    if (!obj.isMesh || !obj.material) return;
    const list = Array.isArray(obj.material) ? obj.material : [obj.material];
    list.forEach((material, slot) => {
      if (!material.name || material.name.indexOf(part) === -1) return;
      const next = material.clone();
      next.map = texture;
      next.emissive = new THREE.Color(0xffffff);
      next.emissiveMap = texture;
      next.emissiveIntensity = strength;
      next.needsUpdate = true;
      if (Array.isArray(obj.material)) obj.material[slot] = next;
      else obj.material = next;
    });
  });
}

function plateGroup(model, n) {
  const pivot = new THREE.Group();
  model.add(pivot);
  const parts = [];
  model.traverse((obj) => {
    if (!obj.name) return;
    if (obj.name.indexOf("Story plate " + n) === 0 || obj.name.indexOf("Story still " + n) === 0) parts.push(obj);
  });
  const box = new THREE.Box3();
  parts.forEach((part) => box.expandByObject(part));
  const center = box.getCenter(new THREE.Vector3());
  pivot.position.copy(center);
  parts.forEach((part) => pivot.attach(part));
  return pivot;
}

function showFilm(i) {
  index = (i + films.length) % films.length;
  const film = films[index];
  if (modelRoot) {
    paintNamed(modelRoot, "gallery concept", textures[index], 0.85);
    films.forEach((item, n) => paintNamed(modelRoot, "Story still " + (n + 1), textures[n], n === index ? 1 : 0.72));
  }
  const title = document.getElementById("film-title");
  const line = document.getElementById("film-line");
  const open = document.getElementById("film-open");
  const num = document.getElementById("film-index");
  if (title) title.textContent = film.title;
  if (num) num.textContent = "0" + (index + 1);
  if (line) {
    line.dataset.ru = film.ru;
    line.dataset.en = film.en;
    line.textContent = document.documentElement.lang === "en" ? film.en : film.ru;
  }
  if (open) open.href = film.href;
}

function ease(t) {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

function flip(dir) {
  if (!plates.length) return;
  if (reduce) {
    showFilm(index + dir);
    return;
  }
  if (flipping) return;
  flipping = true;
  const plate = plates[index];
  const baseY = plate.position.y;
  const next = (index + dir + films.length) % films.length;
  const start = performance.now();
  const duration = 980;
  const sign = dir > 0 ? -1 : 1;
  let moved = false;
  function step(now) {
    const t = Math.min(1, (now - start) / duration);
    const e = ease(t);
    plate.rotation.x = sign * 1.2 * Math.sin(Math.PI * e);
    plate.position.y = baseY + Math.sin(Math.PI * e) * 0.34;
    if (t > 0.46 && !moved) {
      moved = true;
      showFilm(next);
    }
    if (t < 1) requestAnimationFrame(step);
    else {
      plate.rotation.x = 0;
      plate.position.y = baseY;
      flipping = false;
    }
  }
  requestAnimationFrame(step);
}

function resize() {
  const wrap = canvas.parentElement;
  const width = wrap.clientWidth;
  const height = wrap.clientHeight || Math.round(window.innerHeight * 0.72);
  renderer.setSize(width, height, false);
  camera.aspect = width / Math.max(height, 1);
  camera.updateProjectionMatrix();
}

new GLTFLoader().load("media/archive-case.glb", (gltf) => {
  try {
  const model = gltf.scene;
  modelRoot = model;
  scene.add(model);
  plates = [1, 2, 3].map((n) => plateGroup(model, n));
  showFilm(0);
  resize();
  const box = new THREE.Box3().setFromObject(model);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const distY = (size.y * 0.5) / Math.tan(THREE.MathUtils.degToRad(camera.fov * 0.5));
  const distX = (size.x * 0.5) / Math.tan(THREE.MathUtils.degToRad(camera.fov * 0.5) * camera.aspect);
  const dist = Math.max(distX, distY) * 1.34;
  camera.position.set(center.x, center.y + size.y * 0.08, center.z + dist);
  camera.lookAt(center.x, center.y, center.z);
  canvas.parentElement.classList.add("is-ready");
  maybeIntro();
  } catch (error) {
    console.error(error);
  }
}, undefined, (error) => {
  failNote.textContent = "glb " + (error && error.message ? error.message : "load failed");
});

document.getElementById("flip-next").addEventListener("click", () => flip(1));
document.getElementById("flip-prev").addEventListener("click", () => flip(-1));
canvas.addEventListener("keydown", (event) => {
  if (event.key === "ArrowRight") flip(1);
  if (event.key === "ArrowLeft") flip(-1);
});
canvas.tabIndex = 0;

function maybeIntro() {
  if (active && !shown && !reduce && plates.length) {
    shown = true;
    setTimeout(() => flip(1), 900);
  }
}

const observer = new IntersectionObserver((entries) => {
  active = entries[0].isIntersecting;
  maybeIntro();
}, { threshold: 0.45 });
observer.observe(canvas);

function loop() {
  requestAnimationFrame(loop);
  if (active) renderer.render(scene, camera);
}
loop();
window.addEventListener("resize", resize);
resize();
