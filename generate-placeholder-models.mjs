import { writeFile } from "node:fs/promises";
import * as THREE from "three";
import { GLTFExporter } from "three/examples/jsm/exporters/GLTFExporter.js";

globalThis.FileReader = class FileReader {
  result = null;
  onloadend = null;
  readAsArrayBuffer(blob) {
    blob.arrayBuffer().then((value) => {
      this.result = value;
      this.onloadend?.({ target: this });
    });
  }
  readAsDataURL(blob) {
    blob.arrayBuffer().then((value) => {
      const base64 = Buffer.from(value).toString("base64");
      this.result = `data:${blob.type};base64,${base64}`;
      this.onloadend?.({ target: this });
    });
  }
};

const olive = new THREE.MeshStandardMaterial({ color: 0x4c5440, roughness: 0.72, metalness: 0.12 });
const graphite = new THREE.MeshStandardMaterial({ color: 0x202523, roughness: 0.62, metalness: 0.24 });
const black = new THREE.MeshStandardMaterial({ color: 0x090b0b, roughness: 0.45, metalness: 0.08 });
const glass = new THREE.MeshStandardMaterial({ color: 0x182727, roughness: 0.18, metalness: 0.05, emissive: 0x0b1715 });
const amber = new THREE.MeshStandardMaterial({ color: 0xe4a83d, roughness: 0.35, emissive: 0x5a2800 });

function mesh(geometry, material, position, rotation = [0, 0, 0], name = "part") {
  const item = new THREE.Mesh(geometry, material);
  item.position.set(...position);
  item.rotation.set(...rotation);
  item.name = name;
  item.castShadow = true;
  item.receiveShadow = true;
  return item;
}

function box(size, material, position, name, radius = 0) {
  void radius;
  return mesh(new THREE.BoxGeometry(...size), material, position, [0, 0, 0], name);
}

function makeRadio() {
  const group = new THREE.Group();
  group.name = "TR-01 placeholder";
  group.add(box([0.72, 1.45, 0.36], olive, [0, 0, 0], "body"));
  group.add(box([0.5, 0.34, 0.035], glass, [0, 0.26, 0.198], "display"));
  group.add(box([0.58, 0.38, 0.39], graphite, [0, -0.66, 0], "battery"));
  group.add(mesh(new THREE.CylinderGeometry(0.055, 0.07, 1.0, 18), black, [0.2, 1.18, 0], [0, 0, 0], "antenna"));
  group.add(mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.14, 18), graphite, [-0.18, 0.8, 0], [0, 0, 0], "control"));
  for (let row = 0; row < 3; row += 1) {
    for (let column = 0; column < 3; column += 1) {
      group.add(mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.025, 12), black, [-0.17 + column * 0.17, -0.05 - row * 0.16, 0.205], [Math.PI / 2, 0, 0], `key-${row}-${column}`));
    }
  }
  return group;
}

function makeRepeater() {
  const group = new THREE.Group();
  group.name = "RP-4 placeholder";
  group.add(box([1.85, 1.05, 0.82], olive, [0, 0, 0], "case"));
  group.add(box([1.62, 0.78, 0.04], graphite, [0, 0, 0.43], "front-panel"));
  for (let column = 0; column < 4; column += 1) {
    group.add(mesh(new THREE.CylinderGeometry(0.105, 0.105, 0.08, 18), black, [-0.6 + column * 0.4, 0.18, 0.49], [Math.PI / 2, 0, 0], `connector-${column}`));
  }
  for (let row = 0; row < 6; row += 1) {
    group.add(box([0.65, 0.045, 0.045], black, [0.25, -0.22 - row * 0.075, 0.47], `vent-${row}`));
  }
  group.add(mesh(new THREE.SphereGeometry(0.055, 14, 10), amber, [-0.65, -0.28, 0.48], [0, 0, 0], "status-light"));
  return group;
}

function makeSatellite() {
  const group = new THREE.Group();
  group.name = "ST-5 placeholder";
  group.add(box([1.55, 0.55, 1.05], olive, [0, -0.55, 0], "transport-case"));
  group.add(box([0.28, 0.58, 0.28], graphite, [0, -0.05, 0], "mast"));
  group.add(mesh(new THREE.CylinderGeometry(0.82, 0.82, 0.08, 40), graphite, [0, 0.55, 0], [Math.PI / 2.9, 0, 0], "reflector"));
  group.add(mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.95, 16), black, [0.32, 0.43, 0.34], [0.85, 0, -0.4], "feed-arm"));
  group.add(mesh(new THREE.CylinderGeometry(0.09, 0.12, 0.28, 18), olive, [0.61, 0.72, 0.62], [0.85, 0, -0.4], "feed"));
  return group;
}

function makeConsole() {
  const group = new THREE.Group();
  group.name = "AS-12 placeholder";
  group.add(box([1.85, 0.55, 1.1], olive, [0, -0.45, 0.12], "lower-case"));
  group.add(box([1.75, 1.05, 0.25], graphite, [0, 0.42, -0.35], "display-lid"));
  group.add(box([0.69, 0.54, 0.035], glass, [-0.42, 0.46, -0.205], "screen-left"));
  group.add(box([0.69, 0.54, 0.035], glass, [0.42, 0.46, -0.205], "screen-right"));
  group.add(box([1.62, 0.08, 0.78], graphite, [0, -0.12, 0.22], "control-panel"));
  for (let column = 0; column < 7; column += 1) {
    group.add(mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.035, 12), black, [-0.56 + column * 0.19, -0.06, 0.58], [Math.PI / 2, 0, 0], `control-${column}`));
  }
  return group;
}

async function exportGlb(object, path) {
  const scene = new THREE.Scene();
  scene.add(object);
  const exporter = new GLTFExporter();
  const result = await exporter.parseAsync(scene, { binary: true, onlyVisible: true });
  await writeFile(path, Buffer.from(result));
}

await exportGlb(makeRadio(), "public/modules/tr-01/model.glb");
await exportGlb(makeRepeater(), "public/modules/rp-4/model.glb");
await exportGlb(makeSatellite(), "public/modules/st-5/model.glb");
await exportGlb(makeConsole(), "public/modules/as-12/model.glb");
