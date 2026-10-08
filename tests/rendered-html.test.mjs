import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the training application shell", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<html lang="ru">/i);
  assert.match(html, /<title>Обучающий модуль тренажерно-обучающей системы<\/title>/i);
  assert.match(html, /Подготовка учебной среды/);
  assert.match(html, /ТРЕНАЖЕРНО-ОБУЧАЮЩАЯ СИСТЕМА/);
  assert.match(html, /aria-label="Сменить тему"/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape/i);
});

test("keeps training features in focused components", async () => {
  const componentsRoot = new URL("../app/components/", import.meta.url);
  const requiredComponents = [
    "AppMark.tsx",
    "Catalog.tsx",
    "Menu.tsx",
    "ModelOverview.tsx",
    "Module.tsx",
    "ModuleCard.tsx",
    "PdfViewer.tsx",
    "ShellHeader.tsx",
    "TextMaterials.tsx",
    "ThemeButton.tsx",
    "VideoMaterials.tsx",
  ];

  const [files, trainingApp, moduleScreen, modelOverview, pdfViewer, styles, packageJson, kirisunModule] = await Promise.all([
    readdir(componentsRoot),
    readFile(new URL("../app/TrainingApp.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/components/Module.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/components/ModelOverview.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/components/PdfViewer.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../public/training-content/kirisun-dp990/module.json", import.meta.url), "utf8"),
  ]);

  for (const component of requiredComponents) {
    assert.ok(files.includes(component), `Missing component: ${component}`);
  }

  assert.match(trainingApp, /from "\.\/components\/Catalog"/);
  assert.match(trainingApp, /from "\.\/components\/Module"/);
  assert.doesNotMatch(trainingApp, /function (Catalog|ModuleCard|ModelOverview|PdfViewer)/);
  assert.match(pdfViewer, /pdfjs-dist/);
  assert.match(pdfViewer, /getDocument\(\{ url: material\.file \}\)/);
  assert.match(moduleScreen, /hotspotsVisible/);
  assert.match(moduleScreen, /Скрыть точки/);
  assert.match(modelOverview, /hotspotsVisible && module\.hotspots\.map/);
  assert.match(modelOverview, /model-loader/);
  assert.doesNotMatch(modelOverview, /poster=\{module\.cover\}/);
  assert.match(styles, /\.pdf-scroll::\-webkit-scrollbar-thumb/);
  assert.match(styles, /--bg:\s*#003735/);
  assert.equal((styles.match(/--accent:\s*#ffb96a/g) ?? []).length, 2);
  assert.match(styles, /\.module-dock[\s\S]*flex-direction:\s*column/);
  assert.doesNotMatch(styles, /\.book-(stage|shell|page|arrow)/);
  assert.match(packageJson, /"pdfjs-dist"/);

  const moduleData = JSON.parse(kirisunModule);
  assert.equal(moduleData.shortName, "Kirisun DP990");
  assert.equal(moduleData.hotspots.length, 10);
  assert.equal(moduleData.texts[0].file, "/training-content/kirisun-dp990/texts/guide.pdf");
});
