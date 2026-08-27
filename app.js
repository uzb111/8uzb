"use strict";

const state = {
  config: null,
  features: null,
  media: null,
  bookPages: null,
  topic: null,
  currentYear: null,
  currentBookPage: null,
  map: null,
  baseLayer: null,
  baseLayers: null,
  activeBasemap: "imagery",
  layerGroup: null,
  featureLayers: new Map(),
  visibleLayers: new Set(["state", "city", "event", "route", "thematic"]),
  selectedStateId: null,
  playbackTimer: null,
  isPlaying: false,
  activeTab: "book"
};

const $ = (id) => document.getElementById(id);
const storage = window.TARIX360_STORAGE || {
  mode: "local-static",
  resolveAsset: (path) => path,
  resolveData: (path) => path,
  resolveBook: (path) => path
};
const mediaManifestPath = window.TARIX360_DEPLOYMENT?.mediaManifestPath || "data/media_manifest.json";

const CATEGORY_LABELS = Object.freeze({
  state: "davlat",
  city: "shahar",
  event: "voqea",
  route: "yo‘nalish",
  thematic: "shaxs / maskan"
});

function yearOf(value) {
  if (value === null || value === undefined || value === "") return null;
  const match = String(value).match(/-?\d{3,4}/);
  return match ? Number(match[0]) : null;
}

function featureClass(feature) {
  const properties = feature.properties || {};
  const raw = properties.feature_class || properties.source_layer || "thematic";
  const aliases = {
    states: "state",
    cities: "city",
    events: "event",
    routes: "route",
    thematic_points: "thematic",
    person: "thematic",
    site: "thematic"
  };
  return aliases[raw] || raw;
}

function featureLabel(feature) {
  const properties = feature.properties || {};
  return properties.title_uz || properties.name_uz || properties.name || properties.polity_uz || properties.polity_en || properties.id || "Obyekt";
}

function isActive(feature, year) {
  const properties = feature.properties || {};
  const date = yearOf(properties.date);
  if (date !== null) return date === year || Math.abs(date - year) <= 1;

  let start = yearOf(properties.start_date);
  let end = yearOf(properties.end_date);
  if (start === null && end === null) return true;
  if (start === null) start = end;
  if (end === null) end = start;
  return year >= start && year <= end;
}

