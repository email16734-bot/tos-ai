import { readFile } from "node:fs/promises";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

const files = [
  "public/modules/tr-01/model.glb",
  "public/modules/rp-4/model.glb",
  "public/modules/st-5/model.glb",
  "public/modules/as-12/model.glb",
];

for (const file of files) {
  const data = await readFile(file);
  const buffer = data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength);
  const gltf = await new Promise((resolve, reject) => {
    new GLTFLoader().parse(buffer, "", resolve, reject);
  });
  console.log(file, gltf.scene.children.length);
}
