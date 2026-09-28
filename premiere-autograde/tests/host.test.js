// Teste jsx/host.jsx contre une imitation du modèle objet de Premiere Pro.
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const TICKS_PER_SECOND = 254016000000;
const source = fs.readFileSync(path.join(__dirname, "..", "jsx", "host.jsx"), "utf8");

function collection(items) {
  const c = items.slice();
  c.numItems = items.length;
  c.numTracks = items.length;
  return c;
}

function time(seconds) {
  return { ticks: String(Math.round(seconds * TICKS_PER_SECOND)), seconds };
}

function makeProperty(displayName, value) {
  return {
    displayName,
    value,
    setValue(v) { this.value = v; },
    getValue() { return this.value; },
    isTimeVarying() { return false; }
  };
}

// Propriétés de Lumetri telles qu'un Premiere en français pourrait les nommer.
function frenchLumetri() {
  const names = ["Correction de base", "Température", "Teinte", "Saturation", "Exposition", "Contraste",
    "Tons clairs", "Tons foncés", "Blancs", "Noirs", "Créatif", "Vibrance", "Saturation", "Teinte des tons foncés"];
  return { matchName: "AE.ADBE Lumetri", displayName: "Couleur Lumetri", properties: collection(names.map((n) => makeProperty(n, n === "Saturation" ? 100 : 0))) };
}

function makeWorld({ selection = [], lumetriOnFirst = false } = {}) {
  const clipA = { name: "A001.mov", nodeId: "a", start: time(0), end: time(4), components: collection([{ matchName: "AE.ADBE Motion" }]) };
  const clipB = { name: "B002.mov", nodeId: "b", start: time(4), end: time(10), components: collection([{ matchName: "AE.ADBE Motion" }]) };
  if (lumetriOnFirst) clipA.components = collection([clipA.components[0], frenchLumetri()]);
  let cti = time(5);
  const exported = [];
  const seq = {
    name: "Séquence 01",
    videoTracks: collection([{ clips: collection([clipA, clipB]) }]),
    getSelection: () => selection.map((n) => (n === "a" ? clipA : clipB)),
    getPlayerPosition: () => cti,
    setPlayerPosition: (ticks) => { cti = { ticks: String(ticks), seconds: Number(ticks) / TICKS_PER_SECOND }; }
  };
  const qeItems = [clipA, clipB].map((clip) => ({
    name: clip.name,
    type: "Clip",
    start: { secs: clip.start.seconds },
    addVideoEffect(fx) {
      if (fx === "LUMETRI") clip.components = collection([clip.components[0], frenchLumetri()]);
    }
  }));
  const context = {
    app: { project: { activeSequence: seq }, enableQE() {} },
    qe: {
      project: {
        getActiveSequence: () => ({
          CTI: { get timecode() { return "00:00:0" + Math.floor(cti.seconds) + ":00"; } },
          getVideoTrackAt: () => ({ numItems: qeItems.length, getItemAt: (i) => qeItems[i] }),
          exportFramePNG: (tc, p) => exported.push([tc, p])
        }),
        // Premiere en français : seul le nom localisé existe
        getVideoEffectByName: (n) => (n === "Couleur Lumetri" ? "LUMETRI" : null)
      }
    }
  };
  vm.createContext(context);
  vm.runInContext(source + "\nthis.AutoGrade = AutoGrade;", context);
  const run = (expr) => JSON.parse(vm.runInContext(expr, context));
  return { run, clipA, clipB, exported, seq };
}

test("sans sélection, prend le plan sous la tête de lecture", () => {
  const w = makeWorld();
  const res = w.run("AutoGrade.listTargets()");
  assert.equal(res.ok, true);
  assert.equal(res.fromSelection, false);
  assert.equal(res.targets.length, 1);
  assert.equal(res.targets[0].name, "B002.mov");
  assert.equal(res.targets[0].clipIndex, 1);
});

test("avec une sélection, renvoie tous les plans sélectionnés", () => {
  const w = makeWorld({ selection: ["a", "b"] });
  const res = w.run("AutoGrade.listTargets()");
  assert.deepEqual(res.targets.map((t) => t.name), ["A001.mov", "B002.mov"]);
  assert.equal(res.fromSelection, true);
});

test("exportFrame place la tête au milieu du plan et remet Lumetri au neutre", () => {
  const w = makeWorld({ lumetriOnFirst: true });
  w.clipA.components[1].properties[1].value = 42; // Température réglée à la main
  const res = w.run('AutoGrade.exportFrame(0, 0, "/tmp/frame_0")');
  assert.equal(res.ok, true);
  assert.equal(Number(w.seq.getPlayerPosition().seconds), 2);
  assert.deepEqual(w.exported, [["00:00:02:00", "/tmp/frame_0"]]);
  assert.equal(w.clipA.components[1].properties[1].value, 0);
});

test("applyParams ajoute Lumetri (nom français) et règle les curseurs", () => {
  const w = makeWorld();
  const params = { temperature: 12, tint: -3, exposure: 0.35, contrast: 10, highlights: -20, shadows: 15, whites: 5, blacks: -4, saturation: 108, vibrance: 12 };
  const res = w.run("AutoGrade.applyParams(0, 1, " + JSON.stringify(params) + ")");
  assert.equal(res.ok, true, res.error);
  assert.equal(res.addedLumetri, true);
  assert.deepEqual(res.missing, []);
  assert.deepEqual(res.applied, params);
  const props = w.clipB.components[1].properties;
  const byName = (n) => props.filter((p) => p.displayName === n);
  // seule la première « Saturation » (Correction de base) est modifiée
  assert.equal(byName("Saturation")[0].value, 108);
  assert.equal(byName("Saturation")[1].value, 100);
  assert.equal(byName("Teinte des tons foncés")[0].value, 0);
  assert.equal(byName("Tons foncés")[0].value, 15);
});

test("erreur claire quand il n'y a pas de séquence", () => {
  const w = makeWorld();
  w.seq.videoTracks = null;
  const res = w.run("(function(){ app.project.activeSequence = null; return AutoGrade.listTargets(); })()");
  assert.equal(res.ok, false);
  assert.match(res.error, /séquence active/);
});
