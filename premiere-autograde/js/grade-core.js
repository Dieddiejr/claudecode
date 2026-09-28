/*
 * Moteur d'étalonnage partagé : bornes des réglages, statistiques d'image,
 * aperçu (même formule pour la vignette et le LUT .cube) et consignes pour Claude.
 * Fonctionne dans le panneau (window.GradeCore) et sous Node (tests).
 */
(function (factory) {
  // Dans le panneau CEP, Node est actif (« module » existe) : on vérifie d'abord window.
  if (typeof window !== "undefined") window.GradeCore = factory();
  else module.exports = factory();
})(function () {
  "use strict";

  // Réglages de la section « Correction de base » de Lumetri Color.
  // neutral = valeur par défaut de Lumetri ; min/max = bornes que l'on s'autorise.
  var PARAMS = {
    temperature: { min: -100, max: 100, neutral: 0, label: "Température" },
    tint: { min: -100, max: 100, neutral: 0, label: "Teinte" },
    exposure: { min: -3, max: 3, neutral: 0, label: "Exposition" },
    contrast: { min: -100, max: 100, neutral: 0, label: "Contraste" },
    highlights: { min: -100, max: 100, neutral: 0, label: "Tons clairs" },
    shadows: { min: -100, max: 100, neutral: 0, label: "Tons foncés" },
    whites: { min: -100, max: 100, neutral: 0, label: "Blancs" },
    blacks: { min: -100, max: 100, neutral: 0, label: "Noirs" },
    saturation: { min: 0, max: 200, neutral: 100, label: "Saturation" },
    vibrance: { min: -100, max: 100, neutral: 0, label: "Vibrance" }
  };
  var PARAM_KEYS = Object.keys(PARAMS);

  var STYLES = {
    naturel: "Correction neutre et fidèle : image juste, peaux naturelles, aucun effet visible.",
    cinema: "Look cinéma doux : contraste maîtrisé, noirs légèrement relevés, saturation retenue, carnations chaudes.",
    chaud: "Ambiance chaude et lumineuse type fin de journée, sans rendre les peaux orange.",
    froid: "Ambiance fraîche et moderne, légèrement bleutée, en gardant des peaux crédibles.",
    documentaire: "Rendu documentaire / reportage : réaliste, légèrement contrasté, couleurs sobres.",
    pop: "Rendu vif et punchy pour réseaux sociaux : couleurs franches, bon contraste, sans excès."
  };

  function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }
  function round(v, step) { return Number((Math.round(v / step) * step).toFixed(2)); }

  function neutralParams() {
    var out = {};
    PARAM_KEYS.forEach(function (k) { out[k] = PARAMS[k].neutral; });
    return out;
  }

  // Valide et borne les réglages renvoyés par Claude. Les valeurs manquantes
  // ou non numériques retombent sur la valeur neutre.
  function sanitizeParams(raw) {
    var out = neutralParams();
    if (!raw || typeof raw !== "object") return out;
    PARAM_KEYS.forEach(function (k) {
      var v = Number(raw[k]);
      if (isFinite(v)) {
        var p = PARAMS[k];
        out[k] = round(clamp(v, p.min, p.max), k === "exposure" ? 0.05 : 1);
      }
    });
    return out;
  }

  // Rapproche chaque réglage de sa valeur neutre (intensité 0..1).
  function scaleParams(params, intensity) {
    var out = {};
    var t = clamp(intensity, 0, 1.5);
    PARAM_KEYS.forEach(function (k) {
      var n = PARAMS[k].neutral;
      var v = n + (params[k] - n) * t;
      out[k] = round(clamp(v, PARAMS[k].min, PARAMS[k].max), k === "exposure" ? 0.05 : 1);
    });
    return out;
  }

  function smoothstep(e0, e1, x) {
    var t = clamp((x - e0) / (e1 - e0), 0, 1);
    return t * t * (3 - 2 * t);
  }
  function toLinear(c) { return Math.pow(clamp(c, 0, 1), 2.2); }
  function toDisplay(c) { return Math.pow(clamp(c, 0, 1), 1 / 2.2); }
  function luma(r, g, b) { return 0.2126 * r + 0.7152 * g + 0.0722 * b; }

  // Approximation de Lumetri, valeurs d'entrée/sortie en 0..1 (espace affichage).
  // Sert à l'aperçu avant/après et au LUT de secours : Premiere applique ensuite
  // ses propres formules, le rendu final peut donc légèrement différer.
  function makeTransform(params) {
    var p = sanitizeParams(params);
    var temp = p.temperature / 100;
    var tint = p.tint / 100;
    var gainR = 1 + 0.18 * temp + 0.04 * tint;
    var gainG = 1 - 0.12 * tint;
    var gainB = 1 - 0.18 * temp + 0.04 * tint;
    var norm = 1 / luma(gainR, gainG, gainB);
    gainR *= norm; gainG *= norm; gainB *= norm;
    var expo = Math.pow(2, p.exposure);
    var contrast = p.contrast / 100;
    var hi = p.highlights / 100, sh = p.shadows / 100;
    var wh = p.whites / 100, bl = p.blacks / 100;
    var sat = p.saturation / 100;
    var vib = p.vibrance / 100;

    function tone(v) {
      // contraste : courbe en S autour du gris moyen
      var s = smoothstep(0, 1, v);
      v = v + (s - v) * contrast;
      v += hi * 0.22 * smoothstep(0.45, 1, v) * (1 - v * 0.3);
      v += sh * 0.22 * (1 - smoothstep(0, 0.55, v)) * (0.3 + v);
      v += wh * 0.12 * Math.pow(v, 3);
      v += bl * 0.1 * Math.pow(1 - v, 3);
      return clamp(v, 0, 1);
    }

    return function (r, g, b) {
      var lr = toLinear(r) * gainR * expo;
      var lg = toLinear(g) * gainG * expo;
      var lb = toLinear(b) * gainB * expo;
      var dr = toDisplay(lr), dg = toDisplay(lg), db = toDisplay(lb);
      var y0 = luma(dr, dg, db);
      var y1 = tone(y0);
      // on applique la courbe sur la luminance pour préserver les teintes
      var k = y0 > 1e-4 ? y1 / y0 : 1;
      dr *= k; dg *= k; db *= k;
      if (y0 <= 1e-4) { dr = dg = db = y1; }
      var y = luma(dr, dg, db);
      var mx = Math.max(dr, dg, db), mn = Math.min(dr, dg, db);
      var curSat = mx > 1e-4 ? (mx - mn) / mx : 0;
      var amount = sat * (1 + vib * (1 - curSat) * 0.8);
      dr = y + (dr - y) * amount;
      dg = y + (dg - y) * amount;
      db = y + (db - y) * amount;
      return [clamp(dr, 0, 1), clamp(dg, 0, 1), clamp(db, 0, 1)];
    };
  }

  // Applique le rendu sur un tableau RGBA (ImageData.data) et renvoie une copie.
  function applyToPixels(data, params) {
    var f = makeTransform(params);
    var out = new Uint8ClampedArray(data.length);
    for (var i = 0; i < data.length; i += 4) {
      var c = f(data[i] / 255, data[i + 1] / 255, data[i + 2] / 255);
      out[i] = c[0] * 255 + 0.5;
      out[i + 1] = c[1] * 255 + 0.5;
      out[i + 2] = c[2] * 255 + 0.5;
      out[i + 3] = data[i + 3];
    }
    return out;
  }

  // Mesures type « scopes » transmises à Claude en plus de l'image.
  function computeStats(data) {
    var hist = new Array(256);
    for (var h = 0; h < 256; h++) hist[h] = 0;
    var n = 0, sr = 0, sg = 0, sb = 0, ssat = 0, clipHi = 0, clipLo = 0;
    for (var i = 0; i < data.length; i += 4) {
      var r = data[i], g = data[i + 1], b = data[i + 2];
      var y = Math.round(luma(r, g, b));
      hist[y]++;
      sr += r; sg += g; sb += b;
      var mx = Math.max(r, g, b), mn = Math.min(r, g, b);
      ssat += mx > 0 ? (mx - mn) / mx : 0;
      if (mx >= 250) clipHi++;
      if (mx <= 5) clipLo++;
      n++;
    }
    function pct(p) {
      var target = n * p, acc = 0;
      for (var v = 0; v < 256; v++) { acc += hist[v]; if (acc >= target) return v; }
      return 255;
    }
    function ire(v) { return Math.round(v / 255 * 100); }
    return {
      luminance_ire: { p1: ire(pct(0.01)), p10: ire(pct(0.1)), median: ire(pct(0.5)), p90: ire(pct(0.9)), p99: ire(pct(0.99)) },
      moyenne_rgb: { r: Math.round(sr / n), g: Math.round(sg / n), b: Math.round(sb / n) },
      saturation_moyenne_pct: Math.round(ssat / n * 100),
      pixels_brules_pct: Math.round(clipHi / n * 1000) / 10,
      pixels_bouches_pct: Math.round(clipLo / n * 1000) / 10
    };
  }

  // LUT 3D au format .cube (Adobe/Resolve), à charger dans Lumetri > Créatif > Look
  // si l'application automatique des curseurs échoue.
  function buildCubeLUT(params, size, title) {
    size = size || 33;
    var f = makeTransform(params);
    var lines = [
      "TITLE \"" + String(title || "Claude AutoGrade").replace(/"/g, "'") + "\"",
      "LUT_3D_SIZE " + size,
      "DOMAIN_MIN 0.0 0.0 0.0",
      "DOMAIN_MAX 1.0 1.0 1.0"
    ];
    var d = size - 1;
    for (var b = 0; b < size; b++) {
      for (var g = 0; g < size; g++) {
        for (var r = 0; r < size; r++) {
          var c = f(r / d, g / d, b / d);
          lines.push(c[0].toFixed(6) + " " + c[1].toFixed(6) + " " + c[2].toFixed(6));
        }
      }
    }
    return lines.join("\n") + "\n";
  }

  var SYSTEM_PROMPT = [
    "Tu es un étalonneur (coloriste) professionnel qui règle Lumetri Color dans Adobe Premiere Pro.",
    "On te donne une image fixe extraite d'un plan vidéo, des mesures de type scopes, et le style voulu.",
    "",
    "Méthode, dans cet ordre :",
    "1. Correction technique : exposition, balance des blancs (les neutres doivent être neutres), contraste, récupération des hautes lumières et des ombres, carnations naturelles.",
    "2. Seulement ensuite, le style demandé, avec retenue. Un résultat propre et crédible vaut mieux qu'un effet appuyé.",
    "",
    "Réglages disponibles (section Correction de base de Lumetri, valeurs absolues) :",
    "- temperature : -100 (plus froid/bleu) à 100 (plus chaud/orange), neutre 0",
    "- tint : -100 (vers le vert) à 100 (vers le magenta), neutre 0",
    "- exposure : -3 à 3 en diaphs, neutre 0",
    "- contrast, highlights, shadows, whites, blacks : -100 à 100, neutre 0",
    "- saturation : 0 à 200, neutre 100",
    "- vibrance : -100 à 100, neutre 0",
    "",
    "Repères : sur des images déjà correctes, la plupart des réglages restent entre -30 et 30 ; l'exposition bouge rarement de plus de 1 diaph ; la saturation reste entre 85 et 125.",
    "Si l'image semble être en profil log (très grise, peu contrastée, peu saturée), dis-le : ces réglages ne remplacent pas une LUT de conversion.",
    "Réponds en français, de façon simple et pédagogique, pour quelqu'un qui débute en étalonnage."
  ].join("\n");

  var RESPONSE_SCHEMA = {
    type: "object",
    properties: {
      diagnostic: { type: "string", description: "Ce qui ne va pas dans l'image, en 1 à 3 phrases simples." },
      profil_log_probable: { type: "boolean" },
      parametres: {
        type: "object",
        properties: {
          temperature: { type: "number" },
          tint: { type: "number" },
          exposure: { type: "number" },
          contrast: { type: "number" },
          highlights: { type: "number" },
          shadows: { type: "number" },
          whites: { type: "number" },
          blacks: { type: "number" },
          saturation: { type: "number" },
          vibrance: { type: "number" }
        },
        required: PARAM_KEYS.slice(),
        additionalProperties: false
      },
      explication: { type: "string", description: "Pourquoi ces réglages, en quelques phrases, pour apprendre." }
    },
    required: ["diagnostic", "profil_log_probable", "parametres", "explication"],
    additionalProperties: false
  };

  function buildUserText(opts) {
    var styleText = STYLES[opts.style] || STYLES.naturel;
    var lines = [
      "Plan : " + (opts.clipName || "sans nom"),
      "Style voulu : " + styleText
    ];
    if (opts.notes) lines.push("Précisions de l'utilisateur : " + opts.notes);
    lines.push("Mesures de l'image (luminance en IRE 0-100, RGB 0-255) :");
    lines.push(JSON.stringify(opts.stats));
    lines.push("Donne les réglages Lumetri à appliquer sur ce plan.");
    return lines.join("\n");
  }

  return {
    PARAMS: PARAMS,
    PARAM_KEYS: PARAM_KEYS,
    STYLES: STYLES,
    SYSTEM_PROMPT: SYSTEM_PROMPT,
    RESPONSE_SCHEMA: RESPONSE_SCHEMA,
    neutralParams: neutralParams,
    sanitizeParams: sanitizeParams,
    scaleParams: scaleParams,
    makeTransform: makeTransform,
    applyToPixels: applyToPixels,
    computeStats: computeStats,
    buildCubeLUT: buildCubeLUT,
    buildUserText: buildUserText
  };
});