function isPermanentAnchor(feature) {
  const category = featureClass(feature);
  return category === "city" || category === "thematic";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function styleForFeature(feature) {
  const category = featureClass(feature);
  if (category === "state") {
    const influenceZone = (feature.properties || {}).boundary_kind === "influence_zone";
    return {
      color: influenceZone ? "#b9853e" : "#8c6423",
      weight: influenceZone ? 1.8 : 2.2,
      fillColor: influenceZone ? "#c99443" : "#dfaa3d",
      fillOpacity: influenceZone ? 0.12 : 0.27,
      dashArray: influenceZone ? "7 6" : null,
      className: `history-state${influenceZone ? " influence-zone" : ""}`
    };
  }
  if (category === "route") {
    return { color: "#d75d4e", weight: 3.2, dashArray: "10 8", opacity: 0.94, className: "history-route" };
  }
  return { color: "#627b91", weight: 2, fillColor: "#7f96a8", fillOpacity: 0.2, className: "history-shape" };
}

function pointStyle(feature) {
  const category = featureClass(feature);
  const properties = feature.properties || {};
  const exactYear = yearOf(properties.date);
  const current = exactYear !== null && Math.abs(exactYear - state.currentYear) <= 1;
  if (category === "event") {
    return { radius: current ? 8 : 6.5, color: "#7d211f", fillColor: "#f06858", fillOpacity: 0.98, weight: 2.5, className: `history-point event-point${current ? " is-current" : ""}` };
  }
  if (category === "thematic") {
    return { radius: 7, color: "#56356d", fillColor: "#b984d8", fillOpacity: 0.96, weight: 2, className: "history-point thematic-point" };
  }
  return { radius: 5.2, color: "#16334f", fillColor: "#64a9df", fillOpacity: 0.98, weight: 2, className: "history-point city-point" };
}

function pointLayer(feature, latlng) {
  if (featureClass(feature) !== "city") return L.circleMarker(latlng, pointStyle(feature));
  return L.marker(latlng, {
    icon: L.divIcon({
      className: "history-city-marker",
      html: '<span class="city-symbol" aria-hidden="true"><i></i></span>',
      iconSize: [22, 22],
      iconAnchor: [11, 11],
      popupAnchor: [0, -10],
      tooltipAnchor: [0, -10]
    }),
    riseOnHover: true
  });
}

function featureDetails(feature) {
  const properties = feature.properties || {};
  if (featureClass(feature) === "city") {
    const modernLocation = [properties.modern_name_uz, properties.modern_region_uz, properties.modern_country_uz].filter(Boolean).join(", ");
    return [
      ["Tarixiy nom", properties.historical_name_uz || featureLabel(feature)],
      ["Hozirgi joy", modernLocation],
      ["Mavzudagi roli", properties.summary_uz || properties.role || ""],
      ["Joy aniqligi", properties.location_precision || properties.coordinate_quality || ""]
    ].filter((row) => row[1]);
  }
  return [
    ["Nomi", featureLabel(feature)],
    ["Sana", properties.date || [properties.start_date, properties.end_date].filter(Boolean).join(" – ")],
    ["Turi", properties.category || CATEGORY_LABELS[featureClass(feature)] || properties.status || ""],
    ["Izoh", properties.notes || properties.role || ""]
  ].filter((row) => row[1]);
}

function bindFeature(feature, layer) {
  const properties = feature.properties || {};
  const category = featureClass(feature);
  const html = featureDetails(feature)
    .map(([label, value]) => `<div class="popup-row"><b>${escapeHtml(label)}:</b> ${escapeHtml(value)}</div>`)
    .join("");

  if (category === "state") {
    const period = [properties.start_date, properties.end_date].filter(Boolean).join("–");
    layer.bindTooltip(`<strong>${escapeHtml(featureLabel(feature))}</strong>${period ? `<span>${escapeHtml(period)}</span>` : ""}`, {
      sticky: true,
      direction: "top",
      className: "state-hover-label"
    });
    layer.on("click", () => selectStateFeature(feature));
    layer.on("mouseover", () => {
      if (!state.selectedStateId && typeof layer.setStyle === "function") layer.setStyle({ weight: 3.4, fillOpacity: 0.38 });
    });
    layer.on("mouseout", applyStateSelectionStyles);
    return;
  }

  layer.bindPopup(`<div class="history-popup${category === "city" ? " city-popup" : ""}"><strong>${escapeHtml(featureLabel(feature))}</strong>${html}</div>`);

  if (category === "city") {
    const cityCount = topicFeatures().filter((item) => featureClass(item) === "city").length;
    layer.bindTooltip(escapeHtml(properties.name_uz || properties.name), {
      permanent: cityCount <= 12,
      sticky: cityCount > 12,
      direction: "top",
      className: "city-label",
      offset: [0, -5]
    });
  }
}

function initMap() {
  state.map = L.map("map", { zoomControl: true, preferCanvas: false, minZoom: 3 }).setView([39.7, 66.9], 5);
  state.baseLayers = {
    imagery: L.tileLayer("https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
      maxZoom: 19,
      className: "imagery-basemap",
      attribution: "Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community"
    }),
    osm: L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      className: "osm-basemap",
      attribution: "© OpenStreetMap contributors"
    })
  };
  state.baseLayer = state.baseLayers[state.activeBasemap].addTo(state.map);
  state.layerGroup = L.layerGroup().addTo(state.map);
}

