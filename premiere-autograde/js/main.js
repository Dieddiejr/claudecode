/* Panneau Claude AutoGrade : analyse des plans avec Claude et réglage de Lumetri Color. */
(function () {
  "use strict";

  var fs = require("fs");
  var os = require("os");
  var path = require("path");

  var Core = window.GradeCore;
  var Anthropic = window.Anthropic;
  var MODEL = "claude-opus-5-5";
  var KEY_STORAGE = "claude-autograde.apiKey";
  var MAX_IMAGE_EDGE = 1280;

  var $ = function (id) { return document.getElementById(id); };
  var state = { results: [], current: -1, busy: false };

  // ---------- Premiere (ExtendScript) ----------

  function host(fnCall) {
    return new Promise(function (resolve, reject) {
      window.__adobe_cep__.evalScript(fnCall, function (raw) {
        var res;
        try { res = JSON.parse(raw); } catch (e) {
          return reject(new Error("Réponse inattendue de Premiere : " + raw));
        }
        if (!res.ok) return reject(new Error(res.error));
        resolve(res);
      });
    });
  }

  function call(fn) {
    var args = Array.prototype.slice.call(arguments, 1).map(function (a) { return JSON.stringify(a); });
    return host("AutoGrade." + fn + "(" + args.join(",") + ")");
  }

  function waitForFile(candidates, timeoutMs) {
    var start = Date.now();
    return new Promise(function (resolve, reject) {
      (function poll() {
        for (var i = 0; i < candidates.length; i++) {
          try {
            var st = fs.statSync(candidates[i]);
            if (st.size > 0) {
              // on attend que la taille se stabilise (écriture terminée)
              return setTimeout(function (p, size) {
                if (fs.statSync(p).size === size) resolve(p); else poll();
              }, 150, candidates[i], st.size);
            }
          } catch (e) { /* pas encore écrit */ }
        }
        if (Date.now() - start > timeoutMs) return reject(new Error("Premiere n'a pas exporté l'image du plan."));
        setTimeout(poll, 150);
      })();
    });
  }

  // ---------- Image ----------

  function loadImage(file) {
    return new Promise(function (resolve, reject) {
      var img = new Image();
      img.onload = function () { resolve(img); };
      img.onerror = function () { reject(new Error("Impossible de lire l'image exportée.")); };
      img.src = "data:image/png;base64," + fs.readFileSync(file).toString("base64");
    });
  }

  function drawScaled(img, maxEdge) {
    var scale = Math.min(1, maxEdge / Math.max(img.width, img.height));
    var c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(img.width * scale));
    c.height = Math.max(1, Math.round(img.height * scale));
    c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
    return c;
  }

  // ---------- Claude ----------

  function apiKey() {
    try { return localStorage.getItem(KEY_STORAGE) || ""; } catch (e) { return ""; }
  }

  function friendlyError(err) {
    if (err instanceof Anthropic.AuthenticationError) return "Clé API refusée. Vérifie-la dans « Clé API ».";
    if (err instanceof Anthropic.PermissionDeniedError) return "Cette clé API n'a pas accès au modèle.";
    if (err instanceof Anthropic.RateLimitError) return "Trop de requêtes pour le moment. Réessaie dans une minute.";
    if (err instanceof Anthropic.APIConnectionError) return "Connexion à Claude impossible. Vérifie ta connexion Internet.";
    if (err instanceof Anthropic.APIError) return "Erreur Claude (" + err.status + ") : " + err.message;
    return err && err.message ? err.message : String(err);
  }

  async function askClaude(jpegBase64, stats, clipName) {
    var client = new Anthropic({ apiKey: apiKey(), dangerouslyAllowBrowser: true });
    var response = await client.beta.messages.create({
      model: MODEL,
      max_tokens: 16000,
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      output_config: {
        effort: "medium",
        format: { type: "json_schema", schema: Core.RESPONSE_SCHEMA }
      },
      system: Core.SYSTEM_PROMPT,
      messages: [{
        role: "user",
        content: [
          { type: "image", source: { type: "base64", media_type: "image/jpeg", data: jpegBase64 } },
          {
            type: "text",
            text: Core.buildUserText({ clipName: clipName, style: $("style").value, notes: $("notes").value.trim(), stats: stats })
          }
        ]
      }]
    });

    if (response.stop_reason === "refusal") {
      throw new Error("Claude a refusé d'analyser cette image" + (response.stop_details && response.stop_details.explanation ? " : " + response.stop_details.explanation : "."));
    }
    if (response.stop_reason === "max_tokens") throw new Error("Réponse de Claude incomplète. Relance l'analyse.");
    var text = response.content.filter(function (b) { return b.type === "text"; }).map(function (b) { return b.text; }).join("");
    var parsed;
    try { parsed = JSON.parse(text); } catch (e) { throw new Error("Réponse de Claude illisible. Relance l'analyse."); }
    parsed.parametres = Core.sanitizeParams(parsed.parametres);
    return parsed;
  }

  // ---------- Flux principal ----------

  function setStatus(msg, kind) {
    var el = $("status");
    el.textContent = msg || "";
    el.className = "status" + (kind ? " " + kind : "");
  }

  function setBusy(busy) {
    state.busy = busy;
    ["analyze", "apply", "apply-all", "reset", "export-lut"].forEach(function (id) { $(id).disabled = busy; });
  }

  async function analyze() {
    if (state.busy) return;
    if (!apiKey()) {
      $("settings").hidden = false;
      setStatus("Ajoute d'abord ta clé API Anthropic.", "error");
      return;
    }
    setBusy(true);
    try {
      setStatus("Recherche des plans…");
      var list = await call("listTargets");
      var targets = list.targets;
      var tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "claude-autograde-"));
      state.results = [];

      for (var i = 0; i < targets.length; i++) {
        var t = targets[i];
        var label = "Plan " + (i + 1) + "/" + targets.length + " (" + t.name + ")";
        setStatus(label + " : export de l'image…");
        var base = path.join(tmpDir, "frame_" + i);
        await call("exportFrame", t.trackIndex, t.clipIndex, base);
        var file = await waitForFile([base + ".png", base], 15000);
        var img = await loadImage(file);

        var full = drawScaled(img, MAX_IMAGE_EDGE);
        var small = drawScaled(img, 320);
        var stats = Core.computeStats(small.getContext("2d").getImageData(0, 0, small.width, small.height).data);
        var jpeg = full.toDataURL("image/jpeg", 0.9).split(",")[1];

        setStatus(label + " : Claude analyse l'image…");
        var answer = await askClaude(jpeg, stats, t.name);
        state.results.push({ target: t, image: small, answer: answer });
        renderPicker();
        select(state.results.length - 1);
      }
      setStatus(targets.length + " plan(s) analysé(s). Vérifie l'aperçu puis clique sur « Appliquer ».", "ok");
    } catch (err) {
      setStatus(friendlyError(err), "error");
    } finally {
      setBusy(false);
    }
  }

  function intensity() { return Number($("intensity").value) / 100; }

  function currentParams(result) {
    return Core.scaleParams(result.answer.parametres, intensity());
  }

  function renderPicker() {
    var picker = $("clip-picker");
    picker.innerHTML = "";
    state.results.forEach(function (r, i) {
      var o = document.createElement("option");
      o.value = i;
      o.textContent = (i + 1) + ". " + r.target.name + " (V" + (r.target.trackIndex + 1) + ")";
      picker.appendChild(o);
    });
    picker.parentNode.hidden = state.results.length < 2;
    $("apply-all").hidden = state.results.length < 2;
  }

  function select(i) {
    state.current = i;
    $("clip-picker").value = i;
    var r = state.results[i];
    $("result").hidden = false;
    $("diagnostic").textContent = r.answer.diagnostic;
    $("explanation").textContent = r.answer.explication;
    $("log-warning").hidden = !r.answer.profil_log_probable;
    renderPreview();
  }

  function renderPreview() {
    var r = state.results[state.current];
    if (!r) return;
    var src = r.image;
    var params = currentParams(r);
    var before = $("before"), after = $("after");
    before.width = after.width = src.width;
    before.height = after.height = src.height;
    before.getContext("2d").drawImage(src, 0, 0);
    var data = src.getContext("2d").getImageData(0, 0, src.width, src.height);
    var out = new ImageData(Core.applyToPixels(data.data, params), src.width, src.height);
    after.getContext("2d").putImageData(out, 0, 0);

    var rows = Core.PARAM_KEYS.map(function (k) {
      var p = Core.PARAMS[k];
      var v = params[k];
      var changed = v !== p.neutral;
      var shown = k === "exposure" ? (v > 0 ? "+" : "") + v.toFixed(2) : (k !== "saturation" && v > 0 ? "+" : "") + v;
      return "<tr><td>" + p.label + "</td><td" + (changed ? ' class="changed"' : "") + ">" + shown + "</td></tr>";
    });
    $("params").innerHTML = rows.join("");
    $("intensity-value").textContent = $("intensity").value + " %";
  }

  function describeApply(res) {
    var msg = "Lumetri réglé sur « " + res.clip + " »" + (res.addedLumetri ? " (effet ajouté)" : "") + ".";
    if (res.missing && res.missing.length) {
      msg += "\nRéglages non trouvés dans Lumetri : " + res.missing.join(", ") +
        ". Utilise « Exporter en LUT .cube » comme solution de secours.";
    }
    return msg;
  }

  async function apply(all) {
    if (state.busy || state.current < 0) return;
    setBusy(true);
    try {
      var list = all ? state.results : [state.results[state.current]];
      var messages = [];
      for (var i = 0; i < list.length; i++) {
        var r = list[i];
        var res = await call("applyParams", r.target.trackIndex, r.target.clipIndex, currentParams(r));
        messages.push(describeApply(res));
      }
      var incomplete = messages.some(function (m) { return m.indexOf("non trouvés") >= 0; });
      setStatus(messages.join("\n"), incomplete ? "error" : "ok");
    } catch (err) {
      setStatus(friendlyError(err), "error");
    } finally {
      setBusy(false);
    }
  }

  async function reset() {
    if (state.busy || state.current < 0) return;
    setBusy(true);
    try {
      var r = state.results[state.current];
      await call("resetParams", r.target.trackIndex, r.target.clipIndex);
      setStatus("Curseurs Lumetri remis au neutre sur « " + r.target.name + " ».", "ok");
    } catch (err) {
      setStatus(friendlyError(err), "error");
    } finally {
      setBusy(false);
    }
  }

  function exportLut() {
    var r = state.results[state.current];
    if (!r) return;
    try {
      var dir = path.join(os.homedir(), "Desktop", "Claude AutoGrade");
      fs.mkdirSync(dir, { recursive: true });
      var safeName = r.target.name.replace(/[\\/:*?"<>|]+/g, "_").replace(/\.[^.]+$/, "");
      var file = path.join(dir, safeName + "_" + $("style").value + ".cube");
      fs.writeFileSync(file, Core.buildCubeLUT(currentParams(r), 33, "Claude AutoGrade - " + r.target.name));
      setStatus("LUT enregistrée : " + file + "\nDans Lumetri > Créatif > Look, choisis « Parcourir… » et sélectionne ce fichier.", "ok");
    } catch (err) {
      setStatus("Impossible d'écrire la LUT : " + err.message, "error");
    }
  }

  // ---------- Interface ----------

  $("toggle-settings").addEventListener("click", function () {
    $("settings").hidden = !$("settings").hidden;
    $("api-key").value = apiKey();
  });
  $("save-key").addEventListener("click", function () {
    try {
      localStorage.setItem(KEY_STORAGE, $("api-key").value.trim());
      $("settings").hidden = true;
      setStatus("Clé API enregistrée.", "ok");
    } catch (e) {
      setStatus("Impossible d'enregistrer la clé : " + e.message, "error");
    }
  });
  $("analyze").addEventListener("click", analyze);
  $("apply").addEventListener("click", function () { apply(false); });
  $("apply-all").addEventListener("click", function () { apply(true); });
  $("reset").addEventListener("click", reset);
  $("export-lut").addEventListener("click", exportLut);
  $("intensity").addEventListener("input", renderPreview);
  $("clip-picker").addEventListener("change", function () { select(Number(this.value)); });

  if (!apiKey()) {
    $("settings").hidden = false;
    setStatus("Bienvenue ! Commence par enregistrer ta clé API Anthropic.");
  }
})();
