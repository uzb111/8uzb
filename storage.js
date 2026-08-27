(function initTarix360Storage(global) {
  "use strict";

  const deployment = global.TARIX360_DEPLOYMENT || {};
  const storageMode = deployment.contentMode || "local-static";

  function preserveRemoteUrl(path) {
    return /^(?:https?:)?\/\//i.test(path) || path.startsWith("data:") || path.startsWith("blob:");
  }

  function normalizeLocalPath(path) {
    if (typeof path !== "string" || !path.trim()) {
      throw new TypeError("Storage path must be a non-empty string");
    }
    if (preserveRemoteUrl(path)) return path;
    return path.replace(/^\.\//, "").replace(/\\/g, "/");
  }

  function joinBase(base, path, removablePrefix) {
    const normalized = normalizeLocalPath(path);
    if (preserveRemoteUrl(normalized) || !base) return normalized;
    const prefix = removablePrefix ? `${removablePrefix.replace(/\/$/, "")}/` : "";
    const tail = prefix && normalized.startsWith(prefix) ? normalized.slice(prefix.length) : normalized;
    return `${String(base).replace(/\/$/, "")}/${tail.replace(/^\//, "")}`;
  }

  function resolveDriveApi(path) {
    const normalized = normalizeLocalPath(path);
    if (preserveRemoteUrl(normalized)) return normalized;
    const endpoint = deployment.contentEndpoint || "/api/content";
    const separator = endpoint.includes("?") ? "&" : "?";
    return `${endpoint}${separator}path=${encodeURIComponent(normalized)}`;
  }

  function resolve(path, base, removablePrefix) {
    if (storageMode === "drive-api") return resolveDriveApi(path);
    return joinBase(base, path, removablePrefix);
  }

  global.TARIX360_STORAGE = Object.freeze({
    mode: storageMode,
    environment: deployment.environment || "localhost",
    release: deployment.release || "development",
    sourceOfTruth: deployment.sourceOfTruth || "google-drive",
    resolveAsset: (path) => resolve(path, deployment.assetBase),
    resolveData: (path) => resolve(path, deployment.dataBase, "data"),
    resolveBook: (path) => resolve(path, deployment.bookBase || deployment.assetBase)
  });
})(window);