function selectBasemap(basemap) {
  const nextLayer = state.baseLayers?.[basemap];
  if (!nextLayer || basemap === state.activeBasemap) return;
  if (state.baseLayer) state.map.removeLayer(state.baseLayer);
  state.baseLayer = nextLayer.addTo(state.map);
  state.baseLayer.bringToBack();
  state.activeBasemap = basemap;
  document.querySelectorAll(".basemap-toggle").forEach((button) => {
    const active = button.dataset.basemap === basemap;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
}

function topicFeatures(topic = state.topic) {
  const ids = new Set(topic.showFeatureIds || []);
  return state.features.features.filter((feature) => ids.has((feature.properties || {}).id));
}

function visibleTopicFeatures(topic = state.topic, year = state.currentYear) {
  return topicFeatures(topic)
    .filter((feature) => isPermanentAnchor(feature) || isActive(feature, year))
    .filter((feature) => state.visibleLayers.has(featureClass(feature)));
}

function featureById(featureId) {
  return state.features?.features.find((feature) => (feature.properties || {}).id === featureId) || null;
}

function pointInRing(point, ring) {
  let inside = false;
  for (let index = 0, previous = ring.length - 1; index < ring.length; previous = index++) {
    const [x1, y1] = ring[index];
    const [x2, y2] = ring[previous];
    const intersects = ((y1 > point[1]) !== (y2 > point[1])) && (point[0] < ((x2 - x1) * (point[1] - y1)) / ((y2 - y1) || Number.EPSILON) + x1);
    if (intersects) inside = !inside;
  }
  return inside;
}

function pointInState(point, geometry) {
  if (!geometry || !Array.isArray(point)) return false;
  const insidePolygon = (polygon) => polygon.length > 0 && pointInRing(point, polygon[0]) && !polygon.slice(1).some((hole) => pointInRing(point, hole));
  if (geometry.type === "Polygon") return insidePolygon(geometry.coordinates);
  if (geometry.type === "MultiPolygon") return geometry.coordinates.some(insidePolygon);
  return false;
}

function relationForState(city, stateId) {
  return ((city.properties || {}).state_relations || []).find((item) => item.state_id === stateId) || null;
}

function relatedCitiesForState(stateFeature) {
  const stateId = (stateFeature.properties || {}).id;
  const topicIds = new Set(state.topic.showFeatureIds || []);
  return state.features.features
    .filter((feature) => featureClass(feature) === "city" && topicIds.has((feature.properties || {}).id))
    .map((city) => {
      const relation = relationForState(city, stateId);
      const inside = pointInState(city.geometry?.coordinates, stateFeature.geometry);
      return relation || inside ? { city, relation, inside } : null;
    })
    .filter(Boolean)
    .sort((a, b) => Number(Boolean(b.relation)) - Number(Boolean(a.relation)) || featureLabel(a.city).localeCompare(featureLabel(b.city), "uz"));
}

const RELATION_LABELS = Object.freeze({
  poytaxt: "Poytaxt",
  siyosiy_markaz: "Siyosiy markaz",
  asosiy_shahar: "Asosiy shahar",
  yirik_markaz: "Yirik markaz",
  tayanch_markaz: "Tayanch markaz",
  nazorat_markazi: "Nazorat markazi",
  hal_qiluvchi_markaz: "Hal qiluvchi markaz",
  chegara_markazi: "Chegara markazi",
  chegara_savdo_markazi: "Savdo-chegara markazi",
  chegara_qalasi: "Chegara qal’asi",
  strategik_shahar: "Strategik shahar",
  voha_markazi: "Voha markazi",
  sharqiy_markaz: "Sharqiy markaz",
  qarorgoh: "Hukmdor qarorgohi",
  asosiy_markaz: "Asosiy markaz",
  voha_shahri: "Voha shahri",
  sharqiy_darvoza: "Sharqiy darvoza",
  "yo‘l_markazi": "Yo‘l markazi",
  shahar: "Shahar"
});

function boundaryTypeLabel(properties) {
  if (properties.boundary_kind === "influence_zone") return "Ta’sir zonasi";
  if (properties.boundary_kind === "territorial_extent") return "Taxminiy hudud";
  return properties.status === "reconstructed" ? "Rekonstruksiya" : "Tarixiy hudud";
}

function renderStateSources(properties) {
  const sourceList = $("stateSourceList");
  const sources = Array.isArray(properties.source_refs) ? properties.source_refs : [];
  if (!sources.length) {
    sourceList.innerHTML = `<div class="profile-source-note">${escapeHtml(properties.geometry_quality || properties.notes || "Manba metama’lumoti tayyorlanmoqda.")}</div>`;
    return;
  }
  sourceList.innerHTML = sources.map((source) => {
    const title = typeof source === "string" ? source : source.title || "Tarixiy manba";
    const url = typeof source === "string" ? source : source.url || (source.drive_file_id ? `https://drive.google.com/file/d/${encodeURIComponent(source.drive_file_id)}/view` : "");
    const pages = typeof source === "object" && Array.isArray(source.pages) ? ` · ${source.pages.join(", ")}-bet` : "";
    if (!url) return `<div class="profile-source-note">${escapeHtml(title + pages)}</div>`;
    return `<a href="${escapeHtml(url)}" target="_blank" rel="noreferrer"><span>${escapeHtml(title + pages)}</span><b>↗</b></a>`;
  }).join("");
}

function renderStateProfile(feature) {
  const properties = feature.properties || {};
  const cities = relatedCitiesForState(feature);
  $("stateProfileName").textContent = featureLabel(feature);
  $("stateProfilePeriod").textContent = [properties.start_date, properties.end_date].filter(Boolean).join("–") || "Sana ko‘rsatilmagan";
  $("stateProfileType").textContent = boundaryTypeLabel(properties);
  const confidence = Number(properties.confidence);
  $("stateProfileConfidence").textContent = Number.isFinite(confidence) ? `Ishonch ${Math.round(confidence * 100)}%` : "Taxminiy rekonstruksiya";
  $("stateProfileSummary").textContent = properties.notes || `${state.currentYear}-yil sahnasidagi tanlangan tarixiy siyosiy hudud.`;
  $("stateProfileUncertainty").textContent = properties.uncertainty_note || "Chegara tarixiy manbalardan umumlashtirilgan; zamonaviy davlat chegarasi emas.";
  $("stateCityCount").textContent = `${cities.length} ta bog‘liq nuqta`;

  const cityList = $("stateCityList");
  if (!cities.length) {
    cityList.innerHTML = '<div class="profile-empty">Bu mavzu sahnasida poligon bilan bog‘langan shahar nuqtasi yo‘q.</div>';
  } else {
    cityList.innerHTML = "";
    cities.forEach(({ city, relation }) => {
      const properties = city.properties || {};
      const button = document.createElement("button");
      button.type = "button";
      button.className = "state-city-item";
      const relationLabel = relation ? (RELATION_LABELS[relation.kind] || relation.kind.replaceAll("_", " ")) : "Poligon ichidagi shahar";
      const current = [properties.modern_name_uz, properties.modern_country_uz].filter(Boolean).join(", ");
      button.innerHTML = `<span class="state-city-glyph" aria-hidden="true"><i></i></span><span><strong>${escapeHtml(featureLabel(city))}</strong><small>${escapeHtml(relationLabel)}</small><em>${escapeHtml(current || "Hozirgi joylashuv aniqlanmoqda")}</em></span><b>↗</b>`;
      button.title = relation?.note_uz || properties.summary_uz || featureLabel(city);
      button.addEventListener("click", () => locateFromStateProfile(properties.id));
      cityList.appendChild(button);
    });
  }
  renderStateSources(properties);
  $("stateProfile").classList.remove("hidden");
  document.body.classList.add("state-profile-open");
}

function applyStateSelectionStyles() {
  state.featureLayers.forEach((container, featureId) => {
    const feature = featureById(featureId);
    if (!feature || featureClass(feature) !== "state") return;
    const baseStyle = styleForFeature(feature);
    const isSelected = state.selectedStateId === featureId;
    const isDimmed = Boolean(state.selectedStateId) && !isSelected;
    container.eachLayer((child) => {
      if (typeof child.setStyle !== "function") return;
      child.setStyle(isSelected
        ? { ...baseStyle, color: "#ffd36e", weight: 4, fillOpacity: 0.43, opacity: 1 }
        : isDimmed
          ? { ...baseStyle, weight: 1, fillOpacity: 0.045, opacity: 0.28 }
          : baseStyle);
    });
    if (isSelected && typeof container.bringToFront === "function") container.bringToFront();
  });
}

function selectStateFeature(feature) {
  const featureId = (feature.properties || {}).id;
  state.selectedStateId = featureId;
  applyStateSelectionStyles();
  const container = state.featureLayers.get(featureId);
  const bounds = container?.getBounds();
  if (bounds?.isValid()) state.map.fitBounds(bounds.pad(0.16), { maxZoom: 6.5, animate: true, duration: 0.65 });
  renderStateProfile(feature);
}

function closeStateProfile({ preserveStyles = false } = {}) {
  state.selectedStateId = null;
  $("stateProfile")?.classList.add("hidden");
  document.body.classList.remove("state-profile-open");
  if (!preserveStyles) applyStateSelectionStyles();
}

function locateFromStateProfile(featureId) {
  if (!window.matchMedia("(max-width: 700px)").matches) {
    locateFeature(featureId);
    return;
  }
  closeStateProfile();
  $("mapStage").scrollIntoView({ behavior: "smooth", block: "center" });
  window.setTimeout(() => {
    state.map.invalidateSize({ animate: false });
    locateFeature(featureId);
  }, 320);
}

function compositionText(features) {
  const counts = new Map();
  features.forEach((feature) => {
    const category = featureClass(feature);
    counts.set(category, (counts.get(category) || 0) + 1);
  });
  return [...counts.entries()]
    .map(([category, count]) => `${count} ${CATEGORY_LABELS[category] || category}`)
    .join(" · ") || "Faol qatlam yo‘q";
}

function renderMap({ fitBounds = false, animate = true } = {}) {
  state.layerGroup.clearLayers();
  state.featureLayers.clear();
  const selected = visibleTopicFeatures();
  const bounds = [];

  if (animate) {
    $("mapStage").classList.remove("scene-ready");
    requestAnimationFrame(() => $("mapStage").classList.add("scene-ready"));
  }

  selected.forEach((feature) => {
    const container = L.geoJSON(feature, {
      style: styleForFeature,
      pointToLayer: pointLayer,
      onEachFeature: bindFeature
    }).addTo(state.layerGroup);
    const featureId = (feature.properties || {}).id;
    container._tarixFeatureId = featureId;
    state.featureLayers.set(featureId, container);
    const layerBounds = container.getBounds();
    if (layerBounds.isValid()) bounds.push(layerBounds);
  });

  if (state.selectedStateId && !state.featureLayers.has(state.selectedStateId)) closeStateProfile({ preserveStyles: true });
  applyStateSelectionStyles();

  if (fitBounds && bounds.length) {
    const combined = bounds.slice(1).reduce((result, item) => result.extend(item), bounds[0]);
    state.map.fitBounds(combined.pad(0.12), { maxZoom: 7, animate: true, duration: 0.65 });
  }

  $("visibleFeatureCount").textContent = `${selected.length} obyekt`;
  $("sceneComposition").textContent = compositionText(selected);
  $("mapNotice").classList.toggle("hidden", selected.length > 0);
  $("sceneStatus").textContent = `${state.topic.id}-mavzu · ${state.currentYear}-yil · ${selected.length} obyekt`;
  renderEventList(selected);
}

function locateFeature(featureId) {
  const layer = state.featureLayers.get(featureId);
  if (!layer) return;
  const feature = featureById(featureId);
  if (feature && featureClass(feature) === "state") {
    selectStateFeature(feature);
    return;
  }
  const bounds = layer.getBounds();
  if (bounds.isValid()) state.map.fitBounds(bounds.pad(0.5), { maxZoom: 8, animate: true });
  const childLayers = layer.getLayers();
  if (childLayers[0] && typeof childLayers[0].openPopup === "function") childLayers[0].openPopup();
}

function renderEventList(features) {
  const list = $("eventList");
  list.innerHTML = "";
  const meaningful = features
    .filter((feature) => ["event", "city", "thematic"].includes(featureClass(feature)))
    .sort((a, b) => (yearOf((a.properties || {}).date) || 0) - (yearOf((b.properties || {}).date) || 0));

  $("eventCount").textContent = `${meaningful.length} ta`;
  $("eventSummary").innerHTML = `<span>${state.currentYear}</span><p>${escapeHtml(state.topic.mapStory)}</p>`;

  if (!meaningful.length) {
    list.innerHTML = '<div class="empty-state">Bu yil uchun alohida voqea yoki nuqta tanlanmagan.</div>';
    return;
  }

  meaningful.forEach((feature, index) => {
    const properties = feature.properties || {};
    const category = featureClass(feature);
    const featureId = properties.id;
    const button = document.createElement("button");
    button.type = "button";
    button.className = `event-item ${category}`;
    button.style.setProperty("--delay", `${Math.min(index * 45, 360)}ms`);
    button.innerHTML = `<span class="event-dot ${category}"></span><div><div class="type">${escapeHtml(properties.category || CATEGORY_LABELS[category] || "obyekt")}</div><div class="name">${escapeHtml(featureLabel(feature))}</div><div class="detail">${escapeHtml(properties.date || [properties.start_date, properties.end_date].filter(Boolean).join(" – ") || properties.role || "Xaritadagi tarixiy obyekt")}</div></div><span class="locate-arrow">↗</span>`;
    button.addEventListener("click", () => locateFeature(featureId));
    list.appendChild(button);
  });
}

function bookPageRecord(pageNumber) {
  return state.bookPages.pages.find((item) => item.page === pageNumber);
}

function originalBookUrl(pageNumber = state.currentBookPage) {
  const fileId = state.bookPages.source.driveFileId;
  return `https://drive.google.com/file/d/${encodeURIComponent(fileId)}/view#page=${pageNumber}`;
}

function prefetchBookPage(pageNumber) {
  const record = bookPageRecord(pageNumber);
  if (!record) return;
  const image = new Image();
  image.src = storage.resolveAsset(record.file);
}

function renderBookPage() {
  const [start, end] = state.topic.pages;
  state.currentBookPage = Math.max(start, Math.min(end, Number(state.currentBookPage || start)));
  const record = bookPageRecord(state.currentBookPage);
  if (!record) throw new Error(`${state.currentBookPage}-bet book manifestida topilmadi.`);

  $("pdfRangeText").textContent = `${start}–${end}-betlar`;
  $("bookPages").textContent = `Kitob: ${start}–${end}-bet`;
  $("bookPageNumber").textContent = `${state.currentBookPage} / ${end}`;
  $("bookPageCurrent").textContent = `${state.currentBookPage}-bet`;
  $("previousBookPage").disabled = state.currentBookPage <= start;
  $("nextBookPage").disabled = state.currentBookPage >= end;
  $("openPdfNew").href = originalBookUrl();
  $("pdfHint").textContent = "Joriy sahifa yengil WebP sifatida yuklandi; to‘liq 145 MB PDF avtomatik ochilmaydi.";
  $("bookPageStatus").textContent = `${state.currentBookPage}-bet yuklanmoqda…`;
  $("bookPagePlaceholder").classList.remove("hidden");

  const image = $("bookPageImage");
  image.classList.remove("ready");
  image.alt = `${state.currentBookPage}-bet — ${state.topic.title}`;
  image.src = storage.resolveAsset(record.file);
  $("bookScroll").scrollTop = 0;

  if (state.currentBookPage > start) prefetchBookPage(state.currentBookPage - 1);
  if (state.currentBookPage < end) prefetchBookPage(state.currentBookPage + 1);
}

function stepBookPage(offset) {
  state.currentBookPage += offset;
  renderBookPage();
}

function renderGallery() {
  const gallery = $("gallery");
  gallery.innerHTML = "";
  const generatedNames = new Set(state.topic.generatedImages || []);
  const media = state.media
    .filter((item) => item.topic === state.topic.id)
    .sort((a, b) => {
      const priority = (item) => generatedNames.has(item.file.split("/").pop()) ? 0 : item.kind === "generated" ? 1 : 2;
      return priority(a) - priority(b);
    });

  $("galleryCount").textContent = `${media.length} ta`;
  media.forEach((item, index) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "media-card";
    card.style.setProperty("--delay", `${Math.min(index * 55, 440)}ms`);
    const kindLabel = item.kind === "generated" ? "Rekonstruksiya" : "Tarixiy manba";
    card.innerHTML = `<div class="media-visual"><img loading="lazy" src="${escapeHtml(storage.resolveAsset(item.file))}" alt="${escapeHtml(item.title)}"><span class="media-kind ${escapeHtml(item.kind)}">${kindLabel}</span></div><div class="media-info"><div class="media-title">${escapeHtml(item.title)}</div><div class="media-meta">${kindLabel}${item.license ? ` · ${escapeHtml(item.license)}` : ""}</div></div>`;
    card.addEventListener("click", () => openLightbox(item));
    gallery.appendChild(card);
  });
}

function openLightbox(item) {
  $("lightboxImg").src = storage.resolveAsset(item.file);
  $("lightboxImg").alt = item.title || "Tarixiy rasm";
  $("lightboxCaption").textContent = item.title;
  $("lightbox").classList.remove("hidden");
  $("lightboxClose").focus();
}

function closeLightbox() {
  $("lightbox").classList.add("hidden");
  $("lightboxImg").src = "";
}

function topicMilestones(topic = state.topic) {
  const years = new Set([topic.years[0], topic.focusYear, topic.years[1]]);
  topicFeatures(topic).forEach((feature) => {
    const properties = feature.properties || {};
    [properties.date, properties.start_date, properties.end_date].forEach((value) => {
      const year = yearOf(value);
      if (year !== null && year >= topic.years[0] && year <= topic.years[1]) years.add(year);
    });
  });
  return [...years].sort((a, b) => a - b);
}

function renderTimelineMoments() {
  const container = $("timelineMoments");
  container.innerHTML = "";
  topicMilestones().forEach((year) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "moment-chip";
    button.classList.toggle("active", year === state.currentYear);
    button.textContent = year;
    button.addEventListener("click", () => {
      stopPlayback();
      setSceneYear(year);
    });
    container.appendChild(button);
  });
}

