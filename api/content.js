"use strict";

const { Readable } = require("node:stream");
const manifest = require("../data/web_content_manifest.json");
const bookPages = require("../data/book_pages_manifest.json");

let cachedToken = null;
let cachedTokenExpiresAt = 0;

function buildContentIndex() {
  const records = [...(manifest.datasets || []), ...(manifest.media || []), ...(bookPages.pages || [])];
  if (manifest.book?.driveFileId) {
    records.push({
      path: manifest.book.localPath,
      driveFileId: manifest.book.driveFileId,
      mimeType: "application/pdf"
    });
  }
  return new Map(records.map((item) => [item.path, item]));
}

const contentIndex = buildContentIndex();

function normalizeRequestedPath(value) {
  if (typeof value !== "string" || !value.trim()) return null;
  const normalized = value.trim().replace(/\\/g, "/").replace(/^\.\//, "").replace(/^\/+/, "");
  if (!normalized || normalized.split("/").includes("..")) return null;
  return normalized;
}

async function getAccessToken() {
  if (process.env.GOOGLE_DRIVE_ACCESS_TOKEN) return process.env.GOOGLE_DRIVE_ACCESS_TOKEN;
  if (cachedToken && Date.now() < cachedTokenExpiresAt) return cachedToken;

  const clientId = process.env.GOOGLE_DRIVE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_DRIVE_CLIENT_SECRET;
  const refreshToken = process.env.GOOGLE_DRIVE_REFRESH_TOKEN;
  if (!clientId || !clientSecret || !refreshToken) {
    throw new Error("Google Drive server credentials are not configured");
  }

  const body = new URLSearchParams({
    client_id: clientId,
    client_secret: clientSecret,
    refresh_token: refreshToken,
    grant_type: "refresh_token"
  });
  const response = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body
  });
  if (!response.ok) throw new Error(`Google OAuth token request failed (${response.status})`);

  const payload = await response.json();
  cachedToken = payload.access_token;
  cachedTokenExpiresAt = Date.now() + Math.max(60, Number(payload.expires_in || 3600) - 120) * 1000;
  return cachedToken;
}

function copyHeader(upstream, response, header) {
  const value = upstream.headers.get(header);
  if (value) response.setHeader(header, value);
}

module.exports = async function contentHandler(request, response) {
  if (!['GET', 'HEAD'].includes(request.method)) {
    response.setHeader("Allow", "GET, HEAD");
    return response.status(405).json({ error: "Method not allowed" });
  }

  const rawPath = Array.isArray(request.query.path) ? request.query.path[0] : request.query.path;
  const requestedPath = normalizeRequestedPath(rawPath);
  const content = requestedPath ? contentIndex.get(requestedPath) : null;
  if (!content?.driveFileId) return response.status(404).json({ error: "Content not found" });

  try {
    const token = await getAccessToken();
    const headers = { Authorization: `Bearer ${token}` };
    if (request.headers.range) headers.Range = request.headers.range;

    const driveUrl = `https://www.googleapis.com/drive/v3/files/${encodeURIComponent(content.driveFileId)}?alt=media&supportsAllDrives=true`;
    const upstream = await fetch(driveUrl, { method: request.method, headers });
    if (!upstream.ok && upstream.status !== 206) {
      return response.status(upstream.status === 404 ? 404 : 502).json({ error: "Drive content is unavailable" });
    }

    response.status(upstream.status);
    response.setHeader("Content-Type", content.mimeType || upstream.headers.get("content-type") || "application/octet-stream");
    response.setHeader("Cache-Control", "public, max-age=3600, s-maxage=86400, stale-while-revalidate=604800");
    response.setHeader("X-Content-Type-Options", "nosniff");
    response.setHeader("Accept-Ranges", "bytes");
    ["content-length", "content-range", "etag", "last-modified"].forEach((header) => copyHeader(upstream, response, header));

    if (request.method === "HEAD" || !upstream.body) return response.end();
    Readable.fromWeb(upstream.body).pipe(response);
  } catch (error) {
    console.error("TARIX360 content gateway:", error.message);
    return response.status(503).json({ error: "Content service is not configured" });
  }
};
