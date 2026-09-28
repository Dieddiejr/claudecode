/*
 * Côté Premiere Pro (ExtendScript, ES3) : repère les plans à étalonner,
 * exporte une image de chaque plan et règle l'effet Lumetri Color.
 * Chaque fonction publique renvoie une chaîne JSON.
 */
var AutoGrade = (function () {
  var LUMETRI_MATCH_NAME = "AE.ADBE Lumetri";
  // Nom de l'effet dans le panneau Effets, selon la langue de Premiere.
  var LUMETRI_EFFECT_NAMES = ["Lumetri Color", "Couleur Lumetri", "Lumetri-Farbe", "Colore Lumetri", "Color de Lumetri", "Color Lumetri", "Cor Lumetri"];

  // Noms des curseurs (displayName) selon la langue, comparés sans accents ni casse.
  var PARAM_ALIASES = {
    temperature: ["temperature", "temperatur", "temperatura"],
    tint: ["tint", "teinte", "farbton", "tinta", "tono"],
    exposure: ["exposure", "exposition", "belichtung", "esposizione", "exposicion", "exposicao"],
    contrast: ["contrast", "contraste", "kontrast", "contrasto"],
    highlights: ["highlights", "tons clairs", "hautes lumieres", "lichter", "luci", "iluminaciones", "realces"],
    shadows: ["shadows", "tons fonces", "ombres", "tiefen", "ombre", "sombras"],
    whites: ["whites", "blancs", "weiss", "weisstone", "bianchi", "blancos", "brancos"],
    blacks: ["blacks", "noirs", "schwarz", "schwarztone", "neri", "negros", "pretos"],
    saturation: ["saturation", "sattigung", "saturazione", "saturacion", "saturacao"],
    vibrance: ["vibrance", "vivacite", "dynamik", "vividezza", "intensidad", "vibracao"]
  };
  var NEUTRAL = { temperature: 0, tint: 0, exposure: 0, contrast: 0, highlights: 0, shadows: 0, whites: 0, blacks: 0, saturation: 100, vibrance: 0 };

  function quote(s) {
    return '"' + String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\r/g, "\\r").replace(/\n/g, "\\n").replace(/\t/g, "\\t") + '"';
  }
  function toJSON(v) {
    if (v === null || v === undefined) return "null";
    if (typeof v === "number") return isFinite(v) ? String(v) : "null";
    if (typeof v === "boolean") return v ? "true" : "false";
    if (typeof v === "string") return quote(v);
    if (v instanceof Array) {
      var parts = [];
      for (var i = 0; i < v.length; i++) parts.push(toJSON(v[i]));
      return "[" + parts.join(",") + "]";
    }
    var props = [];
    for (var k in v) if (v.hasOwnProperty(k)) props.push(quote(k) + ":" + toJSON(v[k]));
    return "{" + props.join(",") + "}";
  }
  function ok(data) { data = data || {}; data.ok = true; return toJSON(data); }
  function fail(msg) { return toJSON({ ok: false, error: String(msg) }); }

  function normalize(s) {
    s = String(s).toLowerCase();
    var map = [[/[\u00e0\u00e1\u00e2\u00e3\u00e4]/g, "a"], [/[\u00e7]/g, "c"], [/[\u00e8\u00e9\u00ea\u00eb]/g, "e"], [/[\u00ec\u00ed\u00ee\u00ef]/g, "i"], [/[\u00f2\u00f3\u00f4\u00f5\u00f6]/g, "o"], [/[\u00f9\u00fa\u00fb\u00fc]/g, "u"], [/\u00df/g, "ss"], [/[\u2011\u2013\u2014\-_:]/g, " "]];
    for (var i = 0; i < map.length; i++) s = s.replace(map[i][0], map[i][1]);
    return s.replace(/\s+/g, " ").replace(/^\s+|\s+$/g, "");
  }

  function activeSequence() {
    var seq = app.project.activeSequence;
    if (!seq) throw new Error("Aucune s\u00e9quence active. Ouvre une s\u00e9quence dans la timeline.");
    return seq;
  }

  function ticksOf(t) { return Number(t.ticks); }

  function clipInfo(trackIndex, clipIndex, clip) {
    var start = ticksOf(clip.start), end = ticksOf(clip.end);
    return {
      trackIndex: trackIndex,
      clipIndex: clipIndex,
      name: clip.name,
      startTicks: String(start),
      endTicks: String(end),
      midTicks: String(Math.floor((start + end) / 2)),
      hasLumetri: !!findLumetri(clip)
    };
  }

  function isSameClip(a, b) {
    try {
      if (a.nodeId && b.nodeId) return a.nodeId === b.nodeId;
    } catch (e) {}
    return a.name === b.name && ticksOf(a.start) === ticksOf(b.start);
  }

  // Plans sélectionnés dans la timeline ; à défaut, le plan vidéo le plus haut sous la tête de lecture.
  function listTargets() {
    try {
      var seq = activeSequence();
      var targets = [];
      var tracks = seq.videoTracks;
      var selection = seq.getSelection ? seq.getSelection() : [];
      for (var s = 0; selection && s < selection.length; s++) {
        var sel = selection[s];
        for (var t = 0; t < tracks.numTracks; t++) {
          var clips = tracks[t].clips;
          for (var c = 0; c < clips.numItems; c++) {
            if (isSameClip(clips[c], sel)) targets.push(clipInfo(t, c, clips[c]));
          }
        }
      }
      var fromSelection = targets.length > 0;
      if (!fromSelection) {
        var cti = ticksOf(seq.getPlayerPosition());
        for (var tt = tracks.numTracks - 1; tt >= 0 && targets.length === 0; tt--) {
          var cl = tracks[tt].clips;
          for (var cc = 0; cc < cl.numItems; cc++) {
            if (ticksOf(cl[cc].start) <= cti && cti < ticksOf(cl[cc].end)) {
              targets.push(clipInfo(tt, cc, cl[cc]));
              break;
            }
          }
        }
      }
      if (targets.length === 0) return fail("Aucun plan trouv\u00e9 : s\u00e9lectionne un ou plusieurs plans dans la timeline, ou place la t\u00eate de lecture sur un plan.");
      return ok({ sequence: seq.name, fromSelection: fromSelection, targets: targets });
    } catch (e) {
      return fail(e.message || e);
    }
  }

  function getClip(trackIndex, clipIndex) {
    var seq = activeSequence();
    var track = seq.videoTracks[trackIndex];
    if (!track) throw new Error("Piste vid\u00e9o introuvable (V" + (trackIndex + 1) + ").");
    var clip = track.clips[clipIndex];
    if (!clip) throw new Error("Plan introuvable sur V" + (trackIndex + 1) + ". La timeline a peut-\u00eatre chang\u00e9 : relance l'analyse.");
    return clip;
  }

  function findLumetri(clip) {
    var comps = clip.components;
    for (var i = 0; i < comps.numItems; i++) {
      if (comps[i].matchName === LUMETRI_MATCH_NAME) return comps[i];
    }
    return null;
  }

  function findQEItem(trackIndex, clip) {
    app.enableQE();
    var qeSeq = qe.project.getActiveSequence();
    var qeTrack = qeSeq.getVideoTrackAt(trackIndex);
    var startSecs = Number(clip.start.seconds);
    var best = null, bestDelta = 1e9;
    for (var i = 0; i < qeTrack.numItems; i++) {
      var item = qeTrack.getItemAt(i);
      if (!item || item.type === "Empty") continue;
      var s = null;
      try { s = Number(item.start.secs); } catch (e) {}
      var delta = s === null || isNaN(s) ? 1e8 : Math.abs(s - startSecs);
      if (item.name === clip.name && delta < bestDelta) { best = item; bestDelta = delta; }
    }
    return best;
  }

  function addLumetri(trackIndex, clip) {
    var qeItem = findQEItem(trackIndex, clip);
    if (!qeItem) throw new Error("Impossible de retrouver le plan pour y ajouter Lumetri Color.");
    for (var i = 0; i < LUMETRI_EFFECT_NAMES.length; i++) {
      var fx = qe.project.getVideoEffectByName(LUMETRI_EFFECT_NAMES[i]);
      if (fx) {
        qeItem.addVideoEffect(fx);
        var comp = findLumetri(clip);
        if (comp) return comp;
      }
    }
    throw new Error("Impossible d'ajouter Lumetri Color automatiquement. Glisse l'effet Lumetri Color sur le plan puis relance.");
  }

  // Associe chaque réglage à la première propriété Lumetri dont le nom correspond.
  function mapProperties(comp) {
    var found = {}, names = [];
    var props = comp.properties;
    for (var i = 0; i < props.numItems; i++) {
      var p = props[i];
      var n = normalize(p.displayName);
      names.push(p.displayName);
      for (var key in PARAM_ALIASES) {
        if (!PARAM_ALIASES.hasOwnProperty(key) || found[key]) continue;
        var aliases = PARAM_ALIASES[key];
        for (var a = 0; a < aliases.length; a++) {
          if (n === aliases[a]) { found[key] = p; break; }
        }
      }
    }
    return { found: found, names: names };
  }

  function setParams(comp, params) {
    var mapped = mapProperties(comp);
    var applied = {}, missing = [];
    for (var key in params) {
      if (!params.hasOwnProperty(key)) continue;
      var prop = mapped.found[key];
      if (!prop) { missing.push(key); continue; }
      try {
        if (prop.isTimeVarying && prop.isTimeVarying()) prop.setTimeVarying(false);
        prop.setValue(Number(params[key]), true);
        applied[key] = Number(prop.getValue());
      } catch (e) {
        missing.push(key);
      }
    }
    return { applied: applied, missing: missing, propertyNames: mapped.names };
  }

  // Place la tête de lecture au milieu du plan, remet nos curseurs Lumetri au neutre
  // (pour analyser l'image d'origine), puis exporte l'image en PNG.
  function exportFrame(trackIndex, clipIndex, basePath) {
    try {
      var seq = activeSequence();
      var clip = getClip(trackIndex, clipIndex);
      var mid = Math.floor((ticksOf(clip.start) + ticksOf(clip.end)) / 2);
      seq.setPlayerPosition(String(mid));
      var comp = findLumetri(clip);
      if (comp) setParams(comp, NEUTRAL);
      app.enableQE();
      var qeSeq = qe.project.getActiveSequence();
      var timecode = qeSeq.CTI.timecode;
      qeSeq.exportFramePNG(timecode, basePath);
      return ok({ basePath: basePath, timecode: timecode });
    } catch (e) {
      return fail(e.message || e);
    }
  }

  function applyParams(trackIndex, clipIndex, params) {
    try {
      var clip = getClip(trackIndex, clipIndex);
      var comp = findLumetri(clip);
      var added = false;
      if (!comp) { comp = addLumetri(trackIndex, clip); added = true; }
      var res = setParams(comp, params);
      res.addedLumetri = added;
      res.clip = clip.name;
      return ok(res);
    } catch (e) {
      return fail(e.message || e);
    }
  }

  function resetParams(trackIndex, clipIndex) {
    try {
      var comp = findLumetri(getClip(trackIndex, clipIndex));
      if (!comp) return ok({ applied: {}, missing: [] });
      return ok(setParams(comp, NEUTRAL));
    } catch (e) {
      return fail(e.message || e);
    }
  }

  return {
    listTargets: listTargets,
    exportFrame: exportFrame,
    applyParams: applyParams,
    resetParams: resetParams
  };
})();