function setSceneYear(year, { fitBounds = false } = {}) {
  const min = state.topic.years[0];
  const max = state.topic.years[1];
  state.currentYear = Math.max(min, Math.min(max, Number(year)));
  $("yearSlider").value = state.currentYear;
  $("yearValue").textContent = state.currentYear;
  renderTimelineMoments();
  renderMap({ fitBounds, animate: true });
}

function stepMoment(direction) {
  stopPlayback();
  const milestones = topicMilestones();
  const candidates = direction > 0
    ? milestones.filter((year) => year > state.currentYear)
    : milestones.filter((year) => year < state.currentYear).reverse();
  if (candidates.length) setSceneYear(candidates[0]);
}

function updatePlaybackButton() {
  $("playTimeline").classList.toggle("active", state.isPlaying);
  $("playTimeline").querySelector(".play-icon").textContent = state.isPlaying ? "Ⅱ" : "▶";
  $("playTimeline").querySelector(".play-label").textContent = state.isPlaying ? "To‘xtatish" : "Jonlantirish";
  document.body.classList.toggle("timeline-playing", state.isPlaying);
}

function stopPlayback() {
  if (state.playbackTimer) window.clearTimeout(state.playbackTimer);
  state.playbackTimer = null;
  state.isPlaying = false;
  updatePlaybackButton();
}

