// Lancer avec : node --test tests/
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const Core = require("../js/grade-core.js");

test("sanitizeParams borne les valeurs et remplace les valeurs invalides", () => {
  const p = Core.sanitizeParams({ temperature: 250, exposure: -9, saturation: "abc", contrast: 12.4, tint: null });
  assert.equal(p.temperature, 100);
  assert.equal(p.exposure, -3);
  assert.equal(p.saturation, 100);
  assert.equal(p.contrast, 12);
  assert.equal(p.tint, 0);
  assert.deepEqual(Object.keys(p).sort(), Core.PARAM_KEYS.slice().sort());
});

test("scaleParams à 0 % donne les valeurs neutres, à 50 % la moitié", () => {
  const p = Core.sanitizeParams({ temperature: 40, saturation: 140, exposure: 1 });
  assert.deepEqual(Core.scaleParams(p, 0), Core.neutralParams());
  const half = Core.scaleParams(p, 0.5);
  assert.equal(half.temperature, 20);
  assert.equal(half.saturation, 120);
  assert.equal(half.exposure, 0.5);
});

test("les réglages neutres ne modifient pas l'image", () => {
  const f = Core.makeTransform(Core.neutralParams());
  for (const [r, g, b] of [[0, 0, 0], [1, 1, 1], [0.5, 0.2, 0.8], [0.1, 0.9, 0.4]]) {
    const out = f(r, g, b);
    assert.ok(Math.abs(out[0] - r) < 1e-6 && Math.abs(out[1] - g) < 1e-6 && Math.abs(out[2] - b) < 1e-6, `${r},${g},${b} -> ${out}`);
  }
});

test("chaque réglage agit dans le bon sens", () => {
  const grey = [0.5, 0.5, 0.5];
  const run = (params, rgb = grey) => Core.makeTransform(params)(...rgb);
  const warm = run({ temperature: 50 });
  assert.ok(warm[0] > warm[2], "température + réchauffe");
  const magenta = run({ tint: 50 });
  assert.ok(magenta[1] < magenta[0], "teinte + vers le magenta");
  assert.ok(run({ exposure: 1 })[1] > 0.5, "exposition + éclaircit");
  assert.ok(run({ contrast: 60 }, [0.2, 0.2, 0.2])[0] < 0.2, "contraste + assombrit les ombres");
  assert.ok(run({ shadows: 60 }, [0.15, 0.15, 0.15])[0] > 0.15, "tons foncés + relève les ombres");
  assert.ok(run({ highlights: -60 }, [0.85, 0.85, 0.85])[0] < 0.85, "tons clairs - récupère les hautes lumières");
  const desat = run({ saturation: 0 }, [0.8, 0.3, 0.2]);
  assert.ok(Math.abs(desat[0] - desat[2]) < 1e-6, "saturation 0 donne du gris");
});

test("la courbe de tons reste croissante quels que soient les réglages", () => {
  for (const params of [{ contrast: 100 }, { contrast: -100 }, { highlights: 100, shadows: 100 }, { whites: -100, blacks: 100 }, { contrast: 80, highlights: -100, shadows: 100 }]) {
    const f = Core.makeTransform(params);
    let prev = -1;
    for (let i = 0; i <= 100; i++) {
      const v = f(i / 100, i / 100, i / 100)[1];
      assert.ok(v >= prev - 1e-9, `${JSON.stringify(params)} non monotone à ${i}`);
      prev = v;
    }
  }
});

test("buildCubeLUT produit un fichier .cube valide", () => {
  const cube = Core.buildCubeLUT({ temperature: 20, contrast: 15 }, 17, 'Plan "A"');
  const lines = cube.trim().split("\n");
  assert.equal(lines[0], "TITLE \"Plan 'A'\"");
  assert.equal(lines[1], "LUT_3D_SIZE 17");
  const data = lines.slice(4);
  assert.equal(data.length, 17 ** 3);
  for (const l of data) {
    const nums = l.split(" ").map(Number);
    assert.equal(nums.length, 3);
    for (const n of nums) assert.ok(n >= 0 && n <= 1);
  }
  // premier point = noir, le rouge varie le plus vite
  assert.deepEqual(data[0].split(" ").map(Number), [0, 0, 0]);
  const neutral = Core.buildCubeLUT(Core.neutralParams(), 3).trim().split("\n").slice(4);
  assert.equal(neutral[1], "0.500000 0.000000 0.000000");
});

test("computeStats mesure luminance, dominante et écrêtage", () => {
  const px = [];
  for (let i = 0; i < 100; i++) px.push(i < 10 ? 255 : 128, 128, i < 10 ? 255 : 100, 255);
  const s = Core.computeStats(new Uint8ClampedArray(px));
  assert.equal(s.pixels_brules_pct, 10);
  assert.ok(s.moyenne_rgb.r > s.moyenne_rgb.b);
  assert.ok(s.luminance_ire.median > 40 && s.luminance_ire.median < 60);
});

test("le schéma de réponse exige tous les réglages", () => {
  assert.deepEqual(Core.RESPONSE_SCHEMA.properties.parametres.required.slice().sort(), Core.PARAM_KEYS.slice().sort());
  const text = Core.buildUserText({ clipName: "A001", style: "cinema", notes: "", stats: { x: 1 } });
  assert.match(text, /Look cinéma/);
});