function startPlayback() {
  stopPlayback();
  const milestones = topicMilestones();
  if (!milestones.some((year) => year > state.currentYear)) setSceneYear(milestones[0]);
  state.isPlaying = true;
  updatePlaybackButton();

  const tick = () => {
    const next = topicMilestones().find((year) => year > state.currentYear);
    if (next === undefined) {
      stopPlayback();
      return;
    }
    setSceneYear(next);
    state.playbackTimer = window.setTimeout(tick, 1350);
  };
  state.playbackTimer = window.setTimeout(tick, 450);
}

function togglePlayback() {
  if (state.isPlaying) stopPlayback();
  else startPlayback();
}

function updateTopicNavigation() {
  const index = state.config.topics.findIndex((topic) => topic.id === state.topic.id);
  $("topicProgress").textContent = `${index + 1} / ${state.config.topics.length}`;
  $("previousTopic").disabled = index === 0;
  $("nextTopic").disabled = index === state.config.topics.length - 1;
}

function selectTopic(id) {
  const topic = state.config.topics.find((item) => item.id === id);
  if (!topic) return;
  stopPlayback();
  closeStateProfile();
  state.topic = topic;
  state.currentYear = topic.focusYear;
  state.currentBookPage = topic.pages[0];

  document.querySelectorAll(".topic-btn").forEach((button) => {
    const active = Number(button.dataset.id) === id;
    button.classList.toggle("active", active);
    button.setAttribute("aria-current", active ? "true" : "false");
  });

  $("topicNumber").textContent = `${id}-mavzu`;
  $("topicTitle").textContent = topic.title;
  $("mapStory").textContent = topic.mapStory;
  $("topicYears").textContent = `${topic.years[0]}–${topic.years[1]}`;
  $("yearSlider").min = topic.years[0];
  $("yearSlider").max = topic.years[1];
  $("yearSlider").value = state.currentYear;
  $("yearValue").textContent = state.currentYear;

  updateTopicNavigation();
  renderBookPage();
  renderGallery();
  renderTimelineMoments();
  renderMap({ fitBounds: true, animate: true });
}

function changeTopic(offset) {
  const index = state.config.topics.findIndex((topic) => topic.id === state.topic.id);
  const next = state.config.topics[index + offset];
  if (next) selectTopic(next.id);
}

function renderTopicButtons() {
  const list = $("topicsList");
  list.innerHTML = "";
  state.config.topics.forEach((topic) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "topic-btn";
    button.dataset.id = topic.id;
    button.innerHTML = `<span class="topic-index">${topic.id}</span><span class="topic-copy"><strong>${escapeHtml(topic.title)}</strong><small>${topic.pages[0]}–${topic.pages[1]}-bet · ${topic.years[0]}–${topic.years[1]}</small></span><span class="topic-arrow">›</span>`;
    button.addEventListener("click", () => selectTopic(topic.id));
    list.appendChild(button);
  });
}

function setStudyTab(name) {
  state.activeTab = name;
  const definitions = [
    ["book", "bookPanel", "bookTabBtn"],
    ["gallery", "galleryPanel", "galleryTabBtn"],
    ["events", "eventsPanel", "eventsTabBtn"]
  ];
  definitions.forEach(([tabName, panelId, buttonId]) => {
    $(panelId).classList.toggle("active", tabName === name);
    $(buttonId).classList.toggle("active", tabName === name);
  });
  if (name === "book") renderBookPage();
  if (window.matchMedia("(max-width: 700px)").matches) {
    $("bookPanel").parentElement.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function toggleTeacherMode() {
  const enabled = document.body.classList.toggle("presentation-mode");
  $("teacherModeBtn").classList.toggle("active", enabled);
  $("teacherModeBtn").textContent = enabled ? "Oddiy rejim" : "Proyektor";
  window.setTimeout(() => state.map.invalidateSize({ animate: true }), 240);
}

function bindInterface() {
  $("bookTabBtn").addEventListener("click", () => setStudyTab("book"));
  $("galleryTabBtn").addEventListener("click", () => setStudyTab("gallery"));
  $("eventsTabBtn").addEventListener("click", () => setStudyTab("events"));
  $("previousTopic").addEventListener("click", () => changeTopic(-1));
  $("nextTopic").addEventListener("click", () => changeTopic(1));
  $("previousMoment").addEventListener("click", () => stepMoment(-1));
  $("nextMoment").addEventListener("click", () => stepMoment(1));
  $("playTimeline").addEventListener("click", togglePlayback);
  $("resetYear").addEventListener("click", () => {
    stopPlayback();
    setSceneYear(state.topic.focusYear);
  });
  $("yearSlider").addEventListener("input", (event) => {
    stopPlayback();
    setSceneYear(Number(event.target.value));
  });
  $("previousBookPage").addEventListener("click", () => stepBookPage(-1));
  $("nextBookPage").addEventListener("click", () => stepBookPage(1));
  $("teacherModeBtn").addEventListener("click", toggleTeacherMode);
  $("lightboxClose").addEventListener("click", closeLightbox);
  $("lightbox").addEventListener("click", (event) => {
    if (event.target.id === "lightbox") closeLightbox();
  });
  $("bookPageImage").addEventListener("load", () => {
    $("bookPageImage").classList.add("ready");
    $("bookPagePlaceholder").classList.add("hidden");
  });
  $("bookPageImage").addEventListener("error", () => {
    $("bookPageStatus").textContent = "Sahifa yuklanmadi. To‘liq PDF tugmasidan foydalaning.";
    $("bookPagePlaceholder").classList.remove("hidden");
  });

  document.querySelectorAll(".basemap-toggle").forEach((button) => {
    button.addEventListener("click", () => selectBasemap(button.dataset.basemap));
  });

  $("stateProfileClose").addEventListener("click", () => closeStateProfile());

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeLightbox();
      closeStateProfile();
    }
    const tag = document.activeElement?.tagName;
    if (["INPUT", "BUTTON", "A"].includes(tag)) return;
    if (event.key === "ArrowLeft") stepMoment(-1);
    if (event.key === "ArrowRight") stepMoment(1);
    if (event.key === "PageUp") changeTopic(-1);
    if (event.key === "PageDown") changeTopic(1);
    if (event.code === "Space") {
      event.preventDefault();
      togglePlayback();
    }
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopPlayback();
  });

  let resizeTimer = null;
  window.addEventListener("resize", () => {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => state.map?.invalidateSize({ animate: false }), 140);
  });
}

function validateData(config, features, media, bookPages) {
  if (!Array.isArray(config.topics) || !config.topics.length) throw new Error("Mavzu konfiguratsiyasi bo‘sh.");
  if (!Array.isArray(features.features)) throw new Error("master_all_features GeoJSON noto‘g‘ri.");
  if (!Array.isArray(media)) throw new Error("media_manifest massiv bo‘lishi kerak.");
  if (!Array.isArray(bookPages.pages) || !bookPages.pages.length) throw new Error("book_pages_manifest bo‘sh.");
  const featureIds = new Set(features.features.map((feature) => (feature.properties || {}).id));
  const missing = config.topics.flatMap((topic) => (topic.showFeatureIds || []).filter((id) => !featureIds.has(id)));
  if (missing.length) throw new Error(`Master GeoJSON’da ${missing.length} ta feature ID topilmadi: ${missing.join(", ")}`);
}

async function fetchJson(path) {
  const response = await fetch(storage.resolveData(path), { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} yuklanmadi (${response.status})`);
  return response.json();
}

async function boot() {
  const [config, features, media, bookPages] = await Promise.all([
    fetchJson("data/topic_config_10.json"),
    fetchJson("data/master_all_features.geojson"),
    fetchJson(mediaManifestPath),
    fetchJson("data/book_pages_manifest.json")
  ]);
  validateData(config, features, media, bookPages);
  state.config = config;
  state.features = features;
  state.media = media;
  state.bookPages = bookPages;

  initMap();
  bindInterface();
  renderTopicButtons();
  selectTopic(1);
  document.body.classList.add("app-ready");
}

boot().catch((error) => {
  console.error(error);
  document.body.innerHTML = `<main class="fatal-error"><strong>TARIX360 yuklanmadi</strong><pre>${escapeHtml(error.stack || error)}</pre><p>Papkani START_LOCAL.bat orqali ishga tushiring.</p></main>`;
});
